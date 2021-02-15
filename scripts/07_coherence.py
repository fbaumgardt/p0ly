import argparse, mne, numpy as np, scipy as sp, tensorpac as tp

from config import fname, coh_cfg, morlet_cfg, firwin_cfg, epo_cfg, n_jobs

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
    epochs = mne.read_epochs(fname)
    epochs.info['bads'] = []
    if rereference:
        # local reference skews coherence metrics
        epochs.set_eeg_reference()
    return epochs.pick('eeg').apply_baseline(baseline)

# TODO: HOW DO I SPLIT BY CONDITIONS AND MAKE THEM ACCESSIBLE / DEFINE NAME FILES???

epochs = load_subject(fname.subject_epo(subject=subject, lock=lock), epo_cfg.baseline[lock])
for n in coh_cfg.modes:
    for m in coh_cfg.methods:
        for cond,c in coh_cfg.conditions.items():
            if n=="cwt_morlet":
                con = mne.connectivity.spectral_connectivity(
                    epochs[c],
                    method=m,
                    mode=n,
                    tmin=coh_cfg.toi[lock][0],
                    tmax=coh_cfg.toi[lock][1],
                    cwt_freqs=morlet_cfg.freqs,
                    cwt_n_cycles=morlet_cfg.n_cycles,
                    n_jobs=n_jobs
                )
                fmin=morlet_cfg.freqs[0]
                fmax=morlet_cfg.freqs[-1]
                t = con[2]
                dat = con[0]
            else:
                con = mne.connectivity.spectral_connectivity(
                    epochs[c],
                    method=m,
                    mode=n,
                    fmin=[f[0] for f in firwin_cfg.freqs],
                    fmax=[f[1] for f in firwin_cfg.freqs],
                    tmin=coh_cfg.toi[lock][0],
                    tmax=coh_cfg.toi[lock][1],
                    n_jobs=n_jobs
                )
                t = con[2][:1]
                dat = con[0][...,np.newaxis]
                fmin=firwin_cfg.freqs[0][0]
                fmax=firwin_cfg.freqs[-1][-1]
            mne.time_frequency.EpochsTFR(epochs.info,dat,t,con[1],method=m) \
            .save(fname.subject_connectivity(subject=subject,lock=lock,fmin=fmin,fmax=fmax,
                                             method=m,mode=n,condition=cond),overwrite=True)


"""
import mne, numpy as np, matplotlib.pyplot as plt
epochs = mne.read_epochs("/data/multimodal/multimodal001/multimodal001.stimulus-epo.fif.gz")
con = mne.connectivity.spectral_connectivity(
    epochs,
    method='coh',#'cohy','imcoh','plv','ciplv','ppc'],#,'pli','pli2_unbiased','wpli','wpli2_debiased'],
    mode='cwt_morlet',
    tmin=-.5,
    tmax=1.5,
    cwt_freqs=np.array([2,3,4,5,7,9,11,13,15,18,21,25,30,35,40,50,60]),
    cwt_n_cycles=np.array([3,3,3,3,5,5,5,5,7,7,7,7,9,9,9,9,9]),
    n_jobs=120
    )

"""