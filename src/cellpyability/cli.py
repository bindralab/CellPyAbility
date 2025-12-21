"""
Command-line interface for CellPyAbility.

This module provides CLI commands to run the three main modules:
- gda: dose-response analysis
- synergy: drug combination synergy analysis
- simple: nuclei count matrix
"""

import argparse
import sys
from pathlib import Path


def create_parser():
    """Create the argument parser for CellPyAbility CLI."""
    parser = argparse.ArgumentParser(
        prog='cellpyability',
        description='CellPyAbility: Cell viability and dose-response analysis tool'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )
    
    subparsers = parser.add_subparsers(
        title='modules',
        description='Available analysis modules',
        dest='module',
        required=True
    )
    
    # GDA module parser
    gda_parser = subparsers.add_parser(
        'gda',
        help='Growth Delay Assay: dose-response analysis of two cell lines (B-D, E-G) and one treatment (2-11)'
    )
    gda_parser.add_argument(
        '--title',
        required=True,
        help='Title of the experiment (e.g., 20250101_CellLine_Drug)'
    )
    gda_parser.add_argument(
        '--upper-name',
        required=True,
        help='Name for upper cell condition (rows B-D)'
    )
    gda_parser.add_argument(
        '--lower-name',
        required=True,
        help='Name for lower cell condition (rows E-G)'
    )
    gda_parser.add_argument(
        '--top-conc',
        type=float,
        required=True,
        help='Top concentration in molar (e.g., 0.000001 for 1 µM)'
    )
    gda_parser.add_argument(
        '--dilution',
        type=float,
        required=True,
        help='Dilution factor between columns (e.g., 3 for 3-fold dilution)'
    )
    gda_parser.add_argument(
        '--image-dir',
        required=True,
        type=str,
        help='Directory containing the 60 well images'
    )
    gda_parser.add_argument(
        '--no-plot',
        action='store_true',
        help='Skip displaying the plot (still saves it)'
    )
    gda_parser.add_argument(
        '--counts-file',
        type=str,
        help='Path to pre-existing counts CSV file (for testing, bypasses CellProfiler)'
    )
    gda_parser.add_argument(
        '--output-dir',
        type=str,
        help='Custom output directory (default: ./cellpyability_output/ in current working directory)'
    )
    
    # Synergy module parser
    synergy_parser = subparsers.add_parser(
        'synergy',
        help='Synergy analysis: dose response analysis for one cell line and two treatments (row gradient and column gradient)'
    )
    synergy_parser.add_argument(
        '--title',
        required=True,
        help='Title of the experiment'
    )
    synergy_parser.add_argument(
        '--x-drug',
        required=True,
        help='Drug name for horizontal gradient (increases along row)'
    )
    synergy_parser.add_argument(
        '--x-top-conc',
        type=float,
        required=True,
        help='Horizontal top concentration in molar'
    )
    synergy_parser.add_argument(
        '--x-dilution',
        type=float,
        required=True,
        help='Horizontal dilution factor'
    )
    synergy_parser.add_argument(
        '--y-drug',
        required=True,
        help='Drug name for vertical gradient (increases along column)'
    )
    synergy_parser.add_argument(
        '--y-top-conc',
        type=float,
        required=True,
        help='Vertical top concentration in molar'
    )
    synergy_parser.add_argument(
        '--y-dilution',
        type=float,
        required=True,
        help='Vertical dilution factor'
    )
    synergy_parser.add_argument(
        '--image-dir',
        required=True,
        type=str,
        help='Directory containing the 180 well images'
    )
    synergy_parser.add_argument(
        '--no-plot',
        action='store_true',
        help='Skip displaying the plot (still saves it)'
    )
    synergy_parser.add_argument(
        '--counts-file',
        type=str,
        help='Path to pre-existing counts CSV file (for testing, bypasses CellProfiler)'
    )
    synergy_parser.add_argument(
        '--output-dir',
        type=str,
        help='Custom output directory (default: ./cellpyability_output/ in current working directory)'
    )
    
    # Simple module parser
    simple_parser = subparsers.add_parser(
        'simple',
        help='Simple nuclei counting: 96-well count matrix without analysis'
    )
    simple_parser.add_argument(
        '--title',
        required=True,
        help='Title of the experiment'
    )
    simple_parser.add_argument(
        '--image-dir',
        required=True,
        type=str,
        help='Directory containing the well images'
    )
    simple_parser.add_argument(
        '--counts-file',
        type=str,
        help='Path to pre-existing counts CSV file (for testing, bypasses CellProfiler)'
    )
    simple_parser.add_argument(
        '--output-dir',
        type=str,
        help='Custom output directory (default: ./cellpyability_output/ in current working directory)'
    )
    
    return parser


def run_gda(args):
    """Run the GDA module with CLI arguments."""
    # Import here to avoid circular imports and GUI loading
    from cellpyability import gda_analysis
    
    gda_analysis.run_gda(
        title_name=args.title,
        upper_name=args.upper_name,
        lower_name=args.lower_name,
        top_conc=args.top_conc,
        dilution=args.dilution,
        image_dir=args.image_dir,
        show_plot=not args.no_plot,
        counts_file=getattr(args, 'counts_file', None),
        output_dir=getattr(args, 'output_dir', None)
    )


def run_synergy(args):
    """Run the synergy module with CLI arguments."""
    from cellpyability import synergy_analysis
    
    synergy_analysis.run_synergy(
        title_name=args.title,
        x_drug=args.x_drug,
        x_top_conc=args.x_top_conc,
        x_dilution=args.x_dilution,
        y_drug=args.y_drug,
        y_top_conc=args.y_top_conc,
        y_dilution=args.y_dilution,
        image_dir=args.image_dir,
        show_plot=not args.no_plot,
        counts_file=getattr(args, 'counts_file', None),
        output_dir=getattr(args, 'output_dir', None)
    )


def run_simple(args):
    """Run the simple module with CLI arguments."""
    from cellpyability import simple_analysis
    
    simple_analysis.run_simple(
        title=args.title,
        image_dir=args.image_dir,
        counts_file=getattr(args, 'counts_file', None),
        output_dir=getattr(args, 'output_dir', None)
    )


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        if args.module == 'gda':
            run_gda(args)
        elif args.module == 'synergy':
            run_synergy(args)
        elif args.module == 'simple':
            run_simple(args)
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
