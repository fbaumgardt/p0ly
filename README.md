### Introduction

p0lyis a computational pipeline for EEG data preprocessing and analysis. Its goal is to provide automated and repeatable data clean up and computation of a wide range of analyses. It is written primarily in Python and built atop the MNE M/EEG data processing library and the PyDOIT workflow management system.

The pipeline consists of a set of processing tasks (/scripts), a central configuration file (config.py) and a set of instructions for parsing/computing condition-relevant metadata (event_codes.py). Once the configuration is set up, tasks can be run on datasets with a single command line instruction - without further interaction and with automated execution of all necessary preprocessing steps. After a task completed, a range of Jupyter notebooks can be used to visualize and further investigate the analysis results.

Currently available analyses are Event Related and Global Field Potentials, Time Frequency Analysis (Power and ITPC), Connectivity Analysis (within-frequency and cross-frequency, time-resolved and -averaged), Waveform Geometry Analysis (by-cycle), Parametric and Non-parametric Statistics, Network Analysis, and Single-trial Analysis (Linear Mixed Models).

* Getting started
 * Requirements
 * Installation
  * Remote setup w/ PyCharm
 * Project setup
  * Data folder
  * Config file
  * Event codes
  * Metadata parsing

### Pipeline stages

####00 - Initialize dataset

This stage scans folder for Brainvision files and assigns subject ids to them, then it create folders for each subject and moves the original files into them.
**Input:** folder with *BrainVision files*
**Output:** files get uniform *subject IDs*, moved to *subfolders*

####01 - Preprocess raw

This stage rereferences the EEG, then detects and interpolates bad channels. After the first round of channel correction, blink and saccade artifacts are removed by subtracting EOG-correlated ICA components. Then a second round of channel correction is applied. Finally, z-score based artifact detection and annotation is performed. The full recording is saved to MNE raw format. In addition, the ICA matrix is saved.
**Input:** *BrainVision files* and subject ID
**Output:** cleaned and annotated *raw files*, *ICA matrix*

####02 - Epoch raw

In this step, the recording is segmented according to the (possibly multiple) lock markers and time intervals defined in the configuration file. If methods for metadata computation are provided they're applied and metadata is attached to the ```.metadata``` property. Trials containing segments that have been annotated (as containing artifacts) in the previous step are dropped. The epoched data is saved to MNE epoch format.
**Input:** cleaned and annotated *raw files*, configuration with *time-locks* that are defined by *event codes* and *time intervals*
**Output:** *trial-segmented data* with trial metadata attached and bad trials removed

#### 03 - Morlet wavelet filtering

This step applies Morlet wavelet convolution to the epoched data and saves the (unaveraged) complex format result in MNE TFR format. The frequencies and width of the wavelets are specified in the `freqs` and `n_cycles` variables. `csd` determines if a spatial filter is applied before the analysis. `toi` and `decim` specify the crop and resampling to be applied *after* wavelet convolution.
**Input:** *trial-segmented data*, configuration with *frequencies* and *toi*
**Output:** *time-frequency data*, cropped and resampled

#### 04 - FIRWIN filtering

Analogous to step 3, this step applies windowed FIR bandpass filtering to the epoched data and saves the (unaveraged) complex format result in MNE TFR format. The frequency bands and bandwidths are specified in the `freqs` and `bandwidth` variables. `toi` specifies the crop to be applied *after* FIRWIN filtering.
**Input:** *trial-segmented data*, configuration with *frequency bands* and *toi*
**Output:** *time-frequency data*, cropped and resampled

####10 - Single-trial Analysis

