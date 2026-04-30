# Synthesis: Karpathy's LLM Wiki + Neuroscience of Memory

**The core insight:** Karpathy's April 2026 LLM Wiki architecture is an independently derived rediscovery of hippocampal indexing theory — built by engineering intuition, validated by neuroscience.

---

## The Karpathy LLM Wiki Architecture

From his gist `llm-wiki.md` (gist.github.com/karpathy/442a6bf555914893e9891c11519de94f):

```
raw/          ← immutable source documents (LLM reads, never writes)
wiki/         ← LLM-generated + LLM-maintained markdown pages
  index.md    ← content catalog, updated on every ingest
  log.md      ← append-only audit trail of all operations
  AGENTS.md   ← schema/conventions co-evolved with the LLM
```

**Three operations:**

| Operation | Trigger | What happens |
|-----------|---------|-------------|
| **Ingest** | New source added | Extract → summarize → create/update concept pages → update index → append log |
| **Query** | User asks question | Read index → fetch relevant pages → synthesize answer with wikilinks → optionally file answer as new page |
| **Lint** | Periodic / manual | Find contradictions, stale claims, orphan pages, missing cross-refs, data gaps |

**His explicit anti-RAG position:** "RAG re-discovers the same information repeatedly; it never accumulates. The LLM wiki *compiles* knowledge — cross-references are pre-built, contradictions already flagged."

**His compiler analogy:** Raw sources = source code. Wiki = compiled executable. You don't query source code; you run the binary.

**His Bush/Memex connection:** Frames this as solving Vannevar Bush's 1945 unsolved problem — who maintains the associative trails as new material arrives? The LLM does.

**Scale he reports:** ~100 articles, ~400,000 words, running without direct human edits.

---

## How Karpathy's Design Maps to Neuroscience

| Karpathy Component | Neuroscience Analog | Paper |
|--------------------|---------------------|-------|
| `raw/` directory | Sensory input / neocortical sensory areas (immutable perceptual traces) | Distributed engram complex |
| `wiki/` pages | Compiled neocortical representations (semantic memory) | CLS slow system |
| `index.md` | Hippocampal index (sparse pointers to distributed content) | Teyler & DiScenna 1986; HippoRAG NeurIPS 2024 |
| `log.md` | Hippocampal time cells / episodic sequence | Eichenbaum; Nature 2024 temporal structure |
| **Ingest operation** | Memory encoding + initial consolidation | CA3 autoassociation + SO→Spindle→Ripple |
| **Query operation** | Pattern completion (CA3) + cortical reinstatement | CA3→CA1→neocortex; HippoRAG PageRank |
| **Lint operation** | Systems reorganization during consolidation | Neuron 2025 "post-standard model" |
| `AGENTS.md` schema | vmPFC contextual schema / memory allocation rules | Nature Neuroscience 2026, Silva lab |
| Cross-page wikilinks | Hippocampal relational binding / knowledge graph edges | HippoRAG; Bakermans Nature Neuroscience 2025 |
| No vector search | Index-first navigation = hippocampal indexing (not brute-force cortical search) | Teyler & DiScenna |

**The one critical thing Karpathy's system lacks** that neuroscience demands: **prioritized selective consolidation**. The biological brain does not compile everything equally — SWRs (Science 2024, Buzsáki) select which experiences get consolidated based on novelty × value × prediction error. His system ingests everything. A neuroscience-informed upgrade would add a salience scorer at ingest time.

---

## The Design Space: Six Setups

These six setups form a spectrum from Karpathy's simple, file-based approach to a full neurobiological stack. Each is genuinely useful at different scales, use cases, and engineering budgets.

```
COMPLEXITY →

Setup 1          Setup 2         Setup 3          Setup 4           Setup 5          Setup 6
LLM Wiki         HippoRAG        CLS Dual-Store   Event-Episodic    Compositional    Full Stack
(Karpathy)       (Graph+PPR)     (Fast/Slow)      (LC-NE+SWR)       (Primitive)      (Hippocampal-
                                                                                      Cortical)

SCALE:
Personal         Team/Domain     Long-running     Persistent        Cross-domain     Enterprise/
research         knowledge       agent            agent             generalization   Foundation
~100K words      ~10M words      continuous       millions of       across tasks     agent OS
                                 interactions     episodes
```

### When to use which:

| Setup | Best for | Avoid when |
|-------|---------|------------|
| 1. LLM Wiki | Personal research, curated domain knowledge | Need real-time updates or >1M tokens |
| 2. HippoRAG | Multi-hop reasoning, large corpora, team knowledge | Source material changes rapidly |
| 3. CLS Dual-Store | Agents that learn from every interaction | Memory need is purely retrieval, not learning |
| 4. Event-Episodic | Long-running persistent agents, chat history | Stateless request/response agents |
| 5. Compositional | Agents that generalize across many domains | Single-domain knowledge only |
| 6. Full Stack | Foundation agent platforms, enterprise memory OS | Prototype / MVP stage |

---

## Cross-Setup Shared Design Principles

These principles appear in all setups to varying degrees, derived from both Karpathy and the neuroscience:

1. **Compile, don't just retrieve** (Karpathy): Pre-synthesize knowledge; accumulate understanding rather than re-discovering it each query.

2. **Separate raw from compiled** (Karpathy + sensory cortex immutability): Raw sources are immutable. Compiled representations can be regenerated.

3. **Index-first navigation** (hippocampal indexing): Agents read a catalog/index to route to the right content, then fetch. Not brute-force similarity search.

4. **Log everything** (hippocampal time cells / episodic sequence): Append-only audit trail enables temporal reasoning and debugging.

5. **Salience-weighted selection** (SWR selection, Science 2024): Not everything deserves equal compilation effort. Novelty × value × prediction error determines depth of processing.

6. **Event boundaries segment episodes** (LC-NE, Neuron 2025): Surprises and context shifts create natural memory boundaries; don't accumulate indefinitely into a single context.

7. **Schema as living artifact** (vmPFC gating, Nature Neuroscience 2026): Explicit, inspectable, co-evolved rules for how memory is organized — not implicit in weights.

8. **Lint/reorganize periodically** (systems reorganization, Neuron 2025): Memory health is a maintenance operation, not a property of the initial write.
