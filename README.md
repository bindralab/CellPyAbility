# CellPyAbility

CellPyAbility is an open-source cell viability and dose-response analysis tool that seamlessly integrates with our provided [protocols](protocol.pdf). Please review our [license](LICENSE.txt) prior to use. The software can be run as a [Windows application](#windows-application) or in [Python](#running-in-python). 

CellPyAbility is still in development; if you encounter any bugs, please contact me at james.elia@yale.edu. Thank you for your patience :)

## Table of Contents
- [Quick Start](#quick-start): ignore my hard work on the documentation and run CellPyAbility ASAP

- [Abstract](#abstract): overview of the method and software

- [Requirements](#requirements): necessary steps before running the software

  - [Data Requirements](#data-requirements): applies to all uses
  - [Application Requirements](#application-requirements): applies to Windows application
  - [Python Script Requirements](#python-script-requirements): applies to stand-alone scripts

- [Windows Application](#windows-application): code-free executable for Windows OS

- [Python Scripts](#python-scripts): stand-alone Python scripts for each module

- [Example Outputs](#example-outputs): examples of figures and tables for each module
  - [GDA Module](#gda-module): two cell lines, one drug gradient
  - [Synergy Module](#synergy-module): one cell line, two drug gradients
  - [Simple Module](#simple-module): nuclei count matrix
  - [Testing](#testing): test data for validating software setup

- [Contributions](#contributions): who did what

## Quick Start

### Windows Application
- Download the [Windows executable](CellPyAbility_exe/CellPyAbility.exe)
  - We recommend moving CellPyAbility.exe into an empty directory (running it will create files)
- Download the [GDA test data](test/test_GDA)
- Run CellPyAbility.exe and select the GDA module from the menu
- Run the test data and compare the results to the [expected output](test/test_expected_outputs)

### Python
```bash
# make a copy of the repo in the root directory and navigate to it
git clone https://github.com/CellPyAbility
cd CellPyAbility

# if using conda, create and use a stable CellPyAbility environment
conda env create -f CellPyAbility_py/environment.yml
conda activate CellPyAbility

# OR if using pip, install the requirements to create a stable environment
python -m pip install -r CellPyAbility_py/requirements.txt

# download the test data locally via Git Large File Storage
git lfs pull

# run the GDA script on the test data provided in this repo
python CellPyAbility_py/CellPyAbility_GDA.py
```
Compare the GDA results to the [expected outputs](test/test_expected_outputs).

## Abstract

The purpose of this repository is to offer open-access software for the automated analysis of dose-response experiments (growth delay assays, or GDAs) via nuclei counting.

Nuclei counting provides several advantages over other common methods of measuring cell viability. Compared to the commonly used methylthiazol tetrazolium (MTT; reduction-based) or CellTiter-Glo (ATP-based) assays, GDAs: 
- provide single-cell resolution of survival 

- are insensitive to metabolic variability within a cell or between cell lines 

- are compatible with redox-altering chemicals 

- require simpler methodology and cheaper reagents

- can be used on live cells using non-toxic nuclear dyes like Hoechst. 

A disadvantage of the GDA is the computational and temporal cost of the required image analysis. CellPyAbility rapidly calculates dose-response metrics and publication-ready graphics from a folder of unedited, whole-well GDA images in approximately one minute on commodity hardware.

CellPyAbility includes the synergy module which analyzes 59 unique drug concentration combinations, returning dose-response metrics and Bliss independence scores, a measure of synergy in cellular systems.

Finally, the simple module returns a matrix of nuclei counts in a 96-well format without further analysis, allowing maximum flexibility.

CellPyAbility uses [CellProfiler](https://cellprofiler.org/) to quantify nuclei, which maximizes modularity for the user. Please see the [CellProfiler license](CellProfilerLicense.txt).

## Requirements

### Data Requirements

Reading the [protocols](protocol.pdf) first may aid in understanding the data requirements.

- Only the inner 60 wells of a 96-well plate (B-G, 2-11) should be used

- Image file names must contain their corresponding well
  - B2, ImageB2, DAPI-B2-(362), etc. for the image file of the B2 well in the 96-well plate

- The GDA module requires a directory of 60 images 
  - B-D: Cell Line A in triplicate | E-G: Cell Line B in triplicate

- The synergy module requires a directory of 180 images
  - Wells of the same name (B2, ...) across three plates are triplicates

### Application Requirements

- The user must have CellProfiler (tested on version 4.2.5, though others may work)
  - [Windows 64-bit Version 4.2.5](https://cellprofiler-releases.s3.amazonaws.com/CellProfiler-Windows-4.2.5.exe)

- The user must have Windows OS.

### Python Script Requirements

- The user must have CellProfiler (tested on version 4.2.5, though others may work)
  - [Windows 64-bit Version 4.2.5](https://cellprofiler-releases.s3.amazonaws.com/CellProfiler-Windows-4.2.5.exe) | [MacOS Version 4.2.5](https://cellprofiler-releases.s3.amazonaws.com/CellProfiler-macOS-4.2.5.zip)

- The user must have a functional Python 3 environment to run the scripts.

- The user should use the [Python dependencies](CellPyAbility_py/requirements.txt). Other package versions have not yet been tested but may work.

## Windows Application
Running the Windows application requires no programming experience, Python environment, or dependencies. It is a single file containing all three modules with graphical user interfaces (GUIs) for user inputs.

Download the [CellPyAbility application](CellPyAbility_exe/CellPyAbility.exe). I recommend saving it to an empty directory dedicated to CellPyAbility because running the application will generate several files in its directory.

Upon the first run, CellPyAbility may take some time (<1 min) to load. Once running, a GUI prompts the user to choose from three modules. Hovering over each module will give a description of its uses:

- **GDA**: dose-response analysis of two cell lines in response to one treatment

- **synergy**: dose-response analysis of one cell line in response to two treatments in combination

- **simple**: nuclei count matrix in a 96-well format

After selecting a module, the application will look for the CellProfiler.exe in the default save locations:
- "C:\Program Files\CellProfiler\CellProfiler.exe"

- "C:\Program Files (x86)\CellProfiler\CellProfiler.exe"

If CellProfiler.exe cannot be found, the user will be prompted to input the path to the CellProfiler.exe file. The path is saved to a .txt file within the directory for future reference, so subsequent runs will proceed directly to the next step.

A GUI specific to each module will prompt the user for experimental details. Using the GDA module as an example:
- title of the experiment (e.g. 20250101_CellLine_Drug)

- name of the cell condition in rows B-D (e.g. Cell Line Wildtype)

- name of the cell condition in rows E-G (e.g. Cell Line Gene A KO)

- top on-cell concentration in molar (if cells in column 11 are in 1 uM of drug: 0.000001)

- the dilution factor between columns (if 3-fold dilutions between each column: 3)

- a file browser to select the directory containing the 60 images

After submitting the GUI, a terminal window will open to track CellProfiler's image analysis progress. Once all images are counted, subsequent analysis is almost instant. All figures and tabular results will be in a subdirectory named after the module (e.g. GDA_output). See [Example Outputs](#example-outputs).

A small GUI window will then prompt the user if they would like to run another experiment. If "yes", the initial module selection GUI will prompt the user again. If "no", the application will close.

A log file with detailed logging is written to the directory. If the application fails at any point, it may be useful to consult the log for critical messages or to identify the last step to succeed.

## Python Scripts
For those who resist the corporate yoke of Microsoft, or for users looking for more control over the software, CellPyAbility can be run directly in Python with out-of-the-box scripts.

Download the [CellPyAbility_py directory](CellPyAbility_py). This is the working directory for our program and contains three modules:
- [CellPyAbility_GDA](CellPyAbility_py/CellPyAbility_GDA.py): dose-response analysis of two cell lines/cell conditions with a drug gradient.

- [CellPyAbility_synergy](CellPyAbility_py/CellPyAbility_synergy.py): dose-response and synergy (Bliss) analysis of one cell line/cell condition with simultaneous horizontal and vertical drug gradients.

- [CellPyAbility_simple](CellPyAbility_py/CellPyAbility_simple.py): raw nuclei count matrix recapitulating the 96-well format.

[CellPyAbility_toolbox](CellPyAbility_py/CellPyAbility_toolbox.py) is a script containing functions, variables, and imports used across the modules, like logging and handling relative paths.

Note that the scripts reference items in the directory, so the [CellPyAbility_py directory](CellPyAbility_py) must be downloaded and **should not be altered** without foresight.

Upon running a module, the script will look for the CellProfiler application in the default save locations:
- **Windows 64-bit**: "C:\Program Files\CellProfiler\CellProfiler.exe"

- **Windows 32-bit**: "C:\Program Files (x86)\CellProfiler\CellProfiler.exe"

- **Mac OS**: "/Applications/CellProfiler.app/Contents/MacOS/cp"

If CellProfiler cannot be found, the user will be prompted to input the path to the CellProfiler file:
- For Windows, this is the 'CellProfiler\CellProfiler.exe' file

- For MacOS, this is the 'CellProfiler.app/Contents/MacOS/cp' file 
  - CellProfiler.app is a directory and will cause 'PermissionError: [Errno 13]' if used as the file path

The path is saved to a .txt file within the directory for future reference, so subsequent runs will proceed directly to the next step.

A GUI will prompt the user for experimental details. I will use [CellPyAbility_GDA](CellPyAbility_py/CellPyAbility_GDA.py) as an example, but [CellPyAbility_synergy](CellPyAbility_py/CellPyAbility_synergy.py) and [CellPyAbility_simple](CellPyAbility_py/CellPyAbility_simple.py) follow the same workflow. The GDA GUI asks for the following: 
- title of the experiment (e.g. 20250101_CellLine_Drug)

- name of the cell condition in rows B-D (e.g. Cell Line Wildtype)

- name of the cell condition in rows E-G (e.g. Cell Line Gene A KO)

- concentration gradient in molar units, excluding 0 and tab-separated

- a file browser to select the directory containing the 60 images

After submitting the GUI, a terminal window will open to track CellProfiler's image analysis progress. Once all images are counted, subsequent analysis is almost instant. All figures and tabular results will be in a subdirectory named after the module (e.g. GDA_output). See [Example Outputs](#example-outputs).

A log file with detailed logging is written to the directory. Additionally messages with results and output file locations (INFO), warnings (WARNING), errors (ERROR), or critical failure (CRITICAL) messages will be written directly to the terminal.

### Modifying the CellProfiler Pipeline

Across multiple cell lines and densities, our provided [CellProfiler Pipeline](CellPyAbility_py/CellPyAbility.cppipe) appears robust. However, if the user wishes to make any changes, a few guidelines must be followed to maintain compatibility with the scripts as written:
- The module output names must remain as:
  - Count_nuclei
  - FileName_images

- The CellProfiler output CSV file name must remain as:
  - path/to/CellPyAbility_py/cp_output/CellPyAbilityImage.csv

The modularity of the Python scripts and CellProfiler pipeline may prove useful. For example, if the user wishes to use all 96 wells instead of 60, minor Python knowledge and effort would be needed to enact this change. As another example, the user could analyze microscope images of 10x magnification instead of 4x magnification by increasing the expected pixel ranges for nuclei in the [CellProfiler pipeline](CellPyAbility_py/CellPyAbility.cppipe).

## Example Outputs
### GDA Module
The GDA module outputs three tabular files with increasing degrees of analysis:
- [raw nuclei counts](test/test_expected_outputs/test_GDA_counts.csv)

- [normalized cell viability matrix](test/test_expected_outputs/test_GDA_ViabilityMatrix.csv)

- [cell viability statistics](test/test_expected_outputs/test_GDA_Stats.csv)

Additionally, the script generates a plot with 5-parameter logistic curves:

![GDA plot](test/test_expected_outputs/test_GDA_plot.png)

### Synergy Module
The synergy module outputs four tabular files:
- [raw nuclei counts](test/test_expected_outputs/test_synergy_counts.csv)

- [normalized cell viability matrix](test/test_expected_outputs/test_synergy_ViabilityMatrix.csv)

- [cell viability statistics](test/test_expected_outputs/test_synergy_stats.csv)

- [Bliss synergy matrix](test/test_expected_outputs/test_synergy_BlissMatrix.csv)

Additionally, the script generates an interactive [3D surface map](test/test_expected_outputs/test_synergy_plot.html) in HTML with synergy as heat:

![synergy plot](test/test_expected_outputs/test_synergy_plot_screenshot.png)

### Simple Module
Finally, the simple module outputs nuclei counts in a 96-well matrix format. This offers maximum flexibility but does not provide any analysis.
- [count matrix](test/test_expected_outputs/test_simple_CountMatrix.csv)

### Testing

The example outputs above are the results from running the [GDA test data](test/test_GDA/) and the [synergy test data](test/test_synergy/). I recommend running these test sets to ensure the scripts are working properly prior to running one's own data. The [test parameters](test/test_params.txt) text file contains the exact experimental info used to generate the example outputs. 

Due to the size of the files in the test directory, it is saved to [Git LFS](https://git-lfs.com/). If the user has Git LFS installed, the test directory can be downloaded by entering '**git lfs pull**' in the directory's terminal after cloning the repo.

Please note that we have not tested the analysis scripts on other protocols. For best results, please follow the provided [protocol](protocol.pdf).

## Contributions
Summary information regarding the authors as of 2025:
- My name is James Elia, and I am a PhD candidate in Yale's Pathology and Molecular Medicine program. I am the author of the repository and the code herein.

- Sam Friedman, MS is a Computational Research Support Analyst at Yale Center for Research Computing. He provided programming mentorship and development support for the repository.

- Ranjit Bindra, MD, PhD is the Harvey and Kate Cushing Professor of Therapeutic Radiology and Professor of Pathology at Yale School of Medicine. He provided scientific mentorship and publishing support for the repository.

## Comments or Questions?
Please contact me at james.elia@yale.edu
