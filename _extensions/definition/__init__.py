"""
Bidirectional Definition Directive Extension for Sphinx.

Provides a {definition} directive that:
1. Renders as sphinx-design cards where written
2. Registers terms with Sphinx's glossary domain
3. Auto-generates unified glossary page
4. Creates bidirectional links between definitions and glossary
"""

from typing import Any, Dict, List, Set

from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment

from .directive import (
    DefinitionDirective,
    definition_card,
    visit_definition_card_html,
    depart_definition_card_html,
)
from .collector import DefinitionsCollector
from .generator import collect_glossary_pages

__version__ = '0.1.0'

__all__ = [
    '__version__',
    'DefinitionDirective',
    'definition_card',
    'visit_definition_card_html',
    'depart_definition_card_html',
    'DefinitionsCollector',
    'collect_glossary_pages',
    'setup',
]


def init_collector(app: Sphinx) -> None:
    """
    Initialize the definitions collector on builder-inited.

    Creates a fresh collector on the environment for this build.
    """
    env = app.env
    case_sensitive = app.config.definition_case_sensitive
    env.definition_collector = DefinitionsCollector(case_sensitive=case_sensitive)


def get_outdated_docs(
    app: Sphinx,
    env: BuildEnvironment,
    added: Set[str],
    changed: Set[str],
    removed: Set[str],
) -> List[str]:
    """
    Mark glossary page for rebuild when any document changes.

    This ensures the glossary always reflects current definitions.
    """
    glossary_path = app.config.definition_glossary_path
    return [glossary_path]


def merge_collectors(
    app: Sphinx,
    env: BuildEnvironment,
    docnames: List[str],
    other_env: BuildEnvironment,
) -> None:
    """
    Merge collectors from parallel builds.

    When Sphinx runs parallel builds, each process has its own
    collector. This merges them into the main environment.
    """
    if not hasattr(other_env, 'definition_collector'):
        return
    if other_env.definition_collector is None:
        return

    # Ensure main env has collector
    if not hasattr(env, 'definition_collector') or env.definition_collector is None:
        env.definition_collector = DefinitionsCollector(
            case_sensitive=app.config.definition_case_sensitive
        )

    # Merge definitions from other collector
    other_collector = other_env.definition_collector
    for entry in other_collector.get_all_definitions():
        # Skip if already exists (shouldn't happen, but be safe)
        if entry.term.lower() in env.definition_collector:
            continue
        env.definition_collector.add_definition(
            term=entry.term,
            definition=entry.definition,
            docname=entry.docname,
            lineno=entry.lineno,
            anchor=entry.anchor,
        )


def setup(app: Sphinx) -> Dict[str, Any]:
    """Initialize the definition extension."""
    # Configuration values
    app.add_config_value('definition_glossary_path', 'glossary', 'env')
    app.add_config_value('definition_card_color', 'info', 'env')
    app.add_config_value('definition_case_sensitive', False, 'env')
    app.add_config_value('definition_link_to_glossary', True, 'env')

    # Register directive
    app.add_directive('definition', DefinitionDirective)

    # Register custom node with HTML visitor
    app.add_node(
        definition_card,
        html=(visit_definition_card_html, depart_definition_card_html),
    )

    # Event handlers
    app.connect('builder-inited', init_collector)
    app.connect('env-get-outdated', get_outdated_docs)
    app.connect('env-merge-info', merge_collectors)
    app.connect('html-collect-pages', collect_glossary_pages)

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
