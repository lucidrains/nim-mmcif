## Python bindings for the mmCIF parser using nimpy.

import nimpy
import sequtils
import ./mmcif

proc parse_mmcif(filepath: string): mmCIF {.exportpy.} =
  ## Parse an mmCIF file and return the mmCIF structure.
  ##
  ## Args:
  ##   filepath: Path to the mmCIF file.
  ##
  ## Returns:
  ##   mmCIF object containing parsed atoms.
  ##
  ## Raises:
  ##   IOError: If file cannot be read.
  ##   ParseError: If parsing fails.
  return mmcif_parse(filepath)

proc get_atom_count(filepath: string): int {.exportpy.} =
  ## Get the number of atoms in an mmCIF file.
  ##
  ## Args:
  ##   filepath: Path to the mmCIF file.
  ##
  ## Returns:
  ##   Number of atoms in the file.
  ##
  ## Raises:
  ##   IOError: If file cannot be read.
  ##   ParseError: If parsing fails.
  let parsed = mmcif_parse(filepath)
  return parsed.atoms.len

proc get_atoms(filepath: string): seq[Atom] {.exportpy.} =
  ## Get all atoms from an mmCIF file.
  ##
  ## Args:
  ##   filepath: Path to the mmCIF file.
  ##
  ## Returns:
  ##   Sequence of Atom objects.
  ##
  ## Raises:
  ##   IOError: If file cannot be read.
  ##   ParseError: If parsing fails.
  let parsed = mmcif_parse(filepath)
  return parsed.atoms

proc get_atom_positions(filepath: string): seq[tuple[x, y, z: float]] {.exportpy.} =
  ## Get 3D coordinates of all atoms from an mmCIF file.
  ##
  ## Args:
  ##   filepath: Path to the mmCIF file.
  ##
  ## Returns:
  ##   Sequence of (x, y, z) coordinate tuples.
  ##
  ## Raises:
  ##   IOError: If file cannot be read.
  ##   ParseError: If parsing fails.
  let parsed = mmcif_parse(filepath)
  return parsed.atoms.mapIt((x: it.x, y: it.y, z: it.z))

proc parse_mmcif_batch(filepaths: seq[string]): seq[mmCIF] {.exportpy.} =
  ## Parse multiple mmCIF files and return a sequence of mmCIF structures.
  ##
  ## Args:
  ##   filepaths: Sequence of paths to mmCIF files.
  ##
  ## Returns:
  ##   Sequence of mmCIF objects containing parsed atoms.
  ##
  ## Raises:
  ##   IOError: If any file cannot be read.
  ##   ParseError: If parsing fails for any file.
  return mmcif_parse_batch(filepaths)