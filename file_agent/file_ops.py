"""File operation utilities for the File Agent."""

import os
from pathlib import Path
from typing import Literal

from rich.console import Console
from rich.syntax import Syntax

from file_agent.config import config
from file_agent.utils import format_file_size, get_file_size, sanitize_filename, validate_path

console = Console()


def create_file(path: str, content: str) -> dict[str, str | bool]:
    """Create a new file with the specified content.

    Creates a new file at the specified path with the given content. The path
    is validated to prevent directory traversal attacks, and parent directories
    are created automatically if they don't exist. File size is checked against
    the configured maximum.

    Args:
        path: Path where the file should be created (relative to current directory).
            Parent directories will be created automatically if needed.
        content: Content to write to the file. Must be UTF-8 encodable.

    Returns:
        Dictionary with operation result containing:
            - success (bool): True if the file was created successfully, False otherwise
            - message (str): Success message or error description
            - path (str): The resolved file path (absolute or relative)

    Note:
        Path validation prevents directory traversal attacks. File size must not
        exceed MAX_FILE_SIZE configuration (default 10MB). All files are written
        with UTF-8 encoding. If the file already exists, it will be overwritten.
    """
    try:
        # Validate and sanitize path
        file_path = validate_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Check file size
        content_size = len(content.encode('utf-8'))
        if content_size > config.max_file_size:
            return {
                "success": False,
                "message": f"File content exceeds maximum size of {format_file_size(config.max_file_size)}",
                "path": str(file_path),
            }

        # Write file
        file_path.write_text(content, encoding='utf-8')

        return {
            "success": True,
            "message": f"File created successfully: {file_path}",
            "path": str(file_path),
        }
    except ValueError as e:
        return {"success": False, "message": str(e), "path": path}
    except Exception as e:
        return {"success": False, "message": f"Error creating file: {str(e)}", "path": path}


def edit_file(
    path: str, content: str, mode: Literal["replace", "append"] = "replace"
) -> dict[str, str | bool]:
    """Edit an existing file.

    Modifies an existing file by either replacing its entire content or appending
    new content to the end. The file must exist before editing. File size after
    the edit is checked against the configured maximum.

    Args:
        path: Path to the file to edit (relative to current directory).
            The file must already exist.
        content: Content to add or replace. In replace mode, this becomes the
            entire file content. In append mode, this is added after a newline.
        mode: Edit mode - "replace" to overwrite the entire file, "append" to
            add content at the end. Defaults to "replace".

    Returns:
        Dictionary with operation result containing:
            - success (bool): True if the file was edited successfully, False otherwise
            - message (str): Success message or error description
            - path (str): The resolved file path (absolute or relative)

    Note:
        The file must exist before editing. In append mode, a newline is inserted
        between existing content and new content. File size after edit must not
        exceed MAX_FILE_SIZE configuration. Path validation prevents directory
        traversal attacks.
    """
    try:
        file_path = validate_path(path)

        if not file_path.exists():
            return {
                "success": False,
                "message": f"File does not exist: {file_path}",
                "path": str(file_path),
            }

        # Check file size
        current_size = get_file_size(file_path)
        content_size = len(content.encode('utf-8'))
        new_size = current_size + content_size if mode == "append" else content_size

        if new_size > config.max_file_size:
            return {
                "success": False,
                "message": f"File would exceed maximum size of {format_file_size(config.max_file_size)}",
                "path": str(file_path),
            }

        # Read existing content if appending
        if mode == "append":
            existing_content = file_path.read_text(encoding='utf-8')
            new_content = existing_content + "\n" + content
        else:
            new_content = content

        # Write file
        file_path.write_text(new_content, encoding='utf-8')

        return {
            "success": True,
            "message": f"File edited successfully: {file_path}",
            "path": str(file_path),
        }
    except ValueError as e:
        return {"success": False, "message": str(e), "path": path}
    except Exception as e:
        return {"success": False, "message": f"Error editing file: {str(e)}", "path": path}


def show_file(path: str) -> dict[str, str | bool | dict]:
    """Display file contents with syntax highlighting.

    Reads and returns the contents of a file along with metadata. The file must
    exist and not exceed the maximum file size limit. Language for syntax
    highlighting is automatically determined from the file extension.

    Args:
        path: Path to the file to display (relative to current directory).
            The file must exist.

    Returns:
        Dictionary with operation result containing:
            - success (bool): True if the file was read successfully, False otherwise
            - message (str): Success message or error description
            - path (str): The resolved file path
            - content (str): The file contents (only if success is True)
            - metadata (dict): File metadata including:
                - path (str): File path
                - size (str): Human-readable file size
                - modified (float): Modification timestamp
                - extension (str): File extension
            - language (str): Language identifier for syntax highlighting

    Note:
        The file must exist and not exceed MAX_FILE_SIZE configuration. Language
        detection supports common file types (Python, JavaScript, TypeScript,
        HTML, CSS, JSON, Markdown, YAML, TOML, Bash, Rust, Go, Java, C++, C).
        Unknown extensions default to "text". Path validation prevents directory
        traversal attacks.
    """
    try:
        file_path = validate_path(path)

        if not file_path.exists():
            return {
                "success": False,
                "message": f"File does not exist: {file_path}",
                "path": str(file_path),
            }

        # Check file size
        file_size = get_file_size(file_path)
        if file_size > config.max_file_size:
            return {
                "success": False,
                "message": f"File exceeds maximum size of {format_file_size(config.max_file_size)}",
                "path": str(file_path),
            }

        # Read file content
        content = file_path.read_text(encoding='utf-8')

        # Get file metadata
        stat = file_path.stat()
        metadata = {
            "path": str(file_path),
            "size": format_file_size(file_size),
            "modified": stat.st_mtime,
            "extension": file_path.suffix,
        }

        # Determine language for syntax highlighting
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".html": "html",
            ".css": "css",
            ".json": "json",
            ".md": "markdown",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".sh": "bash",
            ".rs": "rust",
            ".go": "go",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
        }
        language = language_map.get(file_path.suffix, "text")

        return {
            "success": True,
            "message": "File displayed successfully",
            "path": str(file_path),
            "content": content,
            "metadata": metadata,
            "language": language,
        }
    except ValueError as e:
        return {"success": False, "message": str(e), "path": path}
    except Exception as e:
        return {"success": False, "message": f"Error reading file: {str(e)}", "path": path}


def delete_file(path: str, confirm: bool = False) -> dict[str, str | bool]:
    """Delete a file with optional confirmation.

    Permanently deletes a file from the filesystem. This operation is irreversible.
    The file must exist and deletion must be explicitly confirmed.

    Args:
        path: Path to the file to delete (relative to current directory).
            The file must exist.
        confirm: Whether deletion is confirmed. Must be True to actually delete
            the file. If False, the operation will fail with a confirmation error.

    Returns:
        Dictionary with operation result containing:
            - success (bool): True if the file was deleted successfully, False otherwise
            - message (str): Success message or error description
            - path (str): The resolved file path (absolute or relative)

    Warning:
        This operation is irreversible. Once a file is deleted, it cannot be
        recovered. Always ensure you have backups if needed.

    Note:
        The file must exist before deletion. Only files can be deleted, not
        directories. Path validation prevents directory traversal attacks.
        Confirmation is required to prevent accidental deletions.
    """
    try:
        file_path = validate_path(path)

        if not file_path.exists():
            return {
                "success": False,
                "message": f"File does not exist: {file_path}",
                "path": str(file_path),
            }

        if not confirm:
            return {
                "success": False,
                "message": "Deletion not confirmed. Use confirm=True to delete.",
                "path": str(file_path),
            }

        # Delete file
        file_path.unlink()

        return {
            "success": True,
            "message": f"File deleted successfully: {file_path}",
            "path": str(file_path),
        }
    except ValueError as e:
        return {"success": False, "message": str(e), "path": path}
    except Exception as e:
        return {"success": False, "message": f"Error deleting file: {str(e)}", "path": path}


def list_directory(path: str | None = None) -> dict[str, str | bool | list]:
    """List directory contents.

    Retrieves and returns a list of files and subdirectories in the specified
    directory. Files include their sizes, directories are marked accordingly.
    The listing is sorted alphabetically.

    Args:
        path: Path to directory to list. If None, lists the current working
            directory. The path must exist and be a directory.

    Returns:
        Dictionary with operation result containing:
            - success (bool): True if the directory was listed successfully, False otherwise
            - message (str): Success message or error description
            - path (str): The resolved directory path
            - items (list): List of dictionaries, each containing:
                - name (str): Item name
                - type (str): "file" or "directory"
                - size (str | None): Human-readable file size for files, None for directories

    Note:
        The path must exist and be a directory (not a file). Items are sorted
        alphabetically. File sizes are formatted in human-readable format (B, KB,
        MB, GB). Path validation prevents directory traversal attacks. Empty
        directories return an empty items list.
    """
    try:
        if path is None:
            dir_path = Path.cwd()
        else:
            dir_path = validate_path(path)

        if not dir_path.exists():
            return {
                "success": False,
                "message": f"Directory does not exist: {dir_path}",
                "path": str(dir_path),
            }

        if not dir_path.is_dir():
            return {
                "success": False,
                "message": f"Path is not a directory: {dir_path}",
                "path": str(dir_path),
            }

        # List directory contents
        items = []
        for item in sorted(dir_path.iterdir()):
            if item.is_file():
                size = format_file_size(get_file_size(item))
                items.append({"name": item.name, "type": "file", "size": size})
            else:
                items.append({"name": item.name, "type": "directory", "size": None})

        return {
            "success": True,
            "message": f"Directory listed successfully: {dir_path}",
            "path": str(dir_path),
            "items": items,
        }
    except ValueError as e:
        return {"success": False, "message": str(e), "path": str(path) if path else "."}
    except Exception as e:
        return {
            "success": False,
            "message": f"Error listing directory: {str(e)}",
            "path": str(path) if path else ".",
        }
