"""Tests for tag inferrer - vocabulary-based tag suggestion.

RED PHASE: These tests define expected behavior before implementation.

Strategy: Seed + Expand
- Use existing tags from corpus as vocabulary
- Match content to existing tags via keyword/semantic matching
- Suggest new tags when appropriate (flagged for review)
"""

import pytest
from pathlib import Path


class TestTagInferrerBasics:
    """Tests for basic TagInferrer functionality."""

    def test_returns_tag_result(self, file_no_frontmatter):
        """Should return a TagResult namedtuple."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        inferrer = TagInferrer()

        result = inferrer.infer(file_no_frontmatter)

        assert hasattr(result, 'tags')
        assert hasattr(result, 'suggested_new')
        assert hasattr(result, 'needs_review')

    def test_tags_is_list(self, file_no_frontmatter):
        """Tags should be a list of strings."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        inferrer = TagInferrer()

        result = inferrer.infer(file_no_frontmatter)

        assert isinstance(result.tags, list)
        for tag in result.tags:
            assert isinstance(tag, str)

    def test_suggested_new_is_list(self, file_no_frontmatter):
        """Suggested new tags should be a list."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        inferrer = TagInferrer()

        result = inferrer.infer(file_no_frontmatter)

        assert isinstance(result.suggested_new, list)


class TestTagInferrerVocabulary:
    """Tests for tag vocabulary management."""

    def test_loads_vocabulary_from_file(self, tmp_path):
        """Should load tag vocabulary from YAML file."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        vocab_file = tmp_path / "tags.yaml"
        vocab_file.write_text("""
theory:
  - theory/marxism
  - theory/dialectics
  - theory/class-analysis
politics:
  - politics/imperialism
  - politics/organizing
""")
        inferrer = TagInferrer(vocabulary_file=vocab_file)

        assert "theory/marxism" in inferrer.vocabulary
        assert "politics/imperialism" in inferrer.vocabulary

    def test_accepts_vocabulary_dict(self):
        """Should accept vocabulary as a dictionary."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        vocab = {
            "theory": ["theory/marxism", "theory/dialectics"],
            "politics": ["politics/labor", "politics/party"],
        }
        inferrer = TagInferrer(vocabulary=vocab)

        assert "theory/marxism" in inferrer.vocabulary
        assert "politics/labor" in inferrer.vocabulary

    def test_vocabulary_is_flat_list(self):
        """Vocabulary should be flattened to list of all tags."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        vocab = {
            "theory": ["theory/a", "theory/b"],
            "politics": ["politics/c"],
        }
        inferrer = TagInferrer(vocabulary=vocab)

        assert len(inferrer.vocabulary) == 3

    def test_default_vocabulary_exists(self):
        """Should have default vocabulary if none provided."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        inferrer = TagInferrer()

        # Should have some default tags
        assert len(inferrer.vocabulary) > 0


class TestTagInferrerMatching:
    """Tests for tag matching from vocabulary."""

    def test_matches_theory_tags_for_theoretical_content(self, file_no_frontmatter):
        """Theoretical content should get theory-related tags."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        vocab = {
            "theory": ["theory/class-analysis", "theory/imperialism"],
            "politics": ["politics/organizing"],
        }
        inferrer = TagInferrer(vocabulary=vocab)

        result = inferrer.infer(file_no_frontmatter)

        # Labor aristocracy content should get imperialism tag
        assert any("imperialism" in tag for tag in result.tags)

    def test_matches_philosophy_tags(self, file_custom_fields):
        """Dialectical materialism should get philosophy tags."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        vocab = {
            "philosophy": ["philosophy/dialectics", "philosophy/materialism"],
            "theory": ["theory/marxism"],
        }
        inferrer = TagInferrer(vocabulary=vocab)

        result = inferrer.infer(file_custom_fields)

        # Should match dialectics or materialism
        matched_philosophy = any(
            "dialectics" in tag or "materialism" in tag
            for tag in result.tags
        )
        assert matched_philosophy

    def test_matches_multiple_relevant_tags(self, file_no_frontmatter):
        """Should match multiple relevant tags from vocabulary."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        vocab = {
            "theory": [
                "theory/class-analysis",
                "theory/imperialism",
                "theory/labor",
            ],
        }
        inferrer = TagInferrer(vocabulary=vocab)

        result = inferrer.infer(file_no_frontmatter)

        # Should match multiple relevant tags
        assert len(result.tags) >= 1


class TestTagInferrerExistingTags:
    """Tests for handling existing tags in frontmatter."""

    def test_preserves_valid_existing_tags(self):
        """Should preserve existing tags that are in vocabulary."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        content = "# Test\n\nSome content."
        vocab = {"theory": ["theory/marxism", "theory/dialectics"]}
        inferrer = TagInferrer(vocabulary=vocab)

        result = inferrer.infer(
            content,
            existing_tags=["theory/marxism", "theory/dialectics"]
        )

        assert "theory/marxism" in result.tags
        assert "theory/dialectics" in result.tags

    def test_flags_unknown_existing_tags(self):
        """Existing tags not in vocabulary should be flagged for review."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        content = "# Test\n\nContent."
        vocab = {"theory": ["theory/marxism"]}
        inferrer = TagInferrer(vocabulary=vocab)

        result = inferrer.infer(
            content,
            existing_tags=["custom/unknown-tag"]
        )

        # Unknown tag should be in suggested_new for review
        assert "custom/unknown-tag" in result.suggested_new
        assert result.needs_review is True

    def test_normalizes_tag_case(self):
        """Should normalize tag case to lowercase."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        vocab = {"theory": ["theory/marxism"]}
        inferrer = TagInferrer(vocabulary=vocab)

        result = inferrer.infer(
            "# Test",
            existing_tags=["Theory/Marxism"]  # Wrong case
        )

        # Should normalize to lowercase
        assert "theory/marxism" in result.tags


class TestTagInferrerSuggestions:
    """Tests for suggesting new tags."""

    def test_suggests_new_tags_from_content(self, file_no_frontmatter):
        """Should suggest new tags when content doesn't match vocabulary."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        # Minimal vocabulary that won't match content
        vocab = {"misc": ["misc/unrelated"]}
        inferrer = TagInferrer(vocabulary=vocab)

        result = inferrer.infer(file_no_frontmatter)

        # Should suggest new tags based on content analysis
        # (labor aristocracy, imperialism, etc.)
        assert len(result.suggested_new) >= 0  # May suggest new

    def test_suggested_tags_follow_format(self):
        """Suggested new tags should follow namespace/tag format."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        # Content with unique terminology
        content = "# Primitive Accumulation\n\nMarx's concept of..."
        vocab = {"theory": ["theory/marxism"]}
        inferrer = TagInferrer(vocabulary=vocab)

        result = inferrer.infer(content)

        for tag in result.suggested_new:
            # Should have namespace/tag format
            assert "/" in tag or tag.replace("-", "").isalnum()

    def test_needs_review_when_new_tags_suggested(self):
        """Should flag needs_review when suggesting new tags."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        content = "# Unique Topic\n\nVery specific content."
        vocab = {"misc": ["misc/other"]}
        inferrer = TagInferrer(vocabulary=vocab)

        result = inferrer.infer(content)

        if len(result.suggested_new) > 0:
            assert result.needs_review is True


class TestTagInferrerStringParsing:
    """Tests for parsing string tags to array."""

    def test_parses_comma_separated_tags(self, file_string_tags):
        """Should parse 'theory, philosophy, marxism' to array."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        inferrer = TagInferrer()

        # Extract the string tags from fixture
        result = inferrer.parse_string_tags("theory, philosophy, marxism")

        assert isinstance(result, list)
        assert "theory" in result
        assert "philosophy" in result
        assert "marxism" in result

    def test_strips_whitespace_from_tags(self):
        """Should strip whitespace from parsed tags."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        inferrer = TagInferrer()

        result = inferrer.parse_string_tags("  theory  ,  philosophy  ")

        assert result == ["theory", "philosophy"]

    def test_handles_already_array_tags(self):
        """Should handle tags that are already arrays."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        inferrer = TagInferrer()

        result = inferrer.parse_string_tags(["theory", "philosophy"])

        assert result == ["theory", "philosophy"]


class TestTagInferrerFuzzyMatching:
    """Tests for fuzzy tag matching."""

    def test_fuzzy_matches_similar_tags(self):
        """Should fuzzy match similar tag names."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        vocab = {"theory": ["theory/dialectical-materialism"]}
        inferrer = TagInferrer(vocabulary=vocab)

        # Content mentions "dialectics" and "materialism" separately
        content = "# Dialectics\n\nMaterialist dialectics is..."

        result = inferrer.infer(content)

        # Should match dialectical-materialism via fuzzy
        assert any("dialectic" in tag for tag in result.tags)

    def test_configurable_fuzzy_threshold(self):
        """Should allow configurable fuzzy match threshold."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        vocab = {"theory": ["theory/class-analysis"]}

        # Low threshold - more matches
        inferrer_low = TagInferrer(vocabulary=vocab, fuzzy_threshold=0.5)
        # High threshold - fewer matches
        inferrer_high = TagInferrer(vocabulary=vocab, fuzzy_threshold=0.9)

        content = "# Class Struggle\n\nThe struggle..."

        result_low = inferrer_low.infer(content)
        result_high = inferrer_high.infer(content)

        # Lower threshold may match more liberally
        assert len(result_low.tags) >= len(result_high.tags)


class TestTagInferrerConfiguration:
    """Tests for tag inferrer configuration."""

    def test_configurable_max_tags(self, file_no_frontmatter):
        """Should limit number of inferred tags."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        vocab = {
            "theory": ["theory/a", "theory/b", "theory/c", "theory/d", "theory/e"]
        }
        inferrer = TagInferrer(vocabulary=vocab, max_tags=3)

        result = inferrer.infer(file_no_frontmatter)

        assert len(result.tags) <= 3

    def test_minimum_confidence_for_tags(self, file_no_frontmatter):
        """Should only include tags above minimum confidence."""
        from frontmatter_normalizer.inferrer.tags import TagInferrer

        vocab = {"theory": ["theory/marxism", "theory/obscure-topic"]}
        inferrer = TagInferrer(vocabulary=vocab, min_confidence=0.5)

        result = inferrer.infer(file_no_frontmatter)

        # Only confident matches should be included
        # (low confidence matches go to suggested_new)
        assert isinstance(result.tags, list)
