"""Serialization utilities for missing references.

Provides functions to convert collected missing references to JSON and Markdown.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .collector import MissingRefsCollector

__all__ = [
    'to_dict',
    'to_markdown',
    'write_json',
    'write_markdown',
]


def to_dict(collector: 'MissingRefsCollector') -> dict[str, Any]:
    """Convert collected data to a dictionary structure.

    Args:
        collector: The MissingRefsCollector instance

    Returns:
        Dict with missing_documents list, by_category grouping, and metadata.
    """
    # Build the documents list
    documents = []
    for target, info in sorted(collector.missing.items()):
        documents.append({
            'target': target,
            'category': info['category'],
            'referenced_by': sorted(info['referenced_by']),
        })

    return {
        'generated_at': datetime.now(UTC).isoformat(),
        'count': len(collector.missing),
        'missing_documents': documents,
        'by_category': collector.group_by_category(),
    }


def to_markdown(collector: 'MissingRefsCollector', title: str = "Planned Articles") -> str:
    """Generate markdown content for a 'Coming Soon' page.

    Args:
        collector: The MissingRefsCollector instance
        title: Page title

    Returns:
        Markdown string
    """
    if not collector.missing:
        return f"# {title}\n\nNo planned articles at this time.\n"

    lines = [
        f"# {title}",
        "",
        "These articles are referenced but not yet written. Check back soon!",
        "",
    ]

    # Output by category (already sorted by group_by_category)
    by_category = collector.group_by_category()
    for category, targets in by_category.items():
        lines.append(f"## {category.title()}")
        lines.append("")
        for target in targets:
            # Extract the document name from path
            name = target.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
            refs = collector.missing[target]['referenced_by']
            ref_text = f" *(referenced from: {', '.join(refs)})*" if refs else ""
            lines.append(f"- **{name}**{ref_text}")
        lines.append("")

    return '\n'.join(lines)


def write_json(collector: 'MissingRefsCollector', path: Path) -> None:
    """Write collected data to a JSON file.

    Args:
        collector: The MissingRefsCollector instance
        path: Output file path
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(to_dict(collector), indent=2),
        encoding='utf-8'
    )


def write_markdown(
    collector: 'MissingRefsCollector',
    path: Path,
    title: str = "Planned Articles"
) -> None:
    """Write a 'Coming Soon' markdown page.

    Args:
        collector: The MissingRefsCollector instance
        path: Output file path
        title: Page title
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_markdown(collector, title), encoding='utf-8')
