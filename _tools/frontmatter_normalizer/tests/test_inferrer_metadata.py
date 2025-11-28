"""Tests for metadata inferrer - deterministic field extraction.

RED PHASE: These tests define expected behavior before implementation.
"""

import pytest
from pathlib import Path
from datetime import datetime
import re


class TestMetadataInferrerZkid:
    """Tests for Zettelkasten ID generation."""

    def test_generates_12_digit_zkid(self, temp_md_file, file_no_frontmatter):
        """zkid should be 12 digits in YYYYMMDDHHMM format."""
        from frontmatter_normalizer.inferrer.metadata import MetadataInferrer

        filepath = temp_md_file(file_no_frontmatter)
        inferrer = MetadataInferrer()

        zkid = inferrer.infer_zkid(filepath)

        assert len(zkid) == 12
        assert zkid.isdigit()

    def test_zkid_matches_pattern(self, temp_md_file, file_no_frontmatter):
        """zkid should match schema pattern ^[0-9]{12}$."""
        from frontmatter_normalizer.inferrer.metadata import MetadataInferrer

        filepath = temp_md_file(file_no_frontmatter)
        inferrer = MetadataInferrer()

        zkid = inferrer.infer_zkid(filepath)

        assert re.match(r'^[0-9]{12}$', zkid)

    def test_zkid_is_valid_datetime(self, temp_md_file, file_no_frontmatter):
        """zkid should represent a valid datetime."""
        from frontmatter_normalizer.inferrer.metadata import MetadataInferrer

        filepath = temp_md_file(file_no_frontmatter)
        inferrer = MetadataInferrer()

        zkid = inferrer.infer_zkid(filepath)

        # Should parse without error
        parsed = datetime.strptime(zkid, '%Y%m%d%H%M')
        assert parsed.year >= 2020  # Reasonable minimum


class TestMetadataInferrerDates:
    """Tests for date-created and date-edited inference."""

    def test_returns_dict_with_both_dates(self, temp_md_file, file_no_frontmatter):
        """Should return dict with date-created and date-edited."""
        from frontmatter_normalizer.inferrer.metadata import MetadataInferrer

        filepath = temp_md_file(file_no_frontmatter)
        inferrer = MetadataInferrer()

        dates = inferrer.infer_dates(filepath)

        assert 'date-created' in dates
        assert 'date-edited' in dates

    def test_dates_are_iso_format(self, temp_md_file, file_no_frontmatter):
        """Dates should be YYYY-MM-DD format."""
        from frontmatter_normalizer.inferrer.metadata import MetadataInferrer

        filepath = temp_md_file(file_no_frontmatter)
        inferrer = MetadataInferrer()

        dates = inferrer.infer_dates(filepath)

        # Should match YYYY-MM-DD
        assert re.match(r'^\d{4}-\d{2}-\d{2}$', dates['date-created'])
        assert re.match(r'^\d{4}-\d{2}-\d{2}$', dates['date-edited'])

    def test_dates_are_valid(self, temp_md_file, file_no_frontmatter):
        """Dates should parse as valid dates."""
        from frontmatter_normalizer.inferrer.metadata import MetadataInferrer

        filepath = temp_md_file(file_no_frontmatter)
        inferrer = MetadataInferrer()

        dates = inferrer.infer_dates(filepath)

        # Should parse without error
        datetime.strptime(dates['date-created'], '%Y-%m-%d')
        datetime.strptime(dates['date-edited'], '%Y-%m-%d')


class TestMetadataInferrerTitle:
    """Tests for title extraction from H1."""

    def test_extracts_h1_title(self, file_no_frontmatter):
        """Should extract title from first H1 heading."""
        from frontmatter_normalizer.inferrer.metadata import MetadataInferrer

        inferrer = MetadataInferrer()

        title = inferrer.infer_title(file_no_frontmatter)

        assert title == "Labor Aristocracy"

    def test_returns_none_without_h1(self):
        """Should return None if no H1 found."""
        from frontmatter_normalizer.inferrer.metadata import MetadataInferrer

        content = "No heading here, just text."
        inferrer = MetadataInferrer()

        title = inferrer.infer_title(content)

        assert title is None

    def test_uses_first_h1_only(self):
        """Should use first H1 if multiple exist."""
        from frontmatter_normalizer.inferrer.metadata import MetadataInferrer

        content = "# First Title\n\nContent.\n\n# Second Title\n\nMore content."
        inferrer = MetadataInferrer()

        title = inferrer.infer_title(content)

        assert title == "First Title"

    def test_handles_frontmatter_before_h1(self, file_schema_compliant):
        """Should find H1 even with frontmatter present."""
        from frontmatter_normalizer.inferrer.metadata import MetadataInferrer

        inferrer = MetadataInferrer()

        title = inferrer.infer_title(file_schema_compliant)

        assert title == "Test Document"


class TestMetadataInferrerAuthor:
    """Tests for default author."""

    def test_returns_default_author(self):
        """Should return 'Percy' as default author."""
        from frontmatter_normalizer.inferrer.metadata import MetadataInferrer

        inferrer = MetadataInferrer()

        author = inferrer.infer_author()

        assert author == "Percy"

    def test_author_is_configurable(self):
        """Should allow custom default author via config."""
        from frontmatter_normalizer.inferrer.metadata import MetadataInferrer

        inferrer = MetadataInferrer(default_author="Custom Author")

        author = inferrer.infer_author()

        assert author == "Custom Author"
