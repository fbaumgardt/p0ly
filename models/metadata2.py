import numpy as np, pandas as pd
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

def get_incorrects(sti,coi):
    for i,s in enumerate(sti):
        last_coi = (coi[coi<s])[-1] if np.any(coi<s) else -1
        yield(len([t for t in sti if t<s and t>last_coi]) if last_coi>=0 else np.infty)

def add_incorrect(df):
    holder = np.array([0.]*len(df))
    for bt in ['auditive/left','auditive/right','visual/left','visual/right',]: # BlockType
        sta = (df.BlockType.to_numpy()==bt)
        for bi in [0,1,2,3,4,5,6,7,8]: # BlockIndex
            stb = sta & (df.BlockIndex.to_numpy()==bi)
            for st in (['250','500','1000','2000','0','45','90','135']):
                stc = stb & (df.StimulusType.to_numpy()==st) # stc: boolean mask for bt&bi&st
                sti = np.where(stc)[0] # sti: indices for stc
                coi = np.where(stc & (df.FeedbackType.to_numpy()=='positive'))[0] # coi: indices for correct
                holder[sti] = np.array(list(get_incorrects(sti,coi)))
    df['Incorrect'] = holder
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

def add_blockpercent(df, blocks=None):
    blocks = zip(['visual/right', 'visual/right', 'visual/left', 'visual/left', 'auditive/right', 'auditive/right',
                 'auditive/left', 'auditive/left'], [1, 2, 1, 2, 1, 2, 1, 2])
    # blocks = zip(["dmss"]*df.BlockIndex.max(),range(1,df.BlockIndex.max()+1))
    df['BlockPercent'] = np.sum([get_trial_pos_in_block(a, b, df) for a, b in blocks], axis=0)
    df['BlockPercent'] = df.apply(lambda x: float(x.BlockPercent),axis=1)
    return df


def add_md(e):
    e.metadata = add_incorrect(add_delay(add_blockpercent(add_correctness(add_modality(add_subject(e.metadata, e.filename.split("/")[-2]))))))
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