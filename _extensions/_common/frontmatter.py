"""Shared frontmatter parsing for Sphinx extensions.

This is the single source of truth for YAML frontmatter extraction.
All extensions should import from here.
"""

from typing import Any, Dict, Tuple
import yaml


def extract_frontmatter(content: str) -> Dict[str, Any]:
    """Extract YAML frontmatter from markdown content.

    Args:
        content: Raw markdown file content.

    Returns:
        Dictionary of frontmatter fields. Empty dict if:
        - No frontmatter present
        - Frontmatter doesn't start at line 1
        - Unclosed frontmatter
        - Invalid YAML
        - YAML parses to non-dict (string, list, etc.)

    Example:
        >>> content = '''---
        ... title: My Document
        ... tags:
        ...   - theory/marxism
        ... ---
        ... # Content here
        ... '''
        >>> extract_frontmatter(content)
        {'title': 'My Document', 'tags': ['theory/marxism']}
    """
    # Frontmatter must start at beginning of file
    if not content.startswith('---'):
        return {}

    lines = content.split('\n')
    if len(lines) < 2:
        return {}

    # Find closing delimiter
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        return {}

    # Extract and parse YAML
    yaml_content = '\n'.join(lines[1:end_idx])
    try:
        result = yaml.safe_load(yaml_content)
        return result if isinstance(result, dict) else {}
    except yaml.YAMLError:
        return {}


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Parse frontmatter and body from markdown content.

    This is the extended version that returns both frontmatter and body,
    used by the frontmatter_normalizer tool.

    Args:
        content: Raw markdown file content.

    Returns:
        Tuple of (frontmatter_dict, body_string).
        If no valid frontmatter, returns ({}, full_content).
        Empty frontmatter returns ({}, body).

    Example:
        >>> content = '''---
        ... title: My Doc
        ... ---
        ... # Heading
        ... Body text
        ... '''
        >>> fm, body = parse_frontmatter(content)
        >>> fm
        {'title': 'My Doc'}
        >>> body
        '\\n# Heading\\nBody text\\n'
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
