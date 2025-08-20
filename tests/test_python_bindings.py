"""Tests for nim-mmcif Python bindings."""
import math
from pathlib import Path

import pytest

from nim_mmcif import get_atom_count, get_atom_positions, get_atoms, parse_mmcif


class TestMmcifParser:
    """Test cases for the mmCIF parser."""

    @pytest.fixture
    def test_mmcif_file(self):
        """Fixture providing path to test mmCIF file."""
        return Path(__file__).parent / "test.mmcif"

    def test_file_exists(self, test_mmcif_file):
        """Verify test file exists."""
        assert test_mmcif_file.exists(), f"Test file not found: {test_mmcif_file}"

    def test_parse_mmcif_returns_dict(self, test_mmcif_file):
        """Test that parse_mmcif returns a dictionary with atoms."""
        result = parse_mmcif(test_mmcif_file)
        
        assert isinstance(result, dict)
        assert "atoms" in result
        assert isinstance(result["atoms"], list)
        assert len(result["atoms"]) == 7

    def test_get_atom_count(self, test_mmcif_file):
        """Test atom count retrieval."""
        count = get_atom_count(test_mmcif_file)
        
        assert isinstance(count, int)
        assert count == 7

    def test_get_atoms_returns_list(self, test_mmcif_file):
        """Test that get_atoms returns a list of atom dictionaries."""
        atoms = get_atoms(test_mmcif_file)
        
        assert isinstance(atoms, list)
        assert len(atoms) == 7
        assert all(isinstance(atom, dict) for atom in atoms)

    def test_atom_structure(self, test_mmcif_file):
        """Test that atoms have the expected structure."""
        atoms = get_atoms(test_mmcif_file)
        first_atom = atoms[0]
        
        # Check required fields
        required_fields = [
            "type", "id", "type_symbol", "label_atom_id",
            "label_comp_id", "label_asym_id", "label_entity_id", "label_seq_id",
            "Cartn_x", "Cartn_y", "Cartn_z", "x", "y", "z",
            "occupancy", "B_iso_or_equiv"
        ]
        
        for field in required_fields:
            assert field in first_atom, f"Missing required field: {field}"

    def test_first_atom_values(self, test_mmcif_file):
        """Verify values of the first atom match expected data."""
        atoms = get_atoms(test_mmcif_file)
        atom = atoms[0]
        
        # Expected values from test.mmcif
        assert atom["type"] == "ATOM"
        assert atom["id"] == 1
        assert atom["type_symbol"] == "N"
        assert atom["label_atom_id"] == "N"
        assert atom["label_comp_id"] == "VAL"
        assert atom["label_asym_id"] == "A"
        assert atom["label_entity_id"] == 1
        assert atom["label_seq_id"] == 1
        
        # Check coordinates
        assert math.isclose(atom["Cartn_x"], 6.204, abs_tol=0.001)
        assert math.isclose(atom["Cartn_y"], 16.869, abs_tol=0.001)
        assert math.isclose(atom["Cartn_z"], 4.854, abs_tol=0.001)
        
        # Check that x, y, z match Cartn values
        assert atom["x"] == atom["Cartn_x"]
        assert atom["y"] == atom["Cartn_y"]
        assert atom["z"] == atom["Cartn_z"]
        
        # Check other properties
        assert math.isclose(atom["occupancy"], 1.00, abs_tol=0.001)
        assert math.isclose(atom["B_iso_or_equiv"], 49.05, abs_tol=0.001)

    def test_all_atoms_are_valid(self, test_mmcif_file):
        """Verify all atoms have valid data."""
        atoms = get_atoms(test_mmcif_file)
        
        for i, atom in enumerate(atoms):
            # Check atom type
            assert atom["type"] in ["ATOM", "HETATM"]
            
            # Check ID is sequential
            assert atom["id"] == i + 1
            
            # Check coordinates are numbers
            assert isinstance(atom["x"], (int, float))
            assert isinstance(atom["y"], (int, float))
            assert isinstance(atom["z"], (int, float))
            
            # Check coordinates are reasonable
            assert -1000 < atom["x"] < 1000
            assert -1000 < atom["y"] < 1000
            assert -1000 < atom["z"] < 1000
            
            # Check occupancy and B-factor
            assert 0 <= atom["occupancy"] <= 1
            assert atom["B_iso_or_equiv"] >= 0

    def test_get_atom_positions(self, test_mmcif_file):
        """Test coordinate extraction."""
        positions = get_atom_positions(test_mmcif_file)
        
        assert isinstance(positions, list)
        assert len(positions) == 7
        
        # Check first position
        x, y, z = positions[0]
        assert math.isclose(x, 6.204, abs_tol=0.001)
        assert math.isclose(y, 16.869, abs_tol=0.001)
        assert math.isclose(z, 4.854, abs_tol=0.001)
        
        # Check all positions are valid tuples
        for pos in positions:
            assert isinstance(pos, tuple)
            assert len(pos) == 3
            assert all(isinstance(coord, (int, float)) for coord in pos)

    def test_nonexistent_file_raises_error(self):
        """Test proper error handling for missing files."""
        nonexistent = "nonexistent_file.mmcif"
        
        with pytest.raises(FileNotFoundError):
            parse_mmcif(nonexistent)
        
        with pytest.raises(FileNotFoundError):
            get_atom_count(nonexistent)
        
        with pytest.raises(FileNotFoundError):
            get_atoms(nonexistent)
        
        with pytest.raises(FileNotFoundError):
            get_atom_positions(nonexistent)

    def test_valine_residue_consistency(self, test_mmcif_file):
        """Verify all atoms belong to VAL residue."""
        atoms = get_atoms(test_mmcif_file)
        
        for atom in atoms:
            assert atom["label_comp_id"] == "VAL"
            assert atom["auth_comp_id"] == "VAL"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])