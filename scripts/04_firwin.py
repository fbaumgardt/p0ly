import argparse, mne, numpy as np

from config import fname, n_jobs, firwin_cfg as cfg

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument('subject',
                    help='The subject to create')
parser.add_argument('lock',
                    help='The timelock to apply')

args = parser.parse_args()
subject = args.subject
lock = args.lock
scale = cfg.scale
freqs = cfg.freqs
toi = cfg.toi.get(lock)
bsl = cfg.baseline.get(lock)
print(f'Frequency analysis (FIRWIN) for {subject} @ {lock}-lock')

epochs = mne.read_epochs(fname.subject_epo(subject=subject,lock=lock)).apply_baseline(bsl).pick('eeg')
epochs.info['bads'] = []
tfr = np.array([epochs.copy().filter(f[0],f[1],n_jobs=n_jobs).get_data() for f in freqs]).transpose(1,2,0,3)
tfr = mne.time_frequency.EpochsTFR(epochs.info,tfr,epochs.times,[np.mean(f) for f in freqs],events=epochs.events,event_id=epochs.event_id,metadata=epochs.metadata).crop(toi[0],toi[1])
tfr.save(fname.subject_firwin(subject=subject,lock=lock,fmin=np.mean(freqs[0]),fmax=np.mean(freqs[-1]),nsteps=len(freqs),scale=scale),overwrite=True)