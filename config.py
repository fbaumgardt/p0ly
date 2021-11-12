"""
===========
Config file
===========
Configuration parameters for the study.
"""

subj_prefix = "dmss"

import os, getpass, json as js, numpy as np
from socket import getfqdn
from fnames import FileNames
from glob import glob
import event_codes as codes
from configs.default import *
if subj_prefix=="dmss":
    from configs.dmss import config as cfg
else:
    from configs.multimodal import config as cfg

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
dir = cfg.base_dir
# You want to add your machine to this list
if host == 'Device.local':
    # My laptop
    bv_data_dir = f'.{dir}'
    n_jobs = 2  # My laptop has 2 cores
elif host == 'titan.amherst':
    # My workstation
    bv_data_dir = dir
    n_jobs = 64  # My workstation has 128 cores
elif user == 'fbaumgardt':
    # Personal defaults
    bv_data_dir = f'.{dir}'
    n_jobs = 1
else:
    # Defaults
    bv_data_dir = f'.{dir}'
    n_jobs = 1

# For BLAS to use the right amount of cores
os.environ['OMP_NUM_THREADS'] = str(n_jobs)


###############################################################################
# These are all the relevant parameters for the analysis.

raw_cfg = RawCfg(**cfg.raw)
epo_cfg = EpoCfg(**cfg.epo)
morlet_cfg = MorletCfg(**cfg.morlet)
firwin_cfg = FirwinCfg(**cfg.firwin)
coh_cfg = CoherenceCfg(**cfg.coherence)
glm_cfg = GLMCfg(**cfg.linear_model)
tpac_cfg = tPACCfg(**cfg.tpac)


###############################################################################
# All subjects

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
fname.add('subject_morlet','{subject_dir}/{subject}{csd}.{fmin}-{fmax}.{nsteps}-{scale}.{lock}.morlet-tfr.h5')

fname.add('subject_regression','{subject_dir}/{subject}.{fmin}-{fmax}.{nsteps}-{scale}.{lock}.epo.fif.gz')

fname.add('subject_connectivity','{subject_dir}/{subject}{csd}.{lock}.{condition}.{fmin}-{fmax}.{mode}.{method}-tfr.h5')
fname.add('subject_cfc','{subject_dir}/{subject}.{lock}.{lmin}-{lmax}.{hmin}-{hmax}.{method}.connectivity-tfr.h5')
fname.add('subject_tpac','{subject_dir}/{subject}.{lock}.{lmin}-{lmax}.{hmin}-{hmax}.{method}.{combinations}.{condition}.tpac-epo.fif.gz')

fname.add('regression','{base_dir}/{subj_prefix}.{lock}.{fmin}-{fmax}.{model_id}-epo.fif.gz')

# File produced by check_system.py
fname.add('system_check', './system_check.txt')
