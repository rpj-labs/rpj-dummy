# Agent Memory Systems: Deep Research Report
**Period Covered: March – April 2026**

This research folder documents the state of memory systems for AI agents — how they work, which frameworks implement them, how teams deploy them in production, and where the field is heading.

---

## Why Memory Matters

Memory is what separates a one-shot chatbot from a genuinely useful agent. Without it, every interaction starts from zero. With it, agents can:

- Recall what a user told them three weeks ago
- Build up a model of a user's preferences over time
- Learn from mistakes without retraining
- Coordinate across multiple agent instances without losing context

By 2026, persistent memory has become the central infrastructure problem for production agents — not model quality, not tool access.

---

## Folder Structure

```
agent-memory-research/
├── README.md                              ← You are here
│
├── 01-fundamentals/
│   ├── memory-taxonomy.md                 ← Types of memory and what each stores
│   ├── architectures.md                   ← Core design patterns for memory systems
│   └── cognitive-science-roots.md        ← Human memory models that inspired AI memory
│
├── 02-frameworks/
│   ├── letta-memgpt.md                    ← Letta / MemGPT: OS-inspired memory
│   ├── mem0.md                            ← Mem0: universal memory layer
│   ├── langgraph-memory.md               ← LangGraph: checkpointing and stores
│   ├── graphiti.md                        ← Graphiti / Neo4j: graph-native memory
│   ├── mempalace.md                       ← MemPalace: spatial/hierarchical memory (April 2026)
│   ├── anthropic-memory-tools.md         ← Anthropic: CLAUDE.md, memory tool API, auto-dream
│   └── frameworks-comparison.md          ← Side-by-side comparison table
│
├── 03-storage-backends/
│   ├── vector-databases.md               ← Pinecone, Chroma, Qdrant, Weaviate, pgvector
│   ├── knowledge-graphs.md              ← Neo4j, graph structures for relational memory
│   ├── key-value-stores.md              ← Redis and fast in-session memory
│   └── hybrid-storage-strategies.md    ← Combining backends in one system
│
├── 04-practical-setups/
│   ├── single-agent-patterns.md         ← Patterns for a single agent with memory
│   ├── multi-agent-patterns.md          ← Shared memory, actor-aware memory
│   ├── production-checklist.md          ← What you actually need before going live
│   └── code-examples.md                 ← Concrete code snippets and configs
│
├── 05-challenges-and-mitigations/
│   ├── hallucination-contradiction.md   ← Memory poisoning and conflict detection
│   ├── temporal-decay.md                ← Stale facts and time-aware forgetting
│   ├── memory-drift.md                  ← Compounding errors across sessions
│   └── security-and-privacy.md         ← GDPR, HIPAA, adversarial memory attacks
│
├── 06-benchmarks-and-evaluation/
│   ├── locomo.md                         ← Long-context multi-session benchmark
│   ├── memorybench.md                   ← Continual learning and feedback benchmark
│   ├── ama-bench.md                     ← Agentic long-horizon memory benchmark
│   └── evaluation-guide.md             ← How to evaluate your own memory system
│
└── 07-emerging-research/
    ├── reinforcement-learning-memory.md ← RL-optimized memory operations
    ├── context-engineering.md          ← ACE, compaction APIs, summarization
    ├── karpathy-llm-wiki.md            ← Karpathy's LLM Knowledge Base pattern (April 2026)
    └── future-directions.md            ← What 2026–2027 looks like
```

---

## Key Takeaways (TL;DR)

1. **Four memory types dominate**: Working (in-context), Episodic (what happened), Semantic (what I know), Procedural (how to act). Most production systems implement all four at some level.
2. **Five major frameworks**: Letta (OS model), Mem0 (universal layer), LangGraph (graph-checkpointed state), MemPalace (spatial/hierarchical, April 2026), Anthropic native tools (CLAUDE.md + memory API).
3. **Storage is a three-way combination**: vector DB for semantic search, knowledge graph for relational facts, key-value store for fast session state.
4. **The hard problems are temporal**: stale facts, contradiction detection, and memory drift are harder than retrieval.
5. **Benchmarks are behind**: most existing benchmarks predate 1M-token context windows and are being replaced.
6. **Two new patterns (April 2026)**: MemPalace's verbatim-first spatial hierarchy and Karpathy's LLM Wiki "compile your knowledge" pattern both challenge extraction-first orthodoxy.

---

## Sources

- [A-Mem: Agentic Memory for LLM Agents (arXiv 2502.12110)](https://arxiv.org/pdf/2502.12110)
- [State of AI Agent Memory 2026 (Mem0)](https://mem0.ai/blog/state-of-ai-agent-memory-2026)
- [Agent Memory: How to Build Agents that Learn and Remember (Letta)](https://www.letta.com/blog/agent-memory)
- [A Practical Guide to Memory for Autonomous LLM Agents (Towards Data Science)](https://towardsdatascience.com/a-practical-guide-to-memory-for-autonomous-llm-agents/)
- [Graph-based Agent Memory: Taxonomy, Techniques, Applications (arXiv 2602.05665)](https://arxiv.org/html/2602.05665v1)
- [ICLR 2026 Workshop: MemAgents](https://openreview.net/pdf?id=U51WxL382H)
- [Memory for Autonomous LLM Agents: Mechanisms, Evaluation, Emerging Frontiers (arXiv 2603.07670)](https://arxiv.org/html/2603.07670v1)
- [Architecture and Orchestration of Memory Systems in AI Agents (Analytics Vidhya)](https://www.analyticsvidhya.com/blog/2026/04/memory-systems-in-ai-agents/)
- [AI Agent Memory: Types, Implementation, Challenges & Best Practices 2026](https://47billion.com/blog/ai-agent-memory-types-implementation-best-practices/)
- [LinkedIn Cognitive Memory Agent (InfoQ)](https://www.infoq.com/news/2026/04/linkedin-cognitive-memory-agent/)
