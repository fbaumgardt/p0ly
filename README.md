* Introduction

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
