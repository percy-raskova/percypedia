"""
Tests for publish_filter Sphinx extension.

Tests the draft/publish workflow and Obsidian comment stripping.
These tests establish a baseline for safe refactoring.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from publish_filter import (
    get_unpublished_docs,
    builder_inited,
    strip_obsidian_comments,
    setup,
    PROTECTED_DOCNAMES,
    OBSIDIAN_COMMENT_PATTERN,
)


class TestConstants:
    """Test Group 0: Module constants."""

    def test_obsidian_pattern_is_string(self):
        """
        Given: OBSIDIAN_COMMENT_PATTERN constant
        When: Checking type
        Then: It is a string (regex pattern)
        """
        assert isinstance(OBSIDIAN_COMMENT_PATTERN, str)

    def test_obsidian_pattern_matches_simple_comment(self):
        """
        Given: OBSIDIAN_COMMENT_PATTERN
        When: Applied to %%comment%%
        Then: Matches the comment
        """
        import re
        text = "%%hidden%%"
        match = re.search(OBSIDIAN_COMMENT_PATTERN, text)
        assert match is not None
        assert match.group() == "%%hidden%%"


class TestProtectedDocnames:
    """Test Group 1: Protected docnames configuration."""

    def test_index_is_protected(self):
        """
        Given: PROTECTED_DOCNAMES constant
        When: Checking for 'index'
        Then: 'index' is in the protected set
        """
        assert 'index' in PROTECTED_DOCNAMES

    def test_glossary_is_protected(self):
        """
        Given: PROTECTED_DOCNAMES constant
        When: Checking for 'glossary'
        Then: 'glossary' is in the protected set
        """
        assert 'glossary' in PROTECTED_DOCNAMES

    def test_honeypot_is_protected(self):
        """
        Given: PROTECTED_DOCNAMES constant
        When: Checking for 'honeypot'
        Then: 'honeypot' is in the protected set
        """
        assert 'honeypot' in PROTECTED_DOCNAMES


class TestGetUnpublishedDocs:
    """Test Group 2: Scanning for unpublished documents."""

    def test_empty_directory_returns_empty_set(self, tmp_path):
        """
        Given: Empty source directory
        When: get_unpublished_docs is called
        Then: Returns empty set
        """
        app = MagicMock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        assert result == set()

    def test_published_doc_not_in_result(self, tmp_path):
        """
        Given: Document with publish: true
        When: get_unpublished_docs is called
        Then: Document is not in unpublished set
        """
        # Create published doc
        doc = tmp_path / "article.md"
        doc.write_text("---\npublish: true\n---\n# Article\n")

        app = MagicMock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        assert 'article' not in result

    def test_unpublished_doc_in_result(self, tmp_path):
        """
        Given: Document with publish: false
        When: get_unpublished_docs is called
        Then: Document is in unpublished set
        """
        # Create unpublished doc
        doc = tmp_path / "draft.md"
        doc.write_text("---\npublish: false\n---\n# Draft\n")

        app = MagicMock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        assert 'draft' in result

    def test_doc_without_publish_field_not_unpublished(self, tmp_path):
        """
        Given: Document without publish field (default is published)
        When: get_unpublished_docs is called
        Then: Document is not in unpublished set
        """
        doc = tmp_path / "article.md"
        doc.write_text("---\ntitle: Article\n---\n# Article\n")

        app = MagicMock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        assert 'article' not in result

    def test_doc_without_frontmatter_not_unpublished(self, tmp_path):
        """
        Given: Document without frontmatter
        When: get_unpublished_docs is called
        Then: Document is not in unpublished set
        """
        doc = tmp_path / "article.md"
        doc.write_text("# Article\n\nContent here.")

        app = MagicMock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        assert 'article' not in result

    def test_nested_unpublished_doc(self, tmp_path):
        """
        Given: Unpublished document in subdirectory
        When: get_unpublished_docs is called
        Then: Document path includes directory
        """
        subdir = tmp_path / "theory"
        subdir.mkdir()
        doc = subdir / "draft.md"
        doc.write_text("---\npublish: false\n---\n# Draft\n")

        app = MagicMock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        assert 'theory/draft' in result

    def test_protected_index_never_excluded(self, tmp_path):
        """
        Given: index.md with publish: false
        When: get_unpublished_docs is called
        Then: 'index' is NOT in unpublished set (protected)
        """
        doc = tmp_path / "index.md"
        doc.write_text("---\npublish: false\n---\n# Home\n")

        app = MagicMock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        assert 'index' not in result

    def test_protected_glossary_never_excluded(self, tmp_path):
        """
        Given: glossary.md with publish: false
        When: get_unpublished_docs is called
        Then: 'glossary' is NOT in unpublished set (protected)
        """
        doc = tmp_path / "glossary.md"
        doc.write_text("---\npublish: false\n---\n# Glossary\n")

        app = MagicMock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        assert 'glossary' not in result

    def test_protected_honeypot_never_excluded(self, tmp_path):
        """
        Given: honeypot.md with publish: false
        When: get_unpublished_docs is called
        Then: 'honeypot' is NOT in unpublished set (protected)
        """
        doc = tmp_path / "honeypot.md"
        doc.write_text("---\npublish: false\n---\n# Honeypot\n")

        app = MagicMock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        assert 'honeypot' not in result

    def test_skips_underscore_prefixed_files(self, tmp_path):
        """
        Given: File starting with underscore (e.g., _template.md)
        When: get_unpublished_docs is called
        Then: File is skipped (not included in results)
        """
        doc = tmp_path / "_template.md"
        doc.write_text("---\npublish: false\n---\n# Template\n")

        app = MagicMock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        assert '_template' not in result

    def test_skips_underscore_prefixed_directories(self, tmp_path):
        """
        Given: Document in underscore directory (e.g., _drafts/)
        When: get_unpublished_docs is called
        Then: Document is skipped
        """
        drafts = tmp_path / "_drafts"
        drafts.mkdir()
        doc = drafts / "article.md"
        doc.write_text("---\npublish: false\n---\n# Draft\n")

        app = MagicMock()
        app.srcdir = str(tmp_path)

        result = get_unpublished_docs(app)

        assert '_drafts/article' not in result

    def test_handles_invalid_yaml_gracefully(self, tmp_path):
        """
        Given: Document with invalid YAML frontmatter
        When: get_unpublished_docs is called
        Then: Document is skipped, no exception raised
        """
        doc = tmp_path / "broken.md"
        doc.write_text("---\ninvalid: yaml: content:\n---\n# Broken\n")

        app = MagicMock()
        app.srcdir = str(tmp_path)

        # Should not raise
        result = get_unpublished_docs(app)

        assert 'broken' not in result

    def test_handles_unreadable_file_gracefully(self, tmp_path):
        """
        Given: Document that raises exception on read
        When: get_unpublished_docs is called
        Then: Document is skipped, no exception raised
        """
        doc = tmp_path / "article.md"
        doc.write_text("---\npublish: false\n---\n")

        app = MagicMock()
        app.srcdir = str(tmp_path)

        # Make file unreadable by patching read_text
        with patch.object(Path, 'read_text', side_effect=PermissionError):
            # Should not raise
            result = get_unpublished_docs(app)

        # Result depends on implementation, but should not crash


class TestBuilderInited:
    """Test Group 3: Builder initialization handler."""

    def test_adds_unpublished_to_exclude_patterns(self, tmp_path):
        """
        Given: Unpublished document exists
        When: builder_inited is called
        Then: Document pattern is added to exclude_patterns
        """
        doc = tmp_path / "draft.md"
        doc.write_text("---\npublish: false\n---\n# Draft\n")

        app = MagicMock()
        app.srcdir = str(tmp_path)
        app.config.exclude_patterns = []

        builder_inited(app)

        assert 'draft.md' in app.config.exclude_patterns

    def test_does_not_duplicate_patterns(self, tmp_path):
        """
        Given: Pattern already in exclude_patterns
        When: builder_inited is called
        Then: Pattern is not duplicated
        """
        doc = tmp_path / "draft.md"
        doc.write_text("---\npublish: false\n---\n# Draft\n")

        app = MagicMock()
        app.srcdir = str(tmp_path)
        app.config.exclude_patterns = ['draft.md']  # Already excluded

        builder_inited(app)

        # Count occurrences
        count = app.config.exclude_patterns.count('draft.md')
        assert count == 1

    def test_no_changes_when_all_published(self, tmp_path):
        """
        Given: All documents are published
        When: builder_inited is called
        Then: exclude_patterns is unchanged
        """
        doc = tmp_path / "article.md"
        doc.write_text("---\npublish: true\n---\n# Article\n")

        app = MagicMock()
        app.srcdir = str(tmp_path)
        app.config.exclude_patterns = ['existing.md']

        builder_inited(app)

        assert app.config.exclude_patterns == ['existing.md']

    def test_nested_doc_pattern_includes_path(self, tmp_path):
        """
        Given: Unpublished document in subdirectory
        When: builder_inited is called
        Then: Pattern includes directory path
        """
        subdir = tmp_path / "theory"
        subdir.mkdir()
        doc = subdir / "draft.md"
        doc.write_text("---\npublish: false\n---\n# Draft\n")

        app = MagicMock()
        app.srcdir = str(tmp_path)
        app.config.exclude_patterns = []

        builder_inited(app)

        assert 'theory/draft.md' in app.config.exclude_patterns


class TestStripObsidianComments:
    """Test Group 4: Obsidian comment stripping."""

    def test_strips_inline_comment(self):
        """
        Given: Source with inline Obsidian comment
        When: strip_obsidian_comments is called
        Then: Comment is removed
        """
        app = MagicMock()
        source = ["Some text %%hidden%% more text"]

        strip_obsidian_comments(app, 'test', source)

        assert source[0] == "Some text  more text"

    def test_strips_multiline_comment(self):
        """
        Given: Source with multi-line Obsidian comment
        When: strip_obsidian_comments is called
        Then: Entire comment including newlines is removed
        """
        app = MagicMock()
        source = ["Before\n%%\nHidden\nContent\n%%\nAfter"]

        strip_obsidian_comments(app, 'test', source)

        assert source[0] == "Before\n\nAfter"

    def test_strips_multiple_comments(self):
        """
        Given: Source with multiple Obsidian comments
        When: strip_obsidian_comments is called
        Then: All comments are removed
        """
        app = MagicMock()
        source = ["Text %%one%% middle %%two%% end"]

        strip_obsidian_comments(app, 'test', source)

        assert source[0] == "Text  middle  end"

    def test_preserves_text_without_comments(self):
        """
        Given: Source without Obsidian comments
        When: strip_obsidian_comments is called
        Then: Source is unchanged
        """
        app = MagicMock()
        original = "Normal text without comments"
        source = [original]

        strip_obsidian_comments(app, 'test', source)

        assert source[0] == original

    def test_handles_empty_source(self):
        """
        Given: Empty source list
        When: strip_obsidian_comments is called
        Then: No error occurs
        """
        app = MagicMock()
        source = []

        # Should not raise
        strip_obsidian_comments(app, 'test', source)

    def test_handles_none_in_source(self):
        """
        Given: Source with None value
        When: strip_obsidian_comments is called
        Then: No error occurs
        """
        app = MagicMock()
        source = [None]

        # Should not raise
        strip_obsidian_comments(app, 'test', source)

    def test_handles_empty_string_source(self):
        """
        Given: Source with empty string
        When: strip_obsidian_comments is called
        Then: No error occurs
        """
        app = MagicMock()
        source = [""]

        # Should not raise
        strip_obsidian_comments(app, 'test', source)

        assert source[0] == ""

    def test_strips_comment_at_start(self):
        """
        Given: Comment at start of document
        When: strip_obsidian_comments is called
        Then: Comment is removed
        """
        app = MagicMock()
        source = ["%%hidden%%# Heading"]

        strip_obsidian_comments(app, 'test', source)

        assert source[0] == "# Heading"

    def test_strips_comment_at_end(self):
        """
        Given: Comment at end of document
        When: strip_obsidian_comments is called
        Then: Comment is removed
        """
        app = MagicMock()
        source = ["Content%%hidden%%"]

        strip_obsidian_comments(app, 'test', source)

        assert source[0] == "Content"

    def test_single_percent_not_affected(self):
        """
        Given: Text with single percent signs
        When: strip_obsidian_comments is called
        Then: Single percents are preserved
        """
        app = MagicMock()
        source = ["50% complete, 100% done"]

        strip_obsidian_comments(app, 'test', source)

        assert source[0] == "50% complete, 100% done"

    def test_nested_percent_comment(self):
        """
        Given: Nested comment structure %%outer %%inner%% outer%%
        When: strip_obsidian_comments is called
        Then: Non-greedy matching removes first complete comment
        """
        app = MagicMock()
        # Non-greedy match should match %%outer %% first
        source = ["%%first%% middle %%second%%"]

        strip_obsidian_comments(app, 'test', source)

        assert source[0] == " middle "


class TestSetup:
    """Test Group 5: Extension setup."""

    def test_setup_returns_valid_extension_info(self):
        """
        Given: Mock Sphinx app
        When: setup() is called
        Then: Returns dict with version and parallel safety info
        """
        app = MagicMock()

        result = setup(app)

        assert isinstance(result, dict)
        assert 'version' in result
        assert 'parallel_read_safe' in result
        assert 'parallel_write_safe' in result

    def test_parallel_read_safe_is_true(self):
        """
        Given: Mock Sphinx app
        When: setup() is called
        Then: parallel_read_safe is True
        """
        app = MagicMock()

        result = setup(app)

        assert result['parallel_read_safe'] is True

    def test_parallel_write_safe_is_true(self):
        """
        Given: Mock Sphinx app
        When: setup() is called
        Then: parallel_write_safe is True
        """
        app = MagicMock()

        result = setup(app)

        assert result['parallel_write_safe'] is True

    def test_connects_builder_inited_event(self):
        """
        Given: Mock Sphinx app
        When: setup() is called
        Then: builder-inited event is connected
        """
        app = MagicMock()

        setup(app)

        calls = [call[0][0] for call in app.connect.call_args_list]
        assert 'builder-inited' in calls

    def test_connects_source_read_event(self):
        """
        Given: Mock Sphinx app
        When: setup() is called
        Then: source-read event is connected
        """
        app = MagicMock()

        setup(app)

        calls = [call[0][0] for call in app.connect.call_args_list]
        assert 'source-read' in calls


class TestIntegration:
    """Test Group 6: Integration tests."""

    def test_full_workflow_draft_excluded(self, tmp_path):
        """
        Given: Mixed published and unpublished documents
        When: builder_inited runs
        Then: Only unpublished docs added to exclude_patterns
        """
        # Create published doc
        published = tmp_path / "article.md"
        published.write_text("---\npublish: true\n---\n# Article\n")

        # Create unpublished doc
        draft = tmp_path / "draft.md"
        draft.write_text("---\npublish: false\n---\n# Draft\n")

        # Create doc without frontmatter (default published)
        nofront = tmp_path / "plain.md"
        nofront.write_text("# Plain Article\n")

        app = MagicMock()
        app.srcdir = str(tmp_path)
        app.config.exclude_patterns = []

        builder_inited(app)

        assert 'draft.md' in app.config.exclude_patterns
        assert 'article.md' not in app.config.exclude_patterns
        assert 'plain.md' not in app.config.exclude_patterns

    def test_comment_with_frontmatter(self):
        """
        Given: Document with frontmatter and Obsidian comments
        When: strip_obsidian_comments is called
        Then: Comments removed, frontmatter preserved
        """
        app = MagicMock()
        source = ["---\ntitle: Test\n---\n# Heading\n%%todo: fix this%%\nContent"]

        strip_obsidian_comments(app, 'test', source)

        assert "---\ntitle: Test\n---" in source[0]
        assert "%%todo: fix this%%" not in source[0]
        assert "Content" in source[0]
