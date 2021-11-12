import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import argparse, mne, numpy as np, pandas as pd, tensorpac as tp

from config import fname, tpac_cfg

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument('subject',
                    help='The subject to create')
parser.add_argument('lock',
                    help='The timelock to create')

args = parser.parse_args()
subject = args.subject
lock = args.lock
print(f'Preprocessing {subject}')

def load_subject(fname,baseline=(None,None),rereference=True):
    epochs = mne.read_epochs(fname).pick('eeg').apply_baseline(baseline)
    if rereference:
        # local reference skews coherence metrics
        epochs.set_eeg_reference('average')
    return epochs


def get_pac(e, method='gc', fph=[[2,4],[4,8],[8,13]], famp=[[13,20],[20,30],[30,45],[45,60]], combinations='within', condition="LockSample>0", padding=2000, pac_kwargs={}):
    pac = tp.EventRelatedPac(fph, famp, **pac_kwargs)
    e = e[condition]
    # get params ready
    padding = 2000 # TODO: Fix padding type in outer loop
    n_samples=e.get_data().shape[-1];n_chans=len(e.ch_names);n_amp=len(pac.f_amp);n_pha=len(pac.f_pha);
    in_dim = [-1,n_samples]; out_dim = [-1,n_chans,n_samples-2*padding]

    padding = 2000
    # filter phase and amplitude signals
    phase = pac.filter(e.info['sfreq'],e.get_data().reshape(in_dim),edges=padding,ftype='phase') \
        .reshape([n_pha]+out_dim)
    amplitude = pac.filter(e.info['sfreq'],e.get_data().reshape(in_dim),edges=padding,ftype='amplitude') \
        .reshape([n_amp]+out_dim)

    if combinations=='within':
        result = np.array([pac.fit(
            phase[:,:,i,:],amplitude[:,:,i,:],method=method)
            for i,ch in enumerate(e.ch_names)
        ]).transpose(1,2,0,3).reshape(out_dim) # n_chan x n_amp x n_pha x n_time -> n_epochs x n_chan x n_time
    elif combinations=='across':
        result = np.array([[
            pac.fit(phase[:,:,ch_pha,:],amplitude[:,:,ch_amp,:],method=method
            ) for ch_pha in range(n_chans)] for ch_amp in range(n_chans)  # iterate over phase channel
        ])  # return (ch_amp x ch_pha x f_amp x f_pha x time)
    elif isinstance(combinations,list):
        result = np.array([
            pac.fit(phase[:, :, ch_pha, :], amplitude[:, :, ch_amp, :], method=method
                    ) for ch_pha,ch_amp in combinations  # iterate over channel combinations
        ])  # return (ch_pha/ch_amp x f_amp x f_pha x time)
    else:
        print("Parameter 'combinations' has unrecognized format.")
    return (pac,result)

conditions = tpac_cfg.conditions
combinations = tpac_cfg.combinations
method = tpac_cfg.method
fpha = tpac_cfg.f_phase
famp = tpac_cfg.f_amplitude
toi = tpac_cfg.toi[lock]
bsl = tpac_cfg.baseline[lock]

# 1. Load subject
epochs = load_subject(fname.subject_epo(subject=subject,lock=lock),bsl)
epochs.info['bads']=[] # reset bad channels, so they don't get dropped
# get tpac
for c,d in conditions.items():
    e = epochs[d]
    pac,res = get_pac(e,method,fph=fpha,famp=famp,combinations=combinations,padding=min(toi[0]-epochs.times[0],epochs.times[-1]-toi[1])*epochs.info['sfreq'])
    fpha = pac.f_pha; famp = pac.f_amp

    if combinations=='within':
        # put f_pha in metadata
        metadata = pd.DataFrame([pd.Series(data=np.tile([f[0] for f in fpha],len(famp)),name="lo_pha"),
                              pd.Series(data=np.tile([f[1] for f in fpha],len(famp)),name="hi_pha"),
                              pd.Series(data=np.repeat([f[0] for f in famp],len(fpha)),name="lo_amp"),
                              pd.Series(data=np.repeat([f[1] for f in famp],len(fpha)),name="hi_amp")]).transpose()
    elif combinations=='across':
        # put channels and f_pha in metadata
        metadata = pd.DataFrame([pd.Series(data='',),pd.Series(data='',name='f_amp'),pd.series(data='',name='ch_pha')])
    mne.EpochsArray(res,e.info,tmin=toi[0],metadata=metadata)\
        .save(fname.subject_tpac(subject=subject,lock=lock,lmin=fpha[0][0],
                                 lmax=fpha[-1][1],hmin=famp[0][0],hmax=famp[-1][1],
                                 method=method,combinations=combinations,condition=c),overwrite=True)



# make csv.gz with coherence data
# if time-resolved
# save as array of tfrs
# within as averagetfrs across