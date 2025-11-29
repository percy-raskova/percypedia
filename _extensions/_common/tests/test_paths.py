"""Tests for centralized path configuration module."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest


class TestDefaultPaths:
    """Test default path values without environment overrides."""

    def test_project_root_is_rstnotes_directory(self):
        """PROJECT_ROOT should be the rstnotes repository root."""
        from _common.paths import PROJECT_ROOT

        # Should end with 'rstnotes' (the repo name)
        assert PROJECT_ROOT.name == 'rstnotes'
        assert PROJECT_ROOT.is_dir()

    def test_content_root_is_content_subdirectory(self):
        """CONTENT_ROOT should be content/ under PROJECT_ROOT."""
        from _common.paths import PROJECT_ROOT, CONTENT_ROOT

        assert CONTENT_ROOT == PROJECT_ROOT / 'content'
        assert CONTENT_ROOT.is_dir()

    def test_build_root_is_build_subdirectory(self):
        """BUILD_ROOT should be _build/ under PROJECT_ROOT."""
        from _common.paths import PROJECT_ROOT, BUILD_ROOT

        assert BUILD_ROOT == PROJECT_ROOT / '_build'

    def test_all_paths_are_absolute(self):
        """All path constants should be absolute paths."""
        from _common.paths import (
            PROJECT_ROOT, CONTENT_ROOT, BUILD_ROOT,
            EXTENSIONS_DIR, TOOLS_DIR, STATIC_DIR,
            TEMPLATES_DIR, SCHEMAS_DIR, ASSETS_DIR
        )

        assert PROJECT_ROOT.is_absolute()
        assert CONTENT_ROOT.is_absolute()
        assert BUILD_ROOT.is_absolute()
        assert EXTENSIONS_DIR.is_absolute()
        assert TOOLS_DIR.is_absolute()
        assert STATIC_DIR.is_absolute()
        assert TEMPLATES_DIR.is_absolute()
        assert SCHEMAS_DIR.is_absolute()
        assert ASSETS_DIR.is_absolute()


class TestInfrastructureDirectories:
    """Test infrastructure directory path constants."""

    def test_extensions_dir_path(self):
        """EXTENSIONS_DIR should point to _extensions/."""
        from _common.paths import PROJECT_ROOT, EXTENSIONS_DIR

        assert EXTENSIONS_DIR == PROJECT_ROOT / '_extensions'
        assert EXTENSIONS_DIR.is_dir()

    def test_tools_dir_path(self):
        """TOOLS_DIR should point to _tools/."""
        from _common.paths import PROJECT_ROOT, TOOLS_DIR

        assert TOOLS_DIR == PROJECT_ROOT / '_tools'
        assert TOOLS_DIR.is_dir()

    def test_static_dir_path(self):
        """STATIC_DIR should point to _static/."""
        from _common.paths import PROJECT_ROOT, STATIC_DIR

        assert STATIC_DIR == PROJECT_ROOT / '_static'
        assert STATIC_DIR.is_dir()

    def test_templates_dir_path(self):
        """TEMPLATES_DIR should point to _templates/."""
        from _common.paths import PROJECT_ROOT, TEMPLATES_DIR

        assert TEMPLATES_DIR == PROJECT_ROOT / '_templates'
        assert TEMPLATES_DIR.is_dir()

    def test_schemas_dir_path(self):
        """SCHEMAS_DIR should point to _schemas/."""
        from _common.paths import PROJECT_ROOT, SCHEMAS_DIR

        assert SCHEMAS_DIR == PROJECT_ROOT / '_schemas'
        assert SCHEMAS_DIR.is_dir()

    def test_assets_dir_path(self):
        """ASSETS_DIR should point to _assets/."""
        from _common.paths import PROJECT_ROOT, ASSETS_DIR

        assert ASSETS_DIR == PROJECT_ROOT / '_assets'
        assert ASSETS_DIR.is_dir()


class TestExcludePatterns:
    """Test EXCLUDE_PATTERNS configuration."""

    def test_exclude_patterns_is_list(self):
        """EXCLUDE_PATTERNS should be a list."""
        from _common.paths import EXCLUDE_PATTERNS

        assert isinstance(EXCLUDE_PATTERNS, list)

    def test_exclude_patterns_contains_build_artifacts(self):
        """EXCLUDE_PATTERNS should include common build artifacts."""
        from _common.paths import EXCLUDE_PATTERNS

        assert '_build' in EXCLUDE_PATTERNS
        assert '.venv' in EXCLUDE_PATTERNS
        assert '__pycache__' in EXCLUDE_PATTERNS
        assert '.pytest_cache' in EXCLUDE_PATTERNS
        assert 'node_modules' in EXCLUDE_PATTERNS

    def test_exclude_patterns_contains_version_control(self):
        """EXCLUDE_PATTERNS should include version control directories."""
        from _common.paths import EXCLUDE_PATTERNS

        assert '.git' in EXCLUDE_PATTERNS
        assert '.obsidian' in EXCLUDE_PATTERNS

    def test_exclude_patterns_contains_infrastructure_dirs(self):
        """EXCLUDE_PATTERNS should include infrastructure directories."""
        from _common.paths import EXCLUDE_PATTERNS

        assert '_extensions' in EXCLUDE_PATTERNS
        assert '_templates' in EXCLUDE_PATTERNS
        assert '_tools' in EXCLUDE_PATTERNS
        assert '_static' in EXCLUDE_PATTERNS
        assert '_schemas' in EXCLUDE_PATTERNS
        assert '_assets' in EXCLUDE_PATTERNS

    def test_exclude_patterns_contains_private(self):
        """EXCLUDE_PATTERNS should include private content."""
        from _common.paths import EXCLUDE_PATTERNS

        assert 'private' in EXCLUDE_PATTERNS

    def test_exclude_patterns_contains_sample(self):
        """EXCLUDE_PATTERNS should include sample/demo content."""
        from _common.paths import EXCLUDE_PATTERNS

        assert 'sample' in EXCLUDE_PATTERNS


class TestSphinxExtraExcludes:
    """Test SPHINX_EXTRA_EXCLUDES configuration."""

    def test_sphinx_extra_excludes_is_list(self):
        """SPHINX_EXTRA_EXCLUDES should be a list."""
        from _common.paths import SPHINX_EXTRA_EXCLUDES

        assert isinstance(SPHINX_EXTRA_EXCLUDES, list)

    def test_sphinx_extra_excludes_contains_sample_indexes(self):
        """SPHINX_EXTRA_EXCLUDES should include sample index files."""
        from _common.paths import SPHINX_EXTRA_EXCLUDES

        assert 'sample/*/index.md' in SPHINX_EXTRA_EXCLUDES


class TestEnvironmentVariableOverrides:
    """Test that environment variables can override default paths."""

    def test_project_root_override(self, tmp_path, monkeypatch):
        """PERCYPEDIA_PROJECT_ROOT env var should override PROJECT_ROOT."""
        custom_root = tmp_path / 'custom_project'
        custom_root.mkdir()

        monkeypatch.setenv('PERCYPEDIA_PROJECT_ROOT', str(custom_root))

        # Need to reimport to pick up env var
        import importlib
        import _common.paths
        importlib.reload(_common.paths)

        try:
            assert _common.paths.PROJECT_ROOT == custom_root
        finally:
            # Clean up: reload without env var
            monkeypatch.delenv('PERCYPEDIA_PROJECT_ROOT')
            importlib.reload(_common.paths)

    def test_content_root_override(self, tmp_path, monkeypatch):
        """PERCYPEDIA_CONTENT_ROOT env var should override CONTENT_ROOT."""
        custom_content = tmp_path / 'custom_content'
        custom_content.mkdir()

        monkeypatch.setenv('PERCYPEDIA_CONTENT_ROOT', str(custom_content))

        import importlib
        import _common.paths
        importlib.reload(_common.paths)

        try:
            assert _common.paths.CONTENT_ROOT == custom_content
        finally:
            monkeypatch.delenv('PERCYPEDIA_CONTENT_ROOT')
            importlib.reload(_common.paths)

    def test_build_root_override(self, tmp_path, monkeypatch):
        """PERCYPEDIA_BUILD_ROOT env var should override BUILD_ROOT."""
        custom_build = tmp_path / 'custom_build'
        custom_build.mkdir()

        monkeypatch.setenv('PERCYPEDIA_BUILD_ROOT', str(custom_build))

        import importlib
        import _common.paths
        importlib.reload(_common.paths)

        try:
            assert _common.paths.BUILD_ROOT == custom_build
        finally:
            monkeypatch.delenv('PERCYPEDIA_BUILD_ROOT')
            importlib.reload(_common.paths)


class TestPathsModuleUsability:
    """Test that the paths module is usable by other modules."""

    def test_can_import_all_exports(self):
        """All documented exports should be importable."""
        from _common.paths import (
            PROJECT_ROOT,
            CONTENT_ROOT,
            BUILD_ROOT,
            EXTENSIONS_DIR,
            TOOLS_DIR,
            STATIC_DIR,
            TEMPLATES_DIR,
            SCHEMAS_DIR,
            ASSETS_DIR,
            EXCLUDE_PATTERNS,
            SPHINX_EXTRA_EXCLUDES,
        )

        # All should be non-None
        assert PROJECT_ROOT is not None
        assert CONTENT_ROOT is not None
        assert BUILD_ROOT is not None
        assert EXTENSIONS_DIR is not None
        assert TOOLS_DIR is not None
        assert STATIC_DIR is not None
        assert TEMPLATES_DIR is not None
        assert SCHEMAS_DIR is not None
        assert ASSETS_DIR is not None
        assert EXCLUDE_PATTERNS is not None
        assert SPHINX_EXTRA_EXCLUDES is not None

    def test_category_nav_uses_exclude_patterns(self):
        """category_nav should import EXCLUDE_PATTERNS from paths module."""
        from category_nav.directive import EXCLUDE_PATTERNS
        from _common.paths import EXCLUDE_PATTERNS as CENTRALIZED_PATTERNS

        # category_nav should be using the centralized patterns
        # Note: Use == instead of 'is' due to potential module reloading in tests
        assert EXCLUDE_PATTERNS == CENTRALIZED_PATTERNS

    def test_frontmatter_schema_uses_schemas_dir(self):
        """frontmatter_schema should use SCHEMAS_DIR for schema path."""
        from frontmatter_schema import SCHEMA_PATH
        from _common.paths import SCHEMAS_DIR

        # Schema path should be under SCHEMAS_DIR
        assert SCHEMA_PATH.parent == SCHEMAS_DIR
