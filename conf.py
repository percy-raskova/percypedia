# Configuration file for the Sphinx documentation builder.
# PercyBrain Zettelkasten Knowledge Base
# Format: MyST Markdown with wiki link support

import sys
from pathlib import Path

# Add local extensions to path
sys.path.insert(0, str(Path(__file__).parent / '_extensions'))

# -- Project information -----------------------------------------------------
project = 'PercyBrain'
copyright = '2025, Percy'
author = 'Percy'
version = '2.0'
release = '2.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'myst_parser',          # MyST Markdown support
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.todo',
    'sphinx.ext.graphviz',
    'sphinx_design',        # Cards, grids, tabs
    'sphinx_tags',          # Blog-style tags
    'hoverxref.extension',  # Tooltip hovers for glossary terms
    'category_nav',         # Auto-generate nav from frontmatter categories
    'publish_filter',       # Draft/publish workflow + Obsidian comment stripping
    'missing_refs',         # Track forward-links to unwritten docs
    # 'ablog',              # Disabled: conflicts with Furo theme (layout.html issue)
    #                       # See: https://github.com/pradyunsg/furo/discussions/262
]

# -- missing_refs configuration ----------------------------------------------
# Generate a "Planned Articles" page from forward-links to unwritten docs
missing_refs_generate_page = False  # Set True to auto-generate coming-soon.md
missing_refs_page_path = 'coming-soon.md'
missing_refs_page_title = 'Planned Articles'

# -- category_nav configuration ----------------------------------------------
# Files to exclude from category navigation (by docname)
category_nav_exclude = [
    'index', 'glossary', 'docs/index',
    'sample/concepts/index', 'sample/methods/index', 'sample/systems/index',
]
category_nav_default = 'Miscellaneous'

# -- MyST Parser configuration -----------------------------------------------
# Enable MyST extensions for Zettelkasten workflow
myst_enable_extensions = [
    "colon_fence",      # ::: directive syntax (renders in plain MD editors)
    "deflist",          # Definition lists
    "dollarmath",       # $math$ syntax
    "fieldlist",        # :field: metadata
    "substitution",     # {{variables}}
    "tasklist",         # [ ] checkbox lists
    "attrs_inline",     # Inline attributes {#id .class}
]

# Auto-generate header anchors for cross-referencing
myst_heading_anchors = 3

# MyST substitutions for templating
# Usage in markdown: {{assets}}/images/photo.png
myst_substitutions = {
    "assets": "https://assets.percybrain.com",  # R2 bucket public URL
}

# Source file suffixes (support both .md and .rst during migration)
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'myst-nb' if 'myst_nb' in extensions else 'myst',
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '.venv', 'private', '_assets', '_extensions', '_templates', '_tools', '_*', '.pytest_cache', 'sample/*/index.md', 'node_modules']
language = 'en'

# Auto-label sections with document prefix to avoid duplicates
autosectionlabel_prefix_document = True

# Enable todos
todo_include_todos = True

# sphinx-tags configuration
tags_create_tags = True
tags_create_badges = True

# sphinx-hoverxref configuration (glossary tooltips)
hoverxref_auto_ref = True
hoverxref_roles = ['term', 'ref', 'doc']  # Enable tooltips for these roles
hoverxref_role_types = {
    'term': 'tooltip',
    'ref': 'tooltip',
    'doc': 'tooltip',
}
hoverxref_tooltip_class = 'rst-content'

# -- Options for HTML output -------------------------------------------------
# Theme: Furo (synced with Kitty terminal color scheme)
html_theme = 'furo'

html_theme_options = {
    # Light mode (inverted Blood Moon)
    "light_css_variables": {
        "color-brand-primary": "#dc143c",      # Crimson
        "color-brand-content": "#a01028",      # Crimson dim
        "color-background-primary": "#f8f4f4",
        "color-background-secondary": "#efe8e8",
        "color-foreground-primary": "#1a0000",
        "font-stack": "system-ui, -apple-system, sans-serif",
    },
    # Dark mode - PercyBrain Blood Moon (synced with Neovim)
    "dark_css_variables": {
        # Base colors (from percybrain-theme.lua)
        "color-background-primary": "#1a0000",    # bg - Deep blood red/black
        "color-background-secondary": "#0d0000",  # bg_dark
        "color-background-hover": "#2a0a0a",      # bg_highlight
        "color-background-border": "#dc143c",     # border - Crimson

        # Text colors
        "color-foreground-primary": "#e8e8e8",    # fg - Light gray
        "color-foreground-secondary": "#b0b0b0",  # fg_dark
        "color-foreground-muted": "#5a2020",      # fg_gutter

        # Accent colors
        "color-brand-primary": "#ffd700",         # gold - Primary accent
        "color-brand-content": "#ffd700",         # gold

        # Links
        "color-link": "#4488ff",                  # blue - Functions color
        "color-link-underline": "#4488ff",
        "color-link--hover": "#ffd700",           # gold on hover
        "color-link-underline--hover": "#ffd700",

        # Admonitions
        "color-admonition-background": "#0d0000",
        "color-admonition-title": "#ffd700",

        # Code
        "color-code-background": "#0d0000",
        "color-code-foreground": "#e8e8e8",
        "color-inline-code-background": "#2a0a0a",

        # API/highlights
        "color-api-background": "#2a0a0a",
        "color-api-background-hover": "#3a1a1a",
        "color-highlight-on-target": "#2a0a0a",

        # Sidebar
        "color-sidebar-background": "#0d0000",
        "color-sidebar-background-border": "#dc143c",
        "color-sidebar-link-text": "#e8e8e8",
        "color-sidebar-item-background--current": "#2a0a0a",
        "color-sidebar-item-background--hover": "#2a0a0a",

        # Search
        "color-search-icon": "#ffd700",
        "color-search-placeholder": "#b0b0b0",
    },
    "navigation_with_keys": True,
    "sidebar_hide_name": False,
}

html_static_path = ['_static']
html_css_files = ['custom.css']
html_js_files = ['sidebar-collapse.js', 'contact.js']
html_title = "Percypedia: No Investigation, No Right to Speak"

# Custom RST prolog for tag role
rst_prolog = """
.. role:: tag
   :class: tag
"""
