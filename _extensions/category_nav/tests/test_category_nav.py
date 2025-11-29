"""Tests for category_nav Sphinx extension.

TDD RED phase: These tests define the expected behavior.
Run with: pytest _extensions/category_nav/tests/ -v
"""

import pytest
from pathlib import Path


class TestExtractFrontmatter:
    """Tests for YAML frontmatter extraction from markdown files."""

    def test_extracts_category_from_frontmatter(self):
        from category_nav.directive import extract_frontmatter

        content = """---
category: Philosophy
title: Test Document
---

# Heading

Content here.
"""
        result = extract_frontmatter(content)

        assert result['category'] == 'Philosophy'
        assert result['title'] == 'Test Document'

    def test_returns_empty_dict_without_frontmatter(self):
        from category_nav.directive import extract_frontmatter

        content = """# Just a heading

No frontmatter here.
"""
        result = extract_frontmatter(content)

        assert result == {}

    def test_handles_frontmatter_with_only_category(self):
        from category_nav.directive import extract_frontmatter

        content = """---
category: Methods
---

# Title
"""
        result = extract_frontmatter(content)

        assert result['category'] == 'Methods'
        assert 'title' not in result

    def test_handles_tags_as_list(self):
        from category_nav.directive import extract_frontmatter

        content = """---
category: Systems
tags:
  - politics/marxism
  - theory/labor-aristocracy
---

# Document
"""
        result = extract_frontmatter(content)

        assert result['category'] == 'Systems'
        assert result['tags'] == ['politics/marxism', 'theory/labor-aristocracy']

    def test_ignores_malformed_frontmatter(self):
        from category_nav.directive import extract_frontmatter

        content = """---
this is not: valid: yaml: at: all
---

# Content
"""
        result = extract_frontmatter(content)

        # Should not crash, return empty or partial
        assert isinstance(result, dict)

    def test_requires_opening_delimiter_at_start(self):
        from category_nav.directive import extract_frontmatter

        content = """Some text first

---
category: WontWork
---
"""
        result = extract_frontmatter(content)

        assert result == {}


class TestExtractTitle:
    """Tests for extracting document title from content."""

    def test_extracts_h1_title(self):
        from category_nav.directive import extract_title

        content = """---
category: Test
---

# This Is The Title

Some content.
"""
        result = extract_title(content)

        assert result == 'This Is The Title'

    def test_returns_none_without_h1(self):
        from category_nav.directive import extract_title

        content = """---
category: Test
---

## Only H2 Here

Content.
"""
        result = extract_title(content)

        assert result is None

    def test_uses_first_h1_only(self):
        from category_nav.directive import extract_title

        content = """# First Title

# Second Title
"""
        result = extract_title(content)

        assert result == 'First Title'


class TestCollectCategories:
    """Tests for scanning files and grouping by category."""

    def test_groups_files_by_category(self, tmp_path):
        from category_nav.directive import collect_categories

        # Create test files
        (tmp_path / 'doc1.md').write_text('---\ncategory: Philosophy\n---\n# Doc 1')
        (tmp_path / 'doc2.md').write_text('---\ncategory: Methods\n---\n# Doc 2')
        (tmp_path / 'doc3.md').write_text('---\ncategory: Philosophy\n---\n# Doc 3')

        result = collect_categories(tmp_path)

        assert 'Philosophy' in result
        assert 'Methods' in result
        assert len(result['Philosophy']) == 2
        assert len(result['Methods']) == 1

    def test_uncategorized_files_go_to_default(self, tmp_path):
        from category_nav.directive import collect_categories

        (tmp_path / 'orphan.md').write_text('# No Frontmatter')

        result = collect_categories(tmp_path, default_category='Miscellaneous')

        assert 'Miscellaneous' in result
        assert len(result['Miscellaneous']) == 1

    def test_excludes_specified_files(self, tmp_path):
        from category_nav.directive import collect_categories

        (tmp_path / 'index.md').write_text('---\ncategory: Root\n---\n# Index')
        (tmp_path / 'glossary.md').write_text('---\ncategory: Reference\n---\n# Glossary')
        (tmp_path / 'real_doc.md').write_text('---\ncategory: Content\n---\n# Real')

        result = collect_categories(
            tmp_path,
            exclude=['index', 'glossary']
        )

        assert 'Root' not in result
        assert 'Reference' not in result
        assert 'Content' in result

    def test_handles_nested_directories(self, tmp_path):
        from category_nav.directive import collect_categories

        # Create nested structure
        (tmp_path / 'concepts').mkdir()
        (tmp_path / 'concepts' / 'idea.md').write_text(
            '---\ncategory: Philosophy\n---\n# Idea'
        )
        (tmp_path / 'methods').mkdir()
        (tmp_path / 'methods' / 'process.md').write_text(
            '---\ncategory: Methods\n---\n# Process'
        )

        result = collect_categories(tmp_path)

        assert 'Philosophy' in result
        assert 'Methods' in result
        # Check docnames include path
        philosophy_docs = [doc['docname'] for doc in result['Philosophy']]
        assert 'concepts/idea' in philosophy_docs

    def test_extracts_title_from_frontmatter_or_content(self, tmp_path):
        from category_nav.directive import collect_categories

        # Title in frontmatter
        (tmp_path / 'with_title.md').write_text(
            '---\ncategory: A\ntitle: Explicit Title\n---\n# H1 Title'
        )
        # Title from H1
        (tmp_path / 'from_h1.md').write_text(
            '---\ncategory: A\n---\n# Extracted From H1'
        )

        result = collect_categories(tmp_path)

        titles = {doc['docname']: doc['title'] for doc in result['A']}
        assert titles['with_title'] == 'Explicit Title'
        assert titles['from_h1'] == 'Extracted From H1'

    def test_sorts_documents_alphabetically_by_title(self, tmp_path):
        from category_nav.directive import collect_categories

        (tmp_path / 'z.md').write_text('---\ncategory: Test\n---\n# Zebra')
        (tmp_path / 'a.md').write_text('---\ncategory: Test\n---\n# Apple')
        (tmp_path / 'm.md').write_text('---\ncategory: Test\n---\n# Mango')

        result = collect_categories(tmp_path)

        titles = [doc['title'] for doc in result['Test']]
        assert titles == ['Apple', 'Mango', 'Zebra']

    def test_skips_files_starting_with_underscore(self, tmp_path):
        from category_nav.directive import collect_categories

        (tmp_path / '_private.md').write_text('---\ncategory: Hidden\n---\n# Private')
        (tmp_path / 'public.md').write_text('---\ncategory: Visible\n---\n# Public')

        result = collect_categories(tmp_path)

        assert 'Hidden' not in result

    def test_skips_unpublished_documents(self, tmp_path):
        from category_nav.directive import collect_categories

        # publish: false should be excluded
        (tmp_path / 'draft.md').write_text(
            '---\ncategory: Test\npublish: false\n---\n# Draft Doc'
        )
        # publish: true should be included
        (tmp_path / 'published.md').write_text(
            '---\ncategory: Test\npublish: true\n---\n# Published Doc'
        )
        # No publish key defaults to included (for backwards compatibility)
        (tmp_path / 'no_key.md').write_text(
            '---\ncategory: Test\n---\n# No Publish Key'
        )

        result = collect_categories(tmp_path)

        docnames = [doc['docname'] for doc in result['Test']]
        assert 'draft' not in docnames
        assert 'published' in docnames
        assert 'no_key' in docnames

    def test_skips_templates_directory(self, tmp_path):
        from category_nav.directive import collect_categories

        # Templates directory should be excluded
        (tmp_path / '_templates').mkdir()
        (tmp_path / '_templates' / 'note.md').write_text(
            '---\ncategory: Templates\n---\n# Note Template'
        )
        (tmp_path / '_templates' / 'daily.md').write_text(
            '---\ncategory: Templates\n---\n# Daily Template'
        )
        # Regular file should be included
        (tmp_path / 'normal.md').write_text(
            '---\ncategory: Content\n---\n# Normal Doc'
        )

        result = collect_categories(tmp_path)

        assert 'Templates' not in result
        assert 'Content' in result
        docnames = [doc['docname'] for docs in result.values() for doc in docs]
        assert '_templates/note' not in docnames
        assert '_templates/daily' not in docnames


class TestCategoryNavOutput:
    """Tests for the final toctree structure generation."""

    def test_categories_sorted_alphabetically(self, tmp_path):
        from category_nav.directive import collect_categories

        (tmp_path / 'z.md').write_text('---\ncategory: Zebras\n---\n# Z')
        (tmp_path / 'a.md').write_text('---\ncategory: Apples\n---\n# A')
        (tmp_path / 'm.md').write_text('---\ncategory: Mangos\n---\n# M')

        result = collect_categories(tmp_path)

        category_order = list(result.keys())
        assert category_order == sorted(category_order)

    def test_miscellaneous_sorted_last(self, tmp_path):
        from category_nav.directive import collect_categories

        (tmp_path / 'categorized.md').write_text('---\ncategory: Aardvarks\n---\n# A')
        (tmp_path / 'orphan.md').write_text('# No category')

        result = collect_categories(tmp_path, default_category='Miscellaneous')

        categories = list(result.keys())
        assert categories[-1] == 'Miscellaneous'


class TestMarkAsOrphan:
    """Tests for the mark_as_orphan event handler."""

    def test_marks_document_as_orphan(self):
        """Should set orphan metadata on document."""
        from category_nav import mark_as_orphan
        from unittest.mock import Mock

        app = Mock()
        app.env.metadata = {}

        mark_as_orphan(app, 'test-doc', ['source content'])

        assert app.env.metadata['test-doc']['orphan'] is True

    def test_preserves_existing_metadata(self):
        """Should not overwrite existing document metadata."""
        from category_nav import mark_as_orphan
        from unittest.mock import Mock

        app = Mock()
        app.env.metadata = {
            'test-doc': {'author': 'Test Author', 'title': 'Test Title'}
        }

        mark_as_orphan(app, 'test-doc', ['source content'])

        assert app.env.metadata['test-doc']['author'] == 'Test Author'
        assert app.env.metadata['test-doc']['title'] == 'Test Title'
        assert app.env.metadata['test-doc']['orphan'] is True


class TestCategoryNavSetup:
    """Tests for the Sphinx extension setup function."""

    def test_registers_category_nav_directive(self):
        """Setup should register the category-nav directive."""
        from category_nav import setup
        from category_nav.directive import CategoryNavDirective
        from unittest.mock import Mock

        app = Mock()
        setup(app)

        # Check add_directive was called with correct args
        app.add_directive.assert_called_once_with('category-nav', CategoryNavDirective)

    def test_registers_config_values(self):
        """Setup should register configuration values."""
        from category_nav import setup
        from unittest.mock import Mock

        app = Mock()
        setup(app)

        config_calls = {call[0][0]: call[0][1] for call in app.add_config_value.call_args_list}
        assert 'category_nav_default' in config_calls
        assert config_calls['category_nav_default'] == 'Miscellaneous'
        assert 'category_nav_exclude' in config_calls
        assert config_calls['category_nav_exclude'] == ['index', 'glossary']

    def test_connects_source_read_event(self):
        """Setup should connect to source-read event."""
        from category_nav import setup
        from unittest.mock import Mock

        app = Mock()
        setup(app)

        event_names = [call[0][0] for call in app.connect.call_args_list]
        assert 'source-read' in event_names

    def test_returns_extension_metadata(self):
        """Setup should return proper extension metadata."""
        from category_nav import setup
        from unittest.mock import Mock

        app = Mock()
        result = setup(app)

        assert 'version' in result
        assert result['parallel_read_safe'] is True
        assert result['parallel_write_safe'] is True


class TestCategoryNavDirectiveRun:
    """Tests for the CategoryNavDirective.run method."""

    def _create_mock_directive(self, tmp_path):
        """Create a properly mocked CategoryNavDirective instance."""
        from category_nav.directive import CategoryNavDirective
        from unittest.mock import Mock, patch, PropertyMock

        # Mock the state_machine and state to avoid initialization issues
        mock_state = Mock()
        mock_state_machine = Mock()

        # Create instance using object.__new__ to bypass __init__
        directive = object.__new__(CategoryNavDirective)

        # Set instance attributes directly on __dict__ to bypass property
        mock_env = Mock()
        mock_env.srcdir = str(tmp_path)
        mock_env.docname = 'index'

        mock_config = Mock()
        mock_config.category_nav_default = 'Miscellaneous'
        mock_config.category_nav_exclude = []

        # Store references on internal attributes
        directive._env = mock_env
        directive._config = mock_config

        return directive, mock_env, mock_config

    def test_run_returns_nodes_for_each_category(self, tmp_path):
        """Should return a node for each category."""
        from category_nav.directive import CategoryNavDirective
        from docutils import nodes
        from unittest.mock import Mock, patch

        # Create test files
        (tmp_path / 'doc1.md').write_text('---\ncategory: Alpha\n---\n# Doc 1')
        (tmp_path / 'doc2.md').write_text('---\ncategory: Beta\n---\n# Doc 2')

        # Mock the env and config properties
        mock_env = Mock()
        mock_env.srcdir = str(tmp_path)
        mock_env.docname = 'index'

        mock_config = Mock()
        mock_config.category_nav_default = 'Miscellaneous'
        mock_config.category_nav_exclude = []

        with patch.object(CategoryNavDirective, 'env', mock_env), \
             patch.object(CategoryNavDirective, 'config', mock_config):
            directive = object.__new__(CategoryNavDirective)
            result = directive.run()

        # Should have 2 sections (Alpha and Beta)
        assert len(result) == 2
        assert all(isinstance(node, nodes.section) for node in result)

    def test_run_creates_toctree_with_correct_entries(self, tmp_path):
        """Should create toctree with correct document entries."""
        from category_nav.directive import CategoryNavDirective
        from unittest.mock import Mock, patch

        (tmp_path / 'theory.md').write_text('---\ncategory: Theory\ntitle: Theory Doc\n---\n# Theory')

        mock_env = Mock()
        mock_env.srcdir = str(tmp_path)
        mock_env.docname = 'index'

        mock_config = Mock()
        mock_config.category_nav_default = 'Miscellaneous'
        mock_config.category_nav_exclude = []

        with patch.object(CategoryNavDirective, 'env', mock_env), \
             patch.object(CategoryNavDirective, 'config', mock_config):
            directive = object.__new__(CategoryNavDirective)
            result = directive.run()

        # Get the toctree from the section
        section = result[0]
        toc = section.children[0]

        assert toc['entries'] == [('Theory Doc', 'theory')]
        assert toc['includefiles'] == ['theory']

    def test_run_sets_toctree_attributes(self, tmp_path):
        """Should set correct toctree attributes."""
        from category_nav.directive import CategoryNavDirective
        from unittest.mock import Mock, patch

        (tmp_path / 'doc.md').write_text('---\ncategory: TestCat\n---\n# Doc')

        mock_env = Mock()
        mock_env.srcdir = str(tmp_path)
        mock_env.docname = 'index'

        mock_config = Mock()
        mock_config.category_nav_default = 'Miscellaneous'
        mock_config.category_nav_exclude = []

        with patch.object(CategoryNavDirective, 'env', mock_env), \
             patch.object(CategoryNavDirective, 'config', mock_config):
            directive = object.__new__(CategoryNavDirective)
            result = directive.run()
            toc = result[0].children[0]

        assert toc['caption'] == 'TestCat'
        assert toc['maxdepth'] == 2
        assert toc['glob'] is False
        assert toc['hidden'] is False
        assert toc['parent'] == 'index'

    def test_run_returns_empty_list_when_no_docs(self, tmp_path):
        """Should return empty list when no markdown files found."""
        from category_nav.directive import CategoryNavDirective
        from unittest.mock import Mock, patch

        mock_env = Mock()
        mock_env.srcdir = str(tmp_path)
        mock_env.docname = 'index'

        mock_config = Mock()
        mock_config.category_nav_default = 'Miscellaneous'
        mock_config.category_nav_exclude = []

        with patch.object(CategoryNavDirective, 'env', mock_env), \
             patch.object(CategoryNavDirective, 'config', mock_config):
            directive = object.__new__(CategoryNavDirective)
            result = directive.run()

        assert result == []

    def test_run_respects_exclude_list(self, tmp_path):
        """Should exclude files in category_nav_exclude config."""
        from category_nav.directive import CategoryNavDirective
        from unittest.mock import Mock, patch

        (tmp_path / 'index.md').write_text('---\ncategory: Root\n---\n# Index')
        (tmp_path / 'other.md').write_text('---\ncategory: Content\n---\n# Other')

        mock_env = Mock()
        mock_env.srcdir = str(tmp_path)
        mock_env.docname = 'index'

        mock_config = Mock()
        mock_config.category_nav_default = 'Miscellaneous'
        mock_config.category_nav_exclude = ['index']

        with patch.object(CategoryNavDirective, 'env', mock_env), \
             patch.object(CategoryNavDirective, 'config', mock_config):
            directive = object.__new__(CategoryNavDirective)
            result = directive.run()

        # Only 'Content' category (index excluded)
        assert len(result) == 1
        toc = result[0].children[0]
        assert toc['caption'] == 'Content'

    def test_run_section_has_proper_id(self, tmp_path):
        """Should generate proper section IDs from category names."""
        from category_nav.directive import CategoryNavDirective
        from unittest.mock import Mock, patch

        (tmp_path / 'doc.md').write_text('---\ncategory: My Category\n---\n# Doc')

        mock_env = Mock()
        mock_env.srcdir = str(tmp_path)
        mock_env.docname = 'index'

        mock_config = Mock()
        mock_config.category_nav_default = 'Miscellaneous'
        mock_config.category_nav_exclude = []

        with patch.object(CategoryNavDirective, 'env', mock_env), \
             patch.object(CategoryNavDirective, 'config', mock_config):
            directive = object.__new__(CategoryNavDirective)
            result = directive.run()

        # Check section ID format
        assert 'category-my-category' in result[0]['ids']
