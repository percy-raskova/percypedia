"""Frontmatter Normalizer - idempotent markdown frontmatter normalization.

This tool normalizes YAML frontmatter in markdown files to match a schema:
- Migrates old field names to new names
- Discards non-schema fields
- Infers missing fields using NLP and file metadata
- Preserves body content exactly
"""

from .normalizer import normalize, Normalizer, NormalizationResult
from .parser import parse_frontmatter, parse_file
from .writer import render_frontmatter, write_file

__version__ = "0.1.0"

__all__ = [
    "normalize",
    "Normalizer",
    "NormalizationResult",
    "parse_frontmatter",
    "parse_file",
    "render_frontmatter",
    "write_file",
]
