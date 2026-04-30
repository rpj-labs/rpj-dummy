# Karpathy's LLM Knowledge Base Pattern

**Origin:** Andrej Karpathy, April 3, 2026
**Gist:** https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
**Stars:** 5,000+ within days of posting

---

## What It Is

Karpathy's LLM Knowledge Base (LLM Wiki) is not a framework or a library — it's a **workflow pattern**. The idea: use an LLM agent as a research librarian that builds and maintains a structured markdown wiki from your raw source documents. The wiki becomes a persistent, compounding knowledge base that grows smarter over time.

The pattern became widely discussed after Karpathy posted about it on X in early April 2026 as part of his broader "vibe-coding" philosophy: informal, exploratory AI-assisted workflows that compound value over time.

---

## The Core Insight: Compile Your Knowledge

The central analogy Karpathy uses is from software engineering: **compilation**.

When you write source code, you don't execute the source directly — you compile it into an optimized artifact and run that. The compilation is expensive but pays off across every subsequent execution.

Applied to knowledge:
- **Raw sources** (articles, papers, PDFs, notes) = source code
- **LLM compilation pass** = the compiler
- **The wiki** = the compiled artifact
- **Queries** = runtime execution against the compiled artifact

```
Raw sources                    Wiki (compiled knowledge)
───────────────                ────────────────────────────
article_1.pdf        LLM       kubernetes.md
research_paper.pdf ─────────►  distributed-systems.md
meeting_notes.md   compile     team-conventions.md
slack_export.txt               project-decisions.md
```

You don't re-read all your raw sources every time you have a question. You query the compiled wiki. The LLM maintains the wiki so it stays accurate and cross-referenced.

---

## Three-Layer Architecture

```
raw/
├── articles/           ← immutable curated sources
│   ├── paper1.pdf
│   └── blog_post.md
├── notes/
│   └── meeting_2026-03-15.md
└── transcripts/
    └── interview.txt

wiki/                   ← LLM-generated, LLM-maintained
├── index.md            ← catalog of all wiki pages by category
├── log.md              ← append-only operations log
├── kubernetes.md       ← one page per concept
├── fastapi.md
├── team/
│   ├── alice.md
│   └── decisions.md
└── ...

CLAUDE.md               ← schema, conventions, workflow instructions
```

### raw/ — Immutable Sources

The LLM **reads but never modifies** the raw directory. This is the source of truth. You add files here; the LLM ingests them.

### wiki/ — The Living Wiki

The LLM **owns this layer entirely**. Every page is LLM-generated and LLM-maintained. When you add a new source, the LLM updates 10–15 wiki pages — not just creating a new page, but updating cross-references in existing ones.

Wiki page structure (convention, not enforced):
```markdown
# Kubernetes

## Summary
[2-3 sentence overview]

## Core Concepts
[Key concepts with brief explanations]

## Team Usage
[How our team uses this, decisions made]

## Cross-references
- See also: [[docker]], [[networking]], [[alice]] (who leads K8s migrations)

## Sources
- [Paper: Kubernetes in Production](raw/articles/k8s-paper.pdf)
- [Meeting 2026-03-15](raw/notes/meeting_2026-03-15.md)

## Provenance
Last updated: 2026-04-03 | Sources: 4
```

### CLAUDE.md — The Schema

The CLAUDE.md at the root tells the LLM how to behave as a wiki maintainer:

```markdown
# LLM Wiki: Schema and Conventions

## Directory structure
- raw/: immutable source documents. READ ONLY.
- wiki/: your maintained wiki. You own this entirely.
- wiki/index.md: always update after any page changes.
- wiki/log.md: append an entry for every operation.

## Page conventions
- One concept per page. Split when a page exceeds ~400 lines.
- Every page must have a Sources section citing raw/ files.
- Cross-references use [[PageName]] syntax.
- Dates: always absolute (2026-04-03), never relative.

## Workflow

### Ingest new source
1. Read the source document
2. Identify which existing wiki pages it updates (check index.md)
3. Update or create pages — touch as many as needed
4. Add cross-references bidirectionally
5. Update index.md
6. Append to log.md: "INGEST: <source> → touched <n> pages"

### Lint pass
1. Scan all pages for: contradictions, stale claims, broken [[links]], orphan pages
2. Fix each issue
3. Log: "LINT: found <n> issues, fixed <m>"

### Query
1. Read index.md to find relevant pages
2. Read those pages
3. Answer with citations
4. If the answer reveals new synthesis worth saving, create/update a page
5. Log: "QUERY: <topic> → answered from <n> pages"
```

---

## The Key Operations

### Ingest

When you add a new source:

```
You: @claude Here's a new paper on distributed consensus. [paper.pdf]
     Ingest it into the wiki.

Claude: Reading paper...
        Checking index.md for relevant existing pages...
        Updating: distributed-systems.md (added RAFT section)
        Updating: consistency-models.md (new comparison table)
        Creating: consensus-algorithms.md (new page, 47 lines)
        Updating: index.md (added consensus-algorithms.md)
        Appending to log.md: "INGEST: paper.pdf → touched 3 pages, created 1"
        
        Done. 4 wiki pages updated.
```

### Lint

The periodic health-check pass:

```
You: Run a lint pass on the wiki.

Claude: Scanning 23 pages...
        - kubernetes.md: references [[docker-swarm]] which doesn't exist → fixed
        - fastapi.md: says "current version 0.104" — sources show 0.115 → updated
        - alice.md: cross-references bob.md but bob.md doesn't link back → fixed
        - 3 orphan pages found (no incoming links): archived to wiki/archive/
        
        LINT: 5 issues fixed, 3 pages archived. Wiki health: good.
```

### Query

```
You: What's the team's current thinking on event sourcing?

Claude: Reading index.md... relevant pages: event-sourcing.md, architecture-decisions.md
        
        Based on wiki/architecture-decisions.md (updated 2026-03-20):
        The team evaluated event sourcing for the payments service in Q1 2026.
        Decision: use it for audit log, not for primary state.
        Rationale: complexity not worth it for current scale.
        
        Based on wiki/event-sourcing.md:
        [detailed answer with citations]
        
        Sources: architecture-decisions.md, event-sourcing.md
```

---

## Why It Beats Traditional RAG for This Use Case

RAG chunks your documents and retrieves chunks. The LLM Wiki pattern is fundamentally different:

| | RAG | LLM Wiki |
|-|-----|---------|
| Write path | Chunk → embed → store | LLM reads and rewrites wiki pages |
| Storage | Vector DB (opaque) | Markdown files (human-readable) |
| Update handling | Add new chunks (duplicates accumulate) | LLM updates existing pages |
| Cross-references | None | Explicit, maintained by LLM |
| Contradiction handling | Both chunks exist (agent must reconcile) | LLM resolves during ingest/lint |
| Query cost | Embed query → vector search → retrieve chunks → synthesize | Read index → read pages → answer |
| Human legibility | Low (vector embeddings) | High (markdown) |
| Codebase familiarity | None | CLAUDE.md teaches the LLM the schema |

**Key claim:** Karpathy reports the wiki is "70x more efficient than RAG" — meaning 70x fewer tokens needed per query, because the wiki is pre-synthesized rather than raw chunks. This hasn't been independently benchmarked but the intuition is sound.

---

## LLM Wiki v2: Community Extensions

Rohit Gupta published LLM Wiki v2 (GitHub Gist) extending Karpathy's pattern with lessons from building `agentmemory`:

**Additions:**
- `wiki/people/` subdirectory for entity pages (mirrors MemPalace's People wing concept)
- `wiki/decisions/` for ADR-style decision records with datestamps
- Confidence scores on wiki claims (0–1 float) so the LLM knows what's uncertain
- `wiki/changelog.md` separate from log.md for human-readable history
- Automated lint on every ingest (not just manual runs)

---

## Combining with Claude Code

The pattern pairs naturally with Claude Code's CLAUDE.md and memory system:

```
myproject/
├── CLAUDE.md          ← project instructions (conventional Claude Code)
├── wiki/              ← Karpathy wiki (project knowledge base)
│   ├── index.md
│   ├── log.md
│   └── ...
└── raw/               ← source documents
```

The CLAUDE.md for a Claude Code project can instruct Claude to:
- Always read wiki/index.md at session start
- Update the wiki after any significant architectural decision
- Run a lint pass every 10th session

This way the wiki becomes self-maintaining within Claude Code sessions without any external tooling.

---

## Practical Setup Guide

**Step 1: Initialize the structure**

```bash
mkdir -p my-wiki/{raw,wiki}
touch my-wiki/wiki/index.md my-wiki/wiki/log.md my-wiki/CLAUDE.md
```

**Step 2: Write your CLAUDE.md** (see schema section above)

**Step 3: Add raw sources**

```bash
cp important-paper.pdf my-wiki/raw/
cp meeting-notes.md my-wiki/raw/
```

**Step 4: Trigger ingest**

```
# In Claude Code, inside the my-wiki directory:
claude "Ingest all files in raw/ that aren't yet in log.md"
```

**Step 5: Query**

```
claude "What are the team's conventions for error handling?"
```

**Step 6: Lint (weekly or after major additions)**

```
claude "Run a full lint pass on the wiki"
```

---

## Honest Limitations

1. **Ingest is slow:** The LLM touches 10–15 files per new source. At current API speeds, ingesting a large corpus takes minutes to hours.
2. **No automated triggers:** Unlike Mem0 or Letta, nothing automatically ingests new content. You have to prompt Claude to do it.
3. **No semantic search:** Retrieval is based on the LLM reading index.md and choosing pages — not vector similarity. For very large wikis (hundreds of pages), this may miss relevant content.
4. **LLM judgment determines quality:** The wiki is only as good as the LLM's comprehension during ingest. Poor summaries silently degrade the knowledge base.
5. **Single-user by design:** Like MemPalace, this is designed for a single human's personal knowledge base, not multi-tenant production.

---

## Sources

- [llm-wiki GitHub Gist (Karpathy)](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [Karpathy shares LLM Knowledge Base architecture that bypasses RAG (VentureBeat)](https://venturebeat.com/data/karpathy-shares-llm-knowledge-base-architecture-that-bypasses-rag-with-an)
- [Beyond RAG: How Karpathy's LLM Wiki Pattern Builds Compounding Knowledge (Level Up Coding)](https://levelup.gitconnected.com/beyond-rag-how-andrej-karpathys-llm-wiki-pattern-builds-knowledge-that-actually-compounds-31a08528665e)
- [What Is Andrej Karpathy's LLM Wiki? (MindStudio)](https://www.mindstudio.ai/blog/andrej-karpathy-llm-wiki-knowledge-base-claude-code)
- [Karpathy's LLM Knowledge Bases: The Post-Code AI Workflow (Antigravity Codes)](https://antigravity.codes/blog/karpathy-llm-knowledge-bases)
- [LLM Wiki v2 — extending Karpathy's pattern (GitHub Gist, Rohit Gupta)](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2)
- [Andrej Karpathy's LLM Wiki: Build a Compounding Knowledge Base (Data Science Dojo)](https://datasciencedojo.com/blog/llm-wiki-tutorial/)
- [How I Built a Self-Maintaining Knowledge Base Using Claude Code and Karpathy's LLM Wiki (HackerNoon)](https://hackernoon.com/how-i-built-a-self-maintaining-knowledge-base-for-6-projects-using-claude-code-and-karpathys-llm-wiki)
