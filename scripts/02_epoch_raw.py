import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import argparse, mne, numpy as np, pandas as pd

from config import fname, epo_cfg
from functools import reduce

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument('subject',
                    help='The subject to create')
parser.add_argument('lock',
                    help='The timelock to apply')

args = parser.parse_args()
subject = args.subject
lock = args.lock
event_codes = epo_cfg.event_codes
toi = epo_cfg.toi.get(lock)
bsl = epo_cfg.baseline.get(lock)

#if not lock in event_codes.keys():
#    print("Ooopsie")

print(f'Epoching {subject} @ {lock}-lock')

invert_dict = lambda dct: {v:k for k,v in dct.items()}
get_all_types = lambda dct: dict(**dct.get('types',{}).get('main',{}),**dct.get('types',{}).get('aux',{}))
get_types_by_trial = lambda events, conf, lock: np.array(['/'.join([invert_dict(get_all_types(conf.get(lock,{}))).get(k) for k in e.keys() if k in get_all_types(conf.get(lock,{})).values()]) for e in events])

def _find_blocks(x, y):
    a = x[2];
    b = y;
    c = x[1];
    d = x[0]
    if a[0] == b[0]:  # block types
        if a[1] == 'begin':  # block position
            d.update({a[0]: d.get(a[0], 0) + 1})  # block number
            c = c + [(a[0], d[a[0]], a[2], b[2])]  # add block to list
        elif b[1] == 'end':
            d.update({b[0]: d.get(b[0], 0) + 1})
            c = c + [(b[0], d[b[0]], a[2], b[2])]
    else:
        if a[1] == 'begin' and b[1] == 'begin':
            d.update({a[0]: d.get(a[0], 0) + 1})  # block number
            c = c + [(a[0], d[a[0]], a[2], b[2])]  # add block to list
        elif a[1] == 'end' and b[1] == 'end':
            d.update({b[0]: d.get(b[0], 0) + 1})
            c = c + [(b[0], d[b[0]], a[2], b[2])]
    if b[2] == np.infty:
        return c
    else:
        return (d, c, b)


def _get_trial(events, einvs, begin_code, end_code, sample):
    begins = events[:sample]
    begins = begins[begins[:, 2] == begin_code, :]
    begins = begins[-1][0] if len(begins) else np.infty
    ends = events[sample:]
    ends = ends[ends[:, 2] == end_code, :]
    ends = ends[0][0] if len(ends) else 0
    events = events[np.logical_and(events[:, 0] >= begins, events[:, 0] <= ends)]
    return {einvs[e[2]]: e[0] for e in events}

def get_metadata(raw, cond, lock='stimulus'):
    """
    Use Condition definition to build metadata dataframe from MNE Raw Object.

    :param raw: RawType object
    :param cond: Condition definition in Dict/Json format (dict)
    :returns: Dataframe for use as Metadata object
    """
    evts, eids = mne.events_from_annotations(raw)
    einvs = {v: k for k, v in eids.items()}

    locks = cond.get(lock, {}).get('types', {}).get('main', {})
    lock_codes = [eids.get(v, -1) for v in locks.values()]
    lock_sample = np.array([[e[0], i, e[2]] for i, e in enumerate(evts) if e[2] in lock_codes])
    lock_type = np.array([lock for e in lock_sample[:, 2]])

    block_codes = {eids[w]: (k, l) for k, v in cond.get('block', {}).items() for l, w in v.items() if w in eids.keys()}
    block_events = [[block_codes[e[2]][0], block_codes[e[2]][1], e[0]] for e in evts if e[2] in block_codes.keys()]
    blocks = reduce(_find_blocks, block_events + [['', 'begin', np.infty]], ({}, [], ['', 'end', 0]))

    block_idx = [np.logical_and(lock_sample[:, 0] < b[3], lock_sample[:, 0] > b[2]) for b in blocks]
    block_type = reduce(np.char.add, [np.where(i, b[0], '') for i, b in zip(block_idx, blocks)], '')
    block_idx = np.sum([i * b[1] for i, b in zip(block_idx, blocks)], axis=0)

    events_by_trials = np.array(
        [_get_trial(evts[z[0]:z[2]], einvs, eids.get(cond.get('trial', {}).get('begin', 'Stim/-1'), -1),
                    eids.get(cond.get('trial', {}).get('end', 'Stim/-1'), -1), z[1] - z[0])
         for z in
         [(0, lock_sample[0, 1], lock_sample[1, 1])] + [z for z in zip(lock_sample[:-2, 1], lock_sample[1:-1, 1],
                                                                       lock_sample[2:, 1])] + [
             (lock_sample[-2, 1], lock_sample[-1, 1], len(evts))]])

    triggers = np.array(
        [np.max([e.get(t, 0) for t in cond.get('reaction', {}).get('begin', ['Stim/S -1'])]) for e in events_by_trials])
    responses = np.array(
        [np.min([e.get(t, np.infty) for t in cond.get('reaction', {}).get('end', ['Stim/S -1'])]) for e in
         events_by_trials])
    response_time = (responses - triggers) / raw.info['sfreq']

    stimulus_type, response_type, feedback_type = (get_types_by_trial(events_by_trials, cond, l) for l in
                                                   ['stimulus', 'response', 'feedback'])

    # response_valence = 1*np.array(['positive' in r for r in response_valence])-1*np.array(['negative' in r for r in response_valence])

    md = {'LockType': lock_type, 'LockSample': lock_sample[:, 0], 'BlockType': block_type,
          'BlockIndex': block_idx, 'StimulusType': stimulus_type, 'ResponseType': response_type,
          'ResponseTimes': response_time, 'FeedbackType': feedback_type, 'TrialEvents': events_by_trials}
    return pd.DataFrame(md)

def get_trialstatus(metadata,epochs):
    dropped = metadata[['LockSample']].merge(epochs.metadata[['LockSample']],how='outer',indicator=True)._merge.to_numpy()
    i=0;
    while dropped[i] != 'both':
        i+=1
    stim = np.arange(i,0,-1)*-1
    rest = np.zeros_like(dropped[i:])
    rest[dropped[i:]=='both']=np.arange(np.sum(dropped[i:]=='both'))+1
    return np.concatenate((stim,rest))

def get_epochs_with_metadata(raw,cond,tmin=-2.5,tmax=3.5,baseline=None,detrend=1,lock='stimulus'):
    if 'trial' in cond.keys():
        evts,eids = mne.events_from_annotations(raw)
        locks = cond.get(lock,{}).get('types',{}).get('main',{})
        event_id = {'/'.join([cond.get('condition','#'),k]).replace('#/',''):eids.get(v,-1) for k,v in locks.items() if v in eids.keys()}
        metadata = get_metadata(raw,cond,lock)
        evts = evts[np.sum([evts[:,2]==v for v in event_id.values()],axis=0)>0]
        epochs = mne.Epochs(raw,evts,event_id,tmin=tmin,tmax=tmax,baseline=baseline,detrend=detrend,metadata=metadata)
        epochs = epochs[epochs.metadata.TrialEvents.map(lambda d: np.any([k in cond.get('require', d.keys()) for k in d.keys()]))]
        return epochs
    else:
        epochs = [get_epochs_with_metadata(raw,c,tmin,tmax,baseline,detrend,lock) for c in cond.values()]
        metadata = pd.concat([e.metadata for e in epochs]).sort_values('LockSample')
        if metadata.size:
            epochs = [e.load_data() for e in epochs]
            epochs = mne.concatenate_epochs([e for e in epochs if len(e)],add_offset=False)
            metadata['TrialStatus'] = get_trialstatus(metadata,epochs)
        else:
            epochs = epochs[0]
        return (epochs[np.argsort(epochs.metadata.LockSample.to_numpy())],metadata)

raw = mne.io.read_raw_fif(fname.subject_raw(subject=subject),preload=True)

# TODO: split
epochs,metadata = get_epochs_with_metadata(raw,event_codes,tmin=toi[0],tmax=toi[1],baseline=bsl,lock=lock)

# TODO: Need to modularize/parameterize metadata parsing
if metadata.size:
    metadata['subject'] = subject
    #metadata['stimulation'] = con_inv[subj.split("/")[-2]]
    metadata['correct'] = metadata.apply(lambda x: '/correct' in x.ResponseType, axis=1)
    metadata['onoff'] = metadata.apply(lambda x: 'on' if x.TrialStatus < 0 else 'off', axis=1)

epochs.save(fname.subject_epo(subject=subject,lock=lock),overwrite=True)
metadata.to_csv(fname.subject_csv(subject=subject))