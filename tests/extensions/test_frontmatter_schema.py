"""Tests for frontmatter_schema validation.

TDD RED phase: These tests define the expected schema behavior.
Run with: PYTHONPATH=_extensions pytest _extensions/frontmatter_schema/tests/ -v
"""

import json
import pytest
from pathlib import Path


class TestSchemaLoading:
    """Tests for loading the JSON schema."""

    def test_schema_file_exists(self):
        from frontmatter_schema import SCHEMA_PATH
        assert SCHEMA_PATH.exists(), f"Schema not found at {SCHEMA_PATH}"

    def test_schema_is_valid_json(self):
        from frontmatter_schema import load_schema
        schema = load_schema()
        assert isinstance(schema, dict)
        assert '$schema' in schema

    def test_schema_has_required_structure(self):
        from frontmatter_schema import load_schema
        schema = load_schema()

        assert schema['type'] == 'object'
        assert 'properties' in schema

        # All expected fields defined
        expected_fields = [
            'zkid', 'author', 'title', 'description',
            'date-created', 'date-edited', 'category', 'tags',
            'publish', 'status'
        ]
        for field in expected_fields:
            assert field in schema['properties'], f"Missing field: {field}"


class TestValidFrontmatter:
    """Tests for valid frontmatter that should pass validation."""

    def test_empty_frontmatter_is_valid(self):
        """All fields are optional, so empty frontmatter is valid."""
        from frontmatter_schema import validate_frontmatter
        errors = validate_frontmatter({})
        assert errors == []

    def test_minimal_frontmatter_is_valid(self):
        from frontmatter_schema import validate_frontmatter
        errors = validate_frontmatter({
            'title': 'Test Document'
        })
        assert errors == []

    def test_complete_frontmatter_is_valid(self):
        from frontmatter_schema import validate_frontmatter
        errors = validate_frontmatter({
            'zkid': '202411281430',
            'author': 'Percy',
            'title': 'Labor Aristocracy',
            'description': 'Analysis of labor aristocracy.',
            'date-created': '2024-11-28',
            'date-edited': '2024-11-28',
            'category': 'Theory',
            'tags': ['theory/class-analysis', 'politics/marxism'],
            'publish': True,
            'status': 'complete'
        })
        assert errors == []

    def test_publish_false_is_valid(self):
        from frontmatter_schema import validate_frontmatter
        errors = validate_frontmatter({
            'title': 'Draft Document',
            'publish': False
        })
        assert errors == []

    def test_all_status_values_are_valid(self):
        from frontmatter_schema import validate_frontmatter
        for status in ['draft', 'review', 'complete']:
            errors = validate_frontmatter({
                'title': 'Test',
                'status': status
            })
            assert errors == [], f"Status '{status}' should be valid"

    def test_hierarchical_tags_are_valid(self):
        from frontmatter_schema import validate_frontmatter
        errors = validate_frontmatter({
            'tags': [
                'theory/marxism',
                'politics/labor-aristocracy',
                'organizing/strategy/community'
            ]
        })
        assert errors == []

    def test_single_tag_is_valid(self):
        from frontmatter_schema import validate_frontmatter
        errors = validate_frontmatter({
            'tags': ['theory']
        })
        assert errors == []


class TestInvalidFrontmatter:
    """Tests for invalid frontmatter that should fail validation."""

    def test_invalid_zkid_format(self):
        from frontmatter_schema import validate_frontmatter

        # Too short
        errors = validate_frontmatter({'zkid': '20241128'})
        assert len(errors) > 0
        assert 'zkid' in errors[0]

        # Contains letters
        errors = validate_frontmatter({'zkid': '2024112814ab'})
        assert len(errors) > 0

        # Too long
        errors = validate_frontmatter({'zkid': '2024112814301'})
        assert len(errors) > 0

    def test_invalid_status_value(self):
        from frontmatter_schema import validate_frontmatter
        errors = validate_frontmatter({'status': 'published'})
        assert len(errors) > 0
        assert 'status' in errors[0]

    def test_publish_must_be_boolean(self):
        from frontmatter_schema import validate_frontmatter
        errors = validate_frontmatter({'publish': 'yes'})
        assert len(errors) > 0
        assert 'publish' in errors[0]

    def test_tags_must_be_array(self):
        from frontmatter_schema import validate_frontmatter
        errors = validate_frontmatter({'tags': 'theory, politics'})
        assert len(errors) > 0
        assert 'tags' in errors[0]

    def test_tags_must_be_lowercase(self):
        from frontmatter_schema import validate_frontmatter
        errors = validate_frontmatter({'tags': ['Theory/Marxism']})
        assert len(errors) > 0

    def test_tags_cannot_have_spaces(self):
        from frontmatter_schema import validate_frontmatter
        errors = validate_frontmatter({'tags': ['theory marxism']})
        assert len(errors) > 0

    def test_title_cannot_be_empty_string(self):
        from frontmatter_schema import validate_frontmatter
        errors = validate_frontmatter({'title': ''})
        assert len(errors) > 0
        assert 'title' in errors[0]

    def test_unknown_fields_are_rejected(self):
        """additionalProperties: false means extra fields fail."""
        from frontmatter_schema import validate_frontmatter
        errors = validate_frontmatter({
            'title': 'Test',
            'slug': 'test-slug',  # Not in schema
            'confidence': 'high'  # Not in schema
        })
        assert len(errors) > 0

    def test_duplicate_tags_are_rejected(self):
        from frontmatter_schema import validate_frontmatter
        errors = validate_frontmatter({
            'tags': ['theory/marxism', 'theory/marxism']
        })
        assert len(errors) > 0


class TestExtractFrontmatter:
    """Tests for extracting frontmatter from markdown content."""

    def test_extracts_valid_frontmatter(self):
        from frontmatter_schema import extract_frontmatter
        content = """---
title: Test Document
category: Theory
---

# Heading
"""
        result = extract_frontmatter(content)
        assert result['title'] == 'Test Document'
        assert result['category'] == 'Theory'

    def test_returns_empty_dict_without_frontmatter(self):
        from frontmatter_schema import extract_frontmatter
        content = "# Just a heading\n\nNo frontmatter."
        result = extract_frontmatter(content)
        assert result == {}

    def test_handles_tags_as_array(self):
        from frontmatter_schema import extract_frontmatter
        content = """---
tags:
  - theory/marxism
  - politics/strategy
---
"""
        result = extract_frontmatter(content)
        assert result['tags'] == ['theory/marxism', 'politics/strategy']


class TestExtractAndValidate:
    """Tests for combined extraction and validation."""

    def test_valid_markdown_passes(self):
        from frontmatter_schema import extract_and_validate
        content = """---
title: Valid Document
category: Theory
tags:
  - theory/marxism
publish: true
status: complete
---

# Valid Document
"""
        errors = extract_and_validate(content)
        assert errors == []

    def test_invalid_markdown_fails(self):
        from frontmatter_schema import extract_and_validate
        content = """---
status: invalid_status
tags: not_an_array
---

# Invalid
"""
        errors = extract_and_validate(content)
        assert len(errors) >= 2  # At least status and tags errors

    def test_no_frontmatter_is_valid(self):
        from frontmatter_schema import extract_and_validate
        content = "# Just Content\n\nNo frontmatter here."
        errors = extract_and_validate(content)
        assert errors == []


class TestValidateFile:
    """Tests for validating individual files."""

    def test_validates_file_from_path(self, tmp_path):
        from frontmatter_schema import validate_file

        test_file = tmp_path / 'test.md'
        test_file.write_text("""---
title: Test
status: invalid_value
---
# Test
""")
        errors = validate_file(test_file)
        assert len(errors) > 0
        assert 'status' in errors[0]

    def test_valid_file_returns_empty_list(self, tmp_path):
        from frontmatter_schema import validate_file

        test_file = tmp_path / 'valid.md'
        test_file.write_text("""---
title: Valid
category: Theory
publish: true
---
# Valid
""")
        errors = validate_file(test_file)
        assert errors == []


class TestValidateDirectory:
    """Tests for batch validation of directories."""

    def test_finds_all_invalid_files(self, tmp_path):
        from frontmatter_schema import validate_directory

        # Valid file
        (tmp_path / 'valid.md').write_text('---\ntitle: Valid\n---\n# Valid')

        # Invalid file
        (tmp_path / 'invalid.md').write_text('---\nstatus: bad\n---\n# Invalid')

        results = validate_directory(tmp_path)

        assert 'valid.md' not in results
        assert 'invalid.md' in results
        assert len(results['invalid.md']) > 0

    def test_skips_excluded_directories(self, tmp_path):
        from frontmatter_schema import validate_directory

        # File in excluded directory
        (tmp_path / '.venv').mkdir()
        (tmp_path / '.venv' / 'bad.md').write_text('---\nstatus: invalid\n---\n# Bad')

        # File in underscore directory
        (tmp_path / '_templates').mkdir()
        (tmp_path / '_templates' / 'template.md').write_text('---\nstatus: invalid\n---\n')

        results = validate_directory(tmp_path)

        assert '.venv/bad.md' not in results
        assert '_templates/template.md' not in results

    def test_returns_empty_dict_when_all_valid(self, tmp_path):
        from frontmatter_schema import validate_directory

        (tmp_path / 'doc1.md').write_text('---\ntitle: Doc 1\n---\n# Doc 1')
        (tmp_path / 'doc2.md').write_text('---\ntitle: Doc 2\n---\n# Doc 2')

        results = validate_directory(tmp_path)

        assert results == {}

    def test_handles_nested_directories(self, tmp_path):
        from frontmatter_schema import validate_directory

        (tmp_path / 'theory').mkdir()
        (tmp_path / 'theory' / 'bad.md').write_text('---\nstatus: invalid\n---\n# Bad')

        results = validate_directory(tmp_path)

        assert 'theory/bad.md' in results
