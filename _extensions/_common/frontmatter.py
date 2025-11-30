"""Shared frontmatter parsing for Sphinx extensions.

This is the single source of truth for YAML frontmatter extraction.
All extensions should import from here.
"""

import logging
from typing import Any

import yaml

logger = logging.getLogger(__name__)


def extract_frontmatter(content: str) -> dict[str, Any]:
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
    except yaml.YAMLError as e:
        logger.debug('Invalid YAML frontmatter: %s', e)
        return {}


def _find_frontmatter_boundaries(content: str) -> tuple[list[str], int | None]:
    """Find the closing delimiter index for frontmatter.

    Args:
        content: Raw markdown content that starts with '---'.

    Returns:
        Tuple of (lines, end_idx) where end_idx is the line index of closing '---',
        or None if not found or content is too short.
    """
    lines = content.split('\n')
    if len(lines) < 2:
        return lines, None

    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            return lines, i

    return lines, None


def _parse_yaml_frontmatter(
    yaml_content: str, lines: list[str], end_idx: int, original_content: str
) -> tuple[dict[str, Any], str]:
    """Parse YAML content and return frontmatter dict with body.

    Args:
        yaml_content: The YAML string between delimiters.
        lines: All lines of the original content.
        end_idx: Index of closing delimiter.
        original_content: Original content for fallback return.

    Returns:
        Tuple of (frontmatter_dict, body_string).
    """
    # Handle empty frontmatter
    if not yaml_content.strip():
        return {}, '\n'.join(lines[end_idx + 1:])

    try:
        result = yaml.safe_load(yaml_content)
        if not isinstance(result, dict):
            return {}, original_content

        return result, '\n'.join(lines[end_idx + 1:])

    except yaml.YAMLError as e:
        logger.debug('Invalid YAML frontmatter in parse_frontmatter: %s', e)
        return {}, original_content


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
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

    lines, end_idx = _find_frontmatter_boundaries(content)

    if end_idx is None:
        return {}, content

    yaml_content = '\n'.join(lines[1:end_idx])
    return _parse_yaml_frontmatter(yaml_content, lines, end_idx, content)
