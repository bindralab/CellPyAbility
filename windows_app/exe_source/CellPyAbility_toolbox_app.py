"""
CellPyAbility_toolbox.py is intended to be an object/function repo for the CellPyAbility application.
This script should remain in the same directory as the other CellPyAbility scripts.
For more information, please see the README at https://github.com/bindralab/CellPyAbility.
"""

import logging
import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, simpledialog

import pandas as pd

# Creates logging protocol for CellPyAbility
# Include 'logger = cellpyability_logger()' at start of script
def cellpyability_logger():
    logger = logging.getLogger("CellPyAbility")

    # Log all messages
    logger.setLevel(logging.DEBUG)

    # Create a log.log file with all messages
    log_file = Path(sys.executable).resolve().parent / "log.log"

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

# Establishes the base directory as /CellPyAbility/
# Include 'base_dir = establish_base() at start of script
def establish_base():
    if getattr(sys, 'frozen', False):
        # Running as a bundled .exe
        base_dir = Path(sys.executable).resolve().parent
    else:
        # Running as a .py script
        base_dir = Path(__file__).resolve().parent

    if not base_dir.exists():
        logger.critical(f'Base directory {base_dir} does not exist.')
        raise RuntimeError(f'Base directory {base_dir} does not exist.')
    elif not os.access(base_dir, os.W_OK):
        logger.critical(f'Base directory {base_dir} is not writable.')
        raise RuntimeError(f'Base directory {base_dir} is not writable.')

    logger.info(f'Base directory {base_dir} established ...')
    return base_dir

# Define base_dir so it can be used in later scripts
base_dir = establish_base()

# The next two functions will be used in get_cellprofiler_path()
def save_txt(config_file, path):
    with open(config_file, 'w') as file:
        file.write(str(path))
    logger.info(f'Path saved succesfully in {config_file} as: {path}')

def prompt_path():
    # We cannot use input() in the app since there is no terminal window
    # Create a hidden root window
    root = tk.Tk()
    root.withdraw()
    logger.debug('Hidden tkinter window created')

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

    # Final cleanup of quotes, just in case
    if path:
        logger.debug("CellProfiler unqiue path location prompt complete")
        return path.strip().strip('"').strip("'")
    else:
        # CellProfiler path is essential, so raise error if they do not provide it
        logger.critical('No CellProfiler path provided')
        raise RuntimeError('No path provided for CellProfiler executable')

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

# Define cp_path
cp_path = get_cellprofiler_path()


def get_pipeline_path():
    """Get CellProfiler pipeline path, supporting frozen and script modes."""
    if getattr(sys, 'frozen', False):
        meipass_dir = getattr(sys, '_MEIPASS', None)
        if meipass_dir is None:
            raise RuntimeError(
                'Internal error: PyInstaller frozen mode detected but sys._MEIPASS attribute '
                'is missing. This should not occur in properly built executables.'
            )
        pipeline_path = Path(meipass_dir) / 'CellPyAbility.cppipe'
    else:
        pipeline_path = Path(__file__).resolve().parent / 'CellPyAbility.cppipe'
    if not pipeline_path.exists():
        raise RuntimeError(f'CellPyAbility.cppipe not found at {pipeline_path}')
    return pipeline_path.resolve()


def get_output_base_dir():
    """Get writable output root for GUI runs."""
    output_base = base_dir / 'cellpyability_output'
    output_base.mkdir(parents=True, exist_ok=True)
    return output_base.resolve()


def configure_cli_backend():
    """
    Configure environment so shared CLI backend behaves correctly in GUI/PyInstaller context.
    """
    os.environ['CELLPYABILITY_PIPELINE_PATH'] = str(get_pipeline_path())
    os.environ['CELLPYABILITY_CONFIG_DIR'] = str(base_dir.resolve())
    os.environ['CELLPYABILITY_CP_PATH'] = str(Path(get_cellprofiler_path()).resolve())
    return get_output_base_dir()