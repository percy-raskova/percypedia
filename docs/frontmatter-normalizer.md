---
category: Meta
---

# Frontmatter Normalizer Tool

The frontmatter normalizer is an ML-powered tool that standardizes YAML frontmatter across all markdown files. It migrates deprecated fields, infers missing values, and ensures schema compliance.

## Quick Start

```bash
# See what would change (no modifications)
mise run fm:dry-run

# Actually normalize all files (creates .bak backups)
mise run fm:normalize

# Validate against schema
mise run fm:validate

# Generate status report
mise run fm:report
```

## What It Does

### Field Migration

Automatically renames deprecated fields:

| Old Field | New Field |
|-----------|-----------|
| `id` | `zkid` |
| `created` | `date-created` |
| `updated` | `date-edited` |

### Field Inference

Uses ML models to infer missing values:

| Field | Inference Method |
|-------|------------------|
| `zkid` | Generated from file modification time |
| `title` | Extracted from first H1 heading |
| `author` | Default: "Percy" |
| `date-created` | From file creation time |
| `date-edited` | From file modification time |
| `category` | ML classification (Sentence Transformers) |
| `tags` | Vocabulary matching + fuzzy search (rapidfuzz) |

### Category Classification

The normalizer uses **Sentence Transformers** (`all-mpnet-base-v2`) to classify documents into intent-based categories:

- **Theory** - Explanatory essays, philosophical frameworks
- **Praxis** - Methodologies, actionable guides
- **Polemics** - Critiques, arguments, debates
- **Creative** - Poetry, satire, fiction
- **Meta** - Documentation about the knowledge base

Classification works by computing semantic similarity between document content and category intent descriptions defined in `categories.yaml`.

### Tag Inference

The tag inferrer uses a **Seed + Expand** strategy:

1. **Vocabulary matching** - Matches content keywords against known tags
2. **Fuzzy search** - Uses rapidfuzz for approximate matching (threshold: 70%)
3. **Existing tag validation** - Preserves valid existing tags, flags unknown ones for review

The inferrer extracts keywords from content, filters stopwords, and matches against the tag vocabulary. Tags are hierarchical (e.g., `theory/class-analysis`) and the keyword index maps each segment to potential tags.

### Schema Enforcement

Removes fields not in the schema (`additionalProperties: false`):

- `slug` (auto-generated, not stored)
- `confidence` (deprecated)
- `related` (deprecated)
- `influences` (deprecated)

## Commands

### `mise run fm:normalize`

Normalize all frontmatter in the repository.

```bash
mise run fm:normalize
```

Options (via direct CLI):
- `--dry-run` - Show changes without writing
- `--no-backup` - Skip creating `.bak` files
- `--exclude PATTERN` - Additional exclusion patterns
- `--verbose` / `-v` - Detailed output
- `--quiet` / `-q` - Minimal output

### `mise run fm:dry-run`

Preview normalization without modifying files.

```bash
mise run fm:dry-run
```

### `mise run fm:validate`

Check all files against the frontmatter schema.

```bash
mise run fm:validate
```

### `mise run fm:report`

Generate a summary report of frontmatter status.

```bash
mise run fm:report
```

Output includes:
- Files missing required fields
- Files with deprecated fields
- Category distribution
- Schema validation errors

### `mise run fm:test`

Run the normalizer's test suite.

```bash
mise run fm:test
```

## Setup

The normalizer requires ML dependencies not included in the base Sphinx build:

```bash
mise run fm:setup
```

This installs:
- `spacy` - NLP library
- `en_core_web_lg` - SpaCy language model
- `sentence-transformers` - Semantic similarity
- `click` - CLI framework
- `rapidfuzz` - Fuzzy string matching

These dependencies are in `Pipfile` (dev) but not `Pipfile.ci` (production builds).

## Architecture

```
_tools/frontmatter_normalizer/
├── cli.py              # Click CLI interface
├── normalizer.py       # Core merge logic
├── parser.py           # YAML frontmatter parsing
├── writer.py           # YAML output formatting
├── config.py           # Schema fields, migrations, defaults
├── categories.yaml     # Intent-based category definitions
└── inferrer/
    ├── _common.py      # Shared utilities, protocol definitions
    ├── metadata.py     # zkid, dates, title, author
    ├── category_st.py  # Sentence Transformers classifier
    └── tags.py         # Vocabulary-based tag matching
```

## Category Configuration

Categories are defined in `_tools/frontmatter_normalizer/categories.yaml`:

```yaml
Theory:
  intent: "Teach me about X"
  description: "Explanatory essays, philosophical frameworks, concept definitions"
  keywords:
    - analysis
    - theory
    - concept

Praxis:
  intent: "Help me do X"
  description: "Methodologies, organizing guides, actionable frameworks"
  keywords:
    - guide
    - how-to
    - methodology
```

The classifier computes semantic similarity between document content and these descriptions to determine the best category match.

## Backup and Recovery

By default, normalization creates `.bak` files:

```bash
# Original preserved as .bak
theory/labor-aristocracy.md.bak

# Restore if needed
mv theory/labor-aristocracy.md.bak theory/labor-aristocracy.md
```

Use `--no-backup` to skip backup creation (not recommended for first runs).

## Integration with CI

The normalizer is **not** run in CI builds. It's a local development tool for maintaining frontmatter consistency.

CI builds use `Pipfile.ci` which excludes ML dependencies to keep build times fast.
