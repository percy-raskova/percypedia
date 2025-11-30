"""Configuration module - category definitions and schema constants.

Central configuration for:
- Valid schema fields
- Category definitions with keywords for classification (loaded from YAML)
- Default tag vocabulary
- Field migration mappings
"""

import sys
from pathlib import Path
from typing import Any

import yaml

# Add _extensions to path for centralized imports
_EXTENSIONS_PATH = Path(__file__).parent.parent.parent / '_extensions'
if str(_EXTENSIONS_PATH) not in sys.path:
    sys.path.insert(0, str(_EXTENSIONS_PATH))

# =============================================================================
# Schema Fields
# =============================================================================

SCHEMA_FIELDS: set[str] = {
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
FIELD_ORDER: list[str] = [
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

FIELD_MIGRATIONS: dict[str, str] = {
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


def _load_categories_from_yaml(filepath: Path) -> dict[str, dict[str, Any]]:
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
CATEGORY_DEFINITIONS: dict[str, dict[str, Any]] = _load_categories_from_yaml(_CATEGORIES_YAML_PATH)

VALID_CATEGORIES: set[str] = set(CATEGORY_DEFINITIONS.keys())

# =============================================================================
# Default Tag Vocabulary
# =============================================================================

DEFAULT_TAG_VOCABULARY: dict[str, list[str]] = {
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

# Import centralized patterns (includes infrastructure dirs, build artifacts, etc.)
from _common.paths import EXCLUDE_PATTERNS

DEFAULT_EXCLUDE_PATTERNS: list[str] = EXCLUDE_PATTERNS

# =============================================================================
# Default Values for New Files
# =============================================================================

DEFAULTS = {
    "author": "Percy",
    "publish": False,
    "status": "draft",
}
