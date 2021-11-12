import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

"""
Find Brainvision files, assign subject identifier and sort in project directory.
"""
import argparse
from os import makedirs, rename
from glob import glob
from config import fname

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('brainvision',
                    help='The BrainVision dataset to import')
parser.add_argument('subject',
                    help='The subject to create')
args = parser.parse_args()
brainvision = args.brainvision
subject = args.subject
print(f'Importing data for {brainvision} into {subject}')

subject_dir = fname.subject_dir(subject=subject)
files = [f[len(fname.base_dir)+1:] for f in glob(f"{fname.base_dir}/{brainvision}*") if f[-4:] in [".eeg","vhdr","vmrk"]]

if len(files):
    makedirs(subject_dir)
    for f in files:
        rename(fname.base_dir+"/"+f,fname.subject_file(subject=subject,file=f))

    f = open(fname.subject_file(subject=subject,file="brainvision.csv"),"w")
    f.writelines(sorted(files))
    f.close()

# make output?