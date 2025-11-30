"""AI Archive Directive.

Provides the ai-archive directive for generating an index of AI content.
"""

from typing import Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

__all__ = [
    'AIArchiveDirective',
]


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

    option_spec: ClassVar[dict[str, Any]] = {
        'show-dates': directives.flag,
        'type': directives.unchanged,  # 'chats', 'exchanges', 'messages', 'all'
        'class': directives.class_option,
    }

    def run(self) -> list[nodes.Node]:
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
        """Build a section for a content type.

        Args:
            title: Section title
            items: Dict of items to display
            item_type: Type of item ('chat', 'exchange', 'message')
            show_dates: Whether to show dates

        Returns:
            Section node with content list
        """
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
