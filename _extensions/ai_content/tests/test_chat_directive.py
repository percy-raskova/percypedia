"""
Tests for AIChatDirective - Sprint 1: Core chat directive.

These tests verify the {ai-chat} directive parses [human]/[assistant]
messages and renders as a styled chat container.
"""

import pytest

from .conftest import SAMPLE_CHAT_CONTENT, make_mock_directive


class TestChatMessageParsing:
    """Test Group 1: Parse [human]/[assistant] markers."""

    def test_parse_single_exchange(self):
        """
        Given: Content with one [human] and one [assistant] block
        When: parse_messages is called
        Then: Returns list with 2 messages, correct senders
        """
        from ai_content.parser import parse_chat_messages

        content = """[human]
How do I use Azure?

[assistant]
Azure is a cloud platform..."""

        messages = parse_chat_messages(content)

        assert len(messages) == 2
        assert messages[0]['sender'] == 'human'
        assert 'Azure' in messages[0]['content']
        assert messages[1]['sender'] == 'assistant'
        assert 'cloud platform' in messages[1]['content']

    def test_parse_multiple_exchanges(self):
        """
        Given: Content with multiple back-and-forth exchanges
        When: parse_messages is called
        Then: Returns all messages in order
        """
        from ai_content.parser import parse_chat_messages

        content = """[human]
First question

[assistant]
First answer

[human]
Follow-up question

[assistant]
Follow-up answer"""

        messages = parse_chat_messages(content)

        assert len(messages) == 4
        assert messages[0]['sender'] == 'human'
        assert messages[1]['sender'] == 'assistant'
        assert messages[2]['sender'] == 'human'
        assert messages[3]['sender'] == 'assistant'

    def test_parse_preserves_markdown_in_messages(self):
        """
        Given: Message content with markdown formatting
        When: parse_messages is called
        Then: Markdown is preserved in content
        """
        from ai_content.parser import parse_chat_messages

        content = """[human]
What is **important**?

[assistant]
Here's a list:
- Item 1
- Item 2

```python
print("code")
```"""

        messages = parse_chat_messages(content)

        assert '**important**' in messages[0]['content']
        assert '- Item 1' in messages[1]['content']
        assert '```python' in messages[1]['content']

    def test_parse_handles_empty_content(self):
        """
        Given: Empty content
        When: parse_messages is called
        Then: Returns empty list
        """
        from ai_content.parser import parse_chat_messages

        messages = parse_chat_messages("")
        assert messages == []

    def test_parse_handles_no_markers(self):
        """
        Given: Content without [human]/[assistant] markers
        When: parse_messages is called
        Then: Returns empty list (no valid messages)
        """
        from ai_content.parser import parse_chat_messages

        content = "Just some random text without markers"
        messages = parse_chat_messages(content)

        assert messages == []


class TestChatDirectiveRendering:
    """Test Group 2: Directive renders as chat container."""

    @pytest.fixture
    def mock_directive(self):
        """Create a mock directive with minimal Sphinx environment."""
        from ai_content.directives import AIChatDirective

        return make_mock_directive(
            AIChatDirective,
            arguments=['azure-discussion'],
            content=SAMPLE_CHAT_CONTENT,
            options={
                'date': '2024-05-02',
                'source': 'Claude Desktop',
            },
            docname='ai-archive/chats',
        )

    def test_directive_renders_chat_container(self, mock_directive):
        """
        Given: An ai-chat directive with messages
        When: The directive is processed
        Then: Output contains ai_chat_node with proper classes
        """
        from ai_content.directives import AIChatDirective
        from ai_content.nodes import ai_chat_node

        result = AIChatDirective.run(mock_directive)

        assert len(result) == 1
        assert isinstance(result[0], ai_chat_node)
        assert 'ai-chat' in result[0]['classes']

    def test_directive_includes_header_with_title(self, mock_directive):
        """
        Given: Directive with name 'azure-discussion'
        When: Processed
        Then: Header contains formatted title
        """
        from ai_content.directives import AIChatDirective

        result = AIChatDirective.run(mock_directive)
        chat_node = result[0]

        # Find header
        header = None
        for child in chat_node.children:
            if hasattr(child, 'get') and 'ai-chat-header' in child.get('classes', []):
                header = child
                break

        assert header is not None

    def test_directive_includes_ai_badge(self, mock_directive):
        """
        Given: Any ai-chat directive
        When: Processed
        Then: Output includes AI badge for transparency
        """
        from ai_content.directives import AIChatDirective

        result = AIChatDirective.run(mock_directive)
        chat_node = result[0]

        assert 'ai-generated' in chat_node['classes']

    def test_directive_renders_messages(self, mock_directive):
        """
        Given: Directive with human and assistant messages
        When: Processed
        Then: Both messages appear in output with correct sender classes
        """
        from ai_content.directives import AIChatDirective

        result = AIChatDirective.run(mock_directive)
        chat_node = result[0]

        # Find messages container
        messages_container = None
        for child in chat_node.children:
            if hasattr(child, 'get') and 'ai-chat-messages' in child.get('classes', []):
                messages_container = child
                break

        assert messages_container is not None
        # Should have 2 message nodes
        message_nodes = [c for c in messages_container.children
                        if hasattr(c, 'get') and 'ai-message' in c.get('classes', [])]
        assert len(message_nodes) == 2

    def test_directive_stores_in_env(self, mock_directive):
        """
        Given: An ai-chat directive
        When: Processed
        Then: Chat metadata stored in env.ai_content_chats
        """
        from ai_content.directives import AIChatDirective

        AIChatDirective.run(mock_directive)

        chats = mock_directive.env.ai_content_chats
        assert 'azure-discussion' in chats
        assert chats['azure-discussion']['date'] == '2024-05-02'
        assert chats['azure-discussion']['source'] == 'Claude Desktop'


class TestChatDirectiveOptions:
    """Test Group 3: Directive options handling."""

    def test_date_option_parsed(self):
        """
        Given: Directive with :date: 2024-05-02
        When: Processed
        Then: Date is stored and rendered
        """
        from ai_content.directives import AIChatDirective

        directive = make_mock_directive(
            AIChatDirective,
            arguments=['test-chat'],
            content=['[human]', 'Test', '', '[assistant]', 'Response'],
            options={'date': '2024-05-02'},
            lineno=1,
        )

        AIChatDirective.run(directive)

        assert directive.env.ai_content_chats['test-chat']['date'] == '2024-05-02'

    def test_source_option_parsed(self):
        """
        Given: Directive with :source: Claude Desktop
        When: Processed
        Then: Source is stored
        """
        from ai_content.directives import AIChatDirective

        directive = make_mock_directive(
            AIChatDirective,
            arguments=['test-chat'],
            content=['[human]', 'Test', '', '[assistant]', 'Response'],
            options={'source': 'Claude Desktop'},
            lineno=1,
        )

        AIChatDirective.run(directive)

        assert directive.env.ai_content_chats['test-chat']['source'] == 'Claude Desktop'

    def test_id_option_stored_but_not_rendered(self):
        """
        Given: Directive with :id: (private UUID)
        When: Processed
        Then: ID stored in env but not in rendered output
        """
        from ai_content.directives import AIChatDirective

        directive = make_mock_directive(
            AIChatDirective,
            arguments=['test-chat'],
            content=['[human]', 'Test', '', '[assistant]', 'Response'],
            options={'id': 'd08cc89d-7559-40fd-a38c-e96362b064fc'},
            lineno=1,
        )

        result = AIChatDirective.run(directive)
        chat_node = result[0]

        # ID should be in env
        assert directive.env.ai_content_chats['test-chat']['id'] == 'd08cc89d-7559-40fd-a38c-e96362b064fc'

        # ID should NOT be in rendered node attributes
        assert 'd08cc89d' not in str(chat_node.get('ids', []))


class TestChatAnchorGeneration:
    """Test Group 4: Anchor IDs for cross-referencing."""

    def test_anchor_id_from_name(self):
        """
        Given: Directive with name 'azure-discussion'
        When: Processed
        Then: Node has anchor id 'ai-chat-azure-discussion'
        """
        from ai_content.directives import AIChatDirective

        directive = make_mock_directive(
            AIChatDirective,
            arguments=['azure-discussion'],
            content=['[human]', 'Test', '', '[assistant]', 'Response'],
            lineno=1,
        )

        result = AIChatDirective.run(directive)
        chat_node = result[0]

        assert 'ai-chat-azure-discussion' in chat_node['ids']

    def test_anchor_handles_spaces_in_name(self):
        """
        Given: Directive with name 'Azure Architecture Discussion'
        When: Processed
        Then: Anchor ID is slugified
        """
        from ai_content.directives import AIChatDirective

        directive = make_mock_directive(
            AIChatDirective,
            arguments=['Azure Architecture Discussion'],
            content=['[human]', 'Test', '', '[assistant]', 'Response'],
            lineno=1,
        )

        result = AIChatDirective.run(directive)
        chat_node = result[0]

        # Should be slugified
        anchor = chat_node['ids'][0]
        assert ' ' not in anchor
        assert 'azure' in anchor.lower()
