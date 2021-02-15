import argparse, mne, statsmodels.api as sm, numpy as np, pandas as pd, hashlib as hl
from time import time as tm
from glob import glob
from joblib import Parallel, delayed
from config import firwin_cfg, glm_cfg, fname, n_jobs, subj_prefix, subjects

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument('lock',
                    help='The timelock to create')

args = parser.parse_args()
lock = args.lock
print(f'Single-trial analysis for {subj_prefix} @ {lock}')

factor_fn = {'Modality': lambda x: (x['Modality']=='visual')*1-(x['Modality']=='auditive')*1,
             'Visual': lambda x: (x['Modality']=='visual')*1,
             'Auditory': lambda x: (x['Modality']=='auditive')*1,
             'FeedbackType': lambda x: (x['FeedbackType']=='positive')*1-(x['FeedbackType']=='negative')*1,
             'BlockTime': lambda x: (x['BlockPosition']=='Begin')*1-(x['BlockPosition']=='End')*1,
             'Intercept': lambda x: np.ones((len(x),))
            }

models = {"multimodal033":[13]+[18]*7+[20,20,18,18,18,17,18,13],
"multimodal029":[18]*8+[12,18,18,18,17,18,18,8],
"multimodal004":[18]*8+[12,18,18,18],
"multimodal027":[18,18,18,18,16,18,8,11,18,18,13,8,14,14,8,8],
"multimodal030":[18,18,8]+[18]*13,
"multimodal024":[18]*5+[16,18,18,17,18,18,13,12,18,18,18],
"multimodal031":[18,16]+[18]*10+[12,17,18,18],
"multimodal003":[18]*7+[8]+[18]*5+[17,18,18],
"multimodal025":[16]+[18]*7+[17]+[18]*7,
"multimodal018":[13]+[18]*6+[17,18,16,18,18,16,18,18,18],
"multimodal017":[18,18,18,12,2,18,18,18,15,18,18,18,18,18,18,18],
"multimodal021":[8,18,18,4,18,18,18,13,4,18,18,8,17,18,12,8],
"multimodal023":[18,18,18,18,18,18,18,18,18,18,18,13,18,18,18,18],
"multimodal016":[18,18,18,16,18,16,18,13,18,18,18,18],
"multimodal013":[18,18,18,18,18,18,18,18,18,18,18,18,16,18,18,18],
"multimodal006":[18,18,18,18,18,16,18,18,12,18,18,18,12,18,18,13],
"multimodal028":[18,18,18,8,18,18,18,18,18,18,18,18,18,18,18,18],
"multimodal014":[2,18,16,18,18,18,18,18,18,18,18,18,18,18,18,13],
"multimodal007":[8,18,16,18,18,18,18,8,18,18,18,4,18,16,16,13],
"multimodal019":[18,16,2,13,18,18,18,18,18,8,18,13,12,18,18,13]}

def sample_lmm(f,d,lmm_kwargs={}):
    return sm.MixedLM.from_formula(f, d, groups='Subject', **lmm_kwargs).fit()

def channel_lmm(formula, data, design, ch_name="", n_jobs=1):
    s = tm()
    print(f"Computing linear model for {ch_name}")
    res = Parallel(n_jobs=n_jobs)(delayed(sample_lmm)(formula, design.assign(EEG=data[:, s])) for s in range(data.shape[1]))
    print("Finished in {:.0f}s:".format(tm() - s))
    return res

def group_lmm(epochs, formula, lmm_kwargs={}, n_jobs=1):
    """Compute linear mixed model with factors on multiple Epochs data sets"""
    data = np.vstack([ep.get_data() for ep in epochs])
    design = reduce_columns(pd.concat([e.metadata for e in epochs]),formula)
    lmms = [channel_lmm(formula,data[:,ch,:],design,epochs[0].ch_names[ch],n_jobs) for ch in range(data.shape[1])]
    return lmms

def reduce_columns(df,formula):
    return df.loc[:,[c for c in df.columns if c in formula+"Subject"]]

def add_delay(df):
    holder = np.array([0.]*len(df))
    for bt in ['auditive/left','auditive/right','visual/left','visual/right',]: # BlockType
        sta = (df.BlockType.to_numpy()==bt)
        for bi in [0,1,2,3,4,5,6,7,8]: # BlockIndex
            stb = sta & (df.BlockIndex.to_numpy()==bi)
            for st in (['250','500','1000','2000','0','45','90','135']):
                stc = stb & (df.StimulusType.to_numpy()==st) # stc: boolean mask for bt&bi&st
                sti = np.where(stc)[0] # sti: indices for stc
                coi = np.where(stc & (df.FeedbackType.to_numpy()=='positive'))[0] # coi: indices for correct
                holder[sti] = np.array([(s-coi[coi<s][-1]) if np.any(coi<s) else np.infty for s in sti])
    df['Delay'] = holder
    return df

def add_modality(df):
    return df.assign(Modality=df.apply(lambda x: x.BlockType.split("/")[0],axis=1))

def add_correctness(df):
    return df.assign(Correctness=df.apply(lambda x: (x.FeedbackType=='positive')*1.,axis=1))

def get_trial_pos_in_block(block_type,block_index,df,pos=None):
    pos = np.zeros_like(df.BlockType)*0.
    mask = np.logical_and(df.BlockType==block_type,df.BlockIndex==block_index)
    pos[mask] = (np.arange(np.sum(mask))+1)/np.sum(mask)
    return pos

def add_blockpercent(df, zippy=None):
    zippy = zip(['visual/right', 'visual/right', 'visual/left', 'visual/left', 'auditive/right', 'auditive/right',
                 'auditive/left', 'auditive/left'], [1, 2, 1, 2, 1, 2, 1, 2])
    # zippy = zip(["dmss"]*df.BlockIndex.max(),range(1,df.BlockIndex.max()+1))
    df['BlockPercent'] = np.sum([get_trial_pos_in_block(a, b, df) for a, b in zippy], axis=0)
    df['BlockPercent'] = df.apply(lambda x: float(x.BlockPercent),axis=1)
    return df

def add_subject(df,s):
    return df.assign(Subject=s)

def add_md(e):
    e.metadata = add_delay(add_blockpercent(add_correctness(add_modality(add_subject(e.metadata, e.filename.split("/")[-2])))))
    return e

def add_subblock(df):
    types = [df.BlockType.unique()[:2],df.BlockType.unique()[2:]]
    arr = np.zeros_like(df.BlockType)
    subblocks = [slice(0,25),slice(25,50),slice(50,100),slice(100,None)]
    for i in [0,1]:
        for j in [0,1]:
            idx = np.array([1,2,3,4])+4*j+8*i;
            coords = np.where((df.BlockIndex==i+1) & (df.BlockType.isin(types[j])))[0]
            for r,s in zip(idx,subblocks):
                arr[coords[s]]=r
    return df.assign(subblock=arr)

def add_model_types(df,model_types):
    df = add_subblock(df)
    return df.assign(model_type=df.apply(lambda d:model_types[d.subblock-1],axis=1))

def add_sep_shared(df):
    return df.assign(parameters=df.apply(lambda d: "separate" if d.model_type in [13,15,17] else "shared",axis=1))

def add_model_family(df):
    return df.assign(model_family=df.apply(lambda d: "WM" if d.model_type in [15,16,17,18] else "RL" if d.model_type in [3,4,11,12,13,14,19,20] else "RLWM",axis=1))

def add_more_md(e):
    subj = e.filename.split("/")[-2]
    df = add_model_types(e.metadata,models[subj])
    df = add_model_family(add_sep_shared(df))
    e.metadata=df
    return e


subjects_epo = [fname.subject_epo(subject=subject,lock=lock) for subject in subjects if pd.read_csv(fname.subject_csv(subject=subject)).size and subject in models.keys()]

freqs = glm_cfg.freqs
tmin,tmax = glm_cfg.toi[lock]
bsl = glm_cfg.baseline[lock]
decim = glm_cfg.decim
n_subj = glm_cfg.n_subj
formula = glm_cfg.formula
model_id = hl.md5(glm_cfg.formula.encode('UTF-8')).hexdigest()[:6]

print(f"Computing {formula}")
originals = [e for e in Parallel(n_jobs=n_jobs)(delayed(mne.read_epochs)(f) for f in subjects_epo) if len(e)>0]
originals.sort(key=lambda x: len(x), reverse=True)
originals = [add_more_md(add_md(o)) for o in originals]


#originals = [o for o in originals if len(o)>1000 and np.mean(o.metadata.FeedbackType.to_numpy()=='positive')>.5]

print(f"NUMBER OF SUBJECTS: {len(originals)}")

for fmin,fmax in freqs:#[(4,8),(8,12),(13,20),(20,30),(30,45),(45,60),(60,90)]:
        print("Filtering epochs")
        filtering = lambda e: e['ResponseTimes>0 & Delay>0 & Delay<inf'].pick('eeg').filter(fmin,fmax).apply_hilbert(envelope=True).apply_baseline(bsl).crop(tmin,tmax).decimate(decim)
        epochs = Parallel(n_jobs=n_jobs)(delayed(filtering)(e) for e in originals)

        print("Filtered {}-{}Hz".format(fmin,fmax))
        lmms = group_lmm(epochs,formula,n_jobs=n_jobs)
        #print("Model computed in {:.2f}s".format())
        params = np.transpose([[m.params.to_numpy() for m in l] for l in lmms],axes=[2,0,1])
        pvalues = np.transpose([[m.pvalues.to_numpy() for m in l] for l in lmms],axes=[2,0,1])

        md = ["param/{}".format(x) for x in lmms[0][0].params.index.to_numpy()]+["pvalue/{}".format(x) for x in lmms[0][0].pvalues.index.to_numpy()]
        mne.EpochsArray(np.vstack([params,pvalues]),epochs[0][:len(md)].info,
                        tmin=epochs[0].times[0],events=[[i+1,0,i+1] for i in range(len(md))],
                        event_id={md[i]:i+1 for i in range(len(md))}
                       ).save(fname.regression(subj_prefix=subj_prefix,lock=lock,fmin=fmin,fmax=fmax,model_id=model_id),overwrite=True)
