---
category: Theory
Confidence: high
Date: '2024-10-18'
Related: '{doc}`/systems/druids_architecture`, {doc}`dialectical_materialism`'
Status: foundational-concept
Tags: knowledge-management, emergence, systems-design, urban-planning
Updated: '2024-11-26'
---

# Desire Paths

## Definition

(desire-path-core)=

{term}`Desire paths` are trails worn into landscapes by repeated foot traffic,
appearing where people actually walk rather than where planners intended. They
represent emergent structure—organic pathways created by collective behavior
rather than top-down design.

:::{figure} https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Desire_path.jpg/320px-Desire_path.jpg
:align: center
:alt: Grass worn away showing dirt path

Classic desire path: worn trail through grass reveals actual usage patterns
:::

## Origin in Urban Planning

### Historical Context

Term emerged from landscape architecture and urban planning. Famous examples:

**Ohio State University approach** (apocryphal but illustrative):

1. Plant grass across entire campus
2. Wait one semester
3. Pave where paths appear
4. Result: Sidewalks match actual usage

**Contrast with typical approach**:

1. Design "logical" pathway system
2. Build sidewalks
3. Install "KEEP OFF GRASS" signs where people shortcut
4. Result: Conflict between design and use

This mirrors broader tension in {term}`dialectical materialism` between idealist
planning (imposing theory) and materialist analysis (observing practice). See
{doc}`dialectical_materialism` for theoretical grounding.

### Why Desire Paths Form

People optimize for:

- **Shortest distance**: Geometry of actual travel, not aesthetic layout
- **Least effort**: Avoiding stairs, steep grades when alternatives exist
- **Social clustering**: Following others creates positive feedback loops
- **Local knowledge**: Regular users know shortcuts planners don't

:::{note}
This isn't "chaos" or "lack of discipline"—it's *rational behavior* responding
to actual conditions. Planners who fight desire paths are imposing ideology
over material reality.
:::

## Application to Knowledge Management

### The Central Problem

Knowledge management faces identical tension:

```{eval-rst}
.. table:: Planning vs. Emergence
   :widths: 30 35 35

   ========================  ============================  =========================
   Approach                  Strengths                     Weaknesses
   ========================  ============================  =========================
   Top-down hierarchy        Clear structure, findable     Rigid, artificial
   Bottom-up tagging         Flexible, organic             Chaotic, lost knowledge
   Weighted edges (desire)   Structure + emergence         Requires usage data
   ========================  ============================  =========================
```

### Traditional Approaches Fail

**Hierarchical filing**:

```text
Projects/
├── Organizing/
├── Theory/
└── Technical/
```

Problem: Real knowledge doesn't fit neat categories. "Is {term}`SICA` organizing
or technical? Both?" Forcing choice loses connections.

**Pure tagging**:

```text
Note #organizing #theory #data #python #activism
```

Problem: No structure emerges. Tags proliferate, meaning degrades, findability
decreases over time.

### Weighted Edges: Implementing Desire Paths

Solution inspired by {ref}`desire-path-core` concept:

```python
class WeightedKnowledgeEdge:
    """Edge that strengthens with traversal"""

    def __init__(self, from_node, to_node):
        self.from_node = from_node
        self.to_node = to_node
        self.weight = 1.0  # Initial weight
        self.traversals = 0
        self.created_at = datetime.now()
        self.last_traversed = None

    def traverse(self):
        """Strengthen edge when traversed"""
        self.traversals += 1
        self.weight *= 1.1  # Increase by 10%
        self.last_traversed = datetime.now()

    def decay(self, days_inactive):
        """Weaken edge if unused"""
        if days_inactive > 30:
            self.weight *= 0.95  # Decrease by 5%

        if self.weight < 0.1:
            return None  # Path has faded

        return self
```

**Key properties**:

1. **All connections start equal**: No pre-defined "important" links
2. **Usage strengthens paths**: Frequently traversed edges become primary routes
3. **Disuse weakens paths**: Unused connections fade (like grass regrowing)
4. **Emergence over time**: Structure appears from collective behavior

This is *materialism* applied to information architecture—observe actual usage,
don't impose idealist structure.

### Neo4j Implementation

Graph databases naturally support weighted edges:

```cypher
// Create notes with weighted connections
CREATE (a:Note {id: 'dialectical_materialism', title: 'Dialectical Materialism'})
CREATE (b:Note {id: 'sica', title: 'SICA Methodology'})
CREATE (c:Note {id: 'lumpen', title: 'Lumpen Organizing'})

// Create weighted relationships
CREATE (a)-[:RELATES_TO {weight: 1.0, traversals: 0}]->(b)
CREATE (a)-[:RELATES_TO {weight: 1.0, traversals: 0}]->(c)
CREATE (b)-[:RELATES_TO {weight: 1.0, traversals: 0}]->(c)

// When user navigates a→b, strengthen edge:
MATCH (a:Note)-[r:RELATES_TO]->(b:Note)
WHERE a.id = 'dialectical_materialism' AND b.id = 'sica'
SET r.weight = r.weight * 1.1,
    r.traversals = r.traversals + 1,
    r.last_traversed = timestamp()

// Find strongest paths (desire paths in knowledge graph):
MATCH path = (a:Note)-[r:RELATES_TO*1..3]->(b:Note)
WHERE a.id = 'dialectical_materialism'
RETURN path, reduce(weight = 1, rel in relationships(path) | weight * rel.weight) AS path_strength
ORDER BY path_strength DESC
```

Over time, frequently-used connections become "main roads" in your knowledge base.
Rarely-used connections fade. Structure emerges from usage.

## Connection to DRUIDS Architecture

{doc}`/systems/druids_architecture` implements desire paths at system level:

**Centralized systems** (failed socialist states, corporate knowledge bases):

- Top-down structure imposed
- Single routing mechanism
- Fails when central plan doesn't match usage
- Users work around system → shadow knowledge bases

**DRUIDS approach** (distributed with emergence):

- Multiple nodes with equal status
- Connections strengthen with usage
- No single "correct" structure
- System *learns* from user behavior

:::{note}
This is {term}`democratic centralism` properly understood: coordination emerges
from collective practice, not imposed from above. See discussion in
{doc}`/systems/druids_architecture`.
:::

## Relationship to Material Analysis

Desire paths concept is fundamentally *materialist*:

1. **Observe practice**: Watch what people actually do
2. **Identify patterns**: Find regularities in behavior
3. **Support emergence**: Build infrastructure that reinforces useful patterns
4. **Iterate**: System evolves as usage changes

This methodology applies to:

- **Organizing work**: See {doc}`lumpen_organizing` and {doc}`/methods/sica_methodology`
- **System design**: See {doc}`/systems/druids_architecture`
- **Knowledge management**: This note's primary focus
- **Security analysis**: Understand actual information flows vs. planned

:::{warning}
**Idealist trap**: Assuming your planned structure is "correct" and users
who deviate are wrong. This is imposing theory over practice—the opposite of
{term}`dialectical materialism`.
:::

## Practical Implementation

### For PercyBrain Zettelkasten

Current implementation considerations:

```python
# PercyBrain weighted edge system

class ZettelkastenNote:
    def __init__(self, id, content):
        self.id = id
        self.content = content
        self.outgoing_edges = {}  # {target_id: EdgeMetadata}
        self.incoming_edges = {}

    def link_to(self, target_note, context=None):
        """Create or strengthen link"""
        if target_note.id in self.outgoing_edges:
            # Strengthen existing path
            self.outgoing_edges[target_note.id].traverse()
        else:
            # Create new path
            edge = WeightedEdge(self.id, target_note.id, context)
            self.outgoing_edges[target_note.id] = edge
            target_note.incoming_edges[self.id] = edge

    def get_strongest_connections(self, n=5):
        """Return top N most-traversed paths (desire paths)"""
        sorted_edges = sorted(
            self.outgoing_edges.values(),
            key=lambda e: e.weight,
            reverse=True
        )
        return sorted_edges[:n]

    def suggest_connections(self, threshold=0.5):
        """Suggest links based on similar strong paths from related notes"""
        suggestions = []

        for edge in self.outgoing_edges.values():
            if edge.weight > threshold:
                # Check what the target links to
                target = get_note(edge.to_node)
                for target_edge in target.outgoing_edges.values():
                    if target_edge.to_node not in self.outgoing_edges:
                        # Potential desire path: A→B→C but not A→C
                        suggestions.append({
                            'target': target_edge.to_node,
                            'reason': f'Often accessed after {edge.to_node}',
                            'strength': edge.weight * target_edge.weight
                        })

        return sorted(suggestions, key=lambda s: s['strength'], reverse=True)
```

### Visualization

Desire paths should be *visible* to users:

```text
[Note: Dialectical Materialism]

Strongest connections (desire paths):
━━━━━━━━━━━━ SICA Methodology (visited 47 times)
━━━━━━━━━ Lumpen Organizing (visited 38 times)
━━━━ DRUIDS Architecture (visited 12 times)
━━ Surveillance Analysis (visited 5 times)

Fading connections (unused >60 days):
─ Early draft notes (last: 2024-08-12)
```

This makes structure *legible*—users see organic architecture as it forms.

## Common Pitfalls

❌ **Mistake 1**: Preserving all connections equally

✓ **Correct**: Let untraversed paths fade. Not all connections are equally valuable.

❌ **Mistake 2**: Gaming the system (artificially traversing to boost weight)

✓ **Correct**: Weight increase should be logarithmic, not linear. Early traversals
matter more than later ones.

❌ **Mistake 3**: No decay mechanism

✓ **Correct**: Paths unused for extended periods should weaken. Context changes,
old connections become less relevant.

❌ **Mistake 4**: Forgetting bidirectionality

✓ **Correct**: A→B and B→A are *different* paths. Asymmetry is meaningful data.

## Connections

**Theoretical Foundation**:

- {doc}`dialectical_materialism` - Materialism over idealism in design
- {term}`praxis` - Observe practice, build supporting theory

**System Implementation**:

- {doc}`/systems/druids_architecture` - Distributed knowledge with emergent structure
- {doc}`/methods/sica_methodology` - Data-driven emergence in organizing

**Conceptual Relations**:

- {term}`democratic centralism` - Coordination without imposed structure
- {term}`weighted edges` - Technical implementation

## Further Reading

### Urban Planning

- Jacobs, Jane. *The Death and Life of Great American Cities* (1961)
- Alexander, Christopher. *A Pattern Language* (1977)

### Knowledge Management

- Bush, Vannevar. "As We May Think" (1945) - Associative indexing
- Ahrens, Sönke. *How to Take Smart Notes* (2017) - Zettelkasten method

### Graph Theory

- Barabási, Albert-László. *Linked* (2002) - Network emergence
- Watts, Duncan. *Six Degrees* (2003) - Small-world networks

:::{note}
The desire paths concept bridges urban planning, knowledge management, and
revolutionary organizing—all share the same materialist principle: structure
emerges from practice, not imposed theory.
:::
