# Percypedia Sphinx Extensions

Custom Sphinx extensions for the Percypedia knowledge base.

## Extensions

| Extension | Purpose | Key Functions |
|-----------|---------|---------------|
| `category_nav` | Generate navigation from frontmatter | `collect_categories()`, `CategoryNavDirective` |
| `publish_filter` | Draft/publish workflow | `get_unpublished_docs()`, `strip_obsidian_comments()` |
| `frontmatter_schema` | JSON Schema validation | `validate_frontmatter()`, `validate_directory()` |
| `missing_refs` | Track forward-links | `MissingRefsCollector`, outputs `missing_refs.json` |
| `_common` | Shared utilities | `extract_frontmatter()` |

## Architecture

```
_extensions/
├── _common/              # Shared utilities (not a Sphinx extension)
│   ├── frontmatter.py    # YAML frontmatter parsing
│   └── tests/
├── category_nav/         # Sphinx extension
│   ├── __init__.py       # Extension entry point
│   ├── directive.py      # Main implementation
│   └── tests/
├── frontmatter_schema/   # Sphinx extension (optional)
├── missing_refs/         # Sphinx extension
└── publish_filter/       # Sphinx extension
```

## Dependency Graph

```
category_nav ──────┐
frontmatter_schema ├──► _common.frontmatter.extract_frontmatter()
publish_filter ────┘
```

## Testing

Run all extension tests:
```bash
mise run test
```

Run specific extension tests:
```bash
PYTHONPATH=_extensions pytest _extensions/category_nav/tests/ -v
```

## Adding a New Extension

1. Create directory: `_extensions/my_extension/`
2. Add `__init__.py` with `setup(app)` function
3. Register in `conf.py` extensions list
4. Add tests in `my_extension/tests/`
5. Import shared utilities from `_common` as needed
