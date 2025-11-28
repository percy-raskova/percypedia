"""Tests for frontmatter writer - YAML serialization.

RED PHASE: These tests define expected behavior before implementation.
"""

import pytest
from pathlib import Path


class TestWriterBasics:
    """Tests for basic writer functionality."""

    def test_renders_frontmatter_with_delimiters(self):
        """Should render frontmatter with --- delimiters."""
        from frontmatter_normalizer.writer import render_frontmatter

        frontmatter = {"title": "Test", "category": "Concepts"}
        body = "# Test\n\nContent here."

        result = render_frontmatter(frontmatter, body)

        assert result.startswith("---\n")
        assert "\n---\n" in result
        assert result.endswith("\n\nContent here.")

    def test_renders_empty_frontmatter(self):
        """Empty frontmatter should still have delimiters."""
        from frontmatter_normalizer.writer import render_frontmatter

        frontmatter = {}
        body = "# Test\n\nContent."

        result = render_frontmatter(frontmatter, body)

        # Should have minimal frontmatter section
        assert "---" in result
        assert "Content." in result

    def test_preserves_body_exactly(self):
        """Body content should be preserved exactly."""
        from frontmatter_normalizer.writer import render_frontmatter

        frontmatter = {"title": "Test"}
        body = "# Test\n\nParagraph one.\n\n## Section\n\nParagraph two.\n"

        result = render_frontmatter(frontmatter, body)

        # Body should appear exactly as given after frontmatter
        assert body in result


class TestWriterFieldOrdering:
    """Tests for field ordering in output."""

    def test_orders_fields_by_schema_priority(self):
        """Fields should be ordered: zkid, author, title, description, dates, category, tags, publish, status."""
        from frontmatter_normalizer.writer import render_frontmatter

        frontmatter = {
            "status": "draft",
            "tags": ["theory"],
            "zkid": "202411281430",
            "title": "Test",
            "category": "Concepts",
            "author": "Percy",
            "publish": False,
            "date-created": "2024-11-28",
            "date-edited": "2024-11-28",
            "description": "A test.",
        }
        body = "# Test"

        result = render_frontmatter(frontmatter, body)

        # Extract the YAML section
        lines = result.split("\n")
        yaml_lines = []
        in_yaml = False
        for line in lines:
            if line.strip() == "---":
                if in_yaml:
                    break
                in_yaml = True
                continue
            if in_yaml:
                yaml_lines.append(line)

        # Check ordering
        field_positions = {}
        for i, line in enumerate(yaml_lines):
            if ":" in line:
                field = line.split(":")[0].strip()
                field_positions[field] = i

        # zkid should come before author
        assert field_positions.get("zkid", 999) < field_positions.get("author", 999)
        # author should come before title
        assert field_positions.get("author", 999) < field_positions.get("title", 999)
        # category should come before tags
        assert field_positions.get("category", 999) < field_positions.get("tags", 999)
        # tags should come before publish
        assert field_positions.get("tags", 999) < field_positions.get("publish", 999)


class TestWriterYAMLFormatting:
    """Tests for YAML formatting."""

    def test_quotes_string_values_with_special_chars(self):
        """String values with special chars should be quoted."""
        from frontmatter_normalizer.writer import render_frontmatter

        frontmatter = {"title": "Test: A Subtitle"}
        body = "# Test"

        result = render_frontmatter(frontmatter, body)

        # Colon requires quoting
        assert "'Test: A Subtitle'" in result or '"Test: A Subtitle"' in result

    def test_renders_tags_as_yaml_array(self):
        """Tags should be rendered as YAML array."""
        from frontmatter_normalizer.writer import render_frontmatter

        frontmatter = {
            "tags": ["theory/marxism", "politics/organizing"]
        }
        body = "# Test"

        result = render_frontmatter(frontmatter, body)

        # Should be YAML array format
        assert "tags:" in result
        assert "  - theory/marxism" in result or "- theory/marxism" in result

    def test_renders_boolean_as_lowercase(self):
        """Boolean values should be lowercase (true/false)."""
        from frontmatter_normalizer.writer import render_frontmatter

        frontmatter = {"publish": False}
        body = "# Test"

        result = render_frontmatter(frontmatter, body)

        assert "publish: false" in result

    def test_quotes_date_strings(self):
        """Date strings should be quoted to prevent YAML date parsing."""
        from frontmatter_normalizer.writer import render_frontmatter

        frontmatter = {"date-created": "2024-11-28"}
        body = "# Test"

        result = render_frontmatter(frontmatter, body)

        # Should be quoted to prevent auto-parsing
        assert "'2024-11-28'" in result or '"2024-11-28"' in result

    def test_quotes_zkid_to_preserve_leading_zeros(self):
        """zkid should be quoted to preserve as string."""
        from frontmatter_normalizer.writer import render_frontmatter

        frontmatter = {"zkid": "202411281430"}
        body = "# Test"

        result = render_frontmatter(frontmatter, body)

        # Should be quoted string
        assert "'202411281430'" in result or '"202411281430"' in result


class TestWriterRoundTrip:
    """Tests for round-trip consistency."""

    def test_roundtrip_preserves_all_fields(self):
        """Parsing rendered output should give same frontmatter."""
        from frontmatter_normalizer.writer import render_frontmatter
        from frontmatter_normalizer.parser import parse_frontmatter

        original = {
            "zkid": "202411281430",
            "author": "Percy",
            "title": "Test Document",
            "description": "A test.",
            "date-created": "2024-11-28",
            "date-edited": "2024-11-28",
            "category": "Concepts",
            "tags": ["theory/marxism"],
            "publish": False,
            "status": "draft",
        }
        body = "# Test\n\nContent."

        rendered = render_frontmatter(original, body)
        parsed_fm, parsed_body = parse_frontmatter(rendered)

        assert parsed_fm == original
        assert parsed_body.strip() == body.strip()

    def test_roundtrip_with_complex_tags(self):
        """Complex tag arrays should survive round-trip."""
        from frontmatter_normalizer.writer import render_frontmatter
        from frontmatter_normalizer.parser import parse_frontmatter

        original = {
            "tags": [
                "theory/class-analysis",
                "politics/us-politics",
                "history/20th-century",
            ]
        }
        body = "# Test"

        rendered = render_frontmatter(original, body)
        parsed_fm, _ = parse_frontmatter(rendered)

        assert parsed_fm["tags"] == original["tags"]


class TestWriterFileOperations:
    """Tests for file write operations."""

    def test_write_to_file(self, tmp_path):
        """Should write normalized content to file."""
        from frontmatter_normalizer.writer import write_file

        filepath = tmp_path / "test.md"
        frontmatter = {"title": "Test", "category": "Concepts"}
        body = "# Test\n\nContent."

        write_file(filepath, frontmatter, body)

        content = filepath.read_text()
        assert "---" in content
        assert "title: Test" in content or "title: 'Test'" in content
        assert "Content." in content

    def test_backup_before_write(self, tmp_path):
        """Should create backup before overwriting."""
        from frontmatter_normalizer.writer import write_file

        filepath = tmp_path / "test.md"
        filepath.write_text("Original content")

        frontmatter = {"title": "New"}
        body = "# New content"

        write_file(filepath, frontmatter, body, backup=True)

        # Backup should exist
        backup_path = tmp_path / "test.md.bak"
        assert backup_path.exists()
        assert backup_path.read_text() == "Original content"

    def test_dry_run_does_not_write(self, tmp_path):
        """Dry run should not modify file."""
        from frontmatter_normalizer.writer import write_file

        filepath = tmp_path / "test.md"
        original = "Original content"
        filepath.write_text(original)

        frontmatter = {"title": "New"}
        body = "# New content"

        write_file(filepath, frontmatter, body, dry_run=True)

        # File should be unchanged
        assert filepath.read_text() == original
