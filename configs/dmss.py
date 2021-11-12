import numpy as np
import event_codes as codes
from .default import Cfg

## Conditions
conditions = {"corr1": "FeedbackType=='positive/size1'", "err1": "FeedbackType=='negative/size1'",
              "corr2": "FeedbackType=='positive/size2'", "err2": "FeedbackType=='negative/size2'",
              "corr4": "FeedbackType=='positive/size4'", "err4": "FeedbackType=='negative/size4'"}

## Epoching
event_codes=codes.dmss()
locks=['stimulus','delay','probe','response','feedback']
toi = {'stimulus':(-2.5,7),'delay':(-2.5,5),'probe':(-2.5,3.5),'response':(-2.5,3.5),'feedback':(-2.5,3.5)}
bsl = {'stimulus':None,'delay':None,'probe':None,'response':None,'feedback':None}

## Filtering
firwin_freqs = [[1,1],[100,100]]  #np.round(np.exp(np.linspace(np.log(1),np.log(60),25)),1)

firwin_freqs = [np.array([a,b])+.5 for a,b in zip(range(1,60,2),range(2,61,2))]
firwin_toi = {'stimulus':(-.5,5),'delay':(-.5,3),'probe':(-.5,1.5),'response':(-1.2,1),'feedback':(-.5,1.5)}
morlet_freqs = np.round(np.exp(np.linspace(np.log(1),np.log(60),25)),1)
n_cycles = np.round(np.exp(np.linspace(np.log(2),np.log(12),25)))

config = Cfg(
    base_dir="/data/dmss",
    raw=dict(ref_channels=["TP9","TP10"]),
    epo=dict(event_codes=event_codes,locks=locks,toi=toi,baseline=bsl),
    morlet=dict(freqs=morlet_freqs,n_cycles=n_cycles,decim=5,csd=False),
    firwin=dict(freqs=firwin_freqs,
                  toi=firwin_toi,scale='linear', bandwidth=1),
    coherence=dict(locks=['stimulus'],freqs=firwin_freqs,n_cycles=n_cycles,modes=['multitaper']),
    linear_model=dict(freqs=[[.5,20]],
                        formula="EEG ~ C(Modality)*Correctness*ResponseTimes + C(Modality)*Correctness*BlockPercent + "
                                "C(Modality)*Correctness*BlockIndex + C(Modality)*Correctness*Incorrect"),
    tpac=dict(conditions = conditions)
)
