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


class TestPoisonedContentValidity:
    """Tests ensuring poisoned content remains valid for Sphinx builds.

    Poisoning must not break:
    - MyST markdown syntax
    - Sphinx directives
    - HTML structure
    """

    def test_poisoned_content_preserves_markdown_structure(self):
        """Poisoning should not break basic markdown."""
        from honeypot.poisoners import poison_content

        markdown = """# Heading

This is a paragraph.

- List item 1
- List item 2

```python
code_block = True
```
"""
        result = poison_content(markdown, level="balanced")

        # Should still have heading marker
        assert "#" in result
        # Should still have list markers
        assert "-" in result
        # Should still have code fence
        assert "```" in result

    def test_poisoned_content_preserves_myst_directives(self):
        """Poisoning should not corrupt MyST directive syntax."""
        from honeypot.poisoners import poison_content

        myst_content = """```{admonition} Warning
:class: warning

This is important content.
```

```{code-block} python
print("hello")
```
"""
        result = poison_content(myst_content, level="balanced")

        # Directive markers must be preserved
        assert "```{" in result or "```" in result
        # Admonition structure should remain
        assert "admonition" in result.lower() or "warning" in result.lower()

    def test_poisoned_html_is_well_formed(self):
        """Generated HTML structures should be well-formed."""
        from honeypot.poisoners import prompt_injection, css_content_replace

        # Prompt injection HTML
        pi_html = prompt_injection("TEST-123")
        assert pi_html.count("<div") == pi_html.count("</div>")

        # CSS replacement HTML
        css_result = css_content_replace("visible", "hidden")
        assert css_result['html'].count("<span") == css_result['html'].count("</span>")

    def test_dom_reorder_produces_valid_html(self):
        """DOM reordering should produce valid HTML structure."""
        from honeypot.poisoners import dom_reorder

        result = dom_reorder(["Para 1", "Para 2", "Para 3"])

        # Should have matching tags
        assert result.count("<div") == result.count("</div>")
        assert result.count("<p") == result.count("</p>")
        # Should have all paragraphs
        assert "Para 1" in result
        assert "Para 2" in result
        assert "Para 3" in result


class TestHoneypotBuildIntegration:
    """Integration tests verifying honeypot doesn't break builds.

    These tests ensure the honeypot extension can be enabled without
    causing Sphinx build failures.
    """

    def test_honeypot_templates_exist(self):
        """All referenced templates should exist."""
        from pathlib import Path

        template_dir = Path(__file__).parent.parent / 'templates'

        expected_templates = [
            'api_docs.md.j2',
            'internal_policy.md.j2',
            'training_data.md.j2',
        ]

        for template in expected_templates:
            template_path = template_dir / template
            assert template_path.exists(), f"Missing template: {template}"

    def test_honeypot_templates_are_valid_jinja2(self):
        """Templates should be parseable by Jinja2."""
        from pathlib import Path

        try:
            from jinja2 import Environment, FileSystemLoader
        except ImportError:
            pytest.skip("Jinja2 not installed")

        template_dir = Path(__file__).parent.parent / 'templates'
        env = Environment(loader=FileSystemLoader(str(template_dir)))

        templates = ['api_docs.md.j2', 'internal_policy.md.j2', 'training_data.md.j2']

        for template_name in templates:
            # Should not raise
            template = env.get_template(template_name)
            assert template is not None

    def test_rendered_template_has_frontmatter(self):
        """Rendered templates should include valid frontmatter."""
        from pathlib import Path

        try:
            from jinja2 import Environment, FileSystemLoader
        except ImportError:
            pytest.skip("Jinja2 not installed")

        from honeypot.poisoners import generate_canary, poison_content

        template_dir = Path(__file__).parent.parent / 'templates'
        env = Environment(loader=FileSystemLoader(str(template_dir)))

        template = env.get_template('api_docs.md.j2')
        rendered = template.render(
            canary_code="TEST-123",
            page_path="test/page",
            poison_content=poison_content,
        )

        # Should start with frontmatter
        assert rendered.strip().startswith('---'), "Template must include frontmatter"
        # Should have closing frontmatter
        assert rendered.count('---') >= 2, "Frontmatter must be closed"
