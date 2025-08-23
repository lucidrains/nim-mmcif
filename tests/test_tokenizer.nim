import ../nim_mmcif/mmcif

# Test the tokenizer with a sample line
let testLine = """ATOM   1  N   "N A"  .  VAL  A  1  1  ?  6.204   16.869  4.854  1.00  49.05  ?  1  VAL  A  "N A"  1"""

let tokens = tokenizeLine(testLine)

echo "Number of tokens: ", tokens.len
for i, token in tokens:
  echo "Token ", i, ": '", token, "'"