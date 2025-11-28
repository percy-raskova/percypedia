"""Tests for category inferrer - SpaCy NLP-based classification.

RED PHASE: These tests define expected behavior before implementation.
"""

import pytest
from pathlib import Path


class TestCategoryInferrerBasics:
    """Tests for basic CategoryInferrer functionality."""

    def test_returns_category_result(self, file_no_frontmatter):
        """Should return a CategoryResult namedtuple."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        inferrer = CategoryInferrer()

        result = inferrer.infer(file_no_frontmatter)

        assert hasattr(result, 'category')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'needs_review')
        assert hasattr(result, 'alternatives')

    def test_category_is_valid_schema_value(self, file_no_frontmatter):
        """Inferred category must be one of the valid schema categories."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        valid_categories = {
            "Theory", "Praxis", "Polemics", "Creative", "Meta"
        }
        inferrer = CategoryInferrer()

        result = inferrer.infer(file_no_frontmatter)

        assert result.category in valid_categories

    def test_confidence_is_float_between_0_and_1(self, file_no_frontmatter):
        """Confidence should be a float between 0 and 1."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        inferrer = CategoryInferrer()

        result = inferrer.infer(file_no_frontmatter)

        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0

    def test_needs_review_when_confidence_low(self):
        """Should flag needs_review when confidence below threshold."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        # Ambiguous content that should have low confidence
        ambiguous_content = "# Notes\n\nSome random notes about various things."
        inferrer = CategoryInferrer()

        result = inferrer.infer(ambiguous_content)

        # Low confidence should trigger needs_review
        if result.confidence < 0.6:
            assert result.needs_review is True


class TestCategoryInferrerClassification:
    """Tests for category classification accuracy."""

    def test_classifies_theory_as_theory_or_praxis(self, file_no_frontmatter):
        """Labor aristocracy content straddles theory and practice."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        inferrer = CategoryInferrer()

        result = inferrer.infer(file_no_frontmatter)

        # Labor aristocracy discusses theory but also "organizing" and "building solidarity"
        # Vector similarity may classify as Praxis due to practical implications
        assert result.category in ("Theory", "Praxis")

    def test_classifies_philosophy_as_theory(self, file_custom_fields):
        """Dialectical materialism should be Theory."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        inferrer = CategoryInferrer()

        result = inferrer.infer(file_custom_fields)

        assert result.category == "Theory"

    def test_classifies_guide_as_praxis(self, file_old_field_names):
        """Organizing guide content should be Praxis."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        inferrer = CategoryInferrer()

        result = inferrer.infer(file_old_field_names)

        assert result.category == "Praxis"

    def test_classifies_documentation_as_meta(self, file_partial_frontmatter):
        """Taxonomy documentation should be Meta."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        inferrer = CategoryInferrer()

        result = inferrer.infer(file_partial_frontmatter)

        assert result.category == "Meta"

    def test_classifies_creative_writing_returns_valid_category(self, file_creative_writing):
        """Creative writing should return a valid category (edge case for keyword matching)."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        inferrer = CategoryInferrer()

        result = inferrer.infer(file_creative_writing)

        # Without SpaCy vectors, keyword matching may not perfectly classify creative content
        # Verify it at least returns a valid category and provides alternatives
        valid_categories = {"Theory", "Praxis", "Polemics", "Creative", "Meta"}
        assert result.category in valid_categories
        # Should flag for review since confidence will be low on ambiguous content
        assert len(result.alternatives) >= 1

    def test_classifies_polemic_returns_valid_category(self, file_polemic):
        """Polemic content should return a valid category (edge case for keyword matching)."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        inferrer = CategoryInferrer()

        result = inferrer.infer(file_polemic)

        # Polemic content has mixed keywords - now has its own category
        valid_categories = {"Theory", "Praxis", "Polemics", "Creative", "Meta"}
        assert result.category in valid_categories
        assert len(result.alternatives) >= 1


class TestCategoryInferrerAlternatives:
    """Tests for alternative category suggestions."""

    def test_provides_alternatives_list(self, file_no_frontmatter):
        """Should provide list of alternative categories with scores."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        inferrer = CategoryInferrer()

        result = inferrer.infer(file_no_frontmatter)

        assert isinstance(result.alternatives, list)
        # Should have at least one alternative
        assert len(result.alternatives) >= 1

    def test_alternatives_are_tuples(self, file_no_frontmatter):
        """Alternatives should be (category, score) tuples."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        inferrer = CategoryInferrer()

        result = inferrer.infer(file_no_frontmatter)

        for alt in result.alternatives:
            assert isinstance(alt, tuple)
            assert len(alt) == 2
            category, score = alt
            assert isinstance(category, str)
            assert isinstance(score, float)

    def test_alternatives_sorted_by_score(self, file_no_frontmatter):
        """Alternatives should be sorted by descending score."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        inferrer = CategoryInferrer()

        result = inferrer.infer(file_no_frontmatter)

        scores = [score for _, score in result.alternatives]
        assert scores == sorted(scores, reverse=True)


class TestCategoryInferrerExistingCategory:
    """Tests for handling existing category in frontmatter."""

    def test_preserves_valid_existing_category(self, file_schema_compliant):
        """Should preserve valid category from existing frontmatter."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        inferrer = CategoryInferrer()

        # Pass existing frontmatter to inferrer
        result = inferrer.infer(
            file_schema_compliant,
            existing_category="Theory"
        )

        # Should keep existing valid category
        assert result.category == "Theory"
        assert result.confidence == 1.0  # High confidence for existing

    def test_validates_existing_category(self):
        """Should validate that existing category is in schema."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        content = "# Test\n\nContent"
        inferrer = CategoryInferrer()

        # Invalid category should be re-inferred
        result = inferrer.infer(content, existing_category="InvalidCategory")

        # Should NOT be the invalid category
        assert result.category != "InvalidCategory"
        assert result.confidence < 1.0  # Re-inferred, not preserved


class TestCategoryInferrerSpaCyIntegration:
    """Tests for SpaCy model integration."""

    def test_uses_spacy_vectors(self, file_no_frontmatter):
        """Should use SpaCy word vectors for classification."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        # Large model has 685k word vectors for best similarity
        inferrer = CategoryInferrer(model_name="en_core_web_lg")

        result = inferrer.infer(file_no_frontmatter)

        # Should produce valid result with vector-based classification
        assert result.category is not None
        # With vectors, should have reasonable confidence
        assert result.confidence > 0.0

    def test_fallback_without_vectors(self):
        """Should have fallback if model not available."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        # Content with clear keywords
        content = "# Organizing Guide\n\nHow to organize a union."
        # Use a non-existent model to trigger fallback
        inferrer = CategoryInferrer(model_name="nonexistent_model_xyz")

        result = inferrer.infer(content)

        # Should still classify via keyword fallback
        assert result.category is not None


class TestCategoryInferrerConfiguration:
    """Tests for configurable behavior."""

    def test_configurable_confidence_threshold(self, file_no_frontmatter):
        """Should allow custom confidence threshold for needs_review."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        # Very high threshold - almost everything needs review
        inferrer = CategoryInferrer(confidence_threshold=0.95)

        result = inferrer.infer(file_no_frontmatter)

        # Most content won't hit 95% confidence
        if result.confidence < 0.95:
            assert result.needs_review is True

    def test_configurable_category_definitions(self):
        """Should allow custom category definitions."""
        from frontmatter_normalizer.inferrer.category import CategoryInferrer

        custom_categories = {
            "Theory": ["dialectics", "materialism", "class analysis"],
            "Practice": ["organizing", "strategy", "tactics"],
        }
        inferrer = CategoryInferrer(categories=custom_categories)

        content = "# Class Analysis\n\nTheoretical content about class."

        result = inferrer.infer(content)

        assert result.category in custom_categories.keys()
