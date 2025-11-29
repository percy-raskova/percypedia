"""Tests for frontmatter parser - YAML extraction from markdown.

RED PHASE: These tests define expected behavior before implementation.
"""

import pytest
from pathlib import Path


class TestParserBasics:
    """Tests for basic parser functionality."""

    def test_parses_frontmatter_and_body(self, file_schema_compliant):
        """Should return tuple of (frontmatter_dict, body_string)."""
        from frontmatter_normalizer.parser import parse_frontmatter

        frontmatter, body = parse_frontmatter(file_schema_compliant)

        assert isinstance(frontmatter, dict)
        assert isinstance(body, str)

    def test_extracts_all_frontmatter_fields(self, file_schema_compliant):
        """Should extract all frontmatter fields."""
        from frontmatter_normalizer.parser import parse_frontmatter

        frontmatter, _ = parse_frontmatter(file_schema_compliant)

        assert frontmatter['zkid'] == '202411281430'
        assert frontmatter['author'] == 'Percy'
        assert frontmatter['title'] == 'Test Document'
        assert frontmatter['category'] == 'Theory'

    def test_extracts_body_after_frontmatter(self, file_schema_compliant):
        """Should extract body content after frontmatter."""
        from frontmatter_normalizer.parser import parse_frontmatter

        _, body = parse_frontmatter(file_schema_compliant)

        assert "# Test Document" in body
        assert "schema-compliant frontmatter" in body


class TestParserNoFrontmatter:
    """Tests for files without frontmatter."""

    def test_returns_empty_dict_for_no_frontmatter(self, file_no_frontmatter):
        """Files without frontmatter should return empty dict."""
        from frontmatter_normalizer.parser import parse_frontmatter

        frontmatter, body = parse_frontmatter(file_no_frontmatter)

        assert frontmatter == {}
        assert "Labor Aristocracy" in body

    def test_entire_content_is_body(self, file_no_frontmatter):
        """Without frontmatter, entire content is body."""
        from frontmatter_normalizer.parser import parse_frontmatter

        frontmatter, body = parse_frontmatter(file_no_frontmatter)

        # Body should be the entire content
        assert body.strip() == file_no_frontmatter.strip()


class TestParserEdgeCases:
    """Tests for edge cases in parsing."""

    def test_handles_unclosed_frontmatter(self):
        """Unclosed frontmatter delimiter should return empty dict."""
        from frontmatter_normalizer.parser import parse_frontmatter

        content = "---\ntitle: Test\nNo closing delimiter"

        frontmatter, body = parse_frontmatter(content)

        assert frontmatter == {}
        assert "title: Test" in body

    def test_handles_frontmatter_not_at_start(self):
        """Frontmatter not at line 1 should be ignored."""
        from frontmatter_normalizer.parser import parse_frontmatter

        content = "\n---\ntitle: Test\n---\n\n# Body"

        frontmatter, body = parse_frontmatter(content)

        assert frontmatter == {}

    def test_handles_empty_frontmatter(self):
        """Empty frontmatter section should return empty dict."""
        from frontmatter_normalizer.parser import parse_frontmatter

        content = "---\n---\n\n# Body"

        frontmatter, body = parse_frontmatter(content)

        assert frontmatter == {}
        assert "# Body" in body

    def test_handles_invalid_yaml(self):
        """Invalid YAML should return empty dict."""
        from frontmatter_normalizer.parser import parse_frontmatter

        content = "---\ntitle: [invalid yaml\n---\n\n# Body"

        frontmatter, body = parse_frontmatter(content)

        assert frontmatter == {}

    def test_handles_non_dict_yaml(self):
        """Non-dict YAML (list, scalar) should return empty dict."""
        from frontmatter_normalizer.parser import parse_frontmatter

        content = "---\n- item1\n- item2\n---\n\n# Body"

        frontmatter, body = parse_frontmatter(content)

        assert frontmatter == {}

    def test_handles_empty_content(self):
        """Empty content should return empty dict and empty body."""
        from frontmatter_normalizer.parser import parse_frontmatter

        frontmatter, body = parse_frontmatter("")

        assert frontmatter == {}
        assert body == ""


class TestParserYAMLTypes:
    """Tests for YAML type handling."""

    def test_preserves_string_values(self, file_schema_compliant):
        """String values should remain strings."""
        from frontmatter_normalizer.parser import parse_frontmatter

        frontmatter, _ = parse_frontmatter(file_schema_compliant)

        assert isinstance(frontmatter['title'], str)
        assert isinstance(frontmatter['author'], str)

    def test_preserves_boolean_values(self, file_schema_compliant):
        """Boolean values should remain booleans."""
        from frontmatter_normalizer.parser import parse_frontmatter

        frontmatter, _ = parse_frontmatter(file_schema_compliant)

        assert frontmatter['publish'] is False
        assert isinstance(frontmatter['publish'], bool)

    def test_preserves_list_values(self, file_schema_compliant):
        """List values should remain lists."""
        from frontmatter_normalizer.parser import parse_frontmatter

        frontmatter, _ = parse_frontmatter(file_schema_compliant)

        assert isinstance(frontmatter['tags'], list)
        assert len(frontmatter['tags']) == 2

    def test_handles_quoted_strings(self):
        """Quoted strings should be parsed correctly."""
        from frontmatter_normalizer.parser import parse_frontmatter

        content = "---\nzkid: '202411281430'\ndate-created: '2024-11-28'\n---\n\n# Body"

        frontmatter, _ = parse_frontmatter(content)

        assert frontmatter['zkid'] == '202411281430'
        assert frontmatter['date-created'] == '2024-11-28'


class TestParserFileReading:
    """Tests for reading from file paths."""

    def test_reads_from_path(self, temp_md_file, file_schema_compliant):
        """Should read and parse from file path."""
        from frontmatter_normalizer.parser import parse_file

        filepath = temp_md_file(file_schema_compliant)

        frontmatter, body = parse_file(filepath)

        assert frontmatter['title'] == 'Test Document'
        assert "Test Document" in body

    def test_handles_nonexistent_file(self, tmp_path):
        """Should raise error for nonexistent file."""
        from frontmatter_normalizer.parser import parse_file

        filepath = tmp_path / "nonexistent.md"

        with pytest.raises(FileNotFoundError):
            parse_file(filepath)

    def test_handles_path_object(self, temp_md_file, file_no_frontmatter):
        """Should accept Path objects."""
        from frontmatter_normalizer.parser import parse_file

        filepath = temp_md_file(file_no_frontmatter)

        frontmatter, body = parse_file(filepath)

        assert frontmatter == {}
        assert "Labor Aristocracy" in body
