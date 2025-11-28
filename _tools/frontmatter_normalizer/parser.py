"""Parser module - extract frontmatter from markdown content.

Uses the shared _common.frontmatter module for extraction logic.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import yaml


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Parse frontmatter and body from markdown content.

    Args:
        content: Raw markdown content string

    Returns:
        Tuple of (frontmatter_dict, body_string)
        If no valid frontmatter, returns ({}, full_content)
    """
    if not content:
        return {}, ""

    if not content.startswith('---'):
        return {}, content

    lines = content.split('\n')
    if len(lines) < 2:
        return {}, content

    # Find closing delimiter
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        return {}, content

    yaml_content = '\n'.join(lines[1:end_idx])

    # Handle empty frontmatter
    if not yaml_content.strip():
        body = '\n'.join(lines[end_idx + 1:])
        return {}, body

    try:
        result = yaml.safe_load(yaml_content)
        if not isinstance(result, dict):
            return {}, content

        # Body is everything after closing delimiter
        body = '\n'.join(lines[end_idx + 1:])
        return result, body

    except yaml.YAMLError:
        return {}, content


def parse_file(filepath: Path) -> Tuple[Dict[str, Any], str]:
    """Parse frontmatter from a file.

    Args:
        filepath: Path to the markdown file

    Returns:
        Tuple of (frontmatter_dict, body_string)

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    content = filepath.read_text(encoding='utf-8')
    return parse_frontmatter(content)
