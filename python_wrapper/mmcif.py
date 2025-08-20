"""
Python wrapper for nim-mmcif using native Nim bindings
"""
import sys
from pathlib import Path
from typing import List, Dict, Any, Union
from dataclasses import dataclass

# Add the parent directory to Python path so we can import the compiled Nim module
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import nim_mmcif
except ImportError as e:
    # Check if we're in a development environment
    current_dir = Path(__file__).parent.parent
    so_files = list(current_dir.glob("nim_mmcif*.so")) + list(current_dir.glob("nim_mmcif*.dylib")) + list(current_dir.glob("nim_mmcif*.pyd"))
    
    if so_files:
        # Files exist but import failed - might be a compatibility issue
        raise ImportError(
            f"Found nim_mmcif module files {[f.name for f in so_files]} but import failed. "
            f"This might be a compatibility issue. Try rebuilding with 'nimble buildPythonModule'. "
            f"Original error: {e}"
        )
    else:
        # No module files found - need to build
        raise ImportError(
            f"nim_mmcif module not found. Please build it first with 'nimble buildPythonModule'. "
            f"Make sure you have Nim installed and run the build command in the project root. "
            f"Original error: {e}"
        )

@dataclass
class Atom:
    """Python representation of a mmCIF atom"""
    type: str
    id: int
    type_symbol: str
    label_atom_id: str
    label_alt_id: str
    label_comp_id: str
    label_asym_id: str
    label_entity_id: int
    label_seq_id: int
    pdbx_PDB_ins_code: str
    Cartn_x: float
    Cartn_y: float
    Cartn_z: float
    occupancy: float
    B_iso_or_equiv: float
    pdbx_formal_charge: str
    auth_seq_id: int
    auth_comp_id: str
    auth_asym_id: str
    auth_atom_id: str
    pdbx_PDB_model_num: int
    x: float
    y: float
    z: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Atom':
        """Create Atom from dictionary"""
        return cls(**data)

def parse_mmcif(filepath: Union[str, Path]) -> List[Atom]:
    """
    Parse mmCIF file using Nim backend
    
    Args:
        filepath: Path to the mmCIF file
        
    Returns:
        List of Atom objects
        
    Raises:
        FileNotFoundError: If the mmCIF file doesn't exist
        RuntimeError: If the Nim parser fails
    """
    filepath = str(filepath)
    
    if not Path(filepath).exists():
        raise FileNotFoundError(f"mmCIF file not found: {filepath}")
    
    try:
        # Call the Nim function directly
        result = nim_mmcif.parse_mmcif_py(filepath)
        
        # Convert to Atom objects
        atoms = []
        for atom_data in result['atoms']:
            atoms.append(Atom.from_dict(atom_data))
        
        return atoms
        
    except Exception as e:
        raise RuntimeError(f"Failed to parse mmCIF file: {e}")

def get_atom_count(filepath: Union[str, Path]) -> int:
    """
    Get the number of atoms in a mmCIF file
    
    Args:
        filepath: Path to the mmCIF file
        
    Returns:
        Number of atoms in the file
    """
    filepath = str(filepath)
    
    if not Path(filepath).exists():
        raise FileNotFoundError(f"mmCIF file not found: {filepath}")
    
    try:
        return nim_mmcif.get_atom_count_py(filepath)
    except Exception as e:
        raise RuntimeError(f"Failed to get atom count: {e}")

# For backward compatibility
mmcif_parse = parse_mmcif