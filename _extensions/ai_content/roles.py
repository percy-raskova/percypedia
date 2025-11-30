"""
AI Content Cross-Reference Roles.

Provides roles for referencing AI content across documents:
- :ai:chat:`name` - Reference a chat conversation
- :ai:exchange:`name` - Reference an exchange
- :ai:message:`name` - Reference a message quote
- :ai:ref:`name` - Generic reference (searches all types)
"""

from typing import Tuple, List

from docutils import nodes
from docutils.parsers.rst.states import Inliner


def make_ai_reference(
    content_type: str,
    storage_attr: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: Inliner,
) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
    """
    Create a reference node for AI content.

    Args:
        content_type: Type of content ('chat', 'exchange', 'message')
        storage_attr: Environment attribute name (e.g., 'ai_content_chats')
        rawtext: Raw role text
        text: Parsed text (the reference name)
        lineno: Line number
        inliner: Inliner object

    Returns:
        Tuple of (nodes, messages)
    """
    env = inliner.document.settings.env
    storage = getattr(env, storage_attr, {})

    # Look up the content
    if text in storage:
        content_data = storage[text]
        title = content_data.get('title', text)
        anchor = content_data.get('anchor', f'ai-{content_type}-{text}')
        docname = content_data.get('docname', '')

        # Create reference node
        ref_node = nodes.reference(rawtext, title, internal=True)
        ref_node['refuri'] = f'{docname}.html#{anchor}'
        ref_node['classes'] = ['ai-ref', f'ai-{content_type}-ref']

        return [ref_node], []
    else:
        # Content not found - create a problematic reference
        msg = inliner.reporter.warning(
            f'AI {content_type} "{text}" not found',
            line=lineno,
        )
        prb = nodes.problematic(rawtext, rawtext)
        return [prb], [msg]


def ai_chat_role(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: Inliner,
    options: dict = None,
    content: list = None,
) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
    """Role for :ai:chat:`name` references."""
    return make_ai_reference(
        'chat', 'ai_content_chats', rawtext, text, lineno, inliner
    )


def ai_exchange_role(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: Inliner,
    options: dict = None,
    content: list = None,
) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
    """Role for :ai:exchange:`name` references."""
    return make_ai_reference(
        'exchange', 'ai_content_exchanges', rawtext, text, lineno, inliner
    )


def ai_message_role(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: Inliner,
    options: dict = None,
    content: list = None,
) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
    """Role for :ai:message:`name` references."""
    return make_ai_reference(
        'message', 'ai_content_messages', rawtext, text, lineno, inliner
    )


def ai_ref_role(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: Inliner,
    options: dict = None,
    content: list = None,
) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
    """
    Generic role for :ai:ref:`name` references.

    Searches chats, exchanges, and messages in that order.
    """
    env = inliner.document.settings.env

    # Search in order: chats, exchanges, messages
    search_order = [
        ('chat', 'ai_content_chats'),
        ('exchange', 'ai_content_exchanges'),
        ('message', 'ai_content_messages'),
    ]

    for content_type, storage_attr in search_order:
        storage = getattr(env, storage_attr, {})
        if text in storage:
            return make_ai_reference(
                content_type, storage_attr, rawtext, text, lineno, inliner
            )

    # Not found anywhere
    msg = inliner.reporter.warning(
        f'AI content "{text}" not found in chats, exchanges, or messages',
        line=lineno,
    )
    prb = nodes.problematic(rawtext, rawtext)
    return [prb], [msg]
