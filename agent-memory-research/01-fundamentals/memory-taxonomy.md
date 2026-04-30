# Memory Taxonomy for AI Agents

The field has converged on four core memory types, drawn from cognitive science and adapted for LLM-based systems. Most production agents implement a subset; sophisticated ones implement all four.

---

## The Four Types

### 1. Working Memory (Short-Term / In-Context)

**What it is:** The LLM's active context window — everything currently "in mind."

**What it stores:**
- The current conversation turn
- Tool call results from the current session
- Intermediate reasoning steps
- Temporary scratch-pad state

**Properties:**
- Extremely fast (zero retrieval latency — already in the prompt)
- Strictly bounded by context window size
- Ephemeral: evaporates when the session ends

**2026 status:** Context windows have grown dramatically (1M+ tokens in frontier models), but cost-per-token means most production systems still manage working memory carefully rather than just dumping everything in.

**Implementation:** No special tooling needed — it's just the prompt. The engineering question is *what to put in it*.

---

### 2. Episodic Memory (What Happened)

**What it is:** A record of specific past interactions, events, and experiences — indexed by time and context.

**What it stores:**
- Past conversation summaries
- Specific things a user said in previous sessions
- Outcomes of past tool calls
- Timestamped event sequences

**Properties (required for a real episodic store):**
1. **Long-term storage** — persists beyond the current session
2. **Explicit reasoning** — the agent can reflect on memory content
3. **Single-shot learning** — captures facts from single exposure
4. **Instance-specific** — details unique to this occurrence
5. **Contextual** — who, when, where, why bound to content

**2026 status:** Almost universally implemented via vector search over conversation summaries. The `MemGPT/Letta` "recall memory" and `Mem0`'s episode store are canonical examples.

**Implementation patterns:**
- Store: summarize session → embed → write to vector DB
- Retrieve: embed query → ANN search → inject top-k into context

---

### 3. Semantic Memory (What I Know)

**What it is:** Factual, general knowledge — not tied to a specific event but extracted and distilled from many interactions.

**What it stores:**
- User preferences ("prefers concise answers")
- Entity facts ("their company uses Python, not Java")
- Domain knowledge accumulated across sessions
- User profile attributes

**Properties:**
- Timeless in character (unlike episodic, not event-anchored)
- Subject to updating and contradiction
- Requires consolidation from episodic memories

**2026 status:** Often the hardest type to implement correctly. Extraction from episodes requires an LLM pass; updates must handle contradictions; stale facts accumulate. Most frameworks delegate extraction to a background LLM worker.

**Implementation patterns:**
- Background job runs after session end
- Smaller model (e.g., Qwen2.5 1.5B) does extraction to save cost
- Facts stored as structured records + embeddings in vector DB
- Contradiction resolution: prefer newer + user-stated over older + agent-inferred

---

### 4. Procedural Memory (How to Act)

**What it is:** Knowledge about *how to do things* — skills, workflows, learned strategies.

**What it stores:**
- Custom instructions for the agent's own behavior
- Learned task templates and playbooks
- Error-correction patterns from past mistakes
- Workflow shortcuts discovered through experience

**Properties:**
- Most similar to "fine-tuning" but without gradient updates
- Changes agent behavior rather than agent knowledge
- Highest-impact for task performance

**2026 status:** Implemented via "system prompt injection" (inserting learned instructions into the system prompt) or "tool library" (agent adds custom tools over time). The `ACON` framework (Agentic Context Engineering) formalizes this as a "context playbook."

**Implementation patterns:**
- Store guidelines as key-value records in a fast store
- Inject top-k relevant guidelines into system prompt based on task type
- Update via a "Reflector → Curator" pipeline after task completion

---

## Memory Interaction Model

```
User Input
    │
    ▼
[Working Memory] ← Retrieval from all long-term stores
    │
    ├─── Episodic retrieval: "What did they say about X last week?"
    ├─── Semantic retrieval: "What do I know about this user?"
    └─── Procedural retrieval: "How should I handle this type of request?"
    │
    ▼
Agent Response
    │
    ▼
[Post-session consolidation]
    ├─── Episodic store: log what happened
    ├─── Semantic store: extract/update facts
    └─── Procedural store: extract/update guidelines
```

---

## The Parametric Memory Type (Honorable Mention)

Some taxonomies add a fifth type: **parametric memory** — knowledge baked into model weights through training/fine-tuning. This is the model's pre-existing knowledge, and it cannot be directly written to at inference time. Most agent memory systems operate on top of parametric memory (they don't replace it). Fine-tuning on domain data can be considered "writing to parametric memory" but requires full retraining cycles.

---

## Quick Reference

| Type        | Stored Where     | Latency    | Persistence | Updateable |
|-------------|-----------------|------------|-------------|------------|
| Working     | Context window  | ~0ms       | Session     | Yes (implicit) |
| Episodic    | Vector DB       | 10–200ms   | Permanent   | Append-only |
| Semantic    | Vector DB + KV  | 10–200ms   | Permanent   | Yes |
| Procedural  | KV + System Prompt | 1–50ms  | Permanent   | Yes |
| Parametric  | Model weights   | ~0ms       | Permanent   | Training only |

---

## Sources

- [Episodic Memory for AI Agents: How It Works (Atlan)](https://atlan.com/know/episodic-memory-ai-agents/)
- [A Survey on Memory Mechanisms of LLM-based Agents (ACM TOIS)](https://dl.acm.org/doi/10.1145/3748302)
- [Memory in the Age of AI Agents (arXiv 2512.13564)](https://arxiv.org/abs/2512.13564)
- [AI Agent Memory: Types, Implementation, Best Practices 2026](https://47billion.com/blog/ai-agent-memory-types-implementation-best-practices/)
- [A Practical Guide to Memory for Autonomous LLM Agents (TDS)](https://towardsdatascience.com/a-practical-guide-to-memory-for-autonomous-llm-agents/)
