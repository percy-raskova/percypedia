# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Percypedia is a personal encyclopedia/knowledge base built with Sphinx and MyST Markdown. It uses a three-layer taxonomy: directories (local organization), categories (website navigation), and tags (AI/Zettelkasten traversal). The site deploys to Cloudflare Pages.

## Commands

### Local Development

```bash
mise run build       # Build HTML to _build/html
mise run preview     # Live preview with auto-reload (port 8000)
mise run watch       # Auto-rebuild without opening browser
mise run serve       # Serve built docs (no auto-rebuild)
mise run clean       # Remove _build directory
mise run test        # Run extension tests
mise run test:watch  # Run tests, stop on first failure
```

### CI Build

```bash
./build.sh           # Full pipenv-based build (Cloudflare Pages)
```

### Dependency Management

- Local dev: `.venv/` with `requirements.txt`
- CI: `Pipfile` + `Pipfile.lock` (pipenv)
- Python 3.13 required

## Architecture

### Custom Sphinx Extensions (`_extensions/`)

Three local extensions power the system:

**category_nav** - Generates navigation from frontmatter
- `extract_frontmatter()` - Parse YAML from markdown
- `collect_categories()` - Group files by `category:` field
- `CategoryNavDirective` - Renders `{category-nav}` directive as toctrees
- Config: `category_nav_default`, `category_nav_exclude` in conf.py

**publish_filter** - Draft/publish workflow
- Excludes docs with `publish: false` from builds
- Strips Obsidian comments (`%%...%%`) from output
- Hooks into `builder-inited` and `source-read` events

**frontmatter_schema** - Validation utilities
- JSON Schema at `_schemas/frontmatter.schema.json`
- `validate_frontmatter()` - Validate dict against schema
- `validate_file()` / `validate_directory()` - Batch validation
- See `docs/frontmatter-schema.md` for field reference

**missing_refs** - Track forward-links to unwritten docs
- Captures `{doc}` cross-references to non-existent documents
- Outputs `_build/html/missing_refs.json` with targets grouped by category
- Optional: Set `missing_refs_generate_page = True` in conf.py to auto-generate a "Planned Articles" page

### Frontmatter Schema

```yaml
---
category: Concepts          # Website sidebar grouping (single value)
tags:                       # AI/search navigation (multiple values)
  - theory/class-analysis
  - politics/marxism
publish: false              # Draft (excluded) or true/missing (included)
---
```

### Key Directories

- `_extensions/` - Custom Sphinx extensions with tests
- `_templates/` - Note templates (note.md, daily.md)
- `_static/` - CSS and static assets
- `private/` - Excluded from git and builds
- `docs/` - Infrastructure documentation

### Extension Testing

Tests use pytest. Run from repo root:

```bash
PYTHONPATH=_extensions pytest _extensions/ -v
```

Test files are colocated: `_extensions/category_nav/tests/test_category_nav.py`
