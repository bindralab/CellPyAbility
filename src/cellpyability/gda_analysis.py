"""
GDA analysis module - refactored to separate analysis logic from GUI.
This can be called from either the CLI or the original GUI script.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.optimize import root as scipy_root

from . import toolbox as tb

# Initialize toolbox
logger, base_dir = tb.logger, tb.base_dir


def run_gda(title_name, upper_name, lower_name, top_conc, dilution, image_dir, show_plot=True, counts_file=None):
    """
    Run GDA (Growth Delay Assay) analysis.
    
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
    """
    
    # Create a concentration range array
    doses = tb.dose_range_x(top_conc, dilution)
    
    # Run CellProfiler headless and return a DataFrame with the raw nuclei counts and the .csv path
    df_cp, cp_csv = tb.run_cellprofiler(image_dir, counts_file=counts_file)
    
    # Load the CellProfiler counts into a DataFrame
    df_cp.drop('ImageNumber', axis=1, inplace=True)
    df_cp.columns = ['nuclei', 'well']
    
    # Rename rows from the TIFF file names to the corresponding well names
    df_cp['well'] = df_cp['well'].apply(lambda x: tb.rename_wells(x, tb.wells))
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
    column_concentrations = dict(zip(column_labels, [0] + doses))
    
    # Define file path to or create CellPyAbility/GDA_output/ subfolder
    gda_output_dir = base_dir / 'GDA_output'
    gda_output_dir.mkdir(exist_ok=True)
    logger.debug('CellPyAbility/GDA_output/ identified or created and identified.')
    
    # Consolidate analytics into a new .csv file
    df_stats = pd.DataFrame(columns=column_labels)
    df_stats.index.name = '96-Well Column'
    df_stats.loc['Drug Concentration'] = list(column_concentrations.values())
    df_stats.loc[f'Relative Cell Viability {upper_name}'] = upper_normalized_means
    df_stats.loc[f'Relative Cell Viability {lower_name}'] = lower_normalized_means
    df_stats.loc[f'Relative Standard Deviation {upper_name}'] = upper_sd
    df_stats.loc[f'Relative Standard Deviation {lower_name}'] = lower_sd
    df_stats.to_csv(gda_output_dir / f'{title_name}_GDA_Stats.csv')
    logger.info(f'{title_name}_GDA_Stats saved to GDA_output.')
    
    # Normalize nuclei counts for each well individually
    def normalize_row(row):
        return (row['nuclei'] / upper_vehicle) if row['Row'] in upper_rows else (row['nuclei'] / lower_vehicle)
    
    df_cp['normalized_nuclei'] = df_cp.apply(normalize_row, axis=1)
    logger.debug('Each well normalized to its condition vehicle.')
    
    # Create viability matrix via pivot on normalized values
    viability_matrix = df_cp.pivot(index='Row', columns='Column', values='normalized_nuclei')
    
    # Reindex to maintain plate order and replace column labels with doses
    viability_matrix = viability_matrix.reindex(index=upper_rows+lower_rows, columns=column_labels)
    viability_matrix.columns = [column_concentrations[col] for col in viability_matrix.columns]
    
    # Rename rows to replicates
    viability_matrix.index = [f'{upper_name} rep {i}' for i in [1,2,3]] + [f'{lower_name} rep {i}' for i in [1,2,3]]
    logger.debug('Created viability matrix via vectorized pivot.')
    
    # Save the viability matrix as a .csv
    viability_matrix.to_csv(gda_output_dir / f'{title_name}_GDA_ViabilityMatrix.csv')
    logger.info(f'{title_name} viability matrix saved to GDA_output.')
    
    # Assign doses to the x-axis
    x = np.array(doses)
    
    # Assign average normalized nuclei counts to the y-axis for each condition
    # skip the vehicle at index 0
    y1 = np.array(upper_normalized_means[1:])
    y2 = np.array(lower_normalized_means[1:])
    logger.debug('Assigned doses and normalized means to x and y values via NumPy, respectively.')
    
    # Define non-linear regression for the xy-plot and estimate IC50s
    # Define the 5PL function
    def fivePL(x, A, B, C, D, G):  # (x = doses, A = max y, B = Hill slope, C = inflection, D = min y, G = asymetry):
        return ((A - D) / (1.0 + (x / C) ** B) ** G) + D
    
    # Define the Hill function as a fallback (if 5PL doesn't fit)
    def hill(x, Emax, EC50, HillSlope):
        return Emax * (x**HillSlope) / (EC50**HillSlope + x**HillSlope)
    
    # Initial guesses for parameters
    params_init_5PL_y1 = [y1[np.argmax(y1)], 1, x[np.abs(y1 - 0.5).argmin()], y1[np.argmin(y1)], 1]  # [A, B, C, D, G]
    params_init_5PL_y2 = [y2[np.argmax(y2)], 1, x[np.abs(y2 - 0.5).argmin()], y2[np.argmin(y2)], 1]  # [A, B, C, D, G]
    
    # Generate x values for the fitted curves
    x_plot = np.linspace(min(x), max(x), 1000)
    logger.debug('Generating a linear space containing highest and lowest doses via NumPy.')
    
    # Use curve_fit to fit the data for y1 and y2
    # Identify initial maxfev along with higher maxfev in case optimal parameters not found
    maxfev_initial = int(500)
    maxfev_retry = int(5000)
    
    # Fit the upper data with a 5PL of increasing maxfev, else return that 5PL does not fit
    try:
        popt_5PL_y1, pcov_5PL_y1 = curve_fit(
            fivePL, x, y1,
            p0=params_init_5PL_y1,
            maxfev=maxfev_initial
        )
        logger.debug(f'Fitting a 5-parameter logistic to {upper_name} with maxfev={maxfev_initial}.')
    
        x_plot_5PL_y1 = x_plot
        y_plot_5PL_y1 = fivePL(x_plot, *popt_5PL_y1)
        logger.debug(f'Made 5PL curve for {upper_name}.')
    
        def root_func_y1(xx): return fivePL(xx, *popt_5PL_y1) - 0.5
        initial_guess_y1 = x[np.abs(y1 - 0.5).argmin()]
        IC50_y1 = scipy_root(root_func_y1, initial_guess_y1)
        IC50_value_y1 = IC50_y1.x[0]
        logger.info(f'5PL IC50 for {upper_name}: {IC50_value_y1}.')
    except RuntimeError:
        try:
            logger.debug(f'RuntimeError with maxfev={maxfev_initial} for {upper_name}. Retrying with maxfev={maxfev_retry}…')
            popt_5PL_y1, pcov_5PL_y1 = curve_fit(
                fivePL, x, y1,
                p0=params_init_5PL_y1,
                maxfev=maxfev_retry
            )
    
            x_plot_5PL_y1 = x_plot
            y_plot_5PL_y1 = fivePL(x_plot, *popt_5PL_y1)
            logger.debug(f'Made 5PL curve for {upper_name}.')
    
            def root_func_y1(xx): return fivePL(xx, *popt_5PL_y1) - 0.5
            initial_guess_y1 = x[np.abs(y1 - 0.5).argmin()]
            IC50_y1 = scipy_root(root_func_y1, initial_guess_y1)
            IC50_value_y1 = IC50_y1.x[0]
            logger.info(f'5PL IC50 for {upper_name}: {IC50_value_y1}.')
        except RuntimeError:
            logger.warning(f'RuntimeError with maxfev={maxfev_retry} for {upper_name}. 5PL does not fit these data. Falling back to Hill.')
            # Initialize Hill function
            Emax_init       = y1.max()
            EC50_init       = x[np.abs(y1 - 0.5).argmin()]
            HillSlope_init  = 1
            popt_hill_y1, pcov_hill_y1 = curve_fit(
                hill, x, y1,
                p0=[Emax_init, EC50_init, HillSlope_init],
                maxfev=10000
            )
            # Set up the Hill curve
            y_plot_5PL_y1 = hill(x_plot, *popt_hill_y1)
            x_plot_5PL_y1 = x_plot
            logger.debug(f'Made Hill curve for {upper_name}.')
    
            # IC50 via root‐finding on the Hill model
            def root_hill_y1(xx): return hill(xx, *popt_hill_y1) - 0.5
            IC50_hill_y1 = scipy_root(root_hill_y1, EC50_init)
            IC50_value_y1 = IC50_hill_y1.x[0]
            logger.info(f'Hill IC50 for {upper_name}: {IC50_value_y1}.')
    
    # Repeat for lower data
    try:
        popt_5PL_y2, pcov_5PL_y2 = curve_fit(
            fivePL, x, y2,
            p0=params_init_5PL_y2,
            maxfev=maxfev_initial
        )
        logger.debug(f'Fitting a 5-parameter logistic to {lower_name} with maxfev={maxfev_initial}.')
    
        popt_5PL_y2, pcov_5PL_y2 = curve_fit(
            fivePL, x, y2,
            p0=params_init_5PL_y2,
            maxfev=maxfev_retry
        )
        x_plot_5PL_y2 = x_plot
        y_plot_5PL_y2 = fivePL(x_plot, *popt_5PL_y2)
        logger.debug(f'Made 5PL curve for {lower_name}.')
        def root_func_y2(xx): return fivePL(xx, *popt_5PL_y2) - 0.5
        initial_guess_y2 = x[np.abs(y2 - 0.5).argmin()]
        IC50_y2 = scipy_root(root_func_y2, initial_guess_y2)
        IC50_value_y2 = IC50_y2.x[0]
        logger.info(f'5PL IC50 for {lower_name}: {IC50_value_y2}.')
    except RuntimeError:
        try:
            logger.debug(f'RuntimeError with maxfev={maxfev_initial} for {lower_name}. Retrying with maxfev={maxfev_retry}…')
            popt_5PL_y2, pcov_5PL_y2 = curve_fit(
                fivePL, x, y2,
                p0=params_init_5PL_y2,
                maxfev=maxfev_retry
            )
    
            x_plot_5PL_y2 = x_plot
            y_plot_5PL_y2 = fivePL(x_plot, *popt_5PL_y2)
            logger.debug(f'Made 5PL curve for {lower_name}.')
    
            def root_func_y2(xx): return fivePL(xx, *popt_5PL_y2) - 0.5
            initial_guess_y2 = x[np.abs(y2 - 0.5).argmin()]
            IC50_y2 = scipy_root(root_func_y2, initial_guess_y2)
            IC50_value_y2 = IC50_y2.x[0]
            logger.info(f'5PL IC50 for {lower_name}: {IC50_value_y2}.')
    
        except RuntimeError:
            logger.warning(f'RuntimeError with maxfev={maxfev_retry} for {lower_name}. 5PL does not fit these data. Falling back to Hill.')
            # Initialize Hill function
            Emax_init       = y2.max()
            EC50_init       = x[np.abs(y2 - 0.5).argmin()]
            HillSlope_init  = 1
            popt_hill_y2, pcov_hill_y2 = curve_fit(
                hill, x, y2,
                p0=[Emax_init, EC50_init, HillSlope_init],
                maxfev=10000
            )
            # Set up the Hill curve
            y_plot_5PL_y2 = hill(x_plot, *popt_hill_y2)
            x_plot_5PL_y2 = x_plot
            logger.debug(f'Made Hill curve for {lower_name}.')
    
            # IC50 via root‐finding on the Hill model
            def root_hill_y2(xx): return hill(xx, *popt_hill_y2) - 0.5
            IC50_hill_y2 = scipy_root(root_hill_y2, EC50_init)
            IC50_value_y2 = IC50_hill_y2.x[0]
            logger.info(f'Hill IC50 for {lower_name}: {IC50_value_y2}.')
    
    # Find the IC50 ratio of the upper condition / lower condition (may be irrelevant depending on purpose of experiment)
    IC50_ratio = IC50_value_y1 / IC50_value_y2
    logger.info(f'{upper_name} IC50 / {lower_name} IC50 = {IC50_ratio}')
    
    # Plot the curves if 5PL fit, otherwise connecting points by line
    plt.plot(x_plot_5PL_y1, y_plot_5PL_y1, 'b-')
    plt.plot(x_plot_5PL_y2, y_plot_5PL_y2, 'r-')
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
    plt.text(0.05, 0.09, f'IC50 = {IC50_value_y1:.2e}',
        color='blue',
        fontsize=10,
        transform=plt.gca().transAxes
    )
    plt.text(
        0.05, 0.05, f'IC50 = {IC50_value_y2:.2e}',
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
    plt.savefig(gda_output_dir / f'{title_name}_GDA_plot.png', dpi=200, bbox_inches='tight')
    logger.info(f'{title_name} GDA plot saved to CellPyAbility/GDA_output/.')
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    # Rename the CellProfiler output using the provided title name
    counts_csv = gda_output_dir / f'{title_name}_GDA_counts.csv'
    
    tb.rename_counts(cp_csv, counts_csv)
    logger.info(f'{title_name} raw counts saved to GDA_output.')
