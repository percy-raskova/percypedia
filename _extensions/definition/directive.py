"""
DefinitionDirective - Renders term definitions as sphinx-design cards.

Usage in MyST Markdown:
    ```{definition} Term Name
    The definition body text...
    ```
"""

from typing import Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.errors import ExtensionError
from sphinx.util.docutils import SphinxDirective

__all__ = [
    'DefinitionDirective',
    'definition_card',
    'depart_definition_card_html',
    'visit_definition_card_html',
]

# CSS class constants (compatible with sphinx-design)
CSS_CARD = 'sd-card'
CSS_SHADOW = 'sd-shadow-sm'
CSS_DEFINITION_CARD = 'definition-card'
CSS_CARD_HEADER = 'sd-card-header'
CSS_CARD_TITLE = 'sd-card-title'
CSS_CARD_BODY = 'sd-card-body'
CSS_CARD_FOOTER = 'sd-card-footer'

# Anchor ID prefix for term definitions
TERM_ANCHOR_PREFIX = 'term-'


class definition_card(nodes.General, nodes.Element):
    """Custom node for definition cards."""
    pass


class DefinitionDirective(SphinxDirective):
    """
    Directive for inline term definitions.

    Renders as a sphinx-design card and registers the term with
    Sphinx's glossary domain for {term} cross-referencing.
    """

    has_content = True
    required_arguments = 1  # Term name
    optional_arguments = 0
    final_argument_whitespace = True  # Allow spaces in term name

    option_spec: ClassVar[dict[str, Any]] = {
        'class': directives.class_option,
    }

    def run(self) -> list[nodes.Node]:
        """Process the definition directive."""
        # Validate term name
        term_name = self.arguments[0].strip() if self.arguments else ''
        if not term_name:
            raise ExtensionError(
                f"Definition directive requires a term name at {self.get_location()}"
            )

        # Validate content
        if not self.content or not any(line.strip() for line in self.content):
            raise ExtensionError(
                f"Definition for '{term_name}' has no content at {self.get_location()}"
            )

        # Create anchor ID
        anchor_id = f"{TERM_ANCHOR_PREFIX}{nodes.make_id(term_name)}"

        # Build card structure
        # Outer container with definition-card class
        card = definition_card()
        card['classes'] = [CSS_CARD, CSS_SHADOW, CSS_DEFINITION_CARD]
        if 'class' in self.options:
            card['classes'].extend(self.options['class'])
        card['ids'] = [anchor_id]

        # Card header with term name
        header = nodes.container(classes=[CSS_CARD_HEADER])
        title = nodes.paragraph(classes=[CSS_CARD_TITLE])
        title_text = nodes.strong(text=term_name)
        title += title_text
        header += title
        card += header

        # Card body with parsed content
        body = nodes.container(classes=[CSS_CARD_BODY])

        # Parse the content as nested RST/MyST
        self.state.nested_parse(
            self.content,
            self.content_offset,
            body,
        )
        card += body

        # Card footer with link to glossary (will be added in Sprint 5)
        footer = nodes.container(classes=[CSS_CARD_FOOTER])
        # Placeholder - footer link added later
        card += footer

        # Store definition info in env dict (for backward compat)
        env = self.env
        if not hasattr(env, 'definition_all_definitions'):
            env.definition_all_definitions = {}

        definition_text = '\n'.join(self.content)
        env.definition_all_definitions[term_name.lower()] = {
            'term': term_name,
            'docname': env.docname,
            'lineno': self.lineno,
            'anchor': anchor_id,
            'content': definition_text,
        }

        # Also add to collector for glossary generation
        if hasattr(env, 'definition_collector') and env.definition_collector is not None:
            from .collector import DuplicateTermError
            try:
                env.definition_collector.add_definition(
                    term=term_name,
                    definition=definition_text,
                    docname=env.docname,
                    lineno=self.lineno,
                    anchor=anchor_id,
                )
            except DuplicateTermError as e:
                raise ExtensionError(str(e)) from e

        return [card]


def visit_definition_card_html(self, node: definition_card) -> None:
    """Render definition_card as HTML."""
    classes = ' '.join(node.get('classes', []))
    ids = ' '.join(f'id="{id}"' for id in node.get('ids', []))
    self.body.append(f'<div class="{classes}" {ids}>')


def depart_definition_card_html(self, _node: definition_card) -> None:
    """Close definition_card HTML."""
    self.body.append('</div>')
