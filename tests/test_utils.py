"""Tests for utility functions."""

import tempfile
from pathlib import Path

import pytest

from file_agent.utils import (
    format_file_size,
    get_file_size,
    sanitize_filename,
    validate_path,
)


class TestValidatePath:
    """Tests for validate_path function."""

    def test_validate_path_relative(self, tmp_path: Path) -> None:
        """Test validating a relative path."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("test")

        result = validate_path("test.txt", base_dir=tmp_path)

        assert result == file_path.resolve()

    def test_validate_path_absolute(self, tmp_path: Path) -> None:
        """Test validating an absolute path."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("test")

        result = validate_path(str(file_path.resolve()))

        assert result == file_path.resolve()

    def test_validate_path_directory_traversal(self, tmp_path: Path) -> None:
        """Test that directory traversal is prevented."""
        with pytest.raises(ValueError, match="outside"):
            validate_path("../../../etc/passwd", base_dir=tmp_path)


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_sanitize_filename_normal(self) -> None:
        """Test sanitizing a normal filename."""
        assert sanitize_filename("test.txt") == "test.txt"

    def test_sanitize_filename_dangerous_chars(self) -> None:
        """Test sanitizing filename with dangerous characters."""
        assert sanitize_filename("test/../file.txt") == "test___file.txt"
        assert sanitize_filename("file<>name.txt") == "file__name.txt"

    def test_sanitize_filename_leading_trailing(self) -> None:
        """Test sanitizing filename with leading/trailing dots."""
        assert sanitize_filename("..test.txt..") == "test.txt"


class TestFileSize:
    """Tests for file size functions."""

    def test_get_file_size(self, tmp_path: Path) -> None:
        """Test getting file size."""
        file_path = tmp_path / "test.txt"
        content = "test content"
        file_path.write_text(content)

        size = get_file_size(file_path)

        assert size == len(content.encode('utf-8'))

    def test_format_file_size(self) -> None:
        """Test formatting file sizes."""
        assert format_file_size(0) == "0.0 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1048576) == "1.0 MB"
        assert format_file_size(1073741824) == "1.0 GB"
