#!/usr/bin/env python3
"""Build script for nim-mmcif."""

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
    cmd = ['nim', 'c', '--app:lib', '--opt:speed', '--threads:on']
    
    if system == 'Darwin':
        cmd.extend(['--cc:clang', '--out:nim_mmcif.so'])
    elif system == 'Linux':
        cmd.extend(['--cc:gcc', '--passL:-fPIC', '--out:nim_mmcif.so'])
    elif system == 'Windows':
        cmd.extend(['--cc:gcc', '--out:nim_mmcif.pyd'])
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