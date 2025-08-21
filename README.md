# nim-mmcif

Fast mmCIF (Macromolecular Crystallographic Information File) parser written in Nim with Python bindings via [nimporter](https://github.com/Pebaz/nimporter).

The goal of this repository is to experiment with vibe coding while building something useful for bioinformatics community, to see how much of a cross platform library can be driven to completion by transformers

## Features

- 🚀 High-performance parsing of mmCIF files using Nim
- 🐍 Seamless Python integration via nimporter
- 🌍 Cross-platform support (Linux, macOS, Windows)
- 🏗️ Automatic compilation on import
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

```python
import nim_mmcif

# Parse an mmCIF file
data = nim_mmcif.parse_mmcif("path/to/file.mmcif")
print(f"Found {len(data['atoms'])} atoms")

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

## API Reference

### Functions

#### `parse_mmcif(filepath: str) -> dict`
Parse an mmCIF file and return a dictionary with parsed data.

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
cd nim_mmcif
nim c --app:lib --out:nim_mmcif.so nim_mmcif.nim  # Linux/macOS
nim c --app:lib --out:nim_mmcif.pyd nim_mmcif.nim  # Windows
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
- [Nimporter Setup](NIMPORTER_SETUP.md) - Details on nimporter integration

## Performance

The Nim implementation provides significant performance improvements over pure Python parsers, especially for large mmCIF files commonly used in structural biology.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Nim](https://nim-lang.org/) for high performance
- Python integration via [nimporter](https://github.com/Pebaz/nimporter) and [nimpy](https://github.com/yglukhov/nimpy)
- mmCIF format specification from [wwPDB](https://www.wwpdb.org/)
