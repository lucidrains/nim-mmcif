"""Pytest configuration with automatic Nim extension building."""

import subprocess
import sys
from pathlib import Path


def pytest_sessionstart(session):
    """Build Nim extension before running tests."""
    project_root = Path(__file__).parent
    build_script = project_root / "build_nim.py"
    
    if not build_script.exists():
        return
    
    print("Building Nim extension...")
    
    try:
        result = subprocess.run(
            [sys.executable, str(build_script)],
            capture_output=True,
            text=True,
            cwd=str(project_root)
        )
        
        if result.returncode != 0:
            print(result.stderr or result.stdout)
            raise RuntimeError(f"Failed to build Nim extension")
        
        print("✓ Nim extension built successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        raise