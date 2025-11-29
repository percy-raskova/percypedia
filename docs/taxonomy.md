---
category: Meta
---

# Three-Layer Taxonomy

This knowledge base uses a three-layer taxonomy system that separates concerns between human navigation, website presentation, and machine traversal.

## The Layers

| Layer | Purpose | Source | Consumer |
|-------|---------|--------|----------|
| **Directories** | Human navigation | Filesystem | You, locally |
| **Categories** | Website navigation | `category:` frontmatter | Readers, sidebar |
| **Tags** | AI/Zettelkasten navigation | `tags:` frontmatter | Search, AI agents |

## Directories (Human Navigation)

The filesystem structure reflects how *you* think about organizing files locally:

```
rstnotes/
├── sample/
│   ├── concepts/      # Theoretical foundations
│   ├── methods/       # Practical methodologies
│   └── systems/       # Technical architectures
├── docs/              # Infrastructure documentation
└── private/           # Unpublished drafts (excluded from build)
```

This is your mental model. Organize files where they make sense to *you*. The website doesn't care where files physically live.

## Categories (Website Navigation)

Categories determine how content appears in the website sidebar. Add `category:` to frontmatter:

```yaml
---
category: Theory
---

# Dialectical Materialism
```

The `{category-nav}` directive in `index.md` automatically groups documents by category.

### Intent-Based Categories

Categories are organized by **reader intent** - what the reader is looking for:

| Category | Reader Intent | Content Type |
|----------|--------------|--------------|
| **Theory** | "Teach me about X" | Explanatory essays, philosophical frameworks, concept definitions |
| **Praxis** | "Help me do X" | Methodologies, organizing guides, actionable frameworks |
| **Polemics** | "Show me who's wrong about X" | Critiques, arguments against positions, debates |
| **Creative** | "Show me art about X" | Poetry, satire, fiction, personal essays |
| **Meta** | "How does this site work?" | Documentation about the knowledge base itself |

This intent-based schema helps readers find content based on what they need, not just what genre it belongs to.

### Key Properties

- One category per file (for clean navigation)
- Categories are sorted alphabetically
- Documents within categories are sorted by title
- The default category (Miscellaneous) always appears last

### Configuration

In `conf.py`:

```python
category_nav_exclude = ['index', 'glossary', ...]  # Files to skip
category_nav_default = 'Miscellaneous'               # Default category (appears last)
```

## Tags (AI/Zettelkasten Navigation)

Tags create a multi-dimensional graph for machine traversal. A file can have unlimited tags:

```yaml
---
category: Theory
tags:
  - politics/marxism
  - theory/labor-aristocracy
  - organizing/strategy
---
```

Tags function as "virtual directories" - one file inhabits multiple conceptual spaces simultaneously.

### Hierarchical Tags

Use `/` to create tag hierarchies:

- `politics/marxism`
- `politics/anarchism`
- `theory/class-analysis`
- `theory/labor-aristocracy`

The `sphinx-tags` extension generates tag pages at `/tags/<tag>/`.

### Use Cases

1. **AI context retrieval** - "Find all documents tagged `organizing/*`"
2. **Cross-cutting concerns** - A document about labor aristocracy relates to both theory and organizing
3. **Zettelkasten linking** - Discover connections across category boundaries

## How They Work Together

Consider a document about lumpen organizing:

```yaml
---
category: Theory                      # Website: appears under "Theory"
tags:
  - organizing/strategy               # AI: findable via organizing
  - theory/class-analysis             # AI: findable via theory
  - politics/marxism                  # AI: findable via politics
---

# Lumpen Organizing
```

- **Directory**: Lives in `sample/concepts/` (your local organization)
- **Category**: Shows under "Theory" in sidebar (reader intent: "teach me about X")
- **Tags**: Discoverable via multiple paths (machine traversal)

## Implementation

Three custom Sphinx extensions plus a shared module power this workflow:

### category_nav (`_extensions/category_nav/`)

- `extract_frontmatter()` - Parse YAML from markdown (from `_common.frontmatter`)
- `collect_categories()` - Group files by category
- `CategoryNavDirective` - Generate toctrees
- Respects `publish: false` to exclude drafts

### publish_filter (`_extensions/publish_filter/`)

- Excludes documents with `publish: false` from the entire build
- Strips Obsidian comments (`%%...%%`) from output

### _common (`_extensions/_common/`)

Shared utilities used by all extensions:

**frontmatter.py** - Single source of truth for YAML frontmatter extraction
- `extract_frontmatter(content)` - Parse YAML from markdown string
- Returns `(frontmatter_dict, body_content)` tuple

**traversal.py** - Unified directory walking
- `iter_markdown_files(srcdir, exclude_patterns, ...)` - Iterate markdown files
- Parameters:
  - `skip_underscore_files` - Skip `_index.md` etc. (default: True)
  - `skip_underscore_dirs` - Skip `_build/` etc. (default: True)
  - `skip_dot_dirs` - Skip `.git/` etc. (default: True)

### External Extensions

- `sphinx-tags` - Generates tag pages for AI/search navigation

## Templates

Use `<leader>mN` in Neovim to create notes from templates in `_templates/`:

### note.md (General purpose)

```yaml
---
zkid: 202411281430            # Zettelkasten ID (YYYYMMDDHHMM)
title: "Document Title"
author: Percy
date-created: 2024-11-28T14:30
date-edited: 2024-11-28T14:30
category:                     # Website navigation
tags: []                      # AI/Zettelkasten navigation
publish: false                # Draft by default
status: draft
---
```

### daily.md (Daily notes)

Pre-configured with date-based tags for journal entries.

## Publishing Workflow

Documents have a `publish` key controlling visibility:

| Value | Behavior |
|-------|----------|
| `publish: false` | Draft - excluded from build |
| `publish: true` | Published - included in build |
| (no key) | Published - backwards compatible |

To publish a draft:

1. Write and refine with `publish: false`
2. When ready, change to `publish: true`
3. Run `mise run build`

## Obsidian Comments

Use `%%...%%` for comments that don't appear in the published site:

```markdown
# Document Title

%%TODO: Add more examples here%%

This content is visible.

%%
This entire block
is hidden from readers
%%

More visible content.
```

Comments are stripped during the Sphinx build - they never reach the HTML output.

## Adding New Content

1. Create file with `<leader>mN` (uses template)
2. Fill in `category:` for website navigation
3. Add `tags:` for cross-referencing
4. Write content (use `%%comments%%` for notes-to-self)
5. Set `publish: true` when ready
6. Build with `mise run build`

### Quick Example

```yaml
---
zkid: 202411281430
title: "New Methodology"
author: Percy
date-created: 2024-11-28T14:30
date-edited: 2024-11-28T14:30
category: Praxis
tags:
  - organizing/tactics
  - theory/praxis
publish: true
status: complete
---

# New Methodology

%%Remember to add references%%

Content here.
```
