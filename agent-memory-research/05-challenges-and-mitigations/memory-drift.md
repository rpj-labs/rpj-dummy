# Memory Drift in Agent Memory Systems

Memory drift is the phenomenon where stored knowledge gradually deviates from ground truth over time, not because individual facts decay, but because errors compound across retrieval and consolidation cycles.

---

## What Drift Looks Like

Unlike a single hallucination or a single stale fact, drift is a systemic process:

```
Session 1: User says "I'm thinking about switching to Kubernetes."
           Extraction: "User is evaluating Kubernetes"
           
Session 3: Retrieval shows "User is evaluating Kubernetes"
           Agent asks about it, user says "Yeah, we're in the middle of the migration"
           Extraction: "User is migrating to Kubernetes"
           
Session 7: Agent references "User's Kubernetes migration"
           User mentions a cluster issue
           Extraction: "User is running Kubernetes in production"
           (Migration may not actually be done)

Session 15: Any question about infrastructure → agent assumes Kubernetes
            Even if user has since abandoned it or pivoted
```

Each step was individually reasonable. Collectively, the agent has drifted from reality.

---

## Three Failure Points

The SSGM paper identifies three critical points where drift enters the system:

### 1. Memory Poisoning (Input Ingestion)

Bad facts enter during extraction:
- Misattribution (fact assigned to wrong entity)
- Over-generalization (specific → too general)
- Inference presented as fact

### 2. Semantic Drift (Consolidation Updates)

When memories are merged or consolidated, nuance is lost:
- "User is interested in X" + "User tried X" + "User mentioned X" → "User uses X"
- Consolidation LLMs tend to strengthen weak signals

### 3. Conflict/Hallucination (Retrieval)

When contradictory memories coexist, retrieval ambiguity causes:
- The agent picks one arbitrarily
- The agent reconciles them into a synthesized "fact" that wasn't stated
- The agent becomes confused and produces inconsistent responses

---

## Ground-Truth-Preserving Memory (MemMachine)

The MemMachine paper (arXiv 2604.04853, April 2026) proposes a system that minimizes drift by:

1. **Storing raw episodes, not extracted summaries** — the original conversation text is the source of truth
2. **Lazy extraction** — facts are extracted on-demand, not upfront (avoids extraction errors becoming permanent)
3. **Lightweight background models** — use a small local model (Qwen2.5 1.5B) for cheap extraction, avoiding costly LLM calls for every session
4. **Immutable episode log** — the episode store is append-only; derived facts can be deleted and re-extracted, but episodes cannot

```
MemMachine Architecture:

[Immutable Episode Store]  ← raw conversations, never modified
         │
         │ on-demand or background
         ▼
[Extractor] (Qwen2.5 1.5B)
  reads episodes, produces derived facts
         │
         ▼
[Derived Fact Store]  ← can be wiped and rebuilt from episodes
  vector DB: semantic facts
  KV store: structured profile
         │
         ▼
[Retriever]
  queries derived facts for relevant context
```

The key insight: if you discover your extraction is wrong, you can wipe the derived facts and re-extract from the immutable episodes. You never lose the raw data.

---

## Drift Detection

### Semantic consistency checking

Periodically run a consistency check over all stored facts for a user:

```python
async def consistency_check(user_id: str, memory_store, llm) -> list[str]:
    """Returns a list of detected contradictions/drift."""
    all_memories = memory_store.get_all(user_id=user_id)
    
    if len(all_memories) < 2:
        return []
    
    # Cluster memories into groups (by entity/topic)
    # Check each group for internal consistency
    prompt = f"""
Below are {len(all_memories)} stored facts about a user.
Identify any contradictions or facts that seem mutually inconsistent.
List them as "CONFLICT: [fact1] vs [fact2]".

Facts:
{chr(10).join(f"- {m['content']} (stored: {m['created_at'].date()})" for m in all_memories)}

Contradictions found:
"""
    response = await llm.invoke(prompt)
    
    conflicts = [
        line.replace("CONFLICT: ", "")
        for line in response.split("\n")
        if line.startswith("CONFLICT:")
    ]
    return conflicts
```

### Access pattern anomaly detection

If a user's memory store suddenly has many contradictions, it may indicate drift:

```python
def drift_score(memories: list) -> float:
    """Higher = more likely drifted. Run as a health metric."""
    if not memories:
        return 0.0
    
    # Factors that indicate drift:
    # 1. Many memories about same entity with different values
    entity_counts = {}
    for m in memories:
        entity = m.get("entity", "unknown")
        entity_counts[entity] = entity_counts.get(entity, 0) + 1
    
    max_entity_count = max(entity_counts.values()) if entity_counts else 0
    redundancy_score = max_entity_count / len(memories)
    
    # 2. High proportion of agent-inferred vs user-stated
    agent_ratio = sum(1 for m in memories if m.get("source") == "agent_inferred") / len(memories)
    
    return (redundancy_score * 0.5 + agent_ratio * 0.5)
```

---

## ACE: Agentic Context Engineering (March 2026)

The ACE framework addresses drift at the system level with a three-agent loop:

```
[Generator Agent]
  - Produces the main response/trajectory
  - Works with current context
         │
         ▼
[Reflector Agent]
  - Reviews Generator's output
  - Identifies: errors, missing context, assumptions made
  - Does NOT write to memory
         │
         ▼
[Curator Agent]
  - Receives Reflector's analysis
  - Decides what to commit to the "context playbook"
  - Resolves conflicts with existing playbook entries
  - Has final authority over memory writes
```

The Curator's job is specifically to prevent drift by validating before committing. It checks:
- Is this new information or already known?
- Does it contradict anything in the playbook?
- Is this a confident user statement or a weak inference?
- Will this generalize correctly (not over-fit to a specific session)?

---

## Practical Drift Mitigation

In order of implementation complexity:

1. **Store source type** — cheapest protection: always know if a fact is user-stated or inferred
2. **Append-only episodes** — store raw conversation; derived facts are always derivable
3. **Single-entity ownership** — each attribute belongs to one canonical record, not multiple memories
4. **Periodic consolidation sweeps** — scheduled jobs that detect and resolve conflicts
5. **ACE-style curator** — a separate validation LLM reviews every write before it's committed

---

## Sources

- [MemMachine: Ground-Truth-Preserving Memory (arXiv 2604.04853)](https://arxiv.org/html/2604.04853v1)
- [Governing Evolving Memory in LLM Agents: SSGM (arXiv 2603.11768)](https://arxiv.org/html/2603.11768)
- [Memory for Autonomous LLM Agents: Mechanisms, Evaluation, Frontiers (arXiv 2603.07670)](https://arxiv.org/html/2603.07670v1)
- [Memory for AI Agents: A New Paradigm of Context Engineering (The New Stack)](https://thenewstack.io/memory-for-ai-agents-a-new-paradigm-of-context-engineering/)
- [From Storage to Experience: Evolution of LLM Agent Memory Mechanisms](https://www.preprints.org/manuscript/202601.0618/v2/download)
