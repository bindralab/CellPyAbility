"""
Simple analysis module - refactored to separate analysis logic from GUI.
This can be called from either the CLI or the original GUI script.
"""

from . import toolbox as tb

# Initialize toolbox
logger, base_dir = tb.logger, tb.base_dir


def run_simple(title, image_dir, counts_file=None):
    """
    Run simple nuclei counting analysis.
    
    Parameters:
    -----------
    title : str
        Title of the experiment
    image_dir : str
        Directory containing the well images
    counts_file : str, optional
        Path to pre-existing counts CSV file (for testing)
    """
    
    # Run CellProfiler via the command line
    df_cp, cp_csv = tb.run_cellprofiler(image_dir, counts_file=counts_file)
    df_cp.drop(columns='ImageNumber', inplace=True)
    df_cp.columns = ['nuclei','well']
    
    # Rename wells and define row/column names
    df_cp['well'] = df_cp['well'].apply(lambda x: tb.rename_wells(x, tb.wells))
    df_cp[['Row','Column']] = df_cp['well'].str.extract(r'^([B-G])(\d+)$')
    
    # Pivot df_cp so it matches a 96-well layout (nuclei count matrix)
    row_labels = ['B','C','D','E','F','G']
    column_labels = [str(i) for i in range(2,12)]
    count_matrix = (
        df_cp
        .pivot(index='Row', columns='Column', values='nuclei')
        .reindex(index=row_labels, columns=column_labels)
    )
    
    # Define or create and define CellPyAbility/simple_output/ directory
    outdir = base_dir / 'simple_output'
    outdir.mkdir(exist_ok=True)
    
    # Save the count matrix to the simple_output directory
    count_matrix.to_csv(outdir / f'{title}_simple_CountMatrix.csv')
    logger.info(f"Saved count matrix for '{title}' to {outdir}")
