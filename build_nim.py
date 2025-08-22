#!/usr/bin/env python3
"""
Cross-platform build script for nim-mmcif.
Automatically detects platform and builds the Nim extension.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def get_platform_info():
    """Get current platform information."""
    system = platform.system()
    machine = platform.machine()
    python_version = sys.version_info
    
    print(f"Platform: {system}")
    print(f"Architecture: {machine}")
    print(f"Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    return system, machine, python_version


def check_nim_installation():
    """Check if Nim is installed."""
    try:
        result = subprocess.run(['nim', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"Nim found: {result.stdout.splitlines()[0]}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: Nim not found!")
        print("Please install Nim from: https://nim-lang.org/install.html")
        return False


def check_nimpy_installation():
    """Check if nimpy is installed."""
    try:
        result = subprocess.run(['nimble', 'list', '--installed'],
                              capture_output=True, text=True, check=True)
        if 'nimpy' in result.stdout:
            print("nimpy found")
            return True
        else:
            print("nimpy not found, installing...")
            subprocess.run(['nimble', 'install', 'nimpy', '-y'], check=True)
            return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: nimble not found or nimpy installation failed!")
        return False


def build_nim_extension(system, machine):
    """Build the Nim extension for the current platform."""
    # Copy mmcif.nim to nim_mmcif directory if it doesn't exist
    import shutil
    src_file = Path('src/mmcif.nim')
    dest_file = Path('nim_mmcif/mmcif.nim')
    if src_file.exists() and not dest_file.exists():
        print(f"Copying {src_file} to {dest_file}")
        shutil.copy2(src_file, dest_file)
    
    os.chdir('nim_mmcif')
    
    # Base command
    cmd = ['nim', 'c', '--app:lib']
    
    # Platform-specific flags
    if system == 'Darwin':  # macOS
        # Set minimum macOS deployment target to 10.9 for wheel compatibility
        macos_target = os.environ.get('MACOSX_DEPLOYMENT_TARGET', '10.9')
        
        # Check if we're building for a specific architecture
        archflags = os.environ.get('ARCHFLAGS', '')
        
        # Determine target architecture
        if '-arch x86_64' in archflags:
            target_arch = 'x86_64'
            nim_cpu = 'amd64'
        elif '-arch arm64' in archflags:
            target_arch = 'arm64'
            nim_cpu = 'arm64'
        else:
            # Default to host architecture
            target_arch = 'arm64' if machine == 'arm64' else 'x86_64'
            nim_cpu = 'arm64' if machine == 'arm64' else 'amd64'
        
        print(f"Building for macOS {target_arch} (host: {machine})")
        
        cmd.extend([f'--cpu:{nim_cpu}', 
                   f'--passC:-arch {target_arch} -mmacosx-version-min={macos_target}',
                   f'--passL:-arch {target_arch} -mmacosx-version-min={macos_target}'])
        cmd.extend(['--cc:clang', '--out:nim_mmcif.so'])
    
    elif system == 'Linux':
        if machine in ['aarch64', 'arm64']:
            cmd.append('--cpu:arm64')
        else:
            cmd.append('--cpu:amd64')
        cmd.extend(['--cc:gcc', '--passL:-fPIC', '--out:nim_mmcif.so'])
    
    elif system == 'Windows':
        # Always build for 64-bit on Windows
        cmd.append('--cpu:amd64')
        cmd.append('--os:windows')
        
        # Check for Visual Studio
        msvc_available = False
        try:
            result = subprocess.run(['where', 'cl'], capture_output=True, text=True)
            if result.returncode == 0:
                msvc_available = True
                print("MSVC compiler found")
        except:
            pass
        
        if msvc_available:
            cmd.append('--cc:vcc')
            cmd.append('--passC:/MD')  # Use multithreaded DLL runtime
        else:
            print("Using MinGW-w64 GCC")
            cmd.append('--cc:gcc')
            # Ensure 64-bit build
            cmd.append('--passC:-m64')
            cmd.append('--passL:-m64')
            # Build as shared library
            cmd.append('--passL:-shared')
            # Use static runtime to avoid DLL dependencies
            cmd.append('--passL:-static-libgcc')
            cmd.append('--passL:-static-libstdc++')
            # Add Windows system libraries
            cmd.append('--passL:-lmsvcrt')
            cmd.append('--passL:-lkernel32')
            cmd.append('--passL:-luser32')
            # Link statically with pthread if needed
            cmd.append('--passL:-static -lpthread')
            # Export all symbols for Python
            cmd.append('--passL:-Wl,--export-all-symbols')
            # Add subsystem flag for DLL
            cmd.append('--passL:-Wl,--subsystem,windows')
        
        cmd.append('--out:nim_mmcif.pyd')
    
    else:
        print(f"WARNING: Unknown platform {system}, using defaults")
        cmd.append('--out:nim_mmcif.so')
    
    # Add optimization flags
    cmd.extend(['--opt:speed', '--threads:on'])
    
    # Add source file
    cmd.append('nim_mmcif.nim')
    
    print(f"Building with command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Build successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    finally:
        os.chdir('..')


def test_import():
    """Test if the module can be imported."""
    try:
        # Add current directory to path
        sys.path.insert(0, '.')
        
        import nim_mmcif
        print(f"✅ Module imported successfully: v{nim_mmcif.__version__}")
        
        # Test basic functionality
        funcs = ['parse_mmcif', 'get_atom_count', 'get_atoms', 'get_atom_positions']
        for func in funcs:
            if hasattr(nim_mmcif, func):
                print(f"  ✓ Function '{func}' available")
            else:
                print(f"  ✗ Function '{func}' missing")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def main():
    """Main build process."""
    print("=" * 60)
    print("nim-mmcif Cross-Platform Build Script")
    print("=" * 60)
    
    # Get platform info
    system, machine, python_version = get_platform_info()
    print("-" * 60)
    
    # Check prerequisites
    if not check_nim_installation():
        sys.exit(1)
    
    if not check_nimpy_installation():
        sys.exit(1)
    
    print("-" * 60)
    
    # Install Python dependencies
    print("Installing Python dependencies...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'nimporter'], check=True)
    
    print("-" * 60)
    
    # Build the extension
    print("Building Nim extension...")
    if not build_nim_extension(system, machine):
        print("\nBuild failed! Please check the error messages above.")
        sys.exit(1)
    
    print("-" * 60)
    
    # Test the build
    print("Testing build...")
    if test_import():
        print("\n✅ Build completed successfully!")
        print("You can now install the package with: pip install -e .")
    else:
        print("\n❌ Build test failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()