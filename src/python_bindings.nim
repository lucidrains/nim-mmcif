import mmcif
import nimpy

pyExportModule("nim_mmcif")

proc parse_mmcif_py(filepath: string): PyObject {.exportpy.} =
  ## Parse mmCIF file and return Python-compatible object
  let mmcifResult = mmcif_parse(filepath)
  
  var atoms = newSeq[PyObject]()
  
  for atom in mmcifResult.atoms:
    var atomDict = pyDict()
    atomDict["type"] = atom.`type`
    atomDict["id"] = atom.id
    atomDict["type_symbol"] = atom.type_symbol
    atomDict["label_atom_id"] = atom.label_atom_id
    atomDict["label_alt_id"] = atom.label_alt_id
    atomDict["label_comp_id"] = atom.label_comp_id
    atomDict["label_asym_id"] = atom.label_asym_id
    atomDict["label_entity_id"] = atom.label_entity_id
    atomDict["label_seq_id"] = atom.label_seq_id
    atomDict["pdbx_PDB_ins_code"] = atom.pdbx_PDB_ins_code
    atomDict["Cartn_x"] = atom.Cartn_x
    atomDict["Cartn_y"] = atom.Cartn_y
    atomDict["Cartn_z"] = atom.Cartn_z
    atomDict["occupancy"] = atom.occupancy
    atomDict["B_iso_or_equiv"] = atom.B_iso_or_equiv
    atomDict["pdbx_formal_charge"] = atom.pdbx_formal_charge
    atomDict["auth_seq_id"] = atom.auth_seq_id
    atomDict["auth_comp_id"] = atom.auth_comp_id
    atomDict["auth_asym_id"] = atom.auth_asym_id
    atomDict["auth_atom_id"] = atom.auth_atom_id
    atomDict["pdbx_PDB_model_num"] = atom.pdbx_PDB_model_num
    atomDict["x"] = atom.x
    atomDict["y"] = atom.y
    atomDict["z"] = atom.z
    
    atoms.add(atomDict)
  
  var resultDict = pyDict()
  resultDict["atoms"] = atoms
  resultDict["num_atoms"] = mmcifResult.atoms.len
  
  return resultDict

proc get_atom_count_py(filepath: string): int {.exportpy.} =
  ## Get number of atoms in mmCIF file
  let result = mmcif_parse(filepath)
  return result.atoms.len