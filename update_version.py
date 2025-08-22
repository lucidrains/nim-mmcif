#!/usr/bin/env python3
"""
Script to update version number across all project files.
Usage: python update_version.py <new_version>
"""

import sys
import re
from pathlib import Path


def update_version(new_version: str):
    """Update version in all project files."""
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print(f"Error: Invalid version format '{new_version}'. Use X.Y.Z format.")
        sys.exit(1)
    
    files_to_update = {
        'nim_mmcif/_version.py': {
            'pattern': r'__version__ = "[^"]+"',
            'replacement': f'__version__ = "{new_version}"'
        },
        'mmcif.nimble': {
            'pattern': r'version\s*=\s*"[^"]+"',
            'replacement': f'version       = "{new_version}"'
        }
    }
    
    for filepath, config in files_to_update.items():
        path = Path(filepath)
        if not path.exists():
            print(f"Warning: {filepath} not found")
            continue
        
        content = path.read_text()
        updated_content = re.sub(config['pattern'], config['replacement'], content)
        
        if content != updated_content:
            path.write_text(updated_content)
            print(f"Updated {filepath} to version {new_version}")
        else:
            print(f"No changes needed in {filepath}")
    
    print(f"\nVersion updated to {new_version}")
    print("The version in pyproject.toml is now dynamically read from nim_mmcif/_version.py")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_version.py <new_version>")
        print("Example: python update_version.py 0.0.12")
        sys.exit(1)
    
    update_version(sys.argv[1])