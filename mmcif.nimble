# Package

version       = "0.0.5"
author        = "lucidrains"
description   = "Parser for mmCIF"
license       = "MIT"
srcDir        = "nim_mmcif"

# Dependencies

requires "nim >= 2.2.4"
requires "nimpy >= 0.2.1"

# Tasks

task buildPythonModule, "Build Python module":
  when defined(windows):
    exec "nim c --app:lib --dynlibOverride:python3 --passL:\"-static-libgcc -static-libstdc++\" --out:python_wrapper/python_bindings.pyd nim_mmcif/python_bindings.nim"
  else:
    exec "nim c --app:lib --out:python_wrapper/python_bindings.so nim_mmcif/python_bindings.nim"
