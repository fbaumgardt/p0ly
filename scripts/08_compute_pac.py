import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import argparse, mne, numpy as np, scipy as sp, tensorpac as tp

from config import fname, pac_cfg

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


def get_pac(e, pac=(2,0,0), fph=(3,15,2,2), famp=(16,105,8,8)):  # (phase-chan, amp-chan, trial, phase-freq, amp-freq)
    pac = tp.Pac(pac, fph, famp)

    # get params ready
    n_samples=e.get_data().shape[-1];n_chans=len(e.ch_names);padding = 2000;n_amp=len(pac.f_amp);n_pha=len(pac.f_pha);
    in_dim = [-1,n_samples]; out_dim = [-1,n_chans,n_samples-2*padding]

    # filter phase and amplitude signals
    phase = pac.filter(e.info['sfreq'],e.get_data().reshape(in_dim),edges=padding,ftype='phase') \
        .reshape([n_pha]+out_dim)
    amplitude = pac.filter(e.info['sfreq'],e.get_data().reshape(in_dim),edges=padding,ftype='amplitude') \
        .reshape([n_amp]+out_dim)

    return np.transpose([
        pac.fit(
            np.tile(phase[:,:,ch:ch+1,:], [1,1,n_chans,1]).reshape([n_pha,-1,out_dim[-1]]),  # phase signal for one channel
            amplitude.reshape([n_amp,-1,out_dim[-1]])  # amplitude signal for all channels

        ).reshape([n_amp,n_pha,-1,n_chans]) for ch in range(n_chans)  # iterate over phase channel
    ], [3,2,1,0,4])  # return (trials x f_pha x f_amp x ch_pha x ch_amp)

# 1. Load subject
epochs = load_subject(fname.epoch(subject,lock),(-.3,-.1))
# get pac
get_pac(epochs)
# if collapsed over trial
# make csv.gz with coherence data
# if time-resolved
# save as array of tfrs
