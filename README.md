# CellPyAbility

The objective of CellPyAbility is to offer an open-access cell viability analysis tool that seamlessly integrates with our provided [protocols](path/to/protocol).

## Prerequisites

While we try to make CellPyAbility widely applicable, there are several technical limitations. These limitations are covered in detail within the written protocol, but below are some requirements in brief:

- The user must have a functional Python 3 environment to run the scripts.
- The user must have the necessary [Python dependencies](requirements.txt).
- Cells must be adherent or able to adhere to a 96-well plate prior to imaging.
- Only the inner 60 wells (B2-G11) of the 96-well plate should contain cells. The outer wells can be filled with PBS or another solution to help buffer evaporation.
- [CellProfiler](https://github.com/CellProfiler/CellProfiler) must be installed and functional. The license is included [here](CellProfilerLicense.txt).
- We use a fluorescence imager with excitation at 362 nm (Hoechst) and twelve stitched images of 20x magnification. 
  - CellPyAbility can be modified to work with other imaging protocols by editing the [CellProfiler pipeline](CellPyAbility/CellPyAbility.cppipe) (see [Modifying the CellProfiler Pipeline](##Modifying-the-CellProfiler-Pipeline)).
- Image file names must contain their corresponding well.
  - e.g. B2, ImageB2, DAPI-B2-(362), etc. for the image file of the B2 well in the 96-well plate.

## Quick Start
Download the [CellPyAbility directory](CellPyAbility). This is the working directory for our program and contains three Python scripts with unique functions:
- [CellPyAbility_GDA](CellPyAbility/CellPyAbility_GDA.py): dose-response analysis of two cell lines/cell conditions with a drug gradient.
- [CellPyAbility_synergy](CellPyAbility/CellPyAbility_synergy.py): dose-response and synergy (Bliss) analysis of one cell line/cell condition with simultaneous horizontal and vertical drug gradients.
- [CellPyAbility_simple](CellPyAbility/CellPyAbility_simple.py): raw nuclei count matrix recapitulating the 96-well format.

Note that the scripts reference items in the directory, so the [CellPyAbility directory](CellPyAbility) must be downloaded and **should not be altered** without foresight.

The first time the user runs any of the scripts, a console input will be required for the path to the CellProfiler file:
- For Windows, this is the CellProfiler.exe file. 
- For MacOS, this is the path/to/CellProfiler.app/Contents/MacOS/CellProfiler file 
  - CellProfiler.app is a directory and will cause 'PermissionError: [Errno 13]' if used as the file path. 
- The inputted path will then be saved as CellPyAbility/cellprofiler_path.txt, which is automatically retrieved for all future runs.

Next, a GUI will prompt the user for experimental details. I will use [CellPyAbility_GDA](CellPyAbility/CellPyAbility_GDA.py) as an example, but [CellPyAbility_synergy](CellPyAbility/CellPyAbility_synergy.py) and [CellPyAbility_simple](CellPyAbility/CellPyAbility_simple.py) follow the same workflow. The GDA GUI asks for the following: 
- title of the experiment (e.g. 20250101_CellLine_Drug)
- name of the cell condition in rows B-D (e.g. Cell Line Wildtype)
- name of the cell condition in rows E-G (e.g. Cell Line Gene A KO)
- concentration gradient in molar units, excluding 0 and tab-separated
- a file browser to select the directory containing the 60 images

We provide example image sets in the [test directory](test) with the expected outputs, along with a [drug concentration gradient template](test/drug_concentrations.csv). We recommend running these test sets to ensure the scripts are working properly prior to running one's own data. 

Please note that the test directory includes 240 images of 2.8 MB each; therefore, downloading it will decrease your available storage for cat videos and increase your carbon footprint.

## Modifying the CellProfiler Pipeline

Across multiple cell lines and densities, our provided [CellProfiler Pipeline](CellPyAbility/CellPyAbility.cppipe) appears robust and precise. However, if the user wishes to make any changes, a few guidelines must be followed to maintain compatibility with the scripts as written:
- The CSV headers/module output names must remain as:
  - Count_nuclei
  - FileName_images
- The CellProfiler output CSV file name must remain as:
  - path/to/CellPyAbility/cp_output/CellPyAbilityImage.csv

Please note that we have not tested the analysis scripts on other protocols. For best results, please follow the provided [protocol](path/to/protocol).

## Comments or Concerns?
Please contact me at james.elia@yale.edu