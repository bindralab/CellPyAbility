"""
CellPyAbility_toolbox.py is intended to be an object/function repo for the CellPyAbility application.
This script should remain in the same directory as the other CellPyAbility scripts.
For more information, please see the README at https://github.com/bindralab/CellPyAbility.
"""

import logging
import os
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import shutil


class CellPyAbilityError(Exception):
    """Base exception for CellPyAbility."""


class ConfigurationError(CellPyAbilityError):
    """Raised when required configuration is missing or invalid."""


class InputValidationError(CellPyAbilityError):
    """Raised when user-provided inputs are invalid."""


class CellProfilerExecutionError(CellPyAbilityError):
    """Raised when CellProfiler subprocess execution fails."""


class DataValidationError(CellPyAbilityError):
    """Raised when expected data format/columns are not present."""

def cellpyability_logger():
    """
    Creates and configures the CellPyAbility logger.
    
    Logs all messages (DEBUG and above) to cellpyability.log.
    In frozen mode (Windows .exe), logs to the directory containing the executable.
    In script mode, logs to the current working directory.
    Logs INFO and above to console output.
    
    Returns:
    --------
    logger : logging.Logger
        Configured logger instance
    """
    logger = logging.getLogger("CellPyAbility")
    logger.setLevel(logging.DEBUG) # print all messages to log

    # If handlers exist, return immediately to avoid duplicates
    if logger.hasHandlers():
        return logger

    # Determine log file path
    if getattr(sys, 'frozen', False):
        # Bundled executable - log in the same directory as the .exe
        log_dir = Path(sys.executable).resolve().parent
    else:
        # Script mode - log in current working directory
        log_dir = Path.cwd()
        
    log_file = log_dir / "cellpyability.log"
    
    try:
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
    except (PermissionError, IOError):
        # Fallback to current working directory if executable dir is not writable
        log_file = Path.cwd() / "cellpyability.log"
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

    logger.debug(f'Logger setup complete. Logging to: {log_file}')
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
        raise ConfigurationError(f'Package directory {base_dir} does not exist.')
    
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
        # Resolve converts relative paths (../results) to absolute (C:\Users\...\results)
        output_base = Path(output_dir).resolve() 
    
    # Create the output directory if it doesn't exist
    output_base.mkdir(parents=True, exist_ok=True)
    
    # Verify it's writable
    if not os.access(output_base, os.W_OK):
        logger.critical(f'Output directory {output_base} is not writable.')
        raise ConfigurationError(f'Output directory {output_base} is not writable.')
    
    logger.info(f'Output directory {output_base} established ...')
    return output_base

def save_txt(config_file, path):
    """
    Save a path string to a text file.
    
    Parameters:
    -----------
    config_file : str or Path
        Path to the configuration file to write
    path : str or Path
        Path to save in the configuration file
    """
    with open(config_file, 'w') as file:
        file.write(str(path))
    logger.info(f'Path saved successfully in {config_file} as: {path}')

def prompt_path():
    """
    Prompt user to enter the CellProfiler executable path.
    
    In GUI/frozen mode, uses a tkinter file dialog.
    In CLI mode, uses a terminal prompt.
    
    Returns:
    --------
    str
        User-provided path with quotes and whitespace stripped
    """
    if getattr(sys, 'frozen', False):
        import tkinter as tk
        from tkinter import filedialog, simpledialog
        
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()
        logger.debug('Hidden tkinter window created for path prompt')

        # Prompt the user to pick the CellProfiler executable via a file dialog
        path = filedialog.askopenfilename(
            title="Select your CellProfiler executable",
            filetypes=[("Executables", "*.exe" if os.name == "nt" else "*"), ("All files", "*.*")]
        )

        # If they hit “Cancel” (empty string), fall back to a simple text prompt
        if not path:
            path = simpledialog.askstring(
                title="Enter CellProfiler Path",
                prompt="Could not pick a file. Please type the full path to CellProfiler:"
            )

        root.destroy()
        if path:
            return path.strip().strip('"').strip("'")
        else:
            logger.critical('No CellProfiler path provided in GUI prompt')
            raise ConfigurationError('No path provided for CellProfiler executable')

    return input("Enter the path to the CellProfiler program: ").strip().strip('"').strip("'")

def get_cellprofiler_path():
    """
    Get the path to the CellProfiler executable.
    
    Checks for saved path in cellprofiler_path.txt, then checks default installation
    locations on Windows and macOS. If not found, prompts user for the path.
    Saves the path for future use.
    
    Returns:
    --------
    str or Path
        Path to the CellProfiler executable
    """
    env_cp_path = os.getenv("CELLPYABILITY_CP_PATH")
    if env_cp_path:
        env_cp_path = Path(env_cp_path).expanduser().resolve()
        if env_cp_path.exists():
            logger.debug(f"Using CellProfiler path from CELLPYABILITY_CP_PATH: {env_cp_path}")
            return str(env_cp_path)
        raise ConfigurationError(
            f"CELLPYABILITY_CP_PATH is set but does not exist: {env_cp_path}"
        )

    config_dir = Path(os.getenv("CELLPYABILITY_CONFIG_DIR", str(Path.cwd()))).expanduser().resolve()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "cellprofiler_path.txt"

    if config_file.exists():
        with open(config_file, "r") as file:
            saved_path_str = file.read().strip()
            # Verify and resolve the saved path immediately
            if os.path.exists(saved_path_str):
                saved_path = Path(saved_path_str).resolve()
                logger.debug(f"Using saved CellProfiler path: {saved_path}")
                return str(saved_path)
            else:
                logger.warning(f"The path {saved_path_str} does not exist. Proceeding to default locations ...")
    else:
        logger.debug("Saved path is missing. Checking default location ...")

    # Define the default locations
    default_64bit_path = Path(r"C:\Program Files\CellProfiler\CellProfiler.exe")
    default_32bit_path = Path(r"C:\Program Files (x86)\CellProfiler\CellProfiler.exe")
    default_mac_path = Path("/Applications/CellProfiler.app/Contents/MacOS/cp")

    # Check defaults
    if default_64bit_path.exists():
        new_path = default_64bit_path.resolve()
        save_txt(config_file, new_path)
    elif default_32bit_path.exists():
        new_path = default_32bit_path.resolve()
        save_txt(config_file, new_path)
    elif default_mac_path.exists():
        new_path = default_mac_path.resolve()
        save_txt(config_file, new_path)
    else:
        # Prompt user and resolve their input
        new_path_str = prompt_path()
        while not os.path.exists(new_path_str):
            logger.error(f'The path {new_path_str} does not exist. Please enter a valid path:')
            new_path_str = prompt_path()
        
        # Convert valid string to resolved Path object
        new_path = Path(new_path_str).resolve()
        logger.debug(f'Saving new path: {new_path}.')
        save_txt(config_file, new_path)

    logger.info('CellProfiler path successfully identified ...')
    return str(new_path)
    
# Define cp_path as None initially (will be set when needed)
cp_path = None

def _ensure_cellprofiler_path():
    """Ensure CellProfiler path is set, calling get_cellprofiler_path if needed."""
    global cp_path
    if cp_path is None:
        cp_path = get_cellprofiler_path()
    return cp_path

def gen_dose_range(dose_max: float, dilution: float, num_doses: int) -> np.ndarray:
    """
    Generates a dose gradient from low to high (excluding vehicle).

    Parameters:
    -----------
    dose_max: float
        top concentration (source of serial dilutions)
    dilution: float
        multiplicative gaps between concentrations (3 = 3fold dilutions)
    num_doses: int
        the number of concentrations, including the top and excluding vehicle

    Returns:
    -----------
    dose_array : NumPy array
    """
    if dose_max <= 0:
        raise InputValidationError("Top concentration must be greater than 0.")
    if dilution <= 1:
        raise InputValidationError("Dilution factor must be greater than 1.")
    if num_doses < 1:
        raise InputValidationError("Number of doses must be at least 1.")

    # Calculate lowest dose directly to avoid accumulating error from float division
    dose_min = dose_max / (dilution ** (num_doses-1))

    # Generate the array log spaced
    dose_array = np.geomspace(dose_min, dose_max, num_doses)

    # Round to 14 sigfig for determinism across machines
    dose_array = np.array([float(f'{x:.14g}') for x in dose_array])
    
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
        counts_path = Path(counts_file).resolve()
        if not counts_path.exists():
            logger.critical(f'Counts file {counts_file} does not exist.')
            raise InputValidationError(f'Counts file {counts_file} does not exist.')
        logger.info(f'Using pre-existing counts file: {counts_file}')
        df_cp = pd.read_csv(counts_path)
        return df_cp, counts_path
    
    # Define the path to the CellProfiler pipeline (.cppipe) in the package directory
    pipeline_env = os.getenv("CELLPYABILITY_PIPELINE_PATH")
    cppipe_path = Path(pipeline_env).expanduser().resolve() if pipeline_env else (base_dir / 'CellPyAbility.cppipe')
    if cppipe_path.exists():
        logger.debug('CellProfiler pipeline exists in package directory ...')
    else:
        logger.critical('CellProfiler pipeline CellPyAbility.cppipe not found in package directory.')
        logger.info('If you are using a different pipeline, make sure it is named CellPyAbility.cppipe and is in the package directory.')
        raise ConfigurationError(
            f'CellProfiler pipeline CellPyAbility.cppipe not found: {cppipe_path}'
        )

    ## Define the folder where CellProfiler will output the .csv results
    # Use the output directory structure for writable files
    output_base = get_output_base_dir(output_dir)
    cp_output_dir = output_base / 'cp_output'
    cp_output_dir.mkdir(exist_ok=True)
    logger.debug(f'cp_output/ directory identified or created at {cp_output_dir}')

    # Convert image_dir to a Path object and resolve it to an absolute path
    # Handles OS-specific separators and converts relative paths (./images) to absolute paths (C:\Users\...)
    image_path_obj = Path(image_dir).resolve()
    
    if not image_path_obj.exists():
        logger.critical(f"Image directory does not exist: {image_path_obj}")
        raise InputValidationError(f"Image directory does not exist: {image_path_obj}")
        
    # We also ensure the pipeline path and output dir are absolute resolved paths
    cppipe_path_obj = cppipe_path.resolve()
    cp_output_obj = cp_output_dir.resolve()
    cp_csv = cp_output_dir / 'CellPyAbilityImage.csv'

    # Prevent stale output reuse across failed runs
    if cp_csv.exists():
        cp_csv.unlink()
        logger.debug(f'Removed existing stale CellProfiler output: {cp_csv}')

    # Run CellProfiler from the command line
    logger.debug('Starting CellProfiler from command line ...')
    cp_exe = _ensure_cellprofiler_path()
    
    # We explicitly convert paths to str() here
    # Subprocess command receives clean string paths formatted for host OS
    command = [
        cp_exe,
        '-c', '-r',
        '-p', str(cppipe_path_obj),
        '-i', str(image_path_obj),
        '-o', str(cp_output_obj)
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, timeout=3600)
    except subprocess.TimeoutExpired as e:
        logger.error('CellProfiler execution timed out.')
        raise CellProfilerExecutionError('CellProfiler timed out after 3600 seconds.') from e
    except subprocess.CalledProcessError as e:
        logger.error(f'CellProfiler execution failed with return code {e.returncode}.')
        stderr = (e.stderr or "").strip()
        stdout = (e.stdout or "").strip()
        details = stderr if stderr else stdout
        raise CellProfilerExecutionError(
            f"CellProfiler failed (exit code {e.returncode}). {details}".strip()
        ) from e
    logger.info('CellProfiler nuclei counting complete.')

    # Define the path to the CellProfiler counting output
    if cp_csv.exists():
        logger.debug('CellPyAbilityImage.csv exists in /cp_output/ ...')
    else:
        logger.critical('CellProfiler output CellPyAbilityImage.csv does not exist in /cp_output/')
        logger.info('If CellPyAbility.cppipe is modified, make sure the output is still named CellPyAbilityImage.csv')
        raise CellProfilerExecutionError(
            'CellProfiler completed but expected output CellPyAbilityImage.csv was not created.'
        )

    # Load the CellProfiler counts into a DataFrame
    df_cp = pd.read_csv(cp_csv)
    
    return df_cp, cp_csv

def rename_wells(tiff_name): 
    """
    Maps well ID from file name to 96-well plate wells.
    """
    match = re.search(r'([A-Ha-h])0*(\d{1,2})', tiff_name)
    
    if match:
        row = match.group(1).upper() # Force uppercase (b -> B)
        col = match.group(2)         # Capture digit (02 -> 2 due to 0* placement)
        
        # Return clean "B2" format
        return f"{row}{col}"
        
    return tiff_name


def standardize_counts_dataframe(df_cp):
    """
    Standardize CellProfiler counts data to ['nuclei', 'well'].
    
    Verifies that the required data is present and attempts to map various
    possible CellProfiler output column names to a standard format.
    
    Raises:
    -------
    DataValidationError
        If the required columns cannot be found or the dataframe is empty.
    """
    if df_cp.empty:
        raise DataValidationError("The provided counts data is empty.")

    columns = list(df_cp.columns)
    
    # If already standardized, return a copy of the required columns
    if {'nuclei', 'well'}.issubset(columns):
        return df_cp[['nuclei', 'well']].copy()

    # Identify count column
    count_candidates = ['Count_Nuclei', 'count_nuclei', 'Nuclei', 'nuclei']
    count_col = next((c for c in count_candidates if c in columns), None)
    
    # Identify well/filename column
    well_candidates = ['FileName_DAPI', 'FileName_DNA', 'FileName', 'well']
    well_col = next((c for c in well_candidates if c in columns), None)

    # Heuristics for missing columns
    if count_col is None or well_col is None:
        non_image_cols = [c for c in columns if c != 'ImageNumber']
        
        # Inference for count column
        if count_col is None:
            numeric_cols = [
                c for c in non_image_cols if pd.api.types.is_numeric_dtype(df_cp[c])
            ]
            if numeric_cols:
                count_col = numeric_cols[0]
                logger.warning(
                    f"Count column not found by name. Inferred '{count_col}' as nuclei count column."
                )

        # Inference for well column
        if well_col is None:
            remaining = [c for c in non_image_cols if c != count_col]
            if remaining:
                well_col = remaining[0]
                logger.warning(
                    f"Well/FileName column not found by name. Inferred '{well_col}' as well identifier."
                )

    if count_col is None or well_col is None:
        raise DataValidationError(
            f"Could not identify required columns in counts file. Found: {columns}. "
            "Expected columns like 'Count_Nuclei' and 'FileName_DAPI'."
        )

    # Standardize and copy
    standardized = df_cp[[count_col, well_col]].copy()
    standardized.columns = ['nuclei', 'well']

    # Final validation of contents
    if standardized['nuclei'].isna().any():
        raise DataValidationError('Nuclei count column contains missing values.')
    if standardized['well'].isna().any():
        raise DataValidationError('Well identifier column contains missing values.')

    return standardized

def rename_counts(cp_csv, counts_csv):
    """
    Rename or copy CellProfiler counts file to final output location.
    Uses copy if source is not in cp_output (e.g., test data), otherwise renames.
    """
    try:
        # Resolve both paths to absolute to ensure safe string comparison
        cp_csv_path = Path(cp_csv).resolve()
        counts_csv_path = Path(counts_csv).resolve()
        
        # Check if source is NOT in cp_output directory (e.g. external test data)
        # Using .resolve() makes this check robust regardless of relative path usage
        if 'cp_output' not in str(cp_csv_path):
            shutil.copy2(cp_csv_path, counts_csv_path)
            logger.debug(f'{cp_csv_path} successfully copied to {counts_csv_path}')
        else:
            os.rename(cp_csv_path, counts_csv_path)
            logger.debug(f'{cp_csv_path} successfully renamed to {counts_csv_path}')
            
    except FileNotFoundError:
        logger.debug(f'{cp_csv} not found')
    except PermissionError:
        logger.debug(f'Permission denied. {cp_csv} may be open or in use.')
    except Exception as e:
        logger.debug(f'While renaming {cp_csv}, an error occurred: {e}')

# Define models at module level so they are accessible
def fivePL(x, A, B, C, D, G):
    """
    Five-parameter logistic (5PL) dose-response model.
    
    Parameters:
    -----------
    x : array-like
        Dose/concentration values
    A : float
        Minimum asymptote (response at infinite dose)
    B : float
        Hill slope
    C : float
        Inflection point (IC50/EC50)
    D : float
        Maximum asymptote (response at zero dose)
    G : float
        Asymmetry factor
    
    Returns:
    --------
    array-like
        Predicted response values
    """
    return ((A - D) / (1.0 + (x / C) ** B) ** G) + D

def hill(x, Emax, EC50, HillSlope):
    """
    Hill equation for dose-response curves.
    
    Parameters:
    -----------
    x : array-like
        Dose/concentration values
    Emax : float
        Maximum effect
    EC50 : float
        Half-maximal effective concentration
    HillSlope : float
        Hill coefficient (slope factor)
    
    Returns:
    --------
    array-like
        Predicted response values
    """
    return Emax * (x**HillSlope) / (EC50**HillSlope + x**HillSlope)

def fit_response_curve(x, y, name):
    """
    Fits 5PL, falls back to Hill, returns (x_plot, y_plot, IC50, params).
    Solves for IC50 algebraically. Returns NaN if IC50 is unsolvable.
    Input x and y should be numpy arrays.
    """
    # Create smooth x-axis for plotting
    x_plot = np.logspace(np.log10(min(x[x > 0])), np.log10(max(x)), 1000)

    # Initial Guesses (Heuristic)
    y_max = np.max(y)
    y_min = np.min(y)
    
    # Find x closest to half-maximal response for initial C/EC50 guess
    # We clip 0.5 to be between min and max to avoid indexing errors
    target_y = (y_max + y_min) / 2
    idx = (np.abs(y - target_y)).argmin()
    c_guess = x[idx]
    
    # [A (max), B (slope), C (inflection), D (min), G (asymmetry)]
    p0_5PL = [y_max, 1.0, c_guess, y_min, 1.0] 
    
    # [Emax, EC50, HillSlope]
    p0_Hill = [y_max, c_guess, 1.0]

    try:
        # Try 5PL
        popt, _ = curve_fit(fivePL, x, y, p0=p0_5PL, maxfev=5000)
        
        # Algebraic IC50 for 5PL
        A, B, C, D, G = popt
        
        # Check domain validity for IC50 (must be able to take roots)
        # We need the term inside the root to be positive
        try:
             term = (A - D) / (0.5 - D)
             if term <= 0:
                 raise ValueError("IC50 undefined (curve doesn't cross 0.5)")
             
             # Solve for x where y = 0.5
             ic50 = C * ((term**(1/G)) - 1)**(1/B)
        except (ValueError, ArithmeticError):
             ic50 = np.nan

        return x_plot, fivePL(x_plot, *popt), ic50
        
    except (RuntimeError, ValueError):
        # Fallback to Hill
        try:
             popt, _ = curve_fit(hill, x, y, p0=p0_Hill, maxfev=10000)
             # Hill parameter index 1 is EC50
             ic50 = popt[1] 
             return x_plot, hill(x_plot, *popt), ic50
        except (RuntimeError, ValueError, ArithmeticError, OverflowError):
             logger.warning(f"Could not fit {name}. Returning connect-the-dots")
             # Return straight lines between points if fit fails
             return x, y, np.nan
