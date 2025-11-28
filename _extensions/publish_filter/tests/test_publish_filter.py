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
