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
| Local-first, offline, hierarchical/spatial memory | **MemPalace** |
| Native Claude agent memory (Claude Code or API) | **Anthropic memory tools** |
| Personal LLM-maintained knowledge base (no vector DB) | **Karpathy LLM Wiki** |

---

## Detailed Comparison Table

| Dimension | Letta | Mem0 | LangGraph | Graphiti | MemPalace | Anthropic tools |
|-----------|-------|------|-----------|---------|-----------|-----------------|
| **Primary model** | Agent-controlled (OS) | Pipeline extraction | Graph state + checkpoints | Knowledge graph | Spatial hierarchy | Filesystem CRUD |
| **Memory types** | All four | Episodic + Semantic | Working (state) | Episodic + Semantic | All four (verbatim-first) | All four (file-based) |
| **Agent framework** | Self-contained | Any framework | LangGraph only | Any framework | Any / MCP | Claude only |
| **Storage backends** | PostgreSQL + vector | Vector + Graph + KV | Pluggable | Neo4j | SQLite + Chroma + FS | Filesystem |
| **Multi-agent support** | Yes (shared blocks) | Yes (user_id) | Yes (shared store) | Yes (shared graph) | No (single-user) | Yes (managed agents) |
| **Managed cloud** | Letta Cloud | Mem0 Cloud | LangSmith / AWS | Neo4j Aura | No | Anthropic hosted |
| **GitHub stars (Apr 2026)** | ~15k | ~48k | ~45k | ~10k | ~47k | N/A (official) |
| **License** | Apache 2.0 | Apache 2.0 | MIT | Apache 2.0 | MIT | Proprietary |
| **Write latency** | Real-time (tool call) | 2–10s (background) | ~0ms (state save) | 2–10s (graph update) | ~0ms (verbatim) | ~0ms (file write) |
| **Read latency** | 50–200ms | 10–200ms | <10ms | 50–300ms | ~170 token wake-up | Depends on file size |
| **Relational queries** | Limited | Via graph mode | No | Excellent | Via cross-references | No |
| **Temporal tracking** | Basic | Basic | None | Excellent | Basic (SQLite) | None |
| **Works offline** | No | No | Yes | No | Yes | Yes (local mode) |
| **GDPR/compliance** | Via self-hosted | Via self-hosted/cloud | Via backend | Via Neo4j | Local, no external | Via Anthropic controls |
| **Operational complexity** | Medium | Low–Medium | Low | High | Very Low | None |
| **Best for** | Long-running persistent agents | Adding memory to any agent | LangChain workloads | Entity-rich relational | Local, offline, single-user | Claude API / Claude Code |

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

### MemPalace (April 2026)
Memory is a spatial palace. Information is stored verbatim first (zero extraction cost) and organized into a named hierarchy: wings → halls → rooms → drawers (raw) / closets (compressed). The 170-token index is always loaded; specific rooms loaded on demand. Deliberately local-first, offline-capable, single-user.

*Analogy: The agent has a well-organized filing cabinet where it knows exactly where things are without reading everything.*

### Anthropic Memory Tools
Memory is a filesystem. Claude reads and writes markdown files in a `/memories` directory using tool calls. Works for both Claude Code (CLAUDE.md + auto-dream) and the Claude API (type `memory_20250818`). The agent journals its own progress and reads its notes before starting each session.

*Analogy: The agent keeps a notebook that it writes in and reads back from — first thing every session.*

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
