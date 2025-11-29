"""Tests for frontmatter_normalizer config module.

Tests for category loading and validation from YAML files.
"""

import pytest
from pathlib import Path

import yaml


class TestLoadCategoriesFromYaml:
    """Tests for _load_categories_from_yaml function."""

    def test_raises_on_missing_file(self, tmp_path):
        """Should raise FileNotFoundError for non-existent file."""
        from frontmatter_normalizer.config import _load_categories_from_yaml

        missing_path = tmp_path / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError, match="Categories file not found"):
            _load_categories_from_yaml(missing_path)

    def test_raises_on_non_dict_yaml(self, tmp_path):
        """Should raise ValueError when YAML is not a dictionary."""
        from frontmatter_normalizer.config import _load_categories_from_yaml

        yaml_path = tmp_path / "categories.yaml"
        yaml_path.write_text("- item1\n- item2\n")  # List instead of dict

        with pytest.raises(ValueError, match="must be a dictionary"):
            _load_categories_from_yaml(yaml_path)

    def test_raises_on_non_dict_category_definition(self, tmp_path):
        """Should raise ValueError when category definition is not a dict."""
        from frontmatter_normalizer.config import _load_categories_from_yaml

        yaml_path = tmp_path / "categories.yaml"
        yaml_path.write_text("Theory: just a string\n")

        with pytest.raises(ValueError, match="must be a dictionary"):
            _load_categories_from_yaml(yaml_path)

    def test_raises_on_missing_keywords(self, tmp_path):
        """Should raise ValueError when keywords field is missing."""
        from frontmatter_normalizer.config import _load_categories_from_yaml

        yaml_path = tmp_path / "categories.yaml"
        yaml_path.write_text("""
Theory:
  description: "Test category"
  example_phrases:
    - "phrase one"
""")

        with pytest.raises(ValueError, match="missing 'keywords' field"):
            _load_categories_from_yaml(yaml_path)

    def test_raises_on_missing_example_phrases(self, tmp_path):
        """Should raise ValueError when example_phrases field is missing."""
        from frontmatter_normalizer.config import _load_categories_from_yaml

        yaml_path = tmp_path / "categories.yaml"
        yaml_path.write_text("""
Theory:
  description: "Test category"
  keywords:
    - keyword1
""")

        with pytest.raises(ValueError, match="missing 'example_phrases' field"):
            _load_categories_from_yaml(yaml_path)

    def test_loads_valid_yaml(self, tmp_path):
        """Should successfully load valid category definitions."""
        from frontmatter_normalizer.config import _load_categories_from_yaml

        yaml_path = tmp_path / "categories.yaml"
        yaml_path.write_text("""
Theory:
  description: "Explanatory essays"
  keywords:
    - theory
    - concept
  example_phrases:
    - "theoretical analysis"

Praxis:
  description: "How-to guides"
  keywords:
    - guide
    - how
  example_phrases:
    - "how to organize"
""")

        result = _load_categories_from_yaml(yaml_path)

        assert "Theory" in result
        assert "Praxis" in result
        assert result["Theory"]["keywords"] == ["theory", "concept"]
        assert result["Praxis"]["example_phrases"] == ["how to organize"]


class TestModuleLevelConstants:
    """Tests for module-level constants derived from loaded config."""

    def test_category_definitions_loaded(self):
        """CATEGORY_DEFINITIONS should be populated from YAML."""
        from frontmatter_normalizer.config import CATEGORY_DEFINITIONS

        assert isinstance(CATEGORY_DEFINITIONS, dict)
        assert len(CATEGORY_DEFINITIONS) > 0
        # Check expected categories from categories.yaml
        assert "Theory" in CATEGORY_DEFINITIONS
        assert "Praxis" in CATEGORY_DEFINITIONS
        assert "Polemics" in CATEGORY_DEFINITIONS

    def test_valid_categories_matches_definitions(self):
        """VALID_CATEGORIES should contain all keys from CATEGORY_DEFINITIONS."""
        from frontmatter_normalizer.config import (
            CATEGORY_DEFINITIONS,
            VALID_CATEGORIES,
        )

        assert VALID_CATEGORIES == set(CATEGORY_DEFINITIONS.keys())

    def test_schema_fields_defined(self):
        """SCHEMA_FIELDS should contain expected field names."""
        from frontmatter_normalizer.config import SCHEMA_FIELDS

        assert "category" in SCHEMA_FIELDS
        assert "tags" in SCHEMA_FIELDS
        assert "publish" in SCHEMA_FIELDS
        assert "title" in SCHEMA_FIELDS

    def test_field_order_matches_schema_fields(self):
        """FIELD_ORDER should contain all SCHEMA_FIELDS."""
        from frontmatter_normalizer.config import SCHEMA_FIELDS, FIELD_ORDER

        assert set(FIELD_ORDER) == SCHEMA_FIELDS

    def test_field_migrations_defined(self):
        """FIELD_MIGRATIONS should map old names to new names."""
        from frontmatter_normalizer.config import FIELD_MIGRATIONS

        assert isinstance(FIELD_MIGRATIONS, dict)
        assert "id" in FIELD_MIGRATIONS
        assert FIELD_MIGRATIONS["id"] == "zkid"

    def test_defaults_defined(self):
        """DEFAULTS should provide sensible default values."""
        from frontmatter_normalizer.config import DEFAULTS

        assert "author" in DEFAULTS
        assert "publish" in DEFAULTS
        assert DEFAULTS["publish"] is False
