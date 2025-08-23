"""Test parsing of quoted values with spaces in mmCIF files."""
import nim_mmcif
import os

def test_quoted_atom_names():
    """Test that quoted atom names with spaces are parsed correctly."""
    test_file = os.path.join(os.path.dirname(__file__), "test_quoted.mmcif")
    
    # Parse the file
    data = nim_mmcif.parse_mmcif(test_file)
    atoms = data["atoms"]
    
    # Test first atom with quoted name "N A"
    assert atoms[0]["label_atom_id"] == "N A", f"Expected 'N A', got '{atoms[0]['label_atom_id']}'"
    assert atoms[0]["auth_atom_id"] == "N A", f"Expected 'N A' for auth_atom_id"
    
    # Test second atom with single-quoted name 'C B'
    assert atoms[1]["label_atom_id"] == "C B", f"Expected 'C B', got '{atoms[1]['label_atom_id']}'"
    assert atoms[1]["auth_atom_id"] == "C B", f"Expected 'C B' for auth_atom_id"
    
    # Test third atom with quoted name "O 1"
    assert atoms[2]["label_atom_id"] == "O 1", f"Expected 'O 1', got '{atoms[2]['label_atom_id']}'"
    assert atoms[2]["auth_atom_id"] == "O 1", f"Expected 'O 1' for auth_atom_id"
    
    # Verify coordinates are still parsed correctly after quoted values
    assert abs(atoms[0]["Cartn_x"] - 6.204) < 0.001, "X coordinate should be correct"
    assert abs(atoms[0]["Cartn_y"] - 16.869) < 0.001, "Y coordinate should be correct"
    assert abs(atoms[0]["Cartn_z"] - 4.854) < 0.001, "Z coordinate should be correct"
    
    # Check that x, y, z aliases work
    assert atoms[0]["x"] == atoms[0]["Cartn_x"], "x should alias Cartn_x"
    assert atoms[0]["y"] == atoms[0]["Cartn_y"], "y should alias Cartn_y"
    assert atoms[0]["z"] == atoms[0]["Cartn_z"], "z should alias Cartn_z"
    
    print("All quoted value tests passed!")

if __name__ == "__main__":
    test_quoted_atom_names()