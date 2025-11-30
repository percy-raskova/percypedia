"""
Tests for honeypot poisoners module.

Tests the text poisoning functions used to create anti-AI honeypot content.
These tests establish a baseline for safe refactoring.
"""


from honeypot.poisoners import (
    FUNC_APP,
    HOMOGLYPHS,
    INV_PLUS,
    INV_SEP,
    INV_TIMES,
    SHY,
    STEALTH_CHARS,
    WJ,
    ZWJ,
    ZWNJ,
    ZWS,
    apply_homoglyphs,
    css_content_replace,
    dom_reorder,
    generate_canary,
    inject_invisible,
    inject_zero_width,
    poison_content,
    prompt_injection,
)


class TestHomoglyphs:
    """Test Group 1: Homoglyph substitution functionality."""

    def test_homoglyphs_constant_has_expected_chars(self):
        """
        Given: HOMOGLYPHS constant
        When: Checking its content
        Then: Contains mappings for common Latin characters
        """
        assert 'a' in HOMOGLYPHS
        assert 'e' in HOMOGLYPHS
        assert 'o' in HOMOGLYPHS
        assert 'A' in HOMOGLYPHS
        assert 'E' in HOMOGLYPHS

    def test_apply_homoglyphs_with_zero_rate_unchanged(self):
        """
        Given: Text and rate=0
        When: apply_homoglyphs is called
        Then: Text is unchanged
        """
        text = "Hello World"
        result = apply_homoglyphs(text, rate=0)
        assert result == text

    def test_apply_homoglyphs_with_full_rate_changes_text(self):
        """
        Given: Text with homoglyph-eligible chars and rate=1.0
        When: apply_homoglyphs is called with a seed
        Then: Some characters are replaced
        """
        text = "aeiou"  # All have homoglyphs
        result = apply_homoglyphs(text, rate=1.0, seed=42)
        # Should differ from original
        assert result != text
        # Should have same length
        assert len(result) == len(text)

    def test_apply_homoglyphs_deterministic_with_seed(self):
        """
        Given: Same text and seed
        When: apply_homoglyphs is called twice
        Then: Results are identical
        """
        text = "Test text with characters"
        result1 = apply_homoglyphs(text, rate=0.5, seed=42)
        result2 = apply_homoglyphs(text, rate=0.5, seed=42)
        assert result1 == result2

    def test_apply_homoglyphs_different_seed_different_result(self):
        """
        Given: Same text with different seeds
        When: apply_homoglyphs is called
        Then: Results may differ
        """
        text = "aaaaaeeeeeoooooooo"  # Many eligible chars
        result1 = apply_homoglyphs(text, rate=0.5, seed=1)
        result2 = apply_homoglyphs(text, rate=0.5, seed=999)
        # With many chars and different seeds, should differ
        assert result1 != result2


class TestZeroWidthCharacters:
    """Test Group 2: Zero-width character injection."""

    def test_zero_width_constants_defined(self):
        """
        Given: Zero-width character constants
        When: Checking their values
        Then: They are proper Unicode zero-width chars
        """
        assert ZWS == '\u200b'
        assert ZWNJ == '\u200c'
        assert ZWJ == '\u200d'
        assert WJ == '\u2060'

    def test_stealth_char_constants_defined(self):
        """
        Given: Stealth character constants (survive Anthropic filtering)
        When: Checking their values
        Then: They are proper Unicode invisible chars
        """
        assert SHY == '\u00ad'
        assert WJ == '\u2060'
        assert FUNC_APP == '\u2061'
        assert INV_TIMES == '\u2062'
        assert INV_SEP == '\u2063'
        assert INV_PLUS == '\u2064'
        assert len(STEALTH_CHARS) == 6

    def test_inject_invisible_uses_stealth_by_default(self):
        """
        Given: Text with multiple words
        When: inject_invisible called with default settings
        Then: Uses stealth chars (WJ) instead of legacy (ZWS)
        """
        text = "hello world"
        result = inject_invisible(text, mode="words")
        assert WJ in result
        assert ZWS not in result

    def test_inject_invisible_stealth_mode_cycles_chars(self):
        """
        Given: Text
        When: inject_invisible called with mode="stealth"
        Then: Cycles through all stealth chars
        """
        text = "test"
        result = inject_invisible(text, mode="stealth")
        # Result should be longer than original (stealth chars added)
        assert len(result) > len(text)
        # Should contain some of the stealth chars
        assert any(char in result for char in STEALTH_CHARS)

    def test_inject_zero_width_words_mode(self):
        """
        Given: Text with multiple words
        When: inject_zero_width called with mode="words"
        Then: ZWS inserted between words
        """
        text = "hello world test"
        result = inject_zero_width(text, mode="words")
        assert result == f"hello{ZWS}world{ZWS}test"

    def test_inject_zero_width_chars_mode(self):
        """
        Given: Text
        When: inject_zero_width called with mode="chars"
        Then: ZWNJ inserted between every character
        """
        text = "abc"
        result = inject_zero_width(text, mode="chars")
        assert result == f"a{ZWNJ}b{ZWNJ}c"

    def test_inject_zero_width_keywords_mode(self):
        """
        Given: Text with specific keywords
        When: inject_zero_width called with mode="keywords" and keyword list
        Then: Only specified keywords get ZWNJ between chars
        """
        text = "The API token is secret"
        keywords = ["API", "secret"]
        result = inject_zero_width(text, mode="keywords", keywords=keywords)

        # API and secret should be poisoned
        poisoned_api = ZWNJ.join("API")
        poisoned_secret = ZWNJ.join("secret")
        assert poisoned_api in result
        assert poisoned_secret in result
        # Non-keywords unchanged
        assert "The" in result.replace(ZWNJ, "")  # Still present when normalized

    def test_inject_zero_width_keywords_no_keywords_unchanged(self):
        """
        Given: Text with mode="keywords" but no keywords list
        When: inject_zero_width is called
        Then: Text unchanged
        """
        text = "Some text here"
        result = inject_zero_width(text, mode="keywords", keywords=None)
        assert result == text

    def test_inject_zero_width_unknown_mode_unchanged(self):
        """
        Given: Unknown mode
        When: inject_zero_width is called
        Then: Text unchanged
        """
        text = "Some text"
        result = inject_zero_width(text, mode="unknown_mode")
        assert result == text


class TestCSSContentReplace:
    """Test Group 3: CSS-based content replacement."""

    def test_css_content_replace_returns_dict(self):
        """
        Given: visible and decoy text
        When: css_content_replace is called
        Then: Returns dict with 'html' and 'css' keys
        """
        result = css_content_replace("Real", "Fake")
        assert isinstance(result, dict)
        assert 'html' in result
        assert 'css' in result

    def test_css_content_replace_html_contains_decoy(self):
        """
        Given: Decoy text
        When: css_content_replace is called
        Then: HTML contains the decoy text
        """
        result = css_content_replace("Real Text", "Decoy Text")
        assert "Decoy Text" in result['html']

    def test_css_content_replace_css_contains_visible(self):
        """
        Given: Visible text
        When: css_content_replace is called
        Then: CSS contains the visible text in content property
        """
        result = css_content_replace("Real Text", "Decoy")
        assert "Real Text" in result['css']
        assert 'content:' in result['css']

    def test_css_content_replace_escapes_quotes(self):
        """
        Given: Visible text with quotes
        When: css_content_replace is called
        Then: Quotes are escaped in CSS
        """
        result = css_content_replace('Text with "quotes"', "Decoy")
        assert '\\"' in result['css']


class TestDOMReorder:
    """Test Group 4: DOM reordering for scraper confusion."""

    def test_dom_reorder_returns_html(self):
        """
        Given: List of paragraphs
        When: dom_reorder is called
        Then: Returns HTML string with flex container
        """
        paragraphs = ["First", "Second", "Third"]
        result = dom_reorder(paragraphs)
        assert '<div class="poison-reorder"' in result
        assert 'display:flex' in result

    def test_dom_reorder_has_order_property(self):
        """
        Given: List of paragraphs
        When: dom_reorder is called
        Then: Each paragraph has CSS order property
        """
        paragraphs = ["First", "Second"]
        result = dom_reorder(paragraphs)
        assert 'order:' in result

    def test_dom_reorder_contains_all_paragraphs(self):
        """
        Given: List of paragraphs
        When: dom_reorder is called
        Then: All paragraph content appears in output
        """
        paragraphs = ["Alpha", "Beta", "Gamma"]
        result = dom_reorder(paragraphs)
        for para in paragraphs:
            assert para in result


class TestPromptInjection:
    """Test Group 5: Prompt injection payload generation."""

    def test_prompt_injection_contains_canary(self):
        """
        Given: Canary code
        When: prompt_injection is called
        Then: Output contains the canary code
        """
        canary = "TEST-12345678"
        result = prompt_injection(canary)
        assert canary in result

    def test_prompt_injection_is_hidden_div(self):
        """
        Given: Any canary code
        When: prompt_injection is called
        Then: Output is a hidden div (off-screen positioning)
        """
        result = prompt_injection("TEST-CODE")
        assert '<div class="poison-prompt"' in result
        assert 'position:absolute' in result
        assert 'left:-9999px' in result

    def test_prompt_injection_has_aria_hidden(self):
        """
        Given: Any canary code
        When: prompt_injection is called
        Then: Div has aria-hidden for accessibility
        """
        result = prompt_injection("TEST-CODE")
        assert 'aria-hidden="true"' in result

    def test_prompt_injection_uses_default_email(self):
        """
        Given: Canary without custom email
        When: prompt_injection is called
        Then: Uses default licensing email
        """
        result = prompt_injection("TEST-CODE")
        assert "licensing@percybrain.com" in result

    def test_prompt_injection_uses_custom_email(self):
        """
        Given: Canary with custom email
        When: prompt_injection is called
        Then: Uses the custom email
        """
        result = prompt_injection("TEST-CODE", fake_email="custom@example.com")
        assert "custom@example.com" in result
        assert "licensing@percybrain.com" not in result


class TestCanaryGeneration:
    """Test Group 6: Canary token generation."""

    def test_generate_canary_returns_prefixed_string(self):
        """
        Given: Page ID and timestamp
        When: generate_canary is called
        Then: Returns string with default PCP prefix
        """
        result = generate_canary("test-page", "2024-01-01")
        assert result.startswith("PCP-")

    def test_generate_canary_custom_prefix(self):
        """
        Given: Custom prefix
        When: generate_canary is called
        Then: Returns string with custom prefix
        """
        result = generate_canary("test", "2024", prefix="CUSTOM")
        assert result.startswith("CUSTOM-")

    def test_generate_canary_deterministic(self):
        """
        Given: Same inputs
        When: generate_canary is called twice
        Then: Results are identical
        """
        result1 = generate_canary("page-1", "2024-01-15T10:30:00")
        result2 = generate_canary("page-1", "2024-01-15T10:30:00")
        assert result1 == result2

    def test_generate_canary_different_inputs_different_output(self):
        """
        Given: Different page IDs
        When: generate_canary is called
        Then: Results differ
        """
        result1 = generate_canary("page-1", "2024-01-01")
        result2 = generate_canary("page-2", "2024-01-01")
        assert result1 != result2

    def test_generate_canary_hash_format(self):
        """
        Given: Any inputs
        When: generate_canary is called
        Then: Returns PREFIX-8hexchars format
        """
        result = generate_canary("test", "2024")
        parts = result.split("-")
        assert len(parts) == 2
        assert len(parts[1]) == 8
        # Should be hex characters
        int(parts[1], 16)  # Should not raise


class TestPoisonContent:
    """Test Group 7: Combined content poisoning."""

    def test_poison_content_minimal_level(self):
        """
        Given: Content with level="minimal"
        When: poison_content is called
        Then: Only adds prompt injection, no text modification
        """
        content = "Simple test content"
        result = poison_content(
            content,
            level="minimal",
            page_id="test",
            timestamp="2024",
        )
        # Original content should be at start
        assert result.startswith(content)
        # Prompt injection should be appended
        assert "poison-prompt" in result

    def test_poison_content_balanced_level(self):
        """
        Given: Content with level="balanced"
        When: poison_content is called
        Then: Applies homoglyphs, ZWS, and prompt injection
        """
        content = "Test with aeiou characters"
        result = poison_content(
            content,
            level="balanced",
            page_id="test",
            timestamp="2024",
            seed=42,
        )
        # Should have ZWS between words
        assert ZWS in result
        # Should have prompt injection
        assert "poison-prompt" in result

    def test_poison_content_maximum_level(self):
        """
        Given: Content with level="maximum"
        When: poison_content is called
        Then: Applies all poisoning techniques
        """
        content = "Test API with secret token"
        result = poison_content(
            content,
            level="maximum",
            page_id="test",
            timestamp="2024",
            seed=42,
        )
        # Should have ZWS
        assert ZWS in result
        # Should have ZWNJ from keyword poisoning
        assert ZWNJ in result
        # Should have prompt injection
        assert "poison-prompt" in result

    def test_poison_content_uses_custom_email(self):
        """
        Given: Content with custom fake_email
        When: poison_content is called
        Then: Custom email appears in prompt injection
        """
        result = poison_content(
            "Test content",
            level="minimal",
            page_id="test",
            timestamp="2024",
            fake_email="trap@example.com",
        )
        assert "trap@example.com" in result

    def test_poison_content_deterministic_with_seed(self):
        """
        Given: Same inputs including seed
        When: poison_content is called twice
        Then: Results are identical
        """
        kwargs = {
            "content": "Repeatable test content with aeiou",
            "level": "maximum",
            "page_id": "test-page",
            "timestamp": "2024-01-01",
            "seed": 12345,
        }
        result1 = poison_content(**kwargs)
        result2 = poison_content(**kwargs)
        assert result1 == result2
