"""
Simple analysis module that returns a nuclei count matrix without further analysis.
Offers maximum flexibility for plate mapping.
"""

from . import toolbox as tb

# Initialize toolbox
logger, base_dir = tb.logger, tb.base_dir


def run_simple(title, image_dir, counts_file=None, output_dir=None):
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
    output_dir : str, optional
        Custom output directory. If None, uses current working directory.
    """
    
    # Run CellProfiler via the command line
    df_cp, cp_csv = tb.run_cellprofiler(image_dir, counts_file=counts_file, output_dir=output_dir)
    
    # Clean up DataFrame columns
    df_cp.drop(columns='ImageNumber', inplace=True)
    df_cp.columns = ['nuclei', 'well']
    
    # Rename wells to e.g. B10 format
    df_cp['well'] = df_cp['well'].apply(lambda x: tb.rename_wells(x))
    
    # Extract row/column
    df_cp[['Row','Column']] = df_cp['well'].str.extract(r'^([B-G])(\d+)$')
    
    # Pivot df_cp so it matches a 96-well layout (nuclei count matrix)
    row_labels = ['B','C','D','E','F','G']
    column_labels = [str(i) for i in range(2,12)]
    
    count_matrix = (
        df_cp
        .pivot(index='Row', columns='Column', values='nuclei')
        .reindex(index=row_labels, columns=column_labels)
    )
    
    # Define or create simple_output/ directory in output directory
    output_base = tb.get_output_base_dir(output_dir)
    outdir = output_base / 'simple_output'
    outdir.mkdir(exist_ok=True)
    
    # Save the count matrix to the simple_output directory
    count_matrix.to_csv(outdir / f'{title}_simple_CountMatrix.csv')
    logger.info(f"Saved count matrix for '{title}' to {outdir}")
    
    # Rename the original CellProfiler output for traceability
    tb.rename_counts(cp_csv, outdir / f'{title}_simple_raw_counts.csv')
    logger.info(f"Saved raw counts for '{title}' to {outdir}")
