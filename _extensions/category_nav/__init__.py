# category_nav - Sphinx extension for frontmatter-based navigation
#
# Generates toctrees grouped by `category:` frontmatter field.
# Files without a category go to "Miscellaneous".
#
# Also marks all documents as orphans since navigation is handled dynamically,
# suppressing Sphinx's "document isn't included in any toctree" warnings.

from typing import Any, Dict, List

from sphinx.application import Sphinx

from .directive import CategoryNavDirective, extract_frontmatter, collect_categories

# =============================================================================
# Constants
# =============================================================================

__version__ = '0.1.0'

# Default configuration values
DEFAULT_CATEGORY = 'Miscellaneous'
DEFAULT_EXCLUDE = ['index', 'glossary']


def mark_as_orphan(app: Sphinx, docname: str, source: List[str]) -> None:
    """Mark all documents as orphans to suppress toctree warnings.

    Since category_nav handles navigation dynamically via the {category-nav}
    directive, documents don't need to be in a static toctree. Adding orphan
    metadata tells Sphinx this is intentional.

    Args:
        app: Sphinx application instance
        docname: Document name being processed
        source: List containing source content (modified in place by other handlers)
    """
    # Store orphan flag in document metadata
    # This is checked by Sphinx's check_consistency()
    app.env.metadata.setdefault(docname, {})['orphan'] = True


def setup(app: Sphinx) -> Dict[str, Any]:
    """Sphinx extension entry point.

    Args:
        app: Sphinx application instance

    Returns:
        Extension metadata dict with version and parallel safety flags
    """
    app.add_directive('category-nav', CategoryNavDirective)
    app.add_config_value('category_nav_default', DEFAULT_CATEGORY, 'env')
    app.add_config_value('category_nav_exclude', DEFAULT_EXCLUDE, 'env')

    # Mark all documents as orphans to suppress toctree warnings
    app.connect('source-read', mark_as_orphan)

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
