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

    Args:
        path: Path where the file should be created.
        content: Content to write to the file.

    Returns:
        Dictionary with operation result: {"success": bool, "message": str, "path": str}
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

    Args:
        path: Path to the file to edit.
        content: Content to add or replace.
        mode: Edit mode - "replace" to overwrite, "append" to add at the end.

    Returns:
        Dictionary with operation result: {"success": bool, "message": str, "path": str}
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

    Args:
        path: Path to the file to display.

    Returns:
        Dictionary with operation result and file metadata.
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

    Args:
        path: Path to the file to delete.
        confirm: Whether deletion is confirmed (should be True to actually delete).

    Returns:
        Dictionary with operation result: {"success": bool, "message": str, "path": str}
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

    Args:
        path: Path to directory to list. If None, lists current directory.

    Returns:
        Dictionary with operation result and directory contents.
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
