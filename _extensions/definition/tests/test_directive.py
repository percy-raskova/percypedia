"""
Tests for DefinitionDirective - Sprint 1: Core Directive.

These tests verify the {definition} directive renders correctly as a
sphinx-design card with proper structure and CSS classes.
"""

import pytest
from pathlib import Path
from textwrap import dedent
from unittest.mock import MagicMock, patch

from docutils import nodes
from sphinx.errors import ExtensionError

from definition.directive import DefinitionDirective, definition_card


class TestDirectiveRendering:
    """Test Group 1: Directive renders as sphinx-design card."""

    @pytest.fixture
    def mock_directive(self):
        """Create a mock directive with minimal Sphinx environment."""
        directive = MagicMock(spec=DefinitionDirective)
        directive.arguments = ['Labor Aristocracy']
        directive.content = [
            'The privileged stratum of the proletariat that benefits from',
            'imperialist super-profits.',
        ]
        directive.content_offset = 0
        directive.lineno = 10
        directive.options = {}

        # Mock environment
        directive.env = MagicMock()
        directive.env.docname = 'theory/labor-aristocracy'
        directive.env.definition_all_definitions = {}

        # Mock state for nested parsing
        directive.state = MagicMock()
        directive.state.nested_parse = MagicMock()

        return directive

    def test_directive_renders_card_container(self, mock_directive):
        """
        Given: A definition directive with term "Labor Aristocracy" and body content
        When: The directive is processed
        Then: Output contains definition_card node with sd-card class
        """
        # Act
        result = DefinitionDirective.run(mock_directive)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], definition_card)
        assert 'sd-card' in result[0]['classes']

    def test_directive_card_has_correct_title(self, mock_directive):
        """
        Given: A definition directive with term "Labor Aristocracy"
        When: The directive is processed
        Then: Card header contains "Labor Aristocracy"
        """
        # Act
        result = DefinitionDirective.run(mock_directive)
        card = result[0]

        # Find header
        header = None
        for child in card.children:
            if isinstance(child, nodes.container) and 'sd-card-header' in child.get('classes', []):
                header = child
                break

        # Assert
        assert header is not None, "Card should have header"
        # Check title text
        title_para = header.children[0]
        assert isinstance(title_para, nodes.paragraph)
        strong = title_para.children[0]
        assert isinstance(strong, nodes.strong)
        assert strong.astext() == 'Labor Aristocracy'

    def test_directive_card_body_contains_definition(self, mock_directive):
        """
        Given: A definition directive with body "The privileged stratum..."
        When: The directive is processed
        Then: Card body container exists and nested_parse was called
        """
        # Act
        result = DefinitionDirective.run(mock_directive)
        card = result[0]

        # Find body
        body = None
        for child in card.children:
            if isinstance(child, nodes.container) and 'sd-card-body' in child.get('classes', []):
                body = child
                break

        # Assert
        assert body is not None, "Card should have body"
        # Verify nested_parse was called to process content
        mock_directive.state.nested_parse.assert_called_once()

    def test_directive_card_has_definition_css_class(self, mock_directive):
        """
        Given: A definition directive
        When: The directive is processed
        Then: Card has CSS class "definition-card" for custom styling
        """
        # Act
        result = DefinitionDirective.run(mock_directive)
        card = result[0]

        # Assert
        assert 'definition-card' in card['classes']

    def test_directive_card_has_anchor_id(self, mock_directive):
        """
        Given: A definition directive for "Labor Aristocracy"
        When: The directive is processed
        Then: Card has anchor ID "term-labor-aristocracy"
        """
        # Act
        result = DefinitionDirective.run(mock_directive)
        card = result[0]

        # Assert
        assert 'term-labor-aristocracy' in card['ids']

    def test_directive_empty_content_raises_error(self, mock_directive):
        """
        Given: A definition directive with no body content
        When: The directive is processed
        Then: ExtensionError is raised with message about empty definition
        """
        # Arrange
        mock_directive.content = []
        mock_directive.get_location = MagicMock(return_value='test.md:10')

        # Act & Assert
        with pytest.raises(ExtensionError) as exc_info:
            DefinitionDirective.run(mock_directive)

        assert 'no content' in str(exc_info.value).lower()

    def test_directive_whitespace_only_content_raises_error(self, mock_directive):
        """
        Given: A definition directive with only whitespace content
        When: The directive is processed
        Then: ExtensionError is raised
        """
        # Arrange
        mock_directive.content = ['   ', '  ', '']
        mock_directive.get_location = MagicMock(return_value='test.md:10')

        # Act & Assert
        with pytest.raises(ExtensionError) as exc_info:
            DefinitionDirective.run(mock_directive)

        assert 'no content' in str(exc_info.value).lower()

    def test_directive_stores_definition_in_env(self, mock_directive):
        """
        Given: A definition directive
        When: The directive is processed
        Then: Definition is stored in env.definition_all_definitions
        """
        # Act
        DefinitionDirective.run(mock_directive)

        # Assert
        definitions = mock_directive.env.definition_all_definitions
        assert 'labor aristocracy' in definitions
        entry = definitions['labor aristocracy']
        assert entry['term'] == 'Labor Aristocracy'
        assert entry['docname'] == 'theory/labor-aristocracy'
        assert entry['lineno'] == 10
        assert 'term-labor-aristocracy' in entry['anchor']


class TestDirectiveWithCustomClasses:
    """Test custom CSS class option."""

    def test_directive_accepts_custom_class(self):
        """
        Given: A definition directive with :class: option
        When: The directive is processed
        Then: Custom class is added to card
        """
        directive = MagicMock(spec=DefinitionDirective)
        directive.arguments = ['Test Term']
        directive.content = ['Definition text.']
        directive.content_offset = 0
        directive.lineno = 1
        directive.options = {'class': ['my-custom-class']}
        directive.env = MagicMock()
        directive.env.docname = 'test'
        directive.env.definition_all_definitions = {}
        directive.state = MagicMock()

        # Act
        result = DefinitionDirective.run(directive)
        card = result[0]

        # Assert
        assert 'my-custom-class' in card['classes']


class TestMultipleDefinitions:
    """Test handling of multiple definitions."""

    def test_multiple_definitions_stored_separately(self):
        """
        Given: Multiple definition directives in same file
        When: Each is processed
        Then: All are stored separately in env
        """
        env = MagicMock()
        env.docname = 'theory/concepts'
        env.definition_all_definitions = {}

        terms = ['Term One', 'Term Two', 'Term Three']

        for i, term in enumerate(terms):
            directive = MagicMock(spec=DefinitionDirective)
            directive.arguments = [term]
            directive.content = [f'Definition of {term}.']
            directive.content_offset = 0
            directive.lineno = (i + 1) * 10
            directive.options = {}
            directive.env = env
            directive.state = MagicMock()

            DefinitionDirective.run(directive)

        # Assert all stored
        assert len(env.definition_all_definitions) == 3
        assert 'term one' in env.definition_all_definitions
        assert 'term two' in env.definition_all_definitions
        assert 'term three' in env.definition_all_definitions


class TestTermNameEdgeCases:
    """Test edge cases in term names."""

    @pytest.fixture
    def base_directive(self):
        """Base directive for testing various term names."""
        directive = MagicMock(spec=DefinitionDirective)
        directive.content = ['Definition text.']
        directive.content_offset = 0
        directive.lineno = 1
        directive.options = {}
        directive.env = MagicMock()
        directive.env.docname = 'test'
        directive.env.definition_all_definitions = {}
        directive.state = MagicMock()
        return directive

    def test_term_with_special_characters(self, base_directive):
        """
        Given: Term name "C++" with special characters
        When: Definition is processed
        Then: Term registered correctly, anchor ID properly escaped
        """
        base_directive.arguments = ['C++']

        result = DefinitionDirective.run(base_directive)
        card = result[0]

        # Anchor should be safe
        assert len(card['ids']) == 1
        assert card['ids'][0].startswith('term-')
        # Stored with original name
        assert 'c++' in base_directive.env.definition_all_definitions

    def test_term_with_unicode(self, base_directive):
        """
        Given: Term name "Teoría del Valor" with unicode
        When: Definition is processed
        Then: Term registered correctly with unicode preserved
        """
        base_directive.arguments = ['Teoría del Valor']

        result = DefinitionDirective.run(base_directive)

        # Original unicode preserved in storage
        entry = base_directive.env.definition_all_definitions['teoría del valor']
        assert entry['term'] == 'Teoría del Valor'

    def test_term_with_leading_trailing_whitespace(self, base_directive):
        """
        Given: Term name with whitespace "  Labor Aristocracy  "
        When: Definition is processed
        Then: Whitespace is stripped
        """
        base_directive.arguments = ['  Labor Aristocracy  ']

        result = DefinitionDirective.run(base_directive)
        card = result[0]

        # Find title
        header = card.children[0]
        title = header.children[0].children[0]
        assert title.astext() == 'Labor Aristocracy'
