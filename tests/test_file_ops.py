"""Tests for file operations module."""

import tempfile
from pathlib import Path

import pytest

from file_agent.file_ops import create_file, delete_file, edit_file, list_directory, show_file


class TestCreateFile:
    """Tests for create_file function."""

    def test_create_file_success(self, tmp_path: Path) -> None:
        """Test successful file creation."""
        file_path = tmp_path / "test.txt"
        content = "Hello, World!"

        result = create_file(str(file_path), content)

        assert result["success"] is True
        assert file_path.exists()
        assert file_path.read_text() == content

    def test_create_file_with_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test creating file in non-existent directory (should create it)."""
        file_path = tmp_path / "subdir" / "test.txt"
        content = "Test content"

        result = create_file(str(file_path), content)

        assert result["success"] is True
        assert file_path.exists()

    def test_create_file_invalid_path(self) -> None:
        """Test creating file with invalid path (directory traversal)."""
        invalid_path = "../../../etc/passwd"

        result = create_file(invalid_path, "malicious content")

        assert result["success"] is False
        assert "outside" in result["message"].lower() or "error" in result["message"].lower()


class TestEditFile:
    """Tests for edit_file function."""

    def test_edit_file_replace(self, tmp_path: Path) -> None:
        """Test replacing file content."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Original content")

        result = edit_file(str(file_path), "New content", mode="replace")

        assert result["success"] is True
        assert file_path.read_text() == "New content"

    def test_edit_file_append(self, tmp_path: Path) -> None:
        """Test appending to file."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Original content")

        result = edit_file(str(file_path), "Appended content", mode="append")

        assert result["success"] is True
        assert "Original content\nAppended content" in file_path.read_text()

    def test_edit_file_nonexistent(self, tmp_path: Path) -> None:
        """Test editing non-existent file."""
        file_path = tmp_path / "nonexistent.txt"

        result = edit_file(str(file_path), "Content", mode="replace")

        assert result["success"] is False
        assert "does not exist" in result["message"].lower()


class TestShowFile:
    """Tests for show_file function."""

    def test_show_file_success(self, tmp_path: Path) -> None:
        """Test showing file contents."""
        file_path = tmp_path / "test.txt"
        content = "Test content\nLine 2"
        file_path.write_text(content)

        result = show_file(str(file_path))

        assert result["success"] is True
        assert result["content"] == content
        assert "metadata" in result

    def test_show_file_nonexistent(self, tmp_path: Path) -> None:
        """Test showing non-existent file."""
        file_path = tmp_path / "nonexistent.txt"

        result = show_file(str(file_path))

        assert result["success"] is False
        assert "does not exist" in result["message"].lower()


class TestDeleteFile:
    """Tests for delete_file function."""

    def test_delete_file_success(self, tmp_path: Path) -> None:
        """Test successful file deletion."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Content")

        result = delete_file(str(file_path), confirm=True)

        assert result["success"] is True
        assert not file_path.exists()

    def test_delete_file_without_confirm(self, tmp_path: Path) -> None:
        """Test deletion without confirmation."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Content")

        result = delete_file(str(file_path), confirm=False)

        assert result["success"] is False
        assert file_path.exists()  # File should still exist

    def test_delete_file_nonexistent(self, tmp_path: Path) -> None:
        """Test deleting non-existent file."""
        file_path = tmp_path / "nonexistent.txt"

        result = delete_file(str(file_path), confirm=True)

        assert result["success"] is False
        assert "does not exist" in result["message"].lower()


class TestListDirectory:
    """Tests for list_directory function."""

    def test_list_directory_success(self, tmp_path: Path) -> None:
        """Test listing directory contents."""
        # Create test files and directories
        (tmp_path / "file1.txt").write_text("Content 1")
        (tmp_path / "file2.py").write_text("Content 2")
        (tmp_path / "subdir").mkdir()

        result = list_directory(str(tmp_path))

        assert result["success"] is True
        assert "items" in result
        assert len(result["items"]) == 3

    def test_list_directory_nonexistent(self) -> None:
        """Test listing non-existent directory."""
        result = list_directory("/nonexistent/directory/path")

        assert result["success"] is False
        assert "does not exist" in result["message"].lower()

    def test_list_directory_current(self) -> None:
        """Test listing current directory."""
        result = list_directory(None)

        assert result["success"] is True
        assert "items" in result
