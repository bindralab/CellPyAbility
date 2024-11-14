# nuclei counter: local version
import numpy as np
import pathlib as path
import plotly.graph_objects as go
import subprocess
import statistics as st
import pandas as pd
from pathlib import Path


import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkthemes import ThemedTk

## Establish the GUI
# Define GUI functions and assign variables to inputs
def submit():
    global x_doses, y_doses, x_title, y_title, plot_title

    # Get input from entry field
    input_x_doses = entry_x_doses.get()
    input_y_doses = entry_y_doses.get()
    plot_title = entry_plot_title.get()
    x_title = entry_x_title.get()
    y_title = entry_y_title.get()

    # Split input into list of strings
    x_doses_str = input_x_doses.split('\t')

    # Check if there are 9 values
    if len(x_doses_str) != 9:
        messagebox.showerror("Error", "Please enter 9 values (exclude zero).")
        return

    # Convert list of strings to list of floats
    try:
        x_doses = [float(dose) for dose in x_doses_str]
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers.")
        return x_doses

 # Split input into list of strings
    y_doses_str = input_y_doses.split('\t')

    # Check if there are 5 values
    if len(y_doses_str) != 5:
        messagebox.showerror("Error", "Please enter 5 values (exclude zero).")
        return

    # Convert list of strings to list of floats
    try:
        y_doses = [float(dose) for dose in y_doses_str]
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers.")
        return y_doses
    root.after(100, root.destroy)

# Allows selection of folder with images for analysis
def select_image_dir():
    global image_dir
    image_dir = filedialog.askdirectory()
    print(image_dir)

# Create main window
root = ThemedTk(theme="black", themebg=True)

# Create GUI labels and entry fields
label_plot_title = ttk.Label(root, text = "Enter the title of the plot:")
label_plot_title.pack()
entry_plot_title = ttk.Entry(root)
entry_plot_title.pack()

label_x_title = ttk.Label(root, text = "Enter the name of the vertical drug used:")
label_x_title.pack()
entry_x_title = ttk.Entry(root)
entry_x_title.pack()

label_y_doses = ttk.Label(root, text="Enter the vertical five doses (exclude zero), separated by tab:")
label_y_doses.pack()
entry_y_doses = ttk.Entry(root)
entry_y_doses.pack()

label_y_title = ttk.Label(root, text = "Enter the name of the horizontal drug used:")
label_y_title.pack()
entry_y_title = ttk.Entry(root)
entry_y_title.pack()

label_x_doses = ttk.Label(root, text="Enter the horizontal nine doses (exclude zero), separated by tab:")
label_x_doses.pack()
entry_x_doses = ttk.Entry(root)
entry_x_doses.pack()

# Create buttons for selecting directories and files
image_dir_button = ttk.Button(root, text="Select Image Directory", command=select_image_dir)
image_dir_button.pack()

# Create submit button
submit_button = ttk.Button(root, text="Submit", command=submit)
submit_button.pack()

# Start main loop
root.mainloop()

# Establish the base directory as the script's location
base_dir = Path(__file__).resolve().parent

# Define required CellProfiler paths, then run CellProfiler
## Define the path to the CellProfiler executable (.exe)
cp_path = Path(r"C:\Program Files (x86)\CellProfiler\CellProfiler.exe")

## Define the path to the pipeline (.cppipe)
cppipe_path = base_dir / "CellPyAbility.cppipe"

## Define the folder where CellProfiler will output the .csv results
output_dir = base_dir / "cp_output"

# Run CellProfiler from the command line
subprocess.run([cp_path, "-c", "-r", "-p", cppipe_path, "-i", image_dir, "-o", output_dir])

# Define the path to the CellProfiler counting output
cp_csv = output_dir / "CellPyAbilityImage.csv"

# Load the CellProfiler counts into a DataFrame
df = pd.read_csv(cp_csv)

# Define wells
well_dict = {
    'B2': [3, 63, 123], 'B3': [4, 64, 124], 'B4': [5, 65, 125], 'B5': [6, 66, 126], 'B6': [7, 67, 127], 'B7': [8, 68, 128], 'B8': [9, 69, 129], 'B9': [10, 70, 130], 'B10': [1, 61, 121], 'B11': [2, 62, 122],
    'C2': [13, 73, 133], 'C3': [14, 74, 134], 'C4': [15, 75, 135], 'C5': [16, 76, 136], 'C6': [17, 77, 137], 'C7': [18, 78, 138], 'C8': [19, 79, 139], 'C9': [20, 80, 140], 'C10': [11, 71, 131], 'C11': [12, 72, 132],
    'D2': [23, 83, 143], 'D3': [24, 84, 144], 'D4': [25, 85, 145], 'D5': [26, 86, 146], 'D6': [27, 87, 147], 'D7': [28, 88, 148], 'D8': [29, 89, 149], 'D9': [30, 90, 150], 'D10': [21, 81, 141], 'D11': [22, 82, 142],
    'E2': [33, 93, 153], 'E3': [34, 94, 154], 'E4': [35, 95, 155], 'E5': [36, 96, 156], 'E6': [37, 97, 157], 'E7': [38, 98, 158], 'E8': [39, 99, 159], 'E9': [40, 100, 160], 'E10': [31, 91, 151], 'E11': [32, 92, 152],
    'F2': [43, 103, 163], 'F3': [44, 104, 164], 'F4': [45, 105, 165], 'F5': [46, 106, 166], 'F6': [47, 107, 167], 'F7': [48, 108, 168], 'F8': [49, 109, 169], 'F9': [50, 110, 170], 'F10': [41, 101, 161], 'F11': [42, 102, 162],
    'G2': [53, 113, 173], 'G3': [54, 114, 174], 'G4': [55, 115, 175], 'G5': [56, 116, 176], 'G6': [57, 117, 177], 'G7': [58, 118, 178], 'G8': [59, 119, 179], 'G9': [60, 120, 180], 'G10': [51, 111, 171], 'G11': [52, 112, 172]
}

# Calculate mean and standard deviation for each well triplicate
well_means = []
well_std = []
for wells in well_dict.values():
    counts = df[df['ImageNumber'].isin(wells)]['Count_Nuclei']
    well_means.append(counts.mean())
    well_std.append(counts.std())

row_concentrations = {
    'B': 0,  # Control
    'C': y_doses[0],
    'D': y_doses[1],
    'E': y_doses[2],
    'F': y_doses[3],
    'G': y_doses[4]
}

column_concentrations = {
    '2': 0,  # Control
    '3': x_doses[0],
    '4': x_doses[1],
    '5': x_doses[2],
    '6': x_doses[3],
    '7': x_doses[4],
    '8': x_doses[5],
    '9': x_doses[6],
    '10': x_doses[7],
    '11': x_doses[8]
}

# Extract row and column labels from well names
rows = [name[0] for name in well_dict.keys()]
columns = [name[1:] for name in well_dict.keys()]

# Map concentrations to rows and columns
row_conc = [row_concentrations[row] for row in rows]
col_conc = [column_concentrations[col] for col in columns]

# Normalize well means to vehicle (B2) mean
normalized_means = [mean / well_means[0] for mean in well_means]

# Frame that data
well_descriptions = {
    'Well': list(well_dict.keys()),
    'Mean': well_means,
    'Standard Deviation': well_std,
    'Normalized Mean': normalized_means,
    'Row Drug Concentration': row_conc,
    'Column Drug Concentration': col_conc
}
df2_results = pd.DataFrame(well_descriptions)

# Export as .csv
csv_output_path = r"C:\Users\james\Documents\Yale\Bindra\Python GDA\csv output\csv_ouput.csv"
df2_results.to_csv(csv_output_path, index=False)

# Read .csv with pandas
df2 = pd.read_csv(csv_output_path)

# Create arrays for x drug effects alone and y drug effects alone
x_effect_alone = df2[df2['Well'].str.startswith('B')]['Normalized Mean'].values
y_effect_alone = df2[df2['Well'].str.endswith('2')]['Normalized Mean'].values

# Initialize a list to store Bliss independence results
bliss_results = []

# Iterate over each well in the DataFrame
for index, row in df2.iterrows():
    well_name = row['Well']
    observed_combined_effect = row['Normalized Mean']
    
    # Determine the x and y effects based on the well name
    if well_name[0] in 'BCDEFG' and well_name[1:] in '234567891011':
        x_effect = df2[df2['Well'] == 'B' + well_name[1:]]['Normalized Mean'].values[0]
        y_effect = df2[df2['Well'] == well_name[0] + '2']['Normalized Mean'].values[0]
        
        # Calculate the expected combined effect
        expected_combined_effect = x_effect * y_effect
        
        # Calculate the Bliss independence
        bliss_independence = expected_combined_effect - observed_combined_effect
        
        # Store the result
        bliss_results.append({
            'Well': well_name,
            'Expected Combined Effect': expected_combined_effect,
            'Observed Combined Effect': observed_combined_effect,
            'Bliss Independence': bliss_independence
        })

# Convert the results to a DataFrame
bliss_df = pd.DataFrame(bliss_results)

# Add 'Row Drug Concentration' and 'Column Drug Concentration' to bliss_df
bliss_df['Row Drug Concentration'] = bliss_df['Well'].apply(lambda x: row_concentrations[x[0]])
bliss_df['Column Drug Concentration'] = bliss_df['Well'].apply(lambda x: column_concentrations[x[1:]])

print(bliss_df)
bliss_output_path = r"C:\Users\james\Documents\Yale\Bindra\Python GDA\csv output\bliss_df.csv"
bliss_df.to_csv(bliss_output_path, index=False)

# Create a pivot table for normalized means
normalized_means_pivot = df2.pivot(index='Column Drug Concentration', columns='Row Drug Concentration', values='Normalized Mean')

# Create a pivot table for Bliss independence
bliss_independence_pivot = bliss_df.pivot(index='Column Drug Concentration', columns='Row Drug Concentration', values='Bliss Independence')

# Convert pivot tables to numpy arrays
cell_survival = normalized_means_pivot.values
bliss_independence = bliss_independence_pivot.values

normalized_means_pivot.to_csv(r"C:\Users\james\Documents\Yale\Bindra\Python GDA\csv output\normalized_means_pivot.csv")
bliss_independence_pivot.to_csv(r"C:\Users\james\Documents\Yale\Bindra\Python GDA\csv output\bliss_pivot.csv")

# Extract x and y values from the pivot tables
x_values = normalized_means_pivot.columns.values
y_values = normalized_means_pivot.index.values

# Replace zero values in x_values and y_values with a small positive number
min_x_value = min(x_values[x_values > 0])
min_y_value = min(y_values[y_values > 0])

x_values = np.where(x_values == 0, min_x_value / (x_values[3]/x_values[2]), x_values)
y_values = np.where(y_values == 0, min_y_value / (y_values[3]/y_values[2]), y_values)

x_tickvals = np.unique(np.concatenate(([min_x_value / (x_values[3]/x_values[2])], x_values)))
y_tickvals = np.unique(np.concatenate(([min_y_value / (y_values[3]/y_values[2])], y_values)))
x_ticktext = ['0'] + [f'{val:.1e}' for val in x_tickvals[1:]]
y_ticktext = ['0'] + [f'{val:.1e}' for val in y_tickvals[1:]]

# Create the 3D surface plot
fig = go.Figure(data=[go.Surface(
    z=cell_survival,
    x=x_values,
    y=y_values,
    surfacecolor=bliss_independence,
    colorscale='jet_r', 
    cmin=-0.3, cmax=0.3,
    colorbar=dict(title='Bliss Independence')
)])

# Find the maximum value in the cell_survival array
max_z_value = np.max(cell_survival)

# Update layout to set x and y axes to logarithmic scale
fig.update_layout(
    title=str(plot_title),
    scene=dict(
        xaxis=dict(
            title=x_title,
            type='log',
            ticktext=x_ticktext,
            tickvals=x_tickvals
        ),
        yaxis=dict(
            title=y_title,
            type='log',
            ticktext=y_ticktext,
            tickvals=y_tickvals
        ),
        zaxis=dict(
            title= 'Relative Cell Survival',
            range=[0,max_z_value]
        )
    )
)

# Show the plot
fig.write_html(r"C:\Users\james\Documents\Yale\Bindra\Python GDA\csv output\Bliss_plot")
fig.show()