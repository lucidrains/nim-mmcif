import unittest
import ../nim_mmcif/mmcif
import os
import sequtils

test "can parse mmcif file":
  let testFile = currentSourcePath().parentDir() / "test.mmcif"
  let parsed = mmcif_parse(testFile)

  test "parses the correct number of atoms":
    check parsed.atoms.len == 7

  test "parses atom fields correctly":
    let firstAtom = parsed.atoms[0]
    check firstAtom.id == 1
    check firstAtom.type_symbol == "N"
    check firstAtom.label_atom_id == "N"
    check firstAtom.label_comp_id == "VAL"
    check firstAtom.Cartn_x == 6.204
    check firstAtom.Cartn_y == 16.869
    check firstAtom.Cartn_z == 4.854
    check firstAtom.occupancy == 1.00
    check firstAtom.B_iso_or_equiv == 49.05
    check firstAtom.auth_seq_id == 1
    check firstAtom.pdbx_PDB_model_num == 1

    let secondAtom = parsed.atoms[1]
    check secondAtom.id == 2
    check secondAtom.type_symbol == "C"
    check secondAtom.label_atom_id == "CA"
    check secondAtom.label_comp_id == "VAL"
    check secondAtom.Cartn_x == 6.913
    check secondAtom.Cartn_y == 17.759
    check secondAtom.Cartn_z == 4.607
    check secondAtom.occupancy == 1.00
    check secondAtom.B_iso_or_equiv == 43.14
    check secondAtom.auth_seq_id == 1
    check secondAtom.pdbx_PDB_model_num == 1

test "can parse multiple mmcif files in batch":
  let testDir = currentSourcePath().parentDir()
  let testFiles = @[
    testDir / "test1.mmcif",
    testDir / "test2.mmcif",
    testDir / "test.mmcif"
  ]
  
  let parsedBatch = mmcif_parse_batch(testFiles)
  
  test "returns correct number of parsed files":
    check parsedBatch.len == 3
  
  test "first file parsed correctly":
    let first = parsedBatch[0]
    check first.atoms.len == 3
    check first.atoms[0].label_comp_id == "ALA"
    check first.atoms[0].Cartn_x == 10.000
    check first.atoms[0].Cartn_y == 20.000
    check first.atoms[0].Cartn_z == 30.000
  
  test "second file parsed correctly":
    let second = parsedBatch[1]
    check second.atoms.len == 3
    check second.atoms[0].label_comp_id == "GLY"
    check second.atoms[2].`type` == "HETATM"
    check second.atoms[2].label_comp_id == "HOH"
  
  test "third file parsed correctly":
    let third = parsedBatch[2]
    check third.atoms.len == 7
    check third.atoms[0].label_comp_id == "VAL"
