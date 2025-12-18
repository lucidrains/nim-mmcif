#!/usr/bin/env python3
"""
Advanced version management script for nim-mmcif.
Supports semantic bumping (patch, minor, major) or manual version setting.
"""

from __future__ import annotations

import sys
import re
import argparse
from pathlib import Path
from typing import NamedTuple

VERSION_FILE = Path("nim_mmcif/_version.py")
NIMBLE_FILE = Path("mmcif.nimble")

class Version(NamedTuple):
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def parse(cls, version_str: str) -> Version:
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_str)
        if not match:
            raise ValueError(f"Invalid version format: {version_str}")
        return cls(*map(int, match.groups()))

def get_current_version() -> Version:
    """Read the current version from the centralized version file."""
    if not VERSION_FILE.exists():
        raise FileNotFoundError(f"Version file not found: {VERSION_FILE}")
    
    content = VERSION_FILE.read_text()
    match = re.search(r'__version__ = "([^"]+)"', content)
    if not match:
        raise ValueError(f"Could not find version string in {VERSION_FILE}")
    
    return Version.parse(match.group(1))

def bump_version(current: Version, bump_type: str) -> Version:
    """Bump the version based on semantic rules."""
    if bump_type == "patch":
        return Version(current.major, current.minor, current.patch + 1)
    elif bump_type == "minor":
        return Version(current.major, current.minor + 1, 0)
    elif bump_type == "major":
        return Version(current.major + 1, 0, 0)
    else:
        # Assume it's a version string
        return Version.parse(bump_type)

def update_file(path: Path, pattern: str, replacement: str, dry_run: bool = False):
    """Update a file if the pattern matches and content changes."""
    if not path.exists():
        print(f"Warning: {path} not found, skipping.")
        return

    content = path.read_text()
    new_content = re.sub(pattern, replacement, content)

    if content == new_content:
        print(f"[-] {path.name}: No changes needed (already at correct version).")
        return

    if dry_run:
        print(f"[DRY RUN] Would update {path.name} to new version.")
    else:
        path.write_text(new_content)
        print(f"[OK] Updated {path.name}")

def main():
    parser = argparse.ArgumentParser(description="Update project version numbers.")
    parser.add_argument(
        "action", 
        help="One of: 'patch', 'minor', 'major', or a specific version string (X.Y.Z)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would change without applying it"
    )
    
    args = parser.parse_args()

    try:
        current_version = get_current_version()
        print(f"Current version: {current_version}")
        
        new_version = bump_version(current_version, args.action)
        print(f"New version:     {new_version}")

        # Update nim_mmcif/_version.py
        update_file(
            VERSION_FILE,
            r'__version__ = "[^"]+"',
            f'__version__ = "{new_version}"',
            args.dry_run
        )

        # Update mmcif.nimble
        update_file(
            NIMBLE_FILE,
            r'version\s*=\s*"[^"]+"',
            f'version       = "{new_version}"',
            args.dry_run
        )

        if not args.dry_run:
            print(f"\nSuccessfully updated version to {new_version}")
        else:
            print("\nDry run completed. No files were modified.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()