import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import argparse, mne

from config import fname, morlet_cfg, n_jobs

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
decim = morlet_cfg.decim
csd = morlet_cfg.csd
print(f'Frequency analysis (Morlet) for {subject} @ {lock}-lock')

epochs = mne.read_epochs(fname.subject_epo(subject=subject,lock=lock)).apply_baseline(bsl)
epochs.info['bads'] = []
epochs.pick('eeg',exclude=['TP10'])
epochs,rest = mne.set_eeg_reference(epochs)
file = fname.subject_morlet(subject=subject,csd=".csd" if csd else "",lock=lock,fmin=freqs[0],fmax=freqs[-1],nsteps=len(freqs),scale=scale)
if csd:
    epochs = mne.preprocessing.compute_current_source_density(epochs,copy=False)
tfr = mne.time_frequency.tfr_morlet(epochs,freqs,n_cycles,output='complex',average=False,return_itc=False,n_jobs=n_jobs,decim=decim).crop(toi[0],toi[1])
tfr.save(file,overwrite=True)