# frontmatter_schema - Validation utilities for Percypedia frontmatter
#
# Provides JSON Schema validation for YAML frontmatter in markdown documents.
# The canonical schema lives in _schemas/frontmatter.schema.json.
#
# Usage:
#   from frontmatter_schema import validate_frontmatter, extract_and_validate
#   errors = validate_frontmatter({'title': 'Test', 'tags': ['foo/bar']})
#   errors = extract_and_validate(markdown_content)

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import from shared module, re-export for backward compatibility
from _common.frontmatter import extract_frontmatter
from _common.traversal import iter_markdown_files
from _common.paths import SCHEMAS_DIR, EXCLUDE_PATTERNS

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


# Path to the canonical schema (from centralized paths)
SCHEMA_PATH = SCHEMAS_DIR / 'frontmatter.schema.json'


# Re-export for backward compatibility
__all__ = ['extract_frontmatter', 'validate_frontmatter', 'extract_and_validate',
           'validate_file', 'validate_directory', 'load_schema']


def load_schema() -> Dict[str, Any]:
    """Load the frontmatter JSON schema from disk.

    Returns:
        The parsed JSON schema as a dictionary.

    Raises:
        FileNotFoundError: If schema file doesn't exist.
        json.JSONDecodeError: If schema is invalid JSON.
    """
    return json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))


def validate_frontmatter(
    frontmatter: Dict[str, Any],
    schema: Optional[Dict[str, Any]] = None,
) -> List[str]:
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


def extract_and_validate(content: str, schema: Optional[Dict[str, Any]] = None) -> List[str]:
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


def validate_file(filepath: Path, schema: Optional[Dict[str, Any]] = None) -> List[str]:
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
    schema: Optional[Dict[str, Any]] = None,
    exclude_patterns: Optional[List[str]] = None,
) -> Dict[str, List[str]]:
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
