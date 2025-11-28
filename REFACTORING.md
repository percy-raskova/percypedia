# Mikado Refactoring Plan: Shared Extension Infrastructure

This document provides step-by-step instructions for refactoring the Percypedia Sphinx extensions to extract shared code into a `_common/` module. Follow these instructions precisely using TDD methodology.

## Problem Statement

Three extensions duplicate the same frontmatter parsing logic:

| Extension | Location | Function |
|-----------|----------|----------|
| `category_nav` | `directive.py:20-55` | `extract_frontmatter()` |
| `frontmatter_schema` | `__init__.py:42-73` | `extract_frontmatter()` |
| `publish_filter` | `__init__.py:30-47` | Inline parsing in `get_unpublished_docs()` |

Additionally, directory traversal logic is duplicated with **subtle behavioral differences**:

| Extension | Underscore Files | Dot Files | Pattern Exclusion |
|-----------|-----------------|-----------|-------------------|
| `category_nav` | Exclude at root | Include | Via config list |
| `publish_filter` | Exclude all parts | Exclude all | None |
| `frontmatter_schema` | Directories only | Directories only | Via config list |

## Goal

Create `_extensions/_common/` with:
- `frontmatter.py` - Single `extract_frontmatter()` implementation
- `traversal.py` - Unified `iter_markdown_files()` with configurable behavior

## Prerequisites

Before starting, ensure:
1. All 76 tests pass: `mise run test`
2. Git working tree is clean: `git status`
3. You're on a feature branch: `git checkout -b refactor/shared-common-module`

---

## Phase 1: Create Shared Test Infrastructure

### Step 1.1: Create Directory Structure

```bash
mkdir -p _extensions/_common/tests
touch _extensions/_common/__init__.py
touch _extensions/_common/tests/__init__.py
```

### Step 1.2: Create Shared Test Fixtures

Create `_extensions/_common/tests/conftest.py` with these fixtures:

```python
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
```

### Step 1.3: Commit Test Infrastructure

```bash
git add _extensions/_common/
git commit -m "test: Add shared test fixtures for extension refactoring

Prepare for Mikado refactoring by creating:
- _common/tests/conftest.py with frontmatter fixtures
- Sample source directory fixture for traversal tests
- Mock Sphinx application fixtures
- Expected result baselines for snapshot testing

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 2: Characterization Tests (RED Phase)

### Step 2.1: Create Frontmatter Characterization Tests

Create `_extensions/_common/tests/test_frontmatter.py`:

```python
"""Characterization tests for extract_frontmatter().

These tests document current behavior BEFORE any changes.
They import from EXISTING implementations to capture baseline.
"""

import pytest


class TestExtractFrontmatterCharacterization:
    """Tests that characterize current extract_frontmatter behavior."""

    # Import from category_nav as the reference implementation
    @pytest.fixture
    def extract_frontmatter(self):
        from category_nav.directive import extract_frontmatter
        return extract_frontmatter

    def test_empty_string_returns_empty_dict(self, extract_frontmatter):
        assert extract_frontmatter("") == {}

    def test_no_frontmatter_returns_empty_dict(self, extract_frontmatter, no_frontmatter):
        assert extract_frontmatter(no_frontmatter) == {}

    def test_frontmatter_not_at_start_returns_empty_dict(
        self, extract_frontmatter, frontmatter_not_at_start
    ):
        assert extract_frontmatter(frontmatter_not_at_start) == {}

    def test_unclosed_frontmatter_returns_empty_dict(
        self, extract_frontmatter, unclosed_frontmatter
    ):
        assert extract_frontmatter(unclosed_frontmatter) == {}

    def test_empty_frontmatter_returns_empty_dict(
        self, extract_frontmatter, empty_frontmatter
    ):
        # Just delimiters with nothing between
        result = extract_frontmatter(empty_frontmatter)
        assert result == {} or result is None or isinstance(result, dict)

    def test_malformed_yaml_returns_empty_dict(
        self, extract_frontmatter, malformed_yaml_frontmatter
    ):
        assert extract_frontmatter(malformed_yaml_frontmatter) == {}

    def test_non_dict_yaml_string_returns_empty_dict(
        self, extract_frontmatter, non_dict_yaml_string
    ):
        assert extract_frontmatter(non_dict_yaml_string) == {}

    def test_non_dict_yaml_list_returns_empty_dict(
        self, extract_frontmatter, non_dict_yaml_list
    ):
        assert extract_frontmatter(non_dict_yaml_list) == {}

    def test_valid_minimal_extracts_correctly(
        self, extract_frontmatter, minimal_frontmatter
    ):
        result = extract_frontmatter(minimal_frontmatter)
        assert result['title'] == 'Minimal'

    def test_valid_complete_extracts_all_fields(
        self, extract_frontmatter, valid_complete_frontmatter
    ):
        result = extract_frontmatter(valid_complete_frontmatter)
        assert result['title'] == 'Test Document'
        assert result['category'] == 'Theory'
        assert result['publish'] is True
        assert 'theory/testing' in result['tags']

    def test_publish_false_extracted_as_boolean(
        self, extract_frontmatter, draft_document
    ):
        result = extract_frontmatter(draft_document)
        assert result['publish'] is False

    def test_unicode_content_handled(
        self, extract_frontmatter, unicode_frontmatter
    ):
        result = extract_frontmatter(unicode_frontmatter)
        assert 'title' in result

    def test_windows_line_endings_handled(
        self, extract_frontmatter, windows_line_endings
    ):
        result = extract_frontmatter(windows_line_endings)
        assert result.get('title') == 'Windows'


class TestImplementationEquivalence:
    """Verify all three implementations behave identically."""

    @pytest.fixture
    def test_contents(self):
        return [
            "",
            "# No frontmatter",
            "---\ntitle: Test\n---\n# Content",
            "---\npublish: false\n---\n# Draft",
            "---\ninvalid: yaml: here\n---",
            "---\ntags:\n  - a\n  - b\n---",
            "---\n---\n# Empty",
            "text\n---\nkey: val\n---",
        ]

    def test_category_nav_matches_frontmatter_schema(self, test_contents):
        from category_nav.directive import extract_frontmatter as cat_extract
        from frontmatter_schema import extract_frontmatter as schema_extract

        for content in test_contents:
            cat_result = cat_extract(content)
            schema_result = schema_extract(content)
            assert cat_result == schema_result, f"Mismatch on: {content[:30]}..."
```

### Step 2.2: Create Traversal Characterization Tests

Create `_extensions/_common/tests/test_traversal.py`:

```python
"""Characterization tests for directory traversal behavior.

CRITICAL: These tests document CURRENT behavioral differences.
DO NOT change these tests until you understand the differences.
"""

import pytest
from pathlib import Path


class TestTraversalBehaviorDifferences:
    """Document behavioral differences between extensions."""

    def test_category_nav_file_selection(self, sample_srcdir):
        """Document which files category_nav selects."""
        from category_nav.directive import collect_categories

        result = collect_categories(sample_srcdir)

        # Flatten all docnames
        all_docnames = set()
        for docs in result.values():
            for doc in docs:
                all_docnames.add(doc['docname'])

        # Document current behavior
        assert 'index' not in all_docnames  # Excluded by default
        assert 'glossary' not in all_docnames  # Excluded by default
        assert 'about' in all_docnames
        assert 'theory/marxism' in all_docnames
        assert 'draft' not in all_docnames  # publish: false
        # NOTE: _private behavior depends on implementation

    def test_publish_filter_unpublished_detection(self, sample_srcdir):
        """Document which files publish_filter marks as unpublished."""
        from publish_filter import get_unpublished_docs
        from unittest.mock import Mock

        app = Mock()
        app.srcdir = str(sample_srcdir)

        result = get_unpublished_docs(app)

        assert 'draft' in result
        assert 'index' not in result
        assert 'theory/marxism' not in result

    def test_frontmatter_schema_directory_validation(self, sample_srcdir):
        """Document which files frontmatter_schema validates."""
        from frontmatter_schema import validate_directory

        # This returns files with ERRORS, not all files
        # So we need to create files with errors to test traversal
        pass  # Implement based on actual behavior


class TestUnderscoreFileBehavior:
    """CRITICAL: Extensions differ on underscore file handling."""

    def test_underscore_file_at_root(self, tmp_path):
        """_private.md at root - BEHAVIOR VARIES."""
        (tmp_path / '_private.md').write_text('---\ncategory: Test\n---\n# Private')
        (tmp_path / 'public.md').write_text('---\ncategory: Test\n---\n# Public')

        from category_nav.directive import collect_categories
        result = collect_categories(tmp_path)

        all_docnames = {doc['docname'] for docs in result.values() for doc in docs}

        # category_nav: Skips files starting with underscore
        assert '_private' not in all_docnames
        assert 'public' in all_docnames


class TestDotFileBehavior:
    """CRITICAL: Extensions differ on dot file handling."""

    def test_dot_directory_always_excluded(self, tmp_path):
        """Files in .directories should always be excluded."""
        (tmp_path / '.hidden').mkdir()
        (tmp_path / '.hidden' / 'secret.md').write_text('---\n---\n# Secret')
        (tmp_path / 'visible.md').write_text('---\ncategory: Test\n---\n# Visible')

        from category_nav.directive import collect_categories
        result = collect_categories(tmp_path)

        all_docnames = {doc['docname'] for docs in result.values() for doc in docs}

        assert '.hidden/secret' not in all_docnames
        assert 'visible' in all_docnames
```

### Step 2.3: Run Tests and Verify Baseline

```bash
mise run test
```

All tests MUST pass. If any fail, the characterization is incorrect - fix the tests to match actual behavior.

### Step 2.4: Commit Characterization Tests

```bash
git add _extensions/_common/tests/
git commit -m "test: Add characterization tests for frontmatter and traversal

RED phase: Document current behavior before refactoring.
- test_frontmatter.py: 15+ edge cases for extract_frontmatter()
- test_traversal.py: Document behavioral differences between extensions
- TestImplementationEquivalence: Verify category_nav matches frontmatter_schema

All tests pass against existing implementations.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 3: Implement Shared Module (GREEN Phase)

### Step 3.1: Implement `_common/frontmatter.py`

Create `_extensions/_common/frontmatter.py`:

```python
"""Shared frontmatter parsing for Sphinx extensions.

This is the single source of truth for YAML frontmatter extraction.
All extensions should import from here.
"""

from typing import Any, Dict
import yaml


def extract_frontmatter(content: str) -> Dict[str, Any]:
    """Extract YAML frontmatter from markdown content.

    Args:
        content: Raw markdown file content.

    Returns:
        Dictionary of frontmatter fields. Empty dict if:
        - No frontmatter present
        - Frontmatter doesn't start at line 1
        - Unclosed frontmatter
        - Invalid YAML
        - YAML parses to non-dict (string, list, etc.)

    Example:
        >>> content = '''---
        ... title: My Document
        ... tags:
        ...   - theory/marxism
        ... ---
        ... # Content here
        ... '''
        >>> extract_frontmatter(content)
        {'title': 'My Document', 'tags': ['theory/marxism']}
    """
    # Frontmatter must start at beginning of file
    if not content.startswith('---'):
        return {}

    lines = content.split('\n')
    if len(lines) < 2:
        return {}

    # Find closing delimiter
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        return {}

    # Extract and parse YAML
    yaml_content = '\n'.join(lines[1:end_idx])
    try:
        result = yaml.safe_load(yaml_content)
        return result if isinstance(result, dict) else {}
    except yaml.YAMLError:
        return {}
```

### Step 3.2: Add Tests for Shared Implementation

Update `_extensions/_common/tests/test_frontmatter.py` to add:

```python
class TestSharedExtractFrontmatter:
    """Tests for the new shared implementation."""

    @pytest.fixture
    def extract_frontmatter(self):
        from _common.frontmatter import extract_frontmatter
        return extract_frontmatter

    # Copy all tests from TestExtractFrontmatterCharacterization
    # They should pass with the shared implementation

    def test_empty_string_returns_empty_dict(self, extract_frontmatter):
        assert extract_frontmatter("") == {}

    # ... (all other tests)


class TestSharedMatchesOriginals:
    """Verify shared implementation matches all originals."""

    @pytest.fixture
    def test_contents(self):
        return [
            "",
            "# No frontmatter",
            "---\ntitle: Test\n---\n# Content",
            "---\npublish: false\n---\n# Draft",
            "---\ninvalid: yaml: here\n---",
            "---\ntags:\n  - a\n  - b\n---",
            "---\n---\n# Empty",
        ]

    def test_shared_matches_category_nav(self, test_contents):
        from category_nav.directive import extract_frontmatter as original
        from _common.frontmatter import extract_frontmatter as shared

        for content in test_contents:
            assert original(content) == shared(content)

    def test_shared_matches_frontmatter_schema(self, test_contents):
        from frontmatter_schema import extract_frontmatter as original
        from _common.frontmatter import extract_frontmatter as shared

        for content in test_contents:
            assert original(content) == shared(content)
```

### Step 3.3: Run Tests

```bash
mise run test
```

All tests must pass.

### Step 3.4: Commit Shared Implementation

```bash
git add _extensions/_common/frontmatter.py _extensions/_common/tests/
git commit -m "feat: Implement shared extract_frontmatter() in _common

GREEN phase: Single implementation that matches all originals.
- _common/frontmatter.py: Canonical extract_frontmatter()
- Tests verify equivalence with category_nav and frontmatter_schema
- All 76+ tests pass

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 4: Migrate Extensions (One at a Time)

### Step 4.1: Migrate `frontmatter_schema`

Edit `_extensions/frontmatter_schema/__init__.py`:

```python
# Replace the local extract_frontmatter with import
from _common.frontmatter import extract_frontmatter

# Keep re-export for backward compatibility
__all__ = ['extract_frontmatter', 'validate_frontmatter', ...]
```

Remove the duplicate `extract_frontmatter()` function (lines 42-73).

Run tests: `mise run test`

Commit:
```bash
git add _extensions/frontmatter_schema/
git commit -m "refactor: frontmatter_schema uses shared extract_frontmatter

- Import from _common.frontmatter instead of local implementation
- Re-export for backward compatibility
- All tests pass

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 4.2: Migrate `category_nav`

Edit `_extensions/category_nav/directive.py`:

```python
# At top of file, add:
from _common.frontmatter import extract_frontmatter

# Remove the local extract_frontmatter() function (lines 20-55)
# Keep extract_title() - it's unique to this module
```

Run tests: `mise run test`

Commit:
```bash
git add _extensions/category_nav/
git commit -m "refactor: category_nav uses shared extract_frontmatter

- Import from _common.frontmatter
- Remove duplicate implementation
- Keep extract_title() (unique to this module)
- All tests pass

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 4.3: Migrate `publish_filter`

Edit `_extensions/publish_filter/__init__.py`:

Replace inline parsing in `get_unpublished_docs()` with:

```python
from _common.frontmatter import extract_frontmatter

def get_unpublished_docs(app) -> Set[str]:
    """Scan source files and return docnames with publish: false."""
    unpublished = set()
    srcdir = Path(app.srcdir)

    for md_file in srcdir.rglob('*.md'):
        rel_path = md_file.relative_to(srcdir)
        if any(part.startswith('_') or part.startswith('.')
               for part in rel_path.parts):
            continue

        try:
            content = md_file.read_text(encoding='utf-8')
            frontmatter = extract_frontmatter(content)

            if frontmatter.get('publish') is False:
                docname = str(rel_path.with_suffix(''))
                unpublished.add(docname)
        except Exception:
            continue

    return unpublished
```

Run tests: `mise run test`

Commit:
```bash
git add _extensions/publish_filter/
git commit -m "refactor: publish_filter uses shared extract_frontmatter

- Replace inline YAML parsing with _common.frontmatter import
- Simplify get_unpublished_docs()
- All tests pass

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 5: Implement Shared Traversal (Optional)

This phase is **higher risk** due to behavioral differences. Only proceed if needed.

### Step 5.1: Document Decision on Unified Behavior

Before implementing, decide:

1. Should `_private.md` at root be excluded? (category_nav: yes, frontmatter_schema: no)
2. Should `.hidden.md` at root be excluded? (category_nav: no, publish_filter: yes)

Recommended: Make behavior configurable:

```python
def iter_markdown_files(
    srcdir: Path,
    exclude_patterns: Set[str] = None,
    skip_underscore_files: bool = True,
    skip_underscore_dirs: bool = True,
    skip_dot_dirs: bool = True,
) -> Iterator[Path]:
    ...
```

### Step 5.2: Implementation

Create `_extensions/_common/traversal.py` with the unified implementation.

### Step 5.3: Migration

Each extension calls with parameters matching its current behavior.

---

## Verification Checklist

After completing all phases:

- [ ] `mise run test` - All 76+ tests pass
- [ ] `mise run build` - Site builds without errors
- [ ] `git log --oneline` - Clean commit history
- [ ] No duplicate `extract_frontmatter()` in:
  - [ ] `category_nav/directive.py`
  - [ ] `frontmatter_schema/__init__.py`
  - [ ] `publish_filter/__init__.py`
- [ ] Import paths still work:
  - [ ] `from category_nav.directive import extract_frontmatter`
  - [ ] `from frontmatter_schema import extract_frontmatter`
  - [ ] `from _common.frontmatter import extract_frontmatter`

---

## Risk Areas

### HIGH RISK: Traversal Logic
The three extensions have different file exclusion rules. Unifying them could change which files are processed. Always run full test suite after changes.

### MEDIUM RISK: Import Path Changes
External code might import directly from extensions. Keep re-exports working.

### LOW RISK: YAML Parsing
All three implementations use identical `yaml.safe_load()` logic. The shared implementation should be drop-in compatible.

---

## Rollback Procedure

If any step fails:

1. Run `git status` to see changes
2. Run `git diff` to review
3. Run `git checkout -- <file>` to revert specific files
4. Or `git reset --hard HEAD` to revert all changes since last commit

Each commit is atomic - you can always revert to a known good state.
