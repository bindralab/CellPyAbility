"""
Synergy analysis module for dose response analysis of one cell line and two drugs.
Calculates relative viability matrices and surface map with Bliss independence as heat.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from . import toolbox as tb

# Initialize toolbox
logger, base_dir = tb.logger, tb.base_dir


def run_synergy(title_name, x_drug, x_top_conc, x_dilution, y_drug, y_top_conc, y_dilution, image_dir, show_plot=True, counts_file=None, output_dir=None):
    """
    Run synergy analysis for drug combination experiments.
    
    Parameters:
    -----------
    title_name : str
        Title of the experiment
    x_drug : str
        Drug name for horizontal gradient (Columns)
    x_top_conc : float
        Horizontal top concentration in molar
    x_dilution : float
        Horizontal dilution factor
    y_drug : str
        Drug name for vertical gradient (Rows)
    y_top_conc : float
        Vertical top concentration in molar
    y_dilution : float
        Vertical dilution factor
    image_dir : str
        Directory containing the 60 well images
    show_plot : bool
        Whether to display the plot (default: True)
    counts_file : str, optional
        Path to pre-existing counts CSV file (for testing)
    output_dir : str, optional
        Custom output directory. If None, uses current working directory.
    """
    
    # Calculate concentration gradients (NumPy arrays)
    x_doses = tb.gen_dose_range(x_top_conc, x_dilution, 9) # 9 doses without vehicle (cols 3-11)
    y_doses = tb.gen_dose_range(y_top_conc, y_dilution, 5) # 5 doses without vehicle (rows C-G)
    
    # Run CellProfiler
    df_cp, cp_csv = tb.run_cellprofiler(image_dir, counts_file=counts_file, output_dir=output_dir)
    
    # Clean CellProfiler output and map it to our 96-well plate
    df_cp.drop(columns='ImageNumber', inplace=True)
    df_cp.columns = ['nuclei', 'well']
    df_cp['well'] = df_cp['well'].apply(lambda x: tb.rename_wells(x))
    
    # Extract rows and columns
    df_cp[['Row','Column']] = df_cp['well'].str.extract(r'^([B-G])(\d+)$')
    
    # Create viability matrix so each cell in the 2D array represents a well
    # Pivot all replicates into a wide format (rows B-G x cols 2-11)
    # We take the mean of technical replicates automatically via pivot_table
    viability_matrix_raw = df_cp.pivot_table(index='Row', columns='Column', values='nuclei', aggfunc='mean')
    
    # Ensure standard sorting (rows B-G, cols 2-11 as strings)
    row_order = ['B','C','D','E','F','G']
    col_order = [str(i) for i in range(2,12)]
    viability_matrix_raw = viability_matrix_raw.reindex(index=row_order, columns=col_order)
    
    # Normalize entire matrix to the vehicle (B2)
    vehicle_val = viability_matrix_raw.loc['B', '2']
    viability_matrix = viability_matrix_raw / vehicle_val
    logger.debug('Viability matrix calculated and normalized to B2.')
    
    # Map concentrations to cols and rows (for labels)
    all_x_doses = np.insert(x_doses, 0, 0) # Add 0 for vehicle
    all_y_doses = np.insert(y_doses, 0, 0) # Add 0 for vehicle
    
    # Map index/columns to concentrations
    conc_map_x = dict(zip(col_order, all_x_doses))
    conc_map_y = dict(zip(row_order, all_y_doses))
    
    # Create detailed statistics DataFrame for CSV export
    # We use groupby to get mean and std for every well, identifying replicates by 'well' name
    df_stats = df_cp.groupby('well')['nuclei'].agg(['mean', 'std']).reset_index()
    df_stats['normalized_mean'] = df_stats['mean'] / vehicle_val
    
    # Map concentrations to the stats dataframe
    df_stats['Row Drug Concentration'] = df_stats['well'].str[0].map(conc_map_y)
    df_stats['Column Drug Concentration'] = df_stats['well'].str[1:].map(conc_map_x)
    
    # Rename columns for final output
    df_stats = df_stats.rename(columns={
        'well': 'Well', 
        'mean': 'Mean', 
        'std': 'Standard Deviation',
        'normalized_mean': 'Normalized Mean'
    })
    
    # Bliss Independence calculation
    # Row B represents "Drug X Alone" (since Drug Y is 0 in row B)
    drug_x_alone = viability_matrix.loc['B'].values # Shape (10,)
    
    # Column 2 represents "Drug Y Alone" (since Drug X is 0 in col 2)
    drug_y_alone = viability_matrix['2'].values     # Shape (6,)
    
    # Calculate expected independent effect by taking outer product
    # If P(A) is prob survival with drug A, and P(B) is prob survival with drug B
    # Expected survival = P(A) * P(B)
    expected_matrix = pd.DataFrame(
        np.outer(drug_y_alone, drug_x_alone),
        index=viability_matrix.index,
        columns=viability_matrix.columns
    )
    
    # Bliss = Expected Survival - Observed Survival
    # Positive Bliss score = Synergy (more killing than independence expects)
    bliss_matrix = expected_matrix - viability_matrix
    logger.debug('Bliss scores calculated via vectorized outer product.')

    # Setup output directories
    output_base = tb.get_output_base_dir(output_dir)
    synergy_output_dir = output_base / 'synergy_output'
    synergy_output_dir.mkdir(exist_ok=True)
    
    # --- INSERTED STATS SAVE START ---
    # Save the detailed stats file
    stats_cols = ['Well', 'Mean', 'Standard Deviation', 'Normalized Mean', 'Row Drug Concentration', 'Column Drug Concentration']
    df_stats[stats_cols].to_csv(synergy_output_dir / f'{title_name}_synergy_stats.csv', index=False)
    logger.info(f'{title_name} synergy stats saved to {synergy_output_dir}')
    # --- INSERTED STATS SAVE END ---
    
    # Save the matrices with experiment labels
    viability_out = viability_matrix.copy()
    viability_out.index = viability_out.index.map(conc_map_y)
    viability_out.columns = viability_out.columns.map(conc_map_x)
    viability_out.index.name = f'{y_drug} (M)'
    viability_out.columns.name = f'{x_drug} (M)'
    
    bliss_out = bliss_matrix.copy()
    bliss_out.index = viability_out.index
    bliss_out.columns = viability_out.columns
    
    viability_out.to_csv(synergy_output_dir / f'{title_name}_synergy_ViabilityMatrix.csv')
    bliss_out.to_csv(synergy_output_dir / f'{title_name}_synergy_BlissMatrix.csv')
    logger.info(f'{title_name} matrices saved.')

    # Prepare data for plotting
    # Convert dataframe to NumPy for Plotly
    z_viability = viability_matrix.values
    z_bliss = bliss_matrix.values
    
    x_vals = all_x_doses
    y_vals = all_y_doses
    
    # Calculate (min / dilution) for x and y since we cannot plot 0 on log scale
    # This places the vehicle "one step down" on the log axis
    x_min_nonzero = np.min(x_vals[x_vals > 0])
    y_min_nonzero = np.min(y_vals[y_vals > 0])

    # Take the bigger of the two dilution factors to unify visual zero    
    visual_dilution = max(x_dilution, y_dilution) 
    
    # Apply this shared factor to calculate the artificial zero location
    x_vals_plot = np.where(x_vals == 0, x_min_nonzero / visual_dilution, x_vals)
    y_vals_plot = np.where(y_vals == 0, y_min_nonzero / visual_dilution, y_vals)
    
    # Format tick text
    x_ticktext = ['0'] + [f'{val:.1e}' for val in x_vals[1:]]
    y_ticktext = ['0'] + [f'{val:.1e}' for val in y_vals[1:]]

    # Create 3D surface plot
    fig = go.Figure(data=[
        go.Surface(
            z=z_viability, 
            x=x_vals_plot, 
            y=y_vals_plot, 
            surfacecolor=z_bliss, 
            colorscale='jet_r', 
            cmin=-0.3, 
            cmax=0.3, 
            colorbar=dict(title='Bliss Independence')
        )
    ])
    
    fig.update_layout(
        title=str(title_name), 
        scene=dict(
            xaxis=dict(title=x_drug, type='log', tickvals=x_vals_plot, ticktext=x_ticktext),
            yaxis=dict(title=y_drug, type='log', tickvals=y_vals_plot, ticktext=y_ticktext),
            zaxis=dict(title='Relative Cell Survival', range=[0, 1.1])
        )
    )
    
    # Save plot
    fig.write_html(synergy_output_dir / f'{title_name}_synergy_plot.html')
    logger.info(f'{title_name} plot saved.')
    
    # Rename raw counts for easier tracking
    tb.rename_counts(cp_csv, synergy_output_dir / f'{title_name}_synergy_counts.csv')

    if show_plot:
        fig.show()
