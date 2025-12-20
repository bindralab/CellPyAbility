"""
CellPyAbility_toolbox.py is intended to be an object/function repo for the CellPyAbility application.
This script should remain in the same directory as the other CellPyAbility scripts.
For more information, please see the README at https://github.com/bindralab/CellPyAbility.
"""

import logging
import os
import subprocess
from pathlib import Path

import pandas as pd

# Creates logging protocol for CellPyAbility
# Include 'logger = cellpyability_logger()' at start of script
def cellpyability_logger():
    logger = logging.getLogger("CellPyAbility")

    # Log all messages
    logger.setLevel(logging.DEBUG)

    # Create a log.log file with all messages
    log_file = Path(__file__).with_name("log.log")
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)

    # Only log >= INFO messages in the terminal
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Format the log messages to include time and level
    fmt = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.debug('Logger setup complete.')
    return logger

# Define logger so it can be referenced in later functions
logger = cellpyability_logger()

# Establishes the base directory for package resources (read-only)
# Use get_output_base_dir() for writable output directories
def establish_base():
    """Get the package installation directory (for reading resources like .cppipe files)."""
    base_dir = Path(__file__).resolve().parent
    
    if not base_dir.exists():
        logger.critical(f'Package directory {base_dir} does not exist.')
        exit(1)
    
    logger.info(f'Package directory {base_dir} established ...')
    return base_dir

# Define base_dir for package resources (pipeline files, etc.)
base_dir = establish_base()

def get_output_base_dir(output_dir=None):
    """
    Get the base directory for output files.
    
    Args:
        output_dir: Optional custom output directory path. If None, uses current working directory.
    
    Returns:
        Path object to the output base directory
    """
    if output_dir is None:
        # Use current working directory for PyPI compatibility
        output_base = Path.cwd() / 'cellpyability_output'
    else:
        output_base = Path(output_dir)
    
    # Create the output directory if it doesn't exist
    output_base.mkdir(parents=True, exist_ok=True)
    
    # Verify it's writable
    if not os.access(output_base, os.W_OK):
        logger.critical(f'Output directory {output_base} is not writable.')
        exit(1)
    
    logger.info(f'Output directory {output_base} established ...')
    return output_base

# The next two functions will be used in get_cellprofiler_path()
def save_txt(config_file, path):
    with open(config_file, 'w') as file:
        file.write(str(path))
    logger.info(f'Path saved succesfully in {config_file} as: {path}')

def prompt_path():
    return input("Enter the path to the CellProfiler program: ").strip().strip('"').strip("'")

# Include 'cp_path = get_cellprofiler_path()' at start of script
def get_cellprofiler_path():
    # First check if a CellProfiler path exists in the directory
    config_file = base_dir / "cellprofiler_path.txt"

    if config_file.exists():
        with open(config_file, "r") as file:
            saved_path = file.read().strip()
            if os.path.exists(saved_path):
                logger.debug(f"Using saved CellProfiler path: {saved_path}.")
                return saved_path
            else:
                logger.warning(f"The path {saved_path} does not exist. Proceeding to default locations ...")
    else:
        logger.debug("Saved path is missing. Checking default location ...")

    # Define the default locations where CellProfiler is saved
    default_64bit_path = Path(r"C:\Program Files\CellProfiler\CellProfiler.exe")
    default_32bit_path = Path(r"C:\Program Files (x86)\CellProfiler\CellProfiler.exe")
    default_mac_path = Path("/Applications/CellProfiler.app/Contents/MacOS/cp")

    # Check if CellProfiler is saved in the default locations
    if default_64bit_path.exists():
        new_path = default_64bit_path
        save_txt(config_file, new_path)
    elif default_32bit_path.exists():
        new_path = default_32bit_path
        save_txt(config_file, new_path)
    elif default_mac_path.exists():
        new_path = default_mac_path
        save_txt(config_file, new_path)
    else:
        # Prompt the user for the a custom path if it cannot be found
        new_path = prompt_path()
        while not os.path.exists(new_path):
            logger.error(f'The path {new_path} does not exist. Please enter a valid path:')
            new_path = prompt_path()
            logger.debug(f'Saving new path: {new_path}.')
        # Save the path to the file for future use
        save_txt(config_file, new_path)

    logger.info('CellProfiler path succesfully identified ...')
    return new_path

# Define cp_path as None initially - will be set when needed
cp_path = None

def _ensure_cellprofiler_path():
    """Ensure CellProfiler path is set, calling get_cellprofiler_path if needed."""
    global cp_path
    if cp_path is None:
        cp_path = get_cellprofiler_path()
    return cp_path

def dose_range_x(dose_max, dilution):
    dose_array = [dose_max]
    for i in range(8):
        dose_max /= (dilution)
        dose_array.insert(0, dose_max)
    logger.debug('Concentration gradient array created.')
    return dose_array

def dose_range_y(dose_max, dilution):
    dose_array = [dose_max]
    for i in range(4):
        dose_max /= (dilution)
        dose_array.insert(0, dose_max)
    logger.debug('Concentration gradient array created.')
    return dose_array

# Runs CellProfiler from the command line with the path to the image directory as a parameter
# When ready to run, write 'df_cp = run_cellprofiler()'
def run_cellprofiler(image_dir, counts_file=None, output_dir=None):
    """
    Run CellProfiler on images or load pre-existing counts file.
    
    Parameters:
    -----------
    image_dir : str
        Directory containing images to analyze
    counts_file : str, optional
        Path to pre-existing counts CSV file (for testing). If provided,
        CellProfiler is not run and this file is used instead.
    output_dir : str, optional
        Base directory for output files. If None, uses current working directory
        and creates './cellpyability_output/' subdirectory for results.
    
    Returns:
    --------
    df_cp : pandas.DataFrame
        DataFrame with nuclei counts
    cp_csv : Path
        Path to the counts CSV file
    """
    
    # If a counts file is provided, use it instead of running CellProfiler
    if counts_file is not None:
        counts_path = Path(counts_file)
        if not counts_path.exists():
            logger.critical(f'Counts file {counts_file} does not exist.')
            exit(1)
        logger.info(f'Using pre-existing counts file: {counts_file}')
        df_cp = pd.read_csv(counts_path)
        return df_cp, counts_path
    
    ## Define the path to the pipeline (.cppipe) - this is in the package directory
    cppipe_path = base_dir / 'CellPyAbility.cppipe'
    if cppipe_path.exists():
        logger.debug('CellProfiler pipeline exists in package directory ...')
    else:
        logger.critical('CellProfiler pipeline CellPyAbility.cppipe not found in package directory.')
        logger.info('If you are using a different pipeline, make sure it is named CellPyAbility.cppipe and is in the package directory.')
        exit(1)

    ## Define the folder where CellProfiler will output the .csv results
    # Use the output directory structure for writable files
    output_base = get_output_base_dir(output_dir)
    cp_output_dir = output_base / 'cp_output'
    cp_output_dir.mkdir(exist_ok=True)
    logger.debug(f'cp_output/ directory identified or created at {cp_output_dir}')

    # Run CellProfiler from the command line
    logger.debug('Starting CellProfiler from command line ...')
    cp_exe = _ensure_cellprofiler_path()
    subprocess.run([cp_exe, '-c', '-r', '-p', cppipe_path, '-i', image_dir, '-o', cp_output_dir])
    logger.info('CellProfiler nuclei counting complete.')

    # Define the path to the CellProfiler counting output
    cp_csv = cp_output_dir / 'CellPyAbilityImage.csv'
    if cp_csv.exists():
        logger.debug('CellPyAbilityImage.csv exists in /cp_output/ ...')
    else:
        logger.critical('CellProfiler output CellPyAbilityImage.csv does not exist in /cp_output/')
        logger.info('If CellPyAbility.cppipe is modified, make sure the output is still named CellPyAbilityImage.csv')
        exit(1)

    # Load the CellProfiler counts into a DataFrame
    df_cp = pd.read_csv(cp_csv)
    
    return df_cp, cp_csv

# Names of the inner 60 wells of a 96-well plate
wells = [
    'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11',
    'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11',
    'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11',
    'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11',
    'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11',
    'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10', 'G11',
    ]

def rename_wells(tiff_name, wells):
    for well in wells:
        if well in tiff_name:
            return well
    logger.debug('Well names extracted from file names.')
    return tiff_name  # Keep original if no target matches

def rename_counts(cp_csv, counts_csv):
    """
    Rename or copy CellProfiler counts file to final output location.
    Uses copy if source is not in cp_output (e.g., test data), otherwise renames.
    """
    try:
        cp_csv_path = Path(cp_csv)
        counts_csv_path = Path(counts_csv)
        
        # If source is not in cp_output directory, copy instead of rename
        # This preserves test data files
        if 'cp_output' not in str(cp_csv_path):
            import shutil
            shutil.copy2(cp_csv, counts_csv)
            logger.debug(f'{cp_csv} succesfully copied to {counts_csv}')
        else:
            os.rename(cp_csv, counts_csv)
            logger.debug(f'{cp_csv} succesfully renamed to {counts_csv}')
    except FileNotFoundError:
        logger.debug(f'{cp_csv} not found')
    except PermissionError:
        logger.debug(f'Permission denied. {cp_csv} may be open or in use.')
    except Exception as e:
        logger.debug(f'While renaming {cp_csv}, an error occurred: {e}')