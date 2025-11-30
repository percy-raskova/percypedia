"""Unified file traversal utilities for Sphinx extensions.

Provides consistent file discovery logic across all extensions that need
to iterate markdown files while respecting exclusion patterns.

Usage:
    from _common.traversal import iter_markdown_files

    for md_file in iter_markdown_files(srcdir, exclude_patterns=['_build']):
        process(md_file)
"""

from collections.abc import Iterator
from pathlib import Path


def iter_markdown_files(
    srcdir: Path,
    exclude_patterns: list[str] | None = None,
    skip_underscore_files: bool = True,
    skip_underscore_dirs: bool = True,
    skip_dot_dirs: bool = True,
) -> Iterator[Path]:
    """Iterate over markdown files in a directory tree.

    Args:
        srcdir: Root directory to search
        exclude_patterns: Directory names to skip (e.g., ['_build', '_templates'])
        skip_underscore_files: Skip files starting with '_' (e.g., _index.md)
        skip_underscore_dirs: Skip directories starting with '_' (e.g., _build/)
        skip_dot_dirs: Skip directories starting with '.' (e.g., .git/)

    Yields:
        Path objects for each matching markdown file

    Note:
        Files are yielded in arbitrary order (depends on filesystem).
        Exclusion checks are performed on directory parts only, not the full path.
    """
    if exclude_patterns is None:
        exclude_patterns = []

    for md_file in srcdir.rglob('*.md'):
        # Skip underscore-prefixed files if configured
        if skip_underscore_files and md_file.name.startswith('_'):
            continue

        # Get relative path parts for directory checks
        rel_path = md_file.relative_to(srcdir)
        dir_parts = rel_path.parts[:-1]  # All parts except filename

        # Check directory exclusions
        skip = False
        for part in dir_parts:
            # Skip directories matching exclude patterns
            if part in exclude_patterns:
                skip = True
                break

            # Skip underscore-prefixed directories if configured
            if skip_underscore_dirs and part.startswith('_'):
                skip = True
                break

            # Skip dot-prefixed directories if configured
            if skip_dot_dirs and part.startswith('.'):
                skip = True
                break

        if not skip:
            yield md_file
