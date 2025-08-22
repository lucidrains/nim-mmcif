#!/usr/bin/env python3
"""
Verify Windows DLL/PYD architecture and dependencies.
"""

import os
import platform
import struct
import sys
from pathlib import Path

def check_dll_architecture(dll_path):
    """Check if a DLL is 32-bit or 64-bit."""
    try:
        with open(dll_path, 'rb') as f:
            # Read DOS header
            if f.read(2) != b'MZ':
                return "Not a valid PE file"
            
            # Skip to PE header offset location
            f.seek(0x3C)
            pe_offset = struct.unpack('<I', f.read(4))[0]
            
            # Go to PE header
            f.seek(pe_offset)
            if f.read(4) != b'PE\x00\x00':
                return "Not a valid PE file"
            
            # Read machine type
            machine_type = struct.unpack('<H', f.read(2))[0]
            
            if machine_type == 0x014c:
                return "32-bit (x86)"
            elif machine_type == 0x8664:
                return "64-bit (x64/AMD64)"
            elif machine_type == 0xaa64:
                return "64-bit (ARM64)"
            else:
                return f"Unknown architecture (0x{machine_type:04x})"
    except Exception as e:
        return f"Error checking file: {e}"

def main():
    print("=" * 60)
    print("DLL/PYD Architecture Verification")
    print("=" * 60)
    
    # Python info
    print(f"Python version: {sys.version}")
    print(f"Python architecture: {struct.calcsize('P') * 8}-bit")
    print(f"Platform: {platform.platform()}")
    print(f"Machine: {platform.machine()}")
    print("-" * 60)
    
    # Check for .pyd files
    nim_mmcif_dir = Path('nim_mmcif')
    if nim_mmcif_dir.exists():
        pyd_files = list(nim_mmcif_dir.glob('*.pyd'))
        dll_files = list(nim_mmcif_dir.glob('*.dll'))
        
        all_files = pyd_files + dll_files
        
        if all_files:
            print("Found DLL/PYD files:")
            for file in all_files:
                arch = check_dll_architecture(file)
                size = file.stat().st_size
                print(f"  {file.name}: {arch}, Size: {size} bytes")
                
                # Check if it's a placeholder
                if size < 1000:  # Placeholder files are typically very small
                    print(f"    WARNING: This appears to be a placeholder file!")
        else:
            print("No .pyd or .dll files found in nim_mmcif directory")
    else:
        print("nim_mmcif directory not found")
    
    print("-" * 60)
    
    # Try to import and check what happens
    try:
        import nim_mmcif
        print("✅ nim_mmcif imported successfully!")
        print(f"Version: {nim_mmcif.__version__}")
    except ImportError as e:
        print(f"❌ Failed to import nim_mmcif: {e}")
    
    print("=" * 60)

if __name__ == '__main__':
    main()