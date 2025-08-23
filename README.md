# nim-mmcif

Fast mmCIF (Macromolecular Crystallographic Information File) parser written in Nim with Python bindings

The goal of this repository is to experiment with vibe coding while building something useful for bioinformatics community, to see how much of a cross platform library can be driven to completion by transformers

## Features

- 🚀 High-performance parsing of mmCIF files using Nim
- 🌍 Cross-platform support (Linux, macOS, Windows)
- 📦 Easy installation via pip

## Installation

### Prerequisites

- Python 3.8 or higher
- Nim compiler (see [platform-specific instructions](CROSS_PLATFORM.md))

### From PyPI (when available)

```bash
pip install nim-mmcif
```

### From Source

```bash
# Install Nim (platform-specific, see below)
# macOS: brew install nim
# Linux: curl https://nim-lang.org/choosenim/init.sh -sSf | sh
# Windows: scoop install nim

# Install the package
git clone https://github.com/lucidrains/nim-mmcif
cd nim-mmcif
pip install -e .
```

For detailed platform-specific instructions, see [CROSS_PLATFORM.md](CROSS_PLATFORM.md).

## Quick Start

### Python Usage

```python
import nim_mmcif

# Parse an mmCIF file
data = nim_mmcif.parse_mmcif("path/to/file.mmcif")
print(f"Found {len(data['atoms'])} atoms")

# Parse multiple files using glob patterns
# Returns dict[str, dict] mapping filepaths to parsed data
results = nim_mmcif.parse_mmcif("path/to/*.mmcif")
for filepath, data in results.items():
    print(f"{filepath}: {len(data['atoms'])} atoms")

# Parse with recursive glob patterns
results = nim_mmcif.parse_mmcif("path/**/*.mmcif")
for filepath, data in results.items():
    print(f"{filepath}: {len(data['atoms'])} atoms")

# Get atom count directly
count = nim_mmcif.get_atom_count("path/to/file.mmcif")
print(f"File contains {count} atoms")

# Get all atoms with their properties
atoms = nim_mmcif.get_atoms("path/to/file.mmcif")
for atom in atoms[:5]:  # Print first 5 atoms
    print(f"Atom {atom['id']}: {atom['label_atom_id']} at ({atom['x']}, {atom['y']}, {atom['z']})")

# Get just the 3D coordinates
positions = nim_mmcif.get_atom_positions("path/to/file.mmcif")
for i, (x, y, z) in enumerate(positions[:5]):
    print(f"Position {i}: ({x:.3f}, {y:.3f}, {z:.3f})")
```

### Nim Usage

```nim
import nim_mmcif/mmcif

# Parse an mmCIF file
let data = mmcif_parse("path/to/file.mmcif")
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
```

### Batch Processing

Process multiple mmCIF files efficiently in a single operation:

```python
import nim_mmcif

# List of mmCIF files to process
files = [
    "path/to/structure1.mmcif",
    "path/to/structure2.mmcif",
    "path/to/structure3.mmcif"
]

# Parse all files in batch (returns list when no globs used)
results = nim_mmcif.parse_mmcif_batch(files)

# Process results
for i, data in enumerate(results):
    print(f"Structure {i+1}: {len(data['atoms'])} atoms")
    
    # Analyze each structure
    atoms = data['atoms']
    if atoms:
        # Get unique chain IDs
        chains = set(atom['label_asym_id'] for atom in atoms)
        print(f"  Chains: {', '.join(sorted(chains))}")
        
        # Count residues
        residues = set((atom['label_asym_id'], atom['label_seq_id']) 
                      for atom in atoms)
        print(f"  Residues: {len(residues)}")

# Batch processing with glob patterns (returns dict)
results = nim_mmcif.parse_mmcif_batch("path/to/*.mmcif")
for filepath, data in results.items():
    print(f"{filepath}: {len(data['atoms'])} atoms")

# Mix of glob patterns and regular paths (returns dict)
results = nim_mmcif.parse_mmcif_batch([
    "specific_file.mmcif",
    "structures/*.mmcif",
    "models/model_?.mmcif"
])
for filepath, data in results.items():
    print(f"{filepath}: {len(data['atoms'])} atoms")
```

Batch processing is particularly useful when:
- Analyzing multiple protein structures for comparative studies
- Processing entire datasets of crystallographic structures
- Building machine learning datasets from PDB files
- Performing high-throughput structural analysis

The batch function provides better performance than individual parsing when processing multiple files, as it reduces the overhead of repeated function calls.

## API Reference

### Functions

#### `parse_mmcif(filepath: str) -> dict | dict[str, dict]`
Parse an mmCIF file or files matching a glob pattern.
- **Single file**: Returns a dictionary with parsed data containing 'atoms' key
- **Glob pattern**: Returns a dictionary mapping file paths to parsed data
- Supports wildcards: `*` (any characters), `?` (single character), `**` (recursive)

#### `parse_mmcif_batch(filepaths: list[str] | str) -> list[dict] | dict[str, dict]`
Parse multiple mmCIF files in a single operation.
- **No glob patterns**: Returns a list of dictionaries with parsed data
- **With glob patterns**: Returns a dictionary mapping file paths to parsed data
- Accepts a single path/pattern or a list of paths/patterns
- More efficient than parsing files individually when processing multiple structures

#### `get_atom_count(filepath: str) -> int`
Get the number of atoms in an mmCIF file.

#### `get_atoms(filepath: str) -> list[dict]`
Get all atoms from an mmCIF file as a list of dictionaries.

#### `get_atom_positions(filepath: str) -> list[tuple[float, float, float]]`
Get 3D coordinates of all atoms as a list of (x, y, z) tuples.

### Atom Properties

Each atom dictionary contains:
- `type`: Record type (ATOM or HETATM)
- `id`: Atom serial number
- `label_atom_id`: Atom name
- `label_comp_id`: Residue name
- `label_asym_id`: Chain identifier
- `label_seq_id`: Residue sequence number
- `x`, `y`, `z`: 3D coordinates (aliases for Cartn_x, Cartn_y, Cartn_z)
- `occupancy`: Occupancy factor
- `B_iso_or_equiv`: B-factor
- And more...

## Platform Support

| Platform | Architecture | Python | Status |
|----------|-------------|--------|--------|
| Linux    | x64, ARM64  | 3.8-3.12 | ✅ |
| macOS    | x64, ARM64  | 3.8-3.12 | ✅ |
| Windows  | x64         | 3.8-3.12 | ✅ |

## Building from Source

### Automatic Build

```bash
python build_nim.py
```

### Manual Build

```bash
# Build using nimble tasks
nimble build         # Build debug version
nimble buildRelease  # Build optimized release version
```

## Development

### Running Tests

```bash
pip install pytest
pytest tests/ -v
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Documentation

- [Cross-Platform Guide](CROSS_PLATFORM.md) - Platform-specific build instructions

## Performance

The Nim implementation provides significant performance improvements over pure Python parsers, especially for large mmCIF files commonly used in structural biology.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Nim](https://nim-lang.org/) for high performance
- Python integration via [nimporter](https://github.com/Pebaz/nimporter) and [nimpy](https://github.com/yglukhov/nimpy)
- mmCIF format specification from [wwPDB](https://www.wwpdb.org/)
