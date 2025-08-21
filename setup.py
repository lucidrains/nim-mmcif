"""Setup script for nim-mmcif package."""
import platform
import shutil
import sys
from pathlib import Path

from setuptools import setup, Extension


def find_and_install_binary() -> bool:
    """
    Find and install the appropriate Python binding for the current platform.
    
    Returns:
        True if binary was found and installed, False otherwise.
    """
    system = platform.system()
    py_version = f"{sys.version_info.major}{sys.version_info.minor}"
    
    # Define binary patterns for each platform
    binary_patterns = {
        'Darwin': [
            f'python_bindings.cpython-{py_version}-darwin.so',
            'python_bindings.dylib',
            'python_bindings.so'
        ],
        'Linux': [
            f'python_bindings.cpython-{py_version}-x86_64-linux-gnu.so',
            f'python_bindings.cpython-{py_version}-linux-gnu.so',
            'python_bindings.so'
        ],
        'Windows': [
            f'python_bindings.cp{py_version}-win_amd64.pyd',
            f'python_bindings.cp{py_version}-win32.pyd',
            'python_bindings.pyd',
            'python_bindings.dll'
        ]
    }
    
    patterns = binary_patterns.get(system, ['python_bindings.so'])
    search_paths = [Path('.'), Path('nim_mmcif_modules')]
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
            
        for pattern in patterns:
            binary_path = search_path / pattern
            if binary_path.exists():
                target_dir = Path('python_wrapper')
                target_dir.mkdir(exist_ok=True)
                target_path = target_dir / pattern
                
                try:
                    shutil.copy2(binary_path, target_path)
                    print(f"Successfully installed binary: {pattern}")
                    return True
                except Exception as e:
                    print(f"Warning: Failed to copy binary {pattern}: {e}", file=sys.stderr)
    
    return False


# Attempt to find and install binary
if not find_and_install_binary():
    print(
        "Warning: No pre-compiled binary found. "
        "You may need to compile the Nim extension manually.",
        file=sys.stderr
    )

# Use pyproject.toml for package configuration

ext_modules = [
    Extension(
        "nim_mmcif.python_bindings", 
        sources=[]
    )
]

setup(ext_modules = ext_modules)