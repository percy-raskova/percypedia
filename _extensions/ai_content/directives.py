"""
AI Content Directives.

Provides directives for embedding AI-generated content in Sphinx documents.
"""

from typing import List

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

from .nodes import ai_chat_node, ai_message_node, ai_exchange_node, ai_question_node, ai_answer_node
from .parser import parse_chat_messages, parse_exchange, format_title, slugify


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

    option_spec = {
        'date': directives.unchanged,
        'source': directives.unchanged,
        'id': directives.unchanged,  # Private, not rendered
        'class': directives.class_option,
    }

    def run(self) -> List[nodes.Node]:
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

        # Store in environment for indexing (exclude private 'id' from public data)
        env = self.env
        if not hasattr(env, 'ai_content_chats'):
            env.ai_content_chats = {}

        env.ai_content_chats[name] = {
            'title': title,
            'slug': slug,
            'anchor': anchor_id,
            'docname': env.docname,
            'lineno': self.lineno,
            'date': self.options.get('date', ''),
            'source': self.options.get('source', ''),
            'id': self.options.get('id', ''),  # Stored but not rendered
            'message_count': len(messages),
        }

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

    option_spec = {
        'date': directives.unchanged,
        'model': directives.unchanged,
        'source': directives.unchanged,
        'id': directives.unchanged,
        'class': directives.class_option,
    }

    def run(self) -> List[nodes.Node]:
        """Process the ai-exchange directive."""
        name = self.arguments[0].strip()
        slug = slugify(name)
        anchor_id = f'ai-exchange-{slug}'
        title = format_title(name)

        # Parse question/answer from content
        content_str = '\n'.join(self.content)
        exchange_data = parse_exchange(content_str)

        if not exchange_data:
            # Fallback: treat entire content as answer with no question
            exchange_data = {
                'question': '',
                'answer': content_str,
            }

        # Build the exchange container
        exchange = ai_exchange_node()
        exchange['classes'] = ['ai-exchange', 'ai-generated']
        if 'class' in self.options:
            exchange['classes'].extend(self.options['class'])
        exchange['ids'] = [anchor_id]

        # Header with title and metadata
        header = nodes.container(classes=['ai-exchange-header'])

        title_para = nodes.paragraph(classes=['ai-exchange-title'])
        title_para += nodes.strong(text=title)
        header += title_para

        # Metadata
        meta_parts = []
        if 'date' in self.options:
            meta_parts.append(self.options['date'])
        if 'model' in self.options:
            meta_parts.append(self.options['model'])
        if 'source' in self.options:
            meta_parts.append(self.options['source'])

        if meta_parts:
            meta_para = nodes.paragraph(classes=['ai-exchange-meta'])
            meta_para += nodes.Text(' • '.join(meta_parts))
            header += meta_para

        # AI badge
        badge = nodes.inline(classes=['ai-badge'])
        badge += nodes.Text('AI Exchange')
        header += badge

        exchange += header

        # Question section
        if exchange_data['question']:
            question_container = ai_question_node()
            question_container['classes'] = ['ai-question']

            q_label = nodes.paragraph(classes=['ai-question-label'])
            q_label += nodes.strong(text='Question')
            question_container += q_label

            q_content = nodes.container(classes=['ai-question-content'])
            q_lines = exchange_data['question'].split('\n')
            self.state.nested_parse(q_lines, self.content_offset, q_content)
            question_container += q_content

            exchange += question_container

        # Answer section
        answer_container = ai_answer_node()
        answer_container['classes'] = ['ai-answer']

        a_label = nodes.paragraph(classes=['ai-answer-label'])
        a_label += nodes.strong(text='Answer')
        answer_container += a_label

        a_content = nodes.container(classes=['ai-answer-content'])
        a_lines = exchange_data['answer'].split('\n')
        self.state.nested_parse(a_lines, self.content_offset, a_content)
        answer_container += a_content

        exchange += answer_container

        # Store in environment
        env = self.env
        if not hasattr(env, 'ai_content_exchanges'):
            env.ai_content_exchanges = {}

        env.ai_content_exchanges[name] = {
            'title': title,
            'slug': slug,
            'anchor': anchor_id,
            'docname': env.docname,
            'lineno': self.lineno,
            'date': self.options.get('date', ''),
            'model': self.options.get('model', ''),
            'source': self.options.get('source', ''),
            'id': self.options.get('id', ''),
        }

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

    option_spec = {
        'sender': directives.unchanged,  # 'human' or 'assistant'
        'date': directives.unchanged,
        'source': directives.unchanged,
        'model': directives.unchanged,
        'context': directives.unchanged,  # Brief context description
        'id': directives.unchanged,
        'class': directives.class_option,
    }

    def run(self) -> List[nodes.Node]:
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

        # Header with metadata
        header = nodes.container(classes=['ai-message-header'])

        # Title (optional - only if it's meaningful)
        if name and not name.startswith('quote-'):
            title_para = nodes.paragraph(classes=['ai-message-title'])
            title_para += nodes.strong(text=title)
            header += title_para

        # Metadata line
        meta_parts = []
        if 'date' in self.options:
            meta_parts.append(self.options['date'])
        if 'model' in self.options:
            meta_parts.append(self.options['model'])
        if 'source' in self.options:
            meta_parts.append(self.options['source'])

        if meta_parts:
            meta_para = nodes.paragraph(classes=['ai-message-meta'])
            meta_para += nodes.Text(' • '.join(meta_parts))
            header += meta_para

        # Context (if provided)
        if 'context' in self.options:
            context_para = nodes.paragraph(classes=['ai-message-context'])
            context_para += nodes.emphasis(text=self.options['context'])
            header += context_para

        # AI badge
        badge = nodes.inline(classes=['ai-badge'])
        badge_text = 'AI Quote' if sender == 'assistant' else 'Human'
        badge += nodes.Text(badge_text)
        header += badge

        message += header

        # Sender label
        sender_label = nodes.paragraph(classes=['ai-sender'])
        sender_label += nodes.Text('Human' if sender == 'human' else 'Assistant')
        message += sender_label

        # Message content
        content_container = nodes.container(classes=['ai-content'])
        content_str = '\n'.join(self.content)
        content_lines = content_str.split('\n')
        self.state.nested_parse(
            content_lines,
            self.content_offset,
            content_container,
        )
        message += content_container

        # Store in environment
        env = self.env
        if not hasattr(env, 'ai_content_messages'):
            env.ai_content_messages = {}

        env.ai_content_messages[name] = {
            'title': title,
            'slug': slug,
            'anchor': anchor_id,
            'docname': env.docname,
            'lineno': self.lineno,
            'sender': sender,
            'date': self.options.get('date', ''),
            'source': self.options.get('source', ''),
            'model': self.options.get('model', ''),
            'context': self.options.get('context', ''),
            'id': self.options.get('id', ''),
        }

        return [message]


class AIArchiveDirective(SphinxDirective):
    """
    Directive to generate an index of all AI content.

    Usage:
        ```{ai-archive}
        :show-dates:
        :type: chats  # or 'exchanges', 'messages', or 'all' (default)
        ```
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    option_spec = {
        'show-dates': directives.flag,
        'type': directives.unchanged,  # 'chats', 'exchanges', 'messages', 'all'
        'class': directives.class_option,
    }

    def run(self) -> List[nodes.Node]:
        """Process the ai-archive directive."""
        env = self.env
        show_dates = 'show-dates' in self.options
        content_type = self.options.get('type', 'all').lower()

        # Main container
        container = nodes.container(classes=['ai-archive-index'])
        if 'class' in self.options:
            container['classes'].extend(self.options['class'])

        # Get content from environment
        chats = getattr(env, 'ai_content_chats', {})
        exchanges = getattr(env, 'ai_content_exchanges', {})
        messages = getattr(env, 'ai_content_messages', {})

        # Build sections based on type filter
        if content_type in ('all', 'chats') and chats:
            container += self._build_section(
                'Conversations', chats, 'chat', show_dates
            )

        if content_type in ('all', 'exchanges') and exchanges:
            container += self._build_section(
                'Exchanges', exchanges, 'exchange', show_dates
            )

        if content_type in ('all', 'messages') and messages:
            container += self._build_section(
                'Quotes', messages, 'message', show_dates
            )

        # If empty, show placeholder
        if len(container.children) == 0:
            para = nodes.paragraph()
            para += nodes.Text('No AI content archived yet.')
            container += para

        return [container]

    def _build_section(
        self,
        title: str,
        items: dict,
        item_type: str,
        show_dates: bool,
    ) -> nodes.section:
        """Build a section for a content type."""
        section = nodes.section(classes=[f'ai-archive-{item_type}s'])

        # Section title
        title_node = nodes.paragraph(classes=['ai-archive-section-title'])
        title_node += nodes.strong(text=title)
        section += title_node

        # Build list
        bullet_list = nodes.bullet_list()

        # Sort by date if available, otherwise by title
        sorted_items = sorted(
            items.items(),
            key=lambda x: x[1].get('date', '') or x[1].get('title', ''),
            reverse=True,  # Most recent first
        )

        for name, data in sorted_items:
            item_node = nodes.list_item()
            para = nodes.paragraph()

            # Create reference
            ref = nodes.reference(
                data.get('title', name),
                data.get('title', name),
                internal=True,
            )
            docname = data.get('docname', '')
            anchor = data.get('anchor', f'ai-{item_type}-{name}')
            ref['refuri'] = f'{docname}.html#{anchor}'
            ref['classes'] = ['ai-ref', f'ai-{item_type}-ref']

            para += ref

            # Add date if requested
            if show_dates and data.get('date'):
                para += nodes.Text(f" ({data['date']})")

            item_node += para
            bullet_list += item_node

        section += bullet_list
        return section
