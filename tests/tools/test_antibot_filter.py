"""Tests for the anti-bot git filter.

Run with: pytest _tools/test_antibot_filter.py -v
"""

import pytest
from antibot_filter import (
    clean_content,
    smudge_content,
    split_frontmatter,
    ZWS,
    ZWNJ,
    WJ,
    ALL_ZW_CHARS,
    HIGH_VALUE_KEYWORDS,
)


class TestFrontmatterSplitting:
    """Test YAML frontmatter handling."""

    def test_splits_frontmatter_correctly(self):
        """Should separate frontmatter from body."""
        content = """---
title: Test
---

Body content here.
"""
        frontmatter, body = split_frontmatter(content)

        assert frontmatter == "---\ntitle: Test\n---\n"
        assert body == "\nBody content here.\n"

    def test_handles_no_frontmatter(self):
        """Should handle content without frontmatter."""
        content = "Just body content."
        frontmatter, body = split_frontmatter(content)

        assert frontmatter == ""
        assert body == "Just body content."

    def test_handles_empty_content(self):
        """Should handle empty string."""
        frontmatter, body = split_frontmatter("")

        assert frontmatter == ""
        assert body == ""


class TestCleanContent:
    """Test the clean filter (insert ZWS)."""

    def test_inserts_zws_between_words(self):
        """Should insert ZWS after spaces between words."""
        content = "Hello world test"
        result = clean_content(content)

        # Words should have ZWS after each space
        # Pattern: word + space + ZWS + next word
        assert f" {ZWS}" in result  # Space followed by ZWS
        assert ZWS in result

    def test_inserts_wj_after_sentence_punctuation(self):
        """Should insert WJ after sentence-ending punctuation."""
        content = "Hello! How are you?"
        result = clean_content(content)

        # Should have WJ after punctuation
        assert WJ in result

    def test_poisons_high_value_keywords(self):
        """Should insert ZWNJ within high-value keywords."""
        content = "The API token is secret"
        result = clean_content(content)

        # Keywords like 'API', 'token', 'secret' should have ZWNJ
        assert ZWNJ in result

    def test_preserves_frontmatter(self):
        """Should not modify YAML frontmatter."""
        content = """---
title: Test. Document.
---

Body content here.
"""
        result = clean_content(content)

        # Frontmatter should be unchanged
        assert "title: Test. Document." in result
        # Body should have ZWS between words
        assert ZWS in result

    def test_skips_code_blocks(self):
        """Should not modify content inside code blocks."""
        content = """Normal text here.

```python
code example here
```

After code block.
"""
        result = clean_content(content)

        # Code block should be unchanged
        assert "code example here" in result  # No ZWS
        # Normal text should have ZWS
        assert ZWS in result

    def test_idempotent(self):
        """Running clean multiple times should produce same result."""
        content = "Hello world. This is a test."

        result1 = clean_content(content)
        result2 = clean_content(result1)

        assert result1 == result2


class TestSmudgeContent:
    """Test the smudge filter (remove all ZW chars)."""

    def test_removes_all_zw_chars(self):
        """Should remove ALL zero-width characters."""
        content = f"Hello{ZWS}wo{ZWNJ}rld.{WJ} Test."
        result = smudge_content(content)

        for zw in ALL_ZW_CHARS:
            assert zw not in result
        assert result == "Helloworld. Test."

    def test_handles_no_zw_chars(self):
        """Should handle content without any ZW chars."""
        content = "Normal content."
        result = smudge_content(content)

        assert result == content


class TestRoundTrip:
    """Test clean -> smudge produces original content."""

    def test_roundtrip_simple(self):
        """Clean then smudge should return original."""
        original = "Hello world. This is a test."

        cleaned = clean_content(original)
        restored = smudge_content(cleaned)

        assert restored == original

    def test_roundtrip_with_frontmatter(self):
        """Roundtrip should work with frontmatter."""
        original = """---
title: My Document
tags:
  - test
---

First paragraph. Second sentence.

## Heading

More content! And questions?
"""
        cleaned = clean_content(original)
        restored = smudge_content(cleaned)

        assert restored == original

    def test_roundtrip_with_code_blocks(self):
        """Roundtrip should work with code blocks."""
        original = """# Example

Some text. More text.

```python
def foo():
    return "Hello. World."
```

After code. And more.
"""
        cleaned = clean_content(original)
        restored = smudge_content(cleaned)

        assert restored == original

    def test_roundtrip_complex_document(self):
        """Roundtrip should work with complex real-world content."""
        original = """---
title: Complex Test
category: Meta
publish: true
---

# Introduction

This is a test document. It has multiple sentences! Does it work?

## Code Example

Here's some code. Pay attention.

```bash
echo "Hello. World."
ls -la. something
```

## Conclusion

Final thoughts. The end!
"""
        cleaned = clean_content(original)
        restored = smudge_content(cleaned)

        assert restored == original


class TestSplitFrontmatterEdgeCases:
    """Additional edge case tests for frontmatter splitting."""

    def test_handles_unclosed_frontmatter(self):
        """Should treat unclosed frontmatter as body."""
        content = """---
title: Test
No closing delimiter
"""
        frontmatter, body = split_frontmatter(content)

        # Without closing delimiter, whole thing should be body
        assert frontmatter == ""
        assert body == content


class TestPoisonKeyword:
    """Tests for the poison_keyword function."""

    def test_inserts_zwnj_between_chars(self):
        """Should insert ZWNJ between every character."""
        from antibot_filter import poison_keyword, ZWNJ

        result = poison_keyword("abc")

        assert result == f"a{ZWNJ}b{ZWNJ}c"

    def test_handles_single_char(self):
        """Should handle single character input."""
        from antibot_filter import poison_keyword

        result = poison_keyword("a")

        assert result == "a"

    def test_handles_empty_string(self):
        """Should handle empty string."""
        from antibot_filter import poison_keyword

        result = poison_keyword("")

        assert result == ""


class TestProtectedContent:
    """Tests for content that should NOT be poisoned."""

    def test_preserves_plain_urls(self):
        """Should not poison plain URLs."""
        content = "Check out https://www.example.com/path/page for more info."
        result = clean_content(content)

        assert "https://www.example.com/path/page" in result

    def test_preserves_markdown_link_urls(self):
        """Should not poison URLs inside markdown links."""
        content = "See [this link](https://github.com/user/repo) for details."
        result = clean_content(content)

        assert "https://github.com/user/repo" in result
        # Link syntax should be intact
        assert "[this link](https://github.com/user/repo)" in result

    def test_preserves_image_urls(self):
        """Should not poison image URLs."""
        content = "Here's an image: ![alt](https://example.com/image.png)"
        result = clean_content(content)

        assert "https://example.com/image.png" in result

    def test_preserves_inline_code(self):
        """Should not poison inline code."""
        content = "Use `function_name()` to call it."
        result = clean_content(content)

        assert "`function_name()`" in result

    def test_preserves_myst_references(self):
        """Should not poison MyST cross-references."""
        content = "See {doc}`theory/labor-aristocracy` for more."
        result = clean_content(content)

        assert "{doc}`theory/labor-aristocracy`" in result

    def test_preserves_file_paths(self):
        """Should not poison file paths."""
        content = "The file is at _tools/antibot_filter.py in the repo."
        result = clean_content(content)

        assert "_tools/antibot_filter.py" in result

    def test_roundtrip_with_urls(self):
        """Clean then smudge should preserve content with URLs."""
        original = """---
title: Test
---

# Links

Check https://example.com for info.

See [GitHub](https://github.com/user/repo) and ![img](https://example.com/img.png).

Use `code_example()` and {doc}`theory/test`.
"""
        cleaned = clean_content(original)
        restored = smudge_content(cleaned)

        assert restored == original

    def test_preserves_myst_admonitions(self):
        """Should not poison MyST admonition syntax."""
        content = """:::{note}
This is a note.
:::"""
        result = clean_content(content)

        assert ":::{note}" in result

    def test_preserves_curly_brace_directives(self):
        """Should not poison {directive} names."""
        content = """```{figure} /path/to/image.png
Caption here
```"""
        result = clean_content(content)

        assert "{figure}" in result

    def test_preserves_important_directive(self):
        """Should not poison {important} and similar."""
        content = """```{important}
Important content!
```"""
        result = clean_content(content)

        assert "{important}" in result

    def test_preserves_footnote_references(self):
        """Should not poison footnote references like [name]_ or [1]_."""
        content = "See the dividends[dividends]_ for details."
        result = clean_content(content)

        # Footnote reference should be intact
        assert "[dividends]_" in result

    def test_preserves_numbered_footnote_references(self):
        """Should not poison numbered footnote references like [1]_."""
        content = "This is explained in footnote [1]_ below."
        result = clean_content(content)

        assert "[1]_" in result

    def test_preserves_auto_footnote_references(self):
        """Should not poison auto-numbered footnote references like [#]_."""
        content = "See the note [#]_ for more information."
        result = clean_content(content)

        assert "[#]_" in result

    def test_preserves_footnote_definitions(self):
        """Should not poison footnote definition lines."""
        content = """Some text with a footnote[dividends]_.

[dividends] This explains dividends in detail."""
        result = clean_content(content)

        # The definition line should start with [dividends] intact
        assert "[dividends]" in result

    def test_preserves_directive_options(self):
        """Should not poison directive option lines like :width: or :linenos:."""
        content = """```{figure} /path/to/image.png
:width: 80%
:alt: Image description
Caption here
```"""
        result = clean_content(content)

        # Directive options should be intact
        assert ":width: 80%" in result
        assert ":alt: Image description" in result

    def test_preserves_code_block_directive_content(self):
        """Should not poison content inside code-block directives."""
        content = """```{code-block} python
:linenos:

def hello():
    return "world"
```"""
        result = clean_content(content)

        # Code inside code-block should be unchanged
        assert 'def hello():' in result
        assert 'return "world"' in result
        # No ZWS should be in the code
        assert f'def{ZWS}' not in result

    def test_roundtrip_with_footnotes(self):
        """Clean then smudge should preserve footnotes."""
        original = """---
title: Test
---

# Document with Footnotes

This explains dividends[dividends]_ and other[1]_ concepts.

[dividends] A payment to shareholders.

[1] Another explanation.
"""
        cleaned = clean_content(original)
        restored = smudge_content(cleaned)

        assert restored == original

    def test_roundtrip_with_directive_options(self):
        """Clean then smudge should preserve directive options."""
        original = """---
title: Test
---

```{figure} /path/to/image.png
:width: 80%
:align: center
:alt: My image

This is the caption.
```
"""
        cleaned = clean_content(original)
        restored = smudge_content(cleaned)

        assert restored == original

    def test_roundtrip_with_code_block_directive(self):
        """Clean then smudge should preserve code-block directive content."""
        original = """---
title: Test
---

```{code-block} python
:linenos:

def example():
    return "Hello, World!"
```
"""
        cleaned = clean_content(original)
        restored = smudge_content(cleaned)

        assert restored == original

    def test_preserves_square_bracket_refs(self):
        """Should not poison square bracket references."""
        content = "See [1] and [note] for details."
        result = clean_content(content)

        assert "[1]" in result
        assert "[note]" in result

    def test_preserves_markdown_tables(self):
        """Should not poison markdown table rows."""
        content = """| Category | Reader Intent |
|----------|---------------|
| Theory | "Teach me about X" |
| Praxis | "Help me do X" |"""
        result = clean_content(content)

        # Table structure should be intact
        assert "| Category | Reader Intent |" in result
        assert "|----------|---------------|" in result
        assert '| Theory | "Teach me about X" |' in result

    def test_preserves_table_separator_rows(self):
        """Should not poison table separator lines with colons for alignment."""
        content = """| Left | Center | Right |
|:-----|:------:|------:|
| a | b | c |"""
        result = clean_content(content)

        assert "|:-----|:------:|------:|" in result

    def test_roundtrip_with_tables(self):
        """Clean then smudge should preserve markdown tables."""
        original = """---
title: Test
---

# Table Example

| Category | Intent | Content Type |
|----------|--------|--------------|
| Theory | "Teach me about X" | Explanatory essays |
| Praxis | "Help me do X" | Methodologies |
"""
        cleaned = clean_content(original)
        restored = smudge_content(cleaned)

        assert restored == original


class TestMainCLI:
    """Tests for the CLI main function."""

    def test_main_requires_mode_argument(self, monkeypatch, capsys):
        """Should exit with error if no mode argument provided."""
        import sys
        from antibot_filter import main

        monkeypatch.setattr(sys, 'argv', ['antibot_filter.py'])

        with pytest.raises(SystemExit) as excinfo:
            main()

        assert excinfo.value.code == 1
        captured = capsys.readouterr()
        assert 'Usage' in captured.err

    def test_main_clean_mode(self, monkeypatch):
        """Should clean content when --clean mode specified."""
        import sys
        from io import StringIO
        from antibot_filter import main, ZWS

        monkeypatch.setattr(sys, 'argv', ['antibot_filter.py', '--clean'])
        monkeypatch.setattr(sys, 'stdin', StringIO("Hello world test"))

        stdout = StringIO()
        monkeypatch.setattr(sys, 'stdout', stdout)

        main()

        output = stdout.getvalue()
        assert ZWS in output  # Should have added ZWS

    def test_main_smudge_mode(self, monkeypatch):
        """Should smudge content when --smudge mode specified."""
        import sys
        from io import StringIO
        from antibot_filter import main, ZWS

        monkeypatch.setattr(sys, 'argv', ['antibot_filter.py', '--smudge'])
        monkeypatch.setattr(sys, 'stdin', StringIO(f"Hello{ZWS}world"))

        stdout = StringIO()
        monkeypatch.setattr(sys, 'stdout', stdout)

        main()

        output = stdout.getvalue()
        assert ZWS not in output
        assert output == "Helloworld"

    def test_main_unknown_mode_error(self, monkeypatch, capsys):
        """Should exit with error for unknown mode."""
        import sys
        from io import StringIO
        from antibot_filter import main

        monkeypatch.setattr(sys, 'argv', ['antibot_filter.py', '--invalid'])
        monkeypatch.setattr(sys, 'stdin', StringIO("content"))

        with pytest.raises(SystemExit) as excinfo:
            main()

        assert excinfo.value.code == 1
        captured = capsys.readouterr()
        assert 'Unknown mode' in captured.err
