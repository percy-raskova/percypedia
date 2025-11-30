"""File operation utilities for Sphinx extensions.

Provides standardized functions for common file operations
like reading markdown files, computing docnames, and writing output.

This is the single source of truth for file I/O patterns.
"""

import json
from pathlib import Path
from typing import Any

__all__ = [
    'compute_docname',
    'read_markdown_file',
    'write_json_file',
    'write_text_file',
]


def compute_docname(md_file: Path, srcdir: Path) -> str:
    """Convert a markdown file path to a Sphinx docname.

    Sphinx docnames are relative paths without the file extension.
    For example: 'theory/marxism.md' -> 'theory/marxism'

    Args:
        md_file: Absolute path to the markdown file
        srcdir: Absolute path to the Sphinx source directory

    Returns:
        The docname string (relative path without extension)

    Example:
        >>> compute_docname(Path('/docs/src/theory/test.md'), Path('/docs/src'))
        'theory/test'
    """
    rel_path = md_file.relative_to(srcdir)
    return str(rel_path.with_suffix(''))


def read_markdown_file(path: Path) -> str:
    """Read a markdown file with consistent UTF-8 encoding.

    Args:
        path: Path to the markdown file

    Returns:
        The file contents as a string

    Raises:
        OSError: If the file cannot be read
    """
    return path.read_text(encoding='utf-8')


def write_json_file(path: Path, data: dict[str, Any]) -> None:
    """Write data to a JSON file with auto-created parent directories.

    Creates parent directories if they don't exist.
    Uses consistent formatting (2-space indent, UTF-8 encoding).

    Args:
        path: Output file path
        data: Dictionary to serialize as JSON

    Example:
        >>> write_json_file(Path('/output/data.json'), {'key': 'value'})
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2),
        encoding='utf-8'
    )


def write_text_file(path: Path, content: str) -> None:
    """Write text content to a file with auto-created parent directories.

    Creates parent directories if they don't exist.
    Uses UTF-8 encoding.

    Args:
        path: Output file path
        content: Text content to write

    Example:
        >>> write_text_file(Path('/output/doc.md'), '# Title')
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
