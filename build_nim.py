#!/usr/bin/env python3
"""Build script for nim-mmcif."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path


def build():
    """Build the Nim extension."""
    if not Path('nim_mmcif').exists():
        print("Error: nim_mmcif directory not found")
        return False
    
    os.chdir('nim_mmcif')
    
    system = platform.system()
    machine = platform.machine()
    cmd = ['nim', 'c', '--app:lib', '--opt:speed', '--threads:on']
    
    if system == 'Darwin':
        cmd.extend(['--cc:clang', '--out:nim_mmcif.so'])
        
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
        cmd.extend(['--cc:gcc', '--passL:-fPIC', '--out:nim_mmcif.so'])
    elif system == 'Windows':
        # Use static linking to avoid DLL dependency issues
        cmd.extend([
            '--cc:gcc',
            '--out:nim_mmcif.pyd',
            '--passL:-static',
            '--passL:-static-libgcc',
            '--passL:-static-libstdc++'
        ])
    else:
        cmd.append('--out:nim_mmcif.so')
    
    cmd.append('nim_mmcif.nim')
    
    print(f"Building: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("Build successful!")
        return True
    except subprocess.CalledProcessError:
        print("Build failed!")
        return False
    finally:
        os.chdir('..')


if __name__ == '__main__':
    sys.exit(0 if build() else 1)