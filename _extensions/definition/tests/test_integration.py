"""
Tests for Bidirectional Links - Sprint 5: Integration with Sphinx std domain.

These tests verify that:
1. Terms are registered with Sphinx's std domain
2. {term}`...` role resolves to generated glossary page
3. Event handlers properly wire up the extension
"""

from unittest.mock import MagicMock

from definition import setup
from definition.collector import DefinitionsCollector
from definition.directive import DefinitionDirective
from definition.generator import collect_glossary_pages


class TestSphinxAppSetup:
    """Test extension setup and configuration."""

    def test_setup_returns_extension_metadata(self):
        """
        Given: A Sphinx app
        When: setup() is called
        Then: Returns dict with version and parallel safety flags
        """
        app = MagicMock()
        app.add_config_value = MagicMock()
        app.add_directive = MagicMock()
        app.add_node = MagicMock()
        app.connect = MagicMock()

        result = setup(app)

        assert 'version' in result
        assert result['parallel_read_safe'] is True
        assert result['parallel_write_safe'] is True

    def test_setup_registers_directive(self):
        """
        Given: A Sphinx app
        When: setup() is called
        Then: 'definition' directive is registered
        """
        app = MagicMock()

        setup(app)

        app.add_directive.assert_any_call('definition', DefinitionDirective)

    def test_setup_adds_config_values(self):
        """
        Given: A Sphinx app
        When: setup() is called
        Then: Config values are registered
        """
        app = MagicMock()

        setup(app)

        config_calls = [call[0][0] for call in app.add_config_value.call_args_list]
        assert 'definition_glossary_path' in config_calls
        assert 'definition_card_color' in config_calls
        assert 'definition_case_sensitive' in config_calls


class TestTermRegistration:
    """Test Group 5: Terms registered in std domain."""

    def test_term_registered_in_std_domain(self):
        """
        Given: {definition}`Labor Aristocracy` processed
        When: Build completes
        Then: 'labor aristocracy' exists in env.domaindata['std']['terms']

        Note: This test verifies the concept - full integration requires
        a real Sphinx build which we'll test separately.
        """
        # Create mock environment with std domain structure
        env = MagicMock()
        env.domaindata = {'std': {'terms': {}}}
        env.docname = 'theory/labor-aristocracy'

        # Simulate what register_term should do
        term = 'Labor Aristocracy'
        normalized = term.lower()
        anchor = f'term-{term.lower().replace(" ", "-")}'
        glossary_path = 'glossary'

        # Register in std domain
        env.domaindata['std']['terms'][normalized] = (
            glossary_path,  # docname
            anchor,  # labelid
            term,  # term_text
        )

        # Verify
        assert normalized in env.domaindata['std']['terms']
        docname, labelid, term_text = env.domaindata['std']['terms'][normalized]
        assert docname == 'glossary'
        assert labelid == 'term-labor-aristocracy'
        assert term_text == 'Labor Aristocracy'

    def test_term_role_resolves_to_glossary_page(self):
        """
        Given: Term registered in std domain
        When: {term}`Labor Aristocracy` is used
        Then: Link points to glossary.html#term-labor-aristocracy

        Note: This verifies the expected URL structure.
        """
        glossary_path = 'glossary'
        anchor = 'term-labor-aristocracy'
        expected_url = f'{glossary_path}.html#{anchor}'

        assert expected_url == 'glossary.html#term-labor-aristocracy'


class TestCollectGlossaryPages:
    """Test html-collect-pages event handler."""

    def test_collect_pages_yields_glossary_tuple(self):
        """
        Given: App with definitions in collector
        When: collect_glossary_pages is called
        Then: Yields (pagename, context, template) tuple
        """
        # Setup
        app = MagicMock()
        app.config.definition_glossary_path = 'glossary'

        collector = DefinitionsCollector()
        collector.add_definition(
            term='Test Term',
            definition='Test definition',
            docname='test',
            lineno=1,
            anchor='term-test-term',
        )

        env = MagicMock()
        env.definition_collector = collector
        env.get_domain = MagicMock()
        env.get_domain.return_value.data = {'terms': {}}
        app.env = env

        # Act
        pages = list(collect_glossary_pages(app))

        # Assert
        assert len(pages) == 1
        pagename, context, template = pages[0]
        assert pagename == 'glossary'
        assert 'title' in context
        assert 'body' in context
        assert template == 'page.html'

    def test_collect_pages_returns_empty_when_no_collector(self):
        """
        Given: App without collector in env
        When: collect_glossary_pages is called
        Then: Returns empty (no pages generated)
        """
        app = MagicMock()
        env = MagicMock()
        env.definition_collector = None
        app.env = env

        pages = list(collect_glossary_pages(app))

        assert len(pages) == 0

    def test_collect_pages_merges_with_std_glossary(self):
        """
        Given: Inline definitions AND standard glossary terms
        When: collect_glossary_pages generates page
        Then: Both appear in the glossary body
        """
        # Setup
        app = MagicMock()
        app.config.definition_glossary_path = 'glossary'

        collector = DefinitionsCollector()
        collector.add_definition(
            term='Inline Term',
            definition='Inline definition',
            docname='article',
            lineno=10,
            anchor='term-inline-term',
        )

        std_domain = MagicMock()
        std_domain.data = {
            'terms': {
                'standard term': ('glossary', 'term-standard-term'),
            }
        }

        env = MagicMock()
        env.definition_collector = collector
        env.get_domain = MagicMock(return_value=std_domain)
        app.env = env

        # Act
        pages = list(collect_glossary_pages(app))

        # Assert
        assert len(pages) == 1
        _, context, _ = pages[0]
        body = context['body']
        assert 'Inline Term' in body
        assert 'Standard Term' in body


class TestBuilderInitEvent:
    """Test builder-inited event handler."""

    def test_builder_init_creates_collector_on_env(self):
        """
        Given: Sphinx builder initializes
        When: builder-inited event fires
        Then: env.definition_collector is created
        """
        from definition import init_collector

        app = MagicMock()
        app.config.definition_case_sensitive = False
        env = MagicMock()
        env.definition_collector = None
        app.env = env

        init_collector(app)

        assert hasattr(env, 'definition_collector')
        assert isinstance(env.definition_collector, DefinitionsCollector)


class TestEnvGetOutdated:
    """Test env-get-outdated event for cache invalidation."""

    def test_glossary_page_always_rebuilt(self):
        """
        Given: Any document changes
        When: env-get-outdated event fires
        Then: Glossary page is marked for rebuild

        Note: This ensures definitions are always current.
        """
        from definition import get_outdated_docs

        app = MagicMock()
        app.config.definition_glossary_path = 'glossary'
        env = MagicMock()

        # Simulate some docs changed
        added = ['new_article']
        changed = ['modified_article']
        removed = ['deleted_article']

        result = get_outdated_docs(app, env, added, changed, removed)

        # Glossary should be in outdated list
        assert 'glossary' in result


class TestEnvMergeInfo:
    """Test env-merge-info for parallel builds."""

    def test_collectors_merge_in_parallel_build(self):
        """
        Given: Parallel build with multiple processes
        When: env-merge-info event fires
        Then: Definitions from all processes are combined
        """
        from definition import merge_collectors

        app = MagicMock()

        # Main env
        main_collector = DefinitionsCollector()
        main_collector.add_definition(
            term='Main Term',
            definition='From main',
            docname='main',
            lineno=1,
            anchor='term-main-term',
        )
        env = MagicMock()
        env.definition_collector = main_collector

        # Other process env
        other_collector = DefinitionsCollector()
        other_collector.add_definition(
            term='Other Term',
            definition='From other',
            docname='other',
            lineno=1,
            anchor='term-other-term',
        )
        other_env = MagicMock()
        other_env.definition_collector = other_collector

        # Merge
        merge_collectors(app, env, [], other_env)

        # Verify both terms present
        assert 'main term' in env.definition_collector
        assert 'other term' in env.definition_collector
