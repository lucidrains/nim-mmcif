"""Test cases for glob pattern support in nim_mmcif."""

from __future__ import annotations

import pytest
from pathlib import Path
import nim_mmcif

class TestGlobPatterns:
    """Test glob pattern functionality."""
    
    def test_single_file_no_glob(self):
        """Test that single file without glob returns dict with 'atoms' key."""
        result = nim_mmcif.parse_mmcif("tests/test.mmcif")
        assert isinstance(result, dict)
        assert 'atoms' in result
        assert len(result['atoms']) == 7
    
    def test_glob_star_pattern(self):
        """Test glob pattern with * wildcard."""
        result = nim_mmcif.parse_mmcif("tests/*.mmcif")
        assert isinstance(result, dict)
        assert len(result) >= 3  # At least test.mmcif, test1.mmcif, test2.mmcif
        for filepath, data in result.items():
            assert 'atoms' in data
            assert filepath.endswith('.mmcif')
    
    def test_glob_question_pattern(self):
        """Test glob pattern with ? wildcard."""
        result = nim_mmcif.parse_mmcif("tests/test?.mmcif")
        assert isinstance(result, dict)
        assert len(result) == 2  # test1.mmcif and test2.mmcif
        assert "tests/test1.mmcif" in result
        assert "tests/test2.mmcif" in result
    
    def test_glob_recursive_pattern(self):
        """Test recursive glob pattern with **."""
        result = nim_mmcif.parse_mmcif("tests/**/*.mmcif")
        assert isinstance(result, dict)
        assert len(result) >= 3
        for filepath in result:
            assert filepath.startswith("tests/")
            assert filepath.endswith(".mmcif")
    
    def test_glob_no_matches(self):
        """Test glob pattern with no matches raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="No mmCIF files found matching pattern"):
            nim_mmcif.parse_mmcif("tests/nonexistent*.mmcif")
    
    def test_batch_single_glob(self):
        """Test batch parsing with single glob pattern returns dict."""
        result = nim_mmcif.parse_mmcif_batch("tests/test*.mmcif")
        assert isinstance(result, dict)
        assert len(result) >= 3
        for filepath, data in result.items():
            assert 'atoms' in data
    
    def test_batch_mixed_glob_and_regular(self):
        """Test batch parsing with mix of glob and regular paths returns dict."""
        result = nim_mmcif.parse_mmcif_batch(["tests/test.mmcif", "tests/test?.mmcif"])
        assert isinstance(result, dict)
        # Should have test.mmcif, test1.mmcif, test2.mmcif
        assert len(result) == 3
        assert "tests/test.mmcif" in result
        assert "tests/test1.mmcif" in result
        assert "tests/test2.mmcif" in result
    
    def test_batch_no_glob_returns_list(self):
        """Test batch parsing without glob patterns returns list."""
        result = nim_mmcif.parse_mmcif_batch(["tests/test.mmcif", "tests/test1.mmcif"])
        assert isinstance(result, list)
        assert len(result) == 2
        assert all('atoms' in item for item in result)
    
    def test_glob_preserves_order(self):
        """Test that glob results are sorted for consistent ordering."""
        result = nim_mmcif.parse_mmcif("tests/test*.mmcif")
        filepaths = list(result.keys())
        assert filepaths == sorted(filepaths)
    
    def test_glob_filters_mmcif_extensions(self):
        """Test that glob only returns .mmcif and .cif files."""
        # This test assumes glob expansion filters by extension
        result = nim_mmcif.parse_mmcif("tests/*")
        assert isinstance(result, dict)
        for filepath in result:
            assert filepath.lower().endswith(('.mmcif', '.cif'))
    
    def test_pathlib_path_with_glob(self):
        """Test that Path objects with glob patterns work."""
        result = nim_mmcif.parse_mmcif(Path("tests/*.mmcif"))
        assert isinstance(result, dict)
        assert len(result) >= 3
    
    def test_single_file_as_batch(self):
        """Test that single file path to batch function works."""
        # Without glob - should return list with one item
        result = nim_mmcif.parse_mmcif_batch("tests/test.mmcif")
        assert isinstance(result, list)
        assert len(result) == 1
        assert 'atoms' in result[0]
        
        # With glob - should return dict
        result = nim_mmcif.parse_mmcif_batch("tests/test?.mmcif")
        assert isinstance(result, dict)
        assert len(result) == 2