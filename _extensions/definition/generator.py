"""
GlossaryGenerator - Generates the unified glossary page.

Creates a virtual glossary page that merges inline {definition} entries
with standard {glossary} entries.
"""

from collections.abc import Iterator
from typing import Any

from sphinx.application import Sphinx

from .collector import DefinitionsCollector

__all__ = [
    'GlossaryGenerator',
    'collect_glossary_pages',
]

# Default configuration values
DEFAULT_GLOSSARY_PATH = 'glossary'
DEFAULT_GLOSSARY_TITLE = 'Glossary'
DEFAULT_TEMPLATE = 'page.html'

# Source type constants
SOURCE_TYPE_INLINE = 'inline'
SOURCE_TYPE_STANDARD = 'standard'

# CSS class for glossary definition list
CSS_GLOSSARY = 'glossary definition-glossary'
CSS_DEFINITION_SOURCE = 'definition-source'


class GlossaryGenerator:
    """Generates the merged glossary page."""

    def __init__(
        self,
        collector: DefinitionsCollector,
        glossary_path: str = DEFAULT_GLOSSARY_PATH,
        glossary_title: str = DEFAULT_GLOSSARY_TITLE,
    ):
        """
        Initialize the generator.

        Args:
            collector: The definitions collector with inline definitions
            glossary_path: Output path for glossary (without extension)
            glossary_title: Title for the glossary page
        """
        self.collector = collector
        self.glossary_path = glossary_path
        self.glossary_title = glossary_title

    def generate_entries(
        self,
        std_terms: dict[str, tuple] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Generate combined glossary entries.

        Args:
            std_terms: Standard glossary terms from env.domaindata['std']['terms']
                      Format: {term_normalized: (docname, labelid, term_text)}

        Returns:
            List of entry dicts sorted alphabetically, each containing:
            - term: Display term
            - definition: Definition text
            - source_doc: Document where defined (for inline)
            - source_type: 'inline' or 'standard'
            - anchor: HTML anchor ID
        """
        entries = []

        # Add inline definitions
        for entry in self.collector.get_all_definitions():
            entries.append({
                'term': entry.term,
                'definition': entry.definition,
                'source_doc': entry.docname,
                'source_type': SOURCE_TYPE_INLINE,
                'anchor': entry.anchor,
            })

        # Add standard glossary terms (if provided and not duplicates)
        # std_terms format: {term_normalized: (docname, labelid)}
        if std_terms:
            inline_terms = {e['term'].lower() for e in entries}
            for normalized, data in std_terms.items():
                if normalized not in inline_terms:
                    # Handle both old (3-tuple) and current (2-tuple) formats
                    if len(data) == 3:
                        docname, anchor, term_text = data
                    else:
                        docname, anchor = data
                        # Reconstruct display text from normalized key
                        term_text = normalized.title()
                    entries.append({
                        'term': term_text,
                        'definition': '',  # Standard glossary definitions not accessible here
                        'source_doc': docname,
                        'source_type': SOURCE_TYPE_STANDARD,
                        'anchor': anchor,
                    })

        # Sort alphabetically
        entries.sort(key=lambda e: e['term'].lower())
        return entries

    def generate_html_page(
        self,
        entries: list[dict[str, Any]],
        base_url: str = '',
    ) -> str:
        """
        Generate HTML content for the glossary page.

        Args:
            entries: List of entry dicts from generate_entries()
            base_url: Base URL for relative links

        Returns:
            HTML string for the glossary page body
        """
        html_parts = [
            f'<h1>{self.glossary_title}</h1>',
            f'<dl class="{CSS_GLOSSARY}">',
        ]

        for entry in entries:
            term = entry['term']
            anchor = entry['anchor']
            definition = entry['definition']
            source_doc = entry['source_doc']
            source_type = entry['source_type']

            # Term with anchor
            html_parts.append(f'<dt id="{anchor}">{term}</dt>')

            # Definition body
            dd_content = []
            if definition:
                dd_content.append(f'<p>{definition}</p>')

            # Source link for inline definitions
            if source_type == SOURCE_TYPE_INLINE:
                source_link = f'{base_url}{source_doc}.html#{anchor}'
                dd_content.append(
                    f'<p class="{CSS_DEFINITION_SOURCE}">'
                    f'<em>Defined in: <a href="{source_link}">{source_doc}</a></em>'
                    f'</p>'
                )

            html_parts.append(f'<dd>{"".join(dd_content)}</dd>')

        html_parts.append('</dl>')
        return '\n'.join(html_parts)

    def generate_page_tuple(
        self,
        entries: list[dict[str, Any]],
    ) -> tuple[str, dict[str, Any], str]:
        """
        Generate page tuple for html-collect-pages event.

        Returns:
            Tuple of (pagename, context, templatename)
        """
        html_body = self.generate_html_page(entries)

        context = {
            'title': self.glossary_title,
            'body': html_body,
        }

        return (self.glossary_path, context, DEFAULT_TEMPLATE)


def collect_glossary_pages(app: Sphinx) -> Iterator[tuple[str, dict[str, Any], str]]:
    """
    Event handler for html-collect-pages.

    Generates the unified glossary page.
    """
    env = app.env

    # Get collector from env
    collector = getattr(env, 'definition_collector', None)
    if collector is None:
        return

    # Get standard glossary terms
    std_domain = env.get_domain('std')
    std_terms = std_domain.data.get('terms', {})

    # Create generator
    generator = GlossaryGenerator(
        collector=collector,
        glossary_path=app.config.definition_glossary_path,
        glossary_title='Glossary',
    )

    # Generate entries
    entries = generator.generate_entries(std_terms)

    if entries:
        yield generator.generate_page_tuple(entries)
