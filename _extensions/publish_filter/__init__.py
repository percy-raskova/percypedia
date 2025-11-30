# publish_filter - Sphinx extension for draft/publish workflow
#
# Features:
# 1. Excludes documents with `publish: false` from the build
# 2. Strips Obsidian-style comments (%%...%%) from output
# 3. Protects critical files from accidental exclusion
#
# Usage in frontmatter:
#   publish: false  -> Document is excluded from build
#   publish: true   -> Document is included (default behavior)

import logging
import re
from pathlib import Path

from sphinx.application import Sphinx

from _common.frontmatter import extract_frontmatter
from _common.traversal import iter_markdown_files

logger = logging.getLogger(__name__)

# Critical files that must NEVER be excluded from builds
# Even if marked publish: false (e.g., by automated tools)
PROTECTED_DOCNAMES = {
    'index',      # Root document - build fails without this
    'glossary',   # Referenced in root toctree
    'honeypot',   # We intentionally want honeypot to be produced!
}

# Obsidian-style comment pattern: %%content%%
# Matches single-line: %%hidden%%
# Matches multi-line: %%\nmulti\nline\n%%
# Uses non-greedy match (.*?) to handle multiple comments on same line
OBSIDIAN_COMMENT_PATTERN = r'%%.*?%%'


def get_unpublished_docs(app: Sphinx) -> set[str]:
    """Scan source files and return docnames with publish: false.

    Args:
        app: Sphinx application instance.

    Returns:
        Set of docnames that have publish: false in frontmatter.
        Protected files (index.md, glossary.md) are never excluded,
        even if marked publish: false.
    """
    unpublished = set()
    srcdir = Path(app.srcdir)

    # Use shared traversal - publish_filter skips all underscore files/dirs and dot dirs
    for md_file in iter_markdown_files(
        srcdir,
        skip_underscore_files=True,
        skip_underscore_dirs=True,
        skip_dot_dirs=True,
    ):
        rel_path = md_file.relative_to(srcdir)
        docname = str(rel_path.with_suffix(''))

        # Never exclude protected files
        if docname in PROTECTED_DOCNAMES:
            continue

        try:
            content = md_file.read_text(encoding='utf-8')
            frontmatter = extract_frontmatter(content)

            if frontmatter.get('publish') is False:
                unpublished.add(docname)

        except OSError as e:
            logger.warning('Could not read %s: %s', md_file, e)
            continue

    return unpublished


def builder_inited(app: Sphinx) -> None:
    """Add unpublished documents to exclude_patterns.

    Args:
        app: Sphinx application instance.
    """
    unpublished = get_unpublished_docs(app)
    if unpublished:
        # Add to exclude patterns
        for docname in unpublished:
            pattern = docname + '.md'
            if pattern not in app.config.exclude_patterns:
                app.config.exclude_patterns.append(pattern)


def strip_obsidian_comments(_app: Sphinx, _docname: str, source: list[str]) -> None:
    """Remove Obsidian-style comments (%%...%%) from source.

    This is a Sphinx source-read event handler that modifies source in-place.

    Args:
        app: Sphinx application instance.
        docname: Document name being processed.
        source: List containing single string of source content (modified in-place).

    Obsidian comments use %% delimiters:
    - Single line: %%this is hidden%%
    - Multi-line: %%\\nthis is\\nhidden\\n%%
    """
    if source and source[0]:
        # DOTALL flag makes . match newlines for multi-line comments
        source[0] = re.sub(OBSIDIAN_COMMENT_PATTERN, '', source[0], flags=re.DOTALL)


def setup(app: Sphinx) -> dict:
    """Sphinx extension entry point.

    Args:
        app: Sphinx application instance.

    Returns:
        Extension metadata dict with version and parallel safety flags.
    """
    # Exclude unpublished docs before reading
    app.connect('builder-inited', builder_inited)

    # Strip Obsidian comments from source
    app.connect('source-read', strip_obsidian_comments)

    return {
        'version': '0.1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
