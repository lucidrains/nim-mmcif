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

# First, try to import the pre-compiled extension directly
mmcif = None
_import_error = None

try:
    # Try direct import of the compiled extension
    # This should work if the extension was pre-compiled during wheel building
    # The extension is compiled as nim_mmcif.pyd (Windows) or nim_mmcif.so (Unix)
    # and placed in the nim_mmcif package directory
    
    # Use importlib to dynamically load the extension module
    import importlib.util
    import os
    
    # Determine the extension filename based on platform
    if platform.system() == 'Windows':
        ext_name = 'nim_mmcif.pyd'
    else:
        ext_name = 'nim_mmcif.so'
    
    # Full path to the extension
    ext_path = Path(__file__).parent / ext_name
    
    # On Windows, also check for _dummy.*.pyd files that might exist
    # but we need the real nim_mmcif.pyd
    if platform.system() == 'Windows' and not ext_path.exists():
        # List all .pyd files in the directory for debugging
        pyd_files = list(Path(__file__).parent.glob('*.pyd'))
        if pyd_files:
            print(f"Found .pyd files: {[f.name for f in pyd_files]}")
            # If there's a _dummy.*.pyd but no nim_mmcif.pyd, that's a build issue
            if any('_dummy' in f.name for f in pyd_files) and not any('nim_mmcif' in f.name for f in pyd_files):
                raise ImportError(
                    f"Build error: Found dummy extension but not the actual nim_mmcif.pyd. "
                    f"The Nim extension was not properly compiled during wheel building."
                )
    
    if ext_path.exists():
        # On Windows, we need to handle DLL loading more carefully
        if platform.system() == 'Windows':
            # Windows sometimes needs help finding dependent DLLs
            # Add the package directory to DLL search path
            import os
            package_dir = Path(__file__).parent
            
            # For Python 3.8+, use os.add_dll_directory if available
            if hasattr(os, 'add_dll_directory'):
                try:
                    with os.add_dll_directory(str(package_dir)):
                        # Load within the context manager
                        pass
                except Exception as dll_err:
                    # Ignore errors, will try other methods
                    pass
            
            # Also try adding to PATH temporarily
            old_path = os.environ.get('PATH', '')
            try:
                os.environ['PATH'] = str(package_dir) + os.pathsep + old_path
            except Exception:
                pass
            
            # On Windows, also try to set up ctypes CDLL loading
            try:
                import ctypes
                # Pre-load any required system libraries
                # This helps when the extension has dependencies
                try:
                    ctypes.CDLL('msvcrt.dll')
                except:
                    pass
            except:
                pass
        
        # Load the extension directly using importlib
        spec = importlib.util.spec_from_file_location("nim_mmcif_ext", ext_path)
        if spec and spec.loader:
            mmcif = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mmcif)
                # print(f"Successfully loaded pre-compiled extension from {ext_path}")
            except ImportError as load_err:
                # On Windows, provide more detailed error information
                if platform.system() == 'Windows' and "DLL load failed" in str(load_err):
                    error_msg = (
                        f"Failed to load Windows extension: {load_err}\n\n"
                        "This is typically caused by missing runtime dependencies.\n"
                        "The extension was compiled but cannot find required DLLs.\n\n"
                        "Possible solutions:\n"
                        "1. Install Visual C++ Redistributable for Visual Studio\n"
                        "2. Ensure the wheel was built with static linking\n"
                        "3. Install from source with Nim compiler available\n"
                    )
                    raise ImportError(error_msg) from load_err
                else:
                    raise
        else:
            raise ImportError(f"Could not create module spec for {ext_path}")
    else:
        raise ImportError(f"Extension file not found: {ext_path}")
    
except ImportError as e:
    _import_error = e
    # Pre-compiled extension not found
    # Check if this is a placeholder build (CI without Nim)
    placeholder_marker = Path(__file__).parent / '.placeholder_extension'
    if placeholder_marker.exists():
        # This is a placeholder build - extension compilation failed during wheel building
        error_msg = (
            f"Failed to import nim_mmcif extension: {_import_error}\n\n"
            "This wheel was built without a properly compiled Nim extension.\n"
            "This is likely a CI/build environment issue.\n\n"
            "To fix this:\n"
            "1. Install from source with Nim compiler available\n"
            "2. Or wait for a properly built wheel to be published\n"
        )
        raise ImportError(error_msg) from e
    
    # Try nimporter as fallback for source installations
    try:
        # First check if setuptools is available (required by nimporter)
        try:
            import setuptools
        except ImportError:
            raise ImportError(
                "setuptools is required but not installed. "
                "Please install it with: pip install setuptools"
            )
        
        # Enable nimporter to compile and import .nim files
        import nimporter

        # Import the Nim module via nimporter
        # This will compile nim_mmcif.nim on the fly if needed
        from . import nim_mmcif as mmcif
        
    except ImportError as nimporter_error:
        # If both methods fail, provide a helpful error message
        error_msg = (
            "Failed to import nim_mmcif extension.\n"
            f"Direct import error: {_import_error}\n"
            f"Nimporter fallback error: {nimporter_error}\n\n"
            "This can happen if:\n"
            "1. The extension was not properly compiled during installation\n"
            "2. nimporter is not installed (pip install nimporter)\n"
            "3. The Nim compiler is not available for runtime compilation\n\n"
            "For wheels, the extension should be pre-compiled.\n"
            "For source installations, you need Nim and nimporter installed."
        )
        raise ImportError(error_msg) from nimporter_error

# If we got here, mmcif should be imported successfully
if mmcif is None:
    raise ImportError("Failed to import nim_mmcif module through any method")


# Helper function to validate file path
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
        If as_dataclass is False:
            - Single file: Dictionary containing parsed mmCIF data with 'atoms' key.
            - Glob pattern: Dictionary mapping file paths to parsed mmCIF data.
        If as_dataclass is True:
            - Single file: MmcifData instance with typed atom access.
            - Glob pattern: Dictionary mapping file paths to MmcifData instances.

    Raises:
        FileNotFoundError: If the file doesn't exist or no files match the glob pattern.
        RuntimeError: If parsing fails.
    """
    # Check if the filepath contains glob patterns
    if _has_glob_pattern(filepath):
        # Expand glob pattern and parse each file
        matched_files = _expand_glob(filepath)
        result = {}
        for file_path in matched_files:
            try:
                result[str(file_path)] = mmcif.parse_mmcif(str(file_path))
            except Exception as e:
                raise RuntimeError(f"Failed to parse mmCIF file {file_path}: {e}") from e
        return dict_to_dataclass(result) if as_dataclass else result
    else:
        # Single file case
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
                  If a single string with glob patterns is provided, it will be expanded.
        as_dataclass: If True, return MmcifData dataclass(es) instead of dict(s).

    Returns:
        If as_dataclass is False:
            - No glob patterns: List of dictionaries, each containing parsed mmCIF data.
            - With glob patterns: Dictionary mapping file paths to parsed mmCIF data.
        If as_dataclass is True:
            - No glob patterns: List of MmcifData instances with typed atom access.
            - With glob patterns: Dictionary mapping file paths to MmcifData instances.

    Raises:
        FileNotFoundError: If any file doesn't exist or no files match glob pattern.
        RuntimeError: If parsing fails for any file.
    """
    # Handle single filepath (string or Path) that might be a glob
    if isinstance(filepaths, (str, Path)):
        if _has_glob_pattern(filepaths):
            # Expand glob and return as dict
            matched_files = _expand_glob(filepaths)
            result = {}
            for file_path in matched_files:
                try:
                    result[str(file_path)] = mmcif.parse_mmcif(str(file_path))
                except Exception as e:
                    raise RuntimeError(f"Failed to parse mmCIF file {file_path}: {e}") from e
            return dict_to_dataclass(result) if as_dataclass else result
        else:
            # Single file, treat as batch of one
            filepaths = [filepaths]
    
    # Check if any filepath in the list contains glob patterns
    expanded_paths = []
    has_any_glob = False
    path_mapping = {}  # Maps expanded path to original pattern
    
    for filepath in filepaths:
        if _has_glob_pattern(filepath):
            has_any_glob = True
            matched = _expand_glob(filepath)
            for matched_path in matched:
                expanded_paths.append(matched_path)
                path_mapping[str(matched_path)] = str(matched_path)
        else:
            validated = _validate_filepath(filepath)
            expanded_paths.append(Path(validated))
            path_mapping[validated] = validated
    
    # If glob patterns were used, return dict format
    if has_any_glob:
        result = {}
        for path in expanded_paths:
            try:
                result[str(path)] = mmcif.parse_mmcif(str(path))
            except Exception as e:
                raise RuntimeError(f"Failed to parse mmCIF file {path}: {e}") from e
        return dict_to_dataclass(result) if as_dataclass else result
    else:
        # No glob patterns, use original batch processing
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