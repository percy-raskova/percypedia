---
category: Meta
---

# Frontmatter Schema Reference

Canonical reference for YAML frontmatter fields in Percypedia documents. The authoritative source is `_schemas/frontmatter.schema.json`.

## Quick Reference

```yaml
---
zkid: 202411281430
author: Percy
title: "Document Title"
description: "Brief summary for SEO."
date-created: 2024-11-28
date-edited: 2024-11-28
category: Theory
tags:
  - theory/marxism
  - politics/strategy
publish: true
status: complete
---
```

## Field Definitions

### Identity Fields

#### zkid

Zettelkasten ID. Immutable identifier in `YYYYMMDDHHMM` format.

| Property | Value |
|----------|-------|
| Type | string |
| Pattern | `^[0-9]{12}$` |
| Required | No |
| Consumed by | Future database integration |

```yaml
zkid: 202411281430
```

#### author

Document author name.

| Property | Value |
|----------|-------|
| Type | string |
| Required | No |
| Default | Percy |
| Consumed by | Future multi-author display |

### Document Fields

#### title

Document title. If omitted, falls back to the first H1 heading in content.

| Property | Value |
|----------|-------|
| Type | string |
| Min length | 1 |
| Required | No |
| Consumed by | `category_nav`, Sphinx page titles |

#### description

Brief summary for SEO meta tags and social sharing.

| Property | Value |
|----------|-------|
| Type | string |
| Max length | 160 characters |
| Required | No |
| Consumed by | Future meta tag generation |

### Timestamp Fields

#### date-created

Document creation date. Should be immutable after initial creation.

| Property | Value |
|----------|-------|
| Type | string |
| Format | `YYYY-MM-DD` |
| Required | No |
| Consumed by | Future sorting/display |

#### date-edited

Last modification date. Update on each revision.

| Property | Value |
|----------|-------|
| Type | string |
| Format | `YYYY-MM-DD` |
| Required | No |
| Consumed by | Future "recently updated" features |

### Navigation Fields

#### category

Website sidebar grouping. One document belongs to exactly one category.

| Property | Value |
|----------|-------|
| Type | string |
| Required | No |
| Default | Miscellaneous |
| Consumed by | `category_nav` extension |

Categories are dynamic - any string value creates a new category in the sidebar. Common categories:

- **Theory** - Analytical frameworks
- **Infrastructure** - Meta-documentation
- **Concepts** - Foundational ideas
- **Methods** - Practical approaches

#### tags

Hierarchical tags for AI/Zettelkasten navigation. Unlike categories, a document can have unlimited tags.

| Property | Value |
|----------|-------|
| Type | array of strings |
| Item pattern | `^[a-z0-9]+(/[a-z0-9-]+)*$` |
| Required | No |
| Consumed by | `sphinx-tags` extension |

Tag format rules:

- Lowercase only
- Use `/` for hierarchy
- Use `-` for multi-word segments
- No spaces

```yaml
# Valid tags
tags:
  - theory
  - theory/marxism
  - politics/labor-aristocracy
  - organizing/strategy/community

# Invalid tags
tags:
  - Theory/Marxism        # uppercase
  - theory marxism        # spaces
  - theory/Labor-Theory   # uppercase
```

### Publication Fields

#### publish

Controls build inclusion. Documents with `publish: false` are excluded from the Sphinx build entirely.

| Property | Value |
|----------|-------|
| Type | boolean |
| Default | true |
| Required | No |
| Consumed by | `publish_filter` extension |

```yaml
publish: false  # Draft, excluded from build
publish: true   # Published, included in build
# (omitted)     # Defaults to published
```

#### status

Editorial workflow status. More granular than `publish` for tracking document maturity.

| Property | Value |
|----------|-------|
| Type | enum |
| Values | `draft`, `review`, `complete` |
| Default | draft |
| Required | No |
| Consumed by | Future workflow tooling |

| Status | Meaning |
|--------|---------|
| `draft` | Work in progress |
| `review` | Needs editing/feedback |
| `complete` | Finished and stable |

## Validation

### Schema Location

The JSON Schema lives at `_schemas/frontmatter.schema.json`.

### Programmatic Validation

```python
from frontmatter_schema import validate_frontmatter, validate_file

# Validate a dictionary
errors = validate_frontmatter({
    'title': 'Test',
    'status': 'invalid'  # Will error
})

# Validate a file
errors = validate_file(Path('docs/example.md'))

# Validate all files in a directory
from frontmatter_schema import validate_directory
results = validate_directory(Path('.'))
for filepath, errors in results.items():
    print(f"{filepath}: {errors}")
```

### Running Tests

```bash
mise run test
```

## Migration Notes

### Deprecated Fields

These fields should no longer be used:

| Old Field | Replacement |
|-----------|-------------|
| `id` | `zkid` |
| `created` | `date-created` |
| `updated` | `date-edited` |
| `slug` | Remove (auto-generated) |
| `confidence` | Remove (unused) |
| `related` | Remove (unused) |

### Strict Mode

The schema uses `additionalProperties: false`. Unknown fields will fail validation. Remove deprecated fields before enabling schema validation in CI.
