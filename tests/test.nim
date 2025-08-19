import unittest

import mmcif

test "can parse":
  check mmcif_parse("./test.mmcif").id == 0
