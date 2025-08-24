## Main module for nim_mmcif package
## Re-exports necessary types and provides convenient access to parsing functions

import nim_mmcif/mmcif

# Re-export types and constants
export Atom, mmCIF, ParseError
export ATOM_RECORD, HETATM_RECORD
export tokenizeLine

# Re-export the main parsing functions with their original names
export mmcif_parse, mmcif_parse_batch