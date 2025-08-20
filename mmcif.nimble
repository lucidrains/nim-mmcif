# Package

version       = "0.0.1"
author        = "lucidrains"
description   = "Parser for mmCIF"
license       = "MIT"
srcDir        = "src"

# Dependencies

requires "nim >= 2.2.4"
requires "nimpy"

# Tasks

task buildPythonModule, "Build Python module":
  when defined(windows):
    exec "nim c --app:lib --out:nim_mmcif.dll src/python_bindings.nim"
  else:
    exec "nim c --app:lib --out:nim_mmcif.so src/python_bindings.nim"
