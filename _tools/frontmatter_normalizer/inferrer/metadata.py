"""Metadata inferrer - deterministic field extraction.

Handles:
- zkid: 12-digit Zettelkasten ID (YYYYMMDDHHMM)
- date-created / date-edited: ISO dates from file timestamps
- title: extracted from first H1 heading
- author: default author (configurable)
"""

import re
from datetime import datetime
from pathlib import Path

from ..config import DEFAULTS
from ._common import strip_frontmatter


class MetadataInferrer:
    """Infers deterministic metadata fields from content and filesystem."""

    def __init__(self, default_author: str | None = None):
        """Initialize the metadata inferrer.

        Args:
            default_author: Default author name for new files (defaults to config.DEFAULTS["author"])
        """
        self.default_author = default_author if default_author is not None else DEFAULTS["author"]

    def infer_zkid(self, filepath: Path) -> str:
        """Generate a 12-digit Zettelkasten ID from file creation time.

        Format: YYYYMMDDHHMM

        Args:
            filepath: Path to the file

        Returns:
            12-digit string ID
        """
        filepath = Path(filepath)

        # Try to get file creation time, fall back to modification time
        try:
            # On Linux, st_ctime is inode change time, not creation
            # st_mtime is usually the best we can get
            stat = filepath.stat()
            # Try birthtime (macOS) first
            timestamp = getattr(stat, 'st_birthtime', None)
            if timestamp is None:
                timestamp = stat.st_mtime
        except (OSError, FileNotFoundError):
            # Fall back to current time
            timestamp = datetime.now().timestamp()

        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y%m%d%H%M')

    def infer_dates(self, filepath: Path) -> dict[str, str]:
        """Infer date-created and date-edited from file timestamps.

        Args:
            filepath: Path to the file

        Returns:
            Dict with 'date-created' and 'date-edited' keys (YYYY-MM-DD format)
        """
        filepath = Path(filepath)

        try:
            stat = filepath.stat()
            # Creation time (or best approximation)
            ctime = getattr(stat, 'st_birthtime', stat.st_ctime)
            mtime = stat.st_mtime

            created = datetime.fromtimestamp(ctime)
            edited = datetime.fromtimestamp(mtime)
        except (OSError, FileNotFoundError):
            # Fall back to current time
            created = edited = datetime.now()

        return {
            'date-created': created.strftime('%Y-%m-%d'),
            'date-edited': edited.strftime('%Y-%m-%d'),
        }

    def infer_title(self, content: str) -> str | None:
        """Extract title from first H1 heading.

        Handles content with or without frontmatter.

        Args:
            content: Markdown content (may include frontmatter)

        Returns:
            Title string, or None if no H1 found
        """
        # Strip frontmatter if present
        body = strip_frontmatter(content)

        # Find first H1 heading (# Title format)
        match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
        if match:
            return match.group(1).strip()

        return None

    def infer_author(self) -> str:
        """Return the default author.

        Returns:
            Author name string
        """
        return self.default_author
