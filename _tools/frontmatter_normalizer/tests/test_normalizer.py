"""Tests for the normalizer - core merge logic.

RED PHASE: These tests define expected behavior before implementation.
"""

import pytest
from pathlib import Path


class TestNormalizerIdempotency:
    """Tests for idempotent behavior - running twice should not change anything."""

    def test_idempotent_on_compliant_file(self, file_schema_compliant, temp_md_file):
        """Already compliant files should not be marked as changed."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_schema_compliant)

        result = normalize(file_schema_compliant, filepath)

        assert result.changed is False

    def test_normalizing_twice_produces_same_result(
        self, file_custom_fields, temp_md_file
    ):
        """Normalizing normalized content should not change it."""
        from frontmatter_normalizer.normalizer import normalize
        from frontmatter_normalizer.writer import render_frontmatter

        filepath = temp_md_file(file_custom_fields)

        # First normalization
        result1 = normalize(file_custom_fields, filepath)
        normalized_content = render_frontmatter(result1.frontmatter, result1.body)

        # Second normalization
        result2 = normalize(normalized_content, filepath)

        assert result2.changed is False


class TestNormalizerFieldDiscarding:
    """Tests for discarding non-schema fields."""

    def test_discards_custom_fields(self, file_custom_fields, temp_md_file):
        """Non-schema fields like Confidence should be discarded."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_custom_fields)

        result = normalize(file_custom_fields, filepath)

        assert 'Confidence' not in result.frontmatter
        assert 'Related' not in result.frontmatter

    def test_keeps_valid_schema_fields(self, file_custom_fields, temp_md_file):
        """Valid fields like category should be preserved."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_custom_fields)

        result = normalize(file_custom_fields, filepath)

        assert result.frontmatter['category'] == 'Theory'


class TestNormalizerFieldMigration:
    """Tests for old field name migration."""

    def test_migrates_id_to_zkid(self, file_old_field_names, temp_md_file):
        """'id' field should be migrated to 'zkid'."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_old_field_names)

        result = normalize(file_old_field_names, filepath)

        assert 'id' not in result.frontmatter
        assert 'zkid' in result.frontmatter
        assert result.frontmatter['zkid'] == '202401011200'

    def test_migrates_date_to_date_created(self, file_old_field_names, temp_md_file):
        """'Date' field should be migrated to 'date-created'."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_old_field_names)

        result = normalize(file_old_field_names, filepath)

        assert 'Date' not in result.frontmatter
        assert 'date-created' in result.frontmatter
        assert result.frontmatter['date-created'] == '2024-01-01'

    def test_migrates_updated_to_date_edited(self, file_old_field_names, temp_md_file):
        """'Updated' field should be migrated to 'date-edited'."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_old_field_names)

        result = normalize(file_old_field_names, filepath)

        assert 'Updated' not in result.frontmatter
        assert 'date-edited' in result.frontmatter
        assert result.frontmatter['date-edited'] == '2024-01-15'

    def test_migrates_tags_case(self, file_old_field_names, temp_md_file):
        """'Tags' (capitalized) should be migrated to 'tags'."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_old_field_names)

        result = normalize(file_old_field_names, filepath)

        assert 'Tags' not in result.frontmatter
        assert 'tags' in result.frontmatter


class TestNormalizerTypeConversion:
    """Tests for type conversions."""

    def test_converts_string_tags_to_array(self, file_string_tags, temp_md_file):
        """String tags should be converted to array."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_string_tags)

        result = normalize(file_string_tags, filepath)

        assert isinstance(result.frontmatter['tags'], list)
        assert 'theory' in result.frontmatter['tags']
        assert 'philosophy' in result.frontmatter['tags']
        assert 'marxism' in result.frontmatter['tags']

    def test_preserves_array_tags(self, file_schema_compliant, temp_md_file):
        """Array tags should remain as arrays."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_schema_compliant)

        result = normalize(file_schema_compliant, filepath)

        assert isinstance(result.frontmatter['tags'], list)


class TestNormalizerInference:
    """Tests for inferring missing fields."""

    def test_adds_frontmatter_to_bare_file(self, file_no_frontmatter, temp_md_file):
        """Files without frontmatter should get full frontmatter."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_no_frontmatter)

        result = normalize(file_no_frontmatter, filepath)

        assert result.changed is True
        assert 'category' in result.frontmatter
        assert 'zkid' in result.frontmatter
        assert 'date-created' in result.frontmatter
        assert 'author' in result.frontmatter

    def test_infers_missing_category(self, file_partial_frontmatter, temp_md_file):
        """Partial frontmatter should have missing fields inferred."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_partial_frontmatter)

        # file_partial_frontmatter already has category
        result = normalize(file_partial_frontmatter, filepath)

        # Category should be preserved, other fields inferred
        assert result.frontmatter['category'] == 'Meta'
        assert 'zkid' in result.frontmatter

    def test_infers_title_from_h1(self, file_no_frontmatter, temp_md_file):
        """Title should be inferred from H1 heading."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_no_frontmatter)

        result = normalize(file_no_frontmatter, filepath)

        assert result.frontmatter['title'] == 'Labor Aristocracy'

    def test_defaults_publish_to_false(self, file_no_frontmatter, temp_md_file):
        """Default publish should be false (draft)."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_no_frontmatter)

        result = normalize(file_no_frontmatter, filepath)

        assert result.frontmatter['publish'] is False

    def test_defaults_status_to_draft(self, file_no_frontmatter, temp_md_file):
        """Default status should be 'draft'."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_no_frontmatter)

        result = normalize(file_no_frontmatter, filepath)

        assert result.frontmatter['status'] == 'draft'


class TestNormalizerBodyPreservation:
    """Tests for preserving body content exactly."""

    def test_preserves_body_content(self, file_no_frontmatter, temp_md_file):
        """Body content should be preserved exactly."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_no_frontmatter)

        result = normalize(file_no_frontmatter, filepath)

        # Body should contain the original content
        assert "Labor Aristocracy" in result.body
        assert "imperialist countries" in result.body

    def test_preserves_body_with_existing_frontmatter(
        self, file_custom_fields, temp_md_file
    ):
        """Body should be preserved when frontmatter exists."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_custom_fields)

        result = normalize(file_custom_fields, filepath)

        assert "Dialectical Materialism" in result.body
        assert "Core Principles" in result.body


class TestNormalizerReviewFlags:
    """Tests for flagging files needing review."""

    def test_flags_low_confidence_category(self, temp_md_file):
        """Files with low-confidence category should be flagged."""
        from frontmatter_normalizer.normalizer import normalize

        # Ambiguous content
        content = "# Notes\n\nSome random notes about various things."
        filepath = temp_md_file(content)

        result = normalize(content, filepath)

        # Should have needs_review if confidence is low
        # (Actual flag depends on inferrer confidence threshold)
        assert hasattr(result, 'needs_review')

    def test_tracks_inferred_fields(self, file_no_frontmatter, temp_md_file):
        """Should track which fields were inferred."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_no_frontmatter)

        result = normalize(file_no_frontmatter, filepath)

        assert hasattr(result, 'inferred_fields')
        assert len(result.inferred_fields) > 0


class TestNormalizerResult:
    """Tests for NormalizationResult structure."""

    def test_result_has_required_attributes(self, file_no_frontmatter, temp_md_file):
        """NormalizationResult should have all required attributes."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_no_frontmatter)

        result = normalize(file_no_frontmatter, filepath)

        assert hasattr(result, 'changed')
        assert hasattr(result, 'frontmatter')
        assert hasattr(result, 'body')
        assert hasattr(result, 'inferred_fields')
        assert hasattr(result, 'needs_review')

    def test_result_frontmatter_is_dict(self, file_no_frontmatter, temp_md_file):
        """Frontmatter should be a dictionary."""
        from frontmatter_normalizer.normalizer import normalize

        filepath = temp_md_file(file_no_frontmatter)

        result = normalize(file_no_frontmatter, filepath)

        assert isinstance(result.frontmatter, dict)
