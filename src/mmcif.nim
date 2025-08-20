import std/[strutils, sequtils, sets]

const ATOM_NAME = "ATOM"

const FIELDS = [
  "type",
  "id",
  "type_symbol",
  "label_atom_id",
  "label_alt_id",
  "label_comp_id",
  "label_asym_id",
  "label_entity_id",
  "label_seq_id",
  "pdbx_PDB_ins_code",
  "Cartn_x",
  "Cartn_y",
  "Cartn_z",
  "occupancy",
  "B_iso_or_equiv",
  "pdbx_formal_charge",
  "auth_seq_id",
  "auth_comp_id",
  "auth_asym_id",
  "auth_atom_id",
  "pdbx_PDB_model_num",
]

const INTEGER_FIELDS = toHashSet([
  "id",
  "label_entity_id",
  "label_seq_id",
  "auth_seq_id",
  "pdbx_PDB_model_num",
])

const FLOAT_FIELDS = toHashSet([
  "Cartn_x",
  "Cartn_y",
  "Cartn_z",
  "occupancy",
  "B_iso_or_equiv",
])

type
  Atom* = object
    `type`*: string
    id*: int
    type_symbol*: string
    label_atom_id*: string
    label_alt_id*: string
    label_comp_id*: string
    label_asym_id*: string
    label_entity_id*: int
    label_seq_id*: int
    pdbx_PDB_ins_code*: string
    Cartn_x*: float
    Cartn_y*: float
    Cartn_z*: float
    occupancy*: float
    B_iso_or_equiv*: float
    pdbx_formal_charge*: string
    auth_seq_id*: int
    auth_comp_id*: string
    auth_asym_id*: string
    auth_atom_id*: string
    pdbx_PDB_model_num*: int
    x*: float
    y*: float
    z*: float

  mmCIF* = object
    atoms*: seq[Atom]

proc parseMmcifString*(mmcif: string): mmCIF =
  var atoms: seq[Atom] = @[]
  let mmcifLines = mmcif.splitLines

  for mmcifLine in mmcifLines:
    if mmcifLine.startsWith(ATOM_NAME):
      var atom = Atom()
      let values = mmcifLine.split(Whitespace).filterIt(it.len > 0)

      for i, value in values:
        if i >= FIELDS.len:
          break
        let field = FIELDS[i]

        if INTEGER_FIELDS.contains(field):
          try:
            let intVal = parseInt(value)
            case field
            of "id": atom.id = intVal
            of "label_entity_id": atom.label_entity_id = intVal
            of "label_seq_id": atom.label_seq_id = intVal
            of "auth_seq_id": atom.auth_seq_id = intVal
            of "pdbx_PDB_model_num": atom.pdbx_PDB_model_num = intVal
            else: discard
          except ValueError:
            discard # Keep default value (0)
        elif FLOAT_FIELDS.contains(field):
          try:
            let floatVal = parseFloat(value)
            case field
            of "Cartn_x": atom.Cartn_x = floatVal
            of "Cartn_y": atom.Cartn_y = floatVal
            of "Cartn_z": atom.Cartn_z = floatVal
            of "occupancy": atom.occupancy = floatVal
            of "B_iso_or_equiv": atom.B_iso_or_equiv = floatVal
            else: discard
          except ValueError:
            discard # Keep default value (0.0)
        else:
          case field
          of "type": atom.`type` = value
          of "type_symbol": atom.type_symbol = value
          of "label_atom_id": atom.label_atom_id = value
          of "label_alt_id": atom.label_alt_id = value
          of "label_comp_id": atom.label_comp_id = value
          of "label_asym_id": atom.label_asym_id = value
          of "pdbx_PDB_ins_code": atom.pdbx_PDB_ins_code = value
          of "pdbx_formal_charge": atom.pdbx_formal_charge = value
          of "auth_comp_id": atom.auth_comp_id = value
          of "auth_asym_id": atom.auth_asym_id = value
          of "auth_atom_id": atom.auth_atom_id = value
          else: discard

      atom.x = atom.Cartn_x
      atom.y = atom.Cartn_y
      atom.z = atom.Cartn_z

      atoms.add(atom)

  return mmCIF(atoms: atoms)

proc mmcif_parse*(filepath: string): mmCIF =
  let content = readFile(filepath)
  return parseMmcifString(content)
