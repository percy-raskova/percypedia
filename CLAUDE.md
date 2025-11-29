# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Percypedia is a personal encyclopedia/knowledge base built with Sphinx and MyST Markdown. It uses a three-layer taxonomy: directories (local organization), categories (website navigation), and tags (AI/Zettelkasten traversal). The site deploys to Cloudflare Pages.

## Quick Reference: Mise Commands

**ALWAYS use `mise run` for all project tasks.** This is the standard task runner.

| Command | When to Use |
|---------|-------------|
| `mise run build` | After editing content or extensions - builds HTML to `_build/html` |
| `mise run test` | After modifying `_extensions/` code - runs pytest |
| `mise run test:watch` | During TDD - stops on first failure |
| `mise run preview` | To view changes - live reload on port 8000 |
| `mise run clean` | Before fresh builds or when seeing stale output |

### All Available Commands

**Build & Preview:**
```bash
mise run build       # Build HTML to _build/html
mise run preview     # Live preview with auto-reload (port 8000)
mise run watch       # Auto-rebuild without opening browser
mise run serve       # Serve built docs (no auto-rebuild)
mise run clean       # Remove _build directory
mise run linkcheck   # Check for broken links
mise run pdf         # Build PDF via LaTeX
```

**Extension Development:**
```bash
mise run test        # Run extension tests
mise run test:watch  # TDD mode - stop on first failure
```

**Frontmatter Tools:**
```bash
mise run fm:validate   # Validate frontmatter against schema
mise run fm:report     # Report on frontmatter status
mise run fm:normalize  # Normalize all frontmatter (creates backups)
mise run fm:dry-run    # Dry run normalization (no changes)
mise run fm:test       # Run frontmatter normalizer tests
```

### CI Build (Cloudflare Pages only)

```bash
./build.sh           # Full pipenv-based build - DO NOT use locally
```

### Dependency Management

- **Local dev**: `.venv/` with `requirements.txt` (auto-activated by mise)
- **CI only**: `Pipfile` + `Pipfile.lock` (pipenv)
- Python 3.13 required

## Architecture

### Custom Sphinx Extensions (`_extensions/`)

Four local extensions plus a shared module power the system:

**category_nav** - Generates navigation from frontmatter
- `extract_frontmatter()` - Parse YAML from markdown (from `_common.frontmatter`)
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

**_common** - Shared utilities for extensions
- `frontmatter.py` - YAML frontmatter extraction (single source of truth)
- `traversal.py` - Unified `iter_markdown_files()` for directory walking
- Used by: category_nav, frontmatter_schema, publish_filter

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

Test files are colocated: `_extensions/<name>/tests/test_<name>.py`
