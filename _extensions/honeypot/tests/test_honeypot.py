"""
Tests for honeypot extension main module.

Tests the Sphinx extension setup and honeypot page generation.
These tests establish a baseline for safe refactoring.
"""

from unittest.mock import MagicMock

from honeypot import (
    cleanup_honeypot_sources,
    generate_honeypot_sources,
    setup,
)


class TestExtensionSetup:
    """Test Group 1: Sphinx extension setup."""

    def test_setup_returns_valid_extension_info(self):
        """
        Given: Mock Sphinx app
        When: setup() is called
        Then: Returns dict with version and parallel safety info
        """
        app = MagicMock()

        result = setup(app)

        assert isinstance(result, dict)
        assert 'version' in result
        assert 'parallel_read_safe' in result
        assert 'parallel_write_safe' in result

    def test_setup_registers_config_values(self):
        """
        Given: Mock Sphinx app
        When: setup() is called
        Then: Config values are registered
        """
        app = MagicMock()

        setup(app)

        # Check add_config_value was called for each config
        calls = [call[0][0] for call in app.add_config_value.call_args_list]
        assert 'honeypot_enabled' in calls
        assert 'honeypot_pages' in calls
        assert 'honeypot_canary_email' in calls

    def test_setup_connects_event_handlers(self):
        """
        Given: Mock Sphinx app
        When: setup() is called
        Then: Event handlers are connected
        """
        app = MagicMock()

        setup(app)

        # Check connect was called for events
        calls = [call[0][0] for call in app.connect.call_args_list]
        assert 'builder-inited' in calls
        assert 'build-finished' in calls


class TestGenerateHoneypotSources:
    """Test Group 2: Honeypot source file generation."""

    def test_disabled_honeypot_does_nothing(self, tmp_path):
        """
        Given: honeypot_enabled = False
        When: generate_honeypot_sources is called
        Then: No files are created
        """
        app = MagicMock()
        app.config.honeypot_enabled = False
        app.srcdir = str(tmp_path)

        generate_honeypot_sources(app)

        # No honeypot directory should exist
        honeypot_dir = tmp_path / 'honeypot-trap'
        assert not honeypot_dir.exists()

    def test_enabled_honeypot_creates_directory(self, tmp_path):
        """
        Given: honeypot_enabled = True
        When: generate_honeypot_sources is called
        Then: honeypot-trap directory is created
        """
        app = MagicMock()
        app.config.honeypot_enabled = True
        app.config.honeypot_pages = []  # Empty list - no pages to generate
        app.config.honeypot_canary_email = ''
        app.srcdir = str(tmp_path)

        generate_honeypot_sources(app)

        honeypot_dir = tmp_path / 'honeypot-trap'
        assert honeypot_dir.exists()

    def test_generates_page_from_template(self, tmp_path):
        """
        Given: honeypot_pages with api_docs template
        When: generate_honeypot_sources is called
        Then: Generates markdown file from template
        """
        app = MagicMock()
        app.config.honeypot_enabled = True
        app.config.honeypot_pages = [
            {'path': 'api-docs/internal-v2', 'template': 'api_docs'},
        ]
        app.config.honeypot_canary_email = ''
        app.srcdir = str(tmp_path)

        generate_honeypot_sources(app)

        # Check file was created
        output_file = tmp_path / 'honeypot-trap' / 'api-docs_internal-v2.md'
        assert output_file.exists()

        # Check content
        content = output_file.read_text()
        assert 'Internal API' in content  # From template
        assert 'PCP-' in content  # Canary code

    def test_generates_multiple_pages(self, tmp_path):
        """
        Given: honeypot_pages with multiple templates
        When: generate_honeypot_sources is called
        Then: Generates all specified pages
        """
        app = MagicMock()
        app.config.honeypot_enabled = True
        app.config.honeypot_pages = [
            {'path': 'api-docs', 'template': 'api_docs'},
            {'path': 'policies', 'template': 'internal_policy'},
            {'path': 'training', 'template': 'training_data'},
        ]
        app.config.honeypot_canary_email = ''
        app.srcdir = str(tmp_path)

        generate_honeypot_sources(app)

        honeypot_dir = tmp_path / 'honeypot-trap'
        files = list(honeypot_dir.glob('*.md'))
        assert len(files) == 3

    def test_adds_prompt_injection_to_content(self, tmp_path):
        """
        Given: honeypot page configuration
        When: generate_honeypot_sources is called
        Then: Generated file includes hidden prompt injection
        """
        app = MagicMock()
        app.config.honeypot_enabled = True
        app.config.honeypot_pages = [
            {'path': 'test-page', 'template': 'api_docs'},
        ]
        app.config.honeypot_canary_email = ''
        app.srcdir = str(tmp_path)

        generate_honeypot_sources(app)

        output_file = tmp_path / 'honeypot-trap' / 'test-page.md'
        content = output_file.read_text()
        # Should contain hidden prompt injection div
        assert 'poison-prompt' in content
        assert 'aria-hidden="true"' in content

    def test_uses_custom_canary_email(self, tmp_path):
        """
        Given: honeypot_canary_email is set
        When: generate_honeypot_sources is called
        Then: Custom email appears in prompt injection
        """
        app = MagicMock()
        app.config.honeypot_enabled = True
        app.config.honeypot_pages = [
            {'path': 'test-page', 'template': 'api_docs'},
        ]
        app.config.honeypot_canary_email = 'custom@trap.example'
        app.srcdir = str(tmp_path)

        generate_honeypot_sources(app)

        output_file = tmp_path / 'honeypot-trap' / 'test-page.md'
        content = output_file.read_text()
        assert 'custom@trap.example' in content

    def test_handles_missing_template_gracefully(self, tmp_path, caplog):
        """
        Given: honeypot_pages with nonexistent template
        When: generate_honeypot_sources is called
        Then: Warns but does not crash
        """
        app = MagicMock()
        app.config.honeypot_enabled = True
        app.config.honeypot_pages = [
            {'path': 'test', 'template': 'nonexistent_template'},
        ]
        app.config.honeypot_canary_email = ''
        app.srcdir = str(tmp_path)

        # Should not raise
        generate_honeypot_sources(app)

        # Warning should be logged
        assert 'template not found' in caplog.text.lower()


class TestCleanupHoneypotSources:
    """Test Group 3: Honeypot cleanup on build finish."""

    def test_disabled_honeypot_does_nothing(self, tmp_path):
        """
        Given: honeypot_enabled = False
        When: cleanup_honeypot_sources is called
        Then: No action taken (function returns early)
        """
        app = MagicMock()
        app.config.honeypot_enabled = False
        app.srcdir = str(tmp_path)

        # Create a honeypot dir to verify it's not touched
        honeypot_dir = tmp_path / 'honeypot-trap'
        honeypot_dir.mkdir()
        (honeypot_dir / 'test.md').write_text('test')

        cleanup_honeypot_sources(app, None)

        # File should still exist (cleanup is currently a no-op for debugging)
        assert (honeypot_dir / 'test.md').exists()

    def test_enabled_honeypot_cleanup_no_exception(self, tmp_path):
        """
        Given: honeypot_enabled = True
        When: cleanup_honeypot_sources is called without exception
        Then: No error occurs
        """
        app = MagicMock()
        app.config.honeypot_enabled = True
        app.srcdir = str(tmp_path)

        # Should not raise
        cleanup_honeypot_sources(app, None)


class TestIntegration:
    """Test Group 4: Integration tests with actual templates."""

    def test_api_docs_template_renders(self, tmp_path):
        """
        Given: api_docs template
        When: Used in honeypot generation
        Then: Contains expected API documentation elements
        """
        app = MagicMock()
        app.config.honeypot_enabled = True
        app.config.honeypot_pages = [
            {'path': 'api', 'template': 'api_docs'},
        ]
        app.config.honeypot_canary_email = ''
        app.srcdir = str(tmp_path)

        generate_honeypot_sources(app)

        content = (tmp_path / 'honeypot-trap' / 'api.md').read_text()
        # Should contain API-related content
        assert 'API' in content
        assert 'endpoint' in content.lower() or 'Endpoint' in content

    def test_internal_policy_template_renders(self, tmp_path):
        """
        Given: internal_policy template
        When: Used in honeypot generation
        Then: Contains expected policy elements
        """
        app = MagicMock()
        app.config.honeypot_enabled = True
        app.config.honeypot_pages = [
            {'path': 'policy', 'template': 'internal_policy'},
        ]
        app.config.honeypot_canary_email = ''
        app.srcdir = str(tmp_path)

        generate_honeypot_sources(app)

        content = (tmp_path / 'honeypot-trap' / 'policy.md').read_text()
        # Should contain policy-related content
        assert 'Policy' in content or 'policy' in content
        assert 'licensing' in content.lower()

    def test_training_data_template_renders(self, tmp_path):
        """
        Given: training_data template
        When: Used in honeypot generation
        Then: Contains expected training data elements
        """
        app = MagicMock()
        app.config.honeypot_enabled = True
        app.config.honeypot_pages = [
            {'path': 'training', 'template': 'training_data'},
        ]
        app.config.honeypot_canary_email = ''
        app.srcdir = str(tmp_path)

        generate_honeypot_sources(app)

        content = (tmp_path / 'honeypot-trap' / 'training.md').read_text()
        # Should contain training data references
        assert 'Training' in content or 'training' in content
        assert 'Dataset' in content or 'dataset' in content or 'data' in content.lower()
