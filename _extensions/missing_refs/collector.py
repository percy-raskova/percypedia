"""Missing References Collector.

Collects and organizes missing document references during Sphinx builds.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .constants import UNCATEGORIZED

if TYPE_CHECKING:
    pass

__all__ = [
    'MissingRefsCollector',
]


class MissingRefsCollector:
    """Collects and organizes missing document references.

    This collector tracks forward-links to documents that don't exist yet,
    grouping them by category for reporting.
    """

    def __init__(self) -> None:
        """Initialize an empty collector."""
        self.missing: dict[str, dict[str, Any]] = {}

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

    # Alias for external use
    group_by_category = _group_by_category

    def to_dict(self) -> dict[str, Any]:
        """Convert collected data to a dictionary structure.

        Returns:
            Dict with missing_documents list, by_category grouping, and metadata.
        """
        # Import here to avoid circular import
        from .serializers import to_dict
        return to_dict(self)

    def to_markdown(self, title: str = "Planned Articles") -> str:
        """Generate markdown content for a 'Coming Soon' page.

        Args:
            title: Page title

        Returns:
            Markdown string
        """
        from .serializers import to_markdown
        return to_markdown(self, title)

    def write_json(self, path: Path) -> None:
        """Write collected data to a JSON file.

        Args:
            path: Output file path
        """
        from .serializers import write_json
        write_json(self, path)

    def write_markdown(self, path: Path, title: str = "Planned Articles") -> None:
        """Write a 'Coming Soon' markdown page.

        Args:
            path: Output file path
            title: Page title
        """
        from .serializers import write_markdown
        write_markdown(self, path, title)

    def merge(self, other: 'MissingRefsCollector') -> None:
        """Merge another collector's data into this one.

        Used for parallel builds to combine results from different workers.

        Args:
            other: Another MissingRefsCollector instance
        """
        for target, info in other.missing.items():
            if target not in self.missing:
                self.missing[target] = {
                    'category': info['category'],
                    'referenced_by': list(info['referenced_by']),
                }
            else:
                # Merge referenced_by lists, avoiding duplicates
                for ref in info['referenced_by']:
                    if ref not in self.missing[target]['referenced_by']:
                        self.missing[target]['referenced_by'].append(ref)

    def __len__(self) -> int:
        """Return the number of missing references."""
        return len(self.missing)

    def __bool__(self) -> bool:
        """Return True if there are any missing references."""
        return bool(self.missing)
