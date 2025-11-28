"""Writer module - render frontmatter to YAML format.

Handles:
- Field ordering (schema order)
- YAML formatting (quoted strings, arrays, booleans)
- File writing with backup support
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .config import FIELD_ORDER


class QuotedString(str):
    """String that should be quoted in YAML output."""
    pass


def _quoted_representer(dumper, data):
    """Custom representer to quote strings."""
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")


# Register custom representer
yaml.add_representer(QuotedString, _quoted_representer)


def render_frontmatter(frontmatter: Dict[str, Any], body: str) -> str:
    """Render frontmatter dict and body to full markdown content.

    Args:
        frontmatter: Dictionary of frontmatter fields
        body: Body content (markdown)

    Returns:
        Full markdown content with frontmatter
    """
    if not frontmatter:
        return f"---\n---\n{body}"

    # Order fields according to schema
    ordered = _order_fields(frontmatter)

    # Format values for YAML
    formatted = _format_values(ordered)

    # Render to YAML
    yaml_content = yaml.dump(
        formatted,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=1000,  # Prevent line wrapping
    )

    # Ensure body has leading newline
    if body and not body.startswith('\n'):
        body = '\n' + body

    return f"---\n{yaml_content}---{body}"


def _order_fields(frontmatter: Dict[str, Any]) -> Dict[str, Any]:
    """Order frontmatter fields according to schema priority."""
    ordered = {}

    # Add fields in schema order
    for field in FIELD_ORDER:
        if field in frontmatter:
            ordered[field] = frontmatter[field]

    # Add any remaining fields (shouldn't happen with strict schema)
    for key, value in frontmatter.items():
        if key not in ordered:
            ordered[key] = value

    return ordered


def _format_values(frontmatter: Dict[str, Any]) -> Dict[str, Any]:
    """Format values for YAML serialization.

    - Quote strings that need it (dates, zkid, special chars)
    - Preserve booleans as lowercase
    - Keep arrays as arrays
    """
    formatted = {}

    for key, value in frontmatter.items():
        if key == 'zkid':
            # Always quote zkid to preserve as string
            formatted[key] = QuotedString(value)
        elif key in ('date-created', 'date-edited'):
            # Quote dates to prevent YAML date parsing
            formatted[key] = QuotedString(value)
        elif isinstance(value, str):
            # Quote strings with special characters
            if any(c in value for c in ':{}[]&*#?|->!%@`'):
                formatted[key] = QuotedString(value)
            else:
                formatted[key] = value
        elif isinstance(value, bool):
            # Booleans stay as booleans (yaml renders as true/false)
            formatted[key] = value
        elif isinstance(value, list):
            # Arrays stay as arrays
            formatted[key] = value
        else:
            formatted[key] = value

    return formatted


def write_file(
    filepath: Path,
    frontmatter: Dict[str, Any],
    body: str,
    backup: bool = True,
    dry_run: bool = False,
) -> None:
    """Write normalized content to file.

    Args:
        filepath: Path to the file
        frontmatter: Frontmatter dictionary
        body: Body content
        backup: Whether to create .bak backup
        dry_run: If True, don't actually write
    """
    filepath = Path(filepath)

    if dry_run:
        return

    # Create backup if requested and file exists
    if backup and filepath.exists():
        backup_path = filepath.with_suffix(filepath.suffix + '.bak')
        backup_path.write_text(filepath.read_text(encoding='utf-8'), encoding='utf-8')

    # Render and write content
    content = render_frontmatter(frontmatter, body)
    filepath.write_text(content, encoding='utf-8')
