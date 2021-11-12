import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import argparse, mne, numpy as np, scipy as sp, tensorpac as tp

from config import fname, coh_cfg, n_jobs

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument('subject',
                    help='The subject to create')
parser.add_argument('lock',
                    help='The timelock to create')

args = parser.parse_args()
subject = args.subject
lock = args.lock
print(f'Coherence analysis for {subject}')

def load_subject(fname,baseline=(None,None),rereference=True):
    epochs = mne.read_epochs(fname)
    epochs.info['bads'] = []
    if rereference:
        # local reference skews coherence metrics
        epochs.set_eeg_reference()
    return epochs.pick('eeg',exclude=['TP10']).apply_baseline(baseline) if baseline is not None else epochs.pick('eeg',exclude=['TP10'])


# TODO: HOW DO I SPLIT BY CONDITIONS AND MAKE THEM ACCESSIBLE / DEFINE NAME FILES???
csd = coh_cfg.csd
epochs = load_subject(fname.subject_epo(subject=subject, lock=lock), coh_cfg.baseline[lock])
if csd:
    epochs = mne.preprocessing.compute_current_source_density(epochs,copy=False)
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
                    cwt_freqs=coh_cfg.freqs,
                    cwt_n_cycles=coh_cfg.n_cycles,
                    n_jobs=n_jobs
                )
                fmin=coh_cfg.freqs[0]
                fmax=coh_cfg.freqs[-1]
                t = con[2]
                dat = con[0]
            else:
                con = mne.connectivity.spectral_connectivity(
                    epochs[c],
                    method=m,
                    mode=n,
                    fmin=[f[0] for f in coh_cfg.freqs],
                    fmax=[f[1] for f in coh_cfg.freqs],
                    tmin=coh_cfg.toi[lock][0],
                    tmax=coh_cfg.toi[lock][1],
                    n_jobs=n_jobs
                )
                t = con[2][:1]
                dat = con[0][...,np.newaxis]
                fmin=coh_cfg.freqs[0][0]
                fmax=coh_cfg.freqs[-1][-1]
            mne.time_frequency.EpochsTFR(epochs.info,dat,t,con[1],method=m) \
            .save(fname.subject_connectivity(subject=subject,csd=".csd" if csd else "",lock=lock,fmin=fmin,fmax=fmax,
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