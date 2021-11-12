"""
Do-it script to execute the entire pipeline using the doit tool:
http://pydoit.org

All the filenames are defined in config.py

Thanks to Marijn van Vliet @wmvanvliet, who created and shared the original scripts
"""

# Configuration for the "doit" tool.
DOIT_CONFIG = dict(
    # While running scripts, output everything the script is printing to the
    # screen.
    verbosity=2,

    # When the user executes "doit list", list the tasks in the order they are
    # defined in this file, instead of alphabetically.
    sort='definition',
)

import sys; sys.path.append("./")

from config import fname, subjects, brainvision_subjects, epo_cfg, morlet_cfg, firwin_cfg, coh_cfg, glm_cfg, tpac_cfg, subj_prefix
import numpy as np, hashlib as hl

def task_check():
    """Check the system dependencies."""
    return dict(
        file_dep=['check_system.py'], # input file(s)
        targets=[fname.system_check], # output file(s)
        actions=['python check_system.py'] # script(s)
    )

def task_initialize_dataset():
    for subject,brainvision in brainvision_subjects:
        subject_dir = fname.subject_dir(subject=subject)
        subject_file = fname.subject_file(subject=subject,file="brainvision.csv")
        yield dict(
            name=subject,
            file_dep=['scripts/00_initialize_dataset.py'],
            targets=[subject_dir,subject_file],
            actions=[f'python scripts/00_initialize_dataset.py {brainvision} {subject}']
        )

def task_preprocess_raw():
    for subject in subjects:
        subject_file = fname.subject_file(subject=subject,file="brainvision.csv")
        subject_raw = fname.subject_raw(subject=subject)
        yield dict(
            name=subject,
            file_dep=['scripts/01_preprocess_raw.py',subject_file],
            targets=[subject_raw],
            actions=[f'python scripts/01_preprocess_raw.py {subject}']
        )

def task_epoch_raw():
    for subject in subjects:
        for lock in epo_cfg.locks:
            subject_raw = fname.subject_raw(subject=subject)
            subject_epo = fname.subject_epo(subject=subject,lock=lock)
            yield dict(
                name=f'{subject}-{lock}',
                file_dep=['scripts/02_epoch_raw.py',subject_raw],
                targets=[subject_epo],
                actions=[f'python scripts/02_epoch_raw.py {subject} {lock}']
            )

def task_morlet():
    scale = morlet_cfg.scale
    freqs = morlet_cfg.freqs
    csd = ".csd" if morlet_cfg.csd else ""
    for subject in subjects:
        for lock in epo_cfg.locks:
            subject_epo = fname.subject_epo(subject=subject,lock=lock)
            subject_morlet = fname.subject_morlet(subject=subject,csd=csd,lock=lock,fmin=freqs[0],fmax=freqs[-1],nsteps=len(freqs),scale=scale)
            yield dict(
                name=f'{subject}-{lock}',
                file_dep=['scripts/03_morlet.py',subject_epo],
                targets=[subject_morlet],
                actions=[f'python scripts/03_morlet.py {subject} {lock}']
            )

def task_firwin():
    scale = firwin_cfg.scale
    freqs = firwin_cfg.freqs
    for subject in subjects:
        for lock in epo_cfg.locks:
            subject_epo = fname.subject_epo(subject=subject,lock=lock)
            subject_firwin = fname.subject_firwin(subject=subject,lock=lock,fmin=np.mean(freqs[0]),fmax=np.mean(freqs[-1]),nsteps=len(freqs),scale=scale)
            yield dict(
                name=f'{subject}-{lock}',
                file_dep=['scripts/04_firwin.py'],#,subject_epo],
                targets=[subject_firwin],
                actions=[f'python scripts/04_firwin.py {subject} {lock}']
            )

def task_firwin_power():
    scale = firwin_cfg.scale
    freqs = firwin_cfg.freqs
    for subject in subjects:
        for lock in epo_cfg.locks:
            subject_epo = fname.subject_epo(subject=subject,lock=lock)
            subject_firwin = fname.subject_firwin(subject=subject,lock=lock,fmin=np.mean(freqs[0]),fmax=np.mean(freqs[-1]),nsteps=len(freqs),scale="power")
            yield dict(
                name=f'{subject}-{lock}',
                file_dep=['scripts/12_power_from_firwin.py'],#,subject_epo],
                targets=[subject_firwin],
                actions=[f'python scripts/12_power_from_firwin.py {subject} {lock}']
            )

def task_firwin_variability():
    scale = firwin_cfg.scale
    freqs = firwin_cfg.freqs
    for subject in subjects:
        for lock in epo_cfg.locks:
            subject_epo = fname.subject_epo(subject=subject,lock=lock)
            subject_firwin = [fname.subject_firwin(subject=subject,lock=lock,fmin=np.mean(freqs[0]),fmax=np.mean(freqs[-1]),nsteps=len(freqs),scale="var."+cond) for cond in ['positive.size1','positive.size2','positive.size4','negative.size4']]
            yield dict(
                name=f'{subject}-{lock}',
                file_dep=['scripts/13_variability_from_firwin.py'],#,subject_epo],
                targets=subject_firwin,
                actions=[f'python scripts/13_variability_from_firwin.py {subject} {lock}']
            )

def task_coherence():
    modes = coh_cfg.modes
    methods = coh_cfg.methods
    conditions = coh_cfg.conditions
    csd = coh_cfg.csd
    get_freqs = lambda n: (coh_cfg.freqs[0],coh_cfg.freqs[-1]) if n=="cwt_morlet" else (coh_cfg.freqs[0][0],coh_cfg.freqs[-1][-1])
    for subject in subjects:
        for lock in epo_cfg.locks:
            subject_epo = fname.subject_epo(subject=subject,lock=lock)
            subjects_connectivity = [fname.subject_connectivity(subject=subject,csd=csd,lock=lock,fmin=get_freqs(n)[0],
                                             fmax=get_freqs(n)[1],method=m,mode=n,condition=cond)
                                             for n in modes for m in methods for cond in conditions]
            yield dict(
                name=f'{subject}-{lock}',
                file_dep=['scripts/07_coherence.py',subject_epo],
                targets=subjects_connectivity,
                actions=[f'python scripts/07_coherence.py {subject} {lock}']
            )

def task_tpac():
    fpha = tpac_cfg.f_phase
    famp = tpac_cfg.f_amplitude
    method = tpac_cfg.method
    combinations = tpac_cfg.combinations
    conditions = tpac_cfg.conditions
    for subject in subjects:
        for lock in epo_cfg.locks:
            subject_epo = fname.subject_epo(subject=subject,lock=lock)
            subjects_connectivity = [fname.subject_tpac(subject=subject,lock=lock,lmin=fpha[0][0],
                                             lmax=fpha[-1][1],hmin=famp[0][0],
                                             hmax=famp[-1][1],method=method,combinations=combinations,condition=cond)
                                             for cond in conditions.keys()]
            yield dict(
                name=f'{subject}-{lock}',
                file_dep=['scripts/09_compute_tpac.py'],#,subject_epo],
                targets=subjects_connectivity,
                actions=[f'python scripts/09_compute_tpac.py {subject} {lock}']
            )

def task_single_trial_analysis():
    freqs = glm_cfg.freqs
    model_id = hl.md5(glm_cfg.formula.encode('UTF-8')).hexdigest()[:6]
    for lock in epo_cfg.locks:
        subjects_epo = [fname.subject_epo(subject=subject,lock=lock) for subject in subjects]
        subjects_regression = [fname.regression(subj_prefix=subj_prefix,lock=lock,fmin=fmin,fmax=fmax,model_id=model_id) for fmin, fmax in freqs]
        yield dict(
            name='{}.{}.{}-{}.{}'.format(subj_prefix,lock,freqs[0][0],freqs[-1][-1],model_id),
            file_dep=['scripts/10_single_trial_analysis.py'],#+subjects_epo,
            targets=subjects_regression,
            actions=[f'python scripts/10_single_trial_analysis.py {lock}']
        )