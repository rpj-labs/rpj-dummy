# MemPalace: Spatial Hierarchical Memory for AI Agents

**Repository:** https://github.com/milla-jovovich/mempalace
**Stars (April 2026):** 47,000+ (22k in first 48 hours)
**Created by:** Milla Jovovich (actress) and Ben Sigman (developer)
**Released:** April 6, 2026
**Paper:** arXiv 2604.21284 — "Spatial Metaphors for LLM Memory: A Critical Analysis"

---

## Why It Went Viral

MemPalace hit 22,000 GitHub stars in 48 hours after release — unusual velocity even for AI tooling. Two factors:
1. The creator (Milla Jovovich) had no prior AI profile, which generated enormous coverage
2. The claimed benchmark score (initially 100%, revised to 96.6% on LongMemEval) was the highest reported for any open-source memory system

The benchmark story became controversial (see "Benchmarks: What's Real" below), but the underlying architecture is genuinely novel and the project is worth understanding on its technical merits.

---

## Core Concept: Method of Loci Applied to AI Memory

The method of loci (memory palace) is a mnemonic technique dating to ancient Greece: you mentally place information in specific locations in a familiar spatial structure (a palace, a route), then walk through it to retrieve items. The spatial structure provides reliable retrieval cues.

MemPalace applies this as a **hierarchical indexing structure** for AI agent memory. Rather than a flat vector store or a graph, memories are organized into a named spatial hierarchy that both humans and LLMs can navigate deterministically.

---

## The Spatial Hierarchy

```
Palace
├── Wing: "People"
│   ├── Hall: "Colleagues"
│   │   ├── Room: "Alice"
│   │   │   ├── Closet: [compressed summary of everything about Alice]
│   │   │   └── Drawer: [verbatim original notes about Alice]
│   │   └── Room: "Bob"
│   └── Hall: "Customers"
│
├── Wing: "Projects"
│   ├── Hall: "Active"
│   │   └── Room: "Payments API"
│   │       ├── Closet: [compressed project summary]
│   │       └── Drawer: [verbatim project notes]
│   └── Hall: "Archived"
│
└── Wing: "Knowledge"
    ├── Hall: "Technical"
    │   ├── Room: "Kubernetes"
    │   └── Room: "FastAPI"
    └── Hall: "Domain"
```

The levels map to semantic granularity:
- **Wings** — broad domains (people, projects, knowledge)
- **Halls** — subcategories within a wing
- **Rooms** — specific entities or topics
- **Closets** — compressed summaries (fast read, lossy)
- **Drawers** — verbatim originals (slow read, lossless)

---

## The Verbatim-First Philosophy

MemPalace's most contrarian design choice: **store verbatim first, compress separately**.

Most memory systems (Mem0, Letta) extract structured facts from conversations at write time. MemPalace stores the raw text first in drawers, then optionally compresses it into closets. This is similar to the MemMachine "immutable episode" approach (see `05-challenges-and-mitigations/memory-drift.md`).

**Why this matters:**
- Zero extraction errors at write time (nothing is interpreted)
- You can always re-derive compressed summaries from originals
- Compression is lossy by definition — deferring it keeps all options open
- Write path requires zero LLM calls, making it fast and cheap

```
Session ends
     │
     ▼
Verbatim text → stored in Drawer (exact, immediate, free)
     │
     ▼ (optional, async)
LLM summarizes Drawer → stored in Closet (lossy, but fast to retrieve)
```

---

## AAAK Compression

MemPalace introduces a custom compression format called **AAAK** (Aggressive Abbreviation Any LLM Can Decode):

- Uses standard abbreviations any LLM can decode without a special parser
- Claims up to 30x token reduction vs. verbatim text

**Important caveat (verified by independent testing):**

Enabling AAAK drops LongMemEval accuracy from **96.6% to 84.2%** — a 12.4 percentage point quality loss. The "30x lossless" claim in the original README was misleading; AAAK is lossy in practice. The team acknowledged this and updated their documentation after the review.

**Use AAAK:** When token cost is the constraint and some accuracy loss is acceptable (e.g., archival of low-priority memories).
**Don't use AAAK:** For high-stakes memories (core user facts, critical decisions).

---

## The Four-Layer Memory Stack

MemPalace implements a four-layer stack designed to minimize "wake-up cost" — the tokens needed to orient the agent at the start of a new session:

```
Layer 1: Index (always loaded, ~170 tokens)
  - The palace map: list of all wings/halls/rooms
  - Which rooms have content
  - Last-modified timestamps
  Cost: ~170 tokens per session, always

Layer 2: Closets (loaded on demand, ~50-200 tokens each)
  - Compressed summaries of rooms
  - LLM reads the index, decides which rooms are relevant, loads closets
  Cost: proportional to relevant topics

Layer 3: Drawers (loaded on demand, full verbatim)
  - Original raw notes
  - Only loaded when closet is insufficient
  Cost: variable, avoid loading unnecessarily

Layer 4: Cross-references (navigated on demand)
  - Links between rooms (Alice → Payments API)
  - Bidirectional
  Cost: each cross-reference fetch costs one Drawer read
```

The 170-token wake-up cost is a key claim. Compare to: Letta's core memory (~2-4k tokens always in context), Mem0's session start injection (~500-2000 tokens). MemPalace claims to beat both on wake-up cost when most topics are irrelevant to the current query.

---

## Storage Backend

MemPalace uses a deliberately simple backend:

| Component | Storage |
|-----------|---------|
| Palace index | SQLite |
| Rooms (verbatim / drawers) | Local filesystem (markdown files) |
| Closets (compressed summaries) | SQLite + filesystem |
| Vector embeddings (for semantic search) | ChromaDB |
| Temporal knowledge graph (fact validity) | SQLite (with valid_from/valid_until) |

This is intentionally local-first. No external database required. Works offline. Everything is human-readable.

---

## MCP Integration

MemPalace ships a native MCP (Model Context Protocol) server:

```json
// Claude Code ~/.claude/settings.json
{
  "mcpServers": {
    "mempalace": {
      "command": "uvx",
      "args": ["mempalace-mcp"],
      "env": {
        "MEMPALACE_PATH": "~/.mempalace"
      }
    }
  }
}
```

Once added, Claude can navigate the palace by calling MCP tools:
- `palace_index()` — view the full structure
- `open_room(wing, hall, room)` — read a specific room
- `write_to_drawer(wing, hall, room, content)` — store verbatim content
- `update_closet(wing, hall, room)` — regenerate summary for a room
- `search_palace(query)` — semantic search across all drawers

---

## Installation and Quick Start

```bash
pip install mempalace

# Initialize a palace
mempalace init ~/.mempalace

# Optional: add custom palace structure
mempalace config add-wing "Projects"
mempalace config add-hall "Projects" "Active"

# Run the MCP server
mempalace serve
```

```python
from mempalace import Palace

palace = Palace("~/.mempalace")

# Store a memory (goes to drawer immediately)
palace.write(
    wing="People",
    hall="Colleagues",
    room="Alice",
    content="Alice mentioned she's joining Acme Corp as senior engineer starting March 1.",
    verbatim=True  # store as-is, no extraction
)

# Read back
room_content = palace.read(wing="People", hall="Colleagues", room="Alice")

# Semantic search
results = palace.search("what company does Alice work at?")

# Compress a room into its closet (async, optional)
palace.compress_room("People", "Colleagues", "Alice")
```

---

## Benchmark Context: What's Real

| Claim | Status |
|-------|--------|
| "100% LongMemEval score" | **Retracted.** Achieved by hand-tuning fixes for failing questions and retesting on the same set. |
| "96.6% Recall@5 on LongMemEval" | **Verified real.** Best published score for an open-source memory system as of April 2026. |
| "30x lossless compression via AAAK" | **Misleading.** AAAK is lossy; 96.6% drops to 84.2% when AAAK is enabled. |
| "+34% retrieval boost vs. flat storage" | **Partially verified.** True for multi-hop queries; near-zero difference for simple lookups. |

The team responded transparently to criticism, updated the README, and the honest numbers remain impressive. The arXiv paper (2604.21284) provides a critical analysis and independent replication.

---

## When to Choose MemPalace

**Choose MemPalace when:**
- You want a local, offline-first memory system
- Your memory domains have natural hierarchical structure (people, projects, topics)
- You value verbatim storage with zero write-time LLM cost
- You're using Claude Code via MCP and want palace navigation built in
- Token efficiency at retrieval time matters (low wake-up cost)

**Don't choose MemPalace when:**
- You need a cloud-hosted, managed service (Mem0 Cloud or Letta Cloud fit better)
- Your memory is user-scoped in a multi-tenant SaaS (MemPalace is single-user by design)
- You need deep entity relationship traversal (Graphiti/Neo4j is stronger)
- You need compliance controls (GDPR deletion, HIPAA audit trails)

---

## Sources

- [GitHub: MemPalace/mempalace](https://github.com/milla-jovovich/mempalace)
- [Spatial Metaphors for LLM Memory: A Critical Analysis (arXiv 2604.21284)](https://arxiv.org/html/2604.21284)
- [An Unexpected Entry Into AI Memory: Milla Jovovich's Open-Source MemPalace (Substack)](https://alexeyondata.substack.com/p/an-unexpected-entry-into-ai-memory)
- [MemPalace Review: The 100% Score Was Fake. 96.6% Is Real. (danilchenko.dev)](https://www.danilchenko.dev/posts/2026-04-10-mempalace-review-ai-memory-system-milla-jovovich/)
- [MemPalace: Viral AI Memory System — An Honest Look (Medium)](https://medium.com/@creativeaininja/mempalace-the-viral-ai-memory-system-that-got-22k-stars-in-48-hours-an-honest-look-and-setup-26c234b0a27b)
- [MemPalace: What the Benchmarks Actually Mean (Medium)](https://medium.com/@tentenco/mempalace-milla-jovovichs-ai-memory-system-what-the-benchmarks-actually-mean-1a3abe4490d8)
- [What Is MemPalace? (a2a-mcp.org)](https://a2a-mcp.org/blog/what-is-mempalace)
