# missing_refs - Capture missing document references as a TODO list
#
# Collects forward-links to documents that don't exist yet and outputs:
# 1. JSON file for programmatic use (_build/missing_refs.json)
# 2. Optional "Coming Soon" markdown page
#
# This lets you create links to documents you plan to write, track them,
# and optionally show readers what's in the pipeline.

import json
import logging
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    'DEFAULT_PAGE_PATH',
    'DEFAULT_PAGE_TITLE',
    'JSON_OUTPUT_FILENAME',
    'REFTYPE_DOC',
    'UNCATEGORIZED',
    'UNKNOWN_SOURCE',
    # Main class
    'MissingRefsCollector',
    # Constants
    '__version__',
    # Global collector management
    'get_collector',
    'on_build_finished',
    # Sphinx event handlers
    'on_missing_reference',
    'reset_collector',
    'setup',
]

# =============================================================================
# Constants
# =============================================================================

# Extension metadata
__version__ = '0.1.0'

# Reference types we track
REFTYPE_DOC = 'doc'

# Category grouping
UNCATEGORIZED = 'uncategorized'

# Fallback values
UNKNOWN_SOURCE = 'unknown'

# Default configuration
DEFAULT_PAGE_TITLE = 'Planned Articles'
DEFAULT_PAGE_PATH = 'coming-soon.md'

# Output filenames
JSON_OUTPUT_FILENAME = 'missing_refs.json'


class MissingRefsCollector:
    """Collects and organizes missing document references."""

    def __init__(self):
        self.missing: dict[str, dict[str, Any]] = {}

    def _group_by_category(self) -> dict[str, list[str]]:
        """Group missing targets by their category.

        Returns:
            Dictionary mapping category names to sorted lists of target paths.
            Targets without a category are grouped under UNCATEGORIZED.
        """
        by_category: dict[str, list[str]] = defaultdict(list)
        for target, info in self.missing.items():
            cat = info['category'] or UNCATEGORIZED
            by_category[cat].append(target)

        # Sort targets within each category
        for cat, targets in by_category.items():
            by_category[cat] = sorted(targets)

        return dict(sorted(by_category.items()))

    def record_missing(self, target: str, referenced_by: str) -> None:
        """Record a missing document reference.

        Args:
            target: The missing document path (e.g., 'theory/future-topic')
            referenced_by: The document containing the broken reference
        """
        if target not in self.missing:
            # Extract category from path (first segment if nested)
            # Handle leading slashes (e.g., '/concepts/topic' -> 'concepts')
            clean_target = target.lstrip('/')
            parts = clean_target.split('/')
            category = parts[0] if len(parts) > 1 else None

            self.missing[target] = {
                'category': category,
                'referenced_by': [],
            }

        # Avoid duplicates
        if referenced_by not in self.missing[target]['referenced_by']:
            self.missing[target]['referenced_by'].append(referenced_by)

    def to_dict(self) -> dict[str, Any]:
        """Convert collected data to a dictionary structure.

        Returns:
            Dict with missing_documents list, by_category grouping, and metadata.
        """
        # Build the documents list
        documents = []
        for target, info in sorted(self.missing.items()):
            documents.append({
                'target': target,
                'category': info['category'],
                'referenced_by': sorted(info['referenced_by']),
            })

        return {
            'generated_at': datetime.now(UTC).isoformat(),
            'count': len(self.missing),
            'missing_documents': documents,
            'by_category': self._group_by_category(),
        }

    def write_json(self, path: Path) -> None:
        """Write collected data to a JSON file.

        Args:
            path: Output file path
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_dict(), indent=2),
            encoding='utf-8'
        )

    def to_markdown(self, title: str = "Planned Articles") -> str:
        """Generate markdown content for a 'Coming Soon' page.

        Args:
            title: Page title

        Returns:
            Markdown string
        """
        if not self.missing:
            return f"# {title}\n\nNo planned articles at this time.\n"

        lines = [
            f"# {title}",
            "",
            "These articles are referenced but not yet written. Check back soon!",
            "",
        ]

        # Output by category (already sorted by _group_by_category)
        by_category = self._group_by_category()
        for category, targets in by_category.items():
            lines.append(f"## {category.title()}")
            lines.append("")
            for target in targets:
                # Extract the document name from path
                name = target.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
                refs = self.missing[target]['referenced_by']
                ref_text = f" *(referenced from: {', '.join(refs)})*" if refs else ""
                lines.append(f"- **{name}**{ref_text}")
            lines.append("")

        return '\n'.join(lines)

    def write_markdown(self, path: Path, title: str = "Planned Articles") -> None:
        """Write a 'Coming Soon' markdown page.

        Args:
            path: Output file path
            title: Page title
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_markdown(title), encoding='utf-8')


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
        app: Sphinx application instance
        env: Build environment
        node: The reference node with reftype and reftarget
        contnode: Content node (unused)
    """
    # Get reference type - we only track document references
    reftype = node.get('reftype', '')
    reftarget = node.get('reftarget', '')

    if reftype == REFTYPE_DOC and reftarget:
        # Get the source document
        source_doc = env.docname if hasattr(env, 'docname') else UNKNOWN_SOURCE
        get_collector(env).record_missing(reftarget, source_doc)

    # Return None to let Sphinx continue with default handling (warning)


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
    collector.write_json(json_path)

    # Log summary
    count = len(collector.missing)
    logger.info(f"Found {count} planned article(s) - see {json_path}")

    # Write markdown if configured
    if app.config.missing_refs_generate_page:
        md_path = Path(app.srcdir) / app.config.missing_refs_page_path
        collector.write_markdown(md_path, app.config.missing_refs_page_title)
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
    app.connect('build-finished', on_build_finished)

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
