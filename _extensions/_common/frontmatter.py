"""Shared frontmatter parsing for Sphinx extensions.

This is the single source of truth for YAML frontmatter extraction.
All extensions should import from here.
"""

from typing import Any, Dict
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
