"""Node building utilities for AI content directives.

Provides helper functions for building common node structures
used across AI content directives.
"""

from typing import Any

from docutils import nodes

from _common.directive_utils import build_content_section, build_header_node
from .nodes import ai_answer_node, ai_question_node

__all__ = [
    'build_answer_section',
    'build_exchange_header',
    'build_message_header',
    'build_question_section',
]


def build_exchange_header(
    title: str, options: dict[str, Any], badge_text: str = 'AI Exchange'
) -> nodes.container:
    """Build header with title, metadata, and AI badge for exchange directives.

    Args:
        title: Title text to display
        options: Directive options dict (may contain 'date', 'model', 'source')
        badge_text: Text for the badge

    Returns:
        Container node with header structure
    """
    return build_header_node(
        css_prefix='ai-exchange',
        title=title,
        options=options,
        badge_text=badge_text,
        meta_keys=('date', 'model', 'source'),
    )


def build_question_section(question_text: str, state: Any, content_offset: int) -> ai_question_node:
    """Build a question section with parsed content.

    Args:
        question_text: Raw question text to parse
        state: Directive state for nested parsing
        content_offset: Content offset for parsing

    Returns:
        Question node with label and content
    """
    return build_content_section(
        content_text=question_text,
        css_class='ai-question',
        label='Question',
        state=state,
        content_offset=content_offset,
        node_class=ai_question_node,
    )


def build_answer_section(answer_text: str, state: Any, content_offset: int) -> ai_answer_node:
    """Build an answer section with parsed content.

    Args:
        answer_text: Raw answer text to parse
        state: Directive state for nested parsing
        content_offset: Content offset for parsing

    Returns:
        Answer node with label and content
    """
    return build_content_section(
        content_text=answer_text,
        css_class='ai-answer',
        label='Answer',
        state=state,
        content_offset=content_offset,
        node_class=ai_answer_node,
    )


def build_message_header(
    name: str, title: str, sender: str, options: dict[str, Any]
) -> nodes.container:
    """Build header with title, metadata, context, and AI badge for message directive.

    Args:
        name: Message name (used to determine if title should show)
        title: Title text to display
        sender: Sender type ('human' or 'assistant')
        options: Directive options dict

    Returns:
        Container node with header structure
    """
    header = nodes.container(classes=['ai-message-header'])

    # Title (optional - only if it's meaningful)
    if name and not name.startswith('quote-'):
        title_para = nodes.paragraph(classes=['ai-message-title'])
        title_para += nodes.strong(text=title)
        header += title_para

    # Metadata line
    meta_parts = [options[k] for k in ('date', 'model', 'source') if k in options]
    if meta_parts:
        meta_para = nodes.paragraph(classes=['ai-message-meta'])
        meta_para += nodes.Text(' • '.join(meta_parts))
        header += meta_para

    # Context (if provided)
    if 'context' in options:
        context_para = nodes.paragraph(classes=['ai-message-context'])
        context_para += nodes.emphasis(text=options['context'])
        header += context_para

    # AI badge
    badge = nodes.inline(classes=['ai-badge'])
    badge += nodes.Text('AI Quote' if sender == 'assistant' else 'Human')
    header += badge

    return header
