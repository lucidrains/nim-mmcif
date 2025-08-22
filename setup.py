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
        if not self.check_nim_installed():
            raise RuntimeError("Nim compiler not found. Please install Nim from: https://nim-lang.org/install.html")
        
        self.ensure_nimpy()
        
        if not self.build_nim_extension():
            raise RuntimeError("Failed to build Nim extension")
        
        super().run()
    
    def check_nim_installed(self):
        """Check if Nim compiler is installed."""
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
            return False
    
    def ensure_nimpy(self):
        """Ensure nimpy is installed."""
        try:
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
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Warning: Could not check/install nimpy: {e}")
    
    def build_nim_extension(self):
        """Build the Nim extension module."""
        system = platform.system()
        machine = platform.machine()
        
        nim_dir = Path('nim_mmcif')
        if not nim_dir.exists():
            return False
        
        original_dir = os.getcwd()
        os.chdir(nim_dir)
        
        try:
            cmd = ['nim', 'c', '--app:lib', '--opt:speed', '--threads:on']
            
            if system == 'Darwin':  # macOS
                output_file = 'nim_mmcif.so'
                cmd.extend(['--cc:clang', f'--out:{output_file}'])
                
                # Check for ARCHFLAGS environment variable (used by cibuildwheel)
                archflags = os.environ.get('ARCHFLAGS', '')
                if '-arch arm64' in archflags:
                    print("Building for ARM64 architecture")
                    cmd.extend(['--cpu:arm64', '--passC:-arch arm64', '--passL:-arch arm64'])
                elif '-arch x86_64' in archflags:
                    print("Building for x86_64 architecture")
                    cmd.extend(['--cpu:amd64', '--passC:-arch x86_64', '--passL:-arch x86_64'])
                else:
                    # Check CIBW_ARCHS_MACOS if ARCHFLAGS not set
                    cibw_arch = os.environ.get('CIBW_ARCHS_MACOS', '')
                    if 'arm64' in cibw_arch:
                        print("Building for ARM64 architecture (from CIBW_ARCHS_MACOS)")
                        cmd.extend(['--cpu:arm64', '--passC:-arch arm64', '--passL:-arch arm64'])
                    elif 'x86_64' in cibw_arch:
                        print("Building for x86_64 architecture (from CIBW_ARCHS_MACOS)")
                        cmd.extend(['--cpu:amd64', '--passC:-arch x86_64', '--passL:-arch x86_64'])
                    else:
                        # Default to native architecture
                        print(f"Building for native architecture: {machine}")
                        if machine == 'arm64':
                            cmd.extend(['--cpu:arm64', '--passC:-arch arm64', '--passL:-arch arm64'])
                        elif machine in ['x86_64', 'AMD64']:
                            cmd.extend(['--cpu:amd64', '--passC:-arch x86_64', '--passL:-arch x86_64'])
                
            elif system == 'Linux':
                output_file = 'nim_mmcif.so'
                cmd.extend(['--cc:gcc', '--passL:-fPIC', f'--out:{output_file}'])
            elif system == 'Windows':
                output_file = 'nim_mmcif.pyd'
                cmd.extend(['--cc:gcc', f'--out:{output_file}'])
            else:
                output_file = 'nim_mmcif.so'
                cmd.append(f'--out:{output_file}')
            
            cmd.append('nim_mmcif.nim')
            
            print(f"Building: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Build failed:\n{result.stderr}")
                return False
            
            if not Path(output_file).exists():
                print(f"ERROR: {output_file} was not created!")
                return False
            
            print(f"Successfully built {output_file}")
            return True
            
        except Exception as e:
            print(f"Build failed: {e}")
            return False
        finally:
            os.chdir(original_dir)


ext_modules = []
cmdclass = {}

if 'bdist_wheel' in sys.argv:
    cmdclass['build_ext'] = NimBuildExt
    ext_modules = [Extension('nim_mmcif._dummy', sources=['nim_mmcif/_dummy.c'])]

setup(
    packages=find_packages(),
    ext_modules=ext_modules,
    cmdclass=cmdclass,
    zip_safe=False,
    include_package_data=True,
)