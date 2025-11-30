"""
Tests for GlossaryGenerator - Sprint 4: Glossary Generation.

These tests verify the unified glossary page generation.
"""

import pytest

from definition.collector import DefinitionsCollector
from definition.generator import GlossaryGenerator


@pytest.fixture
def collector_with_definitions():
    """Create a collector with sample definitions."""
    collector = DefinitionsCollector()

    definitions = [
        ('Labor Aristocracy', 'The privileged stratum...', 'theory/labor-aristocracy', 10),
        ('Super-profits', 'Excess profits from imperialism...', 'theory/imperialism', 20),
        ('Democratic Centralism', 'Organizational principle...', 'theory/organization', 30),
    ]

    for term, definition, docname, lineno in definitions:
        collector.add_definition(
            term=term,
            definition=definition,
            docname=docname,
            lineno=lineno,
            anchor=f'term-{term.lower().replace(" ", "-")}',
        )

    return collector


class TestGlossaryGenerator:
    """Test Group 4: Auto-Generated Glossary."""

    def test_generate_entries_returns_all_inline_definitions(self, collector_with_definitions):
        """
        Given: Inline definitions for "Term A", "Term B", "Term C"
        When: generate_entries is called
        Then: All three terms appear in the entries
        """
        generator = GlossaryGenerator(collector_with_definitions)
        entries = generator.generate_entries()

        assert len(entries) == 3
        terms = [e['term'] for e in entries]
        assert 'Labor Aristocracy' in terms
        assert 'Super-profits' in terms
        assert 'Democratic Centralism' in terms

    def test_glossary_entries_sorted_alphabetically(self, collector_with_definitions):
        """
        Given: Definitions for various terms
        When: generate_entries is called
        Then: Entries are sorted alphabetically
        """
        generator = GlossaryGenerator(collector_with_definitions)
        entries = generator.generate_entries()

        terms = [e['term'] for e in entries]
        assert terms == sorted(terms, key=str.lower)

    def test_glossary_entry_includes_source_document(self, collector_with_definitions):
        """
        Given: "Labor Aristocracy" defined in theory/labor-aristocracy.md
        When: generate_entries is called
        Then: Entry includes source_doc = 'theory/labor-aristocracy'
        """
        generator = GlossaryGenerator(collector_with_definitions)
        entries = generator.generate_entries()

        labor_entry = next(e for e in entries if e['term'] == 'Labor Aristocracy')
        assert labor_entry['source_doc'] == 'theory/labor-aristocracy'
        assert labor_entry['source_type'] == 'inline'

    def test_glossary_entry_includes_definition_text(self, collector_with_definitions):
        """
        Given: "Labor Aristocracy" with definition "The privileged stratum..."
        When: generate_entries is called
        Then: Entry shows the definition text
        """
        generator = GlossaryGenerator(collector_with_definitions)
        entries = generator.generate_entries()

        labor_entry = next(e for e in entries if e['term'] == 'Labor Aristocracy')
        assert 'privileged stratum' in labor_entry['definition']


class TestMergedGlossary:
    """Test merging inline definitions with standard glossary."""

    def test_glossary_contains_standard_glossary_entries(self, collector_with_definitions):
        """
        Given: Standard glossary.md with {glossary} directive defining "Term X"
        And: Inline definition for "Labor Aristocracy"
        When: generate_entries is called with std_terms
        Then: Both terms appear
        """
        generator = GlossaryGenerator(collector_with_definitions)

        # Mock standard glossary data (2-tuple format for Sphinx 7+)
        std_terms = {
            'entryism': ('glossary', 'term-entryism'),
            'opsec': ('glossary', 'term-opsec'),
        }

        entries = generator.generate_entries(std_terms)

        terms = [e['term'] for e in entries]
        # Inline definitions
        assert 'Labor Aristocracy' in terms
        # Standard glossary (note: title case from normalized key)
        assert 'Entryism' in terms
        assert 'Opsec' in terms  # title() from 'opsec'

    def test_standard_entries_marked_as_standard_type(self, collector_with_definitions):
        """
        Given: Standard glossary term
        When: Entry is generated
        Then: source_type is 'standard'
        """
        generator = GlossaryGenerator(collector_with_definitions)

        std_terms = {
            'entryism': ('glossary', 'term-entryism'),
        }

        entries = generator.generate_entries(std_terms)

        entryism = next(e for e in entries if e['term'] == 'Entryism')
        assert entryism['source_type'] == 'standard'


class TestHtmlGeneration:
    """Test HTML output generation."""

    def test_generate_html_page_contains_glossary_title(self, collector_with_definitions):
        """
        Given: Generator with title "Glossary"
        When: generate_html_page is called
        Then: Output contains <h1>Glossary</h1>
        """
        generator = GlossaryGenerator(
            collector_with_definitions,
            glossary_title='Glossary',
        )
        entries = generator.generate_entries()
        html = generator.generate_html_page(entries)

        assert '<h1>Glossary</h1>' in html

    def test_generate_html_page_contains_dl_element(self, collector_with_definitions):
        """
        Given: Definitions
        When: generate_html_page is called
        Then: Output contains <dl class="glossary">
        """
        generator = GlossaryGenerator(collector_with_definitions)
        entries = generator.generate_entries()
        html = generator.generate_html_page(entries)

        assert '<dl class="glossary' in html

    def test_generate_html_page_contains_term_anchors(self, collector_with_definitions):
        """
        Given: Definition with anchor "term-labor-aristocracy"
        When: generate_html_page is called
        Then: Output contains <dt id="term-labor-aristocracy">
        """
        generator = GlossaryGenerator(collector_with_definitions)
        entries = generator.generate_entries()
        html = generator.generate_html_page(entries)

        assert 'id="term-labor-aristocracy"' in html

    def test_generate_html_page_contains_source_links(self, collector_with_definitions):
        """
        Given: Inline definition from theory/labor-aristocracy
        When: generate_html_page is called
        Then: Output contains link to source document
        """
        generator = GlossaryGenerator(collector_with_definitions)
        entries = generator.generate_entries()
        html = generator.generate_html_page(entries)

        assert 'Defined in:' in html
        assert 'theory/labor-aristocracy' in html


class TestPageTupleGeneration:
    """Test page tuple for Sphinx html-collect-pages."""

    def test_generate_page_tuple_returns_correct_format(self, collector_with_definitions):
        """
        Given: Generator
        When: generate_page_tuple is called
        Then: Returns (pagename, context_dict, template_name)
        """
        generator = GlossaryGenerator(
            collector_with_definitions,
            glossary_path='glossary',
        )
        entries = generator.generate_entries()
        result = generator.generate_page_tuple(entries)

        pagename, context, template = result
        assert pagename == 'glossary'
        assert 'title' in context
        assert 'body' in context
        assert template == 'page.html'

    def test_page_context_contains_title(self, collector_with_definitions):
        """
        Given: Generator with title
        When: generate_page_tuple is called
        Then: Context contains title
        """
        generator = GlossaryGenerator(
            collector_with_definitions,
            glossary_title='My Glossary',
        )
        entries = generator.generate_entries()
        _, context, _ = generator.generate_page_tuple(entries)

        assert context['title'] == 'My Glossary'

    def test_page_context_contains_html_body(self, collector_with_definitions):
        """
        Given: Generator with definitions
        When: generate_page_tuple is called
        Then: Context body contains HTML with definitions
        """
        generator = GlossaryGenerator(collector_with_definitions)
        entries = generator.generate_entries()
        _, context, _ = generator.generate_page_tuple(entries)

        assert '<dl' in context['body']
        assert 'Labor Aristocracy' in context['body']
