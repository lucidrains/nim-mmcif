# Package

version       = "0.0.1"
author        = "lucidrains"
description   = "Parser for mmCIF"
license       = "MIT"
srcDir        = "src"

# Dependencies

requires "nim >= 2.2.4"
requires "nimpy >= 0.2.1"

# Tasks

task buildPythonModule, "Build Python module":
  when defined(windows):
    exec "nim c --app:lib --dynlibOverride:python3 --passL:\"-static-libgcc -static-libstdc++\" --out:python_wrapper/python_bindings.pyd src/python_bindings.nim"
  else:
    exec "nim c --app:lib --out:python_wrapper/python_bindings.so src/python_bindings.nim"
