"""Tests for honeypot Sphinx extension.

Tests for generate_honeypot_sources, cleanup_honeypot_sources, and setup.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch


class TestGenerateHoneypotSources:
    """Tests for the generate_honeypot_sources function."""

    def test_skips_when_disabled(self, tmp_path):
        """Should do nothing when honeypot_enabled is False."""
        from honeypot import generate_honeypot_sources

        app = Mock()
        app.config.honeypot_enabled = False
        app.srcdir = str(tmp_path)

        generate_honeypot_sources(app)

        # Should not create honeypot directory
        assert not (tmp_path / 'honeypot-trap').exists()

    def test_creates_honeypot_directory(self, tmp_path, honeypot_template_dir):
        """Should create honeypot-trap directory when enabled."""
        from honeypot import generate_honeypot_sources

        # Create template directory with a template
        honeypot_template_dir.mkdir(exist_ok=True)
        (honeypot_template_dir / 'generic.md.j2').write_text(
            '# {{ page_path }}\n\nCanary: {{ canary_code }}\n'
        )

        app = Mock()
        app.config.honeypot_enabled = True
        app.config.honeypot_pages = [{'path': 'test-page', 'template': 'generic'}]
        app.srcdir = str(tmp_path)

        try:
            generate_honeypot_sources(app)
            assert (tmp_path / 'honeypot-trap').exists()
        finally:
            # Cleanup test template
            (honeypot_template_dir / 'generic.md.j2').unlink(missing_ok=True)

    def test_generates_honeypot_files(self, tmp_path, honeypot_template_dir):
        """Should generate markdown files for each configured page."""
        from honeypot import generate_honeypot_sources

        # Create template directory with a template
        honeypot_template_dir.mkdir(exist_ok=True)
        (honeypot_template_dir / 'test.md.j2').write_text(
            '# Honeypot Page\n\nPath: {{ page_path }}\nCanary: {{ canary_code }}\n'
        )

        app = Mock()
        app.config.honeypot_enabled = True
        app.config.honeypot_pages = [{'path': 'api/internal', 'template': 'test'}]
        app.srcdir = str(tmp_path)

        try:
            generate_honeypot_sources(app)

            # Check file was created
            expected_file = tmp_path / 'honeypot-trap' / 'api_internal.md'
            assert expected_file.exists()

            # Check content was poisoned (has canary)
            content = expected_file.read_text()
            assert 'PCP-' in content  # Canary token prefix
        finally:
            # Cleanup test template
            (honeypot_template_dir / 'test.md.j2').unlink(missing_ok=True)

    def test_warns_when_template_not_found(self, tmp_path):
        """Should warn when template file doesn't exist."""
        from honeypot import generate_honeypot_sources

        app = Mock()
        app.config.honeypot_enabled = True
        app.config.honeypot_pages = [{'path': 'test', 'template': 'nonexistent'}]
        app.srcdir = str(tmp_path)
        app.warn = Mock()

        generate_honeypot_sources(app)

        # Should have warned about template
        app.warn.assert_called()

    def test_warns_when_template_dir_missing(self, tmp_path, honeypot_template_dir):
        """Should warn if template directory doesn't exist."""
        from honeypot import generate_honeypot_sources

        app = Mock()
        app.config.honeypot_enabled = True
        app.config.honeypot_pages = [{'path': 'test'}]
        app.srcdir = str(tmp_path)
        app.warn = Mock()

        # Move template dir temporarily to simulate missing
        temp_backup = honeypot_template_dir.parent / 'templates_backup'

        if honeypot_template_dir.exists():
            honeypot_template_dir.rename(temp_backup)

        try:
            generate_honeypot_sources(app)
            # Should have warned about missing template dir
            app.warn.assert_called()
        finally:
            if temp_backup.exists():
                temp_backup.rename(honeypot_template_dir)


class TestCleanupHoneypotSources:
    """Tests for the cleanup_honeypot_sources function."""

    def test_skips_when_disabled(self, tmp_path):
        """Should do nothing when honeypot_enabled is False."""
        from honeypot import cleanup_honeypot_sources

        app = Mock()
        app.config.honeypot_enabled = False
        app.srcdir = str(tmp_path)

        # Create a honeypot directory that should NOT be touched
        honeypot_dir = tmp_path / 'honeypot-trap'
        honeypot_dir.mkdir()
        (honeypot_dir / 'test.md').write_text('test content')

        cleanup_honeypot_sources(app, None)

        # Directory should still exist (cleanup is currently a no-op)
        assert honeypot_dir.exists()

    def test_does_nothing_when_enabled(self, tmp_path):
        """Currently cleanup is a no-op, just verify no errors."""
        from honeypot import cleanup_honeypot_sources

        app = Mock()
        app.config.honeypot_enabled = True
        app.srcdir = str(tmp_path)

        # Should not raise any errors
        cleanup_honeypot_sources(app, None)

    def test_handles_exception_parameter(self, tmp_path):
        """Should handle exception parameter without errors."""
        from honeypot import cleanup_honeypot_sources

        app = Mock()
        app.config.honeypot_enabled = True
        app.srcdir = str(tmp_path)

        # Should not raise even with an exception passed
        cleanup_honeypot_sources(app, Exception("Build failed"))


class TestHoneypotSetup:
    """Tests for the Sphinx extension setup function."""

    def test_registers_config_values(self):
        """Setup should register configuration values."""
        from honeypot import setup

        app = Mock()
        setup(app)

        config_calls = {call[0][0]: call[0][1] for call in app.add_config_value.call_args_list}
        assert 'honeypot_enabled' in config_calls
        assert config_calls['honeypot_enabled'] is True
        assert 'honeypot_pages' in config_calls
        assert config_calls['honeypot_pages'] == []
        assert 'honeypot_canary_email' in config_calls

    def test_connects_event_handlers(self):
        """Setup should connect builder-inited and build-finished events."""
        from honeypot import setup

        app = Mock()
        setup(app)

        event_names = [call[0][0] for call in app.connect.call_args_list]
        assert 'builder-inited' in event_names
        assert 'build-finished' in event_names

    def test_returns_extension_metadata(self):
        """Setup should return proper extension metadata."""
        from honeypot import setup

        app = Mock()
        result = setup(app)

        assert 'version' in result
        assert result['parallel_read_safe'] is True
        assert result['parallel_write_safe'] is True
