"""Shared test fixtures for Sphinx extension tests."""

import pytest
from pathlib import Path
from unittest.mock import Mock


# =============================================================================
# Frontmatter Content Fixtures
# =============================================================================

@pytest.fixture
def valid_complete_frontmatter():
    """Complete valid frontmatter with all fields."""
    return """---
zkid: '202411281430'
author: Test Author
title: Test Document
description: A test document.
date-created: '2024-11-28'
date-edited: '2024-11-28'
category: Theory
tags:
  - theory/testing
  - meta/fixtures
publish: true
status: complete
---

# Test Document

Content here.
"""


@pytest.fixture
def minimal_frontmatter():
    """Minimal valid frontmatter."""
    return """---
title: Minimal
---

# Minimal
"""


@pytest.fixture
def no_frontmatter():
    """Content without frontmatter."""
    return """# Just a Heading

Regular markdown content.
"""


@pytest.fixture
def malformed_yaml_frontmatter():
    """Invalid YAML syntax."""
    return """---
this: is: not: valid: yaml
---

# Content
"""


@pytest.fixture
def unclosed_frontmatter():
    """Missing closing delimiter."""
    return """---
title: Unclosed
category: Broken
"""


@pytest.fixture
def frontmatter_not_at_start():
    """Frontmatter not at line 1."""
    return """Some text first.

---
title: Won't Work
---
"""


@pytest.fixture
def empty_frontmatter():
    """Just delimiters."""
    return """---
---

# Empty
"""


@pytest.fixture
def draft_document():
    """Document with publish: false."""
    return """---
title: Draft
publish: false
---

# Draft
"""


@pytest.fixture
def non_dict_yaml_string():
    """YAML parses to string."""
    return """---
just a plain string
---
"""


@pytest.fixture
def non_dict_yaml_list():
    """YAML parses to list."""
    return """---
- item one
- item two
---
"""


@pytest.fixture
def windows_line_endings():
    """Windows CRLF."""
    return "---\r\ntitle: Windows\r\n---\r\n# Doc\r\n"


@pytest.fixture
def unicode_frontmatter():
    """Unicode characters."""
    return """---
title: Teoría del Valor
author: Carlos Marx
---

# Teoría
"""


# =============================================================================
# Sample Source Directory Fixture
# =============================================================================

@pytest.fixture
def sample_srcdir(tmp_path):
    """Create realistic source directory for traversal tests."""

    # Root documents
    (tmp_path / 'index.md').write_text('---\ntitle: Home\n---\n# Index')
    (tmp_path / 'glossary.md').write_text('---\ntitle: Glossary\n---\n# Glossary')
    (tmp_path / 'about.md').write_text('---\ncategory: Meta\n---\n# About')

    # Nested - theory/
    (tmp_path / 'theory').mkdir()
    (tmp_path / 'theory' / 'marxism.md').write_text(
        '---\ncategory: Theory\ntags:\n  - theory/marxism\n---\n# Marxism'
    )
    (tmp_path / 'theory' / 'dialectics.md').write_text(
        '---\ncategory: Theory\npublish: true\n---\n# Dialectics'
    )

    # Nested - concepts/
    (tmp_path / 'concepts').mkdir()
    (tmp_path / 'concepts' / 'value.md').write_text(
        '---\ncategory: Concepts\n---\n# Value Theory'
    )

    # Draft (publish: false)
    (tmp_path / 'draft.md').write_text(
        '---\ntitle: Draft\npublish: false\n---\n# Draft'
    )

    # Underscore files (behavior varies!)
    (tmp_path / '_private.md').write_text('---\ntitle: Private\n---\n# Private')

    # Underscore directories (always excluded)
    (tmp_path / '_templates').mkdir()
    (tmp_path / '_templates' / 'note.md').write_text('---\n---\n# Template')

    (tmp_path / '_build').mkdir()
    (tmp_path / '_build' / 'output.md').write_text('# Build')

    # Dot directories (always excluded)
    (tmp_path / '.git').mkdir()
    (tmp_path / '.git' / 'config').write_text('config')

    (tmp_path / '.venv').mkdir()
    (tmp_path / '.venv' / 'readme.md').write_text('# venv')

    # Deeply nested
    (tmp_path / 'theory' / 'advanced').mkdir()
    (tmp_path / 'theory' / 'advanced' / 'deep.md').write_text(
        '---\ncategory: Theory\n---\n# Deep'
    )

    return tmp_path


# =============================================================================
# Mock Sphinx Fixtures
# =============================================================================

@pytest.fixture
def mock_sphinx_app(tmp_path):
    """Mock Sphinx application."""
    app = Mock()
    app.srcdir = str(tmp_path)
    app.outdir = str(tmp_path / '_build' / 'html')
    app.config = Mock()
    app.config.exclude_patterns = []
    app.connect = Mock()
    app.add_config_value = Mock()
    return app


# =============================================================================
# Expected Results (Snapshot Baselines)
# =============================================================================

@pytest.fixture
def expected_category_nav_docnames():
    """Files category_nav should find."""
    return {
        'index', 'glossary', 'about',
        'theory/marxism', 'theory/dialectics', 'theory/advanced/deep',
        'concepts/value',
        # NOT: draft, _private, _templates/*, .venv/*
    }


@pytest.fixture
def expected_unpublished_docnames():
    """Files with publish: false."""
    return {'draft'}
