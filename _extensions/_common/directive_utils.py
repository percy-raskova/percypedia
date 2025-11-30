"""Shared directive utilities for Sphinx extensions.

Provides helper functions for building common directive structures
like headers, content sections, and environment storage management.

This is the single source of truth for directive patterns.
"""

from collections.abc import Callable
from typing import Any

from docutils import nodes

__all__ = [
    'build_content_section',
    'build_header_node',
    'ensure_env_storage',
]


def build_header_node(
    css_prefix: str,
    title: str,
    options: dict[str, Any],
    badge_text: str,
    meta_keys: tuple[str, ...] = ('date', 'model', 'source'),
    *,
    include_title: bool = True,
    context_key: str | None = None,
) -> nodes.container:
    """Build a standardized header with title, metadata, and badge.

    Creates a consistent header structure used by multiple directives:
    - Title (optional)
    - Metadata line (from options dict)
    - Context line (optional)
    - Badge

    Args:
        css_prefix: CSS class prefix (e.g., 'ai-chat', 'ai-exchange')
        title: Title text to display
        options: Directive options dict
        badge_text: Text for the badge (e.g., 'AI Chat', 'AI Exchange')
        meta_keys: Option keys to include in metadata line
        include_title: Whether to include the title (default True)
        context_key: Option key for context line (default None)

    Returns:
        A container node with the header structure

    Example:
        >>> header = build_header_node(
        ...     css_prefix='ai-exchange',
        ...     title='My Exchange',
        ...     options={'date': '2024-01-01', 'model': 'claude-sonnet-4'},
        ...     badge_text='AI Exchange',
        ... )
    """
    header = nodes.container(classes=[f'{css_prefix}-header'])

    # Title (optional)
    if include_title and title:
        title_para = nodes.paragraph(classes=[f'{css_prefix}-title'])
        title_para += nodes.strong(text=title)
        header += title_para

    # Metadata line
    meta_parts = [options[k] for k in meta_keys if k in options and options[k]]
    if meta_parts:
        meta_para = nodes.paragraph(classes=[f'{css_prefix}-meta'])
        meta_para += nodes.Text(' • '.join(meta_parts))
        header += meta_para

    # Context line (optional)
    if context_key and context_key in options:
        context_para = nodes.paragraph(classes=[f'{css_prefix}-context'])
        context_para += nodes.emphasis(text=options[context_key])
        header += context_para

    # Badge
    badge = nodes.inline(classes=['ai-badge'])
    badge += nodes.Text(badge_text)
    header += badge

    return header


def build_content_section(
    content_text: str,
    css_class: str,
    label: str,
    state: Any,
    content_offset: int,
    node_class: type = nodes.container,
) -> nodes.Element:
    """Build a labeled content section with parsed markup.

    Creates a section with:
    - Label (bold text)
    - Nested parsed content

    Args:
        content_text: Raw text content to parse
        css_class: CSS class for the container
        label: Label text (e.g., 'Question', 'Answer')
        state: Directive state for nested parsing
        content_offset: Content offset for nested parsing
        node_class: Node class for the container (default: nodes.container)

    Returns:
        A node containing the labeled section

    Example:
        >>> section = build_content_section(
        ...     content_text='What is Python?',
        ...     css_class='ai-question',
        ...     label='Question',
        ...     state=self.state,
        ...     content_offset=self.content_offset,
        ... )
    """
    container = node_class()
    container['classes'] = [css_class]

    # Label
    label_para = nodes.paragraph(classes=[f'{css_class}-label'])
    label_para += nodes.strong(text=label)
    container += label_para

    # Content
    content_container = nodes.container(classes=[f'{css_class}-content'])
    state.nested_parse(content_text.split('\n'), content_offset, content_container)
    container += content_container

    return container


def ensure_env_storage(
    env: Any,
    attr_name: str,
    factory: type | Callable[[], Any] = dict,
) -> Any:
    """Get or create a storage attribute on the environment.

    Ensures the attribute exists on env, creating it with factory() if needed.

    Args:
        env: Sphinx build environment
        attr_name: Attribute name to get/create
        factory: Callable that returns the initial value (default: dict)

    Returns:
        The storage object (existing or newly created)

    Example:
        >>> storage = ensure_env_storage(env, 'my_extension_data')
        >>> storage['key'] = value
    """
    if not hasattr(env, attr_name):
        setattr(env, attr_name, factory())
    return getattr(env, attr_name)
