"""Characterization tests for directory traversal behavior.

CRITICAL: These tests document CURRENT behavioral differences.
DO NOT change these tests until you understand the differences.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock


class TestTraversalBehaviorDifferences:
    """Document behavioral differences between extensions."""

    def test_category_nav_file_selection(self, sample_srcdir):
        """Document which files category_nav selects."""
        from category_nav.directive import collect_categories

        result = collect_categories(sample_srcdir)

        # Flatten all docnames
        all_docnames = set()
        for docs in result.values():
            for doc in docs:
                all_docnames.add(doc['docname'])

        # Document current behavior
        # index and glossary ARE included (go to Miscellaneous) unless explicitly excluded
        assert 'index' in all_docnames
        assert 'glossary' in all_docnames
        assert 'about' in all_docnames
        assert 'theory/marxism' in all_docnames
        assert 'draft' not in all_docnames  # publish: false
        assert '_private' not in all_docnames  # underscore file skipped

    def test_publish_filter_unpublished_detection(self, sample_srcdir):
        """Document which files publish_filter marks as unpublished."""
        from publish_filter import get_unpublished_docs

        app = Mock()
        app.srcdir = str(sample_srcdir)

        result = get_unpublished_docs(app)

        assert 'draft' in result
        assert 'index' not in result
        assert 'theory/marxism' not in result


class TestUnderscoreFileBehavior:
    """CRITICAL: Extensions differ on underscore file handling."""

    def test_underscore_file_at_root(self, tmp_path):
        """_private.md at root - BEHAVIOR VARIES."""
        (tmp_path / '_private.md').write_text('---\ncategory: Test\n---\n# Private')
        (tmp_path / 'public.md').write_text('---\ncategory: Test\n---\n# Public')

        from category_nav.directive import collect_categories
        result = collect_categories(tmp_path)

        all_docnames = {doc['docname'] for docs in result.values() for doc in docs}

        # category_nav: Skips files starting with underscore
        assert '_private' not in all_docnames
        assert 'public' in all_docnames

    def test_publish_filter_skips_underscore_files(self, tmp_path):
        """publish_filter skips underscore files entirely."""
        (tmp_path / '_private.md').write_text('---\npublish: false\n---\n# Private')
        (tmp_path / 'public.md').write_text('---\npublish: false\n---\n# Public')

        from publish_filter import get_unpublished_docs

        app = Mock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        # publish_filter skips _private.md entirely (doesn't even check publish status)
        assert '_private' not in result
        # But finds public.md with publish: false
        assert 'public' in result


class TestDotFileBehavior:
    """CRITICAL: Extensions differ on dot file handling."""

    def test_dot_directory_always_excluded(self, tmp_path):
        """Files in .directories should always be excluded."""
        (tmp_path / '.hidden').mkdir()
        (tmp_path / '.hidden' / 'secret.md').write_text('---\n---\n# Secret')
        (tmp_path / 'visible.md').write_text('---\ncategory: Test\n---\n# Visible')

        from category_nav.directive import collect_categories
        result = collect_categories(tmp_path)

        all_docnames = {doc['docname'] for docs in result.values() for doc in docs}

        assert '.hidden/secret' not in all_docnames
        assert 'visible' in all_docnames


class TestUnderscoreDirectoryBehavior:
    """All extensions should skip underscore directories."""

    def test_category_nav_skips_underscore_dirs(self, tmp_path):
        """category_nav excludes files in _directories."""
        (tmp_path / '_templates').mkdir()
        (tmp_path / '_templates' / 'note.md').write_text('---\ncategory: Template\n---\n# Note')
        (tmp_path / 'public.md').write_text('---\ncategory: Test\n---\n# Public')

        from category_nav.directive import collect_categories
        result = collect_categories(tmp_path)

        all_docnames = {doc['docname'] for docs in result.values() for doc in docs}

        assert '_templates/note' not in all_docnames
        assert 'public' in all_docnames

    def test_publish_filter_skips_underscore_dirs(self, tmp_path):
        """publish_filter skips files in _directories."""
        (tmp_path / '_templates').mkdir()
        (tmp_path / '_templates' / 'note.md').write_text('---\npublish: false\n---\n# Note')
        (tmp_path / 'public.md').write_text('---\npublish: false\n---\n# Public')

        from publish_filter import get_unpublished_docs

        app = Mock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        assert '_templates/note' not in result
        assert 'public' in result


class TestDefaultExcludePatterns:
    """Test default exclude patterns in category_nav."""

    def test_venv_excluded(self, tmp_path):
        """Files in .venv are excluded."""
        (tmp_path / '.venv').mkdir()
        (tmp_path / '.venv' / 'readme.md').write_text('---\ncategory: Test\n---\n# Venv')
        (tmp_path / 'public.md').write_text('---\ncategory: Test\n---\n# Public')

        from category_nav.directive import collect_categories
        result = collect_categories(tmp_path)

        all_docnames = {doc['docname'] for docs in result.values() for doc in docs}

        assert '.venv/readme' not in all_docnames
        assert 'public' in all_docnames
