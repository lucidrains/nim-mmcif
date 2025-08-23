"""Tests for dataclass-based mmCIF data structures."""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from nim_mmcif import Atom, MmcifData, parse_mmcif, parse_mmcif_batch


@pytest.fixture
def test_mmcif_file():
    """Fixture providing path to test mmCIF file."""
    return Path(__file__).parent / "test.mmcif"


@pytest.fixture  
def test_files():
    """Fixture providing paths to all test mmCIF files."""
    test_dir = Path(__file__).parent
    return [
        test_dir / "test1.mmcif",
        test_dir / "test2.mmcif",
        test_dir / "test.mmcif"
    ]


def test_parse_mmcif_as_dataclass(test_mmcif_file):
    """Test parsing mmCIF file returns MmcifData when as_dataclass=True."""
    result = parse_mmcif(test_mmcif_file, as_dataclass=True)
    
    assert isinstance(result, MmcifData)
    assert isinstance(result.atoms, list)
    assert len(result.atoms) == 7
    assert all(isinstance(atom, Atom) for atom in result.atoms)


def test_atom_dot_notation_access(test_mmcif_file):
    """Test accessing atom properties using dot notation."""
    data = parse_mmcif(test_mmcif_file, as_dataclass=True)
    first_atom = data.atoms[0]
    
    # Test dot notation access
    assert first_atom.type == "ATOM"
    assert first_atom.id == 1
    assert first_atom.type_symbol == "N"
    assert first_atom.label_atom_id == "N"
    assert first_atom.label_comp_id == "VAL"
    assert first_atom.label_asym_id == "A"
    assert first_atom.label_entity_id == 1
    assert first_atom.label_seq_id == 1
    
    # Test coordinate access with both forms
    assert math.isclose(first_atom.Cartn_x, 6.204, abs_tol=0.001)
    assert math.isclose(first_atom.Cartn_y, 16.869, abs_tol=0.001)
    assert math.isclose(first_atom.Cartn_z, 4.854, abs_tol=0.001)
    
    # Test convenience aliases
    assert first_atom.x == first_atom.Cartn_x
    assert first_atom.y == first_atom.Cartn_y
    assert first_atom.z == first_atom.Cartn_z


def test_mmcif_data_properties(test_mmcif_file):
    """Test MmcifData convenience properties and methods."""
    data = parse_mmcif(test_mmcif_file, as_dataclass=True)
    
    # Test atom_count property
    assert data.atom_count == 7
    
    # Test positions property
    positions = data.positions
    assert isinstance(positions, list)
    assert len(positions) == 7
    assert all(isinstance(pos, tuple) and len(pos) == 3 for pos in positions)
    
    # Test chains property
    chains = data.chains
    assert isinstance(chains, set)
    assert 'A' in chains
    
    # Test residues property
    residues = data.residues
    assert isinstance(residues, set)
    assert ('A', 1) in residues


def test_atom_position_property(test_mmcif_file):
    """Test Atom.position property returns correct tuple."""
    data = parse_mmcif(test_mmcif_file, as_dataclass=True)
    first_atom = data.atoms[0]
    
    position = first_atom.position
    assert isinstance(position, tuple)
    assert len(position) == 3
    assert math.isclose(position[0], 6.204, abs_tol=0.001)
    assert math.isclose(position[1], 16.869, abs_tol=0.001)
    assert math.isclose(position[2], 4.854, abs_tol=0.001)


def test_get_chain_method(test_mmcif_file):
    """Test MmcifData.get_chain method."""
    data = parse_mmcif(test_mmcif_file, as_dataclass=True)
    
    chain_a_atoms = data.get_chain('A')
    assert isinstance(chain_a_atoms, list)
    assert len(chain_a_atoms) == 7  # All atoms are in chain A
    assert all(atom.label_asym_id == 'A' for atom in chain_a_atoms)


def test_get_residue_method(test_mmcif_file):
    """Test MmcifData.get_residue method."""
    data = parse_mmcif(test_mmcif_file, as_dataclass=True)
    
    residue_atoms = data.get_residue('A', 1)
    assert isinstance(residue_atoms, list)
    assert len(residue_atoms) == 7  # All atoms are in residue A:1 (VAL)
    assert all(atom.label_asym_id == 'A' and atom.label_seq_id == 1 
              for atom in residue_atoms)


def test_dataclass_to_dict_conversion(test_mmcif_file):
    """Test converting dataclass back to dictionary."""
    data = parse_mmcif(test_mmcif_file, as_dataclass=True)
    
    # Convert back to dict
    dict_data = data.to_dict()
    
    assert isinstance(dict_data, dict)
    assert 'atoms' in dict_data
    assert isinstance(dict_data['atoms'], list)
    assert len(dict_data['atoms']) == 7
    
    # Check first atom structure
    first_atom = dict_data['atoms'][0]
    assert isinstance(first_atom, dict)
    assert first_atom['type'] == 'ATOM'
    assert first_atom['id'] == 1
    assert first_atom['label_comp_id'] == 'VAL'


def test_batch_parse_as_dataclass(test_files):
    """Test batch parsing returns list of MmcifData when as_dataclass=True."""
    results = parse_mmcif_batch(test_files, as_dataclass=True)
    
    assert isinstance(results, list)
    assert len(results) == 3
    assert all(isinstance(result, MmcifData) for result in results)
    
    # Check atom counts
    assert results[0].atom_count == 3  # test1.mmcif
    assert results[1].atom_count == 3  # test2.mmcif
    assert results[2].atom_count == 7  # test.mmcif


def test_glob_pattern_as_dataclass(test_mmcif_file):
    """Test glob pattern returns dict of MmcifData when as_dataclass=True."""
    test_dir = test_mmcif_file.parent
    pattern = str(test_dir / "test*.mmcif")
    
    results = parse_mmcif(pattern, as_dataclass=True)
    
    assert isinstance(results, dict)
    assert len(results) >= 3  # At least test.mmcif, test1.mmcif, test2.mmcif
    
    # Check that values are MmcifData instances
    for path, data in results.items():
        assert isinstance(data, MmcifData)
        assert isinstance(data.atoms, list)
        assert all(isinstance(atom, Atom) for atom in data.atoms)


def test_backward_compatibility(test_mmcif_file):
    """Test that default behavior (as_dataclass=False) still returns dicts."""
    # Default should return dict
    dict_result = parse_mmcif(test_mmcif_file)
    assert isinstance(dict_result, dict)
    assert 'atoms' in dict_result
    assert isinstance(dict_result['atoms'], list)
    assert isinstance(dict_result['atoms'][0], dict)
    
    # Explicit as_dataclass=False
    dict_result2 = parse_mmcif(test_mmcif_file, as_dataclass=False)
    assert isinstance(dict_result2, dict)
    assert dict_result == dict_result2


def test_mixed_usage_in_code(test_mmcif_file):
    """Test that dataclass can be used seamlessly in typical code patterns."""
    data = parse_mmcif(test_mmcif_file, as_dataclass=True)
    
    # Should work with common patterns
    atom_count = 0
    total_x = 0.0
    
    for atom in data.atoms:
        atom_count += 1
        total_x += atom.x
    
    assert atom_count == 7
    avg_x = total_x / atom_count
    assert avg_x > 0
    
    # Filter atoms by type
    backbone_atoms = [atom for atom in data.atoms if atom.label_atom_id in ['N', 'CA', 'C', 'O']]
    assert len(backbone_atoms) > 0
    
    # Group by residue
    residue_groups = {}
    for atom in data.atoms:
        key = (atom.label_asym_id, atom.label_seq_id)
        if key not in residue_groups:
            residue_groups[key] = []
        residue_groups[key].append(atom)
    
    assert len(residue_groups) > 0


def test_type_hints_work(test_mmcif_file):
    """Test that type hints provide proper IDE support (compile-time check)."""
    data: MmcifData = parse_mmcif(test_mmcif_file, as_dataclass=True)
    atom: Atom = data.atoms[0]
    
    # These should have proper type hints
    x: float = atom.x
    chain_id: str = atom.label_asym_id
    atom_id: int = atom.id
    position: tuple[float, float, float] = atom.position
    
    # Check types at runtime
    assert isinstance(x, float)
    assert isinstance(chain_id, str)
    assert isinstance(atom_id, int)
    assert isinstance(position, tuple)