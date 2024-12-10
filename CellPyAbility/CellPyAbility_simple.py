import os
import statistics as st
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import numpy as np
import pandas as pd
from ttkthemes import ThemedTk

## Establish the GUI
# Define GUI functions and assign variables to inputs
def submit():
    global title_name
    # Get input from entry field
    title_name = entry1.get()
    root.after(100, root.destroy)

# Allows selection of folder with images for analysis
def select_image_dir():
    global image_dir
    image_dir = filedialog.askdirectory()
    print(image_dir)

# Create main window
root = ThemedTk(theme='black', themebg=True)

# Create entry fields for inputs
label1 = ttk.Label(root, text='Enter the title of the experiment:')
label1.pack()
entry1 = ttk.Entry(root)
entry1.pack()

# Create buttons for selecting directories and files
image_dir_button = ttk.Button(root, text='Select Image Directory', command=select_image_dir)
image_dir_button.pack()

# Create submit button
submit_button = ttk.Button(root, text='Submit', command=submit)
submit_button.pack()

# Start main loop
root.mainloop()

# Establish the base directory as the script's location
base_dir = Path(__file__).resolve().parent

# Define required CellProfiler paths, then run CellProfiler
## Check for CellProfiler in common save locations across OS
if os.name == 'nt': # Windows
    cp_path = Path(r'C:\Program Files (x86)\CellProfiler\CellProfiler.exe') # 32-bit
    if not cp_path.exists():
        cp_path = Path(r'C:\Program Files\CellProfiler\CellProfiler.exe') # 64-bit
elif os.name == 'darwin': # macOS
    cp_path = Path('/Applications/CellProfiler.app/Contents/MacOS/cp')
elif os.name == 'posix': # Linux (touch grass lol)
    cp_path = Path('cellprofiler')
else:
    raise ValueError(f'Unsupported platform: {os.name}')

try:
    cp_path.resolve(strict=True)
except FileNotFoundError:
    raise FileNotFoundError('CellProfiler not found. Please select the correct path in Pipeline options.')

## Define the path to the pipeline (.cppipe)
cppipe_path = base_dir / 'CellPyAbility.cppipe'

## Define the folder where CellProfiler will output the .csv results
output_dir = base_dir / 'cp_output'

# Run CellProfiler from the command line
subprocess.run([cp_path, '-c', '-r', '-p', cppipe_path, '-i', image_dir, '-o', output_dir])

# Define the path to the CellProfiler counting output
cp_csv = output_dir / 'CellPyAbilityImage.csv'

# Define function to search for and replace well names
def rename_to_any_target(entry, targets):
    for target in targets:
        if target in entry:
            return target
    return entry  # Keep original if no target matches

# List of targets to check
targets = [
    'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11',
    'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11',
    'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11',
    'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11',
    'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11',
    'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10', 'G11',
    ]

# Load the CellProfiler counts into a DataFrame
df = pd.read_csv(cp_csv)
df.drop('ImageNumber', axis=1, inplace=True)
df.columns = ['nuclei', 'well']
df['well'] = df['well'].apply(lambda x: rename_to_any_target(x, targets))
df = df[['well', 'nuclei']]

# Extract rows and columns for the matrix
row_labels = ['B', 'C', 'D', 'E', 'F', 'G']
column_labels = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11']

# Create an empty matrix
count_matrix = pd.DataFrame(
    index=row_labels,
    columns=column_labels,
    dtype=float
)

# Fill the matrix with count data
for row_label in row_labels:
    for column_label in column_labels:
        # Find the well matching the current row and column
        well_pattern = row_label + column_label  # e.g. 'B' + '2' = 'B2'
        matching_wells = df[df['well'] == well_pattern]
        # Match each well to its nuclei count
        count_matrix.at[row_label, column_label] = matching_wells['nuclei']

# Save the matrix to a file
count_matrix.to_csv(base_dir / f'GDA_output/{title_name}_simple_CountMatrix.csv')