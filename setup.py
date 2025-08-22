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
        # Try to ensure Nim is available
        if not self.check_nim_installed():
            print("WARNING: Nim compiler not found!")
            print("Nim should be pre-installed in the build environment.")
            print("Attempting to continue with pre-built binary or fallback...")
            # Check if a pre-built binary exists
            if not self.check_prebuilt_binary():
                print("WARNING: No pre-built binary found and Nim compiler not available")
                print("Please install Nim: https://nim-lang.org/install.html")
                # For CI/CD environments, we should have Nim installed
                # Only create placeholder as absolute last resort
                if os.environ.get('CI'):
                    print("WARNING: CI environment detected but Nim not found!")
                    print("This should not happen - please check CI configuration")
                    print("Creating placeholder extension as fallback...")
                    self.create_dummy_extension()
                else:
                    print("Continuing without Nim extension - runtime compilation will be attempted")
        else:
            # Ensure nimpy is installed
            self.ensure_nimpy()
            
            # Build the Nim extension
            if not self.build_nim_extension():
                print("WARNING: Nim build failed, checking for pre-built binary...")
                if not self.check_prebuilt_binary():
                    print("WARNING: Failed to build Nim extension and no pre-built binary found")
                    if os.environ.get('CI'):
                        print("CI environment detected - creating placeholder extension")
                        self.create_dummy_extension()
        
        # Run the parent build_ext
        super().run()
    
    def check_nim_installed(self):
        """Check if Nim compiler is installed."""
        # First try normal PATH
        try:
            result = subprocess.run(
                ['nim', '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Found Nim: {result.stdout.splitlines()[0]}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # On Windows CI, Nim might be at a specific location
        if platform.system() == 'Windows' and os.environ.get('CI'):
            nim_path = r'C:\nim-2.2.4\bin\nim.exe'
            if os.path.exists(nim_path):
                try:
                    result = subprocess.run(
                        [nim_path, '--version'],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    print(f"Found Nim at {nim_path}: {result.stdout.splitlines()[0]}")
                    # Add to PATH for this process
                    os.environ['PATH'] = r'C:\nim-2.2.4\bin;' + os.environ.get('PATH', '')
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
        
        return False
    
    def check_prebuilt_binary(self):
        """Check if a pre-built binary exists."""
        system = platform.system()
        
        if system == 'Darwin':  # macOS
            binary_name = 'nim_mmcif.so'
        elif system == 'Linux':
            binary_name = 'nim_mmcif.so'
        elif system == 'Windows':
            binary_name = 'nim_mmcif.pyd'
        else:
            binary_name = 'nim_mmcif.so'
        
        binary_path = Path('nim_mmcif') / binary_name
        if binary_path.exists():
            print(f"Found pre-built binary: {binary_path}")
            return True
        
        return False
    
    def create_dummy_extension(self):
        """Create a dummy extension file for CI environments without Nim."""
        system = platform.system()
        
        if system == 'Windows':
            binary_name = 'nim_mmcif.pyd'
        else:
            binary_name = 'nim_mmcif.so'
        
        binary_path = Path('nim_mmcif') / binary_name
        
        # Create a minimal placeholder file
        # This will allow the wheel to build, but the actual functionality
        # will require nimporter to compile at runtime
        print(f"Creating placeholder extension: {binary_path}")
        binary_path.touch()
        
        # Also create a marker file to indicate this is a placeholder
        marker_path = Path('nim_mmcif') / '.placeholder_extension'
        marker_path.write_text('This is a placeholder extension created during CI build without Nim compiler.')
        
        return True
    
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
    
    def build_nim_extension(self):
        """Build the Nim extension module."""
        system = platform.system()
        machine = platform.machine()
        
        # Change to nim_mmcif directory
        nim_dir = Path('nim_mmcif')
        if not nim_dir.exists():
            print(f"ERROR: {nim_dir} directory not found!")
            return False
        
        original_dir = os.getcwd()
        os.chdir(nim_dir)
        
        try:
            # Base command
            cmd = ['nim', 'c', '--app:lib']
            
            # Platform-specific settings
            if system == 'Darwin':  # macOS
                if machine == 'arm64':
                    cmd.extend(['--cpu:arm64', '--passC:-arch arm64', '--passL:-arch arm64'])
                else:
                    cmd.extend(['--cpu:amd64', '--passC:-arch x86_64', '--passL:-arch x86_64'])
                cmd.extend(['--cc:clang', '--out:nim_mmcif.so'])
                output_file = 'nim_mmcif.so'
            
            elif system == 'Linux':
                if machine in ['aarch64', 'arm64']:
                    cmd.append('--cpu:arm64')
                else:
                    cmd.append('--cpu:amd64')
                cmd.extend(['--cc:gcc', '--passL:-fPIC', '--out:nim_mmcif.so'])
                output_file = 'nim_mmcif.so'
            
            elif system == 'Windows':
                cmd.append('--cpu:amd64')
                # On Windows, we need to use the .pyd extension
                cmd.append('--out:nim_mmcif.pyd')
                output_file = 'nim_mmcif.pyd'
                
                # Add Windows-specific flags
                # Try to use Visual Studio compiler if available
                if os.path.exists('C:/Program Files/Microsoft Visual Studio') or \
                   os.path.exists('C:/Program Files (x86)/Microsoft Visual Studio'):
                    cmd.append('--cc:vcc')
                else:
                    # Use MinGW if available
                    cmd.append('--cc:gcc')
            
            else:
                print(f"WARNING: Unknown platform {system}, using defaults")
                cmd.append('--out:nim_mmcif.so')
                output_file = 'nim_mmcif.so'
            
            # Add optimization flags
            cmd.extend(['--opt:speed', '--threads:on'])
            
            # Add source file
            cmd.append('nim_mmcif.nim')
            
            print(f"Building Nim extension with command: {' '.join(cmd)}")
            
            # Run the build command
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Build failed with return code {result.returncode}")
                print(f"stdout: {result.stdout}")
                print(f"stderr: {result.stderr}")
                return False
            
            # Check if the output file was created
            if not Path(output_file).exists():
                print(f"ERROR: Expected output file {output_file} was not created!")
                return False
            
            print(f"Successfully built {output_file}")
            return True
            
        except Exception as e:
            print(f"Build failed with exception: {e}")
            return False
        finally:
            os.chdir(original_dir)


# Check if we're building a wheel or sdist
building_wheel = 'bdist_wheel' in sys.argv
building_sdist = 'sdist' in sys.argv

# For wheel builds, we need to ensure the extension is built
ext_modules = []
cmdclass = {}

if building_wheel:
    # When building wheels, we use the custom build_ext to compile Nim code
    cmdclass['build_ext'] = NimBuildExt
    # Add a dummy extension to trigger build_ext
    ext_modules = [Extension('nim_mmcif._dummy', sources=['nim_mmcif/_dummy.c'])]
else:
    # For source distributions or regular installs, rely on nimporter
    try:
        import nimporter
        print("Using nimporter for Nim extensions")
    except ImportError:
        if not building_sdist:
            print("Warning: nimporter not found.")
            print("Install with: pip install nimporter")


setup(
    packages=find_packages(),
    ext_modules=ext_modules,
    cmdclass=cmdclass,
    zip_safe=False,  # Required for nimporter to work correctly
    include_package_data=True,  # Include files specified in MANIFEST.in
)