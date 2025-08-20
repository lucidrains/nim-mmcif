"""
Python wrapper for nim-mmcif using native Nim bindings
"""
import sys
import platform
from pathlib import Path
from typing import List, Dict, Any, Union
from dataclasses import dataclass


try:
    import python_bindings as nim_mmcif
except ImportError as e:
    # Check multiple locations for the binary
    search_dirs = [
        Path(__file__).parent,  # In the same directory as this file
        Path(__file__).parent.parent,  # In the parent directory (development)
        Path(__file__).parent / 'platform_modules',  # Platform-specific subdirectory
    ]
    
    # Add all search directories to sys.path
    for search_dir in search_dirs:
        if search_dir.exists() and str(search_dir) not in sys.path:
            sys.path.insert(0, str(search_dir))
    
    # Collect all potential binary files
    binary_extensions = ['*.so', '*.dylib', '*.pyd', '*.dll']
    so_files = []
    for search_dir in search_dirs:
        if search_dir.exists():
            for ext in binary_extensions:
                so_files.extend(search_dir.glob(f"python_bindings{ext}"))
    
    if so_files:
        # Files exist but import failed - try to load them directly
        import importlib.util
        import importlib
        
        nim_mmcif = None
        last_error = None
        
        for so_file in so_files:
            try:
                # For Windows, try ctypes first as a fallback
                if so_file.suffix in ['.pyd', '.dll'] and platform.system() == 'Windows':
                    import ctypes
                    # Try to load the DLL to check for missing dependencies
                    try:
                        ctypes.CDLL(str(so_file))
                    except OSError as dll_error:
                        last_error = f"DLL load failed: {dll_error}"
                        continue
                
                # Try loading the specific file
                spec = importlib.util.spec_from_file_location("python_bindings", so_file)
                if spec and spec.loader:
                    nim_mmcif = importlib.util.module_from_spec(spec)
                    sys.modules["python_bindings"] = nim_mmcif
                    spec.loader.exec_module(nim_mmcif)
                    break
            except Exception as load_error:
                last_error = str(load_error)
                continue
        
        if nim_mmcif is None:
            # Still failed - provide detailed error message
            error_msg = (
                f"Found python_bindings module files {[f.name for f in so_files]} but import failed. "
            )
            if platform.system() == 'Windows':
                error_msg += (
                    f"On Windows, this is often due to missing DLL dependencies. "
                    f"Make sure Visual C++ Redistributables are installed. "
                )
            error_msg += (
                f"Try rebuilding with appropriate flags for your platform. "
                f"Last error: {last_error if last_error else e}"
            )
            raise ImportError(error_msg)
    else:
        # No module files found - need to build
        build_cmd = "nim c --app:lib --out:python_bindings.so src/python_bindings.nim"
        if platform.system() == 'Windows':
            build_cmd = 'nim c --app:lib --dynlibOverride:python3 --passL:"-static-libgcc -static-libstdc++" --out:python_bindings.pyd src/python_bindings.nim'
        
        raise ImportError(
            f"python_bindings module not found. Please build it first with: {build_cmd}. "
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