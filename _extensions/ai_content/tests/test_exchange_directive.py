"""
Tests for AIExchangeDirective - Sprint 2: Single Q&A pairs.

The {ai-exchange} directive is for the most common use case:
a single question and answer, separated by ---.
"""

import pytest

from .conftest import SAMPLE_EXCHANGE_CONTENT, make_mock_directive


class TestExchangeParsing:
    """Test Group 1: Parse question/answer separated by ---."""

    def test_parse_simple_exchange(self):
        """
        Given: Content with question, ---, and answer
        When: parse_exchange is called
        Then: Returns dict with question and answer
        """
        from ai_content.parser import parse_exchange

        content = """What is the Y combinator?
---
The Y combinator is a fixed-point combinator that enables recursion..."""

        result = parse_exchange(content)

        assert 'question' in result
        assert 'answer' in result
        assert 'Y combinator' in result['question']
        assert 'fixed-point' in result['answer']

    def test_parse_multiline_question(self):
        """
        Given: Multi-line question before ---
        When: parse_exchange is called
        Then: Full question is captured
        """
        from ai_content.parser import parse_exchange

        content = """I have a complex question
that spans multiple lines
and includes context.
---
Here's the answer."""

        result = parse_exchange(content)

        assert 'complex question' in result['question']
        assert 'multiple lines' in result['question']

    def test_parse_multiline_answer(self):
        """
        Given: Multi-line answer after ---
        When: parse_exchange is called
        Then: Full answer is captured with formatting
        """
        from ai_content.parser import parse_exchange

        content = """Question?
---
Here's a detailed answer:

1. First point
2. Second point

```python
code_example()
```"""

        result = parse_exchange(content)

        assert '1. First point' in result['answer']
        assert '```python' in result['answer']

    def test_parse_handles_missing_separator(self):
        """
        Given: Content without --- separator
        When: parse_exchange is called
        Then: Returns None or raises error
        """
        from ai_content.parser import parse_exchange

        content = "Just some text without a separator"
        result = parse_exchange(content)

        assert result is None

    def test_parse_handles_empty_content(self):
        """
        Given: Empty content
        When: parse_exchange is called
        Then: Returns None
        """
        from ai_content.parser import parse_exchange

        result = parse_exchange("")
        assert result is None


class TestExchangeDirective:
    """Test Group 2: Directive rendering."""

    @pytest.fixture
    def mock_directive(self):
        """Create a mock exchange directive."""
        from ai_content.directives import AIExchangeDirective

        return make_mock_directive(
            AIExchangeDirective,
            arguments=['y-combinator-explanation'],
            content=SAMPLE_EXCHANGE_CONTENT,
            options={'date': '2024-06-15'},
            docname='ai-archive/exchanges',
        )

    def test_directive_renders_exchange_node(self, mock_directive):
        """
        Given: An ai-exchange directive
        When: Processed
        Then: Returns ai_exchange_node with proper classes
        """
        from ai_content.directives import AIExchangeDirective
        from ai_content.nodes import ai_exchange_node

        result = AIExchangeDirective.run(mock_directive)

        assert len(result) == 1
        assert isinstance(result[0], ai_exchange_node)
        assert 'ai-exchange' in result[0]['classes']

    def test_directive_has_ai_badge(self, mock_directive):
        """
        Given: An ai-exchange directive
        When: Processed
        Then: Has ai-generated class for badge
        """
        from ai_content.directives import AIExchangeDirective

        result = AIExchangeDirective.run(mock_directive)

        assert 'ai-generated' in result[0]['classes']

    def test_directive_contains_question_and_answer(self, mock_directive):
        """
        Given: Exchange with question and answer
        When: Processed
        Then: Both sections appear in output
        """
        from ai_content.directives import AIExchangeDirective

        result = AIExchangeDirective.run(mock_directive)
        exchange_node = result[0]

        # Should have question and answer containers
        classes = []
        for child in exchange_node.findall():
            if hasattr(child, 'get'):
                classes.extend(child.get('classes', []))

        assert 'ai-question' in classes
        assert 'ai-answer' in classes

    def test_directive_stores_in_env(self, mock_directive):
        """
        Given: An ai-exchange directive
        When: Processed
        Then: Metadata stored in env.ai_content_exchanges
        """
        from ai_content.directives import AIExchangeDirective

        AIExchangeDirective.run(mock_directive)

        exchanges = mock_directive.env.ai_content_exchanges
        assert 'y-combinator-explanation' in exchanges
        assert exchanges['y-combinator-explanation']['date'] == '2024-06-15'

    def test_directive_anchor_id(self, mock_directive):
        """
        Given: Exchange named 'y-combinator-explanation'
        When: Processed
        Then: Anchor is 'ai-exchange-y-combinator-explanation'
        """
        from ai_content.directives import AIExchangeDirective

        result = AIExchangeDirective.run(mock_directive)

        assert 'ai-exchange-y-combinator-explanation' in result[0]['ids']


class TestExchangeOptions:
    """Test Group 3: Exchange-specific options."""

    def test_model_option(self):
        """
        Given: :model: claude-sonnet-4
        When: Processed
        Then: Model stored in env
        """
        from ai_content.directives import AIExchangeDirective

        directive = make_mock_directive(
            AIExchangeDirective,
            arguments=['test-exchange'],
            content=['Question?', '---', 'Answer.'],
            options={'model': 'claude-sonnet-4'},
            lineno=1,
        )

        AIExchangeDirective.run(directive)

        assert directive.env.ai_content_exchanges['test-exchange']['model'] == 'claude-sonnet-4'
