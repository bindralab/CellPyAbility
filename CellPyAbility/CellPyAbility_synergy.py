"""
CellPyAbility_synergy.py is intended for dose combination analysis of 59 combinations and one vehicle.
This script should remain in the same directory as the other CellPyAbility scripts.
For more information, please see the README at https://github.com/bindralab/CellPyAbility.
"""

from tkinter import ttk, filedialog
from ttkthemes import ThemedTk

import CellPyAbility_toolbox as tb
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Initialize toolbox
logger, base_dir = tb.logger, tb.base_dir

# Establish the GUI for experiment info
def synergy_gui():
    image_dir = ''
    def select_image_dir():
        nonlocal image_dir
        image_dir = filedialog.askdirectory()

    # Create main window
    root = ThemedTk(theme='black', themebg=True)

    # Create entry fields for inputs
    entries = {}
    fields = [
        ('title_name', 'Enter the title of the experiment:'),
        ('x_drug', 'Enter the drug name for the horizontal gradient:'),
        ('x_top_conc', 'Enter the horizontal top concentration (M):'),
        ('x_dilution', 'Enter the horizontal dilution factor (x-fold):'),
        ('y_drug', 'Enter the drug name for the vertical gradient:'),
        ('y_top_conc', 'Enter the vertical top concentration (M):'),
        ('y_dilution', 'Enter the vertical dilution factor (x-fold):'),
    ]
    for key, text in fields:
        ttk.Label(root, text=text).pack()
        entry = ttk.Entry(root)
        entry.pack()
        entries[key] = entry

    # Adds button for image directory file select
    image_dir_button = ttk.Button(root, text='Select Image Directory', command=select_image_dir)
    image_dir_button.pack()
    
    # This dictionary will hold the result
    gui_inputs = {}
    
    # Callback function to use when the form is submitted
    def submit():
        for key, entry in entries.items():
            gui_inputs[key] = entry.get()
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

# Load the CellProfiler counts into a DataFrame and rename wells
df_cp.drop('ImageNumber', axis=1, inplace=True)
df_cp.columns = ['nuclei', 'well']
# Map TIFF file names to well IDs
df_cp['well'] = df_cp['well'].apply(lambda x: tb.rename_wells(x, tb.wells))
logger.debug('CellProfiler output rows renamed to well names.')

# Extract row/column for each well for vectorized grouping
df_cp[['Row','Column']] = df_cp['well'].str.extract(r'^([B-G])(\d+)$')
logger.debug('Row and column labels extracted from well names.')

# Group triplicates and calculate statistics
stats = (
    df_cp
    .groupby('well')['nuclei']
    .agg(mean='mean', std='std')
    .reindex(tb.wells)
)
well_means = stats['mean'].tolist()
well_std = stats['std'].tolist()
logger.debug('Nuclei mean and standard deviation calculated.')

# Map concentrations
tb_wells = [str(i) for i in range(2,12)]
column_concentrations = dict(zip(
    tb_wells,
    [0] + x_doses
))
row_concentrations = dict(zip(
    ['B','C','D','E','F','G'],
    [0] + y_doses
))

# Map concentrations to rows and columns
rows = stats.index.str[0].tolist()
columns = stats.index.str[1:].tolist()
row_conc = [row_concentrations[r] for r in rows]
col_conc = [column_concentrations[c] for c in columns]
logger.debug('Row and column concentrations mapped.')

# Normalize well means to vehicle (B2) mean
vehicle = well_means[0]
normalized_means = [(m/vehicle) for m in well_means]
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
for _, row in df_stats.iterrows():
    well_name = row['Well']
    observed_combined_effect = row['Normalized Mean']
    logger.debug('Normalized means pulled from df_stats.')
    
    # Determine the x-alone and y-alone effects based on the well name
    if well_name[0] in 'BCDEFG' and well_name[1:] in '234567891011':
        x_effect = df_stats.loc[df_stats['Well']=='B'+well_name[1:], 'Normalized Mean'].iloc[0]
        y_effect = df_stats.loc[df_stats['Well']==well_name[0]+'2', 'Normalized Mean'].iloc[0]
        logger.debug('x_effect and y_effect identified.')

        # Calculate the expected combined effect
        expected_combined_effect = x_effect * y_effect
        logger.debug('Expected combined effects calculated.')

        # Calculate the Bliss independence
        bliss_independence = expected_combined_effect - observed_combined_effect
        logger.debug('Bliss independence scores calculated.')

        bliss_results.append({
            'Well': well_name,
            'Expected Combined Effect': expected_combined_effect,
            'Observed Combined Effect': observed_combined_effect,
            'Bliss Independence': bliss_independence
        })

# Convert the results to a DataFrame
df_bliss = pd.DataFrame(bliss_results)

# Add 'Row Drug Concentration' and 'Column Drug Concentration' to df_bliss
df_bliss['Row Drug Concentration'] = df_bliss['Well'].str[0].map(row_concentrations)
df_bliss['Column Drug Concentration'] = df_bliss['Well'].str[1:].map(column_concentrations)

# Create pivot tables for plotting and saving
normalized_means_pivot = df_stats.pivot(
    index='Row Drug Concentration', columns='Column Drug Concentration', values='Normalized Mean'
)
bliss_independence_pivot = df_bliss.pivot(
    index='Row Drug Concentration', columns='Column Drug Concentration', values='Bliss Independence'
)

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
min_x_value = x_values[x_values>0].min()
min_y_value = y_values[y_values>0].min()

x_values = np.where(x_values==0, min_x_value/(x_values[3]/x_values[2]), x_values)
y_values = np.where(y_values==0, min_y_value/(y_values[3]/y_values[2]), y_values)

x_tickvals = np.unique(np.concatenate(([min_x_value/(x_values[3]/x_values[2])], x_values)))
y_tickvals = np.unique(np.concatenate(([min_y_value/(y_values[3]/y_values[2])], y_values)))

x_ticktext = ['0'] + [f'{val:.1e}' for val in x_tickvals[1:]]
y_ticktext = ['0'] + [f'{val:.1e}' for val in y_tickvals[1:]]
logger.debug('Replaced zero with non-zero values a fixed log distance from the minimum concentrations.')

# Create the 3D surface plot
fig = go.Figure(data=[go.Surface(z=cell_survival, x=x_values, y=y_values, surfacecolor=bliss_independence, colorscale='jet_r', cmin=-0.3, cmax=0.3, colorbar=dict(title='Bliss Independence'))])
logger.debug('3D surface plot created.')

# Update layout to set x and y axes to logarithmic scale
fig.update_layout(title=str(title_name), scene=dict(xaxis=dict(title=x_drug, type='log', ticktext=x_ticktext, tickvals=x_tickvals), yaxis=dict(title=y_drug, type='log', ticktext=y_ticktext, tickvals=y_tickvals), zaxis=dict(title='Relative Cell Survival', range=[0,np.max(cell_survival)])))
logger.debug('x and y axes changed to log, experiment details added as labels.')

# Rename CellProfiler output with experiment title and save in synergy_output
counts_csv = synergy_output_dir / f'{title_name}_synergy_counts.csv'

tb.rename_counts(cp_csv, counts_csv)
logger.info(f'{title_name} raw counts saved to synergy_output.')

# Save the interactable plot as an HTML
fig.write_html(synergy_output_dir / f'{title_name}_synergy_plot.html')
logger.info(f'{title_name} synergy plot saved to synergy_output.')

fig.show()