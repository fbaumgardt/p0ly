from dataclasses import dataclass, field
from typing import List, Tuple

###############################################################################
# These are all the configuration classes.

@dataclass
class Cfg:
    base_dir: str = field(default_factory=lambda:"")
    raw: dict = field(default_factory=lambda:{})
    epo: dict = field(default_factory=lambda:{})
    morlet: dict = field(default_factory=lambda:{})
    firwin: dict = field(default_factory=lambda:{})
    coherence: dict = field(default_factory=lambda:{})
    linear_model: dict = field(default_factory=lambda:{})
    tpac: dict = field(default_factory=lambda:{})


@dataclass
class RawCfg:
    decim: int = 1
    detrend_fmin: float = .1  # None
    detrend_fmax: float = 250 # None
    stimulation: bool = False
    ref_channels: List[str] = field(default_factory=list)  # empty list = average reference


@dataclass
class EpoCfg:
    toi: dict = field(default_factory=lambda: {"stimulus": (-2.5, 3.5), "response": (-2.5, 3.5),
                                               "feedback": (-2.5, 3.5), "delay": (-2.5, 5.5)})
    baseline: dict = field(default_factory=lambda: {"stimulus": (-.2, 0), "response": (-.2, 0), "feedback": (-.2, 0),"delay": (-.2,0)})
    locks: List[str] = field(default_factory=lambda: ["stimulus", "response", "feedback"])
    event_codes: dict = field(default_factory=dict)


@dataclass
class MorletCfg:
    toi: dict = field(default_factory=lambda:{"stimulus": (-.5, 1.5), "response": (-.5, 1.5),
                                              "feedback": (-.5, 1.5), "delay": (-.5, 3.5)})
    baseline: dict = field(default_factory=lambda:{"stimulus": (-.2, 0), "response": (-.2, 0), "feedback": (-.2, 0),"delay": (-.2,0)})
    freqs: List[float] = field(default_factory=lambda:[[0]])
    n_cycles: List[float] = field(default_factory=lambda:[[0]])
    scale: str = "log"  # log, linear
    decim: int = 1
    csd: bool = False


@dataclass
class FirwinCfg:
    toi: dict = field(default_factory=lambda:{"stimulus": (-.5, 1.5), "response": (-.5, 1.5),
                                              "feedback": (-.5, 1.5), "delay": (-.5, 3.5)})
    baseline: dict = field(default_factory=lambda:{"stimulus": (-.2, 0), "response": (-.2, 0), "feedback": (-.2, 0),"delay": (-.2,0)})
    freqs: List[float] = field(default_factory=lambda:[[2,4],[4,8],[8,13],[13,30],[30,60],[60,100]])  # empty list = canonical frequency bands
    scale: str = "canonical"  # canonical, linear, log
    bandwidth: float = 0


@dataclass
class CoherenceCfg:
    locks: List[str] = field(default_factory=lambda: ["stimulus", "response", "feedback"])
    freqs: List = field(
        default_factory=lambda: [[1, 4], [4, 8], [8, 13], [13, 20], [20, 30], [30, 50], [50, 100]])
    n_cycles: List[float] = field(default_factory=[3])
    methods: List[str] = field(default_factory=lambda:['coh','cohy','imcoh','plv','ciplv','ppc','pli','pli2_unbiased','wpli','wpli2_debiased'])
    modes: List[str] = field(default_factory=lambda: ['multitaper','cwt_morlet'])
    toi: dict = field(default_factory=lambda:{"stimulus": (0, 1), "response": (0, 1),
                                              "feedback": (0, 1), "delay": (0, 3)})
    baseline: dict = field(
        default_factory=lambda: {"stimulus": (-.2, 0), "response": (-.2, 0), "feedback": (-.2, 0), "delay": (-.2, 0)})
    conditions: dict = field(default_factory=lambda: {'correct': 'FeedbackType=="positive"',
                                                      'error': 'FeedbackType=="negative"'})
    csd: bool = False

@dataclass
class tPACCfg:
    toi: dict = field(default_factory=lambda:{"stimulus": (-.5, 1.5), "response": (-.5, 1.5),
                                              "feedback": (-.5, 1.5), "delay": (-.5, 3.5)})
    baseline: dict = field(default_factory=lambda:{"stimulus": (-.2, 0), "response": (-.2, 0), "feedback": (-.2, 0), "delay": (-.2, 0)})
    f_phase: list = field(default_factory=lambda:[[2,4],[4,6],[6,8],[8,10],[10,12]])
    f_amplitude: list = field(default_factory=lambda:[[12,16],[16,20],[20,24],[24,28],[28,32],[32,36],[36,40],[40,44],[44,48],[48,52],[52,56],[56,60],[60,64],[64,68],[68,72],[72,76],[76,80]])
    conditions: dict = field(default_factory=lambda:{"all":"LockSample>0"})
    method: str = field(default_factory=lambda:'gc') # gc | circular
    combinations: str = field(default_factory=lambda:'within') # within | across | list of channel pairs


@dataclass
class GLMCfg:
    formula: str = field(default_factory=lambda:"EEG ~ C(Modality)*Correctness*ResponseTimes + C(Modality)*Correctness*BlockPercent + C(Modality)*Correctness*Delay + C(Modality)*Correctness*C(model_family)")
    toi: dict = field(default_factory=lambda:{"stimulus": (-.5, 1.5), "response": (-.5, 1.5),
                                              "feedback": (-.5, 1.5), "delay": (-.5, 3.5)})
    baseline: dict = field(default_factory=lambda:{"stimulus": (-.2, 0), "response": (-.2, 0), "feedback": (-.2, 0)})
    freqs: List[List[float]] = field(default_factory=lambda:[[1,4],[4,8],[8,13],[13,20],[20,30],[30,50],[50,100]])  # empty list = canonical frequency bands
    scale: str = "canonical"  # canonical, linear, log
    decim: int = 10
    n_subj: int = None

@dataclass
class CondCFG:
    toi: dict = field(default_factory=lambda:{"stimulus": (-.5, 1.5), "response": (-.5, 1.5),
                                              "feedback": (-.5, 1.5), "delay": (-.5, 3.5)})
    baseline: dict = field(default_factory=lambda:{"stimulus": (-.2, 0), "response": (-.2, 0), "feedback": (-.2, 0), "delay": (-.2, 0)})
    locks: List[str] = field(default_factory=lambda: ["stimulus", "response", "feedback"])
    freqs: list = field(default_factory=lambda:[[2,4],[4,6],[6,8],[8,10],[10,12]])
    conditions: dict = field(default_factory=lambda:{
        'all': lambda x: x,
        'visual': lambda x: x['visual'],
        'auditive': lambda x: x['auditive'],
        'visual/left': lambda x: x['visual/left'],
        'visual/right': lambda x: x['visual/right'],
        'auditive/left': lambda x: x['auditive/left'],
        'auditive/right': lambda x: x['auditive/right'],

    })