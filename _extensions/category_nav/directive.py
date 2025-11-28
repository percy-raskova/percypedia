"""category_nav directive - generates toctrees from frontmatter categories.

This module provides:
- extract_frontmatter: Re-exported from _common.frontmatter
- extract_title: Extract H1 title from markdown content
- collect_categories: Scan directory and group files by category
- CategoryNavDirective: Sphinx directive that renders categorized toctrees
"""

import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Any

from docutils import nodes
from sphinx.util.docutils import SphinxDirective

# Import from shared module, re-export for backward compatibility
from _common.frontmatter import extract_frontmatter


def extract_title(content: str) -> Optional[str]:
    """Extract the first H1 heading from markdown content.

    Args:
        content: Raw markdown file content

    Returns:
        Title string or None if no H1 found
    """
    # Match # at start of line, followed by space and title text
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def collect_categories(
    srcdir: Path,
    default_category: str = 'Miscellaneous',
    exclude: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
) -> Dict[str, List[Dict[str, str]]]:
    """Scan source directory and group markdown files by category.

    Args:
        srcdir: Path to source directory
        default_category: Category for files without frontmatter
        exclude: List of docnames to exclude (e.g., ['index', 'glossary'])
        exclude_patterns: List of path patterns to skip (e.g., ['.venv', 'private'])

    Returns:
        Dict mapping category names to lists of document info dicts.
        Each doc dict has 'docname' and 'title' keys.
        Categories are sorted alphabetically, with default_category last.
        Documents within each category are sorted by title.
    """
    if exclude is None:
        exclude = []
    if exclude_patterns is None:
        exclude_patterns = []

    # Default patterns to always exclude
    default_exclude_patterns = ['.venv', '_build', 'private', '.git', '.pytest_cache', '_assets', '_templates']
    all_exclude_patterns = set(exclude_patterns) | set(default_exclude_patterns)

    categories: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    srcdir = Path(srcdir)

    for md_file in srcdir.rglob('*.md'):
        # Skip files starting with underscore
        if md_file.name.startswith('_'):
            continue

        # Skip files in excluded directories
        rel_path = md_file.relative_to(srcdir)
        if any(part in all_exclude_patterns or part.startswith('.')
               for part in rel_path.parts[:-1]):  # Check all parent dirs
            continue

        # Calculate docname (path relative to srcdir, without extension)
        docname = str(rel_path.with_suffix(''))

        # Skip excluded files
        if docname in exclude:
            continue

        # Read and parse file
        content = md_file.read_text(encoding='utf-8')
        frontmatter = extract_frontmatter(content)

        # Skip unpublished documents (publish: false)
        if frontmatter.get('publish') is False:
            continue

        # Get category
        category = frontmatter.get('category', default_category)

        # Get title (prefer frontmatter, fall back to H1)
        title = frontmatter.get('title') or extract_title(content) or docname

        categories[category].append({
            'docname': docname,
            'title': title,
        })

    # Sort documents within each category by title
    for docs in categories.values():
        docs.sort(key=lambda d: d['title'].lower())

    # Sort categories alphabetically, with default_category last
    sorted_categories: Dict[str, List[Dict[str, str]]] = {}
    for key in sorted(categories.keys()):
        if key != default_category:
            sorted_categories[key] = categories[key]

    # Add default category last if it exists
    if default_category in categories:
        sorted_categories[default_category] = categories[default_category]

    return sorted_categories


class CategoryNavDirective(SphinxDirective):
    """Sphinx directive that generates categorized toctrees from frontmatter.

    Usage in MyST markdown:
        ```{category-nav}
        ```

    Scans all markdown files, groups by `category:` frontmatter field,
    and generates a toctree for each category.
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    def run(self) -> List[nodes.Node]:
        """Generate toctree nodes grouped by category."""
        from sphinx.addnodes import toctree

        srcdir = Path(self.env.srcdir)
        default_category = self.config.category_nav_default
        exclude = list(self.config.category_nav_exclude)

        # Collect and categorize documents
        categories = collect_categories(srcdir, default_category, exclude)

        result_nodes: List[nodes.Node] = []

        for category, docs in categories.items():
            # Create section for category
            section = nodes.section()
            section['ids'] = [nodes.make_id(f'category-{category}')]

            # Add category title
            title = nodes.title(text=category)
            section += title

            # Create toctree for this category
            toc = toctree()
            toc['parent'] = self.env.docname
            toc['entries'] = [(doc['title'], doc['docname']) for doc in docs]
            toc['includefiles'] = [doc['docname'] for doc in docs]
            toc['maxdepth'] = 2
            toc['glob'] = False
            toc['hidden'] = False
            toc['numbered'] = 0
            toc['titlesonly'] = False
            toc['caption'] = None
            toc['rawcaption'] = ''
            toc['rawentries'] = []

            section += toc
            result_nodes.append(section)

        return result_nodes
