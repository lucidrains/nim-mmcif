"""
pytest tests for nim-mmcif Python bindings
"""
import pytest
from pathlib import Path

# Add the python_wrapper to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "python_wrapper"))

from mmcif import parse_mmcif, get_atom_count, Atom


class TestMmcifParser:
    """Test cases for the mmCIF parser"""
    
    @pytest.fixture
    def test_mmcif_file(self):
        """Path to test mmCIF file"""
        return Path(__file__).parent / "test.mmcif"
    
    def test_file_exists(self, test_mmcif_file):
        """Test that the test file exists"""
        assert test_mmcif_file.exists(), f"Test file not found: {test_mmcif_file}"
    
    def test_get_atom_count(self, test_mmcif_file):
        """Test getting atom count from mmCIF file"""
        count = get_atom_count(test_mmcif_file)
        assert isinstance(count, int)
        assert count > 0, "Should have at least one atom"
        # Based on the test.mmcif file, we expect 7 atoms
        assert count == 7, f"Expected 7 atoms, got {count}"
    
    def test_parse_mmcif_returns_list(self, test_mmcif_file):
        """Test that parse_mmcif returns a list"""
        atoms = parse_mmcif(test_mmcif_file)
        assert isinstance(atoms, list)
        assert len(atoms) > 0, "Should return at least one atom"
        assert len(atoms) == 7, f"Expected 7 atoms, got {len(atoms)}"
    
    def test_parse_mmcif_atom_structure(self, test_mmcif_file):
        """Test that parsed atoms have correct structure"""
        atoms = parse_mmcif(test_mmcif_file)
        
        # Test first atom
        atom = atoms[0]
        assert isinstance(atom, Atom)
        
        # Check all required fields exist
        assert hasattr(atom, 'type')
        assert hasattr(atom, 'id')
        assert hasattr(atom, 'type_symbol')
        assert hasattr(atom, 'label_atom_id')
        assert hasattr(atom, 'Cartn_x')
        assert hasattr(atom, 'Cartn_y')
        assert hasattr(atom, 'Cartn_z')
        assert hasattr(atom, 'x')
        assert hasattr(atom, 'y')
        assert hasattr(atom, 'z')
    
    def test_first_atom_values(self, test_mmcif_file):
        """Test specific values for the first atom"""
        atoms = parse_mmcif(test_mmcif_file)
        first_atom = atoms[0]
        
        # Based on the test.mmcif file content:
        # ATOM   1    N  N   . VAL A 1 1   ? 6.204   16.869  4.854   1.00 49.05 ? 1   VAL A N   1
        assert first_atom.type == "ATOM"
        assert first_atom.id == 1
        assert first_atom.type_symbol == "N"
        assert first_atom.label_atom_id == "N"
        assert first_atom.label_comp_id == "VAL"
        assert first_atom.label_asym_id == "A"
        assert first_atom.label_entity_id == 1
        assert first_atom.label_seq_id == 1
        assert abs(first_atom.Cartn_x - 6.204) < 0.001
        assert abs(first_atom.Cartn_y - 16.869) < 0.001
        assert abs(first_atom.Cartn_z - 4.854) < 0.001
        assert abs(first_atom.occupancy - 1.00) < 0.001
        assert abs(first_atom.B_iso_or_equiv - 49.05) < 0.001
        
        # Check that x, y, z are copies of Cartn_x, Cartn_y, Cartn_z
        assert abs(first_atom.x - first_atom.Cartn_x) < 0.001
        assert abs(first_atom.y - first_atom.Cartn_y) < 0.001
        assert abs(first_atom.z - first_atom.Cartn_z) < 0.001
    
    def test_all_atom_types(self, test_mmcif_file):
        """Test that all atoms are ATOM type"""
        atoms = parse_mmcif(test_mmcif_file)
        
        for atom in atoms:
            assert atom.type == "ATOM", f"Expected ATOM type, got {atom.type}"
    
    def test_atom_coordinates_range(self, test_mmcif_file):
        """Test that atom coordinates are within reasonable range"""
        atoms = parse_mmcif(test_mmcif_file)
        
        for atom in atoms:
            # Check that coordinates are reasonable (not NaN, not extremely large)
            assert not (atom.x != atom.x), f"x coordinate is NaN for atom {atom.id}"  # NaN check
            assert not (atom.y != atom.y), f"y coordinate is NaN for atom {atom.id}"
            assert not (atom.z != atom.z), f"z coordinate is NaN for atom {atom.id}"
            
            assert abs(atom.x) < 1000, f"x coordinate too large for atom {atom.id}: {atom.x}"
            assert abs(atom.y) < 1000, f"y coordinate too large for atom {atom.id}: {atom.y}"
            assert abs(atom.z) < 1000, f"z coordinate too large for atom {atom.id}: {atom.z}"
    
    def test_nonexistent_file(self):
        """Test that nonexistent file raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            parse_mmcif("nonexistent_file.mmcif")
        
        with pytest.raises(FileNotFoundError):
            get_atom_count("nonexistent_file.mmcif")
    
    def test_atom_ids_sequential(self, test_mmcif_file):
        """Test that atom IDs are sequential starting from 1"""
        atoms = parse_mmcif(test_mmcif_file)
        
        for i, atom in enumerate(atoms):
            expected_id = i + 1
            assert atom.id == expected_id, f"Expected atom ID {expected_id}, got {atom.id}"
    
    def test_valine_residue(self, test_mmcif_file):
        """Test that all atoms belong to VAL residue"""
        atoms = parse_mmcif(test_mmcif_file)
        
        for atom in atoms:
            assert atom.label_comp_id == "VAL", f"Expected VAL residue, got {atom.label_comp_id}"
            assert atom.auth_comp_id == "VAL", f"Expected VAL auth residue, got {atom.auth_comp_id}"


if __name__ == "__main__":
    # Allow running the tests directly
    pytest.main([__file__, "-v"])