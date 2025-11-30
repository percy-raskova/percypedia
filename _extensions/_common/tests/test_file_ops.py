"""Tests for file operation utilities."""

import json
from pathlib import Path

import pytest

from _common.file_ops import (
    compute_docname,
    read_markdown_file,
    write_json_file,
    write_text_file,
)


class TestComputeDocname:
    """Tests for compute_docname function."""

    def test_simple_file(self):
        """Simple file in root returns basename without extension."""
        result = compute_docname(
            Path('/docs/src/index.md'),
            Path('/docs/src')
        )
        assert result == 'index'

    def test_nested_file(self):
        """Nested file returns relative path without extension."""
        result = compute_docname(
            Path('/docs/src/theory/marxism.md'),
            Path('/docs/src')
        )
        assert result == 'theory/marxism'

    def test_deeply_nested(self):
        """Deeply nested file works correctly."""
        result = compute_docname(
            Path('/docs/src/a/b/c/deep.md'),
            Path('/docs/src')
        )
        assert result == 'a/b/c/deep'

    def test_rst_extension(self):
        """Works with .rst extension too."""
        result = compute_docname(
            Path('/docs/src/guide.rst'),
            Path('/docs/src')
        )
        assert result == 'guide'


class TestReadMarkdownFile:
    """Tests for read_markdown_file function."""

    def test_reads_utf8_content(self, tmp_path):
        """Reads UTF-8 content correctly."""
        test_file = tmp_path / 'test.md'
        test_file.write_text('# Hello\n\nWorld', encoding='utf-8')

        content = read_markdown_file(test_file)

        assert content == '# Hello\n\nWorld'

    def test_reads_unicode_characters(self, tmp_path):
        """Reads unicode characters correctly."""
        test_file = tmp_path / 'unicode.md'
        test_file.write_text('# Teoría del Valor\n\n日本語', encoding='utf-8')

        content = read_markdown_file(test_file)

        assert 'Teoría' in content
        assert '日本語' in content

    def test_raises_on_missing_file(self, tmp_path):
        """Raises FileNotFoundError for missing file."""
        missing = tmp_path / 'missing.md'

        with pytest.raises(FileNotFoundError):
            read_markdown_file(missing)


class TestWriteJsonFile:
    """Tests for write_json_file function."""

    def test_writes_json_content(self, tmp_path):
        """Writes valid JSON content."""
        output = tmp_path / 'output.json'
        data = {'key': 'value', 'number': 42}

        write_json_file(output, data)

        content = output.read_text(encoding='utf-8')
        parsed = json.loads(content)
        assert parsed == data

    def test_creates_parent_directories(self, tmp_path):
        """Creates missing parent directories."""
        output = tmp_path / 'nested' / 'deep' / 'file.json'

        write_json_file(output, {'test': True})

        assert output.exists()
        assert output.parent.exists()

    def test_uses_2_space_indent(self, tmp_path):
        """Uses 2-space indentation for readability."""
        output = tmp_path / 'formatted.json'

        write_json_file(output, {'key': 'value'})

        content = output.read_text()
        # JSON with 2-space indent has specific formatting
        assert '  "key"' in content

    def test_overwrites_existing_file(self, tmp_path):
        """Overwrites existing file."""
        output = tmp_path / 'test.json'
        output.write_text('old content')

        write_json_file(output, {'new': 'data'})

        content = json.loads(output.read_text())
        assert content == {'new': 'data'}


class TestWriteTextFile:
    """Tests for write_text_file function."""

    def test_writes_text_content(self, tmp_path):
        """Writes text content correctly."""
        output = tmp_path / 'output.md'

        write_text_file(output, '# Title\n\nContent')

        assert output.read_text(encoding='utf-8') == '# Title\n\nContent'

    def test_creates_parent_directories(self, tmp_path):
        """Creates missing parent directories."""
        output = tmp_path / 'a' / 'b' / 'c' / 'file.txt'

        write_text_file(output, 'content')

        assert output.exists()
        assert (tmp_path / 'a' / 'b' / 'c').is_dir()

    def test_writes_unicode_content(self, tmp_path):
        """Writes unicode content correctly."""
        output = tmp_path / 'unicode.txt'

        write_text_file(output, '日本語 and émojis: 🎉')

        content = output.read_text(encoding='utf-8')
        assert '日本語' in content
        assert '🎉' in content

    def test_overwrites_existing_file(self, tmp_path):
        """Overwrites existing file."""
        output = tmp_path / 'test.txt'
        output.write_text('old')

        write_text_file(output, 'new')

        assert output.read_text() == 'new'
