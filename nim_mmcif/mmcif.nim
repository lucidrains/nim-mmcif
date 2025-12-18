## mmCIF parser module for reading Macromolecular Crystallographic Information Files.

import std/[strutils, sets]

const 
  ATOM_RECORD* = "ATOM"
  HETATM_RECORD* = "HETATM"
  
  # Field names in mmCIF atom records
  ATOM_FIELDS* = [
    "group_PDB",  # This is the first field (ATOM or HETATM)
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
    # Convenience aliases for coordinates
    x*: float
    y*: float
    z*: float

  mmCIF* = object
    ## Container for parsed mmCIF data.
    atoms*: seq[Atom]
    
  ParseError* = object of CatchableError
    ## Error raised when parsing fails.


proc parseValue[T](value: string): T =
  ## Generic parser for different value types.
  if value in [".", "?"]:
    when T is int: return 0
    elif T is float: return 0.0
    else: return ""
  else:
    when T is int:
      try: return parseInt(value)
      except ValueError: return 0
    elif T is float:
      try: return parseFloat(value)
      except ValueError: return 0.0
    else: return value


proc tokenizeLine*(line: string): seq[string] =
  ## Tokenize a line respecting quoted values.
  ## Handles both single and double quotes, and preserves spaces within quotes.
  result = @[]
  if line.len == 0: return
  
  var 
    current = ""
    inQuote = false
    quoteChar = '\0'
  
  for ch in line:
    if not inQuote:
      if ch in {'"', '\''}:
        inQuote = true
        quoteChar = ch
      elif ch in Whitespace:
        if current.len > 0:
          result.add(current)
          current = ""
      else:
        current.add(ch)
    else:
      if ch == quoteChar:
        inQuote = false
        quoteChar = '\0'
        result.add(current)
        current = ""
      else:
        current.add(ch)
  
  if current.len > 0:
    result.add(current)


proc parseAtomLine(line: string): Atom =
  ## Parse a single ATOM or HETATM line into an Atom object.
  var atom = Atom()
  let tokens = tokenizeLine(line)
  
  for i, token in tokens:
    if i >= ATOM_FIELDS.len:
      break
    
    let field = ATOM_FIELDS[i]
    
    case field
    of "group_PDB":
      atom.`type` = token
    of "id":
      atom.id = parseValue[int](token)
    of "type_symbol":
      atom.type_symbol = parseValue[string](token)
    of "label_atom_id":
      atom.label_atom_id = parseValue[string](token)
    of "label_alt_id":
      atom.label_alt_id = parseValue[string](token)
    of "label_comp_id":
      atom.label_comp_id = parseValue[string](token)
    of "label_asym_id":
      atom.label_asym_id = parseValue[string](token)
    of "label_entity_id":
      atom.label_entity_id = parseValue[int](token)
    of "label_seq_id":
      atom.label_seq_id = parseValue[int](token)
    of "pdbx_PDB_ins_code":
      atom.pdbx_PDB_ins_code = parseValue[string](token)
    of "Cartn_x":
      atom.Cartn_x = parseValue[float](token)
      atom.x = atom.Cartn_x
    of "Cartn_y":
      atom.Cartn_y = parseValue[float](token)
      atom.y = atom.Cartn_y
    of "Cartn_z":
      atom.Cartn_z = parseValue[float](token)
      atom.z = atom.Cartn_z
    of "occupancy":
      atom.occupancy = parseValue[float](token)
    of "B_iso_or_equiv":
      atom.B_iso_or_equiv = parseValue[float](token)
    of "pdbx_formal_charge":
      atom.pdbx_formal_charge = parseValue[string](token)
    of "auth_seq_id":
      atom.auth_seq_id = parseValue[int](token)
    of "auth_comp_id":
      atom.auth_comp_id = parseValue[string](token)
    of "auth_asym_id":
      atom.auth_asym_id = parseValue[string](token)
    of "auth_atom_id":
      atom.auth_atom_id = parseValue[string](token)
    of "pdbx_PDB_model_num":
      atom.pdbx_PDB_model_num = parseValue[int](token)
  
  return atom


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
  if not open(file, filepath):
    raise newException(IOError, "Failed to open file: " & filepath)
  
  defer: close(file)  # Automatically close file when leaving scope
  
  try:
    var line: string
    while file.readLine(line):
      let trimmedLine = line.strip()
      if trimmedLine.startsWith(ATOM_RECORD) or trimmedLine.startsWith(HETATM_RECORD):
        result.atoms.add(parseAtomLine(trimmedLine))
  except IOError as e:
    raise newException(IOError, "Failed to read file: " & e.msg)
  except Exception as e:
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