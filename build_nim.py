#!/usr/bin/env python3
"""Build script for nim-mmcif."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path


def get_build_config():
    """Get platform-specific build configuration."""
    system = platform.system()
    machine = platform.machine()
    
    base_cmd = ['nim', 'c', '-d:release', '--app:lib', '--opt:speed', '--threads:on']
    
    if system == 'Darwin':
        base_cmd.extend(['--cc:clang', '--out:nim_mmcif.so'])
        
        # Check for architecture hints from environment
        archflags = os.environ.get('ARCHFLAGS', '')
        cibw_arch = os.environ.get('CIBW_ARCHS_MACOS', '')
        
        if '-arch arm64' in archflags or 'arm64' in cibw_arch or machine == 'arm64':
            print("Building for ARM64 architecture")
            base_cmd.extend(['--cpu:arm64', '--passC:-arch arm64', '--passL:-arch arm64'])
        elif '-arch x86_64' in archflags or 'x86_64' in cibw_arch or machine in ['x86_64', 'AMD64']:
            print("Building for x86_64 architecture")
            base_cmd.extend(['--cpu:amd64', '--passC:-arch x86_64', '--passL:-arch x86_64'])
        else:
            print(f"Building for native architecture: {machine}")
            
    elif system == 'Linux':
        base_cmd.extend(['--cc:gcc', '--passL:-fPIC', '--out:nim_mmcif.so'])
        
    elif system == 'Windows':
        # Use static linking to avoid DLL dependency issues
        base_cmd.extend([
            '--cc:gcc',
            '--out:nim_mmcif.pyd',
            '--passL:-static',
            '--passL:-static-libgcc',
            '--passL:-static-libstdc++'
        ])
    else:
        base_cmd.append('--out:nim_mmcif.so')
    
    return base_cmd


def build():
    """Build the Nim extension."""
    nim_dir = Path('nim_mmcif')
    if not nim_dir.exists():
        print("Error: nim_mmcif directory not found")
        return False
    
    os.chdir(nim_dir)
    
    try:
        cmd = get_build_config()
        cmd.append('nim_mmcif.nim')
        
        print(f"Building: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print("Build successful!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False
        
    finally:
        os.chdir('..')


if __name__ == '__main__':
    sys.exit(0 if build() else 1)