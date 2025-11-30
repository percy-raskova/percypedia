"""
Tests for AI content cross-reference roles - Sprint 4.

These tests verify the :ai:chat:, :ai:exchange:, and :ai:message: roles
create proper cross-references to AI content.
"""


from docutils import nodes

from .conftest import make_mock_inliner


class TestAIChatRole:
    """Test Group 1: :ai:chat: role for referencing chats."""

    def test_role_creates_reference(self):
        """
        Given: :ai:chat:`name` role in text
        When: Role is processed
        Then: Creates a reference node
        """
        from ai_content.roles import ai_chat_role

        rawtext = ':ai:chat:`dialectical-materialism`'
        text = 'dialectical-materialism'

        inliner = make_mock_inliner(
            chats={
                'dialectical-materialism': {
                    'title': 'Dialectical Materialism',
                    'anchor': 'ai-chat-dialectical-materialism',
                    'docname': 'ai-archive/chats',
                }
            }
        )

        result_nodes, _messages = ai_chat_role(
            'ai:chat', rawtext, text, 10, inliner
        )

        assert len(result_nodes) == 1
        assert isinstance(result_nodes[0], nodes.reference)

    def test_role_uses_title_as_text(self):
        """
        Given: :ai:chat:`name` without explicit text
        When: Role is processed
        Then: Uses the chat title as link text
        """
        from ai_content.roles import ai_chat_role

        rawtext = ':ai:chat:`test-chat`'
        text = 'test-chat'

        inliner = make_mock_inliner(
            chats={
                'test-chat': {
                    'title': 'Test Chat Title',
                    'anchor': 'ai-chat-test-chat',
                    'docname': 'test-doc',
                }
            }
        )

        result_nodes, _messages = ai_chat_role(
            'ai:chat', rawtext, text, 10, inliner
        )

        # The reference should contain the title
        ref = result_nodes[0]
        assert 'Test Chat Title' in ref.astext()

    def test_role_handles_missing_chat(self):
        """
        Given: :ai:chat:`nonexistent` for undefined chat
        When: Role is processed
        Then: Returns warning message, still creates node
        """
        from ai_content.roles import ai_chat_role

        rawtext = ':ai:chat:`nonexistent`'
        text = 'nonexistent'

        inliner = make_mock_inliner()  # Empty chats

        result_nodes, _messages = ai_chat_role(
            'ai:chat', rawtext, text, 10, inliner
        )

        # Should still return a node (with problematic class)
        assert len(result_nodes) == 1


class TestAIExchangeRole:
    """Test Group 2: :ai:exchange: role."""

    def test_role_creates_reference(self):
        """
        Given: :ai:exchange:`name` role
        When: Role is processed
        Then: Creates a reference to the exchange
        """
        from ai_content.roles import ai_exchange_role

        rawtext = ':ai:exchange:`commodity-fetishism`'
        text = 'commodity-fetishism'

        inliner = make_mock_inliner(
            exchanges={
                'commodity-fetishism': {
                    'title': 'Commodity Fetishism',
                    'anchor': 'ai-exchange-commodity-fetishism',
                    'docname': 'test-doc',
                }
            }
        )

        result_nodes, _messages = ai_exchange_role(
            'ai:exchange', rawtext, text, 10, inliner
        )

        assert len(result_nodes) == 1
        assert isinstance(result_nodes[0], nodes.reference)


class TestAIMessageRole:
    """Test Group 3: :ai:message: role."""

    def test_role_creates_reference(self):
        """
        Given: :ai:message:`name` role
        When: Role is processed
        Then: Creates a reference to the message
        """
        from ai_content.roles import ai_message_role

        rawtext = ':ai:message:`rate-of-profit`'
        text = 'rate-of-profit'

        inliner = make_mock_inliner(
            messages={
                'rate-of-profit': {
                    'title': 'Rate Of Profit',
                    'anchor': 'ai-message-rate-of-profit',
                    'docname': 'test-doc',
                }
            }
        )

        result_nodes, _messages = ai_message_role(
            'ai:message', rawtext, text, 10, inliner
        )

        assert len(result_nodes) == 1
        assert isinstance(result_nodes[0], nodes.reference)


class TestAIRefRole:
    """Test Group 4: :ai:ref: generic role."""

    def test_role_finds_chat(self):
        """
        Given: :ai:ref:`name` where name is a chat
        When: Role is processed
        Then: Links to the chat
        """
        from ai_content.roles import ai_ref_role

        rawtext = ':ai:ref:`my-chat`'
        text = 'my-chat'

        inliner = make_mock_inliner(
            chats={
                'my-chat': {
                    'title': 'My Chat',
                    'anchor': 'ai-chat-my-chat',
                    'docname': 'test-doc',
                }
            }
        )

        result_nodes, _messages = ai_ref_role(
            'ai:ref', rawtext, text, 10, inliner
        )

        assert len(result_nodes) == 1

    def test_role_finds_exchange(self):
        """
        Given: :ai:ref:`name` where name is an exchange
        When: Role is processed
        Then: Links to the exchange
        """
        from ai_content.roles import ai_ref_role

        rawtext = ':ai:ref:`my-exchange`'
        text = 'my-exchange'

        inliner = make_mock_inliner(
            exchanges={
                'my-exchange': {
                    'title': 'My Exchange',
                    'anchor': 'ai-exchange-my-exchange',
                    'docname': 'test-doc',
                }
            }
        )

        result_nodes, _messages = ai_ref_role(
            'ai:ref', rawtext, text, 10, inliner
        )

        assert len(result_nodes) == 1

    def test_role_finds_message(self):
        """
        Given: :ai:ref:`name` where name is a message
        When: Role is processed
        Then: Links to the message
        """
        from ai_content.roles import ai_ref_role

        rawtext = ':ai:ref:`my-message`'
        text = 'my-message'

        inliner = make_mock_inliner(
            messages={
                'my-message': {
                    'title': 'My Message',
                    'anchor': 'ai-message-my-message',
                    'docname': 'test-doc',
                }
            }
        )

        result_nodes, _messages = ai_ref_role(
            'ai:ref', rawtext, text, 10, inliner
        )

        assert len(result_nodes) == 1
