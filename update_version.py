#!/usr/bin/env python3
"""
Advanced version management script for nim-mmcif.
Supports semantic bumping (patch, minor, major) or manual version setting.
Includes Git integration for automated commits and tagging.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple, Optional

# Constants
VERSION_FILE = Path("nim_mmcif/_version.py")
NIMBLE_FILE = Path("mmcif.nimble")

class Version(NamedTuple):
    """Semantic versioning container."""
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def parse(cls, version_str: str) -> Version:
        """Parse a version string X.Y.Z."""
        match = re.match(r'^v?(\d+)\.(\d+)\.(\d+)$', version_str)
        if not match:
            raise ValueError(f"Invalid version format: {version_str}. Expected X.Y.Z")
        return cls(*map(int, match.groups()))

class VersionManager:
    """Manages version updates across multiple files and Git."""

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose

    def log(self, message: str, level: str = "INFO"):
        """Simple logging with status prefixes."""
        prefix = {
            "INFO":  "[\033[94mINFO\033[0m]",
            "OK":    "[\033[92m OK \033[0m]",
            "SKIP":  "[\033[93mSKIP\033[0m]",
            "DRY":   "[\033[95mDRY \033[0m]",
            "ERROR": "[\033[91mERR \033[0m]"
        }.get(level, f"[{level}]")
        
        # Strip colors if not a TTY or if requested
        if not sys.stdout.isatty():
            prefix = f"[{level}]"
            
        print(f"{prefix} {message}")

    def get_current_version(self) -> Version:
        """Read the current version from the centralized version file."""
        if not VERSION_FILE.exists():
            raise FileNotFoundError(f"Version file not found: {VERSION_FILE}")
        
        content = VERSION_FILE.read_text()
        match = re.search(r'__version__ = "([^"]+)"', content)
        if not match:
            raise ValueError(f"Could not find __version__ string in {VERSION_FILE}")
        
        return Version.parse(match.group(1))

    def bump_version(self, current: Version, action: str) -> Version:
        """Calculate the next version based on the action."""
        if action == "patch":
            return Version(current.major, current.minor, current.patch + 1)
        elif action == "minor":
            return Version(current.major, current.minor + 1, 0)
        elif action == "major":
            return Version(current.major + 1, 0, 0)
        else:
            # Assume it's a specific version string
            return Version.parse(action)

    def update_file(self, path: Path, pattern: str, replacement_fmt: str, new_version: Version):
        """Update a version string in a specific file using regex."""
        if not path.exists():
            self.log(f"{path} not found, skipping.", "SKIP")
            return

        content = path.read_text()
        replacement = replacement_fmt.format(version=new_version)
        new_content = re.sub(pattern, replacement, content)

        if content == new_content:
            self.log(f"{path.name} already at version {new_version}.", "SKIP")
            return

        if self.dry_run:
            self.log(f"Would update {path.name} to {new_version}", "DRY")
        else:
            path.write_text(new_content)
            self.log(f"Updated {path.name} to {new_version}", "OK")

    def run_git_command(self, cmd: list[str]) -> bool:
        """Run a git command and return success."""
        if self.dry_run:
            self.log(f"Would run: git {' '.join(cmd)}", "DRY")
            return True
        
        try:
            subprocess.run(["git"] + cmd, check=True, capture_output=not self.verbose)
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Git command failed: {e}", "ERROR")
            return False

    def handle_git(self, new_version: Version, tag: bool = False, commit: bool = False):
        """Perform Git operations related to the version bump."""
        if not (commit or tag):
            return

        # Check if we are in a git repo
        if not Path(".git").exists():
            self.log("Not a Git repository, skipping Git operations.", "SKIP")
            return

        if commit:
            self.log(f"Committing version bump to {new_version}...")
            # Stage only the version files if they exist
            files_to_add = [str(f) for f in [VERSION_FILE, NIMBLE_FILE] if f.exists()]
            if files_to_add:
                self.run_git_command(["add"] + files_to_add)
                self.run_git_command(["commit", "-m", f"chore: bump version to {new_version}"])
                self.log(f"Committed changes for v{new_version}", "OK")

        if tag:
            tag_name = f"v{new_version}"
            self.log(f"Tagging with {tag_name}...")
            if self.run_git_command(["tag", "-a", tag_name, "-m", f"Release {tag_name}"]):
                self.log(f"Created tag {tag_name}", "OK")

def main():
    parser = argparse.ArgumentParser(description="Update project version numbers and manage Git tags.")
    parser.add_argument(
        "action", 
        help="Target version: 'patch', 'minor', 'major', or a specific 'X.Y.Z'"
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true", 
        help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--commit", "-c",
        action="store_true",
        help="Commit the version bump in Git"
    )
    parser.add_argument(
        "--tag", "-t",
        action="store_true",
        help="Create a Git tag for the new version"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    vm = VersionManager(dry_run=args.dry_run, verbose=args.verbose)

    try:
        current = vm.get_current_version()
        new_version = vm.bump_version(current, args.action)
        
        vm.log(f"Bumping version: {current} -> {new_version}")

        # 1. Update nim_mmcif/_version.py
        vm.update_file(
            VERSION_FILE,
            r'__version__ = "[^"]+"',
            '__version__ = "{version}"',
            new_version
        )

        # 2. Update mmcif.nimble
        # Handles 'version = "..."' or 'version="..."'
        vm.update_file(
            NIMBLE_FILE,
            r'version\s*=\s*"[^"]+"',
            'version       = "{version}"',
            new_version
        )

        # 3. Git Operations
        vm.handle_git(new_version, tag=args.tag, commit=args.commit)

        if args.dry_run:
            vm.log("Dry run complete. No files were changed.", "INFO")
        else:
            vm.log(f"Successfully updated to {new_version}", "INFO")

    except Exception as e:
        vm.log(str(e), "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()