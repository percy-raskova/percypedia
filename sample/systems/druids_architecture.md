---
category: Praxis
Confidence: high
Date: '2024-09-28'
Influences: Socialist state failures, peer-to-peer networks, graph databases
Related: '{doc}`/concepts/desire_paths`, {doc}`/concepts/dialectical_materialism`'
Status: active-development
Tags: systems-design, distributed-systems, organizing-infrastructure, security
Updated: '2024-11-26'
---

# DRUIDS Architecture


## Name

**DRUIDS**: Democratic Revolutionary Unified Information & Documentation System

Pronunciation: /ˈdruːɪdz/ (like the Celtic priests)

:::{note}
Name is deliberately non-threatening. "Revolutionary" in title but sounds like
a documentation platform. Good OPSEC—doesn't trigger keywords.
:::

## Thesis

Knowledge management systems for revolutionary organizing must be *distributed*
rather than *centralized*. Lessons from socialist state failures: centralized
control creates single points of failure, bureaucratic ossification, and
vulnerability to capture. DRUIDS implements {term}`democratic centralism` as
*strategic coordination* rather than *structural hierarchy*.

:::{important}
This isn't about technology preferences—it's application of {term}`dialectical materialism`
to system design. See {doc}`/concepts/dialectical_materialism` for theoretical
foundation.
:::

## Why Existing Systems Fail

### Centralized Platforms (Corporate)

Examples: Google Workspace, Microsoft Teams, Notion, Confluence

**Structural problems**:

```text
Single Company Controls:
├── Access (can be revoked)
├── Data (ownership unclear, surveillance guaranteed)
├── Features (changes without consent)
└── Pricing (extortion after lock-in)
```

**Organizing-specific problems**:

- Subpoena vulnerability: Single point of legal pressure
- Surveillance: Automated scanning, pattern analysis, metadata collection
- Terms of Service: "Extremist content" bans organizing
- Reliability: Depends on profit motive, not movement needs

:::{danger}
**Recent example**: Discord banned numerous leftist servers for "violent
content" in 2023. Years of organizing knowledge lost overnight. This is
*inevitable* with centralized platforms—not if, but when.
:::

### Centralized Self-Hosted

Examples: Self-hosted GitLab, Nextcloud, MediaWiki

**Better than corporate, but**:

```text
Single Server Vulnerabilities:
├── Physical seizure
├── DDoS attacks
├── Single admin as point of failure
├── Backup/replication requires coordination
└── No graceful degradation
```

If server goes down (raid, admin arrested, hardware failure), *everything* stops.

:::{warning}
Self-hosting is necessary but not sufficient. Must be distributed self-hosting.
:::

### Hierarchical "Secure" Platforms

Examples: Signal groups, Telegram channels

**Security theater**:

- End-to-end encryption protects messages
- But: Structure is hierarchical (group admin controls all)
- Knowledge management terrible (no search, no organization, chat = ephemeral)
- Metadata still vulnerable (who talks to whom, when, how often)

Good for tactical communication, inadequate for knowledge management.

## Lessons from Socialist States

### The Centralization Trap

**Historical pattern**:

1. Revolutionary period: Distributed networks, grassroots organizing
2. State power achieved: Centralization "for efficiency"
3. Bureaucracy emerges: Central planning, top-down control
4. Ossification: Cannot adapt, cannot reform, eventual collapse

**Examples**:

- USSR: Gosplan, central committees, Moscow as single decision point
- GDR: Stasi (ironically, excellent information but centralized analysis)
- Cuba: Post-Soviet economic crisis revealed fragility of centralized dependency

**Analysis**: These weren't moral failures—they were *structural* problems.
Centralization creates:

```text
Centralized Structure Produces:

Single Point of Decision → Bottleneck → Slow adaptation
Single Point of Failure → Fragility → Catastrophic collapse
Single Point of Corruption → Elite capture → Bureaucracy
Information flows upward → Analysis centralized → Disconnection from base
```

This is {term}`dialectical materialism` applied to organizational structure:
Material architecture determines political possibilities.

### Democratic Centralism: Strategy vs. Structure

{term}`Democratic centralism` is often misunderstood:

```{eval-rst}
.. table:: Two Interpretations
   :widths: 30 35 35

   =======================  ==========================  ==========================
   Aspect                   Wrong (Structural)          Correct (Strategic)
   =======================  ==========================  ==========================
   Decision-making          Top-down hierarchy          Collective discussion
   Information              Flows upward only           Circulates freely
   Implementation           Command from center         Coordinated execution
   Criticism                Discouraged after decision  Continuous evaluation
   Architecture             Centralized servers         Distributed nodes
   =======================  ==========================  ==========================
```

**DRUIDS implements the strategic interpretation**:

- Decisions made collectively with full information access
- Implementation coordinated but not commanded
- No single point of control or failure
- Continuous adaptation based on feedback

See {doc}`/concepts/dialectical_materialism` for why this matters.

## DRUIDS Design Principles

### 1. No Single Point of Control

(no-single-point)=

Every node in system has equal status. No "master" node, no central authority.

```text
Traditional Architecture:

     [Master Server]
     /    |    \
    /     |     \
 [A]    [B]    [C]

(If master fails, system fails)

DRUIDS Architecture:

   [A] ←→ [B]
    ↑  ⤨  ↑
    ↓  ⤧  ↓
   [C] ←→ [D]

(Any node can function independently, sync when possible)
```

**Implementation**: Conflict-free Replicated Data Types (CRDTs) enable nodes
to sync without consensus protocol. No node is "authoritative."

### 2. Weighted Edges / Desire Paths

Knowledge connections strengthen with use, fade with disuse. See
{doc}`/concepts/desire_paths` for full explanation.

**Why this matters for organizing**:

- Frequently-accessed information becomes easier to find
- Obsolete information naturally deprioritized
- Organic structure emerges from collective usage
- No librarian bottleneck

```python
# Each node tracks local usage patterns
class DRUIDSNode:
    def __init__(self):
        self.local_graph = Neo4jGraph()
        self.usage_tracker = UsageTracker()

    def traverse_link(self, from_doc, to_doc):
        """Strengthen edge on traversal"""
        edge = self.local_graph.get_edge(from_doc, to_doc)
        edge.weight *= 1.1
        edge.last_used = now()

        # Share usage data with other nodes
        self.broadcast_usage_signal({
            'from': from_doc,
            'to': to_doc,
            'timestamp': now(),
            'node_id': self.id
        })

    def receive_usage_signal(self, signal):
        """Incorporate others' usage patterns"""
        edge = self.local_graph.get_edge(signal['from'], signal['to'])
        edge.external_weight += 0.05  # Smaller than local usage

        # Collective desire paths emerge from aggregated signals
```

This implements both distribution (no central server) and emergence (structure
from usage).

### 3. Eventual Consistency

Nodes don't need to be in perfect sync at all times. They converge when connected.

**Why this is organizing-appropriate**:

- Works during internet outages
- Works despite censorship/filtering
- Tolerates node seizures (missing node = delayed sync, not failure)
- Mobile organizing possible (connect when you can)

```text
Node A creates document at 14:00
Node A offline from 14:01-16:00
Node B creates document at 15:00

16:00: Nodes sync
Both documents now on both nodes
No conflict (different documents)

If same document edited:
CRDT merge rules apply
Or: Last-write-wins with timestamp
Or: Manual merge for critical docs
```

### 4. Cryptographic Integrity

Each document signed by creator, changes tracked with cryptography.

```python
class SignedDocument:
    def __init__(self, content, author_key):
        self.content = content
        self.author_pubkey = author_key.public_key()
        self.created_at = now()
        self.signature = author_key.sign(
            self.content + self.created_at
        )
        self.versions = []

    def verify(self) -> bool:
        """Verify document hasn't been tampered with"""
        return self.author_pubkey.verify(
            self.signature,
            self.content + self.created_at
        )

    def update(self, new_content, author_key):
        """Create new version with signature"""
        if not self.verify():
            raise TamperError("Original document compromised")

        new_version = {
            'content': new_content,
            'timestamp': now(),
            'signature': author_key.sign(new_content + now()),
            'prev_hash': hash(self.content)
        }
        self.versions.append(new_version)
        self.content = new_content
```

**Benefits**:

- Detect tampering (state actor compromises node)
- Attribute documents (who wrote what)
- Audit trail (complete history)
- Trust without central authority

### 5. Graceful Degradation

System continues functioning at reduced capacity rather than failing completely.

```text
Full Network (all nodes online):
- Complete document access
- Real-time sync
- Full search across all nodes

Partial Network (some nodes offline):
- Access to local documents
- Access to cached remote documents
- Sync when connections restore

Isolated Node (no network):
- Full local document access
- Local editing continues
- Queue changes for later sync

Never: Total system failure
```

This mirrors cellular organization in underground movements—individual cells
can operate independently while coordinating when possible.

## Technical Architecture

### Storage Layer

**Per-node database**: Neo4j for graph structure with weighted edges

```cypher
// Each node maintains local graph
CREATE (doc:Document {
    id: 'dialectical_materialism_001',
    title: 'Dialectical Materialism',
    content: '...',
    created_at: timestamp(),
    author_pubkey: '...',
    signature: '...'
})

CREATE (doc2:Document {
    id: 'lumpen_organizing_001',
    title: 'Lumpen Organizing',
    ...
})

// Weighted edges track usage
CREATE (doc)-[:REFERENCES {
    weight: 1.0,
    local_traversals: 0,
    external_signals: 0,
    last_used: timestamp()
}]->(doc2)
```

**Full-text search**: Elasticsearch per node for fast local queries

**File storage**: IPFS for large attachments (videos, images, PDFs)

- Content-addressed (hash-based)
- Distributed storage
- Deduplication automatic

### Sync Protocol

```python
class DRUIDSSyncProtocol:
    """Synchronize between nodes using CRDT principles"""

    async def sync_with_peer(self, peer_node):
        """Bidirectional sync with another node"""

        # 1. Exchange document hashes
        my_hashes = self.get_all_document_hashes()
        peer_hashes = await peer_node.get_document_hashes()

        # 2. Identify differences
        i_need = peer_hashes - my_hashes
        they_need = my_hashes - peer_hashes

        # 3. Exchange missing documents
        for doc_id in i_need:
            doc = await peer_node.fetch_document(doc_id)
            self.merge_document(doc)

        for doc_id in they_need:
            doc = self.fetch_document(doc_id)
            await peer_node.send_document(doc)

        # 4. Exchange usage signals (weighted edges)
        my_usage = self.get_recent_usage_signals()
        await peer_node.receive_usage_signals(my_usage)

        peer_usage = await peer_node.get_usage_signals()
        self.incorporate_usage_signals(peer_usage)

    def merge_document(self, remote_doc):
        """Merge remote document with local version"""
        local_doc = self.local_graph.get(remote_doc.id)

        if not local_doc:
            # New document, just add it
            self.local_graph.add(remote_doc)
        else:
            # Both versions exist, merge
            merged = self.crdt_merge(local_doc, remote_doc)
            self.local_graph.update(merged)
```

### Network Topology

Nodes form mesh network, not star topology:

```text
Star (Centralized):

       [Master]
      /   |   \
     /    |    \
   [A]   [B]   [C]

(Master = single point of failure)

Mesh (Distributed):

   [A]--[B]
    | \/ |
    | /\ |
   [C]--[D]

Each node can connect to multiple peers
No hierarchy, no master
Redundant paths
```

**Connection strategy**:

- Bootstrap with known peers (physical meeting, secure channel)
- Discover peers through existing connections
- Maintain connections to N peers (e.g., 5-10)
- Prefer geographic/organizational diversity

### Access Control

**Problem**: Distributed system with no central authority—how to control access?

**Solution**: Cryptographic capabilities + social verification

```python
class AccessControl:
    """Capability-based access without central authority"""

    def __init__(self):
        self.my_keypair = load_keypair()
        self.trusted_keys = load_trusted_keys()
        self.capabilities = {}

    def grant_access(self, pubkey, resource, permissions):
        """Create signed capability token"""
        capability = {
            'resource': resource,
            'permissions': permissions,  # ['read', 'write', 'admin']
            'grantee': pubkey,
            'granter': self.my_keypair.public_key(),
            'issued_at': now(),
            'expires_at': now() + timedelta(days=90)
        }

        signature = self.my_keypair.sign(
            json.dumps(capability)
        )

        return {
            'capability': capability,
            'signature': signature
        }

    def verify_access(self, capability, signature, action):
        """Verify capability is valid"""

        # 1. Check signature
        granter_key = capability['granter']
        if not granter_key.verify(signature, json.dumps(capability)):
            return False

        # 2. Check granter is trusted
        if granter_key not in self.trusted_keys:
            return False

        # 3. Check not expired
        if now() > capability['expires_at']:
            return False

        # 4. Check permission includes action
        if action not in capability['permissions']:
            return False

        return True
```

**Web of trust**: Trust is transitive within limits

- Alice trusts Bob
- Bob trusts Carol
- Alice trusts Carol (up to N degrees, e.g., 2-3)

This prevents need for central authority while limiting exposure.

## Integration with Other Systems

### SICA Methodology

{doc}`/methods/sica_methodology` generates data—DRUIDS stores and distributes it.

**Use case**: Organizer in Baltimore conducts SICA analysis of West Baltimore ZIP
codes. Uploads results to DRUIDS node. Results sync to organizers in other cities
who can:

1. Learn from methodology
2. Compare to their local conditions
3. Adapt analysis for their context
4. Contribute back their findings

Collective knowledge accumulates without central repository.

### Lumpen Organizing Infrastructure

{doc}`/concepts/lumpen_organizing` requires secure communication and knowledge
sharing. DRUIDS provides:

**Documentation**:

- Strategic analysis
- Tactical guides
- Legal resources
- Historical examples

**Coordination**:

- Event planning (encrypted, distributed)
- Resource sharing (mutual aid networks)
- Security alerts (police activity, raids)

**Analysis**:

- Aggregate organizing reports
- Track trends across regions
- Evaluate what works

### Connection to Desire Paths

{doc}`/concepts/desire_paths` implemented via weighted edges. As organizers
use DRUIDS:

- Frequently-accessed connections strengthen
- Related documents become easier to discover
- Obsolete information naturally deprioritized
- Structure emerges from collective usage

No central librarian imposing categories. Organic architecture from practice.

## Security Model

### Threat Analysis

**Adversaries**:

1. Law enforcement (FBI, local police, fusion centers)
2. Corporate surveillance (ISPs, platform providers)
3. Fascist organizations (doxxing, harassment)
4. State-level actors (NSA, intelligence agencies)

**Vulnerabilities**:

- Network traffic analysis (who talks to whom)
- Node seizure (physical or digital)
- Compromised members (informants, infiltration)
- Backdoored software (supply chain attacks)

### Mitigations

**Defense in depth**:

```text
Layer 1: Encryption
└── All data encrypted at rest and in transit
    └── Age encryption for documents
    └── TLS 1.3 for network

Layer 2: Traffic obfuscation
└── Tor for node connections
└── I2P as alternative
└── Random delays, padding

Layer 3: Compartmentalization
└── Nodes know only direct peers
└── Documents marked with sensitivity
└── Need-to-know access

Layer 4: Physical security
└── Full-disk encryption
└── Secure boot
└── Kill switches (remote wipe)

Layer 5: Social security
└── Vetting processes
└── Security culture
└── Incident response plans
```

**Against node seizure**:

- Full disk encryption (LUKS)
- Encrypted backups on multiple nodes
- No single node has complete dataset
- Cryptographic signatures prevent tampering

**Against traffic analysis**:

- Tor hidden services for node communication
- Random delays in sync protocol
- Padding to obscure message sizes
- Cover traffic (dummy syncs)

**Against infiltration**:

- Web of trust limits
- Capability expiration
- Document attribution (know who added what)
- Audit logs (read-only append)

:::{warning}
**No system is perfect**. DRUIDS reduces risk but doesn't eliminate it.
Security culture (training, practices, discipline) matters more than tools.
:::

## Limitations and Tradeoffs

### What DRUIDS Doesn't Solve

❌ **User incompetence**: If someone writes passwords in plain text, no system helps

❌ **Social engineering**: Fooling users into revealing access

❌ **Rubber-hose cryptanalysis**: Physical coercion for keys

❌ **Compromised endpoints**: Malware on user device

❌ **All surveillance**: Traffic analysis still possible despite Tor

### Tradeoffs

**Complexity vs. Security**: More secure = more complex = harder to use correctly

- Solution: Good defaults, extensive documentation, training

**Latency vs. Availability**: Eventual consistency = slower sync

- Solution: Most content isn't time-critical. Real-time comms use Signal.

**Decentralization vs. Discoverability**: No central search = harder to find things

- Solution: Weighted edges create emergent structure. Full-text search per node.

## Comparison to Alternatives

```{eval-rst}
.. table:: DRUIDS vs. Alternatives
   :widths: 20 20 20 20 20

   ==============  =======  ========  =========  ============  ==========
   Feature         DRUIDS   Git+SSH   Corporate  Self-Hosted   P2P Tools
   ==============  =======  ========  =========  ============  ==========
   Distributed     ✓        ✓         ✗          ✗             ✓
   Encrypted       ✓        Partial   Partial    Optional      ✓
   User-friendly   Medium   Low       High       Medium        Low
   Seizure-proof   ✓        Partial   ✗          ✗             ✓
   Search          ✓        Limited   ✓          ✓             Limited
   Weights/Paths   ✓        ✗         ✗          ✗             ✗
   FOSS            ✓        ✓         ✗          ✓             ✓
   ==============  =======  ========  =========  ============  ==========
```

## Implementation Status

### Current State

**Completed**:

- Theoretical framework
- Threat model
- Core architectural design
- CRDT sync protocol (proof-of-concept)

**In Progress**:

- Neo4j weighted edge implementation
- MCP server for federal APIs (SICA integration)
- Tor integration for node communication

**Planned**:

- Web UI for document management
- Mobile apps (iOS/Android)
- Federation with other networks (ActivityPub?)
- Backup/restore tooling

### Roadmap

**Phase 1** (Q1 2025): Core functionality

- Document storage and sync
- Basic search
- CLI interface

**Phase 2** (Q2 2025): Usability

- Web UI
- Weighted edges functional
- Access control implemented

**Phase 3** (Q3 2025): Deployment

- Mobile apps
- Production hardening
- User documentation and training

**Phase 4** (Q4 2025): Integration

- SICA methodology integration
- Federation capabilities
- Extended API for custom tools

### Getting Involved

**Code**: github.com/percy/druids (fictional path)

**Documentation**: docs.druids.network (fictional URL)

**Funding**: Reject VC, accept grassroots donations only

- No investors = no investors to please = no compromises on principles

## Connections

**Theoretical Foundation**:

- {doc}`/concepts/dialectical_materialism` - Materialism applied to architecture
- {doc}`/concepts/desire_paths` - Emergent structure without central control

**Applied Methodology**:

- {doc}`/methods/sica_methodology` - Data infrastructure for organizing
- {doc}`/concepts/lumpen_organizing` - Who this serves

**Design Philosophy**:

- {term}`democratic centralism` - Strategy, not structure
- {term}`praxis` - System design informed by organizing needs

## Further Reading

### Distributed Systems

- Kleppmann, Martin. *Designing Data-Intensive Applications* (2017)
- Shapiro et al. "Conflict-Free Replicated Data Types" (2011)

### Security

- Schneier, Bruce. *Data and Goliath* (2015)
- Micah Lee. *Hacks, Leaks, and Revelations* (2024)

### Revolutionary Organization

- Lenin. *What Is To Be Done?* (1902) - Organizational principles
- Mao. *On Guerrilla Warfare* (1937) - Cell structure, decentralization

### Technical Docs

- IPFS whitepaper: <https://ipfs.io/ipfs/whitepaper>
- Neo4j graph algorithms: <https://neo4j.com/docs/graph-data-science>
- Tor project: <https://www.torproject.org/docs>

:::{note}
**Meta-observation**: DRUIDS itself demonstrates {term}`praxis`—theoretical
analysis (dialectical materialism, desire paths, democratic centralism)
immediately applied to solve material problem (secure, distributed organizing
infrastructure). Theory and practice unified.

This is what revolutionary technology looks like: Not "disruptive innovation"
for profit, but tools designed for specific political needs, grounded in
theoretical analysis, built to serve movements rather than markets.
:::
