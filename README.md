# CellPyAbility [![Tests](https://github.com/bindralab/CellPyAbility/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/bindralab/CellPyAbility/actions/workflows/tests.yml)

CellPyAbility is an open-source cell viability and dose-response analysis tool that seamlessly integrates with our provided [protocols](protocol.pdf). Please review our [license](LICENSE.txt) prior to use. The software can be run from the command line as a [Python package](#command-line-interface-cli) or with a code-free [Windows application](#windows-application). 

## Table of Contents
- [Quick Start](#quick-start): minimal step-by-step guide for running CellPyAbility
  - [PyPI Installation](#pypi-installation): install CellPyAbility with pip and run it with the command line (Python users)
  - [Development Installation](#development-installation-for-contributors): clone the CellPyAbility repo and edit it (Python devs)
  - [Windows Application](#windows-application): install CellPyAbility as a code-free GUI Windows executable

- [Abstract](#abstract): overview of the method and software

- [Requirements](#requirements): necessary steps before running the software

  - [Data Requirements](#data-requirements): applies to all uses
  - [Application Requirements](#application-requirements): applies to Windows application

- [Command Line Interface](#command-line-interface-cli): modern CLI for automated workflows and testing

- [Windows Application](#running-the-windows-application): code-free executable for Windows OS

- [Example Outputs](#example-outputs): examples of figures and tables for each module
  - [GDA Module](#gda-module): two cell lines, one drug gradient
  - [Synergy Module](#synergy-module): one cell line, two drug gradients
  - [Simple Module](#simple-module): nuclei count matrix

- [Testing](#testing): automated tests and example data for validation

- [Contributions](#contributions): who did what

## Quick Start
CellProfiler must be installed because CellPyAbility uses it as a subprocess. See [Requirements](#requirements) for more information.

### PyPI Installation
Install CellPyAbility from PyPI to use it as a command-line tool:

```bash
# Install from PyPI
pip install cellpyability

# Run analysis on your images
# Outputs are saved to ./cellpyability_output/ by default
cellpyability gda \
  --title "MyExperiment" \
  --upper-name "Cell Line A" \
  --lower-name "Cell Line B" \
  --top-conc 0.000001 \
  --dilution 3 \
  --image-dir /path/to/your/images

# Specify custom output location
cellpyability gda \
  --title "MyExperiment" \
  --upper-name "Cell Line A" \
  --lower-name "Cell Line B" \
  --top-conc 0.000001 \
  --dilution 3 \
  --image-dir /path/to/your/images \
  --output-dir /path/to/results
```

**To download example data for testing:**
- Download the [example GDA images](https://github.com/bindralab/CellPyAbility/tree/main/example/example_gda)
- Run: `cellpyability gda --image-dir /path/to/example/example_gda ...`
- Compare to [expected outputs](https://github.com/bindralab/CellPyAbility/tree/main/example/example_expected_outputs)

### Development Installation (For Contributors)
Clone the repository for development and access to example data:

```bash
# Clone the repository
git clone https://github.com/bindralab/CellPyAbility
cd CellPyAbility

# Install in editable mode
pip install -e .

# Download example data (requires Git LFS)
git lfs pull

# Run GDA analysis with example data
cellpyability gda \
  --title "MyExperiment" \
  --upper-name "Cell Line A" \
  --lower-name "Cell Line B" \
  --top-conc 0.000001 \
  --dilution 3 \
  --image-dir example/example_gda

# Or test without CellProfiler using pre-counted data
cellpyability gda \
  --title test \
  --upper-name "Cell Line A" \
  --lower-name "Cell Line B" \
  --top-conc 0.000001 \
  --dilution 3 \
  --image-dir /tmp \
  --counts-file tests/data/test_gda_counts.csv \
  --no-plot
```

For more CLI options, run `cellpyability --help` or `cellpyability gda --help`.

### Windows Application
- Download the [Windows executable](windows_app/CellPyAbility.exe)
  - We recommend moving CellPyAbility.exe into an empty directory (running it will create files)
- Download the [GDA test data](https://github.com/bindralab/CellPyAbility/tree/main/example/example_gda) from the repository
- Run CellPyAbility.exe and select the GDA module from the menu
- Run the test data and compare the results to the [expected output](https://github.com/bindralab/CellPyAbility/tree/main/example/example_expected_outputs)

## Abstract

CellPyAbility is an open-access software for the automated analysis of dose-response experiments (growth delay assays, or GDAs) via nuclei counting.

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

## Command Line Interface (CLI)

The CellPyAbility CLI provides a modern, scriptable interface for automated workflows, batch processing, and continuous integration testing.

### Basic Usage

The CLI provides three subcommands corresponding to the three analysis modules:

```bash
cellpyability --help          # Show available modules
cellpyability gda --help      # Show GDA module options
cellpyability synergy --help  # Show synergy module options  
cellpyability simple --help   # Show simple module options
```

### GDA Module

Analyze dose-response experiments with two cell conditions and one drug gradient:

```bash
cellpyability gda \
  --title "20250101_Experiment" \
  --upper-name "HCT116_WT" \
  --lower-name "HCT116_KO" \
  --top-conc 0.000001 \
  --dilution 3 \
  --image-dir /path/to/images \
  --output-dir /path/to/results  # Optional: custom output location
```

**Parameters:**
- `--title`: Experiment title (used for output file names)
- `--upper-name`: Name for cell condition in rows B-D
- `--lower-name`: Name for cell condition in rows E-G
- `--top-conc`: Top drug concentration in molar (e.g., 0.000001 for 1 µM)
- `--dilution`: Dilution factor between columns (e.g., 3 for 3-fold dilution)
- `--image-dir`: Directory containing 60 well images
- `--no-plot`: (Optional) Skip displaying plot window
- `--counts-file`: (Optional) Use pre-existing counts CSV for testing
- `--output-dir`: (Optional) Custom output directory (default: `./cellpyability_output/`)

**Outputs** (saved to `./cellpyability_output/gda_output/` by default):
- `{title}_gda_Stats.csv`: Dose-response statistics
- `{title}_gda_ViabilityMatrix.csv`: Normalized viability matrix
- `{title}_gda_plot.png`: Publication-ready dose-response plot
- `{title}_gda_counts.csv`: Raw nuclei counts

### Synergy Module

Analyze drug combination experiments with two drug gradients:

```bash
cellpyability synergy \
  --title "20250101_Synergy" \
  --x-drug "Drug_A" \
  --x-top-conc 0.0004 \
  --x-dilution 4 \
  --y-drug "Drug_B" \
  --y-top-conc 0.0001 \
  --y-dilution 4 \
  --image-dir /path/to/images \
  --output-dir /path/to/results  # Optional: custom output location
```

**Parameters:**
- `--title`: Experiment title
- `--x-drug`: Name of horizontal gradient drug
- `--x-top-conc`: Horizontal top concentration in molar
- `--x-dilution`: Horizontal dilution factor
- `--y-drug`: Name of vertical gradient drug
- `--y-top-conc`: Vertical top concentration in molar
- `--y-dilution`: Vertical dilution factor
- `--image-dir`: Directory containing images
- `--no-plot`: (Optional) Skip displaying plot
- `--counts-file`: (Optional) Use pre-existing counts CSV
- `--output-dir`: (Optional) Custom output directory (default: `./cellpyability_output/`)

### Simple Module

Generate a nuclei count matrix without further analysis:

```bash
cellpyability simple \
  --title "20250101_Counts" \
  --image-dir /path/to/images \
  --output-dir /path/to/results  # Optional: custom output location
```

**Parameters:**
- `--title`: Experiment title
- `--image-dir`: Directory containing well images
- `--counts-file`: (Optional) Use pre-existing CellProfiler counts CSV
- `--output-dir`: (Optional) Custom output directory (default: `./cellpyability_output/`)

**Outputs** (saved to `./cellpyability_output/simple_output/` by default):
- `{title}_simple_CountMatrix.csv`: 96-well nuclei count matrix

### Batch Processing Examples

The CLI enables automated batch processing with shell scripts.

For GDA batch analysis:

```bash
#!/bin/bash
CONFIG_FILE=path/to/config.csv
# Process multiple experiments using a CSV config file
tail -n +2 "$CONFIG_FILE" | while IFS=, read -r dir title upper lower conc dil; do
    
    echo "Processing: $title in directory $dir..."

    if [ -d "$dir" ]; then
        cellpyability gda \
            --title "$title" \
            --upper-name "$upper" \
            --lower-name "$lower" \
            --top-conc "$conc" \
            --dilution "$dil" \
            --image-dir "$dir" \
            --no-plot
    else
        echo "Warning: Directory $dir not found. Skipping."
    fi

done
```

For synergy batch analysis:

```bash
#!/bin/bash
CONFIG_FILE=path/to/config.csv
# Process multiple experiments using a CSV config file
tail -n +2 "$CONFIG_FILE" | while IFS=, read -r dir title upper lower conc dil; do
    
    echo "Processing: $title in directory $dir..."

    if [ -d "$dir" ]; then
        cellpyability synergy \
            --title "$title" \
            --x-drug "$xdrug" \
            --x-top-conc "$xconc" \
            --x-dilution "$xdil" \
            --y-drug "$ydrug" \
            --y-top-conc "$yconc" \
            --y-dilution "$ydil" \
            --image-dir "$dir" \
            --no-plot
    else
        echo "Warning: Directory $dir not found. Skipping."
    fi

done
```

### Output Locations

By default, analysis modules create output in `./cellpyability_output/` (in your current working directory):
- GDA: `./cellpyability_output/gda_output/`
- Synergy: `./cellpyability_output/synergy_output/`
- Simple: `./cellpyability_output/simple_output/`

You can customize the output location using the `--output-dir` flag:
```bash
cellpyability gda --output-dir /path/to/results ...
```

This ensures the package works correctly whether installed via PyPI or in development mode.

## Running the Windows Application
Running the Windows application requires no programming experience, Python environment, or dependencies. It is a single file containing all three modules with graphical user interfaces (GUIs) for user inputs.

Download the [CellPyAbility application](windows_app/CellPyAbility.exe). I recommend saving it to an empty directory dedicated to CellPyAbility because running the application will generate several files in its directory.

Upon the first run, CellPyAbility may take ~1 min to load. Once running, a GUI prompts the user to choose from three modules. Hovering over each module will give a description of its uses:

- **GDA**: dose-response analysis of two cell lines in response to one treatment

- **synergy**: dose-response analysis of one cell line in response to two treatments in combination

- **simple**: nuclei count matrix in a 96-well format

After selecting a module, the application will look for the CellProfiler.exe in the default save locations:
- "C:\Program Files\CellProfiler\CellProfiler.exe"

- "C:\Program Files (x86)\CellProfiler\CellProfiler.exe"

If CellProfiler.exe cannot be found, the user will be prompted to input the path to the CellProfiler.exe file via the command line. The path is saved to a .txt file within the directory for future reference, so subsequent runs will proceed directly to the next step.

A GUI specific to each module will prompt the user for experimental details. Using the GDA module as an example:
- title of the experiment (e.g. 20250101_CellLine_Drug)

- name of the cell condition in rows B-D (e.g. Cell Line Wildtype)

- name of the cell condition in rows E-G (e.g. Cell Line Gene A KO)

- top on-cell concentration in molar (if cells in column 11 are in 1 uM of drug: 0.000001)

- the dilution factor between columns (if 3-fold dilutions between each column: 3)

- a file browser to select the directory containing the 60 images

After submitting the GUI, a terminal window will open to track CellProfiler's image analysis progress. Once all images are counted, subsequent analysis is almost instant. All figures and tabular results will be in a subdirectory named after the module (e.g. gda_output). See [Example Outputs](#example-outputs).

A small GUI window will then prompt the user if they would like to run another experiment. If "yes", the initial module selection GUI will prompt the user again. If "no", the application will close.

A log file with detailed logging is written to the directory. If the application fails at any point, it may be useful to consult the log for critical messages or to identify the last step to succeed.

## Example Outputs
### GDA Module
The GDA module outputs three tabular files with increasing degrees of analysis:
- [raw nuclei counts](example/example_expected_outputs/example_gda_counts.csv)

- [normalized cell viability matrix](example/example_expected_outputs/example_gda_ViabilityMatrix.csv)

- [cell viability statistics](example/example_expected_outputs/example_gda_Stats.csv)

Additionally, the script generates a plot with 5-parameter logistic curves:

![GDA plot](example/example_expected_outputs/example_gda_plot.png)
### Synergy Module
The synergy module outputs four tabular files:
- [raw nuclei counts](example/example_expected_outputs/example_synergy_counts.csv)

- [normalized cell viability matrix](example/example_expected_outputs/example_synergy_ViabilityMatrix.csv)

- [cell viability statistics](example/example_expected_outputs/example_synergy_stats.csv)

- [Bliss synergy matrix](example/example_expected_outputs/example_synergy_BlissMatrix.csv)

Additionally, the script generates an interactive [3D surface map](example/example_expected_outputs/example_synergy_plot.html) in HTML with synergy as heat:

![synergy plot](example/example_expected_outputs/example_synergy_plot_screenshot.png)

### Simple Module
Finally, the simple module outputs nuclei counts in a 96-well matrix format. This offers maximum flexibility but does not provide any analysis.
- [count matrix](example/example_expected_outputs/example_simple_CountMatrix.csv)

## Modifying the CellProfiler Pipeline

Across multiple cell lines and densities, our provided [CellProfiler Pipeline](src/cellpyability/CellPyAbility.cppipe) appears robust. However, if the user wishes to make any changes, a few guidelines must be followed to maintain compatibility with the scripts as written:
- The module output names must remain as:
  - Count_nuclei
  - FileName_images

- The CellProfiler output CSV file name must remain as:
  - path/to/src/cellpyability/cp_output/CellPyAbilityImage.csv

The modularity of the Python scripts and CellProfiler pipeline may prove useful. For example, if the user wishes to use all 96 wells instead of 60, minor Python knowledge and effort would be needed to enact this change. As another example, the user could analyze microscope images of 10x magnification instead of 4x magnification by increasing the expected pixel ranges for nuclei in the [CellProfiler pipeline](src/cellpyability/CellPyAbility.cppipe).

## Testing

CellPyAbility includes comprehensive testing infrastructure for both automated validation and manual verification.

### Automated Tests

Run the automated test suite to verify all modules produce expected outputs:

```bash
# Install the package if not already installed
pip install -e .

# Run all module tests
python tests/test_module_outputs.py
```

The test suite validates that each module (GDA, Synergy, Simple) produces output matching expected results when processing test data. All tests should pass before using CellPyAbility for your experiments.

**Test Results:**
- ✅ GDA Module: Verifies dose-response analysis accuracy
- ✅ Synergy Module: Verifies drug combination and Bliss independence calculations  
- ✅ Simple Module: Verifies nuclei count matrix generation

Test data is located in `tests/data/` and includes:
- `test_gda_counts.csv`: Pre-counted nuclei for gda test
- `test_synergy_counts.csv`: Pre-counted nuclei for synergy test
- `test_*_Stats.csv`: Expected analysis outputs for validation

### Manual Testing with Example Data

For manual verification, the `example/` directory contains real experimental data that you can process yourself to verify you get identical results:

1. **Download Example Data:**
   ```bash
   git lfs pull  # Downloads large image files
   ```

2. **Run GDA Example:**
   ```bash
   cellpyability gda \
     --title test \
     --upper-name "Cell Line A" \
     --lower-name "Cell Line B" \
     --top-conc 0.000001 \
     --dilution 3 \
     --image-dir example/example_gda
   ```

3. **Compare Your Results:**
   - Your outputs in `src/cellpyability/gda_output/`
   - Expected outputs in `example/example_expected_outputs/`
   - [Test parameters](example/example_params.txt) used to generate examples

**Available Example Datasets:**
- [GDA test data](example/example_gda/): 60 well images for dose-response analysis
- [Synergy test data](example/example_synergy/): 180 well images for drug combination analysis
- [Expected outputs](example/example_expected_outputs/): Reference results for validation

This dual approach ensures both automated validation (for development/CI) and manual verification (to confirm your specific environment is working correctly).

**Note:** We have not tested the analysis scripts on protocols other than those provided. For best results, please follow the provided [protocol](protocol.pdf).

## Contributions
Summary information regarding the authors as of 2025:
- My name is James Elia, and I am a PhD candidate in Yale's Pathology and Molecular Medicine program. I am the author of the repository and the code herein.

- Sam Friedman, MS is a Computational Research Support Analyst at Yale Center for Research Computing. He provided programming mentorship and development support for the repository.

- Ranjit Bindra, MD, PhD is the Harvey and Kate Cushing Professor of Therapeutic Radiology and Professor of Pathology at Yale School of Medicine. He provided scientific mentorship and publishing support for the repository.

## Comments or Questions?
Please contact me at james.elia@yale.edu
