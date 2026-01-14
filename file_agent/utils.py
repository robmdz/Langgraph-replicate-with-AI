"""Utility functions for the File Agent application."""

import os
from pathlib import Path
from typing import Optional


def validate_path(path: str | Path, base_dir: Optional[Path] = None) -> Path:
    """Validate and normalize a file path to prevent directory traversal attacks.

    This function is a critical security measure that prevents directory traversal
    attacks (e.g., "../../etc/passwd"). It resolves the path to an absolute path
    and ensures it stays within the base directory boundary.

    Args:
        path: The file path to validate. Can be a string or Path object, relative
            or absolute. The path will be resolved to an absolute path.
        base_dir: Base directory to resolve paths relative to. If None, uses the
            current working directory. All resolved paths must be within this base
            directory.

    Returns:
        A normalized Path object representing the resolved absolute path. The path
        is guaranteed to be within the base directory.

    Raises:
        ValueError: If the resolved path is outside the base directory, indicating
            a potential directory traversal attack. The error message includes the
            original path that was rejected.

    Security Note:
        This function is essential for preventing directory traversal attacks. It
        uses Path.relative_to() to ensure the resolved path is a subpath of the
        base directory. This prevents access to files outside the intended working
        directory, even with paths containing ".." or absolute paths.
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

    Removes or replaces characters that could be dangerous in filenames, such as
    path separators, wildcards, and other special characters that could cause
    issues in file operations.

    Args:
        filename: The filename to sanitize. This should be just the filename,
            not a full path.

    Returns:
        A sanitized filename with dangerous characters replaced by underscores.
        Leading and trailing dots and spaces are also removed.

    Security Note:
        This function helps prevent issues with filenames that contain special
        characters. Dangerous characters include: /, \\, .., <, >, :, ", |, ?, *.
        All of these are replaced with underscores. This is a defense-in-depth
        measure, but path validation (validate_path) is the primary security
        mechanism.
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

    Retrieves the size of a file using the filesystem's stat information.
    The file must exist and be readable.

    Args:
        path: Path to the file. The file must exist.

    Returns:
        File size in bytes as an integer.

    Raises:
        OSError: If the file doesn't exist or cannot be accessed. This is raised
            by path.stat() if the file is not accessible.

    Note:
        This function uses Path.stat().st_size to get the file size. The size
        represents the actual disk space used by the file.
    """
    return path.stat().st_size


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Converts a file size in bytes to a human-readable string with appropriate
    units (B, KB, MB, GB, TB). The function automatically selects the most
    appropriate unit based on the size.

    Args:
        size_bytes: Size in bytes as an integer. Should be non-negative.

    Returns:
        A formatted string with the size and unit, e.g., "1.5 MB", "1024.0 B",
        "2.3 GB". The size is displayed with one decimal place.

    Note:
        The function uses binary units (1024 bytes per KB, etc.). Units are
        selected by dividing by 1024 until the result is less than 1024. The
        maximum unit is TB (terabytes).
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
