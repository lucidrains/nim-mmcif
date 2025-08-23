#!/bin/bash

# Test script for hatch build

echo "Testing hatch build system..."

# Clean up any previous builds
rm -rf dist/ build/ *.egg-info

# Install hatch if not already installed
pip install hatch hatch-build-scripts

# Try building the wheel
echo "Building wheel with hatch..."
hatch build -t wheel

# Check if the wheel was created
if ls dist/*.whl 1> /dev/null 2>&1; then
    echo "✓ Wheel built successfully!"
    ls -la dist/
else
    echo "✗ Wheel build failed"
    exit 1
fi

echo "Build test completed successfully!"