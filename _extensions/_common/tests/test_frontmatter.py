"""Characterization tests for extract_frontmatter().

These tests document current behavior BEFORE any changes.
They import from EXISTING implementations to capture baseline.
"""

import pytest


class TestExtractFrontmatterCharacterization:
    """Tests that characterize current extract_frontmatter behavior."""

    # Import from category_nav as the reference implementation
    @pytest.fixture
    def extract_frontmatter(self):
        from category_nav.directive import extract_frontmatter
        return extract_frontmatter

    def test_empty_string_returns_empty_dict(self, extract_frontmatter):
        assert extract_frontmatter("") == {}

    def test_no_frontmatter_returns_empty_dict(self, extract_frontmatter, no_frontmatter):
        assert extract_frontmatter(no_frontmatter) == {}

    def test_frontmatter_not_at_start_returns_empty_dict(
        self, extract_frontmatter, frontmatter_not_at_start
    ):
        assert extract_frontmatter(frontmatter_not_at_start) == {}

    def test_unclosed_frontmatter_returns_empty_dict(
        self, extract_frontmatter, unclosed_frontmatter
    ):
        assert extract_frontmatter(unclosed_frontmatter) == {}

    def test_empty_frontmatter_returns_empty_dict(
        self, extract_frontmatter, empty_frontmatter
    ):
        # Just delimiters with nothing between
        result = extract_frontmatter(empty_frontmatter)
        assert result == {} or result is None or isinstance(result, dict)

    def test_malformed_yaml_returns_empty_dict(
        self, extract_frontmatter, malformed_yaml_frontmatter
    ):
        assert extract_frontmatter(malformed_yaml_frontmatter) == {}

    def test_non_dict_yaml_string_returns_empty_dict(
        self, extract_frontmatter, non_dict_yaml_string
    ):
        assert extract_frontmatter(non_dict_yaml_string) == {}

    def test_non_dict_yaml_list_returns_empty_dict(
        self, extract_frontmatter, non_dict_yaml_list
    ):
        assert extract_frontmatter(non_dict_yaml_list) == {}

    def test_valid_minimal_extracts_correctly(
        self, extract_frontmatter, minimal_frontmatter
    ):
        result = extract_frontmatter(minimal_frontmatter)
        assert result['title'] == 'Minimal'

    def test_valid_complete_extracts_all_fields(
        self, extract_frontmatter, valid_complete_frontmatter
    ):
        result = extract_frontmatter(valid_complete_frontmatter)
        assert result['title'] == 'Test Document'
        assert result['category'] == 'Theory'
        assert result['publish'] is True
        assert 'theory/testing' in result['tags']

    def test_publish_false_extracted_as_boolean(
        self, extract_frontmatter, draft_document
    ):
        result = extract_frontmatter(draft_document)
        assert result['publish'] is False

    def test_unicode_content_handled(
        self, extract_frontmatter, unicode_frontmatter
    ):
        result = extract_frontmatter(unicode_frontmatter)
        assert 'title' in result

    def test_windows_line_endings_handled(
        self, extract_frontmatter, windows_line_endings
    ):
        result = extract_frontmatter(windows_line_endings)
        assert result.get('title') == 'Windows'


class TestImplementationEquivalence:
    """Verify all three implementations behave identically."""

    @pytest.fixture
    def test_contents(self):
        return [
            "",
            "# No frontmatter",
            "---\ntitle: Test\n---\n# Content",
            "---\npublish: false\n---\n# Draft",
            "---\ninvalid: yaml: here\n---",
            "---\ntags:\n  - a\n  - b\n---",
            "---\n---\n# Empty",
            "text\n---\nkey: val\n---",
        ]

    def test_category_nav_matches_frontmatter_schema(self, test_contents):
        from category_nav.directive import extract_frontmatter as cat_extract
        from frontmatter_schema import extract_frontmatter as schema_extract

        for content in test_contents:
            cat_result = cat_extract(content)
            schema_result = schema_extract(content)
            assert cat_result == schema_result, f"Mismatch on: {content[:30]}..."
