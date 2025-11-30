"""
Tests for AIMessageDirective - Sprint 3: Single message quotes.

These tests verify the {ai-message} directive renders a single
AI message excerpt with attribution and styling.
"""

import pytest

from .conftest import SAMPLE_MESSAGE_CONTENT, make_mock_directive


class TestMessageDirective:
    """Test Group 1: Basic ai-message rendering."""

    @pytest.fixture
    def mock_directive(self):
        """Create a mock directive with minimal Sphinx environment."""
        from ai_content.directives import AIMessageDirective

        return make_mock_directive(
            AIMessageDirective,
            arguments=['test-quote'],
            content=SAMPLE_MESSAGE_CONTENT,
            options={'sender': 'assistant'},
            docname='ai-archive/quotes',
        )

    def test_directive_renders_message_node(self, mock_directive):
        """
        Given: An {ai-message} directive with content
        When: Directive is processed
        Then: Renders an ai_message_node container
        """
        from ai_content.directives import AIMessageDirective
        from ai_content.nodes import ai_message_node

        result = AIMessageDirective.run(mock_directive)

        assert len(result) == 1
        assert isinstance(result[0], ai_message_node)

    def test_directive_has_ai_badge(self, mock_directive):
        """
        Given: An {ai-message} directive
        When: Directive is processed
        Then: Contains an AI badge for transparency
        """
        from ai_content.directives import AIMessageDirective

        result = AIMessageDirective.run(mock_directive)
        message_node = result[0]

        # Check for badge in children
        badge_found = False
        for child in message_node.findall():
            if hasattr(child, 'get') and 'ai-badge' in child.get('classes', []):
                badge_found = True
                break

        assert badge_found, "AI badge not found in message node"

    def test_directive_has_assistant_class(self, mock_directive):
        """
        Given: An {ai-message} directive with sender: assistant
        When: Directive is processed
        Then: Has ai-message-assistant class
        """
        from ai_content.directives import AIMessageDirective

        result = AIMessageDirective.run(mock_directive)

        assert 'ai-message-assistant' in result[0].get('classes', [])

    def test_directive_supports_human_sender(self, mock_directive):
        """
        Given: An {ai-message} directive with sender: human
        When: Directive is processed
        Then: Has ai-message-human class
        """
        from ai_content.directives import AIMessageDirective

        mock_directive.options = {'sender': 'human'}
        result = AIMessageDirective.run(mock_directive)

        assert 'ai-message-human' in result[0].get('classes', [])

    def test_directive_defaults_to_assistant(self, mock_directive):
        """
        Given: An {ai-message} directive without sender option
        When: Directive is processed
        Then: Defaults to assistant sender
        """
        from ai_content.directives import AIMessageDirective

        mock_directive.options = {}  # No sender specified
        result = AIMessageDirective.run(mock_directive)

        assert 'ai-message-assistant' in result[0].get('classes', [])


class TestMessageOptions:
    """Test Group 2: Directive options."""

    @pytest.fixture
    def mock_directive(self):
        """Create a mock directive."""
        from ai_content.directives import AIMessageDirective

        return make_mock_directive(
            AIMessageDirective,
            arguments=['test-quote'],
            content=['Quote content.'],
            docname='test-doc',
        )

    def test_date_option_stored(self, mock_directive):
        """
        Given: An {ai-message} with :date: option
        When: Directive is processed
        Then: Date is stored in environment
        """
        from ai_content.directives import AIMessageDirective

        mock_directive.options = {'date': '2024-11-28', 'sender': 'assistant'}
        AIMessageDirective.run(mock_directive)

        env = mock_directive.env
        assert 'test-quote' in env.ai_content_messages
        assert env.ai_content_messages['test-quote']['date'] == '2024-11-28'

    def test_source_option_stored(self, mock_directive):
        """
        Given: An {ai-message} with :source: option
        When: Directive is processed
        Then: Source is stored in environment
        """
        from ai_content.directives import AIMessageDirective

        mock_directive.options = {'source': 'Claude Desktop', 'sender': 'assistant'}
        AIMessageDirective.run(mock_directive)

        env = mock_directive.env
        assert env.ai_content_messages['test-quote']['source'] == 'Claude Desktop'

    def test_model_option_stored(self, mock_directive):
        """
        Given: An {ai-message} with :model: option
        When: Directive is processed
        Then: Model is stored in environment
        """
        from ai_content.directives import AIMessageDirective

        mock_directive.options = {'model': 'claude-sonnet-4', 'sender': 'assistant'}
        AIMessageDirective.run(mock_directive)

        env = mock_directive.env
        assert env.ai_content_messages['test-quote']['model'] == 'claude-sonnet-4'

    def test_context_option_stored(self, mock_directive):
        """
        Given: An {ai-message} with :context: option (brief description)
        When: Directive is processed
        Then: Context is stored in environment
        """
        from ai_content.directives import AIMessageDirective

        mock_directive.options = {
            'context': 'Discussion about labor theory of value',
            'sender': 'assistant',
        }
        AIMessageDirective.run(mock_directive)

        env = mock_directive.env
        assert 'labor theory' in env.ai_content_messages['test-quote']['context']


class TestMessageAnchor:
    """Test Group 3: Anchor ID generation."""

    @pytest.fixture
    def mock_directive(self):
        """Create a mock directive."""
        from ai_content.directives import AIMessageDirective

        return make_mock_directive(
            AIMessageDirective,
            content=['Content.'],
            options={'sender': 'assistant'},
            docname='test-doc',
        )

    def test_anchor_from_name(self, mock_directive):
        """
        Given: An {ai-message} with a name
        When: Directive is processed
        Then: Generates an anchor ID from the name
        """
        from ai_content.directives import AIMessageDirective

        mock_directive.arguments = ['important-insight']
        result = AIMessageDirective.run(mock_directive)

        assert 'ai-message-important-insight' in result[0].get('ids', [])

    def test_anchor_handles_spaces(self, mock_directive):
        """
        Given: An {ai-message} with spaces in name
        When: Directive is processed
        Then: Slugifies the name for anchor
        """
        from ai_content.directives import AIMessageDirective

        mock_directive.arguments = ['My Important Quote']
        result = AIMessageDirective.run(mock_directive)

        assert 'ai-message-my-important-quote' in result[0].get('ids', [])
