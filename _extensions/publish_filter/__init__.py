# publish_filter - Sphinx extension for draft/publish workflow
#
# Features:
# 1. Excludes documents with `publish: false` from the build
# 2. Strips Obsidian-style comments (%%...%%) from output
#
# Usage in frontmatter:
#   publish: false  -> Document is excluded from build
#   publish: true   -> Document is included (default behavior)

import re
from pathlib import Path
from typing import Set

from _common.frontmatter import extract_frontmatter
from _common.traversal import iter_markdown_files


def get_unpublished_docs(app) -> Set[str]:
    """Scan source files and return docnames with publish: false."""
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

        try:
            content = md_file.read_text(encoding='utf-8')
            frontmatter = extract_frontmatter(content)

            if frontmatter.get('publish') is False:
                docname = str(rel_path.with_suffix(''))
                unpublished.add(docname)

        except Exception:
            continue

    return unpublished


def builder_inited(app):
    """Add unpublished documents to exclude_patterns."""
    unpublished = get_unpublished_docs(app)
    if unpublished:
        # Add to exclude patterns
        for docname in unpublished:
            pattern = docname + '.md'
            if pattern not in app.config.exclude_patterns:
                app.config.exclude_patterns.append(pattern)


def strip_obsidian_comments(app, docname, source):
    """Remove Obsidian-style comments (%%...%%) from source.

    Obsidian comments use %% delimiters:
    - Single line: %%this is hidden%%
    - Multi-line: %%\nthis is\nhidden\n%%
    """
    if source and source[0]:
        # Pattern matches %% followed by any content (non-greedy) until %%
        # DOTALL flag makes . match newlines for multi-line comments
        pattern = r'%%.*?%%'
        source[0] = re.sub(pattern, '', source[0], flags=re.DOTALL)


def setup(app):
    """Sphinx extension entry point."""
    # Exclude unpublished docs before reading
    app.connect('builder-inited', builder_inited)

    # Strip Obsidian comments from source
    app.connect('source-read', strip_obsidian_comments)

    return {
        'version': '0.1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
