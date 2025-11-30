# frontmatter_schema - Validation utilities for Percypedia frontmatter
#
# Provides JSON Schema validation for YAML frontmatter in markdown documents.
# The canonical schema lives in _schemas/frontmatter.schema.json.
#
# This module provides validate_frontmatter() and extract_and_validate() functions
# for validating YAML frontmatter against the JSON schema.

import json
from pathlib import Path
from typing import Any

# Import from shared module, re-export for backward compatibility
from _common.frontmatter import extract_frontmatter
from _common.paths import EXCLUDE_PATTERNS, SCHEMAS_DIR
from _common.traversal import iter_markdown_files

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


# Path to the canonical schema (from centralized paths)
SCHEMA_PATH = SCHEMAS_DIR / 'frontmatter.schema.json'


# Re-export for backward compatibility
__all__ = [
    'extract_and_validate',
    'extract_frontmatter',
    'load_schema',
    'validate_directory',
    'validate_file',
    'validate_frontmatter',
]


def load_schema() -> dict[str, Any]:
    """Load the frontmatter JSON schema from disk.

    Returns:
        The parsed JSON schema as a dictionary.

    Raises:
        FileNotFoundError: If schema file doesn't exist.
        json.JSONDecodeError: If schema is invalid JSON.
    """
    return json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))


def validate_frontmatter(
    frontmatter: dict[str, Any],
    schema: dict[str, Any] | None = None,
) -> list[str]:
    """Validate frontmatter against the JSON schema.

    Args:
        frontmatter: Dictionary of frontmatter fields to validate.
        schema: Optional schema dict. Loads from disk if not provided.

    Returns:
        List of validation error messages. Empty list if valid.

    Raises:
        ImportError: If jsonschema package is not installed.
    """
    if not HAS_JSONSCHEMA:
        raise ImportError(
            "jsonschema package required for validation. "
            "Install with: pip install jsonschema"
        )

    if schema is None:
        schema = load_schema()

    validator = jsonschema.Draft7Validator(schema)
    errors = []

    for error in validator.iter_errors(frontmatter):
        # Build a readable error message
        path = '.'.join(str(p) for p in error.absolute_path) if error.absolute_path else 'root'
        errors.append(f"{path}: {error.message}")

    return errors


def extract_and_validate(content: str, schema: dict[str, Any] | None = None) -> list[str]:
    """Extract frontmatter from markdown and validate against schema.

    Convenience function combining extraction and validation.

    Args:
        content: Raw markdown file content.
        schema: Optional schema dict. Loads from disk if not provided.

    Returns:
        List of validation error messages. Empty list if valid.
    """
    frontmatter = extract_frontmatter(content)
    if not frontmatter:
        return []  # No frontmatter is valid (all fields optional)
    return validate_frontmatter(frontmatter, schema)


def validate_file(filepath: Path, schema: dict[str, Any] | None = None) -> list[str]:
    """Validate a markdown file's frontmatter against the schema.

    Args:
        filepath: Path to the markdown file.
        schema: Optional schema dict. Loads from disk if not provided.

    Returns:
        List of validation error messages. Empty list if valid.
    """
    content = filepath.read_text(encoding='utf-8')
    return extract_and_validate(content, schema)


def validate_directory(
    dirpath: Path,
    schema: dict[str, Any] | None = None,
    exclude_patterns: list[str] | None = None,
) -> dict[str, list[str]]:
    """Validate all markdown files in a directory.

    Args:
        dirpath: Path to directory to scan.
        schema: Optional schema dict. Loads from disk if not provided.
        exclude_patterns: Directory names to skip (default: ['.venv', '_build', 'private']).

    Returns:
        Dict mapping relative file paths to lists of errors.
        Only files with errors are included.
    """
    if exclude_patterns is None:
        exclude_patterns = EXCLUDE_PATTERNS

    if schema is None:
        schema = load_schema()

    results = {}

    # Use shared traversal - frontmatter_schema skips underscore dirs but NOT underscore files
    for md_file in iter_markdown_files(
        dirpath,
        exclude_patterns=exclude_patterns,
        skip_underscore_files=False,  # Validate _file.md too
        skip_underscore_dirs=True,
        skip_dot_dirs=True,
    ):
        errors = validate_file(md_file, schema)
        if errors:
            rel_path = md_file.relative_to(dirpath)
            results[str(rel_path)] = errors

    return results
