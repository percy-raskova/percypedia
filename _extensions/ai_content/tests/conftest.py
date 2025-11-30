"""
Shared test fixtures for ai_content extension tests.

This module provides factory functions and fixtures for creating mock
directive objects, reducing duplication across test files.

Uses the common testing utilities from _common.testing with ai_content-specific
defaults pre-configured.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

from _common.testing import (
    make_mock_directive as _make_mock_directive,
    make_mock_inliner as _make_mock_inliner,
)


# Default env attributes for ai_content directives
AI_CONTENT_ENV_DEFAULTS = {
    'ai_content_chats': {},
    'ai_content_exchanges': {},
    'ai_content_messages': {},
}


def make_mock_directive(
    directive_class,
    arguments: list | None = None,
    content: list | None = None,
    options: dict | None = None,
    docname: str = 'test-doc',
    lineno: int = 10,
    content_offset: int = 0,
    env_attrs: dict | None = None,
):
    """
    Factory function to create mock directive instances for ai_content tests.

    Thin wrapper around _common.testing.make_mock_directive that adds
    ai_content-specific environment defaults (chats, exchanges, messages dicts).

    Args:
        directive_class: The directive class to mock (for spec)
        arguments: List of directive arguments (default: empty)
        content: List of content lines (default: empty)
        options: Dict of directive options (default: empty)
        docname: The docname for env (default: 'test-doc')
        lineno: Line number (default: 10)
        content_offset: Content offset (default: 0)
        env_attrs: Additional attributes for env (merged with ai_content defaults)

    Returns:
        A MagicMock configured as a mock directive
    """
    # Merge ai_content defaults with any custom env_attrs
    all_env_attrs = {**AI_CONTENT_ENV_DEFAULTS}
    if env_attrs:
        all_env_attrs.update(env_attrs)

    return _make_mock_directive(
        directive_class=directive_class,
        arguments=arguments,
        content=content,
        options=options,
        docname=docname,
        lineno=lineno,
        content_offset=content_offset,
        env_attrs=all_env_attrs,
    )


def make_mock_inliner(
    chats: dict | None = None,
    exchanges: dict | None = None,
    messages: dict | None = None,
):
    """
    Factory function to create mock inliner for ai_content role tests.

    Thin wrapper around _common.testing.make_mock_inliner that provides
    a domain-specific API with named parameters for chats, exchanges, messages.

    Args:
        chats: Dict of chat entries for env
        exchanges: Dict of exchange entries for env
        messages: Dict of message entries for env

    Returns:
        A MagicMock configured as a mock inliner
    """
    env_attrs = {
        'ai_content_chats': chats or {},
        'ai_content_exchanges': exchanges or {},
        'ai_content_messages': messages or {},
    }
    return _make_mock_inliner(env_attrs=env_attrs)


# Common content patterns for testing
SAMPLE_CHAT_CONTENT = [
    '[human]',
    'How do I use Azure?',
    '',
    '[assistant]',
    'Azure is a cloud platform...',
]

SAMPLE_EXCHANGE_CONTENT = [
    'What is the Y combinator?',
    '---',
    'The Y combinator is a fixed-point combinator...',
]

SAMPLE_MESSAGE_CONTENT = [
    'This is a quoted AI response about dialectics.',
]


def make_archive_directive(
    options: dict | None = None,
    env_attrs: dict | None = None,
    docname: str = 'ai-archive/index',
):
    """
    Factory function specifically for AIArchiveDirective mocks.

    The archive directive has a special requirement: its _build_section method
    must call the real implementation, not return a MagicMock. This factory
    handles that wiring.

    Args:
        options: Dict of directive options (default: empty)
        env_attrs: Additional env attrs (merged with SAMPLE_ARCHIVE_ENV)
        docname: The docname for env (default: 'ai-archive/index')

    Returns:
        A MagicMock configured for archive directive testing
    """
    from ai_content.directives import AIArchiveDirective

    directive = MagicMock(spec=AIArchiveDirective)
    directive.arguments = []
    directive.content = []
    directive.content_offset = 0
    directive.lineno = 10
    directive.options = options or {}

    # Merge default archive env with any custom attrs
    all_env_attrs = {'docname': docname}
    all_env_attrs.update(SAMPLE_ARCHIVE_ENV)
    if env_attrs:
        all_env_attrs.update(env_attrs)

    directive.env = SimpleNamespace(**all_env_attrs)
    directive.state = MagicMock()

    # Wire up _build_section to call the real implementation
    # MagicMock returns MagicMock which docutils nodes ignore, so we need
    # to call the actual method with our mock directive as self
    directive._build_section = lambda *args: AIArchiveDirective._build_section(directive, *args)

    return directive


# Sample environment data for archive tests
SAMPLE_ARCHIVE_ENV = {
    'ai_content_chats': {
        'chat-1': {
            'title': 'Chat One',
            'slug': 'chat-1',
            'anchor': 'ai-chat-chat-1',
            'docname': 'ai-archive/chats',
            'date': '2024-11-01',
        },
        'chat-2': {
            'title': 'Chat Two',
            'slug': 'chat-2',
            'anchor': 'ai-chat-chat-2',
            'docname': 'ai-archive/chats',
            'date': '2024-11-15',
        },
    },
    'ai_content_exchanges': {
        'exchange-1': {
            'title': 'Exchange One',
            'slug': 'exchange-1',
            'anchor': 'ai-exchange-exchange-1',
            'docname': 'theory/article',
            'date': '2024-10-20',
        },
    },
    'ai_content_messages': {
        'message-1': {
            'title': 'Message One',
            'slug': 'message-1',
            'anchor': 'ai-message-message-1',
            'docname': 'theory/quotes',
            'date': '2024-09-15',
        },
    },
}
