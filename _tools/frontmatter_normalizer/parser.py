"""Parser module - extract frontmatter from markdown content.

Imports from the shared _extensions/_common/frontmatter module for extraction logic.
This ensures consistent parsing between Sphinx extensions and the normalizer tool.
"""

import sys
from pathlib import Path
from typing import Any

# Add _extensions to path if not already available
# This handles both:
# 1. Running from repo root (Sphinx builds)
# 2. Running from _tools directory (tool tests)
_repo_root = Path(__file__).parent.parent.parent
_extensions_path = _repo_root / "_extensions"
if str(_extensions_path) not in sys.path:
    sys.path.insert(0, str(_extensions_path))

# Import from the authoritative source
from _common.frontmatter import extract_frontmatter, parse_frontmatter  # noqa: E402


def parse_file(filepath: Path) -> tuple[dict[str, Any], str]:
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


__all__ = ["extract_frontmatter", "parse_file", "parse_frontmatter"]
