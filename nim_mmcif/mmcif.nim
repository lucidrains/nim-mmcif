## mmCIF parser module for reading Macromolecular Crystallographic Information Files.

import std/[strutils, sequtils, sets]

const 
  ATOM_RECORD* = "ATOM"
  HETATM_RECORD* = "HETATM"
  
  # Field names in mmCIF atom records
  ATOM_FIELDS* = [
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
    "group_PDB",
    "pdbx_sifts_xref_db_acc",
    "pdbx_sifts_xref_db_name",
    "pdbx_sifts_xref_db_num",
  ]
  
  # Fields that should be parsed as integers
  INTEGER_FIELDS* = toHashSet([
    "id",
    "label_entity_id",
    "label_seq_id",
    "auth_seq_id",
    "pdbx_PDB_model_num",
    "pdbx_sifts_xref_db_num",
  ])
  
  # Fields that should be parsed as floats
  FLOAT_FIELDS* = toHashSet([
    "Cartn_x",
    "Cartn_y",
    "Cartn_z",
    "occupancy",
    "B_iso_or_equiv",
  ])

type
  Atom* = object
    ## Represents a single atom from an mmCIF file.
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
    group_PDB*: string
    pdbx_sifts_xref_db_acc*: string
    pdbx_sifts_xref_db_name*: string
    pdbx_sifts_xref_db_num*: int
    # Convenience aliases for coordinates
    x*: float
    y*: float
    z*: float

  mmCIF* = object
    ## Container for parsed mmCIF data.
    atoms*: seq[Atom]
    
  ParseError* = object of CatchableError
    ## Error raised when parsing fails.


proc parseIntValue(value: string): int =
  ## Parse a string value as an integer.
  if value == "." or value == "?":
    return 0
  try:
    return parseInt(value)
  except ValueError:
    return 0

proc parseFloatValue(value: string): float =
  ## Parse a string value as a float.
  if value == "." or value == "?":
    return 0.0
  try:
    return parseFloat(value)
  except ValueError:
    return 0.0

proc parseStringValue(value: string): string =
  ## Parse a string value.
  if value == "." or value == "?":
    return ""
  return value


proc parseAtomLine(line: string): Atom =
  ## Parse a single ATOM or HETATM line into an Atom object.
  var atom = Atom()
  let tokens = line.split(Whitespace).filterIt(it.len > 0)
  
  for i, token in tokens:
    if i >= ATOM_FIELDS.len:
      break
    
    let field = ATOM_FIELDS[i]
    
    case field
    of "type":
      atom.`type` = token
    of "id":
      atom.id = parseIntValue(token)
    of "type_symbol":
      atom.type_symbol = parseStringValue(token)
    of "label_atom_id":
      atom.label_atom_id = parseStringValue(token)
    of "label_alt_id":
      atom.label_alt_id = parseStringValue(token)
    of "label_comp_id":
      atom.label_comp_id = parseStringValue(token)
    of "label_asym_id":
      atom.label_asym_id = parseStringValue(token)
    of "label_entity_id":
      atom.label_entity_id = parseIntValue(token)
    of "label_seq_id":
      atom.label_seq_id = parseIntValue(token)
    of "pdbx_PDB_ins_code":
      atom.pdbx_PDB_ins_code = parseStringValue(token)
    of "Cartn_x":
      atom.Cartn_x = parseFloatValue(token)
      atom.x = atom.Cartn_x
    of "Cartn_y":
      atom.Cartn_y = parseFloatValue(token)
      atom.y = atom.Cartn_y
    of "Cartn_z":
      atom.Cartn_z = parseFloatValue(token)
      atom.z = atom.Cartn_z
    of "occupancy":
      atom.occupancy = parseFloatValue(token)
    of "B_iso_or_equiv":
      atom.B_iso_or_equiv = parseFloatValue(token)
    of "pdbx_formal_charge":
      atom.pdbx_formal_charge = parseStringValue(token)
    of "auth_seq_id":
      atom.auth_seq_id = parseIntValue(token)
    of "auth_comp_id":
      atom.auth_comp_id = parseStringValue(token)
    of "auth_asym_id":
      atom.auth_asym_id = parseStringValue(token)
    of "auth_atom_id":
      atom.auth_atom_id = parseStringValue(token)
    of "pdbx_PDB_model_num":
      atom.pdbx_PDB_model_num = parseIntValue(token)
    of "group_PDB":
      atom.group_PDB = parseStringValue(token)
    of "pdbx_sifts_xref_db_acc":
      atom.pdbx_sifts_xref_db_acc = parseStringValue(token)
    of "pdbx_sifts_xref_db_name":
      atom.pdbx_sifts_xref_db_name = parseStringValue(token)
    of "pdbx_sifts_xref_db_num":
      atom.pdbx_sifts_xref_db_num = parseIntValue(token)
  
  return atom


proc parseMmcifString*(content: string): mmCIF =
  ## Parse mmCIF content from a string.
  result = mmCIF(atoms: @[])
  
  for line in content.splitLines:
    let trimmedLine = line.strip()
    if trimmedLine.startsWith(ATOM_RECORD) or trimmedLine.startsWith(HETATM_RECORD):
      result.atoms.add(parseAtomLine(trimmedLine))


proc mmcif_parse*(filepath: string): mmCIF =
  ## Parse an mmCIF file from disk line by line.
  ##
  ## Args:
  ##   filepath: Path to the mmCIF file.
  ##
  ## Returns:
  ##   Parsed mmCIF object containing atoms.
  ##
  ## Raises:
  ##   IOError: If file cannot be read.
  ##   ParseError: If file format is invalid.
  result = mmCIF(atoms: @[])
  
  var file: File
  try:
    if not open(file, filepath):
      raise newException(IOError, "Failed to open file: " & filepath)
    
    var line: string
    while file.readLine(line):
      let trimmedLine = line.strip()
      if trimmedLine.startsWith(ATOM_RECORD) or trimmedLine.startsWith(HETATM_RECORD):
        result.atoms.add(parseAtomLine(trimmedLine))
    
    close(file)
  except IOError as e:
    if file != nil:
      close(file)
    raise newException(IOError, "Failed to read file: " & e.msg)
  except Exception as e:
    if file != nil:
      close(file)
    raise newException(ParseError, "Failed to parse mmCIF: " & e.msg)


proc mmcif_parse_batch*(filepaths: seq[string]): seq[mmCIF] =
  ## Parse multiple mmCIF files from disk line by line.
  ##
  ## Args:
  ##   filepaths: Sequence of paths to mmCIF files.
  ##
  ## Returns:
  ##   Sequence of parsed mmCIF objects containing atoms.
  ##
  ## Raises:
  ##   IOError: If any file cannot be read.
  ##   ParseError: If any file format is invalid.
  result = @[]
  for filepath in filepaths:
    result.add(mmcif_parse(filepath))