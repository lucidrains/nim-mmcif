"""Tests for nim-mmcif Python bindings."""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from nim_mmcif import get_atom_count, get_atom_positions, get_atoms, parse_mmcif, parse_mmcif_batch


# Fixtures
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


# Single file parsing tests
def test_file_exists(test_mmcif_file):
    """Verify test file exists."""
    assert test_mmcif_file.exists(), f"Test file not found: {test_mmcif_file}"


def test_parse_mmcif_returns_dict(test_mmcif_file):
    """Test that parse_mmcif returns a dictionary with atoms."""
    result = parse_mmcif(test_mmcif_file)

    assert isinstance(result, dict)
    assert "atoms" in result
    assert isinstance(result["atoms"], list)
    assert len(result["atoms"]) == 7


def test_get_atom_count(test_mmcif_file):
    """Test atom count retrieval."""
    count = get_atom_count(test_mmcif_file)

    assert isinstance(count, int)
    assert count == 7


def test_get_atoms_returns_list(test_mmcif_file):
    """Test that get_atoms returns a list of atom dictionaries."""
    atoms = get_atoms(test_mmcif_file)

    assert isinstance(atoms, list)
    assert len(atoms) == 7
    assert all(isinstance(atom, dict) for atom in atoms)


def test_atom_structure(test_mmcif_file):
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


def test_first_atom_values(test_mmcif_file):
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


def test_all_atoms_are_valid(test_mmcif_file):
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


def test_get_atom_positions(test_mmcif_file):
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


def test_nonexistent_file_raises_error():
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


def test_valine_residue_consistency(test_mmcif_file):
    """Verify all atoms belong to VAL residue."""
    atoms = get_atoms(test_mmcif_file)

    for atom in atoms:
        assert atom["label_comp_id"] == "VAL"
        assert atom["auth_comp_id"] == "VAL"


# Batch processing tests
def test_batch_parse_returns_list(test_files):
    """Test that parse_mmcif_batch returns a list of results."""
    results = parse_mmcif_batch(test_files)
    
    assert isinstance(results, list)
    assert len(results) == 3
    assert all(isinstance(result, dict) for result in results)
    assert all("atoms" in result for result in results)


def test_batch_parse_correct_atom_counts(test_files):
    """Test that batch parsing returns correct atom counts for each file."""
    results = parse_mmcif_batch(test_files)
    
    # test1.mmcif has 3 atoms
    assert len(results[0]["atoms"]) == 3
    # test2.mmcif has 3 atoms
    assert len(results[1]["atoms"]) == 3
    # test.mmcif has 7 atoms
    assert len(results[2]["atoms"]) == 7


def test_batch_parse_correct_residues(test_files):
    """Test that batch parsing correctly identifies residues in each file."""
    results = parse_mmcif_batch(test_files)
    
    # test1.mmcif - all ALA residues
    test1_atoms = results[0]["atoms"]
    assert all(atom["label_comp_id"] == "ALA" for atom in test1_atoms)
    
    # test2.mmcif - mixed residues
    test2_atoms = results[1]["atoms"]
    assert test2_atoms[0]["label_comp_id"] == "GLY"
    assert test2_atoms[1]["label_comp_id"] == "GLY"
    assert test2_atoms[2]["label_comp_id"] == "HOH"  # Water molecule
    
    # test.mmcif - all VAL residues
    test_atoms = results[2]["atoms"]
    assert all(atom["label_comp_id"] == "VAL" for atom in test_atoms)


def test_batch_parse_atom_types(test_files):
    """Test that batch parsing correctly identifies ATOM vs HETATM records."""
    results = parse_mmcif_batch(test_files)
    
    # test2.mmcif has a HETATM record (water)
    test2_atoms = results[1]["atoms"]
    assert test2_atoms[0]["type"] == "ATOM"
    assert test2_atoms[1]["type"] == "ATOM"
    assert test2_atoms[2]["type"] == "HETATM"


def test_batch_parse_coordinates(test_files):
    """Test that batch parsing correctly extracts coordinates."""
    results = parse_mmcif_batch(test_files)
    
    # Check first atom of test1.mmcif
    first_atom_test1 = results[0]["atoms"][0]
    assert math.isclose(first_atom_test1["Cartn_x"], 10.000, abs_tol=0.001)
    assert math.isclose(first_atom_test1["Cartn_y"], 20.000, abs_tol=0.001)
    assert math.isclose(first_atom_test1["Cartn_z"], 30.000, abs_tol=0.001)
    
    # Check that coordinates are aliased correctly
    assert first_atom_test1["x"] == first_atom_test1["Cartn_x"]
    assert first_atom_test1["y"] == first_atom_test1["Cartn_y"]
    assert first_atom_test1["z"] == first_atom_test1["Cartn_z"]


def test_batch_parse_empty_list():
    """Test that batch parsing handles empty list correctly."""
    results = parse_mmcif_batch([])
    
    assert isinstance(results, list)
    assert len(results) == 0


def test_batch_parse_single_file(test_files):
    """Test that batch parsing works with a single file."""
    results = parse_mmcif_batch([test_files[0]])
    
    assert isinstance(results, list)
    assert len(results) == 1
    assert len(results[0]["atoms"]) == 3


def test_batch_parse_nonexistent_file_raises_error(test_files):
    """Test that batch parsing raises error for nonexistent files."""
    invalid_files = test_files + [Path("nonexistent.mmcif")]
    
    with pytest.raises(FileNotFoundError):
        parse_mmcif_batch(invalid_files)


def test_batch_parse_mixed_path_types(test_files):
    """Test that batch parsing handles both string and Path objects."""
    # Mix strings and Path objects
    mixed_paths = [
        str(test_files[0]),  # string
        test_files[1],        # Path object
        str(test_files[2])    # string
    ]
    
    results = parse_mmcif_batch(mixed_paths)
    
    assert len(results) == 3
    assert len(results[0]["atoms"]) == 3
    assert len(results[1]["atoms"]) == 3
    assert len(results[2]["atoms"]) == 7


def test_batch_parse_preserves_order(test_files):
    """Test that batch parsing preserves the order of input files."""
    # Reverse the order of files
    reversed_files = list(reversed(test_files))
    results = parse_mmcif_batch(reversed_files)
    
    # Should match the reversed order: test.mmcif, test2.mmcif, test1.mmcif
    assert len(results[0]["atoms"]) == 7  # test.mmcif
    assert len(results[1]["atoms"]) == 3  # test2.mmcif
    assert len(results[2]["atoms"]) == 3  # test1.mmcif


# Parametrized tests
@pytest.mark.parametrize("filename,expected_count", [
    ("test.mmcif", 7),
    ("test1.mmcif", 3),
    ("test2.mmcif", 3),
])
def test_atom_counts_parametrized(filename, expected_count):
    """Test atom counts for different files using parametrized testing."""
    test_file = Path(__file__).parent / filename
    count = get_atom_count(test_file)
    assert count == expected_count


@pytest.mark.parametrize("filename,expected_residue", [
    ("test.mmcif", "VAL"),
    ("test1.mmcif", "ALA"),
])
def test_residue_types_parametrized(filename, expected_residue):
    """Test that all atoms in certain files have consistent residue types."""
    test_file = Path(__file__).parent / filename
    atoms = get_atoms(test_file)
    assert all(atom["label_comp_id"] == expected_residue for atom in atoms)


@pytest.mark.parametrize("invalid_input", [
    None,
    "",
    "   ",
    "/definitely/not/a/real/path.mmcif",
])
def test_invalid_inputs(invalid_input):
    """Test that invalid inputs raise appropriate errors."""
    with pytest.raises((FileNotFoundError, TypeError, ValueError, RuntimeError)):
        parse_mmcif(invalid_input)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])