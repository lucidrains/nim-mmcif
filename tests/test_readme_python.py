#!/usr/bin/env python3
"""Test that Python examples from README execute without errors."""

from __future__ import annotations

import os
import sys

# Add parent directory to path to import nim_mmcif
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nim_mmcif

def test_readme_python_example():
    """Test the Python example from README."""
    test_file = os.path.join(os.path.dirname(__file__), "test.mmcif")
    
    # Parse an mmCIF file
    data = nim_mmcif.parse_mmcif(test_file)
    print(f"Found {len(data['atoms'])} atoms")
    
    # Get atom count directly
    count = nim_mmcif.get_atom_count(test_file)
    print(f"File contains {count} atoms")
    
    # Get all atoms with their properties
    atoms = nim_mmcif.get_atoms(test_file)
    for atom in atoms[:5]:  # Print first 5 atoms
        print(f"Atom {atom['id']}: {atom['label_atom_id']} at ({atom['x']}, {atom['y']}, {atom['z']})")
    
    # Get just the 3D coordinates
    positions = nim_mmcif.get_atom_positions(test_file)
    for i, (x, y, z) in enumerate(positions[:5]):
        print(f"Position {i}: ({x:.3f}, {y:.3f}, {z:.3f})")
    
    print("Python README example executed successfully!")

if __name__ == "__main__":
    test_readme_python_example()