import logging
import os
import subprocess
from pathlib import Path
from tkinter import ttk, messagebox, filedialog
from ttkthemes import ThemedTk

import CellPyAbility_toolbox as tb
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Initialize toolbox
logger, base_dir, cp_path = tb.logger, tb.base_dir, tb.cp_path

# Establish the GUI for experiment info
def synergy_gui():
    image_dir = ''
    def select_image_dir():
        nonlocal image_dir
        image_dir = filedialog.askdirectory()

    # Create main window
    root = ThemedTk(theme='black', themebg=True)

    # Create entry fields for inputs
    label1 = ttk.Label(root, text='Enter the title of the experiment:')
    label1.pack()
    entry1 = ttk.Entry(root)
    entry1.pack()
    label2 = ttk.Label(root, text='Enter the drug name for the horizontal gradient:')
    label2.pack()
    entry2 = ttk.Entry(root)
    entry2.pack()
    label3 = ttk.Label(root, text='Enter the horizontal top concentration (M):')
    label3.pack()
    entry3 = ttk.Entry(root)
    entry3.pack()
    label4 = ttk.Label(root, text='Enter the horizontal dilution factor (x-fold):')
    label4.pack()
    entry4 = ttk.Entry(root)
    entry4.pack()
    label5 = ttk.Label(root, text='Enter the drug name for the vertical gradient:')
    label5.pack()
    entry5 = ttk.Entry(root)
    entry5.pack()
    label6 = ttk.Label(root, text='Enter the vertical top concentration (M):')
    label6.pack()
    entry6 = ttk.Entry(root)
    entry6.pack()
    label7 = ttk.Label(root, text='Enter the vertical dilution factor (x-fold):')
    label7.pack()
    entry7 = ttk.Entry(root)
    entry7.pack()

    # Adds button for image directory file select
    image_dir_button = ttk.Button(root, text='Select Image Directory', command=select_image_dir)
    image_dir_button.pack()
    
    # This dictionary will hold the result
    gui_inputs = {}
    
    # Callback function to use when the form is submitted
    def submit():
        gui_inputs['title_name'] = entry1.get()
        gui_inputs['x_drug'] = entry2.get()
        gui_inputs['x_top_conc'] = entry3.get()
        gui_inputs['x_dilution'] = entry4.get()
        gui_inputs['y_drug'] = entry5.get()
        gui_inputs['y_top_conc'] = entry6.get()
        gui_inputs['y_dilution'] = entry7.get()
        gui_inputs['image_dir'] = image_dir
        root.destroy()
    
    # Create button to submit form
    submit_button = ttk.Button(root, text='Submit', command=submit)
    submit_button.pack()
    
    root.mainloop()
    logger.debug('GUI submitted.')
    return gui_inputs 

# Assign the synergy_gui output to script variable
gui_inputs = synergy_gui()

# Assign GUI inputs to script variables
title_name = gui_inputs['title_name']
x_drug = gui_inputs['x_drug']
x_top_conc = float(gui_inputs['x_top_conc'])
x_dilution = float(gui_inputs['x_dilution'])
y_drug = gui_inputs['y_drug']
y_top_conc = float(gui_inputs['y_top_conc'])
y_dilution = float(gui_inputs['y_dilution'])
image_dir = gui_inputs.get('image_dir')
logger.debug('GUI inputs assigned to variables.')

# Calculate x and y concentration gradients
x_doses = tb.dose_range_x(x_top_conc, x_dilution)
logger.debug('x_doses gradient calculated.')
y_doses = tb.dose_range_y(y_top_conc, y_dilution)
logger.debug('y_doses gradient calculated.')

# Run CellProfiler headless and return a DataFrame with the raw nuclei counts and the .csv path
df_cp, cp_csv = tb.run_cellprofiler(image_dir)

# Load the CellProfiler counts into a DataFrame
df_cp.drop('ImageNumber', axis=1, inplace=True)
df_cp.columns = ['nuclei', 'well']

# Initialize lists for results
well_means = []
well_std = []

# Group triplicates and calculate statistics
for well in tb.wells:
    # Find rows where 'File Name' contains the well name
    condition_rows = df_cp[df_cp['well'].str.contains(well, na=False)]
    
    # Extract Count_nuclei for these rows
    counts = condition_rows['nuclei']
    
    # Calculate statistics
    well_means.append(counts.mean())
    well_std.append(counts.std())
    logger.debug('Nuclei mean and standard deviation calculated.')

column_concentrations = {
    '2': 0, # vehicle
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

row_concentrations = {
    'B': 0, # vehicle
    'C': y_doses[0],
    'D': y_doses[1],
    'E': y_doses[2],
    'F': y_doses[3],
    'G': y_doses[4]
}

# Extract row and column labels from well names
rows = [well[0] for well in tb.wells]
columns = [well[1:] for well in tb.wells]
logger.debug('Row and column labels extracted from well names.')

# Map concentrations to rows and columns
row_conc = [row_concentrations[row] for row in rows]
col_conc = [column_concentrations[col] for col in columns]
logger.debug('Row and column concentrations mapped.')

# Normalize well means to vehicle (B2) mean
normalized_means = [mean / well_means[0] for mean in well_means]
logger.debug('Mean nuclei count normalized to vehicle control.')

# Frame that data
well_descriptions = {
    'Well': tb.wells,
    'Mean': well_means,
    'Standard Deviation': well_std,
    'Normalized Mean': normalized_means,
    'Row Drug Concentration': row_conc,
    'Column Drug Concentration': col_conc
}
df_stats = pd.DataFrame(well_descriptions)

# Define file path for synergy_output subfolder
synergy_output_dir = base_dir / 'synergy_output'
synergy_output_dir.mkdir(exist_ok=True)
logger.debug('CellPyAbility/synergy_output/ identified or created and identified.')

# Save the experiment viability statistics as a .csv
df_stats.to_csv(synergy_output_dir / f'{title_name}_synergy_stats.csv', index=False)
logger.info(f'{title_name} synergy stats saved to synergy_output')

# Initialize a list to store Bliss independence results
bliss_results = []

# Pull viability values from df_stats to calculate Bliss Independence
for index, row in df_stats.iterrows():
    well_name = row['Well']
    observed_combined_effect = row['Normalized Mean']
    logger.debug('Normalized means pulled from df_stats.')
    
    # Determine the x-alone and y-alone effects based on the well name
    if well_name[0] in 'BCDEFG' and well_name[1:] in '234567891011':
        x_effect = df_stats[df_stats['Well'] == 'B' + well_name[1:]]['Normalized Mean'].values[0]
        y_effect = df_stats[df_stats['Well'] == well_name[0] + '2']['Normalized Mean'].values[0]
        logger.debug('x_effect (row B normalized means) and y_effect (column 2 normalized means) identified.')

        # Calculate the expected combined effect
        expected_combined_effect = x_effect * y_effect
        logger.debug('Expected combined effects (x_effect * y_effect) calculated.')

        # Calculate the Bliss independence
        bliss_independence = expected_combined_effect - observed_combined_effect
        logger.debug('Bliss independence scores calculated.')

        # Store the result
        bliss_results.append({
            'Well': well_name,
            'Expected Combined Effect': expected_combined_effect,
            'Observed Combined Effect': observed_combined_effect,
            'Bliss Independence': bliss_independence
        })
        logger.info(f'Highest Bliss score in these data: {max(bliss_independence)}.')

# Convert the results to a DataFrame
df_bliss = pd.DataFrame(bliss_results)

# Add 'Row Drug Concentration' and 'Column Drug Concentration' to df_bliss
df_bliss['Row Drug Concentration'] = df_bliss['Well'].apply(lambda x: row_concentrations[x[0]])
df_bliss['Column Drug Concentration'] = df_bliss['Well'].apply(lambda x: column_concentrations[x[1:]])

# Create a pivot table for normalized means
normalized_means_pivot = df_stats.pivot(index='Column Drug Concentration', columns='Row Drug Concentration', values='Normalized Mean')

# Create a pivot table for Bliss independence
bliss_independence_pivot = df_bliss.pivot(index='Column Drug Concentration', columns='Row Drug Concentration', values='Bliss Independence')

# Convert pivot tables to numpy arrays
cell_survival = normalized_means_pivot.values
bliss_independence = bliss_independence_pivot.values

# Save viability and Bliss matrices as .csv files
normalized_means_pivot.to_csv(synergy_output_dir / f'{title_name}_synergy_ViabilityMatrix.csv')
logger.info(f'{title_name} viability matrix saved to synergy_output.')

bliss_independence_pivot.to_csv(synergy_output_dir / f'{title_name}_synergy_BlissMatrix.csv')
logger.info(f'{title_name} Bliss score matrix saved to synergy_output.')

# Extract x and y values from the pivot tables
x_values = normalized_means_pivot.columns.values
y_values = normalized_means_pivot.index.values

# Replace zero values in x_values and y_values with a small positive number of fixed logarithmic distance
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
    title=str(title_name),
    scene=dict(
        xaxis=dict(
            title=x_drug,
            type='log',
            ticktext=x_ticktext,
            tickvals=x_tickvals
        ),
        yaxis=dict(
            title=y_drug,
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
counts_csv = synergy_output_dir / f'{title_name}_synergy_counts.csv'

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
fig.write_html(synergy_output_dir / f'{title_name}_synergy_plot.html')
fig.show()