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
        epochs.set_eeg_reference('mean')
    return epochs


def get_pac(e, method='gc', fph=[[2,4],[4,8],[8,13]], famp=[[13,20],[20,30],[30,45],[45,60]], combinations='within', padding=2000, pac_kwargs={}):
    pac = tp.EventRelatedPac(fph, famp, **pac_kwargs)

    # get params ready
    n_samples=e.get_data().shape[-1];n_chans=len(e.ch_names);n_amp=len(pac.f_amp);n_pha=len(pac.f_pha);
    in_dim = [-1,n_samples]; out_dim = [-1,n_chans,n_samples-2*padding]

    # filter phase and amplitude signals
    phase = pac.filter(e.info['sfreq'],e.get_data().reshape(in_dim),edges=padding,ftype='phase') \
        .reshape([n_pha]+out_dim)
    amplitude = pac.filter(e.info['sfreq'],e.get_data().reshape(in_dim),edges=padding,ftype='amplitude') \
        .reshape([n_amp]+out_dim)

    if combinations=='within':
        result = np.array([pac.fit(
            phase[:,:,i,:],amplitude[:,:,i,:],method=method)
            for i,ch in enumerate(e.ch_names)
        ]) # n_chan x n_amp x n_pha x n_time
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

combinations = tpac_cfg.combinations
method = tpac_cfg.method
fpha = tpac_cfg.f_phase
famp = tpac_cfg.f_amplitude
toi = tpac_cfg.toi[lock]
bsl = tpac_cfg.baseline[lock]

# 1. Load subject
epochs = load_subject(fname.epoch(subject,lock),bsl)
epochs.info['bads']=[] # reset bad channels, so they don't get dropped
# get tpac

pac,res = get_pac(epochs,method,combinations=combinations,padding=min(toi[0]-epochs.times[0],epochs.times[1]-toi[1])*epochs.info['sfreq'])
fpha = pac.f_pha; famp = pac.f_amp

if combinations=='within':
    # put f_pha in metadata
    metadata = pd.concat([pd.Series(data=np.tile(fpha,len(famp)),name="f_pha"),pd.Series(data=np.repeat(famp,len(fpha)),name="f_amp")])
elif combinations=='across':
    # put channels and f_pha in metadata
    metadata = pd.concat([pd.Series(data='',),pd.Series(data='',name='f_amp'),pd.series(data='',name='ch_pha')])
mne.EpochsArray(res,epochs.info,tmin=epochs.times,metadata=metadata)\
    .save(fname.subject_tpac(subject=subject,lock=lock,method=method,combinations=combinations),overwrite=True)



# make csv.gz with coherence data
# if time-resolved
# save as array of tfrs
# within as averagetfrs across