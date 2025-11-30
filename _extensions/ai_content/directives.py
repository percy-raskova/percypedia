"""
AI Content Directives.

Provides directives for embedding AI-generated content in Sphinx documents.

This module contains the main content directives:
- AIChatDirective: Full multi-message conversations
- AIExchangeDirective: Single Q&A exchanges
- AIMessageDirective: Single message quotes

For the archive directive, see archive.py.
For helper functions, see builders.py.
For storage utilities, see storage.py.
"""

from typing import Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

from .builders import (
    build_answer_section,
    build_exchange_header,
    build_message_header,
    build_question_section,
)
from .nodes import ai_chat_node, ai_exchange_node, ai_message_node
from .parser import format_title, parse_chat_messages, parse_exchange, slugify
from .storage import AIContentStorage

# Re-export AIArchiveDirective for backward compatibility
from .archive import AIArchiveDirective

__all__ = [
    'AIChatDirective',
    'AIExchangeDirective',
    'AIMessageDirective',
    'AIArchiveDirective',
]


class AIChatDirective(SphinxDirective):
    """
    Directive for embedding AI chat conversations.

    Usage:
        ```{ai-chat} conversation-name
        :date: 2024-05-02
        :source: Claude Desktop
        :id: optional-private-uuid

        [human]
        User's question here...

        [assistant]
        AI's response here...
        ```
    """

    has_content = True
    required_arguments = 1  # Conversation name
    optional_arguments = 0
    final_argument_whitespace = True

    option_spec: ClassVar[dict[str, Any]] = {
        'date': directives.unchanged,
        'source': directives.unchanged,
        'id': directives.unchanged,  # Private, not rendered
        'class': directives.class_option,
    }

    def run(self) -> list[nodes.Node]:
        """Process the ai-chat directive."""
        name = self.arguments[0].strip()
        slug = slugify(name)
        anchor_id = f'ai-chat-{slug}'
        title = format_title(name)

        # Parse messages from content
        content_str = '\n'.join(self.content)
        messages = parse_chat_messages(content_str)

        # Build the chat container
        chat = ai_chat_node()
        chat['classes'] = ['ai-chat', 'ai-generated']
        if 'class' in self.options:
            chat['classes'].extend(self.options['class'])
        chat['ids'] = [anchor_id]

        # Header with title and metadata
        header = nodes.container(classes=['ai-chat-header'])

        # Title
        title_para = nodes.paragraph(classes=['ai-chat-title'])
        title_para += nodes.strong(text=title)
        header += title_para

        # Metadata line
        meta_parts = []
        if 'date' in self.options:
            meta_parts.append(self.options['date'])
        if 'source' in self.options:
            meta_parts.append(self.options['source'])

        if meta_parts:
            meta_para = nodes.paragraph(classes=['ai-chat-meta'])
            meta_para += nodes.Text(' • '.join(meta_parts))
            header += meta_para

        # AI badge
        badge = nodes.inline(classes=['ai-badge'])
        badge += nodes.Text('AI Chat')
        header += badge

        chat += header

        # Messages container
        messages_container = nodes.container(classes=['ai-chat-messages'])

        for msg in messages:
            sender = msg['sender']
            msg_node = ai_message_node()
            msg_node['classes'] = ['ai-message', f'ai-message-{sender}']
            msg_node['sender'] = sender

            # Sender label
            sender_label = nodes.paragraph(classes=['ai-sender'])
            sender_label += nodes.Text('Human' if sender == 'human' else 'Assistant')
            msg_node += sender_label

            # Message content (parse as nested RST/MyST)
            content_container = nodes.container(classes=['ai-content'])

            # Parse content as nested markup
            content_lines = msg['content'].split('\n')
            self.state.nested_parse(
                content_lines,
                self.content_offset,
                content_container,
            )
            msg_node += content_container

            messages_container += msg_node

        chat += messages_container

        # Store in environment for indexing
        AIContentStorage.store_content(self.env, 'chat', name, {
            'title': title,
            'slug': slug,
            'anchor': anchor_id,
            'docname': self.env.docname,
            'lineno': self.lineno,
            'date': self.options.get('date', ''),
            'source': self.options.get('source', ''),
            'id': self.options.get('id', ''),  # Stored but not rendered
            'message_count': len(messages),
        })

        return [chat]


class AIExchangeDirective(SphinxDirective):
    """
    Directive for a single Q&A exchange.

    Usage:
        ```{ai-exchange} exchange-name
        :date: 2024-06-15
        :model: claude-sonnet-4

        What is the question?
        ---
        Here is the answer...
        ```
    """

    has_content = True
    required_arguments = 1  # Exchange name
    optional_arguments = 0
    final_argument_whitespace = True

    option_spec: ClassVar[dict[str, Any]] = {
        'date': directives.unchanged,
        'model': directives.unchanged,
        'source': directives.unchanged,
        'id': directives.unchanged,
        'class': directives.class_option,
    }

    def run(self) -> list[nodes.Node]:
        """Process the ai-exchange directive."""
        name = self.arguments[0].strip()
        slug = slugify(name)
        anchor_id = f'ai-exchange-{slug}'
        title = format_title(name)

        # Parse question/answer from content
        content_str = '\n'.join(self.content)
        exchange_data = parse_exchange(content_str)
        if not exchange_data:
            exchange_data = {'question': '', 'answer': content_str}

        # Build the exchange container
        exchange = ai_exchange_node()
        exchange['classes'] = ['ai-exchange', 'ai-generated']
        if 'class' in self.options:
            exchange['classes'].extend(self.options['class'])
        exchange['ids'] = [anchor_id]

        exchange += build_exchange_header(title, self.options)

        # Question section (if present)
        if exchange_data['question']:
            exchange += build_question_section(
                exchange_data['question'], self.state, self.content_offset
            )

        # Answer section
        exchange += build_answer_section(
            exchange_data['answer'], self.state, self.content_offset
        )

        # Store in environment
        AIContentStorage.store_content(self.env, 'exchange', name, {
            'title': title, 'slug': slug, 'anchor': anchor_id,
            'docname': self.env.docname, 'lineno': self.lineno,
            'date': self.options.get('date', ''),
            'model': self.options.get('model', ''),
            'source': self.options.get('source', ''),
            'id': self.options.get('id', ''),
        })

        return [exchange]


class AIMessageDirective(SphinxDirective):
    """
    Directive for a single AI message quote/excerpt.

    Usage:
        ```{ai-message} quote-name
        :sender: assistant
        :date: 2024-11-28
        :source: Claude Desktop
        :model: claude-sonnet-4
        :context: Discussion about X

        The quoted message content...
        ```
    """

    has_content = True
    required_arguments = 1  # Quote name
    optional_arguments = 0
    final_argument_whitespace = True

    option_spec: ClassVar[dict[str, Any]] = {
        'sender': directives.unchanged,  # 'human' or 'assistant'
        'date': directives.unchanged,
        'source': directives.unchanged,
        'model': directives.unchanged,
        'context': directives.unchanged,  # Brief context description
        'id': directives.unchanged,
        'class': directives.class_option,
    }

    def run(self) -> list[nodes.Node]:
        """Process the ai-message directive."""
        name = self.arguments[0].strip()
        slug = slugify(name)
        anchor_id = f'ai-message-{slug}'
        title = format_title(name)

        # Get sender (default to assistant)
        sender = self.options.get('sender', 'assistant').lower()
        if sender not in ('human', 'assistant'):
            sender = 'assistant'

        # Build the message node
        message = ai_message_node()
        message['classes'] = ['ai-message', f'ai-message-{sender}', 'ai-generated', 'ai-quote']
        if 'class' in self.options:
            message['classes'].extend(self.options['class'])
        message['ids'] = [anchor_id]
        message['sender'] = sender

        message += build_message_header(name, title, sender, self.options)

        # Sender label
        sender_label = nodes.paragraph(classes=['ai-sender'])
        sender_label += nodes.Text('Human' if sender == 'human' else 'Assistant')
        message += sender_label

        # Message content
        content_container = nodes.container(classes=['ai-content'])
        content_str = '\n'.join(self.content)
        self.state.nested_parse(content_str.split('\n'), self.content_offset, content_container)
        message += content_container

        # Store in environment
        AIContentStorage.store_content(self.env, 'message', name, {
            'title': title, 'slug': slug, 'anchor': anchor_id,
            'docname': self.env.docname, 'lineno': self.lineno, 'sender': sender,
            'date': self.options.get('date', ''),
            'source': self.options.get('source', ''),
            'model': self.options.get('model', ''),
            'context': self.options.get('context', ''),
            'id': self.options.get('id', ''),
        })

        return [message]
