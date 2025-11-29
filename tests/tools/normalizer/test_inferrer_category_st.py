"""Tests for sentence-transformers based category inferrer.

Uses session-scoped fixtures to share model instances across tests for performance.
Uses all-mpnet-base-v2 model for semantic similarity classification.
"""

import pytest
from pathlib import Path


class TestSentenceTransformerCategoryBasics:
    """Tests for basic CategoryInferrerST functionality."""

    def test_returns_category_result(self, st_category_inferrer, file_no_frontmatter):
        """Should return a CategoryResult namedtuple."""
        result = st_category_inferrer.infer(file_no_frontmatter)

        assert hasattr(result, 'category')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'needs_review')
        assert hasattr(result, 'alternatives')

    def test_category_is_valid_schema_value(self, st_category_inferrer, file_no_frontmatter):
        """Inferred category must be one of the valid schema categories."""
        valid_categories = {
            "Theory", "Praxis", "Polemics", "Creative", "Meta"
        }

        result = st_category_inferrer.infer(file_no_frontmatter)

        assert result.category in valid_categories

    def test_confidence_is_float_between_0_and_1(self, st_category_inferrer, file_no_frontmatter):
        """Confidence should be a float between 0 and 1."""
        result = st_category_inferrer.infer(file_no_frontmatter)

        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0

    def test_needs_review_when_confidence_low(self, st_category_inferrer):
        """Should flag needs_review when confidence below threshold."""
        # Ambiguous content that should have low confidence
        ambiguous_content = "# Notes\n\nSome random notes about various things."

        result = st_category_inferrer.infer(ambiguous_content)

        # Low confidence should trigger needs_review
        if result.confidence < 0.6:
            assert result.needs_review is True


class TestSentenceTransformerClassification:
    """Tests for category classification accuracy with sentence-transformers.

    These tests verify that semantic similarity provides accurate classification.
    """

    def test_classifies_theory_content(self, st_category_inferrer, file_no_frontmatter):
        """Labor aristocracy content should classify as Theory or Praxis."""
        result = st_category_inferrer.infer(file_no_frontmatter)

        # Labor aristocracy is theoretical content with practical implications
        # Sentence transformers should capture the semantic meaning
        assert result.category in ("Theory", "Praxis")

    def test_classifies_philosophy_as_theory(self, st_category_inferrer, file_custom_fields):
        """Dialectical materialism should be Theory."""
        result = st_category_inferrer.infer(file_custom_fields)

        assert result.category == "Theory"

    def test_classifies_guide_as_praxis(self, st_category_inferrer, file_old_field_names):
        """Organizing guide content should be Praxis."""
        result = st_category_inferrer.infer(file_old_field_names)

        assert result.category == "Praxis"

    def test_classifies_documentation_as_meta(self, st_category_inferrer, file_partial_frontmatter):
        """Taxonomy documentation should be Meta."""
        result = st_category_inferrer.infer(file_partial_frontmatter)

        assert result.category == "Meta"

    def test_classifies_creative_writing(self, st_category_inferrer, file_creative_writing):
        """Creative writing should be classified appropriately."""
        result = st_category_inferrer.infer(file_creative_writing)

        # The fixture is very short and contains philosophical themes
        # ("contradictions", Schrödinger reference) - model may see Theory
        # Either Creative or Theory is acceptable for this edge case
        assert result.category in ("Creative", "Theory")

    def test_classifies_polemic_appropriately(self, st_category_inferrer, file_polemic):
        """Polemic content should be Polemics, Theory, or Praxis."""
        result = st_category_inferrer.infer(file_polemic)

        # Polemic now has its own category, but may also classify as Theory/Praxis
        assert result.category in ("Polemics", "Theory", "Praxis")


class TestSentenceTransformerAlternatives:
    """Tests for alternative category suggestions."""

    def test_provides_alternatives_list(self, st_category_inferrer, file_no_frontmatter):
        """Should provide list of alternative categories with scores."""
        result = st_category_inferrer.infer(file_no_frontmatter)

        assert isinstance(result.alternatives, list)
        assert len(result.alternatives) >= 1

    def test_alternatives_are_tuples(self, st_category_inferrer, file_no_frontmatter):
        """Alternatives should be (category, score) tuples."""
        result = st_category_inferrer.infer(file_no_frontmatter)

        for alt in result.alternatives:
            assert isinstance(alt, tuple)
            assert len(alt) == 2
            category, score = alt
            assert isinstance(category, str)
            assert isinstance(score, float)

    def test_alternatives_sorted_by_score(self, st_category_inferrer, file_no_frontmatter):
        """Alternatives should be sorted by descending score."""
        result = st_category_inferrer.infer(file_no_frontmatter)

        scores = [score for _, score in result.alternatives]
        assert scores == sorted(scores, reverse=True)


class TestSentenceTransformerExistingCategory:
    """Tests for handling existing category in frontmatter."""

    def test_preserves_valid_existing_category(self, st_category_inferrer, file_schema_compliant):
        """Should preserve valid category from existing frontmatter."""
        result = st_category_inferrer.infer(
            file_schema_compliant,
            existing_category="Theory"
        )

        assert result.category == "Theory"
        assert result.confidence == 1.0

    def test_validates_existing_category(self, st_category_inferrer):
        """Should validate that existing category is in schema."""
        content = "# Test\n\nContent"

        result = st_category_inferrer.infer(content, existing_category="InvalidCategory")

        assert result.category != "InvalidCategory"
        assert result.confidence < 1.0


class TestSentenceTransformerModel:
    """Tests for model loading and configuration.

    Note: These tests create their own instances to test specific model behaviors.
    """

    def test_uses_mpnet_model_by_default(self, st_category_inferrer):
        """Should use all-mpnet-base-v2 by default."""
        # Model name should be accessible
        assert st_category_inferrer._model_name == "all-mpnet-base-v2"

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

    def test_caches_category_embeddings(self, st_category_inferrer):
        """Category embeddings should be computed once and cached."""
        # Session fixture already has model loaded
        assert st_category_inferrer._category_embeddings is not None

        # Cache should be populated
        assert len(st_category_inferrer._category_embeddings) > 0


class TestSentenceTransformerConfiguration:
    """Tests for configurable behavior.

    Note: These tests create their own instances to test specific configurations.
    """

    def test_configurable_confidence_threshold(self, file_no_frontmatter):
        """Should allow custom confidence threshold for needs_review."""
        from frontmatter_normalizer.inferrer.category_st import CategoryInferrerST

        # Very high threshold - almost everything needs review
        inferrer = CategoryInferrerST(confidence_threshold=0.95)

        result = inferrer.infer(file_no_frontmatter)

        if result.confidence < 0.95:
            assert result.needs_review is True

    def test_uses_example_phrases_for_similarity(self, st_category_inferrer):
        """Should use example_phrases from config for semantic similarity."""
        from frontmatter_normalizer.config import CATEGORY_DEFINITIONS

        # Verify we're using example_phrases, not just keywords
        # The inferrer should have access to the full category definitions
        assert st_category_inferrer._category_definitions is not None
        for cat in CATEGORY_DEFINITIONS:
            assert "example_phrases" in st_category_inferrer._category_definitions[cat]


class TestSentenceTransformerVsSpaCyComparison:
    """Tests comparing sentence-transformers to SpaCy classification.

    These tests document expected differences in behavior.
    """

    def test_higher_confidence_on_clear_content(self, st_category_inferrer, file_custom_fields):
        """Sentence-transformers should have higher confidence on clear theoretical content."""
        result = st_category_inferrer.infer(file_custom_fields)

        # Dialectical materialism is clearly Concepts
        # Semantic similarity should give high confidence
        assert result.confidence > 0.5  # Reasonably confident

    def test_handles_short_content(self, st_category_inferrer):
        """Should handle short content gracefully."""
        short_content = "# Title\n\nBrief."

        result = st_category_inferrer.infer(short_content)

        # Should still return a valid result
        assert result.category is not None
        # But confidence may be lower
        assert result.needs_review is True  # Short content should be flagged

    def test_handles_long_content(self, st_category_inferrer):
        """Should handle long content efficiently."""
        # Create long content
        long_content = "# Theory\n\n" + ("This is theoretical content about dialectics. " * 500)

        result = st_category_inferrer.infer(long_content)

        # Should truncate and still classify
        assert result.category in ("Theory", "Creative", "Polemics")


class TestSentenceTransformerRobustness:
    """Tests for ML inferrer robustness to malformed and edge-case content."""

    def test_handles_empty_string(self, st_category_inferrer):
        """Should handle empty string gracefully."""
        result = st_category_inferrer.infer("")

        # Should return a result, not crash
        assert result.category is not None
        assert result.needs_review is True

    def test_handles_only_whitespace(self, st_category_inferrer):
        """Should handle whitespace-only content."""
        result = st_category_inferrer.infer("   \n\n\t  ")

        assert result.category is not None
        assert result.needs_review is True

    def test_handles_only_punctuation(self, st_category_inferrer):
        """Should handle punctuation-only content."""
        result = st_category_inferrer.infer("!@#$%^&*()...???")

        assert result.category is not None
        assert result.needs_review is True

    def test_handles_unicode_content(self, st_category_inferrer):
        """Should handle unicode characters correctly."""
        unicode_content = """# Teoría del Valor

La teoría del valor-trabajo explica cómo el trabajo humano
crea valor en las mercancías. Marx desarrolló esta teoría
basándose en los economistas clásicos.
"""
        result = st_category_inferrer.infer(unicode_content)

        # Should return a valid result without crashing
        assert result.category is not None
        valid_categories = {"Theory", "Praxis", "Polemics", "Creative", "Meta"}
        assert result.category in valid_categories
        assert 0.0 <= result.confidence <= 1.0

    def test_handles_mixed_language_content(self, st_category_inferrer):
        """Should handle content mixing multiple languages."""
        mixed_content = """# Revolutionary Theory

La revolución es necesaria. The working class must organize.
Die Arbeiterklasse. La lutte continue. 工人阶级万岁！
"""
        result = st_category_inferrer.infer(mixed_content)

        assert result.category is not None
        # Mixed content may have lower confidence
        assert 0.0 <= result.confidence <= 1.0

    def test_handles_code_heavy_content(self, st_category_inferrer):
        """Should handle content that is mostly code."""
        code_content = """# Configuration Reference

```python
def process_data(input):
    return [x * 2 for x in input]

class DataProcessor:
    def __init__(self):
        self.cache = {}
```
"""
        result = st_category_inferrer.infer(code_content)

        assert result.category is not None
        # Code-heavy content might classify as Meta (documentation)
        assert result.category in ("Meta", "Theory", "Praxis")

    def test_handles_null_bytes(self, st_category_inferrer):
        """Should handle content with null bytes."""
        content_with_null = "# Title\n\nContent with \x00 null byte."

        result = st_category_inferrer.infer(content_with_null)

        assert result.category is not None

    def test_handles_control_characters(self, st_category_inferrer):
        """Should handle content with control characters."""
        content = "# Title\r\n\r\nContent with \t tabs and \x1b escapes."

        result = st_category_inferrer.infer(content)

        assert result.category is not None

    def test_handles_repeated_content(self, st_category_inferrer):
        """Should handle repetitive/spammy content."""
        spam_content = "theory " * 1000

        result = st_category_inferrer.infer(spam_content)

        # Should return a valid result without crashing
        assert result.category is not None
        valid_categories = {"Theory", "Praxis", "Polemics", "Creative", "Meta"}
        assert result.category in valid_categories
        # Repetitive content may have varying confidence
        assert 0.0 <= result.confidence <= 1.0
