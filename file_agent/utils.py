"""Utility functions for the File Agent application."""

import os
from pathlib import Path
from typing import Optional


def validate_path(path: str | Path, base_dir: Optional[Path] = None) -> Path:
    """Validate and normalize a file path to prevent directory traversal attacks.

    Args:
        path: The file path to validate.
        base_dir: Base directory to resolve paths relative to. Defaults to current directory.

    Returns:
        A normalized Path object.

    Raises:
        ValueError: If the path is invalid or attempts directory traversal.
    """
    if base_dir is None:
        base_dir = Path.cwd()

    # Convert to Path object
    file_path = Path(path)

    # Resolve to absolute path
    if file_path.is_absolute():
        resolved = file_path.resolve()
    else:
        resolved = (base_dir / file_path).resolve()

    # Check if path is within base directory
    try:
        resolved.relative_to(base_dir.resolve())
    except ValueError:
        raise ValueError(f"Path {path} is outside the allowed directory")

    return resolved


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to remove potentially dangerous characters.

    Args:
        filename: The filename to sanitize.

    Returns:
        A sanitized filename.
    """
    # Remove path separators and other dangerous characters
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    sanitized = filename
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')

    return sanitized


def get_file_size(path: Path) -> int:
    """Get the size of a file in bytes.

    Args:
        path: Path to the file.

    Returns:
        File size in bytes.
    """
    return path.stat().st_size


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes.

    Returns:
        Human-readable file size string.
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
