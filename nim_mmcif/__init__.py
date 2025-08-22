"""nim-mmcif: Fast mmCIF parser using Nim via nimporter."""


try:
    # First check if setuptools is available (required by nimporter)
    try:
        import setuptools
    except ImportError:
        raise ImportError(
            "setuptools is required but not installed. "
            "Please install it with: pip install setuptools"
        )
    
    # Check if we have a placeholder extension (created during CI build without Nim)
    from pathlib import Path
    placeholder_marker = Path(__file__).parent / '.placeholder_extension'
    if placeholder_marker.exists():
        print("Note: nim-mmcif was built without Nim compiler. Runtime compilation will be attempted.")
    
    # Enable nimporter to compile and import .nim files
    import nimporter

    # Import the Nim module directly
    # Note: nimporter.build_nim_extensions() is only needed during setup/build,
    # not at runtime. The import hooks are automatically installed when nimporter is imported.
    import nim_mmcif.nim_mmcif as mmcif

    # Re-export the functions with Python-friendly wrappers
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

    __version__ = '0.0.7'

except ImportError as e:
    # Fallback error message if nimporter is not installed
    import sys

    # Check for specific missing dependencies
    missing_deps = []
    
    # Check setuptools first (required by nimporter)
    try:
        import setuptools
    except ImportError:
        missing_deps.append("setuptools")
    
    # Then check nimporter
    try:
        import nimporter
    except ImportError:
        missing_deps.append("nimporter")

    error_msg = "Failed to import nim-mmcif. "

    if missing_deps:
        error_msg += f"Missing dependencies: {', '.join(missing_deps)}\n"
        error_msg += f"Please install with: pip install {' '.join(missing_deps)}\n\n"

    error_msg += (
        "Requirements:\n"
        "1. setuptools: pip install setuptools\n"
        "2. nimporter: pip install nimporter\n"
        "3. Nim compiler: https://nim-lang.org/install.html\n"
        "4. nimpy: nimble install nimpy\n"
    )

    # Only show original error if it's not about known missing dependencies
    if not any(dep in str(e) for dep in ['setuptools', 'nimporter']):
        error_msg += f"\nOriginal error: {e}"

    raise ImportError(error_msg) from e

