"""Python wrapper for nim-mmcif using native Nim bindings."""
import importlib.util
import platform
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

# Constants
BINARY_NAME = "python_bindings"
BINARY_EXTENSIONS = {
    'Darwin': ['.so', '.dylib'],
    'Linux': ['.so'],
    'Windows': ['.pyd', '.dll']
}


def _find_binary() -> Path:
    """
    Find the compiled binary module.
    
    Returns:
        Path to the binary module.
        
    Raises:
        ImportError: If no binary module is found.
    """
    system = platform.system()
    extensions = BINARY_EXTENSIONS.get(system, ['.so'])
    
    search_dirs = [
        Path(__file__).parent,
        Path(__file__).parent.parent,
        Path(__file__).parent / 'platform_modules',
    ]
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
            
        for ext in extensions:
            pattern = f"{BINARY_NAME}*{ext}"
            for binary_path in search_dir.glob(pattern):
                if binary_path.is_file():
                    return binary_path
    
    raise ImportError(
        f"Could not find {BINARY_NAME} binary module. "
        f"Searched in: {[str(d) for d in search_dirs]}"
    )


def _load_binary_module():
    """
    Load the binary module with proper error handling.
    
    Returns:
        The loaded module.
        
    Raises:
        ImportError: If the module cannot be loaded.
    """
    try:
        # Try standard import first
        import python_bindings
        return python_bindings
    except ImportError:
        pass
    
    # Find and load the binary directly
    try:
        binary_path = _find_binary()
    except ImportError as e:
        # Provide build instructions
        build_cmd = "nim c --app:lib --out:python_wrapper/python_bindings"
        if platform.system() == 'Darwin':
            build_cmd += ".so"
        elif platform.system() == 'Linux':
            build_cmd += ".so"
        elif platform.system() == 'Windows':
            build_cmd += ".pyd"
        else:
            build_cmd += ".so"
        build_cmd += " src/python_bindings.nim"
        
        raise ImportError(
            f"No compiled binary found. Build with:\n  {build_cmd}\n"
            f"Ensure Nim and nimpy are installed first."
        ) from e
    
    # Load the module from file
    spec = importlib.util.spec_from_file_location(BINARY_NAME, binary_path)
    if not spec or not spec.loader:
        raise ImportError(f"Could not load spec for {binary_path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[BINARY_NAME] = module
    
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        error_msg = f"Failed to load {binary_path}: {e}"
        if platform.system() == 'Windows':
            error_msg += "\nOn Windows, ensure Visual C++ Redistributables are installed."
        raise ImportError(error_msg) from e
    
    return module


# Load the binary module
nim_mmcif = _load_binary_module()


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
        return nim_mmcif.parse_mmcif(str(filepath))
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
        return nim_mmcif.get_atom_count(str(filepath))
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
        return nim_mmcif.get_atoms(str(filepath))
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
        return nim_mmcif.get_atom_positions(str(filepath))
    except Exception as e:
        raise RuntimeError(f"Failed to get atom positions: {e}") from e