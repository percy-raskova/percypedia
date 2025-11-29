"""Configuration module - category definitions and schema constants.

Central configuration for:
- Valid schema fields
- Category definitions with keywords for classification (loaded from YAML)
- Default tag vocabulary
- Field migration mappings
"""

from pathlib import Path
from typing import Any, Dict, List, Set

import yaml

# =============================================================================
# Schema Fields
# =============================================================================

SCHEMA_FIELDS: Set[str] = {
    "zkid",
    "author",
    "title",
    "description",
    "date-created",
    "date-edited",
    "category",
    "tags",
    "publish",
    "status",
}

# Ordered list for YAML output
FIELD_ORDER: List[str] = [
    "zkid",
    "author",
    "title",
    "description",
    "date-created",
    "date-edited",
    "category",
    "tags",
    "publish",
    "status",
]

# =============================================================================
# Field Migrations (old name -> new name)
# =============================================================================

FIELD_MIGRATIONS: Dict[str, str] = {
    "id": "zkid",
    "Date": "date-created",
    "Updated": "date-edited",
    "Tags": "tags",
    "Status": "status",
}

# =============================================================================
# Category Definitions (5-Category Intent-Based Schema)
# =============================================================================

# Categories optimized for web navigation based on READER INTENT:
# - Theory: "Teach me about X"
# - Praxis: "Help me do X"
# - Polemics: "Show me who's wrong about X"
# - Creative: "Show me art about X"
# - Meta: "How does this site work?"

# Path to categories YAML file (source of truth)
_CATEGORIES_YAML_PATH = Path(__file__).parent / "categories.yaml"


def _load_categories_from_yaml(filepath: Path) -> Dict[str, Dict[str, Any]]:
    """Load category definitions from YAML file.

    Args:
        filepath: Path to the categories.yaml file

    Returns:
        Dictionary of category definitions

    Raises:
        FileNotFoundError: If YAML file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Categories file not found: {filepath}")

    content = filepath.read_text(encoding="utf-8")
    data = yaml.safe_load(content)

    if not isinstance(data, dict):
        raise ValueError(f"Categories YAML must be a dictionary, got {type(data)}")

    # Validate structure
    for category, definition in data.items():
        if not isinstance(definition, dict):
            raise ValueError(f"Category '{category}' must be a dictionary")
        if "keywords" not in definition:
            raise ValueError(f"Category '{category}' missing 'keywords' field")
        if "example_phrases" not in definition:
            raise ValueError(f"Category '{category}' missing 'example_phrases' field")

    return data


# Load categories at module import time
CATEGORY_DEFINITIONS: Dict[str, Dict[str, Any]] = _load_categories_from_yaml(_CATEGORIES_YAML_PATH)

VALID_CATEGORIES: Set[str] = set(CATEGORY_DEFINITIONS.keys())

# =============================================================================
# Default Tag Vocabulary
# =============================================================================

DEFAULT_TAG_VOCABULARY: Dict[str, List[str]] = {
    "theory": [
        "theory/marxism",
        "theory/dialectics",
        "theory/class-analysis",
        "theory/political-economy",
        "theory/imperialism",
        "theory/state",
    ],
    "philosophy": [
        "philosophy/materialism",
        "philosophy/dialectics",
        "philosophy/epistemology",
        "philosophy/ethics",
    ],
    "politics": [
        "politics/organizing",
        "politics/strategy",
        "politics/party",
        "politics/labor",
        "politics/imperialism",
        "politics/anti-imperialism",
    ],
    "history": [
        "history/labor",
        "history/revolution",
        "history/movements",
        "history/colonialism",
    ],
    "economics": [
        "economics/capitalism",
        "economics/finance",
        "economics/labor",
        "economics/crisis",
    ],
    "praxis": [
        "praxis/organizing",
        "praxis/education",
        "praxis/agitation",
        "praxis/propaganda",
    ],
}

# =============================================================================
# Default Exclusion Patterns
# =============================================================================

DEFAULT_EXCLUDE_PATTERNS: List[str] = [
    "_build",
    "_build/*",
    ".venv",
    ".venv/*",
    "private",
    "private/*",
    ".git",
    ".git/*",
    "__pycache__",
    "__pycache__/*",
    "*.pyc",
    ".obsidian",
    ".obsidian/*",
]

# =============================================================================
# Default Values for New Files
# =============================================================================

DEFAULTS = {
    "author": "Percy",
    "publish": False,
    "status": "draft",
}
