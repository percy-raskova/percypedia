"""
Tests for AI Archive Index directive - Sprint 5.

Tests the {ai-archive} directive that generates an index of all
AI content (chats, exchanges, messages).
"""

import pytest

from docutils import nodes

from .conftest import make_archive_directive, SAMPLE_ARCHIVE_ENV


class TestArchiveIndexDirective:
    """Test Group 1: Archive index rendering."""

    @pytest.fixture
    def mock_directive(self):
        """Create a mock directive with AI content in environment."""
        return make_archive_directive()

    def test_directive_renders_container(self, mock_directive):
        """
        Given: An {ai-archive} directive
        When: Processed
        Then: Renders a container node
        """
        from ai_content.directives import AIArchiveDirective

        result = AIArchiveDirective.run(mock_directive)

        assert len(result) == 1
        assert isinstance(result[0], nodes.container)
        assert 'ai-archive-index' in result[0].get('classes', [])

    def test_directive_includes_all_content_types(self, mock_directive):
        """
        Given: Environment with chats, exchanges, and messages
        When: Archive directive processed
        Then: Contains sections for all types
        """
        from ai_content.directives import AIArchiveDirective

        result = AIArchiveDirective.run(mock_directive)
        container = result[0]

        # Check for section headers
        text = container.astext()
        assert 'Chat' in text or 'Conversation' in text
        assert 'Exchange' in text
        assert 'Message' in text or 'Quote' in text

    def test_directive_lists_items(self, mock_directive):
        """
        Given: Environment with AI content
        When: Archive directive processed
        Then: Lists all items with titles
        """
        from ai_content.directives import AIArchiveDirective

        result = AIArchiveDirective.run(mock_directive)
        container = result[0]

        text = container.astext()
        assert 'Chat One' in text
        assert 'Chat Two' in text
        assert 'Exchange One' in text
        assert 'Message One' in text


class TestArchiveIndexOptions:
    """Test Group 2: Archive index options."""

    @pytest.fixture
    def mock_directive(self):
        """Create a mock directive with only chats."""
        return make_archive_directive(
            env_attrs={
                'ai_content_chats': {
                    'chat-1': {'title': 'Chat', 'date': '2024-11-01'},
                },
                'ai_content_exchanges': {},
                'ai_content_messages': {},
            },
        )

    def test_show_dates_option(self, mock_directive):
        """
        Given: {ai-archive} with :show-dates: option
        When: Processed
        Then: Includes dates in listing
        """
        from ai_content.directives import AIArchiveDirective

        mock_directive.options = {'show-dates': True}
        result = AIArchiveDirective.run(mock_directive)

        text = result[0].astext()
        assert '2024' in text  # Date should appear

    def test_type_filter_option(self):
        """
        Given: {ai-archive} with :type: chats option
        When: Processed
        Then: Only shows chats
        """
        from ai_content.directives import AIArchiveDirective

        # Create directive with both chats and exchanges
        directive = make_archive_directive(
            options={'type': 'chats'},
            env_attrs={
                'ai_content_chats': {
                    'chat-1': {'title': 'Chat', 'date': '2024-11-01'},
                },
                'ai_content_exchanges': {
                    'ex-1': {'title': 'Exchange'},
                },
                'ai_content_messages': {},
            },
        )

        result = AIArchiveDirective.run(directive)

        text = result[0].astext()
        assert 'Chat' in text
        # Exchange shouldn't be shown when filtered to chats only
        assert 'Exchange' not in text
