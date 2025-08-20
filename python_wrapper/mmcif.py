"""
Python wrapper for nim-mmcif using native Nim bindings
"""
import sys
from pathlib import Path
from typing import List, Dict, Any, Union
from dataclasses import dataclass


try:
    import python_bindings as nim_mmcif
except ImportError as e:
    # Check if we're in a development environment
    current_dir = Path(__file__).parent.parent
    so_files = list(current_dir.glob("python_bindings*.so")) + list(current_dir.glob("python_bindings*.dylib")) + list(current_dir.glob("python_bindings*.pyd"))
    
    if so_files:
        # Files exist but import failed - try to add the directory to sys.path and import again
        sys.path.insert(0, str(current_dir))
        
        # Try importing with the exact filename (without extension)
        import importlib.util
        import importlib
        
        nim_mmcif = None
        for so_file in so_files:
            try:
                # Try loading the specific file
                spec = importlib.util.spec_from_file_location("python_bindings", so_file)
                if spec and spec.loader:
                    nim_mmcif = importlib.util.module_from_spec(spec)
                    sys.modules["python_bindings"] = nim_mmcif
                    spec.loader.exec_module(nim_mmcif)
                    break
            except Exception:
                continue
        
        if nim_mmcif is None:
            # Still failed - might be a compatibility issue
            raise ImportError(
                f"Found python_bindings module files {[f.name for f in so_files]} but import failed. "
                f"This might be a compatibility issue. Try rebuilding with: nim c --app:lib --out:python_bindings.so src/python_bindings.nim. "
                f"Original error: {e}"
            )
    else:
        # No module files found - need to build
        raise ImportError(
            f"python_bindings module not found. Please build it first with: nim c --app:lib --out:python_bindings.so src/python_bindings.nim. "
            f"Make sure you have Nim installed and run the build command in the project root. "
            f"Original error: {e}"
        )

def parse_mmcif(filepath: Union[str, Path]):
    """
    Parse mmCIF file using Nim backend
    
    Args:
        filepath: Path to the mmCIF file
        
    Returns:
        mmCIF object with atoms
        
    Raises:
        FileNotFoundError: If the mmCIF file doesn't exist
        RuntimeError: If the Nim parser fails
    """
    filepath = str(filepath)
    
    if not Path(filepath).exists():
        raise FileNotFoundError(f"mmCIF file not found: {filepath}")
    
    try:
        return nim_mmcif.parse_mmcif(filepath)
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
        return nim_mmcif.get_atom_count(filepath)
    except Exception as e:
        raise RuntimeError(f"Failed to get atom count: {e}")

def get_atoms(filepath: Union[str, Path]):
    """
    Get all atoms from a mmCIF file
    
    Args:
        filepath: Path to the mmCIF file
        
    Returns:
        List of Atom objects
    """
    filepath = str(filepath)
    
    if not Path(filepath).exists():
        raise FileNotFoundError(f"mmCIF file not found: {filepath}")
    
    try:
        return nim_mmcif.get_atoms(filepath)
    except Exception as e:
        raise RuntimeError(f"Failed to get atoms: {e}")

def get_atom_positions(filepath: Union[str, Path]):
    """
    Get just the 3D coordinates of all atoms
    
    Args:
        filepath: Path to the mmCIF file
        
    Returns:
        List of (x, y, z) tuples
    """
    filepath = str(filepath)
    
    if not Path(filepath).exists():
        raise FileNotFoundError(f"mmCIF file not found: {filepath}")
    
    try:
        return nim_mmcif.get_atom_positions(filepath)
    except Exception as e:
        raise RuntimeError(f"Failed to get atom positions: {e}")

# For backward compatibility
mmcif_parse = parse_mmcif