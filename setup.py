"""Setup script for nim-mmcif package using nimporter."""
import os
import platform
import subprocess
import sys
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext


class NimBuildExt(build_ext):
    """Custom build extension for compiling Nim code on different platforms."""
    
    def run(self):
        # Check if Nim is installed
        try:
            subprocess.run(['nim', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: Nim compiler not found. Please install Nim to build from source.")
            print("Visit: https://nim-lang.org/install.html")
        
        # Check if nimpy is installed
        try:
            result = subprocess.run(['nimble', 'list', '--installed'], 
                                  capture_output=True, text=True, check=True)
            if 'nimpy' not in result.stdout:
                print("Installing nimpy...")
                subprocess.run(['nimble', 'install', 'nimpy', '-y'], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: nimble not found or nimpy not installed.")
        
        # Run the parent build_ext
        super().run()


# Check if nimporter is available for building
try:
    import nimporter
    nim_extensions = []  # nimporter handles compilation automatically
except ImportError:
    print("Warning: nimporter not found. Install with: pip install nimporter")
    print("Nim extensions will need to be compiled manually.")
    nim_extensions = []


setup(
    packages=find_packages(),
    ext_modules=nim_extensions,
    cmdclass={'build_ext': NimBuildExt},
    zip_safe=False,  # Required for nimporter to work correctly
)