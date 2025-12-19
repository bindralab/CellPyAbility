"""
CellPyAbility: Open-source cell viability and dose-response analysis tool

CellPyAbility is an automated analysis tool for dose-response experiments 
via nuclei counting. It provides three modules:
- GDA: dose-response analysis of two cell lines with one drug gradient
- synergy: dose-response and synergy analysis with two drug gradients
- simple: raw nuclei count matrix in 96-well format
"""

__version__ = "0.1.0"
__author__ = "James Elia"
__email__ = "james.elia@yale.edu"

from cellpyability import toolbox

__all__ = ['toolbox']
