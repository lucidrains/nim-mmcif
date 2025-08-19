# imports

import std/[sequtils]

# types

type
  mmCIF = object
    id*: int

# functions

# parsing the mmcif from a given filepath

proc mmcif_parse*(
  filepath: string
): mmCIF =

  mmCIF(id: 0)
