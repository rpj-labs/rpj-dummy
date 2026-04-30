# Graphiti: Real-Time Knowledge Graph Memory

**Repository:** https://github.com/getzep/graphiti
**Neo4j blog:** https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/

---

## What It Is

Graphiti is a real-time, temporally-aware knowledge graph engine designed specifically as memory infrastructure for AI agents. It was built as an alternative to traditional RAG for memory use cases where relationships between facts matter as much as the facts themselves.

---

## Why Not Just RAG?

Standard RAG stores text chunks as isolated vectors. For factual memory, this causes problems:

| Problem | RAG | Graphiti |
|---------|-----|---------|
| "Who does Alice work with?" | Might find Alice's bio, but not her colleagues | Graph traversal finds all colleagues directly |
| Fact update ("Alice now works at ACME") | Old fact stays; both conflict | Entity node is updated; old edge is timestamped |
| "What did the user believe before they changed their mind?" | No temporal tracking | Edge timestamps preserve full history |
| Entity deduplication | "Alice Smith" and "Alice from Engineering" are separate chunks | Both resolve to the same entity node |

---

## Core Concepts

### Node Types

```
┌─────────────────────────────────────────────────────────┐
│  EPISODIC NODES                                         │
│  Specific events with timestamps                        │
│  "User said X during session on 2026-03-15"            │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  ENTITY NODES                                           │
│  Canonical, deduplicated real-world objects             │
│  Person, Company, Tool, Concept                         │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  COMMUNITY NODES                                        │
│  Auto-generated clusters of related entities            │
│  "Python ecosystem", "Alice's tech stack"               │
└─────────────────────────────────────────────────────────┘
```

### Edge Types

- **Entity → Entity**: directional relationships with timestamps and expiry
- **Episodic → Entity**: links events to the entities they mention
- **Community → Entity**: cluster membership edges

Every edge carries:
- `valid_from` — when the relationship became true
- `valid_until` — when it stopped being true (null = still current)
- `source_episode` — which conversation produced this edge
- `confidence` — extraction confidence score

---

## Real-Time Processing

Graphiti's key differentiator: it processes incoming data incrementally, not in batch:

```
New message arrives
       │
       ▼
[Entity extractor]
  LLM identifies entities mentioned
       │
       ▼
[Deduplication]
  Match new entities against existing nodes
  ("Alice Smith" → existing node "Alice Smith @ Acme")
       │
       ▼
[Relationship extractor]
  LLM identifies relationships between entities
       │
       ▼
[Conflict resolution]
  Check if new edges contradict existing edges
  Mark old edges as expired if superseded
       │
       ▼
[Graph update]
  Write new nodes and edges to Neo4j
  Update community detection
```

This runs in seconds, not minutes, making it suitable for real-time agents.

---

## Installation

```bash
pip install graphiti-core
```

Requires a running Neo4j instance:

```bash
docker run -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5
```

---

## Basic Usage

```python
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

# Initialize with Neo4j connection and LLM
graphiti = Graphiti(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
)
await graphiti.build_indices_and_constraints()

# Add a conversation episode
await graphiti.add_episode(
    name="session-2026-03-15",
    episode_body="User said they are migrating from AWS to GCP next quarter. \
                  They use Terraform for infra management.",
    source=EpisodeType.message,
    reference_time=datetime.now(),
    source_description="Customer support chat"
)

# Search the graph
results = await graphiti.search("What cloud provider does the user use?")
for r in results:
    print(r.fact)
# → "User is migrating from AWS to GCP"
# → "User uses Terraform for infrastructure"
```

---

## Advanced: Neo4j Agent Memory Library (2026)

Neo4j released `neo4j-agent-memory` as a first-class integration with the Microsoft Agent Framework, Google ADK, and others:

```python
from neo4j_agent_memory import Neo4jMemoryProvider

memory = Neo4jMemoryProvider(
    uri="bolt://localhost:7687",
    auth=("neo4j", "password"),
    agent_id="assistant-v2"
)

# Three memory tiers
memory.short_term.add(message)              # current session
memory.long_term.semantic.add(fact)         # structured facts
memory.long_term.episodic.add(episode)      # conversation logs
memory.reasoning.add(tool_call_trace)       # agent's own reasoning
```

---

## Neo4j GraphRAG Context Provider (Microsoft Agent Framework)

As of 2026, the Neo4j GraphRAG Context Provider is a first-party integration in the Microsoft Agent Framework:

```python
from agent_framework import Agent
from neo4j_graphrag import Neo4jGraphRAGContextProvider

context = Neo4jGraphRAGContextProvider(
    neo4j_url="bolt://...",
    vector_index="memory_vectors",
    search_mode="hybrid",         # vector + fulltext
    graph_traversal_depth=2       # follow edges 2 hops out
)

agent = Agent(
    model="gpt-4o",
    context_providers=[context]
)
```

---

## Performance Characteristics

| Operation | Typical Latency | Notes |
|-----------|----------------|-------|
| Episode ingestion | 2–10s | LLM extraction + Neo4j writes |
| Graph search | 50–300ms | Depending on traversal depth |
| Community detection | Minutes | Batch job, run periodically |
| Entity dedup | 100–500ms | Per new entity |

GraphRAG implementations show ~5x query speed improvement over traditional RAG on relationship queries, and ~60% hallucination reduction on facts that involve entity relationships.

---

## When to Choose Graphiti / Neo4j

**Choose when:**
- Domain has complex entity relationships (org charts, tech stacks, social graphs)
- You need temporal fact tracking (what was true when)
- Multi-hop queries are common ("find tools used by Alice's team members")
- Accuracy on relational questions matters more than retrieval speed

**Don't choose when:**
- Simple preference/fact storage with no relational queries
- Latency is the primary constraint (vector-only is faster)
- Team has no Neo4j operational experience

---

## Sources

- [Graphiti: Knowledge Graph Memory for an Agentic World (Neo4j)](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/)
- [GitHub: neo4j-labs/agent-memory](https://github.com/neo4j-labs/agent-memory)
- [Building an AI Agent with Memory: Microsoft Agent Framework + Neo4j (Medium)](https://medium.com/neo4j/building-an-ai-agent-with-memory-microsoft-agent-framework-neo4j-e3eab8f09694)
- [Neo4j GraphRAG Context Provider for Agent Framework (Microsoft Learn)](https://learn.microsoft.com/en-us/agent-framework/integrations/neo4j-graphrag)
- [Neo4j Memory Provider for Agent Framework (Microsoft Learn)](https://learn.microsoft.com/en-us/agent-framework/integrations/neo4j-memory)
