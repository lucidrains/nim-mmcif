"""Setup script for nim-mmcif package."""

from __future__ import annotations

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
        # Try different possible nim locations
        nim_commands = ['nim']
        
        # Add Windows-specific paths if on Windows
        if platform.system() == 'Windows':
            # Check environment variables for CI builds
            nim_path = os.environ.get('NIM_PATH')
            if nim_path:
                nim_commands.insert(0, nim_path)
            
            # Common Windows Nim installation paths
            nim_commands.extend([
                r'C:\nim-2.2.4\bin\nim.exe',
                r'C:\nim\bin\nim.exe',
                r'C:\tools\nim\bin\nim.exe',
            ])
        
        for nim_cmd in nim_commands:
            try:
                # On Windows, use shell=True to properly resolve PATH
                use_shell = platform.system() == 'Windows' and nim_cmd == 'nim'
                result = subprocess.run(
                    [nim_cmd, '--version'] if not use_shell else f'{nim_cmd} --version',
                    capture_output=True,
                    text=True,
                    check=True,
                    shell=use_shell
                )
                print(f"Found Nim at {nim_cmd}: {result.stdout.splitlines()[0]}")
                # Store the working nim command for later use
                self.nim_cmd = nim_cmd
                self.use_shell = use_shell
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        print(f"Nim not found. Tried: {nim_commands}")
        return False
    
    def ensure_nimpy(self):
        """Ensure nimpy is installed."""
        try:
            # Find nimble command (similar to nim)
            nimble_commands = ['nimble']
            if platform.system() == 'Windows':
                nimble_path = os.environ.get('NIMBLE_PATH')
                if nimble_path:
                    nimble_commands.insert(0, nimble_path)
                nimble_commands.extend([
                    r'C:\nim-2.2.4\bin\nimble.exe',
                    r'C:\nim\bin\nimble.exe',
                    r'C:\tools\nim\bin\nimble.exe',
                ])
            
            nimble_cmd = None
            use_shell = False
            for cmd in nimble_commands:
                try:
                    use_shell = platform.system() == 'Windows' and cmd == 'nimble'
                    subprocess.run(
                        [cmd, '--version'] if not use_shell else f'{cmd} --version',
                        capture_output=True,
                        text=True,
                        check=True,
                        shell=use_shell
                    )
                    nimble_cmd = cmd
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            if not nimble_cmd:
                print("Warning: nimble not found, skipping nimpy check")
                return
            
            result = subprocess.run(
                [nimble_cmd, 'list', '--installed'] if not use_shell else f'{nimble_cmd} list --installed',
                capture_output=True,
                text=True,
                check=True,
                shell=use_shell
            )
            
            if 'nimpy' not in result.stdout:
                print("Installing nimpy...")
                subprocess.run(
                    [nimble_cmd, 'install', 'nimpy', '-y'] if not use_shell else f'{nimble_cmd} install nimpy -y',
                    check=True,
                    shell=use_shell
                )
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
            # Use the nim command found during check_nim_installed
            nim_cmd = getattr(self, 'nim_cmd', 'nim')
            use_shell = getattr(self, 'use_shell', False)
            
            cmd = [nim_cmd, 'c', '--app:lib', '--opt:speed', '--threads:on']
            
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
                # Use static linking to avoid DLL dependency issues
                cmd.extend([
                    '--cc:gcc',
                    f'--out:{output_file}',
                    '--passL:-static',
                    '--passL:-static-libgcc',
                    '--passL:-static-libstdc++'
                ])
            else:
                output_file = 'nim_mmcif.so'
                cmd.append(f'--out:{output_file}')
            
            cmd.append('nim_mmcif.nim')
            
            # Convert to string if using shell
            if use_shell:
                cmd_str = ' '.join(cmd)
                print(f"Building: {cmd_str}")
                result = subprocess.run(cmd_str, capture_output=True, text=True, shell=True)
            else:
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