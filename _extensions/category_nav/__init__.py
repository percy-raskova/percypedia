# category_nav - Sphinx extension for frontmatter-based navigation
#
# Generates toctrees grouped by `category:` frontmatter field.
# Files without a category go to "Miscellaneous".

from .directive import CategoryNavDirective, extract_frontmatter, collect_categories


def setup(app):
    """Sphinx extension entry point."""
    app.add_directive('category-nav', CategoryNavDirective)
    app.add_config_value('category_nav_default', 'Miscellaneous', 'env')
    app.add_config_value('category_nav_exclude', ['index', 'glossary'], 'env')

    return {
        'version': '0.1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
