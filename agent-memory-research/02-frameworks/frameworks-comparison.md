# Agent Memory Frameworks: Side-by-Side Comparison

**As of April 2026**

---

## Quick-Select Guide

| If you need... | Use |
|----------------|-----|
| Add memory to an existing agent, minimal refactoring | **Mem0** |
| Agent-controlled memory with OS-level self-management | **Letta** |
| Graph-based relational memory with Neo4j | **Graphiti** |
| State persistence + human-in-the-loop for a LangGraph agent | **LangGraph checkpointing** |
| All memory types in one opinionated framework | **Letta** |
| Cloud-managed, zero-ops memory | **Mem0 Cloud** |

---

## Detailed Comparison Table

| Dimension | Letta | Mem0 | LangGraph | Graphiti |
|-----------|-------|------|-----------|---------|
| **Primary model** | Agent-controlled (OS pattern) | Pipeline-based extraction | Graph state + checkpoints | Knowledge graph |
| **Memory types** | Working + Episodic + Semantic + Procedural | Episodic + Semantic | Working (state) | Episodic + Semantic (relational) |
| **Agent framework** | Self-contained | Any framework | LangGraph only | Any framework |
| **Storage backends** | PostgreSQL + vector DB | Vector + Graph + KV | Pluggable (Postgres/Redis/Mongo) | Neo4j |
| **Multi-agent support** | Yes (shared memory blocks) | Yes (user_id scoping) | Yes (shared store) | Yes (shared graph) |
| **Managed cloud** | Letta Cloud | Mem0 Cloud | LangSmith / AWS | Neo4j Aura |
| **GitHub stars (Apr 2026)** | ~15k | ~48k | ~45k | ~10k |
| **License** | Apache 2.0 | Apache 2.0 | MIT | Apache 2.0 |
| **Write latency** | Real-time (tool call) | 2–10s (background extraction) | ~0ms (state save) | 2–10s (graph update) |
| **Read latency** | 50–200ms (vector search) | 10–200ms (hybrid search) | <10ms (checkpoint restore) | 50–300ms (graph traversal) |
| **Relational queries** | Limited | Via Mem0g graph mode | No | Excellent |
| **Temporal tracking** | Basic (timestamps) | Basic | None (state snapshots) | Excellent (edge validity periods) |
| **GDPR/compliance** | Via self-hosted | Via self-hosted or Cloud controls | Via backend choice | Via Neo4j controls |
| **Operational complexity** | Medium | Low–Medium | Low | High |
| **Best for** | Long-running persistent agents | Adding memory to any agent | LangChain/LangGraph workloads | Entity-rich, relational domains |

---

## Architecture Philosophy

### Letta
The agent is the memory manager. Tools give it read/write access to its own memory stores. The mental model is an OS: the agent decides what to remember and what to forget, moves data between tiers, and writes its own notes to archival storage.

*Analogy: The agent is both the user and the sysadmin of its own memory.*

### Mem0
Memory management is a background service. A separate LLM-based pipeline extracts facts from conversations, deduplicates them, resolves contradictions, and stores them. The agent just gets context injected or calls a search tool.

*Analogy: The agent has a personal assistant who takes notes for it.*

### LangGraph
Memory is graph state. The checkpointer takes a snapshot of the graph's full state after each step. Long-term memory is stored in a separate Store object that persists across threads. The framework doesn't prescribe *what* to store, just *how*.

*Analogy: The agent has a save file and a shared notebook.*

### Graphiti
Memory is a living knowledge graph. Every new piece of information is processed to extract entities and relationships, which are merged into an existing graph with temporal versioning. Retrieval is graph traversal, not vector search.

*Analogy: The agent has a continuously updated wiki about everything it has learned.*

---

## Integration Patterns

### Layered combination (recommended for production)

Most sophisticated production systems combine frameworks:

```
┌─────────────────────────────────────────────┐
│           Production Agent                  │
│                                             │
│  LangGraph (orchestration + state)          │
│       │                                     │
│       ├── Mem0 (episodic + semantic memory) │
│       │        uses Qdrant + Redis          │
│       │                                     │
│       └── Graphiti (relational memory)      │
│                uses Neo4j                   │
└─────────────────────────────────────────────┘
```

### Simpler single-framework setups

- **Prototype / small scale:** Mem0 library + in-process Qdrant (Chroma)
- **Mid-scale team agent:** Letta self-hosted
- **Large-scale multi-tenant:** Mem0 Cloud + LangGraph with PostgresSaver
- **Entity-heavy domain (CRM, knowledge base):** Graphiti + Neo4j Aura

---

## Cost Comparison (approximate, April 2026)

| Tier | Letta | Mem0 | LangGraph (self-hosted infra) |
|------|-------|------|-------------------------------|
| Dev/local | Free | Free | Free |
| 1k users/day | ~$50/mo (cloud) | ~$30/mo (cloud) | ~$20/mo (Postgres) |
| 100k users/day | Custom | ~$500/mo | ~$200/mo (Postgres) |

*Note: All cloud pricing is approximate and changes frequently.*

---

## Sources

- [Best AI Agent Memory Frameworks in 2026: Compared and Ranked (Atlan)](https://atlan.com/know/best-ai-agent-memory-frameworks-2026/)
- [The 6 Best AI Agent Memory Frameworks You Should Try in 2026 (MLMastery)](https://machinelearningmastery.com/the-6-best-ai-agent-memory-frameworks-you-should-try-in-2026/)
- [Top 6 AI Agent Memory Frameworks for Devs (2026) (DEV Community)](https://dev.to/nebulagg/top-6-ai-agent-memory-frameworks-for-devs-2026-1fef)
- [Top 10 AI Memory Products 2026 (Medium)](https://medium.com/@bumurzaqov2/top-10-ai-memory-products-2026-09d7900b5ab1)
- [AI Agent Memory: Types, Architecture & Implementation (Redis)](https://redis.io/blog/ai-agent-memory-stateful-systems/)
