"""Shared utilities for Sphinx extensions.

Exports:
    - frontmatter: extract_frontmatter, parse_frontmatter
    - traversal: iter_markdown_files
"""

from .frontmatter import extract_frontmatter, parse_frontmatter
from .traversal import iter_markdown_files

__all__ = [
    'extract_frontmatter',
    'parse_frontmatter',
    'iter_markdown_files',
]
