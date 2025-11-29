---
category: Meta
---

# Missing References Extension

The `missing_refs` extension tracks forward-links to documents that don't exist yet, enabling a "write the link first" workflow where you reference planned content before writing it.

## What It Does

When you create a `{doc}` reference to a non-existent document:

```markdown
See {doc}`theory/future-topic` for more details.
```

The extension:

1. Captures the missing reference during build
2. Records which document contains the broken link
3. Outputs a JSON file for programmatic use
4. Optionally generates a "Planned Articles" page

## Output

### JSON Output (Always Generated)

After every build, `_build/html/missing_refs.json` contains:

```json
{
  "generated_at": "2024-11-28T14:30:00+00:00",
  "count": 3,
  "missing_documents": [
    {
      "target": "theory/future-topic",
      "category": "theory",
      "referenced_by": ["index", "theory/related-topic"]
    }
  ],
  "by_category": {
    "theory": ["theory/future-topic"],
    "concepts": ["concepts/another-planned"]
  }
}
```

### Markdown Page (Optional)

Enable automatic "Coming Soon" page generation:

```python
# conf.py
missing_refs_generate_page = True
missing_refs_page_path = 'coming-soon.md'
missing_refs_page_title = 'Planned Articles'
```

This creates a page listing all planned articles grouped by category.

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `missing_refs_generate_page` | `False` | Generate markdown page |
| `missing_refs_page_path` | `'coming-soon.md'` | Output path for generated page |
| `missing_refs_page_title` | `'Planned Articles'` | Title for generated page |

## Workflow

### 1. Write Links First

Reference documents you plan to write:

```markdown
# Labor Aristocracy

The concept relates to {doc}`theory/surplus-value-transfer` and
{doc}`theory/unequal-exchange`.
```

### 2. Build and Track

```bash
mise run build
```

Check the build output:

```
Found 2 planned article(s) - see _build/html/missing_refs.json
```

### 3. Review Planned Content

```bash
cat _build/html/missing_refs.json | jq '.by_category'
```

### 4. Write the Documents

When you create `theory/surplus-value-transfer.md`, it automatically disappears from the missing refs list on next build.

## Use Cases

- **Content planning**: See what articles are referenced but unwritten
- **Dependency tracking**: Know which documents need a planned article
- **Editorial workflow**: Generate a public "coming soon" page
- **CI integration**: Track content gaps programmatically

## Implementation

Located at `_extensions/missing_refs/__init__.py`.

Key components:

- `MissingRefsCollector` - Accumulates missing references during build
- `on_missing_reference` - Sphinx event handler for broken doc refs
- `on_build_finished` - Writes JSON (and optionally markdown) output
