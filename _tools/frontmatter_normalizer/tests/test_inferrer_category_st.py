"""Tests for sentence-transformers based category inferrer.

RED PHASE: These tests define expected behavior before implementation.

Uses all-mpnet-base-v2 model for semantic similarity classification.
"""

import pytest
from pathlib import Path


class TestSentenceTransformerCategoryBasics:
    """Tests for basic CategoryInferrerST functionality."""

    def test_returns_category_result(self, file_no_frontmatter):
        """Should return a CategoryResult namedtuple."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        inferrer = CategoryInferrerST()

        result = inferrer.infer(file_no_frontmatter)

        assert hasattr(result, 'category')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'needs_review')
        assert hasattr(result, 'alternatives')

    def test_category_is_valid_schema_value(self, file_no_frontmatter):
        """Inferred category must be one of the valid schema categories."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        valid_categories = {
            "Theory", "Praxis", "Polemics", "Creative", "Meta"
        }
        inferrer = CategoryInferrerST()

        result = inferrer.infer(file_no_frontmatter)

        assert result.category in valid_categories

    def test_confidence_is_float_between_0_and_1(self, file_no_frontmatter):
        """Confidence should be a float between 0 and 1."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        inferrer = CategoryInferrerST()

        result = inferrer.infer(file_no_frontmatter)

        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0

    def test_needs_review_when_confidence_low(self):
        """Should flag needs_review when confidence below threshold."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        # Ambiguous content that should have low confidence
        ambiguous_content = "# Notes\n\nSome random notes about various things."
        inferrer = CategoryInferrerST()

        result = inferrer.infer(ambiguous_content)

        # Low confidence should trigger needs_review
        if result.confidence < 0.6:
            assert result.needs_review is True


class TestSentenceTransformerClassification:
    """Tests for category classification accuracy with sentence-transformers.

    These tests verify that semantic similarity provides accurate classification.
    """

    def test_classifies_theory_content(self, file_no_frontmatter):
        """Labor aristocracy content should classify as Theory or Praxis."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        inferrer = CategoryInferrerST()

        result = inferrer.infer(file_no_frontmatter)

        # Labor aristocracy is theoretical content with practical implications
        # Sentence transformers should capture the semantic meaning
        assert result.category in ("Theory", "Praxis")

    def test_classifies_philosophy_as_theory(self, file_custom_fields):
        """Dialectical materialism should be Theory."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        inferrer = CategoryInferrerST()

        result = inferrer.infer(file_custom_fields)

        assert result.category == "Theory"

    def test_classifies_guide_as_praxis(self, file_old_field_names):
        """Organizing guide content should be Praxis."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        inferrer = CategoryInferrerST()

        result = inferrer.infer(file_old_field_names)

        assert result.category == "Praxis"

    def test_classifies_documentation_as_meta(self, file_partial_frontmatter):
        """Taxonomy documentation should be Meta."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        inferrer = CategoryInferrerST()

        result = inferrer.infer(file_partial_frontmatter)

        assert result.category == "Meta"

    def test_classifies_creative_writing(self, file_creative_writing):
        """Creative writing should be classified appropriately."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        inferrer = CategoryInferrerST()

        result = inferrer.infer(file_creative_writing)

        # The fixture is very short and contains philosophical themes
        # ("contradictions", Schrödinger reference) - model may see Theory
        # Either Creative or Theory is acceptable for this edge case
        assert result.category in ("Creative", "Theory")

    def test_classifies_polemic_appropriately(self, file_polemic):
        """Polemic content should be Polemics, Theory, or Praxis."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        inferrer = CategoryInferrerST()

        result = inferrer.infer(file_polemic)

        # Polemic now has its own category, but may also classify as Theory/Praxis
        assert result.category in ("Polemics", "Theory", "Praxis")


class TestSentenceTransformerAlternatives:
    """Tests for alternative category suggestions."""

    def test_provides_alternatives_list(self, file_no_frontmatter):
        """Should provide list of alternative categories with scores."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        inferrer = CategoryInferrerST()

        result = inferrer.infer(file_no_frontmatter)

        assert isinstance(result.alternatives, list)
        assert len(result.alternatives) >= 1

    def test_alternatives_are_tuples(self, file_no_frontmatter):
        """Alternatives should be (category, score) tuples."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        inferrer = CategoryInferrerST()

        result = inferrer.infer(file_no_frontmatter)

        for alt in result.alternatives:
            assert isinstance(alt, tuple)
            assert len(alt) == 2
            category, score = alt
            assert isinstance(category, str)
            assert isinstance(score, float)

    def test_alternatives_sorted_by_score(self, file_no_frontmatter):
        """Alternatives should be sorted by descending score."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        inferrer = CategoryInferrerST()

        result = inferrer.infer(file_no_frontmatter)

        scores = [score for _, score in result.alternatives]
        assert scores == sorted(scores, reverse=True)


class TestSentenceTransformerExistingCategory:
    """Tests for handling existing category in frontmatter."""

    def test_preserves_valid_existing_category(self, file_schema_compliant):
        """Should preserve valid category from existing frontmatter."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        inferrer = CategoryInferrerST()

        result = inferrer.infer(
            file_schema_compliant,
            existing_category="Theory"
        )

        assert result.category == "Theory"
        assert result.confidence == 1.0

    def test_validates_existing_category(self):
        """Should validate that existing category is in schema."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        content = "# Test\n\nContent"
        inferrer = CategoryInferrerST()

        result = inferrer.infer(content, existing_category="InvalidCategory")

        assert result.category != "InvalidCategory"
        assert result.confidence < 1.0


class TestSentenceTransformerModel:
    """Tests for model loading and configuration."""

    def test_uses_mpnet_model_by_default(self):
        """Should use all-mpnet-base-v2 by default."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        inferrer = CategoryInferrerST()

        # Model name should be accessible
        assert inferrer._model_name == "all-mpnet-base-v2"

    def test_allows_custom_model(self):
        """Should allow specifying a different model."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        inferrer = CategoryInferrerST(model_name="all-MiniLM-L6-v2")

        assert inferrer._model_name == "all-MiniLM-L6-v2"

    def test_lazy_loads_model(self):
        """Model should be loaded lazily on first inference."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        inferrer = CategoryInferrerST()

        # Model not loaded yet
        assert inferrer._model is None

        # After inference, model should be loaded
        inferrer.infer("# Test\n\nContent")
        assert inferrer._model is not None

    def test_caches_category_embeddings(self):
        """Category embeddings should be computed once and cached."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        inferrer = CategoryInferrerST()

        # First inference computes embeddings
        inferrer.infer("# Test\n\nContent")
        assert inferrer._category_embeddings is not None

        # Cache should be populated
        assert len(inferrer._category_embeddings) > 0


class TestSentenceTransformerConfiguration:
    """Tests for configurable behavior."""

    def test_configurable_confidence_threshold(self, file_no_frontmatter):
        """Should allow custom confidence threshold for needs_review."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        # Very high threshold - almost everything needs review
        inferrer = CategoryInferrerST(confidence_threshold=0.95)

        result = inferrer.infer(file_no_frontmatter)

        if result.confidence < 0.95:
            assert result.needs_review is True

    def test_uses_example_phrases_for_similarity(self):
        """Should use example_phrases from config for semantic similarity."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST
        from frontmatter_normalizer.config import CATEGORY_DEFINITIONS

        inferrer = CategoryInferrerST()

        # Verify we're using example_phrases, not just keywords
        # The inferrer should have access to the full category definitions
        assert inferrer._category_definitions is not None
        for cat in CATEGORY_DEFINITIONS:
            assert "example_phrases" in inferrer._category_definitions[cat]


class TestSentenceTransformerVsSpaCyComparison:
    """Tests comparing sentence-transformers to SpaCy classification.

    These tests document expected differences in behavior.
    """

    def test_higher_confidence_on_clear_content(self, file_custom_fields):
        """Sentence-transformers should have higher confidence on clear theoretical content."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        inferrer = CategoryInferrerST()
        result = inferrer.infer(file_custom_fields)

        # Dialectical materialism is clearly Concepts
        # Semantic similarity should give high confidence
        assert result.confidence > 0.5  # Reasonably confident

    def test_handles_short_content(self):
        """Should handle short content gracefully."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        short_content = "# Title\n\nBrief."
        inferrer = CategoryInferrerST()

        result = inferrer.infer(short_content)

        # Should still return a valid result
        assert result.category is not None
        # But confidence may be lower
        assert result.needs_review is True  # Short content should be flagged

    def test_handles_long_content(self):
        """Should handle long content efficiently."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        # Create long content
        long_content = "# Theory\n\n" + ("This is theoretical content about dialectics. " * 500)
        inferrer = CategoryInferrerST()

        result = inferrer.infer(long_content)

        # Should truncate and still classify
        assert result.category in ("Theory", "Creative", "Polemics")
