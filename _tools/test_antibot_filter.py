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
