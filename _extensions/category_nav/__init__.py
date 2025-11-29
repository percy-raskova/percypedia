# category_nav - Sphinx extension for frontmatter-based navigation
#
# Generates toctrees grouped by `category:` frontmatter field.
# Files without a category go to "Miscellaneous".
#
# Also marks all documents as orphans since navigation is handled dynamically,
# suppressing Sphinx's "document isn't included in any toctree" warnings.

from .directive import CategoryNavDirective, extract_frontmatter, collect_categories


def mark_as_orphan(app, docname, source):
    """Mark all documents as orphans to suppress toctree warnings.

    Since category_nav handles navigation dynamically via the {category-nav}
    directive, documents don't need to be in a static toctree. Adding orphan
    metadata tells Sphinx this is intentional.
    """
    # Store orphan flag in document metadata
    # This is checked by Sphinx's check_consistency()
    app.env.metadata.setdefault(docname, {})['orphan'] = True


def setup(app):
    """Sphinx extension entry point."""
    app.add_directive('category-nav', CategoryNavDirective)
    app.add_config_value('category_nav_default', 'Miscellaneous', 'env')
    app.add_config_value('category_nav_exclude', ['index', 'glossary'], 'env')

    # Mark all documents as orphans to suppress toctree warnings
    app.connect('source-read', mark_as_orphan)

    return {
        'version': '0.1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
