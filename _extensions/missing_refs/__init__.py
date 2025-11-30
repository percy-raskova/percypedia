# missing_refs - Capture missing document references as a TODO list
#
# Collects forward-links to documents that don't exist yet and outputs:
# 1. JSON file for programmatic use (_build/missing_refs.json)
# 2. Optional "Coming Soon" markdown page
#
# This lets you create links to documents you plan to write, track them,
# and optionally show readers what's in the pipeline.

import logging
from pathlib import Path
from typing import Any

from .collector import MissingRefsCollector
from .constants import (
    DEFAULT_PAGE_PATH,
    DEFAULT_PAGE_TITLE,
    JSON_OUTPUT_FILENAME,
    REFTYPE_DOC,
    UNCATEGORIZED,
    UNKNOWN_SOURCE,
    __version__,
)
from .serializers import write_json, write_markdown

logger = logging.getLogger(__name__)

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # Constants
    'DEFAULT_PAGE_PATH',
    'DEFAULT_PAGE_TITLE',
    'JSON_OUTPUT_FILENAME',
    'REFTYPE_DOC',
    'UNCATEGORIZED',
    'UNKNOWN_SOURCE',
    '__version__',
    # Main class
    'MissingRefsCollector',
    # Global collector management
    'get_collector',
    'reset_collector',
    # Sphinx event handlers
    'on_missing_reference',
    'on_build_finished',
    'on_env_merge_info',
    'setup',
]


def get_collector(env: Any) -> MissingRefsCollector:
    """Get or create the collector instance from the environment.

    Args:
        env: Sphinx build environment

    Returns:
        The MissingRefsCollector for this build
    """
    if not hasattr(env, 'missing_refs_collector') or env.missing_refs_collector is None:
        env.missing_refs_collector = MissingRefsCollector()
    return env.missing_refs_collector


def reset_collector(env: Any) -> None:
    """Reset the collector on the environment (for testing or new builds).

    Args:
        env: Sphinx build environment
    """
    env.missing_refs_collector = None


def on_missing_reference(
    _app: Any,
    env: Any,
    node: dict[str, Any],
    _contnode: Any
) -> None:
    """Handle missing reference events.

    Sphinx calls this when a reference target cannot be resolved.
    We only care about 'doc' references (links to other documents).

    Args:
        _app: Sphinx application instance (unused)
        env: Build environment
        node: The reference node with reftype and reftarget
        _contnode: Content node (unused)
    """
    # Get reference type - we only track document references
    reftype = node.get('reftype', '')
    reftarget = node.get('reftarget', '')

    if reftype == REFTYPE_DOC and reftarget:
        # Get the source document
        source_doc = env.docname if hasattr(env, 'docname') else UNKNOWN_SOURCE
        get_collector(env).record_missing(reftarget, source_doc)

    # Return None to let Sphinx continue with default handling (warning)


def on_env_merge_info(
    _app: Any,
    env: Any,
    _docnames: list[str],
    other: Any
) -> None:
    """Merge collector data from parallel workers.

    Called during parallel builds when worker environments are merged
    into the main environment.

    Args:
        _app: Sphinx application instance (unused)
        env: Main build environment
        _docnames: Document names processed (unused)
        other: Worker's build environment to merge from
    """
    if hasattr(other, 'missing_refs_collector') and other.missing_refs_collector:
        get_collector(env).merge(other.missing_refs_collector)


def on_build_finished(app: Any, exception: Exception | None) -> None:
    """Write output files when build completes.

    Args:
        app: Sphinx application instance
        exception: Exception if build failed, None otherwise
    """
    if exception:
        return  # Don't write if build failed

    collector = get_collector(app.env)

    if not collector.missing:
        return  # Nothing to write

    outdir = Path(app.outdir)

    # Always write JSON
    json_path = outdir / JSON_OUTPUT_FILENAME
    write_json(collector, json_path)

    # Log summary
    count = len(collector.missing)
    logger.info(f"Found {count} planned article(s) - see {json_path}")

    # Write markdown if configured
    if app.config.missing_refs_generate_page:
        md_path = Path(app.srcdir) / app.config.missing_refs_page_path
        write_markdown(collector, md_path, app.config.missing_refs_page_title)
        logger.info(f"Generated {md_path}")

    # Reset for next build
    reset_collector(app.env)


def setup(app: Any) -> dict[str, Any]:
    """Sphinx extension entry point.

    Args:
        app: Sphinx application instance

    Returns:
        Extension metadata with version and parallel safety flags.
    """
    # Configuration options
    app.add_config_value('missing_refs_generate_page', False, 'env')
    app.add_config_value('missing_refs_page_path', DEFAULT_PAGE_PATH, 'env')
    app.add_config_value('missing_refs_page_title', DEFAULT_PAGE_TITLE, 'env')

    # Event handlers
    app.connect('missing-reference', on_missing_reference)
    app.connect('env-merge-info', on_env_merge_info)
    app.connect('build-finished', on_build_finished)

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
