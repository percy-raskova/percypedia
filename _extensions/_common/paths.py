"""Centralized path configuration for Percypedia.

Single source of truth for all path-related constants.
Supports environment variable overrides for CI/deployment.

Usage:
    from _common.paths import CONTENT_ROOT, EXCLUDE_PATTERNS
"""

import os
from pathlib import Path

# =============================================================================
# Root Directories (with env var overrides)
# =============================================================================

# Project root is parent of _extensions directory
PROJECT_ROOT = Path(os.environ.get(
    'PERCYPEDIA_PROJECT_ROOT',
    Path(__file__).parent.parent.parent
)).resolve()

# Content root - where Sphinx srcdir lives
CONTENT_ROOT = Path(os.environ.get(
    'PERCYPEDIA_CONTENT_ROOT',
    PROJECT_ROOT / 'content'
)).resolve()

# Build output directory
BUILD_ROOT = Path(os.environ.get(
    'PERCYPEDIA_BUILD_ROOT',
    PROJECT_ROOT / '_build'
)).resolve()

# =============================================================================
# Infrastructure Directories
# =============================================================================

EXTENSIONS_DIR = PROJECT_ROOT / '_extensions'
TOOLS_DIR = PROJECT_ROOT / '_tools'
STATIC_DIR = PROJECT_ROOT / '_static'
TEMPLATES_DIR = PROJECT_ROOT / '_templates'
SCHEMAS_DIR = PROJECT_ROOT / '_schemas'
ASSETS_DIR = PROJECT_ROOT / '_assets'

# =============================================================================
# Exclude Patterns (Single Source of Truth)
# =============================================================================

# Patterns for excluding from content discovery
# Used by: Sphinx, category_nav, frontmatter_schema, frontmatter_normalizer
EXCLUDE_PATTERNS: list[str] = [
    # Build artifacts
    '_build', '_build/*',
    '.venv', '.venv/*',
    '__pycache__', '__pycache__/*',
    '*.pyc',
    '.pytest_cache', '.pytest_cache/*',
    'node_modules', 'node_modules/*',
    # Version control / editors
    '.git', '.git/*',
    '.obsidian', '.obsidian/*',
    'Thumbs.db', '.DS_Store',
    # Private content
    'private', 'private/*',
    # Infrastructure directories (not content)
    '_extensions', '_extensions/*',
    '_templates', '_templates/*',
    '_tools', '_tools/*',
    '_static', '_static/*',
    '_schemas', '_schemas/*',
    '_assets', '_assets/*',
    # Sample/demo content
    'sample', 'sample/*',
]

# Additional patterns for Sphinx exclude_patterns only
SPHINX_EXTRA_EXCLUDES: list[str] = [
    'sample/*/index.md',  # Sample index files
]
