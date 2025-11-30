"""Frontmatter Normalizer - idempotent markdown frontmatter normalization.

This tool normalizes YAML frontmatter in markdown files to match a schema:
- Migrates old field names to new names
- Discards non-schema fields
- Infers missing fields using NLP and file metadata
- Preserves body content exactly
"""

from .normalizer import NormalizationResult, Normalizer, normalize
from .parser import parse_file, parse_frontmatter
from .writer import render_frontmatter, write_file

__version__ = "0.1.0"

__all__ = [
    "NormalizationResult",
    "Normalizer",
    "normalize",
    "parse_file",
    "parse_frontmatter",
    "render_frontmatter",
    "write_file",
]
