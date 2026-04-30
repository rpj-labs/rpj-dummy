# Reinforcement Learning for Memory Optimization

The newest frontier in agent memory: instead of handcrafting when to store, retrieve, update, and forget, let the agent learn these policies through reinforcement learning.

---

## The Problem with Manual Memory Policies

Current production memory systems have hand-designed rules:
- "Store after every session" → over-stores, fills up with irrelevant facts
- "Retrieve top-5 by similarity" → misses what actually matters
- "Update if similarity > 0.95" → wrong threshold for different fact types
- "Forget after 30 days" → arbitrary, wrong for long-lived preferences

The optimal memory policy is task-dependent and user-dependent. RL can learn it.

---

## AgeMem: Memory Operations as Tools (March 2026)

**Paper:** Not yet assigned arXiv number at time of writing; described in several survey papers

AgeMem (Agentic Memory) treats the five core memory operations as callable tools within the agent's policy:

| Operation | Tool | When Called |
|-----------|------|-------------|
| Store | `memory_store(content, priority)` | Agent decides what's worth keeping |
| Retrieve | `memory_retrieve(query, limit)` | Agent decides when to consult memory |
| Update | `memory_update(id, new_content)` | Agent decides when facts are stale |
| Summarize | `memory_summarize(ids)` | Agent compresses old memories proactively |
| Discard | `memory_discard(id, reason)` | Agent prunes irrelevant or outdated facts |

The entire pipeline is then **optimized with RL** — the agent receives rewards based on task completion, answer quality, and memory efficiency. The RL algorithm discovers:

- Non-obvious strategies like **preemptive summarization** — compressing memories *before* context fills up, not when it's already overflowing
- Task-specific prioritization — code agents store different things than customer service agents
- User-specific policies — power users need different memory behavior than casual users

### Results on AMA-Bench

AgeMem achieves 72% overall on AMA-Bench vs. 65% for Letta (the previous best), with the largest gains on "Error Memory" (52% vs 41%) — learning to remember and avoid past failures.

---

## MAGMA: Multi-Graph Agentic Memory Architecture

**Paper:** arXiv 2601.03236 (January 2026)

MAGMA separates memory into task-specific subgraphs and uses a learned router to direct information to the right graph:

```
Incoming memory
       │
       ▼
[Router LLM]
  classifies memory type and urgency
       │
  ┌────┼────┬────┐
  ▼    ▼    ▼    ▼
[Task] [User] [World] [Agent]
Graph  Graph  Graph   Graph
  │      │      │       │
  └──────┴──────┴───────┘
             │
         [Merger]
     combines results at retrieval
```

Each subgraph has its own insertion, update, and forgetting policies. The Task graph has aggressive TTLs (current project is irrelevant after completion). The User graph is conservative. The World graph is updated via document ingestion, not conversation.

---

## A-Mem: Zettelkasten-Inspired Agentic Memory (Feb 2026)

**Paper:** arXiv 2502.12110

A-Mem is inspired by the Zettelkasten note-taking method. When storing a new memory, the system:

1. Creates a context note describing the memory
2. Generates an index for fast retrieval
3. **Automatically creates links** to related existing memories
4. Updates older memories to cross-reference the new one

This creates a **network of interconnected memories** where retrieval traverses links rather than doing pure vector search:

```python
# Conceptual A-Mem flow
def store_memory_amem(content: str, existing_memories: list):
    new_memory = {
        "content": content,
        "context_note": llm_generate_context(content),
        "index": llm_generate_index(content),
        "links": []
    }
    
    # Find related memories and create links
    related = find_related(content, existing_memories, threshold=0.7)
    for related_mem in related:
        new_memory["links"].append(related_mem["id"])
        # Update the related memory to link back
        related_mem["links"].append(new_memory["id"])
        update_memory(related_mem)
    
    save_memory(new_memory)

# Retrieval traverses the link network
def retrieve_amem(query: str, hop_limit: int = 2):
    # Start with similarity search
    initial = vector_search(query, limit=3)
    
    # Expand through links
    result_set = set(initial)
    for mem in initial:
        for linked_id in mem.get("links", []):
            if len(result_set) < 10:
                result_set.add(get_memory(linked_id))
    
    return rank_by_relevance(query, list(result_set))
```

---

## Adaptive Memory Admission Control (March 2026)

**Paper:** arXiv 2603.04549

Rather than storing everything and then pruning, this approach decides at admission time whether a memory is worth storing at all:

```
New memory candidate
       │
       ▼
[Admission Controller]
  Estimates: information value, novelty, likely future relevance
  Compares against: current memory store capacity and content
       │
  Decision: STORE / REJECT / MERGE_WITH_EXISTING
```

The admission controller is a small trained model (not a large LLM) that makes fast decisions without incurring large LLM inference costs.

**Key insight:** Most of what gets extracted from conversations is low-value. Admission control reduces storage by ~30–50% while maintaining 95%+ of retrieval quality.

---

## Emerging Patterns (April 2026)

1. **Reward-optimized memory policies** — RL is moving from research to practice; expect production frameworks to adopt it in 2026–2027
2. **Small models for memory operations** — Qwen2.5 1.5B, Llama 3.2 3B, and Gemma 3 2B are fast enough for extraction and admission control
3. **Hierarchical RL for memory** — separate RL policies for short-term and long-term memory with different reward functions
4. **Memory as a differentiator** — companies are starting to treat the quality of their memory system as a competitive advantage

---

## Sources

- [A-Mem: Agentic Memory for LLM Agents (arXiv 2502.12110)](https://arxiv.org/pdf/2502.12110)
- [MAGMA: Multi-Graph based Agentic Memory Architecture (arXiv 2601.03236)](https://arxiv.org/html/2601.03236v1)
- [Adaptive Memory Admission Control for LLM Agents (arXiv 2603.04549)](https://arxiv.org/pdf/2603.04549)
- [Memory for Autonomous LLM Agents: Mechanisms, Evaluation, Frontiers (arXiv 2603.07670)](https://arxiv.org/html/2603.07670v1)
- [ICLR 2026 Workshop: MemAgents](https://openreview.net/pdf?id=U51WxL382H)
