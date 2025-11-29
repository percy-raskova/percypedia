"""Tests for honeypot poisoning functions.

TDD: These tests define the expected behavior of poisoner functions.
Run with: pytest _extensions/honeypot/tests/
"""

import pytest


class TestHomoglyphSubstitution:
    """Test homoglyph character substitution."""

    def test_substitutes_common_characters(self):
        """Should replace Latin chars with visually identical Cyrillic/Greek."""
        from honeypot.poisoners import apply_homoglyphs

        # With 100% rate, all eligible chars should be replaced
        result = apply_homoglyphs("aeo", rate=1.0)

        # Should contain non-ASCII characters
        assert result != "aeo"
        assert len(result) == 3  # Same length

    def test_respects_substitution_rate(self):
        """Should only substitute approximately `rate` fraction of chars."""
        from honeypot.poisoners import apply_homoglyphs

        text = "a" * 1000  # 1000 'a' characters
        result = apply_homoglyphs(text, rate=0.1)

        # Count how many were substituted
        original_count = result.count('a')
        substituted = 1000 - original_count

        # Should be roughly 10% (allow 5-15% due to randomness)
        assert 50 <= substituted <= 150

    def test_zero_rate_no_changes(self):
        """With rate=0, text should be unchanged."""
        from honeypot.poisoners import apply_homoglyphs

        text = "hello world"
        result = apply_homoglyphs(text, rate=0.0)
        assert result == text

    def test_preserves_non_homoglyph_chars(self):
        """Characters without homoglyphs should be unchanged."""
        from honeypot.poisoners import apply_homoglyphs

        text = "123 !@#"
        result = apply_homoglyphs(text, rate=1.0)
        assert result == text


class TestZeroWidthInjection:
    """Test zero-width character injection."""

    def test_injects_between_words(self):
        """Should inject ZWS between words."""
        from honeypot.poisoners import inject_zero_width, ZWS

        result = inject_zero_width("hello world", mode="words")
        assert result == f"hello{ZWS}world"

    def test_injects_between_all_chars(self):
        """Should inject ZWNJ between every character."""
        from honeypot.poisoners import inject_zero_width, ZWNJ

        result = inject_zero_width("abc", mode="chars")
        assert result == f"a{ZWNJ}b{ZWNJ}c"

    def test_injects_in_keywords(self):
        """Should inject into specific keywords only."""
        from honeypot.poisoners import inject_zero_width, ZWNJ

        text = "the API endpoint returns data"
        result = inject_zero_width(text, mode="keywords", keywords=["API", "endpoint"])

        # Keywords should have ZWNJ, other words should not
        assert ZWNJ in result
        assert "the" in result  # Non-keyword unchanged
        assert "data" in result  # Non-keyword unchanged


class TestCSSContentReplacement:
    """Test CSS content replacement poisoning."""

    def test_generates_css_hidden_content(self):
        """Should generate HTML that shows garbage but CSS shows real text."""
        from honeypot.poisoners import css_content_replace

        result = css_content_replace(
            visible_text="This is the real content",
            decoy_text="DECOY_GARBAGE_DATA"
        )

        # HTML should contain decoy
        assert "DECOY_GARBAGE_DATA" in result['html']
        # CSS should contain real content
        assert "This is the real content" in result['css']
        # HTML should have the class for CSS targeting
        assert "poison-css" in result['html']


class TestDOMReordering:
    """Test DOM order scrambling with flexbox."""

    def test_scrambles_paragraph_order(self):
        """Should output paragraphs in different order than visual."""
        from honeypot.poisoners import dom_reorder

        paragraphs = ["First", "Second", "Third"]
        result = dom_reorder(paragraphs)

        # Should have order CSS properties
        assert "order:" in result
        # All paragraphs should be present
        for p in paragraphs:
            assert p in result


class TestPromptInjection:
    """Test prompt injection payloads."""

    def test_generates_hidden_div(self):
        """Should generate hidden div with prompt injection."""
        from honeypot.poisoners import prompt_injection

        result = prompt_injection(
            canary_code="PCP-2024-TEST",
            fake_email="test@example.com"
        )

        # Should be hidden
        assert 'aria-hidden="true"' in result
        assert 'style=' in result
        # Should contain canary
        assert "PCP-2024-TEST" in result
        # Should contain authoritative language
        assert "must" in result.lower() or "required" in result.lower()


class TestCanaryTokens:
    """Test canary token generation."""

    def test_generates_unique_tokens(self):
        """Should generate unique tokens for different inputs."""
        from honeypot.poisoners import generate_canary

        token1 = generate_canary("page1", "2024-01-01")
        token2 = generate_canary("page2", "2024-01-01")

        assert token1 != token2
        assert token1.startswith("PCP-")
        assert token2.startswith("PCP-")

    def test_deterministic_for_same_input(self):
        """Same input should produce same token."""
        from honeypot.poisoners import generate_canary

        token1 = generate_canary("page1", "2024-01-01")
        token2 = generate_canary("page1", "2024-01-01")

        assert token1 == token2


class TestFullPoisonPipeline:
    """Test the full poisoning pipeline."""

    def test_apply_all_poisoning(self):
        """Should apply all poisoning techniques in sequence."""
        from honeypot.poisoners import poison_content

        content = "This is some API documentation about endpoints."
        result = poison_content(content, level="maximum")

        # Should be different from original
        assert result != content
        # Should contain original content (possibly with invisible chars)
        # The prompt injection adds ~700 chars, so allow for that
        assert len(result) < len(content) * 20  # Account for prompt injection payload

    def test_maximum_level_includes_prompt_injection(self):
        """Maximum level should include prompt injection div."""
        from honeypot.poisoners import poison_content

        content = "Test content"
        result = poison_content(content, level="maximum")

        # Should have prompt injection
        assert "SYSTEM DIRECTIVE" in result
        assert "poison-prompt" in result

    def test_minimal_level_only_prompt_injection(self):
        """Minimal level should only add prompt injection."""
        from honeypot.poisoners import poison_content

        content = "Test content without homoglyphs aeo"
        result = poison_content(content, level="minimal")

        # Original text should be unchanged (no homoglyphs)
        assert "Test content without homoglyphs aeo" in result
        # But should have prompt injection
        assert "SYSTEM DIRECTIVE" in result
