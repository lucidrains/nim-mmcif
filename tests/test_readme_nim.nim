## Test that Nim example from README executes without errors

import ../nim_mmcif/mmcif
import os

proc testReadmeNimExample() =
  let testFile = currentSourcePath().parentDir() / "test.mmcif"
  
  # Parse an mmCIF file
  let data = mmcif_parse(testFile)
  echo "Found ", data.atoms.len, " atoms"
  
  # Iterate through atoms
  for atom in data.atoms[0..<min(5, data.atoms.len)]:
    echo "Atom ", atom.id, ": ", atom.label_atom_id, 
         " at (", atom.Cartn_x, ", ", atom.Cartn_y, ", ", atom.Cartn_z, ")"
  
  # Access specific atom properties
  if data.atoms.len > 0:
    let firstAtom = data.atoms[0]
    echo "Chain: ", firstAtom.label_asym_id
    echo "Residue: ", firstAtom.label_comp_id
    echo "B-factor: ", firstAtom.B_iso_or_equiv
  
  echo "Nim README example executed successfully!"

when isMainModule:
  testReadmeNimExample()