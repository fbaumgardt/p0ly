import argparse, mne, numpy as np, pandas as pd
from glob import glob

from config import fname, morlet_cfg, n_jobs
from functools import reduce

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument('subject',
                    help='The subject to create')
parser.add_argument('lock',
                    help='The subject to create')

args = parser.parse_args()
subject = args.subject
lock = args.lock
freqs = morlet_cfg.freqs
n_cycles = morlet_cfg.n_cycles
toi = morlet_cfg.toi.get(lock)
bsl = morlet_cfg.baseline.get(lock)
scale = morlet_cfg.scale
print(f'Frequency analysis (Morlet) for {subject} @ {lock}-lock')

epochs = mne.read_epochs(fname.subject_epo(subject=subject,lock=lock)).apply_baseline(bsl)
epochs.info['bads'] = []
tfr = mne.time_frequency.tfr_morlet(epochs,freqs,n_cycles,picks='eeg',output='complex',average=False,return_itc=False,n_jobs=n_jobs).crop(toi[0],toi[1])
tfr.save(fname.subject_morlet(subject=subject,lock=lock,fmin=freqs[0],fmax=freqs[-1],nsteps=len(freqs),scale=scale))