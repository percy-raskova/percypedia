---
category: Infrastructure
---

# MyST Markdown Syntax

This knowledge base uses [MyST Markdown](https://myst-parser.readthedocs.io/) - a rich superset of CommonMark that adds Sphinx roles and directives.

## Why MyST?

| Feature | CommonMark | MyST |
|---------|------------|------|
| Basic formatting | ✓ | ✓ |
| Cross-references | ✗ | ✓ |
| Glossary terms | ✗ | ✓ |
| Admonitions | ✗ | ✓ |
| Figures with captions | ✗ | ✓ |
| Math equations | ✗ | ✓ |
| Renders in GitHub/Obsidian | ✓ | Partially |

## Basic Formatting

### Text Styles

```markdown
**bold** and *italic* and `inline code`

~~strikethrough~~

> Blockquote
```

### Headings

```markdown
# H1 - Document Title
## H2 - Major Section
### H3 - Subsection
#### H4 - Minor Section
```

### Lists

```markdown
- Unordered item
- Another item
  - Nested item

1. Ordered item
2. Another item

- [ ] Task (unchecked)
- [x] Task (checked)
```

### Links

```markdown
[External link](https://example.com)

[Internal doc link](other-file.md)

<https://auto-linked-url.com>
```

## MyST Roles (Inline)

Roles are inline markup using the syntax `` {role}`content` ``.

### Cross-References

```markdown
{ref}`section-label`           # Link to labeled section
{doc}`/path/to/document`       # Link to document
{term}`glossary term`          # Link to glossary with tooltip
{numref}`figure-id`            # Numbered reference to figure
```

### Glossary Terms

Reference terms defined in `glossary.md`:

```markdown
The {term}`dialectical materialism` framework suggests...

{term}`SICA` methodology involves...
```

Hover shows the definition (via sphinx-hoverxref).

### Document Links

```markdown
See {doc}`/concepts/desire_paths` for more.

Related: {doc}`../methods/sica_methodology`
```

## MyST Directives (Blocks)

Directives are block-level markup using fenced code blocks.

### Admonitions

```markdown
:::{note}
This is a note admonition.
:::

:::{warning}
This is a warning.
:::

:::{tip}
Helpful tip here.
:::

:::{important}
Critical information.
:::

:::{danger}
Dangerous operation warning.
:::
```

### Figures

```markdown
:::{figure} {{assets}}/images/diagram.png
:alt: Alt text for accessibility
:width: 80%
:align: center
:name: fig-diagram

Caption text appears below the image.
:::
```

Reference with `{numref}` or `{ref}`:

```markdown
See {numref}`fig-diagram` for the architecture.
```

### Code Blocks

````markdown
```python
def hello():
    print("Hello, world!")
```

```{code-block} python
:linenos:
:emphasize-lines: 2

def hello():
    print("Hello, world!")  # This line highlighted
```
````

### Tables

```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
```

Or with directive for more control:

```markdown
:::{list-table} Table Title
:header-rows: 1
:widths: 30 70

* - Term
  - Definition
* - MyST
  - Markedly Structured Text
:::
```

### Definition Lists

```markdown
Term 1
: Definition of term 1

Term 2
: Definition of term 2
: Can have multiple definitions
```

## Section Labels

Create anchors for cross-referencing:

```markdown
(my-section-label)=
## My Section

Reference it elsewhere:
See {ref}`my-section-label` for details.
```

## Math

Inline math with single dollars:

```markdown
The equation $E = mc^2$ is famous.
```

Block math with double dollars:

```markdown
$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
```

Or with directive for numbering:

```markdown
```{math}
:label: eq-euler

e^{i\pi} + 1 = 0
```

See equation {eq}`eq-euler`.
```

## Substitutions

Defined in `conf.py`, used with double braces:

```markdown
![Image]({{assets}}/images/photo.png)
```

Current substitutions:

| Variable | Value |
|----------|-------|
| `{{assets}}` | R2 bucket URL for images/PDFs |

## Frontmatter

YAML frontmatter for metadata (optional):

```markdown
---
tags: concept, philosophy
status: draft
---

# Document Title
```

:::{warning}
Avoid `Date:` in frontmatter - it conflicts with some extensions.
:::

## File Organization

### Naming Conventions

- Use `snake_case` for filenames: `dialectical_materialism.md`
- Keep names concise but descriptive
- Use subdirectories for categories: `concepts/`, `methods/`, `systems/`

### Document Structure

```markdown
# Title

Brief introduction paragraph.

## First Major Section

Content here.

### Subsection

More detailed content.

## See Also

- {doc}`related-doc-1`
- {doc}`related-doc-2`
```

## Common Patterns

### Concept Note Template

```markdown
# Concept Name

Brief definition in 1-2 sentences.

## Core Idea

Expanded explanation.

## Examples

Concrete examples.

## Related Concepts

- {doc}`related-concept-1`
- {term}`glossary-term`

## References

- External source 1
- External source 2
```

### Adding to Glossary

In `glossary.md`:

```markdown
```{glossary}
:sorted:

new term
    Definition of the new term.
```
```

Then reference with `{term}`new term``.

## Enabled Extensions

From `conf.py`:

| Extension | Syntax | Purpose |
|-----------|--------|---------|
| `colon_fence` | `:::` | Directives that render in plain editors |
| `deflist` | `Term\n: Def` | Definition lists |
| `dollarmath` | `$...$` | LaTeX math |
| `fieldlist` | `:field:` | Metadata fields |
| `substitution` | `{{var}}` | Variable substitution |
| `tasklist` | `- [ ]` | Checkbox task lists |
| `attrs_inline` | `{#id .class}` | Inline attributes |

## Tips

1. **Preview locally**: `mise run preview` for live reload
2. **Check build**: `mise run build` to catch errors
3. **Use glossary**: Define terms once, reference everywhere
4. **Label sections**: Add `(label)=` for easy cross-refs
5. **Prefer `:::`**: Colon fences render better in plain editors
