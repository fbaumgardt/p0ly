import numpy as np
import event_codes as codes
from .default import Cfg

## Conditions
conditions = {"corr1": "FeedbackType=='positive/size1'", "err1": "FeedbackType=='positive/size1'",
              "corr2": "FeedbackType=='positive/size2'", "err2": "FeedbackType=='positive/size2'",
              "corr4": "FeedbackType=='positive/size4'", "err4": "FeedbackType=='positive/size4'"}

##
event_codes=codes.multimodal()
locks=['stimulus','response','feedback']

##
firwin_freqs = [[1,100]]#[[a,b] for a,b in zip(range(2,59,2),range(4,61,2))] #[[1,1],[100,100]]  #np.round(np.exp(np.linspace(np.log(1),np.log(60),25)),1)
morlet_freqs = np.arange(8.,38.)#np.round(np.exp(np.linspace(np.log(1),np.log(80),30)),1)[5:]#np.round(np.exp(np.linspace(np.log(1),np.log(60),25)),1)
n_cycles = np.array([7]*10+[9]*10+[11]*10)#np.round(np.exp(np.linspace(np.log(2),np.log(12),25)))

config = Cfg(
    base_dir="/data/multimodal",
    raw=dict(ref_channels=["TP9","TP10"]),
    epo=dict(event_codes=event_codes,locks=locks),
    morlet=dict(freqs=morlet_freqs,n_cycles=n_cycles,decim=5,csd=False),
    firwin=dict(freqs=[[a,b] for a,b in zip(range(4,57,4),range(8,61,4))], scale='linear'),
    coherence=dict(locks=locks,baseline={'feedback':None},
                   n_cycles=n_cycles,modes=['multitaper'],csd=True),
    linear_model=dict(freqs=[[.5,20]],
                        formula="EEG ~ C(Modality)*Correctness*ResponseTimes + C(Modality)*Correctness*BlockPercent + "
                                "C(Modality)*Correctness*BlockIndex + C(Modality)*Correctness*Incorrect"),
    tpac=dict(conditions = conditions)
)
