import argparse, mne, numpy as np, scipy as sp
from glob import glob
from config import fname, raw_cfg

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument('subject',
                    help='The subject to create')

args = parser.parse_args()
subject = args.subject
print(f'Preprocessing {subject}')

subject_dir = fname.subject_dir(subject=subject)
vhdrs = glob(f"{subject_dir}/*.vhdr")

def rereference(inst,refs='average'):
    if isinstance(refs,list):
        for ch in refs:
            if not ch in inst.info['ch_names']:
                mne.add_reference_channels(inst,ch,copy=False)
    return inst.set_eeg_reference(refs)

def ica_cleanup(raw,filter=[1,40],decim=10,components=20,tmin=100.):
    ica = mne.preprocessing.ICA(max_pca_components=components).fit(raw.copy().crop(tmin=tmin).filter(*filter),decim=decim);
    a = [None]*4
    a[0]=ica.find_bads_eog(raw,ch_name='BVEOG',start=tmin,stop=np.min([tmin+1000.,raw.times[-1]]))[0]
    a[1]=ica.find_bads_eog(raw,ch_name='TVEOG',start=tmin,stop=np.min([tmin+1000.,raw.times[-1]]))[0]
    a[2]=ica.find_bads_eog(raw,ch_name='RHEOG',start=tmin,stop=np.min([tmin+1000.,raw.times[-1]]))[0]
    a[3]=ica.find_bads_eog(raw,ch_name='LHEOG',start=tmin,stop=np.min([tmin+1000.,raw.times[-1]]))[0]
    ica.exclude = list(set([c for b in a for c in b]))
    return (ica.apply(raw),ica)

def minmax_zscore(inst,axis='channels',threshold=3.,max_iter=1,mask=lambda x:[False]*len(x)):#:
    if axis == 'time':
        inst = np.mean(inst.get_data(),axis=1)
    else:
        inst = inst.get_data()
    X = np.max(inst, axis=-1) - np.min(inst, axis=-1)
    mask = mask(X)
    for _ in range(max_iter):
        Y = np.ma.masked_array(X,mask)
        mn = np.mean(Y); sd = np.std(Y)
        mask = np.abs((X-mn)/sd)>3
    return mask

def fix_channels(raw,threshold=3,max_iter=1):
    r = raw.copy()
    r.info['bads'] = np.unique(np.concatenate((np.array(r.info['bads']),np.array(r.ch_names)[minmax_zscore(r,threshold=threshold,max_iter=max_iter)]))).tolist()
    r.interpolate_bads(reset_bads=False)
    return r

def artefact_rejection(r,threshold=3.,max_iter=3,duration=.5,stimulation=False):
    mask = lambda x:[True]*int(np.floor(len(x)/2))+[False]*(len(x)-int(np.floor(len(x)/2))) if stimulation else lambda x: [False]*len(x)
    epo = mne.make_fixed_length_epochs(r,duration=duration,reject_by_annotation=False)
    bad_starts = epo.events[minmax_zscore(epo,axis='time',threshold=threshold,max_iter=max_iter,mask=mask),0]/epo.info['sfreq']
    return mne.Annotations(bad_starts,duration,"bad_minmax_zscore",orig_time=r.annotations.orig_time)
chs = ['TVEOG', 'Fz', 'F3', 'F7', 'LHEOG', 'FC5', 'FC1', 'C3', 'T7', 'TP9', 'CP5', 'CP1', 'Pz', 'P3', 'P7', 'O1', 'Oz', 'O2', 'P4', 'P8', 'CP6', 'CP2', 'Cz', 'C4', 'T8', 'RHEOG', 'FC6', 'FC2', 'F4', 'F8', 'BVEOG', 'AF7', 'AF3', 'AFz', 'F1', 'F5', 'FT7', 'FC3', 'C1', 'C5', 'TP7', 'CP3', 'P1', 'P5', 'PO7', 'PO3', 'POz', 'PO4', 'PO8', 'P6', 'P2', 'CPz', 'CP4', 'TP8', 'C6', 'C2', 'FC4', 'FT8', 'F6', 'AF8', 'AF4', 'F2', 'FCz', 'TP10']

# 1. load and merge brainvision files
r = [mne.io.read_raw_brainvision(file, eog=["TVEOG","BVEOG","LHEOG","RHEOG"], preload=True) for file in vhdrs]
r = mne.concatenate_raws(r)
# 2. rereference (reminder to rereference to 'average' before source localization)
r = rereference(r,raw_cfg.ref_channels) if len(raw_cfg.ref_channels) else rereference(r)
r.reorder_channels(chs)
if r.info['dig']==None:
    r.pick(['eeg','eog']).set_channel_types({'TVEOG':'eog','BVEOG':'eog','RHEOG':'eog','LHEOG':'eog'}).set_montage('easycap-M1');
# 3. find and interpolate bad channels
r = fix_channels(r)
# 4. find and remove ICA components
old_bads = r.info['bads'];r.info['bads']=[] # run ICA on all channels
r,ica = ica_cleanup(r)
# 5. another bad channel run and combine results
r = fix_channels(r)
r.info['bads'] = np.unique(old_bads+r.info['bads']).tolist()
# 6. mark bad segments
r.set_annotations(r.annotations + artefact_rejection(r,stimulation=raw_cfg.stimulation))
# 7. save raw and ica
r.save(fname.subject_raw(subject=subject),overwrite=True)
ica.save(fname.subject_ica(subject=subject),)
