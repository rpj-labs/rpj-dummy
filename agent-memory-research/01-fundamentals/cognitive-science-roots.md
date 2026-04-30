# Cognitive Science Roots of Agent Memory

AI agent memory systems didn't emerge from pure engineering — they were deliberately modeled on cognitive science theories of human memory. Understanding the origins clarifies why these systems are designed the way they are.

---

## Endel Tulving's Memory Taxonomy (1972)

The most influential source. Tulving distinguished:

- **Episodic memory**: Personal experiences tied to time and place ("I met Alice last Tuesday at the cafe")
- **Semantic memory**: General world knowledge decoupled from specific events ("Paris is the capital of France")
- **Procedural memory**: Implicit skills and routines ("how to ride a bike")

Every major AI agent memory framework maps directly onto this taxonomy:
- Episodic → past conversation logs, event records
- Semantic → user profiles, distilled facts
- Procedural → agent guidelines, workflow templates

The 2025–2026 literature routinely cites Tulving as the foundational framework.

---

## Working Memory (Baddeley & Hitch, 1974)

Working memory is the "mental workspace" — the limited-capacity system that holds information for active manipulation. Key properties:

- **Capacity-limited**: ~7 ± 2 chunks (for humans); for LLMs, the context window size
- **Temporary**: doesn't persist without rehearsal/encoding
- **Active**: used for reasoning, not just storage

The MemGPT/Letta "core memory" is a direct analog: always in-context, finite capacity, the agent's active workspace.

---

## Atkinson-Shiffrin Multi-Store Model (1968)

Proposed memory as a hierarchy of stores:

```
Sensory Input → Sensory Register → Short-Term Store → Long-Term Store
                      (very brief)    (limited cap.)    (unlimited)
```

This maps almost exactly to:

```
User Input → Context Window → In-Session State → Persistent Stores
              (immediate)       (session-length)   (cross-session)
```

The MemGPT OS-metaphor (RAM → disk) is essentially a computational implementation of this model.

---

## Zettelkasten Method and Associative Memory

The **A-Mem** system (arXiv 2502.12110, 2026) explicitly draws on the **Zettelkasten** method, a note-taking and knowledge management approach developed by sociologist Niklas Luhmann:

- Each note (memory) is atomic and self-contained
- Notes are linked to other notes by explicit connections
- The value comes from the network of connections, not individual notes
- New notes are written to connect to existing ones

Applied to agent memory: each stored memory gets a context note describing it, an index for searchability, and cross-links to related memories. The system dynamically maintains links as new memories arrive.

This is distinct from simple RAG (which stores isolated chunks) because it preserves relational structure.

---

## Cognitive Architecture: CoALA Framework

The **CoALA** (Cognitive Architectures for Language Agents) paper formalized the connection between cognitive science and AI agents. Key contributions:

1. Mapped human memory types to specific computational implementations
2. Defined the action space for memory operations (read, write, update, delete)
3. Categorized memory by storage location: in-context, external (database), in-weights, in-cache

The CoALA taxonomy is now standard vocabulary in the agent memory literature.

---

## The Forgetting Curve (Ebbinghaus, 1885)

Ebbinghaus showed that memory retention decays exponentially over time without reinforcement. This has a direct analog in agent memory:

- Facts retrieved and used frequently should be retained
- Facts never accessed should eventually be deprecated
- Recency and frequency of access should influence retrieval ranking

Production systems implement this via:
- **Temporal decay weights** in retrieval scoring (e.g., `score *= exp(-0.01 * hours_since_access)`)
- **Access frequency boosting** (memories retrieved often rank higher)
- **Soft deletion policies** (memories below a threshold score get archived or removed)

---

## Prospective Memory

A less-discussed but important type: **prospective memory** is memory for future intentions ("I need to do X later"). For agents, this maps to:

- Pending tasks and reminders
- Follow-up commitments made to users
- Scheduled triggers ("remind the user about their meeting tomorrow")

This is typically implemented outside the main memory store — as task queues or calendar integrations rather than vector search.

---

## Key Divergences from Human Memory

AI agent memory is *inspired by* human memory but is not a simulation of it. Important differences:

| Dimension | Human | AI Agent |
|-----------|-------|----------|
| Encoding | Implicit, unconscious | Explicit tool call or pipeline step |
| Forgetting | Natural decay | Deliberate policy decision |
| Capacity | ~7 chunks working + vast LTM | Context window (working) + unlimited DB |
| Consolidation | Sleep-based | Background job / post-session |
| Reliability | Reconstructive, fallible | Can be exact (stored text) or fallible (LLM extraction) |
| Speed | Milliseconds (LTM retrieval) | 10–200ms (vector DB) |

---

## Sources

- [A Survey on Memory Mechanisms of LLM-based Agents (ACM TOIS 2025)](https://dl.acm.org/doi/10.1145/3748302)
- [A-Mem: Agentic Memory for LLM Agents (arXiv 2502.12110)](https://arxiv.org/pdf/2502.12110)
- [Memory in the Age of AI Agents (arXiv 2512.13564)](https://arxiv.org/abs/2512.13564)
- [ICLR 2026 Workshop: MemAgents for LLM-Based Agentic Systems](https://openreview.net/pdf?id=U51WxL382H)
