# Core Memory Architectures for AI Agents

Three architectural patterns dominate how memory is structured in production agents as of 2026. They are not mutually exclusive — real systems often combine elements of all three.

---

## Architecture 1: OS-Inspired Hierarchical Memory

**Origin:** MemGPT (2023), productized as Letta

**Core idea:** Treat the LLM's context window like RAM in an operating system. An agent can *actively manage* what's in-context (fast but limited) versus what's on-disk (slow but unlimited), just as an OS manages physical memory.

### Memory Tiers

```
┌─────────────────────────────────────────┐
│          CORE MEMORY (RAM)              │  Always in context
│  - System persona / agent identity      │  ~2–4K tokens
│  - Human profile (current session user) │
│  - Scratchpad for active reasoning      │
└────────────────┬────────────────────────┘
                 │ agent-controlled reads/writes
┌────────────────▼────────────────────────┐
│         RECALL MEMORY (L2 Cache)        │  Conversation history
│  - Past messages (current + prior)      │  Retrieved by relevance
│  - Searchable by keyword/semantic query │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        ARCHIVAL MEMORY (Disk)           │  External long-term store
│  - Arbitrary agent notes                │  Unlimited capacity
│  - Documents, facts, long-form content  │  Retrieved by ANN search
└─────────────────────────────────────────┘
```

### How the agent self-manages

The agent has tool calls like:
- `memory_search(query)` — retrieve from archival
- `memory_insert(content)` — write to archival
- `core_memory_replace(section, content)` — edit working memory
- `conversation_search(query)` — search recall store

When context fills up, the agent proactively compresses or offloads content — it's not done externally.

### Strengths
- Agent has full autonomy over its own memory
- Natural handling of very long interactions
- Principled separation of concerns

### Weaknesses
- Adds tool call overhead to every response
- Requires the agent to be smart enough to manage its own memory reliably
- Can fail if agent makes poor eviction decisions

---

## Architecture 2: Pipeline-Based Memory (Extract-Store-Retrieve)

**Origin:** Mem0, various RAG-based systems

**Core idea:** Memory management is an *external pipeline*, not part of the agent's reasoning loop. A separate system extracts, deduplicates, stores, and retrieves memories. The agent just has a `search_memory(query)` tool or gets relevant memories injected automatically.

### Pipeline Stages

```
Session ends
     │
     ▼
[Extractor LLM]
  Reads session transcript
  Extracts: facts, preferences, events
  Deduplicates against existing store
  Resolves contradictions
     │
     ▼
[Storage Layer]
  Vector DB ────── semantic facts, episode summaries
  Knowledge Graph ─ entity relationships
  Key-Value Store ─ explicit preferences, profile data
     │
     ▼
[Retriever]
  At session start or per-turn:
  Query = user message + conversation context
  Fetch top-k memories from all stores
  Inject into system prompt or context
```

### Mem0 specifics (2026)

Mem0 implements this pattern with:
- LLM-driven extraction (default: GPT-4o-mini equivalent)
- Three storage backends simultaneously: vector, graph, KV
- Hybrid search: dense vector + sparse (BM25) + graph traversal
- Background processing so session latency is unaffected

### Strengths
- Agent doesn't need to know about memory — it's transparent
- Easy to add to existing agent systems
- Background processing doesn't block response time
- Memory management logic can be tuned independently

### Weaknesses
- Extraction quality depends on LLM quality
- Introduces pipeline latency (seconds) on writes
- Agent can't proactively "choose to remember" something

---

## Architecture 3: Graph-Structured Memory

**Origin:** Graphiti (2025), MAGMA, A-Mem

**Core idea:** Store memories not as flat vectors but as a knowledge graph where nodes are entities (people, concepts, events) and edges are relationships. Traversal allows multi-hop reasoning that flat vector search can't do.

### Structure

```
User ──── worksAt ────► Acme Corp
 │                           │
 │                        hasStack
 │                           │
 └──── prefersTool ──► VSCode   Python
                        │
                    version: 3.12
                    since: 2025-03
```

### Key properties of graph memory

1. **Temporal awareness** — edges carry timestamps; facts are versioned
2. **Entity deduplication** — "Bob" and "Robert Chen" resolve to the same node
3. **Relationship reasoning** — "Find all tools used by people at Acme" is a graph traversal
4. **Incremental updates** — add edges without recomputing the whole graph
5. **Community detection** — cluster related concepts automatically

### Graphiti's approach

Graphiti processes incoming data in real-time, instantly updating entities and relationships without batch recomputation. It distinguishes between:
- **Episodic nodes** — specific events with timestamps
- **Entity nodes** — deduplicated, canonical objects
- **Community nodes** — automatically grouped clusters of related entities

### Performance trade-off (Mem0 benchmark)

| System | LLM Score | P95 Latency |
|--------|-----------|-------------|
| Vector-only (Mem0) | 66.9% | 1.44s |
| Graph-augmented (Mem0g) | 68.4% | 2.59s |

Graph wins on complex multi-hop questions. Vector wins on speed and simple lookups.

### Strengths
- Excels at relational and multi-hop queries
- Naturally represents "who knows whom" and entity histories
- More robust to duplicate information

### Weaknesses
- Higher operational complexity (need a graph DB)
- Slower writes and reads vs. vector-only
- Requires careful schema design

---

## Hybrid Architecture (2026 Best Practice)

Most production systems in 2026 combine all three:

```
                    Agent
                      │
          ┌───────────┼───────────┐
          │           │           │
    [In-Context]  [Pipeline]  [Graph]
    Core memory   Mem0/custom  Graphiti/Neo4j
    ~4K tokens    vector+KV    relationships
          │           │           │
          └───────────▼───────────┘
                 Unified Retriever
                 (Hybrid search: ANN + BM25 + graph traversal)
                      │
                 Ranked, deduplicated
                 context injection
```

**Rule of thumb:** Start with pipeline-based extraction (Mem0 pattern), add graph edges for relationship-heavy domains, use core memory management (Letta pattern) only if you need agent-driven memory curation.

---

## Sources

- [Memory Blocks: The Key to Agentic Context Management (Letta)](https://www.letta.com/blog/memory-blocks)
- [Graphiti: Knowledge Graph Memory for an Agentic World (Neo4j)](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/)
- [Graph-based Agent Memory: Taxonomy, Techniques, Applications (arXiv 2602.05665)](https://arxiv.org/html/2602.05665v1)
- [State of AI Agent Memory 2026 (Mem0)](https://mem0.ai/blog/state-of-ai-agent-memory-2026)
- [Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory (arXiv 2504.19413)](https://arxiv.org/abs/2504.19413)
