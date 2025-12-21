"""
Test that CLI modules produce output matching expected test files.

This test verifies that running the analysis modules with test count files
produces output that matches the expected Stats files.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from cellpyability import gda_analysis, synergy_analysis, simple_analysis


def compare_csv_files(output_file, expected_file, tolerance=1e-6):
    """
    Compare two CSV files for equality, allowing for floating point tolerance.
    
    Returns:
        tuple: (bool, str) - (files_match, error_message)
    """
    try:
        df_output = pd.read_csv(output_file, index_col=0)
        df_expected = pd.read_csv(expected_file, index_col=0)
        
        # Check shape
        if df_output.shape != df_expected.shape:
            return False, f"Shape mismatch: {df_output.shape} vs {df_expected.shape}"
        
        # Check column names
        if not df_output.columns.equals(df_expected.columns):
            return False, f"Column mismatch: {df_output.columns.tolist()} vs {df_expected.columns.tolist()}"
        
        # Check index
        if not df_output.index.equals(df_expected.index):
            return False, f"Index mismatch: {df_output.index.tolist()} vs {df_expected.index.tolist()}"
        
        # Compare values with tolerance for floats
        for col in df_output.columns:
            for idx in df_output.index:
                val_out = df_output.loc[idx, col]
                val_exp = df_expected.loc[idx, col]
                
                # Handle string comparisons
                if isinstance(val_out, str) or isinstance(val_exp, str):
                    if str(val_out) != str(val_exp):
                        return False, f"String mismatch at [{idx}, {col}]: '{val_out}' vs '{val_exp}'"
                else:
                    # Numeric comparison with tolerance
                    try:
                        if not np.isclose(float(val_out), float(val_exp), rtol=tolerance, atol=tolerance):
                            return False, f"Value mismatch at [{idx}, {col}]: {val_out} vs {val_exp}"
                    except (ValueError, TypeError):
                        if val_out != val_exp:
                            return False, f"Value mismatch at [{idx}, {col}]: {val_out} vs {val_exp}"
        
        return True, "Files match"
    except Exception as e:
        return False, f"Error comparing files: {str(e)}"


def test_gda_module():
    """Test gda module with test counts file."""
    print("\n" + "="*80)
    print("Testing gda Module")
    print("="*80)
    
    test_data_dir = Path(__file__).parent / "data"
    counts_file = test_data_dir / "test_gda_counts.csv"
    expected_stats = test_data_dir / "test_gda_Stats.csv"
    
    # Run gda analysis (output goes to ./cellpyability_output/gda_output/)
    print(f"Running gda analysis with counts file: {counts_file}")
    gda_analysis.run_gda(
        title_name="test",
        upper_name="Cell Line A",
        lower_name="Cell Line B",
        top_conc=0.000001,
        dilution=3,
        image_dir="/tmp/dummy",
        show_plot=False,
        counts_file=str(counts_file)
    )
    
    # Check output file (in current working directory)
    output_stats = Path.cwd() / "cellpyability_output/gda_output/test_gda_Stats.csv"
    
    try:
        if not output_stats.exists():
            print(f"[FAIL] FAILED: Output file not created: {output_stats}")
            return False
        
        print(f"Output file created: {output_stats}")
        
        # Compare files
        match, message = compare_csv_files(output_stats, expected_stats)
        
        if match:
            print(f"[PASS] PASSED: GDA Stats output matches expected file")
            print(f"   {message}")
            result = True
        else:
            print(f"[FAIL] FAILED: GDA Stats output does not match")
            print(f"   {message}")
            
            # Show first few rows for debugging
            print("\n   First rows of output:")
            df_out = pd.read_csv(output_stats, index_col=0)
            print(df_out.head())
            print("\n   First rows of expected:")
            df_exp = pd.read_csv(expected_stats, index_col=0)
            print(df_exp.head())
            
            result = False
    finally:
        # Clean up output files - use ignore_errors for Windows compatibility
        if output_stats.exists():
            try:
                shutil.rmtree(output_stats.parent, ignore_errors=True)
            except Exception as e:
                print(f"Warning: Could not clean up output directory: {e}")
    
    return result


def test_synergy_module():
    """Test synergy module with test counts file."""
    print("\n" + "="*80)
    print("Testing synergy Module")
    print("="*80)
    
    test_data_dir = Path(__file__).parent / "data"
    counts_file = test_data_dir / "test_synergy_counts.csv"
    expected_bliss = test_data_dir / "test_synergy_BlissMatrix.csv"
    
    # Run Synergy analysis (output goes to ./cellpyability_output/synergy_output/)
    print(f"Running Synergy analysis with counts file: {counts_file}")
    synergy_analysis.run_synergy(
        title_name="test",
        x_drug="Drug X",
        x_top_conc=0.0004,
        x_dilution=4,
        y_drug="Drug Y",
        y_top_conc=0.0001,
        y_dilution=4,
        image_dir="/tmp/dummy",
        show_plot=False,
        counts_file=str(counts_file)
    )
    
    # Check output file (in current working directory)
    output_bliss = Path.cwd() / "cellpyability_output/synergy_output/test_synergy_BlissMatrix.csv"
    
    try:
        if not output_bliss.exists():
            print(f"[FAIL] FAILED: Output file not created: {output_bliss}")
            return False
        
        print(f"Output file created: {output_bliss}")
        
        # Compare files
        match, message = compare_csv_files(output_bliss, expected_bliss, tolerance=1e-10)
        
        if match:
            print(f"[PASS] PASSED: Synergy BlissMatrix output matches expected file")
            print(f"   {message}")
            result = True
        else:
            print(f"[FAIL] FAILED: Synergy BlissMatrix output does not match")
            print(f"   {message}")
            
            # Show first few rows for debugging
            print("\n   First rows of output:")
            df_out = pd.read_csv(output_bliss)
            print(df_out.head())
            print("\n   First rows of expected:")
            df_exp = pd.read_csv(expected_bliss)
            print(df_exp.head())
            
            result = False
    finally:
        # Clean up output files - use ignore_errors for Windows compatibility
        if output_bliss.exists():
            try:
                shutil.rmtree(output_bliss.parent, ignore_errors=True)
            except Exception as e:
                print(f"Warning: Could not clean up output directory: {e}")
    
    return result


def test_simple_module():
    """Test simple module with test counts file."""
    print("\n" + "="*80)
    print("Testing simple Module")
    print("="*80)
    
    test_data_dir = Path(__file__).parent / "data"
    # Use gda counts for simple module test
    counts_file = test_data_dir / "test_gda_counts.csv"
    expected_output = test_data_dir / "test_simple_CountMatrix.csv"
    
    # Run Simple analysis (output goes to ./cellpyability_output/simple_output/)
    print(f"Running Simple analysis with counts file: {counts_file}")
    simple_analysis.run_simple(
        title="test",
        image_dir="/tmp/dummy",
        counts_file=str(counts_file)
    )
    
    # Check output file (in current working directory)
    output_matrix = Path.cwd() / "cellpyability_output/simple_output/test_simple_CountMatrix.csv"
    
    try:
        if not output_matrix.exists():
            print(f"[FAIL] FAILED: Output file not created: {output_matrix}")
            return False
        
        print(f"Output file created: {output_matrix}")
        
        # Compare files
        match, message = compare_csv_files(output_matrix, expected_output)
        
        if match:
            print(f"[PASS] PASSED: Simple CountMatrix output matches expected file")
            print(f"   {message}")
            result = True
        else:
            print(f"[FAIL] FAILED: Simple CountMatrix output does not match")
            print(f"   {message}")
            
            # Show files for debugging
            print("\n   Output:")
            df_out = pd.read_csv(output_matrix, index_col=0)
            print(df_out)
            print("\n   Expected:")
            df_exp = pd.read_csv(expected_output, index_col=0)
            print(df_exp)
            
            result = False
    finally:
        # Clean up output files - use ignore_errors for Windows compatibility
        if output_matrix.exists():
            try:
                shutil.rmtree(output_matrix.parent, ignore_errors=True)
            except Exception as e:
                print(f"Warning: Could not clean up output directory: {e}")
    
    return result


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("CellPyAbility Module Output Validation Tests")
    print("="*80)
    print("Testing that analysis modules produce expected output from test count files")
    
    results = {
        'gda': test_gda_module(),
        'synergy': test_synergy_module(),
        'simple': test_simple_module()
    }
    
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    
    all_passed = True
    for module, passed in results.items():
        status = "[PASS] PASSED" if passed else "[FAIL] FAILED"
        print(f"{module:15} {status}")
        if not passed:
            all_passed = False
    
    print("="*80)
    
    if all_passed:
        print("\nAll tests passed! Outputs match expected files.")
        return 0
    else:
        print("\n[WARNING] Some tests failed. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
