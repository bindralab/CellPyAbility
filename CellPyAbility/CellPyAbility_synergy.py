import os
import subprocess
from pathlib import Path
from tkinter import ttk, messagebox, filedialog
from ttkthemes import ThemedTk

import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Establish the base directory as the script's location
base_dir = Path(__file__).resolve().parent

# File where the CellProfiler path will be saved
config_file = base_dir / "cellprofiler_path.txt"

if not base_dir.exists():
    print(f"Base directory {base_dir} does not exist.")
    exit(1)
elif not os.access(base_dir, os.W_OK):
    print(f"Base directory {base_dir} is not writable.")
    exit(1)

def get_cellprofiler_path():
    # Check if the path has already been saved
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
def select_image_dir():
    global temp_image_dir
    temp_image_dir = filedialog.askdirectory()
    print(f"Directory selected: {temp_image_dir}")

def submit():
    global x_doses, y_doses, x_title, y_title, plot_title, image_dir

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
        messagebox.showerror('Error', 'Please enter 9 values (exclude zero).')
        return

    # Convert list of strings to list of floats
    try:
        x_doses = [float(dose) for dose in x_doses_str]
    except ValueError:
        messagebox.showerror('Error', 'Please enter valid numbers.')

 # Split input into list of strings
    y_doses_str = input_y_doses.split('\t')

    # Check if there are 5 values
    if len(y_doses_str) != 5:
        messagebox.showerror('Error', 'Please enter 5 values (exclude zero).')
        return

    # Convert list of strings to list of floats
    try:
        y_doses = [float(dose) for dose in y_doses_str]
    except ValueError:
        messagebox.showerror('Error', 'Please enter valid numbers.')
    
    # Assign the temporary image directory selected to the image_dir variable for further analysis
    image_dir = temp_image_dir
    root.destroy()

# Create main window
root = ThemedTk(theme='black', themebg=True)

# Create GUI labels and entry fields
label_plot_title = ttk.Label(root, text = 'Enter the title of the plot:')
label_plot_title.pack()
entry_plot_title = ttk.Entry(root)
entry_plot_title.pack()

label_x_title = ttk.Label(root, text = 'Enter the name of the vertical drug used:')
label_x_title.pack()
entry_x_title = ttk.Entry(root)
entry_x_title.pack()

label_y_doses = ttk.Label(root, text='Enter the vertical five doses (exclude zero), separated by tab:')
label_y_doses.pack()
entry_y_doses = ttk.Entry(root)
entry_y_doses.pack()

label_y_title = ttk.Label(root, text = 'Enter the name of the horizontal drug used:')
label_y_title.pack()
entry_y_title = ttk.Entry(root)
entry_y_title.pack()

label_x_doses = ttk.Label(root, text='Enter the horizontal nine doses (exclude zero), separated by tab:')
label_x_doses.pack()
entry_x_doses = ttk.Entry(root)
entry_x_doses.pack()

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

# Run CellProfiler from the command line
subprocess.run([cp_path, '-c', '-r', '-p', cppipe_path, '-i', image_dir, '-o', cp_output_dir])

# Define the path to the CellProfiler counting output
cp_csv = cp_output_dir / 'CellPyAbilityImage.csv'

# Load the CellProfiler counts into a DataFrame
df = pd.read_csv(cp_csv)

# Define wells
wells = [
    'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11',
    'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11',
    'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11',
    'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11',
    'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11',
    'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10', 'G11',
]

# Initialize lists for results
well_means = []
well_std = []

# Group rows and calculate statistics
for well in wells:
    # Find rows where 'File Name' contains the well name
    condition_rows = df[df['FileName_images'].str.contains(well, na=False)]
    
    # Extract Count_nuclei for these rows
    counts = condition_rows['Count_nuclei']
    
    # Calculate statistics
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
rows = [well[0] for well in wells]
columns = [well[1:] for well in wells]

# Map concentrations to rows and columns
row_conc = [row_concentrations[row] for row in rows]
col_conc = [column_concentrations[col] for col in columns]

# Normalize well means to vehicle (B2) mean
normalized_means = [mean / well_means[0] for mean in well_means]

# Frame that data
well_descriptions = {
    'Well': wells,
    'Mean': well_means,
    'Standard Deviation': well_std,
    'Normalized Mean': normalized_means,
    'Row Drug Concentration': row_conc,
    'Column Drug Concentration': col_conc
}
df2_results = pd.DataFrame(well_descriptions)

# Define file path for synergy_output subfolder
synergy_output_dir = base_dir / 'synergy_output'
synergy_output_dir.mkdir(exist_ok=True)

# Export as .csv
metrics_output_path = synergy_output_dir / f'{plot_title}_synergy_metrics.csv'
df2_results.to_csv(metrics_output_path, index=False)

# Read .csv with pandas
df2 = pd.read_csv(metrics_output_path)

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

# Create a pivot table for normalized means
normalized_means_pivot = df2.pivot(index='Column Drug Concentration', columns='Row Drug Concentration', values='Normalized Mean')

# Create a pivot table for Bliss independence
bliss_independence_pivot = bliss_df.pivot(index='Column Drug Concentration', columns='Row Drug Concentration', values='Bliss Independence')

# Convert pivot tables to numpy arrays
cell_survival = normalized_means_pivot.values
bliss_independence = bliss_independence_pivot.values

normalized_means_pivot.to_csv(synergy_output_dir / f'{plot_title}_synergy_ViabilityMatrix.csv')
bliss_independence_pivot.to_csv(synergy_output_dir / f'{plot_title}_synergy_BlissMatrix.csv')

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

# Rename CellProfiler output with experiment title and save in synergy_output
counts_csv = synergy_output_dir / f'{plot_title}_synergy_counts.csv'

try:
    os.rename(cp_csv, counts_csv)
    print(f'{cp_csv} succesfully renamed to {counts_csv}')
except FileNotFoundError:
    print(f'{cp_csv} not found')
except PermissionError:
    print(f'Permission denied. {cp_csv} may be open or in use.')
except Exception as e:
    print(f'While renaming {cp_csv}, an error occurred: {e}')

# Show the plot
fig.write_html(synergy_output_dir / f'{plot_title}_synergy_plot.html')
fig.show()