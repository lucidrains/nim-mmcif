"""nim-mmcif: Fast mmCIF parser using Nim with Python bindings."""

from __future__ import annotations

import glob
import platform
import sys
from pathlib import Path
from typing import Any

# Version information
from ._version import __version__

# Dataclass support
from .dataclasses import Atom, MmcifData, dict_to_dataclass

# Import the compiled extension
mmcif = None
_import_error = None

def _try_import_extension():
    """Try to import the pre-compiled Nim extension."""
    global mmcif, _import_error
    
    # Determine the extension filename based on platform
    ext_name = 'nim_mmcif.pyd' if platform.system() == 'Windows' else 'nim_mmcif.so'
    ext_path = Path(__file__).parent / ext_name
    
    if not ext_path.exists():
        raise ImportError(f"Extension file not found: {ext_path}")
    
    # Load the extension directly using importlib
    import importlib.util
    spec = importlib.util.spec_from_file_location("nim_mmcif_ext", ext_path)
    
    if spec and spec.loader:
        mmcif = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mmcif)
        return True
    
    raise ImportError(f"Could not create module spec for {ext_path}")

def _try_nimporter_fallback():
    """Try to compile and import using nimporter (for source installations)."""
    global mmcif
    
    try:
        import setuptools  # Required by nimporter
    except ImportError:
        raise ImportError("setuptools is required but not installed. Install with: pip install setuptools")
    
    import nimporter
    from . import nim_mmcif as mmcif
    return True

# Try importing the extension
try:
    _try_import_extension()
except ImportError as e:
    _import_error = e
    # Try nimporter as fallback for source installations
    try:
        _try_nimporter_fallback()
    except ImportError as nimporter_error:
        error_msg = (
            "Failed to import nim_mmcif extension.\n"
            f"Direct import error: {_import_error}\n"
            f"Nimporter fallback error: {nimporter_error}\n\n"
            "This can happen if:\n"
            "1. The extension was not properly compiled during installation\n"
            "2. nimporter is not installed (pip install nimporter)\n"
            "3. The Nim compiler is not available for runtime compilation\n"
        )
        raise ImportError(error_msg) from nimporter_error

if mmcif is None:
    raise ImportError("Failed to import nim_mmcif module through any method")


# Helper functions
def _validate_filepath(filepath: str | Path) -> str:
    """Convert path to string and validate it exists."""
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"mmCIF file not found: {filepath}")
    return str(filepath)

def _has_glob_pattern(filepath: str | Path) -> bool:
    """Check if a filepath contains glob patterns."""
    str_path = str(filepath)
    return any(char in str_path for char in ['*', '?', '[', ']'])

def _expand_glob(pattern: str | Path) -> list[Path]:
    """Expand a glob pattern into a list of matching file paths."""
    str_pattern = str(pattern)
    matched_files = glob.glob(str_pattern, recursive=True)
    
    # Filter to only include .mmcif files (case insensitive)
    mmcif_files = [
        Path(f) for f in matched_files 
        if f.lower().endswith(('.mmcif', '.cif'))
    ]
    
    if not mmcif_files:
        raise FileNotFoundError(f"No mmCIF files found matching pattern: {pattern}")
    
    return sorted(mmcif_files)  # Sort for consistent ordering

# Re-export the functions with Python-friendly wrappers
def parse_mmcif(filepath: str | Path, as_dataclass: bool = False) -> dict[str, Any] | dict[str, dict[str, Any]] | MmcifData | dict[str, MmcifData]:
    """
    Parse an mmCIF file or files matching a glob pattern using the Nim backend.

    Args:
        filepath: Path to the mmCIF file or glob pattern.
        as_dataclass: If True, return MmcifData dataclass(es) instead of dict(s).

    Returns:
        Result as dictionary or dataclass.

    Raises:
        FileNotFoundError: If the file doesn't exist or no files match the glob pattern.
        RuntimeError: If parsing fails.
    """
    if _has_glob_pattern(filepath):
        return parse_mmcif_batch(filepath, as_dataclass=as_dataclass)
    
    try:
        result = mmcif.parse_mmcif(_validate_filepath(filepath))
        return dict_to_dataclass(result) if as_dataclass else result
    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to parse mmCIF file: {e}") from e

def get_atom_count(filepath: str | Path) -> int:
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
    try:
        return mmcif.get_atom_count(_validate_filepath(filepath))
    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to get atom count: {e}") from e

def get_atoms(filepath: str | Path) -> list[dict[str, Any]]:
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
    try:
        return mmcif.get_atoms(_validate_filepath(filepath))
    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to get atoms: {e}") from e

def get_atom_positions(filepath: str | Path) -> list[tuple[float, float, float]]:
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
    try:
        return mmcif.get_atom_positions(_validate_filepath(filepath))
    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to get atom positions: {e}") from e

def parse_mmcif_batch(filepaths: list[str | Path] | str | Path, as_dataclass: bool = False) -> list[dict[str, Any]] | dict[str, dict[str, Any]] | list[MmcifData] | dict[str, MmcifData]:
    """
    Parse multiple mmCIF files using the Nim backend.

    Args:
        filepaths: List of paths to mmCIF files, a single path, or a glob pattern.
        as_dataclass: If True, return MmcifData dataclass(es) instead of dict(s).

    Returns:
        Result list or dictionary.

    Raises:
        FileNotFoundError: If any file doesn't exist or no files match glob pattern.
        RuntimeError: If parsing fails for any file.
    """
    if isinstance(filepaths, (str, Path)) and _has_glob_pattern(filepaths):
        matched_files = _expand_glob(filepaths)
        result = {str(p): mmcif.parse_mmcif(str(p)) for p in matched_files}
        return dict_to_dataclass(result) if as_dataclass else result

    if isinstance(filepaths, (str, Path)):
        filepaths = [filepaths]
    
    expanded_paths = []
    has_any_glob = False
    
    for filepath in filepaths:
        if _has_glob_pattern(filepath):
            has_any_glob = True
            expanded_paths.extend(_expand_glob(filepath))
        else:
            expanded_paths.append(Path(_validate_filepath(filepath)))
    
    if has_any_glob:
        result = {str(p): mmcif.parse_mmcif(str(p)) for p in expanded_paths}
        return dict_to_dataclass(result) if as_dataclass else result
    else:
        try:
            str_paths = [str(p) for p in expanded_paths]
            result = mmcif.parse_mmcif_batch(str_paths)
            return dict_to_dataclass(result) if as_dataclass else result
        except Exception as e:
            raise RuntimeError(f"Failed to parse mmCIF files in batch: {e}") from e

# Export public API
__all__ = [
    'parse_mmcif',
    'parse_mmcif_batch',
    'get_atom_count',
    'get_atoms',
    'get_atom_positions',
    'Atom',
    'MmcifData',
    '__version__'
]