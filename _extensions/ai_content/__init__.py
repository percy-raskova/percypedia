"""
AI Content Extension for Sphinx.

Provides directives for archiving and displaying AI-generated content
with full transparency and provenance tracking.

Directives:
- {ai-chat}: Full conversation with [human]/[assistant] messages
- {ai-exchange}: Single Q&A pair
- {ai-message}: Single message excerpt
- {ai-archive}: Generate index of all AI content

Roles:
- :ai:chat:`name`: Reference a chat conversation
- :ai:ref:`name`: Generic reference to any AI content
"""

from sphinx.application import Sphinx

from .directives import AIArchiveDirective, AIChatDirective, AIExchangeDirective, AIMessageDirective
from .nodes import (
    ai_answer_node,
    ai_chat_node,
    ai_exchange_node,
    ai_message_node,
    ai_question_node,
    depart_ai_answer_html,
    depart_ai_chat_html,
    depart_ai_exchange_html,
    depart_ai_message_html,
    depart_ai_question_html,
    visit_ai_answer_html,
    visit_ai_chat_html,
    visit_ai_exchange_html,
    visit_ai_message_html,
    visit_ai_question_html,
)
from .roles import ai_chat_role, ai_exchange_role, ai_message_role, ai_ref_role

__version__ = '0.1.0'


def init_ai_content(app: Sphinx) -> None:
    """Initialize AI content storage on builder-inited."""
    env = app.env
    if not hasattr(env, 'ai_content_chats'):
        env.ai_content_chats = {}
    if not hasattr(env, 'ai_content_exchanges'):
        env.ai_content_exchanges = {}
    if not hasattr(env, 'ai_content_messages'):
        env.ai_content_messages = {}


def merge_ai_content(
    app: Sphinx,
    env,
    docnames: list[str],
    other,
) -> None:
    """Merge AI content data from parallel workers.

    Called during parallel builds when worker environments are merged
    into the main environment.

    Args:
        app: Sphinx application instance
        env: Main build environment
        docnames: Document names processed (unused)
        other: Worker's build environment to merge from
    """
    # Merge chats
    if hasattr(other, 'ai_content_chats'):
        if not hasattr(env, 'ai_content_chats'):
            env.ai_content_chats = {}
        env.ai_content_chats.update(other.ai_content_chats)

    # Merge exchanges
    if hasattr(other, 'ai_content_exchanges'):
        if not hasattr(env, 'ai_content_exchanges'):
            env.ai_content_exchanges = {}
        env.ai_content_exchanges.update(other.ai_content_exchanges)

    # Merge messages
    if hasattr(other, 'ai_content_messages'):
        if not hasattr(env, 'ai_content_messages'):
            env.ai_content_messages = {}
        env.ai_content_messages.update(other.ai_content_messages)


def setup(app: Sphinx) -> dict:
    """Initialize the AI content extension."""
    # Configuration values
    app.add_config_value('ai_content_archive_path', 'ai-archive', 'env')
    app.add_config_value('ai_content_badge_text', 'AI Generated', 'env')

    # Register directives
    app.add_directive('ai-chat', AIChatDirective)
    app.add_directive('ai-exchange', AIExchangeDirective)
    app.add_directive('ai-message', AIMessageDirective)
    app.add_directive('ai-archive', AIArchiveDirective)

    # Register roles for cross-referencing
    app.add_role('ai-chat', ai_chat_role)
    app.add_role('ai-exchange', ai_exchange_role)
    app.add_role('ai-message', ai_message_role)
    app.add_role('ai-ref', ai_ref_role)

    # Register custom nodes
    app.add_node(
        ai_chat_node,
        html=(visit_ai_chat_html, depart_ai_chat_html),
    )
    app.add_node(
        ai_message_node,
        html=(visit_ai_message_html, depart_ai_message_html),
    )
    app.add_node(
        ai_exchange_node,
        html=(visit_ai_exchange_html, depart_ai_exchange_html),
    )
    app.add_node(
        ai_question_node,
        html=(visit_ai_question_html, depart_ai_question_html),
    )
    app.add_node(
        ai_answer_node,
        html=(visit_ai_answer_html, depart_ai_answer_html),
    )

    # Event handlers
    app.connect('builder-inited', init_ai_content)
    app.connect('env-merge-info', merge_ai_content)

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
