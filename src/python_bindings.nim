import mmcif
import nimpy
import sequtils

proc parse_mmcif(filepath: string): mmCIF {.exportpy.} =
  ## Parse mmCIF file and return the mmCIF structure
  mmcif_parse(filepath)

proc get_atom_count(filepath: string): int {.exportpy.} =
  ## Get number of atoms in mmCIF file
  let result = mmcif_parse(filepath)
  result.atoms.len

proc get_atoms(filepath: string): seq[Atom] {.exportpy.} =
  ## Get all atoms from mmCIF file
  let result = mmcif_parse(filepath)
  result.atoms

proc get_atom_positions(filepath: string): seq[tuple[x, y, z: float]] {.exportpy.} =
  ## Get just the 3D coordinates of all atoms
  let result = mmcif_parse(filepath)
  result.atoms.mapIt((x: it.x, y: it.y, z: it.z))