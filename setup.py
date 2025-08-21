"""Setup script for nim-mmcif package."""
import os
import platform
import subprocess
import sys
from pathlib import Path
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext


class NimBuildExt(build_ext):
    """Custom build extension for compiling Nim code."""
    
    def run(self):
        # Copy mmcif.nim to nim_mmcif directory if needed
        self.copy_mmcif_source()
        
        # Try to ensure Nim is available
        if not self.check_nim_installed():
            self.install_nim()
        
        # Ensure nimpy is installed
        self.ensure_nimpy()
        
        # Run the parent build_ext
        super().run()
    
    def copy_mmcif_source(self):
        """Ensure mmcif.nim exists in nim_mmcif directory."""
        # No longer needed since files are already in nim_mmcif/
        pass
    
    def check_nim_installed(self):
        """Check if Nim compiler is installed."""
        try:
            result = subprocess.run(
                ['nim', '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Found Nim: {result.stdout.split()[0]}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def install_nim(self):
        """Attempt to install Nim if not found."""
        print("Nim compiler not found. Attempting to install...")
        
        system = platform.system()
        if system == "Linux":
            try:
                # Try to install via choosenim
                subprocess.run(
                    "curl https://nim-lang.org/choosenim/init.sh -sSf | sh -s -- -y",
                    shell=True,
                    check=True
                )
                # Add to PATH
                os.environ["PATH"] = f"{os.environ['HOME']}/.nimble/bin:{os.environ['PATH']}"
            except subprocess.CalledProcessError:
                print("Failed to install Nim automatically.")
                print("Please install Nim manually: https://nim-lang.org/install.html")
        elif system == "Darwin":  # macOS
            try:
                subprocess.run(['brew', 'install', 'nim'], check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("Failed to install Nim via Homebrew.")
                print("Please install Nim manually: brew install nim")
        elif system == "Windows":
            print("Please install Nim manually on Windows:")
            print("Visit: https://nim-lang.org/install_windows.html")
        else:
            print(f"Unsupported system: {system}")
            print("Please install Nim manually: https://nim-lang.org/install.html")
    
    def ensure_nimpy(self):
        """Ensure nimpy is installed."""
        try:
            # Check if nimpy is installed
            result = subprocess.run(
                ['nimble', 'list', '--installed'],
                capture_output=True,
                text=True,
                check=True
            )
            
            if 'nimpy' not in result.stdout:
                print("Installing nimpy...")
                subprocess.run(['nimble', 'install', 'nimpy', '-y'], check=True)
                print("nimpy installed successfully")
            else:
                print("nimpy is already installed")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Warning: Could not check/install nimpy: {e}")
            print("You may need to install it manually: nimble install nimpy")


# Check if we're building a wheel or sdist
building_wheel = 'bdist_wheel' in sys.argv
building_sdist = 'sdist' in sys.argv

# Configure extensions based on build type
ext_modules = []

# Only try to import nimporter if we're actually building
if building_wheel or not (building_sdist or '--help' in sys.argv):
    try:
        import nimporter
        # Let nimporter handle the Nim extensions
        print("Using nimporter for Nim extensions")
    except ImportError:
        print("Warning: nimporter not found.")
        print("Install with: pip install nimporter")
        print("Nim extensions will need to be compiled manually.")


setup(
    packages=find_packages(),
    ext_modules=ext_modules,
    cmdclass={'build_ext': NimBuildExt},
    zip_safe=False,  # Required for nimporter to work correctly
    include_package_data=True,  # Include files specified in MANIFEST.in
)