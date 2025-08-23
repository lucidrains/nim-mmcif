# Package

version       = "0.0.14"
author        = "lucidrains"
description   = "Parser for mmCIF"
license       = "MIT"
srcDir        = "nim_mmcif"

# Dependencies

requires "nim >= 2.0.0"
requires "nimpy >= 0.2.0"

# Tasks

task build, "Build the shared library":
  when defined(windows):
    exec "nim c --app:lib --out:nim_mmcif.pyd nim_mmcif/nim_mmcif.nim"
  else:
    exec "nim c --app:lib --out:nim_mmcif.so nim_mmcif/nim_mmcif.nim"

task buildRelease, "Build the shared library with optimizations":
  when defined(windows):
    exec "nim c -d:release --app:lib --out:nim_mmcif.pyd nim_mmcif/nim_mmcif.nim"
  else:
    exec "nim c -d:release --app:lib --out:nim_mmcif.so nim_mmcif/nim_mmcif.nim"