# Python wrapper for nim-mmcif
from .mmcif import parse_mmcif, get_atom_count, get_atoms, get_atom_positions

__version__ = "0.0.1"
__all__ = ["parse_mmcif", "get_atom_count", "get_atoms", "get_atom_positions"]