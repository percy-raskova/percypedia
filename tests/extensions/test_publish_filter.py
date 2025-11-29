"""Tests for publish_filter Sphinx extension."""

import pytest


class TestStripObsidianComments:
    """Tests for Obsidian comment stripping."""

    def test_strips_single_line_comment(self):
        from publish_filter import strip_obsidian_comments

        source = ['This is visible %%this is hidden%% and this is visible']
        strip_obsidian_comments(None, 'test', source)

        assert source[0] == 'This is visible  and this is visible'

    def test_strips_multiple_comments(self):
        from publish_filter import strip_obsidian_comments

        source = ['%%hidden1%% visible %%hidden2%%']
        strip_obsidian_comments(None, 'test', source)

        assert source[0] == ' visible '

    def test_strips_multiline_comment(self):
        from publish_filter import strip_obsidian_comments

        source = ['''Before
%%
This entire block
is hidden from output
%%
After''']
        strip_obsidian_comments(None, 'test', source)

        assert source[0] == 'Before\n\nAfter'

    def test_preserves_content_without_comments(self):
        from publish_filter import strip_obsidian_comments

        source = ['No comments here, just regular content.']
        strip_obsidian_comments(None, 'test', source)

        assert source[0] == 'No comments here, just regular content.'

    def test_handles_empty_comment(self):
        from publish_filter import strip_obsidian_comments

        source = ['Text %%%% more text']
        strip_obsidian_comments(None, 'test', source)

        assert source[0] == 'Text  more text'

    def test_handles_comment_at_start(self):
        from publish_filter import strip_obsidian_comments

        source = ['%%TODO: write intro%%\n# Title']
        strip_obsidian_comments(None, 'test', source)

        assert source[0] == '\n# Title'

    def test_handles_none_source(self):
        from publish_filter import strip_obsidian_comments

        source = None
        # Should not raise
        strip_obsidian_comments(None, 'test', source)

    def test_handles_empty_source(self):
        from publish_filter import strip_obsidian_comments

        source = ['']
        strip_obsidian_comments(None, 'test', source)
        assert source[0] == ''


class TestGetUnpublishedDocs:
    """Tests for detecting unpublished documents."""

    def test_finds_unpublished_docs(self, tmp_path):
        from publish_filter import get_unpublished_docs
        from unittest.mock import Mock

        # Create test files
        (tmp_path / 'published.md').write_text('---\npublish: true\n---\n# Doc')
        (tmp_path / 'unpublished.md').write_text('---\npublish: false\n---\n# Doc')
        (tmp_path / 'no_key.md').write_text('---\ntitle: Test\n---\n# Doc')

        app = Mock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        assert 'unpublished' in result
        assert 'published' not in result
        assert 'no_key' not in result

    def test_skips_underscore_directories(self, tmp_path):
        from publish_filter import get_unpublished_docs
        from unittest.mock import Mock

        (tmp_path / '_templates').mkdir()
        (tmp_path / '_templates' / 'note.md').write_text(
            '---\npublish: false\n---\n# Template'
        )
        (tmp_path / 'normal.md').write_text('---\npublish: false\n---\n# Doc')

        app = Mock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        # _templates/note should NOT be in result (underscore dir)
        assert '_templates/note' not in result
        assert 'normal' in result

    def test_handles_no_frontmatter(self, tmp_path):
        from publish_filter import get_unpublished_docs
        from unittest.mock import Mock

        (tmp_path / 'no_fm.md').write_text('# Just a heading\n\nContent.')

        app = Mock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        assert len(result) == 0


class TestCriticalFileProtection:
    """Tests ensuring critical files are never excluded from builds.

    These tests catch the scenario where automated tools (like the frontmatter
    normalizer) accidentally mark essential files as drafts.
    """

    def test_index_md_never_excluded_even_with_publish_false(self, tmp_path):
        """index.md must NEVER be excluded, even if marked publish: false.

        This is the root document - excluding it breaks the entire build.
        """
        from publish_filter import get_unpublished_docs
        from unittest.mock import Mock

        # Simulate the bug: index.md accidentally marked as draft
        (tmp_path / 'index.md').write_text('---\npublish: false\n---\n# Home')
        (tmp_path / 'other.md').write_text('---\npublish: false\n---\n# Other')

        app = Mock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        # index should NOT be in the exclusion list
        assert 'index' not in result, "index.md must never be excluded from builds"
        # but other files with publish: false should be
        assert 'other' in result

    def test_conf_py_level_files_protected(self, tmp_path):
        """Files referenced directly in conf.py should be protected."""
        from publish_filter import get_unpublished_docs
        from unittest.mock import Mock

        # glossary.md is typically in the root toctree
        (tmp_path / 'glossary.md').write_text('---\npublish: false\n---\n# Glossary')
        (tmp_path / 'random.md').write_text('---\npublish: false\n---\n# Random')

        app = Mock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        # glossary should be protected (commonly in root toctree)
        assert 'glossary' not in result, "glossary.md should be protected"
        assert 'random' in result


class TestBuilderInited:
    """Tests for the builder-inited event handler."""

    def test_adds_unpublished_to_exclude_patterns(self, tmp_path):
        """Unpublished docs should be added to exclude_patterns."""
        from publish_filter import builder_inited
        from unittest.mock import Mock

        (tmp_path / 'draft.md').write_text('---\npublish: false\n---\n# Draft')
        (tmp_path / 'published.md').write_text('---\npublish: true\n---\n# Pub')

        app = Mock()
        app.srcdir = str(tmp_path)
        app.config.exclude_patterns = []

        builder_inited(app)

        assert 'draft.md' in app.config.exclude_patterns
        assert 'published.md' not in app.config.exclude_patterns

    def test_does_nothing_when_no_unpublished(self, tmp_path):
        """Should not modify exclude_patterns when no drafts exist."""
        from publish_filter import builder_inited
        from unittest.mock import Mock

        (tmp_path / 'published.md').write_text('---\npublish: true\n---\n# Pub')

        app = Mock()
        app.srcdir = str(tmp_path)
        app.config.exclude_patterns = ['existing.md']

        builder_inited(app)

        assert app.config.exclude_patterns == ['existing.md']

    def test_avoids_duplicate_patterns(self, tmp_path):
        """Should not add pattern if it already exists."""
        from publish_filter import builder_inited
        from unittest.mock import Mock

        (tmp_path / 'draft.md').write_text('---\npublish: false\n---\n# Draft')

        app = Mock()
        app.srcdir = str(tmp_path)
        app.config.exclude_patterns = ['draft.md']  # Already present

        builder_inited(app)

        # Should still be only one entry
        assert app.config.exclude_patterns.count('draft.md') == 1


class TestPublishFilterSetup:
    """Tests for the Sphinx extension setup function."""

    def test_connects_builder_inited(self):
        """Setup should connect builder-inited event."""
        from publish_filter import setup
        from unittest.mock import Mock

        app = Mock()
        setup(app)

        event_names = [call[0][0] for call in app.connect.call_args_list]
        assert 'builder-inited' in event_names

    def test_connects_source_read(self):
        """Setup should connect source-read event."""
        from publish_filter import setup
        from unittest.mock import Mock

        app = Mock()
        setup(app)

        event_names = [call[0][0] for call in app.connect.call_args_list]
        assert 'source-read' in event_names

    def test_returns_extension_metadata(self):
        """Setup should return proper extension metadata."""
        from publish_filter import setup
        from unittest.mock import Mock

        app = Mock()
        result = setup(app)

        assert 'version' in result
        assert result['parallel_read_safe'] is True
        assert result['parallel_write_safe'] is True
