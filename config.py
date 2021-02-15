"""
===========
Config file
===========
Configuration parameters for the study.
"""

import os, getpass, json as js, numpy as np
from socket import getfqdn
from fnames import FileNames
from glob import glob
from dataclasses import dataclass, field
from typing import List, Tuple
import event_codes as codes

def group_subjects(subjs):
    if len(subjs):
        acc = [s for s in subjs if subjs[0] in s]
        rest = [s for s in subjs if not subjs[0] in s]
        return [acc]+group_subjects(rest)
    else:
        return []


###############################################################################
# Determine which user is running the scripts on which machine and set the path
# where the data is stored and how many CPU cores to use.

user = getpass.getuser()  # Username of the user running the scripts
host = getfqdn()  # Hostname of the machine running the scripts
mmdl = "/data/multimodal"
# You want to add your machine to this list
if host == 'Device.local':
    # My laptop
    bv_data_dir = f'.{mmdl}'
    n_jobs = 2  # My laptop has 2 cores
elif host == 'titan.amherst':
    # My workstation
    bv_data_dir = mmdl
    n_jobs = 64  # My workstation has 128 cores
elif user == 'fbaumgardt':
    # Personal defaults
    bv_data_dir = f'.{mmdl}'
    n_jobs = 1
else:
    # Defaults
    bv_data_dir = f'.{mmdl}'
    n_jobs = 1

# For BLAS to use the right amount of cores
os.environ['OMP_NUM_THREADS'] = str(n_jobs)

###############################################################################
# These are all the configuration classes.


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


@dataclass
class FirwinCfg:
    toi: dict = field(default_factory=lambda:{"stimulus": (-.5, 1.5), "response": (-.5, 1.5),
                                              "feedback": (-.5, 1.5), "delay": (-.5, 3.5)})
    baseline: dict = field(default_factory=lambda:{"stimulus": (-.2, 0), "response": (-.2, 0), "feedback": (-.2, 0),"delay": (-.2,0)})
    freqs: List[float] = field(default_factory=lambda:[[2,4],[4,8],[8,13],[13,30],[30,60],[60,100]])  # empty list = canonical frequency bands
    scale: str = "canonical"  # canonical, linear, log


@dataclass
class CoherenceCfg:
    methods: List[str] = field(default_factory=lambda:['coh','cohy','imcoh','plv','ciplv','ppc','pli','pli2_unbiased','wpli','wpli2_debiased'])
    modes: List[str] = field(default_factory=lambda: ['multitaper','cwt_morlet'])
    toi: dict = field(default_factory=lambda:{"stimulus": (0, 1), "response": (0, 1),
                                              "feedback": (0, 1), "delay": (-.5, 3.5)})
    conditions: dict = field(default_factory=lambda: {'correct': 'FeedbackType=="positive"',
                                                      'incorrect': 'FeedbackType=="negative"',
                                                      'visual': 'visual',
                                                      'auditive': 'auditive'})

@dataclass
class tPACCfg:
    toi: dict = field(default_factory=lambda:{"stimulus": (-.5, 1.5), "response": (-.5, 1.5),
                                              "feedback": (-.5, 1.5), "delay": (-.5, 3.5)})
    baseline: dict = field(default_factory=lambda:{"stimulus": (-.2, 0), "response": (-.2, 0), "feedback": (-.2, 0)})
    f_phase: dict = field(default_factory=lambda:{'Delta':[1,4],'Theta':[4,8],'Alpha':[8,13]})
    f_amplitude: dict = field(default_factory=lambda:{'Low Beta':[13,20],'High Beta':[20,30],
                                                      'Low Gamma':[30,45],'Mid Gamma':[45,60],
                                                      'High Gamma':[60,100]})
    method: str = field(default_factory=lambda:'gc') # gc | circular
    combinations: str = field(default_factory=lambda:'within') # within | across | list of channel pairs


@dataclass
class GLMCfg:
    formula: "EEG ~ C(Correctness)*BlockPercent"
    toi: dict = field(default_factory=lambda:{"stimulus": (-.5, 1.5), "response": (-.5, 1.5),
                                              "feedback": (-.5, 1.5), "delay": (-.5, 3.5)})
    baseline: dict = field(default_factory=lambda:{"stimulus": (-.2, 0), "response": (-.2, 0), "feedback": (-.2, 0)})
    freqs: List[List[float]] = field(default_factory=lambda:[[1,4],[4,8],[8,13],[13,20],[20,30],[30,50],[50,100]])  # empty list = canonical frequency bands
    scale: str = "canonical"  # canonical, linear, log
    decim: int = 10
    n_subj: int = None

@dataclass
class CondCFG:
    conditions: dict = field(default_factory=lambda:{
        'all': lambda x: x,
        'visual': lambda x: x['visual'],
        'auditive': lambda x: x['auditive'],
        'visual/left': lambda x: x['visual/left'],
        'visual/right': lambda x: x['visual/right'],
        'auditive/left': lambda x: x['auditive/left'],
        'auditive/right': lambda x: x['auditive/right'],

    })

###############################################################################
# These are all the relevant parameters for the analysis.

raw_cfg = RawCfg(ref_channels=['TP9','TP10'])
epo_cfg = EpoCfg(event_codes=codes.dmss(),toi={"stimulus": (-2.5, 7.), "delay": (-2.5, 5.)},locks=['stimulus','delay'])
morlet_cfg = MorletCfg(freqs=[2,3,4,5,7,9,11,13,15],n_cycles=[3,3,3,3,5,5,5,5,7],toi={"stimulus": (-.5, 5.), "delay": (-.5, 3.)})
firwin_cfg = FirwinCfg(freqs=[[a,b] for a,b in zip(range(4,57,4),range(8,61,4))],toi={"stimulus": (-.5, 5.), "delay": (-.5, 3.)},scale='linear')
coh_cfg = CoherenceCfg(methods=['coh'],modes=['multitaper'])
glm_cfg = GLMCfg(formula="EEG ~ C(Modality)*Correctness*ResponseTimes + C(Modality)*Correctness*BlockPercent + C(Modality)*Correctness*Delay + C(Modality)*Correctness*C(parameters)*C(model_family)") # + C(Modality)*BlockPercent + C(Correctness)*ResponseTimes
cond_cfg = ""
tpac_cfg = tPACCfg()
# All subjects

subj_prefix = "multimodal"
locks = epo_cfg.locks
subjects = [sbj[len(bv_data_dir)+1:-1] for sbj in sorted(glob(f"{bv_data_dir}/{subj_prefix}[0-9][0-9][0-9]/"))]

brainvision_subjects = group_subjects([f.split("/")[-1][:-5] for f in sorted(glob(f"{bv_data_dir}/*vhdr"))])
brainvision_subjects = [(f"{subj_prefix}{1+i+len(subjects):03}",bvf[0]) for i,bvf in enumerate(brainvision_subjects)]

###############################################################################
# Templates for filenames
#
# This part of the config file uses the FileNames class. It provides a small
# wrapper around string.format() to keep track of a list of filenames.
# See fnames.py for details on how this class works.
fname = FileNames()

# Some directories
fname.add('base_dir', bv_data_dir)
fname.add('subject_dir','{base_dir}/{subject}')
fname.add('subject_file','{subject_dir}/{file}')

fname.add('subject_raw','{subject_dir}/{subject}.raw.fif.gz')
fname.add('subject_ica','{subject_dir}/{subject}-ica.fif.gz')

fname.add('subject_csv','{subject_dir}/{subject}.md.csv.gz')
fname.add('subject_xlsx','{subject_dir}/{subject}.xlsx')

fname.add('subject_epo','{subject_dir}/{subject}.{lock}-epo.fif.gz')

fname.add('subject_firwin','{subject_dir}/{subject}.{fmin}-{fmax}.{nsteps}-{scale}.{lock}.firwin-tfr.h5')
fname.add('subject_morlet','{subject_dir}/{subject}.{fmin}-{fmax}.{nsteps}-{scale}.{lock}.morlet-tfr.h5')

fname.add('subject_regression','{subject_dir}/{subject}.{fmin}-{fmax}.{nsteps}-{scale}.{lock}.epo.fif.gz')

fname.add('subject_connectivity','{subject_dir}/{subject}.{lock}.{condition}.{fmin}-{fmax}.{mode}.{method}-tfr.h5')
fname.add('subject_cfc','{subject_dir}/{subject}.{lock}.{lmin}-{lmax}.{hmin}-{hmax}.{method}.connectivity-tfr.h5')

fname.add('regression','{base_dir}/{subj_prefix}.{lock}.{fmin}-{fmax}.{model_id}-epo.fif.gz')

# File produced by check_system.py
fname.add('system_check', './system_check.txt')
