"""Configuration module - category definitions and schema constants.

Central configuration for:
- Valid schema fields
- Category definitions with keywords for classification
- Default tag vocabulary
- Field migration mappings
"""

from typing import Dict, List, Set

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

CATEGORY_DEFINITIONS: Dict[str, Dict] = {
    "Theory": {
        "description": "Explanatory essays, philosophical frameworks, and concept definitions",
        "keywords": [
            "theory", "concept", "philosophy", "dialectics", "materialism",
            "analysis", "framework", "understanding", "explains", "definition",
            "class", "imperialism", "capital", "labor", "exploitation",
            "consciousness", "ideology", "contradiction", "synthesis",
        ],
        "example_phrases": [
            "dialectical materialism explains how contradictions drive historical change",
            "theoretical analysis of labor aristocracy and super-profits",
            "understanding class composition in the imperial core",
            "philosophical foundations of historical materialism",
            "the concept of unequal exchange and global imperialism",
            "materialist analysis of ideology and consciousness",
            "explaining the relationship between base and superstructure",
            "theoretical framework for analyzing class fractions",
            "understanding the political police and state repression",
            "dialectical analysis of capitalist contradiction",
        ],
    },
    "Praxis": {
        "description": "Methodologies, organizing guides, and actionable frameworks",
        "keywords": [
            "how", "guide", "method", "organize", "build", "implement",
            "strategy", "tactic", "step", "practical", "action", "data",
            "api", "collect", "measure", "system", "infrastructure",
            "network", "distribute", "coordinate", "mutual", "aid",
        ],
        "example_phrases": [
            "how to organize using social investigation methodology",
            "step by step guide to building mutual aid networks",
            "data-driven approach to identifying organizing targets",
            "implementing distributed systems for secure communication",
            "practical methodology for class analysis at zip code level",
            "querying federal APIs to gather material conditions data",
            "building cryptographic infrastructure for organizing",
            "how to conduct material investigation in your community",
            "organizing strategy for the lumpenproletariat",
            "designing mesh networks without central authority",
        ],
    },
    "Polemics": {
        "description": "Critiques, arguments against positions, and organizational analysis",
        "keywords": [
            "critique", "against", "argue", "wrong", "expose", "corruption",
            "refute", "debunk", "revisionist", "opportunist", "failure",
            "criticism", "self-criticism", "lesson", "mistake", "betrayal",
        ],
        "example_phrases": [
            "critique of CPUSA corruption and bureaucratic capture",
            "arguing against settler colonial apologism",
            "exposing revisionist positions on imperialism",
            "refuting orthodox marxist dismissal of the lumpen",
            "self-criticism of organizing failures and lessons learned",
            "critique of reformist approaches to socialist politics",
            "arguing against opportunism in the communist movement",
            "exposing corruption in left organizations",
            "critical analysis of failed organizing campaigns",
            "debunking liberal conceptions of police reform",
        ],
    },
    "Creative": {
        "description": "Poetry, satire, fiction, and personal essays",
        "keywords": [
            "poem", "poetry", "story", "satire", "fiction", "creative",
            "narrative", "personal", "reflection", "humor", "verse",
            "literary", "imaginative", "artistic", "essay", "memoir",
        ],
        "example_phrases": [
            "a poem about the transgender bathroom experience",
            "satirical essay on gambling under socialism",
            "personal reflection on identity and political struggle",
            "creative exploration of quantum uncertainty and daily life",
            "humorous fermented thoughts on communist philosophy",
            "poetry about marginalized existence and survival",
            "imaginative narrative exploring contradiction and absurdity",
            "personal essay on the experience of transition",
            "satirical take on everyday life under capitalism",
            "literary exploration of revolutionary themes",
        ],
    },
    "Meta": {
        "description": "Documentation about this knowledge base and its infrastructure",
        "keywords": [
            "documentation", "schema", "sphinx", "extension", "frontmatter",
            "deploy", "cloudflare", "taxonomy", "configuration", "template",
            "build", "validation", "site", "knowledge", "base",
        ],
        "example_phrases": [
            "sphinx extension for category navigation",
            "frontmatter schema validation documentation",
            "cloudflare pages deployment configuration",
            "three-layer taxonomy system documentation",
            "how to configure the knowledge base",
            "sphinx build and deployment workflow",
            "yaml frontmatter field reference",
            "custom extension development for this site",
            "documentation about the publish workflow",
            "technical reference for the schema validator",
        ],
    },
}

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
