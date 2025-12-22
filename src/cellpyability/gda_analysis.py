"""
GDA analysis module receives user input from CLI, then runs statistical and graphical analysis
of the nuclei counts from CellProfiler.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import toolbox as tb

# Initialize toolbox
logger, base_dir = tb.logger, tb.base_dir


def run_gda(title_name, upper_name, lower_name, top_conc, dilution, image_dir, show_plot=True, counts_file=None, output_dir=None):
    """
    Run GDA (Growth Delay Assay) analysis for two cell lines (B-D, E-G) and one drug gradient (2-11).
    
    Parameters:
    -----------
    title_name : str
        Title of the experiment
    upper_name : str
        Name for upper cell condition (rows B-D)
    lower_name : str
        Name for lower cell condition (rows E-G)
    top_conc : float
        Top concentration in molar
    dilution : float
        Dilution factor between columns
    image_dir : str
        Directory containing the 60 well images
    show_plot : bool
        Whether to display the plot (default: True)
    counts_file : str, optional
        Path to pre-existing counts CSV file (for testing)
    output_dir : str, optional
        Custom output directory. If None, uses current working directory.
    """
    
    # Create a concentration range array
    doses = tb.gen_dose_range(top_conc, dilution, 9) # 9 because 9 doses, excluding vehicle (columns 3-11)
    
    # Run CellProfiler headless and return a DataFrame with the raw nuclei counts and the .csv path
    df_cp, cp_csv = tb.run_cellprofiler(image_dir, counts_file=counts_file, output_dir=output_dir)
    
    # Load the CellProfiler counts into a DataFrame
    df_cp.drop('ImageNumber', axis=1, inplace=True)
    df_cp.columns = ['nuclei', 'well']
    
    # Rename rows from the TIFF file names to the corresponding well names
    df_cp['well'] = df_cp['well'].apply(lambda x: tb.rename_wells(x))
    logger.debug('CellProfiler output rows renamed to well names.')
    
    # Extract row/column designators for pivoting
    df_cp[['Row','Column']] = df_cp['well'].str.extract(r'^([B-G])(\d+)$')
    logger.debug('Extracted Row and Column from well names.')
    
    # Pivot nuclei counts into a matrix for fast group stats
    count_matrix = df_cp.pivot(index='Row', columns='Column', values='nuclei')
    logger.debug('Pivoted df_cp into count_matrix.')
    
    # Define upper and lower rows
    upper_rows = ['B', 'C', 'D']
    lower_rows = ['E', 'F', 'G']
    
    # Compute mean nuclei per column for upper and lower groups
    upper_counts = count_matrix.loc[upper_rows]
    lower_counts = count_matrix.loc[lower_rows]
    
    upper_means = upper_counts.mean(axis=0)
    lower_means = lower_counts.mean(axis=0)
    
    # Normalize means to vehicle control (column '2')
    upper_vehicle = upper_means['2']
    lower_vehicle = lower_means['2']
    upper_normalized_means = (upper_means / upper_vehicle).loc[[str(i) for i in range(2,12)]].tolist()
    lower_normalized_means = (lower_means / lower_vehicle).loc[[str(i) for i in range(2,12)]].tolist()
    logger.debug('Upper and lower mean nuclei counts normalized to vehicle.')
    
    # Compute standard deviations of normalized counts per condition
    upper_sd = (upper_counts.div(upper_vehicle)).std(axis=0).loc[[str(i) for i in range(2,12)]].tolist()
    lower_sd = (lower_counts.div(lower_vehicle)).std(axis=0).loc[[str(i) for i in range(2,12)]].tolist()
    logger.debug('Computed standard deviations for normalized counts.')
    
    # Pair column number with drug dose
    column_labels = [str(i) for i in range(2,12)]
    
    all_doses = np.insert(doses, 0, 0) # add zero to start of NumPy array for vehicle
    column_concentrations = dict(zip(column_labels, all_doses))
    
    # Define file path to or create gda_output/ subfolder in output directory
    output_base = tb.get_output_base_dir(output_dir)
    gda_output_dir = output_base / 'gda_output'
    gda_output_dir.mkdir(exist_ok=True)
    logger.debug(f'gda_output/ directory created at {gda_output_dir}')
    
    # Consolidate analytics into a new .csv file
    df_stats = pd.DataFrame(columns=column_labels)
    df_stats.index.name = '96-Well Column'
    df_stats.loc['Drug Concentration'] = list(column_concentrations.values())
    df_stats.loc[f'Relative Cell Viability {upper_name}'] = upper_normalized_means
    df_stats.loc[f'Relative Cell Viability {lower_name}'] = lower_normalized_means
    df_stats.loc[f'Relative Standard Deviation {upper_name}'] = upper_sd
    df_stats.loc[f'Relative Standard Deviation {lower_name}'] = lower_sd
    df_stats.to_csv(gda_output_dir / f'{title_name}_gda_Stats.csv')
    logger.info(f'{title_name}_gda_Stats saved to {gda_output_dir}.')
    
    # Normalize nuclei counts for each well individually
    vehicle_map = {r: upper_vehicle for r in upper_rows}
    vehicle_map.update({r: lower_vehicle for r in lower_rows})
    df_cp['normalized_nuclei'] = df_cp['nuclei'] / df_cp['Row'].map(vehicle_map)
    logger.debug('Each well normalized to its condition vehicle (Vectorized).')
    
    # Create viability matrix via pivot on normalized values
    viability_matrix = df_cp.pivot(index='Row', columns='Column', values='normalized_nuclei')
    
    # Reindex to maintain plate order and replace column labels with doses
    viability_matrix = viability_matrix.reindex(index=upper_rows+lower_rows, columns=column_labels)
    viability_matrix.columns = [column_concentrations[col] for col in viability_matrix.columns]
    
    # Rename rows to replicates
    viability_matrix.index = [f'{upper_name} rep {i}' for i in [1,2,3]] + [f'{lower_name} rep {i}' for i in [1,2,3]]
    logger.debug('Created viability matrix via vectorized pivot.')
    
    # Save the viability matrix as a .csv
    viability_matrix.to_csv(gda_output_dir / f'{title_name}_gda_ViabilityMatrix.csv')
    logger.info(f'{title_name} viability matrix saved to {gda_output_dir}.')
    
    # Assign doses to the x-axis
    x = np.array(doses)
    
    # Assign average normalized nuclei counts to the y-axis for each condition
    # skip the vehicle at index 0
    y1 = np.array(upper_normalized_means[1:])
    y2 = np.array(lower_normalized_means[1:])
    logger.debug('Assigned doses and normalized means to x and y values via NumPy, respectively.')
    
    # Use curve_fit to fit the data for y1 and y2 (5PL with Hill Slope as backup)\
    # Solves algebraically for IC50 (if computable)
    x_plot_fit_y1, y_plot_fit_y1, IC50_val_y1 = tb.fit_response_curve(x, y1, upper_name)
    logger.debug('Upper condition curve fitting complete.')
    x_plot_fit_y2, y_plot_fit_y2, IC50_val_y2 = tb.fit_response_curve(x, y2, lower_name)
    logger.debug('Lower condition curve fitting complete.')
    
    # Calculate ratio (Handling potential NaNs safely)
    if np.isnan(IC50_val_y1) or np.isnan(IC50_val_y2):
        IC50_ratio = np.nan
    else:
        IC50_ratio = IC50_val_y1 / IC50_val_y2
        
    logger.info(f'{upper_name} IC50 / {lower_name} IC50 = {IC50_ratio}')
    
    # Plot the curves using the variables defined above
    plt.plot(x_plot_fit_y1, y_plot_fit_y1, 'b-')
    plt.plot(x_plot_fit_y2, y_plot_fit_y2, 'r-')
    logger.debug('Plotted data.')
    
    # Create scatter plot
    # Create basic structure
    plt.style.use('default')
    plt.xscale('log')
    plt.scatter(x, y1, color='blue', label=str(upper_name))
    plt.scatter(x, y2, color='red', label=str(lower_name))
    plt.errorbar(x, y1, yerr=upper_sd[1:], fmt='o', color='blue', capsize=3)
    plt.errorbar(x, y2, yerr=lower_sd[1:], fmt='o', color='red', capsize=3)
    
    # Annotate the plot
    plt.xlabel('Concentration (M)')
    plt.ylabel('Relative Cell Survival')
    plt.title(str(title_name))
    plt.text(0.05, 0.09, f'IC50 = {IC50_val_y1:.2e}',
        color='blue',
        fontsize=10,
        transform=plt.gca().transAxes
    )
    plt.text(
        0.05, 0.05, f'IC50 = {IC50_val_y2:.2e}',
        color='red',
        fontsize=10,
        transform=plt.gca().transAxes
    )
    plt.text(
        0.05, 0.01, f'IC50 ratio = {IC50_ratio:.1f}',
        color='black',
        fontsize=10,
        transform=plt.gca().transAxes
    )
    plt.legend()
    plt.savefig(gda_output_dir / f'{title_name}_gda_plot.png', dpi=200, bbox_inches='tight')
    logger.info(f'{title_name} GDA plot saved to {gda_output_dir}.')
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    # Rename the CellProfiler output using the provided title name
    counts_csv = gda_output_dir / f'{title_name}_gda_counts.csv'
    
    tb.rename_counts(cp_csv, counts_csv)
    logger.info(f'{title_name} raw counts saved to {gda_output_dir}.')
