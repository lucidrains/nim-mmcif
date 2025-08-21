"""nim-mmcif: Fast mmCIF parser using Nim via nimporter."""

import os
import platform
import sys

try:
    # Enable nimporter to compile and import .nim files
    import nimporter
    
    # Import the Nim module directly
    # Note: nimporter.build_nim_extensions() is only needed during setup/build,
    # not at runtime. The import hooks are automatically installed when nimporter is imported.
    from . import nim_mmcif as mmcif
    
    # Re-export the functions with Python-friendly wrappers
    from pathlib import Path
    from typing import Any, Dict, List, Tuple, Union
    
    
    def parse_mmcif(filepath: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse an mmCIF file using the Nim backend.
        
        Args:
            filepath: Path to the mmCIF file.
            
        Returns:
            Dictionary containing parsed mmCIF data with 'atoms' key.
            
        Raises:
            FileNotFoundError: If the file doesn't exist.
            RuntimeError: If parsing fails.
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"mmCIF file not found: {filepath}")
        
        try:
            return mmcif.parse_mmcif(str(filepath))
        except Exception as e:
            raise RuntimeError(f"Failed to parse mmCIF file: {e}") from e
    
    
    def get_atom_count(filepath: Union[str, Path]) -> int:
        """
        Get the number of atoms in an mmCIF file.
        
        Args:
            filepath: Path to the mmCIF file.
            
        Returns:
            Number of atoms in the file.
            
        Raises:
            FileNotFoundError: If the file doesn't exist.
            RuntimeError: If counting fails.
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"mmCIF file not found: {filepath}")
        
        try:
            return mmcif.get_atom_count(str(filepath))
        except Exception as e:
            raise RuntimeError(f"Failed to get atom count: {e}") from e
    
    
    def get_atoms(filepath: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Get all atoms from an mmCIF file.
        
        Args:
            filepath: Path to the mmCIF file.
            
        Returns:
            List of dictionaries, each representing an atom with its properties.
            
        Raises:
            FileNotFoundError: If the file doesn't exist.
            RuntimeError: If reading atoms fails.
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"mmCIF file not found: {filepath}")
        
        try:
            return mmcif.get_atoms(str(filepath))
        except Exception as e:
            raise RuntimeError(f"Failed to get atoms: {e}") from e
    
    
    def get_atom_positions(filepath: Union[str, Path]) -> List[Tuple[float, float, float]]:
        """
        Get 3D coordinates of all atoms from an mmCIF file.
        
        Args:
            filepath: Path to the mmCIF file.
            
        Returns:
            List of (x, y, z) coordinate tuples.
            
        Raises:
            FileNotFoundError: If the file doesn't exist.
            RuntimeError: If reading positions fails.
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"mmCIF file not found: {filepath}")
        
        try:
            return mmcif.get_atom_positions(str(filepath))
        except Exception as e:
            raise RuntimeError(f"Failed to get atom positions: {e}") from e
    
    
    # Export public API
    __all__ = [
        'parse_mmcif',
        'get_atom_count', 
        'get_atoms',
        'get_atom_positions'
    ]
    
    __version__ = '0.0.5'

except ImportError as e:
    # Fallback error message if nimporter is not installed
    import sys
    
    # Check for specific missing dependencies
    missing_deps = []
    try:
        import nimporter
    except ImportError:
        missing_deps.append("nimporter")
    
    error_msg = "Failed to import nim-mmcif. "
    
    if missing_deps:
        error_msg += f"Missing dependencies: {', '.join(missing_deps)}\n"
    
    error_msg += (
        "Please ensure:\n"
        "1. nimporter is installed: pip install nimporter\n"
        "2. Nim compiler is installed: https://nim-lang.org/install.html\n"
        "3. nimpy is installed: nimble install nimpy\n"
    )
    
    # Only show original error if it's not about setuptools
    # (setuptools errors are typically secondary issues from nimporter internals)
    if "setuptools" not in str(e):
        error_msg += f"\nOriginal error: {e}"
    
    raise ImportError(error_msg) from e