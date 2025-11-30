"""Constants for the missing_refs extension."""

__all__ = [
    'DEFAULT_PAGE_PATH',
    'DEFAULT_PAGE_TITLE',
    'JSON_OUTPUT_FILENAME',
    'REFTYPE_DOC',
    'UNCATEGORIZED',
    'UNKNOWN_SOURCE',
    '__version__',
]

# Extension metadata
__version__ = '0.1.0'

# Reference types we track
REFTYPE_DOC = 'doc'

# Category grouping
UNCATEGORIZED = 'uncategorized'

# Fallback values
UNKNOWN_SOURCE = 'unknown'

# Default configuration
DEFAULT_PAGE_TITLE = 'Planned Articles'
DEFAULT_PAGE_PATH = 'coming-soon.md'

# Output filenames
JSON_OUTPUT_FILENAME = 'missing_refs.json'
