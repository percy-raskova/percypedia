"""
Tests for DefinitionsCollector - Sprint 2 & 3: Term Registration & Duplicate Detection.

These tests verify term storage, retrieval, and duplicate detection.
"""

import pytest

from definition.collector import (
    DefinitionEntry,
    DefinitionsCollector,
    DuplicateTermError,
)


class TestDefinitionsCollector:
    """Test basic collector functionality."""

    def test_add_single_definition(self):
        """
        Given: An empty collector
        When: A definition is added
        Then: Definition is stored and retrievable
        """
        collector = DefinitionsCollector()

        collector.add_definition(
            term='Labor Aristocracy',
            definition='The privileged stratum...',
            docname='theory/labor-aristocracy',
            lineno=10,
            anchor='term-labor-aristocracy',
        )

        assert len(collector) == 1
        assert 'labor aristocracy' in collector
        entry = collector.get_definition('Labor Aristocracy')
        assert entry.term == 'Labor Aristocracy'
        assert entry.docname == 'theory/labor-aristocracy'

    def test_add_multiple_different_definitions(self):
        """
        Given: A collector with one definition
        When: Different definitions are added
        Then: All definitions are stored
        """
        collector = DefinitionsCollector()

        terms = [
            ('Term One', 'theory/concepts', 10),
            ('Term Two', 'theory/concepts', 20),
            ('Term Three', 'polemics/intro', 5),
        ]

        for term, docname, lineno in terms:
            collector.add_definition(
                term=term,
                definition=f'Definition of {term}',
                docname=docname,
                lineno=lineno,
                anchor=f'term-{term.lower().replace(" ", "-")}',
            )

        assert len(collector) == 3

    def test_get_all_definitions_sorted(self):
        """
        Given: Definitions added in random order
        When: get_all_definitions is called
        Then: Returns definitions sorted alphabetically
        """
        collector = DefinitionsCollector()

        # Add in non-alphabetical order
        for term in ['Zebra', 'Apple', 'Mango']:
            collector.add_definition(
                term=term,
                definition=f'{term} definition',
                docname='test',
                lineno=1,
                anchor=f'term-{term.lower()}',
            )

        result = collector.get_all_definitions()
        terms = [e.term for e in result]

        assert terms == ['Apple', 'Mango', 'Zebra']


class TestDuplicateDetection:
    """Test Group 3: Duplicate Detection."""

    def test_duplicate_inline_definitions_raises_error(self):
        """
        Given: "Labor Aristocracy" defined in theory/labor-aristocracy.md
        And: "Labor Aristocracy" defined again in polemics/imperialism.md
        When: Second definition is added
        Then: DuplicateTermError raised with both locations
        """
        collector = DefinitionsCollector()

        # First definition
        collector.add_definition(
            term='Labor Aristocracy',
            definition='First definition',
            docname='theory/labor-aristocracy',
            lineno=15,
            anchor='term-labor-aristocracy',
        )

        # Second definition - should raise
        with pytest.raises(DuplicateTermError) as exc_info:
            collector.add_definition(
                term='Labor Aristocracy',
                definition='Second definition',
                docname='polemics/imperialism',
                lineno=42,
                anchor='term-labor-aristocracy',
            )

        error = exc_info.value
        assert error.term == 'Labor Aristocracy'
        assert 'theory/labor-aristocracy:15' in error.locations
        assert 'polemics/imperialism:42' in error.locations

    def test_case_insensitive_duplicates(self):
        """
        Given: "Labor Aristocracy" defined inline
        And: "labor aristocracy" defined inline (different case)
        When: Second definition is added
        Then: DuplicateTermError raised (case-insensitive by default)
        """
        collector = DefinitionsCollector(case_sensitive=False)

        collector.add_definition(
            term='Labor Aristocracy',
            definition='First',
            docname='doc1',
            lineno=1,
            anchor='term-labor-aristocracy',
        )

        with pytest.raises(DuplicateTermError):
            collector.add_definition(
                term='labor aristocracy',  # Different case
                definition='Second',
                docname='doc2',
                lineno=2,
                anchor='term-labor-aristocracy',
            )

    def test_case_sensitive_mode_allows_different_case(self):
        """
        Given: case_sensitive=True
        When: Same term with different case is added
        Then: Both are stored (no error)
        """
        collector = DefinitionsCollector(case_sensitive=True)

        collector.add_definition(
            term='Labor Aristocracy',
            definition='Title case',
            docname='doc1',
            lineno=1,
            anchor='term-labor-aristocracy',
        )

        # Should NOT raise with case_sensitive=True
        collector.add_definition(
            term='labor aristocracy',
            definition='Lower case',
            docname='doc2',
            lineno=2,
            anchor='term-labor-aristocracy-2',
        )

        assert len(collector) == 2

    def test_different_terms_no_error(self):
        """
        Given: "Labor Aristocracy" defined inline
        And: "Super-profits" defined inline
        When: Both are added
        Then: No error, both terms registered
        """
        collector = DefinitionsCollector()

        collector.add_definition(
            term='Labor Aristocracy',
            definition='First term',
            docname='doc1',
            lineno=1,
            anchor='term-labor-aristocracy',
        )

        # Different term - should not raise
        collector.add_definition(
            term='Super-profits',
            definition='Second term',
            docname='doc2',
            lineno=2,
            anchor='term-super-profits',
        )

        assert len(collector) == 2


class TestStandardGlossaryConflict:
    """Test conflicts with standard {glossary} directive."""

    def test_inline_conflicts_with_standard_glossary_raises_error(self):
        """
        Given: "Labor Aristocracy" defined inline
        And: "Labor Aristocracy" also defined in standard glossary
        When: check_against_std_glossary is called
        Then: DuplicateTermError raised with both locations
        """
        collector = DefinitionsCollector()

        collector.add_definition(
            term='Labor Aristocracy',
            definition='Inline definition',
            docname='theory/labor-aristocracy',
            lineno=15,
            anchor='term-labor-aristocracy',
        )

        # Mock standard glossary data
        # Format: {term_normalized: (docname, labelid)} (Sphinx 7+)
        std_terms = {
            'labor aristocracy': ('glossary', 'term-labor-aristocracy'),
        }

        with pytest.raises(DuplicateTermError) as exc_info:
            collector.check_against_std_glossary(std_terms)

        error = exc_info.value
        assert 'Labor Aristocracy' in error.term
        assert any('inline definition' in loc.lower() for loc in error.locations)
        assert any('standard glossary' in loc.lower() for loc in error.locations)

    def test_no_conflict_when_terms_differ(self):
        """
        Given: Inline definition for "Term A"
        And: Standard glossary defines "Term B"
        When: check_against_std_glossary is called
        Then: No error
        """
        collector = DefinitionsCollector()

        collector.add_definition(
            term='Term A',
            definition='Inline A',
            docname='doc1',
            lineno=1,
            anchor='term-a',
        )

        std_terms = {
            'term b': ('glossary', 'term-b'),
        }

        # Should not raise
        collector.check_against_std_glossary(std_terms)


class TestDefinitionEntry:
    """Test DefinitionEntry dataclass."""

    def test_location_property(self):
        """
        Given: A DefinitionEntry
        When: location property is accessed
        Then: Returns "docname:lineno" format
        """
        entry = DefinitionEntry(
            term='Test',
            definition='Def',
            docname='theory/test',
            lineno=42,
            anchor='term-test',
        )

        assert entry.location == 'theory/test:42'


class TestDuplicateTermError:
    """Test DuplicateTermError exception."""

    def test_error_message_includes_all_locations(self):
        """
        Given: DuplicateTermError with multiple locations
        When: Error message is accessed
        Then: All locations are included
        """
        error = DuplicateTermError(
            'Test Term',
            ['doc1:10', 'doc2:20', 'doc3:30']
        )

        message = str(error)
        assert 'Test Term' in message
        assert 'doc1:10' in message
        assert 'doc2:20' in message
        assert 'doc3:30' in message
