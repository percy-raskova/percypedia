---
category: Meta
tags:
  - meta/documentation
  - meta/ai-assistance
publish: true
---

# MyST and AI Cognition

How semantic markup transforms documentation from text into structured knowledge that AI models can meaningfully process.

## The Core Insight

When you write documentation in MyST rather than plain Markdown, you're not just adding formatting—you're encoding **machine-readable intent**. This distinction matters profoundly for how AI assistants understand and work with your documentation.

Plain Markdown:

```markdown
**Warning:** Don't run this in production without backups.
```

MyST:

```markdown
:::{warning}
Don't run this in production without backups.
:::
```

These render identically to human readers. But to an AI model, they carry fundamentally different information.

## Attention and Context Binding

Large language models process text through attention mechanisms that weight relationships between tokens. When an AI encounters a MyST directive, something interesting happens.

Consider this warning block:

```markdown
:::{warning}
Don't run this in production!
:::
```

The `:::` fence pattern triggers recognition of a structured block. The `{warning}` token then activates associations learned from countless documentation examples. But crucially, when the AI processes "Don't run this in production!", attention heads connect back to `warning`—the content inherits semantic weight from its container.

This is analogous to how humans don't forget they're reading a warning box while scanning its contents. The visual formatting (yellow background, icon) serves the same purpose as attention patterns—**maintaining context**.

With plain Markdown `**Warning:**`, the AI must infer warning-semantics from surface patterns. With `{warning}`, the semantics are explicit.

## Domain Prefixes as Cognitive Priming

MyST's domain prefixes demonstrate something fascinating about how AI processes context.

```markdown
:::{py:function} iter_markdown_files(srcdir, exclude_patterns=None)
```

vs.

```markdown
:::{js:function} iterMarkdownFiles(srcdir, excludePatterns)
```

The `py:` token activates a cluster of Python-specific associations:

- Snake_case naming conventions
- `None` as sentinel value
- `self` as first method parameter
- `Args/Returns/Raises` docstring patterns

The `js:` token activates different associations:

- camelCase conventions
- `undefined`/`null` distinctions
- Callback patterns, Promises
- JSDoc `@param` annotations

This works like **cognitive priming** in human psychology. If you hear "bank" after discussing rivers, you think riverbanks. After discussing money, you think financial institutions. Domain prefixes prime AI interpretation toward the appropriate language ecosystem.

## Block vs Inline: Scope of Influence

MyST distinguishes between directives (block-level) and roles (inline). This distinction carries semantic weight.

**Directives** create a modal context:

```markdown
:::{note}
Everything here belongs to the note.
Multiple paragraphs.
Nested content.
:::
```

When an AI encounters a directive, it understands that the directive "owns" everything until the closing fence. Content is interpreted **in context** of that directive type.

**Roles** are point annotations:

```markdown
See {func}`iter_markdown_files` for details.
```

The role applies only to the immediately following backticked content. It doesn't change interpretation of surrounding text—it's a semantic tag on a specific reference.

This maps to the HTML block/inline distinction:

| MyST Element | HTML Analog | Scope |
|--------------|-------------|-------|
| Directives | `<div>`, `<aside>`, `<figure>` | Block-level, owns children |
| Roles | `<span>`, `<code>`, `<a>` | Inline, point annotation |

For a complete syntax reference, see {doc}`myst-syntax`.

## Documentation as Knowledge Graph

References in MyST reveal that documentation is fundamentally a **graph**, not just text.

```markdown
{doc}`getting-started`     # Edge to document node
{ref}`installation-steps`  # Edge to labeled anchor
{func}`mymodule.my_func`   # Edge to code entity
{term}`dialectics`         # Edge to glossary definition
```

These aren't content—they're **edges in a knowledge graph**. When an AI sees `{doc}`, it understands this as navigation topology: "there exists another document in this tree, and this is a link to it."

The `toctree` directive is pure graph metadata:

```markdown
:::{toctree}
:maxdepth: 2

getting-started
api-reference
:::
```

This isn't prose—it's **structure definition**. It declares how documents relate hierarchically. An AI recognizes this as metadata about the knowledge graph, distinct from the actual content.

This graph-awareness enables intelligent navigation. When you ask an AI "what documents relate to authentication?", it can traverse these semantic links rather than just grep for the word "authentication."

## Tags and Multi-Dimensional Navigation

The {doc}`taxonomy` system demonstrates how semantic markup enables multi-dimensional organization.

```yaml
---
category: Theory
tags:
  - politics/marxism
  - theory/labor-aristocracy
  - organizing/strategy
---
```

From an AI perspective, tags create **virtual directories**. A document inhabits multiple conceptual spaces simultaneously. The hierarchical tag structure (`politics/marxism`) provides even more granularity—an AI can reason about `politics/*` as a broader category containing `politics/marxism` as a specific instance.

This multi-dimensional organization is impossible with plain filesystem structure, where a document can only exist in one directory. Tags give AI assistants a richer graph to traverse when finding related content.

## Frontmatter as Structured Metadata

The {doc}`frontmatter-schema` provides machine-readable document metadata:

```yaml
---
zkid: 202411281430
category: Theory
tags: [theory/marxism]
publish: false
status: draft
---
```

Each field carries specific meaning:

| Field | AI Interpretation |
|-------|-------------------|
| `zkid` | Unique identifier for cross-referencing |
| `category` | Primary classification for navigation |
| `tags` | Multi-dimensional graph edges |
| `publish` | Visibility control (false = draft) |
| `status` | Editorial workflow stage |

This structured metadata enables AI queries like "find all draft documents in the Theory category" without natural language ambiguity. The schema defines valid values, so an AI can validate and suggest corrections.

## The Autodoc Bridge

One of MyST/Sphinx's most powerful features is the bridge between documentation and code:

```markdown
:::{automodule} mypackage.utils
:members:
:::
```

This directive is philosophically complex. It's a **reference to external content** that doesn't exist in the documentation source. It instructs: "At build time, import this Python module, introspect it, extract docstrings, generate documentation."

From an AI perspective, this creates bidirectionality:

- Documentation references code (via autodoc directives)
- Code contains documentation (via docstrings)

When someone asks "where is this function documented?", the answer might be "in the docstring at `mypackage/utils.py:42`", not in any `.md` file. Understanding this bridge is essential for comprehensive codebase assistance.

## Custom Directives and Extension Points

Standard directives like `{warning}` and `{note}` are well-understood from training data. But MyST's extensibility creates interesting challenges.

A custom directive like `{category-nav}` (used in this project) requires context-specific understanding:

```markdown
:::{category-nav}
:::
```

An AI without project context would recognize this as "a directive block" structurally, but wouldn't know its semantics. After reading the extension source code at `_extensions/category_nav/`, the AI understands it generates navigation from frontmatter categories.

This illustrates a confidence gradient:

| Directive Type | AI Confidence |
|----------------|---------------|
| Standard Sphinx (`warning`, `note`, `toctree`) | High |
| Domain-specific (`py:function`, `py:class`) | High |
| Common extensions (autodoc, intersphinx) | Medium |
| Project-specific custom directives | Requires context |

## Why This Matters for Documentation Authors

Understanding how AI processes MyST has practical implications:

### Use semantic markup consistently

When you use `{warning}` instead of `**Warning:**`, you give AI assistants explicit semantic information. This enables:

- Accurate importance weighting in summaries
- Better categorization of content types
- More reliable extraction of cautionary information

### Leverage cross-references

Using `{doc}`, `{ref}`, and `{func}` roles instead of plain links creates machine-readable navigation:

```markdown
# Good - semantic cross-reference
See {doc}`myst-syntax` for the complete reference.

# Less good - plain link
See [MyST Syntax](myst-syntax.md) for the complete reference.
```

Both render identically, but the first explicitly declares "this is a document reference," while the second is just a URL that happens to point to a local file.

### Structure frontmatter carefully

Well-structured frontmatter enables AI queries that plain text search cannot:

- "Find all Theory documents about organizing"
- "List drafts that need review"
- "Show recently edited Meta documentation"

The {doc}`frontmatter-schema` defines what fields exist and what values they accept. Adhering to the schema ensures AI tools can work reliably with your metadata.

## The Deeper Principle

At the philosophical root, MyST embodies a powerful insight:

> **Separating meaning from presentation enables transformation.**

When you write `{warning}` instead of styling a yellow box, you encode intent. That intent survives transformation across output formats (HTML, PDF, plain text) and enables machine reasoning about document structure.

This is the same principle behind:

- HTML5 semantic elements (`<article>`, `<nav>`) vs div-soup
- LaTeX document classes vs manual formatting
- CSS separation from HTML

Semantic markup is essentially **machine-readable authorial intent**. It bridges human writing and machine processing—which is why AI can understand MyST documents more deeply than plain text files, even though both are "just text" at the character level.
