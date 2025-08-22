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
        # Debug output for CI
        if os.environ.get('CI'):
            print("=" * 60)
            print("CI Environment Debug Info")
            print(f"Platform: {platform.system()}")
            print(f"Machine: {platform.machine()}")
            print(f"PATH: {os.environ.get('PATH', 'NOT SET')}")
            print(f"Current dir: {os.getcwd()}")
            print("=" * 60)
        
        # Try to ensure Nim is available
        if not self.check_nim_installed():
            print("ERROR: Nim compiler not found!")
            print("Nim is required to build this extension.")
            
            # Check if a pre-built binary exists
            if self.check_prebuilt_binary():
                print("Using pre-built binary.")
                return
            
            # For CI/CD environments, this is a critical error
            if os.environ.get('CI'):
                print("ERROR: CI environment detected but Nim not found!")
                print("Please check CI configuration - Nim should be installed at C:\\nim-2.2.4")
                raise RuntimeError("Nim compiler not found in CI environment")
            else:
                print("Please install Nim from: https://nim-lang.org/install.html")
                print("Or install from source with Nim and nimporter available")
                raise RuntimeError("Nim compiler not found")
        else:
            # Ensure nimpy is installed
            self.ensure_nimpy()
            
            # Build the Nim extension
            if not self.build_nim_extension():
                print("ERROR: Nim build failed!")
                if self.check_prebuilt_binary():
                    print("Using pre-built binary as fallback.")
                else:
                    raise RuntimeError("Failed to build Nim extension")
        
        # Run the parent build_ext
        super().run()
        
        # After building, ensure Windows .pyd file is in the build directory
        if platform.system() == 'Windows':
            self.copy_windows_extension()
    
    def check_nim_installed(self):
        """Check if Nim compiler is installed."""
        # On Windows, prioritize checking known installation paths first
        if platform.system() == 'Windows':
            # Check multiple possible Nim locations on Windows
            # Put CI path first since that's what we're using
            possible_paths = [
                r'C:\nim-2.2.4\bin\nim.exe',  # CI installation path (CHECK THIS FIRST!)
                r'C:\tools\nim\bin\nim.exe',  # Chocolatey installation
                r'C:\Program Files\nim\bin\nim.exe',
                os.path.expanduser(r'~\.nimble\bin\nim.exe'),  # User installation
            ]
            
            for nim_path in possible_paths:
                if os.path.exists(nim_path):
                    try:
                        result = subprocess.run(
                            [nim_path, '--version'],
                            capture_output=True,
                            text=True,
                            check=True
                        )
                        print(f"Found Nim at {nim_path}: {result.stdout.splitlines()[0]}")
                        # Add to PATH for this process and child processes
                        nim_bin_dir = os.path.dirname(nim_path)
                        os.environ['PATH'] = nim_bin_dir + os.pathsep + os.environ.get('PATH', '')
                        # Also set for subprocess calls
                        os.environ['NIM_PATH'] = nim_path
                        os.environ['NIMBLE_PATH'] = os.path.join(nim_bin_dir, 'nimble.exe')
                        return True
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
            
            # If not found in known paths, check PATH
            # Check if nim is already in PATH but with .exe extension
            try:
                result = subprocess.run(
                    ['nim.exe', '--version'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"Found nim.exe in PATH: {result.stdout.splitlines()[0]}")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
            
            # Debug output in CI
            if os.environ.get('CI'):
                print("DEBUG: Nim not found in expected locations in CI!")
                print(f"Current PATH: {os.environ.get('PATH', 'NOT SET')}")
                print("Checking C:\\ for nim directories...")
                try:
                    import glob
                    nim_patterns = [
                        'C:\\nim*',
                        'C:\\tools\\nim*',
                        'C:\\ProgramData\\nim*'
                    ]
                    for pattern in nim_patterns:
                        matches = glob.glob(pattern)
                        if matches:
                            print(f"Found: {matches}")
                except Exception as e:
                    print(f"Could not search directories: {e}")
        
        # For non-Windows or if Windows checks failed, try normal PATH
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
    
    def copy_windows_extension(self):
        """Copy the Windows .pyd file to the build directory."""
        pyd_source = Path('nim_mmcif') / 'nim_mmcif.pyd'
        
        if not pyd_source.exists():
            print(f"WARNING: Windows extension {pyd_source} not found!")
            return False
        
        # Find the build directory
        if self.build_lib:
            build_dir = Path(self.build_lib) / 'nim_mmcif'
            build_dir.mkdir(parents=True, exist_ok=True)
            
            pyd_dest = build_dir / 'nim_mmcif.pyd'
            
            # Copy the .pyd file
            import shutil
            try:
                shutil.copy2(pyd_source, pyd_dest)
                print(f"Copied {pyd_source} to {pyd_dest}")
                
                # Also list the contents to verify
                print(f"Contents of {build_dir}:")
                for file in build_dir.iterdir():
                    print(f"  - {file.name}")
                
                return True
            except Exception as e:
                print(f"ERROR: Failed to copy .pyd file: {e}")
                return False
        else:
            print("WARNING: build_lib not set, cannot copy .pyd file")
            return False
    
    def ensure_nimpy(self):
        """Ensure nimpy is installed."""
        try:
            # Determine nimble command
            nimble_cmd = ['nimble']
            if platform.system() == 'Windows' and os.environ.get('NIMBLE_PATH'):
                nimble_cmd = [os.environ['NIMBLE_PATH']]
            
            # Check if nimpy is installed
            result = subprocess.run(
                nimble_cmd + ['list', '--installed'],
                capture_output=True,
                text=True,
                check=True
            )
            
            if 'nimpy' not in result.stdout:
                print("Installing nimpy...")
                subprocess.run(nimble_cmd + ['install', 'nimpy', '-y'], check=True)
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
            # Base command - use the discovered Nim path on Windows if available
            if platform.system() == 'Windows':
                # Always use the NIM_PATH if it was set during check_nim_installed
                if os.environ.get('NIM_PATH'):
                    nim_exe = os.environ['NIM_PATH']
                    print(f"Using Nim from NIM_PATH: {nim_exe}")
                    cmd = [nim_exe, 'c', '--app:lib']
                else:
                    # Fallback to trying nim.exe in PATH
                    print("NIM_PATH not set, trying nim.exe in PATH")
                    cmd = ['nim.exe', 'c', '--app:lib']
            else:
                cmd = ['nim', 'c', '--app:lib']
            
            # Platform-specific settings
            if system == 'Darwin':  # macOS
                # Set minimum macOS deployment target to 10.9 for wheel compatibility
                macos_target = os.environ.get('MACOSX_DEPLOYMENT_TARGET', '10.9')
                
                # Check if we're building for a specific architecture via cibuildwheel
                # ARCHFLAGS is set by cibuildwheel to indicate target architecture
                archflags = os.environ.get('ARCHFLAGS', '')
                
                # Determine target architecture
                if '-arch x86_64' in archflags:
                    # Building for x86_64
                    target_arch = 'x86_64'
                    nim_cpu = 'amd64'
                elif '-arch arm64' in archflags:
                    # Building for arm64
                    target_arch = 'arm64'
                    nim_cpu = 'arm64'
                else:
                    # Default to host architecture
                    target_arch = 'arm64' if machine == 'arm64' else 'x86_64'
                    nim_cpu = 'arm64' if machine == 'arm64' else 'amd64'
                
                print(f"Building for macOS {target_arch} (host: {machine})")
                print(f"ARCHFLAGS: {archflags}")
                
                cmd.extend([f'--cpu:{nim_cpu}',
                           f'--passC:-arch {target_arch} -mmacosx-version-min={macos_target}',
                           f'--passL:-arch {target_arch} -mmacosx-version-min={macos_target}'])
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
                # Debug: Print Python architecture info
                import struct
                print(f"Python interpreter architecture: {struct.calcsize('P') * 8}-bit")
                print(f"Python version: {sys.version}")
                print(f"Platform machine: {platform.machine()}")
                
                # Always build for 64-bit on Windows CI
                cmd.append('--cpu:amd64')
                # On Windows, we need to use the .pyd extension
                cmd.append('--out:nim_mmcif.pyd')
                output_file = 'nim_mmcif.pyd'
                
                # Check if MSVC is available
                msvc_available = False
                try:
                    # Check if cl.exe (MSVC) is available
                    msvc_check = subprocess.run(['where', 'cl'], capture_output=True, text=True)
                    if msvc_check.returncode == 0:
                        print("MSVC found in PATH")
                        msvc_available = True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
                
                # Get Python library information for Windows
                import sysconfig
                python_lib_dir = sysconfig.get_config_var('LIBDIR')
                python_version = f"{sys.version_info.major}{sys.version_info.minor}"
                
                # In CI environment, prefer GCC for consistency
                if os.environ.get('CI') and not msvc_available:
                    print("CI environment detected, using MinGW-w64 GCC")
                    cmd.append('--cc:gcc')
                    # Override the nim.cfg settings for CI environment
                    cmd.append('--forceBuild')  # Force rebuild with new compiler
                    # Explicitly target 64-bit Windows
                    cmd.append('--os:windows')
                    cmd.append('--passC:-m64')
                    cmd.append('--passL:-m64')
                    # Generate proper Windows DLL
                    cmd.append('--passL:-shared')
                    cmd.append('--passL:-Wl,--out-implib,nim_mmcif.lib')
                    # Use static runtime to avoid DLL dependencies
                    cmd.append('--passL:-static-libgcc')
                    cmd.append('--passL:-static-libstdc++')
                    # Ensure we're building a Python extension module
                    cmd.append('--passL:-Wl,--export-all-symbols')
                    # Link against Python library for MinGW
                    python_home = sys.prefix
                    # Try to find python DLL in common locations
                    python_dll_paths = [
                        os.path.join(python_home, 'libs', f'python{python_version}.lib'),
                        os.path.join(python_home, f'python{python_version}.lib'),
                        os.path.join(sys.base_prefix, 'libs', f'python{python_version}.lib'),
                    ]
                    for dll_path in python_dll_paths:
                        if os.path.exists(dll_path):
                            print(f"Found Python library at: {dll_path}")
                            cmd.append(f'--passL:{dll_path}')
                            break
                    else:
                        # Fallback to standard linking
                        if python_lib_dir:
                            cmd.append(f'--passL:-L{python_lib_dir}')
                        cmd.append(f'--passL:-lpython{python_version}')
                elif msvc_available:
                    # Use MSVC if available (best compatibility with Python on Windows)
                    print("Using MSVC compiler")
                    cmd.append('--cc:vcc')
                    cmd.append('--passC:/MD')  # Use multithreaded DLL runtime
                    # Link against Python library
                    if python_lib_dir:
                        cmd.append(f'--passL:/LIBPATH:{python_lib_dir}')
                    cmd.append(f'--passL:python{python_version}.lib')
                else:
                    # Fall back to GCC (available in cibuildwheel via mingw)
                    print("MSVC not available, using GCC")
                    cmd.append('--cc:gcc')
                    # Override the nim.cfg settings for CI environment
                    cmd.append('--forceBuild')  # Force rebuild with new compiler
                    # Ensure 64-bit build
                    cmd.append('--passC:-m64')
                    cmd.append('--passL:-m64')
                    # Link as shared library
                    cmd.append('--passL:-shared')
                    # Use static libgcc to avoid DLL dependencies
                    cmd.append('--passL:-static-libgcc')
                    cmd.append('--passL:-static-libstdc++')
                    # Link against Python library for MinGW
                    if python_lib_dir:
                        cmd.append(f'--passL:-L{python_lib_dir}')
                    cmd.append(f'--passL:-lpython{python_version}')
            
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
            
            # On Windows, also ensure the .pyd is in the package directory
            if system == 'Windows' and output_file == 'nim_mmcif.pyd':
                # The file should already be in the right place since we're in nim_mmcif dir
                pyd_path = Path(output_file)
                if pyd_path.exists():
                    print(f"Windows extension {output_file} exists at: {pyd_path.absolute()}")
                    # Check file size
                    file_size = pyd_path.stat().st_size
                    print(f"Extension file size: {file_size} bytes")
                    
                    # Try to verify it's a valid DLL using ctypes
                    try:
                        import ctypes
                        # This will fail if the DLL is not valid for this architecture
                        test_dll = ctypes.CDLL(str(pyd_path.absolute()))
                        print("DLL verification passed - extension is loadable")
                    except Exception as e:
                        print(f"WARNING: DLL verification failed: {e}")
                        print("This may indicate an architecture mismatch")
                    
                    # Set an attribute so build_ext knows the extension was built
                    self.nim_extension_built = True
                else:
                    print(f"WARNING: {output_file} not found after build!")
            
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