# _common - Shared Extension Utilities

Shared utilities extracted during the Mikado refactoring to eliminate code duplication.

## Modules

### frontmatter.py

Single source of truth for YAML frontmatter extraction.

```python
from _common.frontmatter import extract_frontmatter

content = '''---
title: Example
category: Concepts
---
# Content
'''

frontmatter = extract_frontmatter(content)
# {'title': 'Example', 'category': 'Concepts'}
```

**Behavior:**
- Returns `{}` if no frontmatter or invalid YAML
- Frontmatter must start at line 1 with `---`
- Handles edge cases: unclosed delimiters, non-dict YAML, malformed syntax

**Used by:**
- `category_nav.directive` - For collecting categories
- `frontmatter_schema` - For validation
- `publish_filter` - For detecting `publish: false`

## Why This Exists

Before refactoring, three extensions had identical `extract_frontmatter()` implementations. This module centralizes the logic to:
- Prevent drift between implementations
- Single place for bug fixes
- Easier testing (113 tests verify equivalence)

## Adding New Shared Utilities

If you find duplicated code across extensions:
1. Add the utility to `_common/`
2. Write characterization tests first (document current behavior)
3. Migrate extensions one at a time
4. Verify all tests pass after each migration
