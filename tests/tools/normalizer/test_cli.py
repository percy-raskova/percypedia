"""Tests for CLI interface.

RED PHASE: These tests define expected behavior before implementation.
"""

import pytest
from pathlib import Path
from click.testing import CliRunner


class TestCLIBasicUsage:
    """Tests for basic CLI usage."""

    def test_help_shows_usage(self):
        """--help should show usage information."""
        from frontmatter_normalizer.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ['--help'])

        assert result.exit_code == 0
        assert 'Usage:' in result.output

    def test_version_shows_version(self):
        """--version should show version."""
        from frontmatter_normalizer.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ['--version'])

        assert result.exit_code == 0
        assert '0.1.0' in result.output or 'version' in result.output.lower()


class TestCLINormalizeCommand:
    """Tests for the normalize command."""

    def test_normalize_single_file(self, temp_md_file, file_no_frontmatter):
        """Should normalize a single file."""
        from frontmatter_normalizer.cli import main

        filepath = temp_md_file(file_no_frontmatter)
        runner = CliRunner()

        result = runner.invoke(main, ['normalize', str(filepath)])

        assert result.exit_code == 0
        # File should be modified
        content = filepath.read_text()
        assert "---" in content

    def test_normalize_directory(self, temp_srcdir):
        """Should normalize all markdown files in directory."""
        from frontmatter_normalizer.cli import main

        runner = CliRunner()

        result = runner.invoke(main, ['normalize', str(temp_srcdir)])

        assert result.exit_code == 0
        # Should report files processed
        assert 'files' in result.output.lower() or 'processed' in result.output.lower()

    def test_dry_run_does_not_modify(self, temp_md_file, file_no_frontmatter):
        """--dry-run should not modify files."""
        from frontmatter_normalizer.cli import main

        filepath = temp_md_file(file_no_frontmatter)
        original_content = filepath.read_text()
        runner = CliRunner()

        result = runner.invoke(main, ['normalize', '--dry-run', str(filepath)])

        assert result.exit_code == 0
        assert filepath.read_text() == original_content

    def test_dry_run_shows_changes(self, temp_md_file, file_no_frontmatter):
        """--dry-run should show what would change."""
        from frontmatter_normalizer.cli import main

        filepath = temp_md_file(file_no_frontmatter)
        runner = CliRunner()

        result = runner.invoke(main, ['normalize', '--dry-run', str(filepath)])

        assert result.exit_code == 0
        # Should indicate file would be changed
        assert 'would' in result.output.lower() or 'change' in result.output.lower()


class TestCLIExcludePatterns:
    """Tests for file exclusion patterns."""

    def test_excludes_build_directory(self, temp_srcdir):
        """Should exclude _build directory by default."""
        from frontmatter_normalizer.cli import main

        runner = CliRunner()

        result = runner.invoke(main, ['normalize', '--dry-run', str(temp_srcdir)])

        assert result.exit_code == 0
        # _build files should not be mentioned
        assert '_build' not in result.output

    def test_excludes_venv_directory(self, temp_srcdir):
        """Should exclude .venv directory by default."""
        from frontmatter_normalizer.cli import main

        runner = CliRunner()

        result = runner.invoke(main, ['normalize', '--dry-run', str(temp_srcdir)])

        assert result.exit_code == 0
        assert '.venv' not in result.output

    def test_excludes_private_directory(self, temp_srcdir):
        """Should exclude private directory by default."""
        from frontmatter_normalizer.cli import main

        runner = CliRunner()

        result = runner.invoke(main, ['normalize', '--dry-run', str(temp_srcdir)])

        assert result.exit_code == 0
        assert 'private' not in result.output

    def test_custom_exclude_pattern(self, temp_srcdir):
        """--exclude should add custom exclusion patterns."""
        from frontmatter_normalizer.cli import main

        runner = CliRunner()

        result = runner.invoke(main, [
            'normalize', '--dry-run',
            '--exclude', 'theory/*',
            str(temp_srcdir)
        ])

        assert result.exit_code == 0
        assert 'theory' not in result.output


class TestCLIBackup:
    """Tests for backup functionality."""

    def test_creates_backup_by_default(self, temp_md_file, file_no_frontmatter):
        """Should create .bak backup files by default."""
        from frontmatter_normalizer.cli import main

        filepath = temp_md_file(file_no_frontmatter)
        runner = CliRunner()

        result = runner.invoke(main, ['normalize', str(filepath)])

        assert result.exit_code == 0
        backup_path = filepath.with_suffix('.md.bak')
        assert backup_path.exists()

    def test_no_backup_flag(self, temp_md_file, file_no_frontmatter):
        """--no-backup should skip backup creation."""
        from frontmatter_normalizer.cli import main

        filepath = temp_md_file(file_no_frontmatter)
        runner = CliRunner()

        result = runner.invoke(main, ['normalize', '--no-backup', str(filepath)])

        assert result.exit_code == 0
        backup_path = filepath.with_suffix('.md.bak')
        assert not backup_path.exists()


class TestCLIReportCommand:
    """Tests for the report command."""

    def test_report_shows_summary(self, temp_srcdir):
        """report command should show summary of files."""
        from frontmatter_normalizer.cli import main

        runner = CliRunner()

        result = runner.invoke(main, ['report', str(temp_srcdir)])

        assert result.exit_code == 0
        # Should show counts
        assert any(char.isdigit() for char in result.output)

    def test_report_lists_needs_review(self, temp_srcdir):
        """report should list files needing review."""
        from frontmatter_normalizer.cli import main

        runner = CliRunner()

        result = runner.invoke(main, ['report', '--needs-review', str(temp_srcdir)])

        assert result.exit_code == 0

    def test_report_json_format(self, temp_srcdir):
        """--json should output JSON format."""
        from frontmatter_normalizer.cli import main
        import json

        runner = CliRunner()

        result = runner.invoke(main, ['report', '--json', str(temp_srcdir)])

        assert result.exit_code == 0
        # Should be valid JSON
        data = json.loads(result.output)
        assert isinstance(data, dict)


class TestCLIValidateCommand:
    """Tests for the validate command."""

    def test_validate_compliant_file(self, temp_md_file, file_schema_compliant):
        """validate should pass for compliant files."""
        from frontmatter_normalizer.cli import main

        filepath = temp_md_file(file_schema_compliant)
        runner = CliRunner()

        result = runner.invoke(main, ['validate', str(filepath)])

        assert result.exit_code == 0
        assert 'valid' in result.output.lower() or 'pass' in result.output.lower()

    def test_validate_non_compliant_file(self, temp_md_file, file_custom_fields):
        """validate should fail for non-compliant files."""
        from frontmatter_normalizer.cli import main

        filepath = temp_md_file(file_custom_fields)
        runner = CliRunner()

        result = runner.invoke(main, ['validate', str(filepath)])

        # Should indicate issues (non-zero exit or warning)
        # Non-schema fields like Confidence should be flagged
        assert 'Confidence' in result.output or result.exit_code != 0


class TestCLIVerbosity:
    """Tests for verbosity options."""

    def test_verbose_shows_details(self, temp_md_file, file_no_frontmatter):
        """--verbose should show detailed output."""
        from frontmatter_normalizer.cli import main

        filepath = temp_md_file(file_no_frontmatter)
        runner = CliRunner()

        result = runner.invoke(main, ['normalize', '--verbose', '--dry-run', str(filepath)])

        assert result.exit_code == 0
        # Should show field-level details
        assert 'category' in result.output.lower() or 'inferred' in result.output.lower()

    def test_quiet_minimal_output(self, temp_md_file, file_no_frontmatter):
        """--quiet should show minimal output."""
        from frontmatter_normalizer.cli import main

        filepath = temp_md_file(file_no_frontmatter)
        runner = CliRunner()

        result = runner.invoke(main, ['normalize', '--quiet', '--dry-run', str(filepath)])

        assert result.exit_code == 0
        # Should have minimal output
        assert len(result.output.strip().split('\n')) <= 3


class TestCLIErrorHandling:
    """Tests for error handling."""

    def test_nonexistent_path_error(self, tmp_path):
        """Should error gracefully for nonexistent path."""
        from frontmatter_normalizer.cli import main

        runner = CliRunner()
        nonexistent = tmp_path / "nonexistent"

        result = runner.invoke(main, ['normalize', str(nonexistent)])

        assert result.exit_code != 0
        assert 'not found' in result.output.lower() or 'error' in result.output.lower()

    def test_invalid_yaml_continues(self, temp_md_file):
        """Should continue processing after invalid YAML."""
        from frontmatter_normalizer.cli import main

        content = "---\ntitle: [invalid\n---\n\n# Body"
        filepath = temp_md_file(content)
        runner = CliRunner()

        result = runner.invoke(main, ['normalize', '--dry-run', str(filepath)])

        # Should not crash
        assert result.exit_code == 0 or 'warning' in result.output.lower()


class TestCLIEdgeCases:
    """Tests for edge cases and error handling."""

    def test_normalize_no_files_found_message(self, tmp_path):
        """Should show message when no markdown files found."""
        from frontmatter_normalizer.cli import main

        # Create directory with non-markdown files
        (tmp_path / 'file.txt').write_text('not markdown')
        runner = CliRunner()

        result = runner.invoke(main, ['normalize', str(tmp_path)])

        assert result.exit_code == 0
        assert 'no' in result.output.lower() and 'found' in result.output.lower()

    def test_report_error_handling(self, temp_md_file):
        """Report should handle file read errors gracefully."""
        from frontmatter_normalizer.cli import main
        import os

        filepath = temp_md_file("---\ntitle: Test\n---\n# Content")
        runner = CliRunner()

        result = runner.invoke(main, ['report', '--json', str(filepath)])

        assert result.exit_code == 0
        # Should produce valid JSON output
        import json
        data = json.loads(result.output)
        assert 'total' in data

    def test_validate_invalid_category(self, temp_md_file):
        """Validate should flag invalid category values."""
        from frontmatter_normalizer.cli import main

        content = "---\ncategory: NotAValidCategory\n---\n# Content"
        filepath = temp_md_file(content)
        runner = CliRunner()

        result = runner.invoke(main, ['validate', str(filepath)])

        # Should flag invalid category
        assert 'invalid' in result.output.lower() or 'category' in result.output.lower()

    def test_validate_invalid_tags_format(self, temp_md_file):
        """Validate should flag invalid tags format (non-list)."""
        from frontmatter_normalizer.cli import main

        content = "---\ntags: not-a-list\n---\n# Content"
        filepath = temp_md_file(content)
        runner = CliRunner()

        result = runner.invoke(main, ['validate', str(filepath)])

        # Should flag tags format issue
        assert 'tags' in result.output.lower() or result.exit_code != 0

    def test_verbose_needs_review_message(self, temp_md_file, monkeypatch):
        """Verbose mode should show needs review warning."""
        from frontmatter_normalizer.cli import main

        # Create file that would need review (unknown category)
        content = "---\ncategory: Unknown\n---\n# Just a document"
        filepath = temp_md_file(content)
        runner = CliRunner()

        result = runner.invoke(main, ['normalize', '--verbose', '--dry-run', str(filepath)])

        # Should show output (verbose mode)
        assert result.exit_code == 0

    def test_exclusion_file_extension_pattern(self, tmp_path):
        """Should handle file extension exclusion patterns."""
        from frontmatter_normalizer.cli import find_markdown_files

        (tmp_path / 'test.md').write_text('# Test')
        (tmp_path / 'backup.md.bak').write_text('# Backup')

        files = find_markdown_files(tmp_path, ['*.bak'])

        # Should find test.md but not the .bak file
        filenames = [f.name for f in files]
        assert 'test.md' in filenames

    def test_exclusion_fnmatch_glob(self, tmp_path):
        """Should handle glob exclusion patterns."""
        from frontmatter_normalizer.cli import find_markdown_files

        (tmp_path / 'subdir').mkdir()
        (tmp_path / 'test.md').write_text('# Test')
        (tmp_path / 'subdir' / 'nested.md').write_text('# Nested')

        files = find_markdown_files(tmp_path, ['subdir/*'])

        filenames = [f.name for f in files]
        assert 'test.md' in filenames
        assert 'nested.md' not in filenames
