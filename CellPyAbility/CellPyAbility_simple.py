import os
import subprocess
from pathlib import Path
from tkinter import filedialog, ttk

import pandas as pd
from ttkthemes import ThemedTk
# Establish the base directory as the script's location
base_dir = Path(__file__).resolve().parent

# File where the CellProfiler path will be saved
config_file = base_dir / "cellprofiler_path.txt"

def get_cellprofiler_path():
    default_64bit_path = Path(r"C:\Program Files\CellProfiler\CellProfiler.exe")
    default_32bit_path = Path(r"C:\Program Files (x86)\CellProfiler\CellProfiler.exe")
    default_mac_path = Path("/Applications/CellProfiler.app/Contents/MacOS/cp")

    # Check if CellProfiler is saved in the default locations
    if default_64bit_path.exists():
        new_path = default_64bit_path
    elif default_32bit_path.exists():
        new_path = default_32bit_path
    elif default_mac_path.exists():
        new_path = default_mac_path
    else:
        # Check if the alternate path is already saved
        if os.path.exists(config_file):
            with open(config_file, "r") as file:
                saved_path = file.read().strip()
                if os.path.exists(saved_path):
                    print(f"Using saved CellProfiler path: {saved_path}")
                    return saved_path
                else:
                    print("Saved path is invalid. Re-entering path ...")

        # Prompt the user for the path if not saved or invalid
        new_path = input("Enter the path to the CellProfiler program: ").strip()
        new_path = new_path.strip('"').strip("'")
        print(new_path)
    
        # Verify the path exists
        if not os.path.exists(new_path):
            print("Error: Path does not exist. Please try again.")
            return get_cellprofiler_path()  # Recursive call for valid input

        # Save the path to the file for future use
        with open(config_file, "w") as file:
            file.write(new_path)
        print(f"Path saved successfully: {new_path}")
    return new_path

# Get the CellProfiler path
cp_path = get_cellprofiler_path()

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

## Define the path to the pipeline (.cppipe)
cppipe_path = base_dir / 'CellPyAbility.cppipe'

## Define the folder where CellProfiler will output the .csv results
cp_output_dir = base_dir / 'cp_output'
cp_output_dir.mkdir(exist_ok=True)

## Define the folder where simple will output
simple_output_dir = base_dir / 'simple_output'
simple_output_dir.mkdir(exist_ok=True)

# Run CellProfiler from the command line
subprocess.run([cp_path, '-c', '-r', '-p', cppipe_path, '-i', image_dir, '-o', cp_output_dir])

# Define the path to the CellProfiler counting output
cp_csv = cp_output_dir / 'CellPyAbilityImage.csv'

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
count_matrix.to_csv(simple_output_dir / f'{title_name}_simple_CountMatrix.csv')