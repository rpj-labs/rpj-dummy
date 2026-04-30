# Setup 3: The CLS Dual-Store (Fast/Slow Continuous Learning)

**Inspiration:** Complementary Learning Systems theory (McClelland, McNaughton & O'Reilly 1995; Nature Communications 2025 update)  
**Neuroscience analog:** Hippocampus (fast episodic cache) ↔ Neocortex (slow semantic store) with interleaved replay  
**Complexity:** Medium-High  
**Best scale:** Agents that learn continuously from interactions; must not catastrophically forget

---

## Core Principle

The biological brain solves the **stability-plasticity dilemma** with two systems that learn at very different rates:

```
FAST SYSTEM (Hippocampus)              SLOW SYSTEM (Neocortex)
────────────────────────               ────────────────────────
One-shot learning                      Gradient-based slow learning
High specificity                       High generalization
Short lifetime (evicts)                Long lifetime (parametric)
Retrieval-augmented (lookup)           Embedded in weights
Verbatim storage                       Abstracted / compressed
Active during encoding                 Updated during consolidation (sleep)
```

The key mechanism: **interleaved replay** — the fast system replays selected episodes to the slow system, which integrates them without forgetting what it already knows.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                      CLS DUAL-STORE AGENT                             │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │  FAST STORE (Hippocampal analog)                             │     │
│  │                                                               │     │
│  │  Write: one-shot, immediate, verbatim                        │     │
│  │  Contents:                                                    │     │
│  │    - Interaction episodes (full text + embeddings)           │     │
│  │    - Recent tool calls and outputs                           │     │
│  │    - User corrections and feedback                           │     │
│  │    - Surprising / high-PE events                             │     │
│  │  Retrieval: KNN on embeddings                                │     │
│  │  Capacity: sliding window (e.g., last 10K interactions)      │     │
│  │  Eviction: LRU weighted by salience score                    │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                    ↕  consolidation pass (async)                       │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │  SLOW STORE (Neocortical analog)                             │     │
│  │                                                               │     │
│  │  Write: batch, interleaved replay, selective                 │     │
│  │  Contents:                                                    │     │
│  │    - Compiled wiki pages (Karpathy-style, see Setup 1)       │     │
│  │    - Knowledge graph (see Setup 2)                           │     │
│  │    - User preference profiles                                │     │
│  │    - Domain schemas and procedures                           │     │
│  │    - Distilled generalizations from fast-store episodes      │     │
│  │  Retrieval: index-first (wiki) + graph traversal             │     │
│  │  Capacity: unbounded (but compression on update)             │     │
│  │  Eviction: explicit deprecation only                         │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │  CONSOLIDATION SCHEDULER (Sleep analog)                      │     │
│  │                                                               │     │
│  │  Trigger: after N interactions OR at low-activity window     │     │
│  │  Steps:                                                       │     │
│  │    1. Score fast-store episodes: novelty × value × PE        │     │
│  │    2. Select top K (10–30%, like biological SWRs)            │     │
│  │    3. For each selected episode:                             │     │
│  │       a. Extract knowledge → update slow store wiki/graph    │     │
│  │       b. Check if generalizable → distill to schema          │     │
│  │       c. Detect contradiction with slow store → flag         │     │
│  │    4. Run lint on slow store section touched                  │     │
│  │    5. Append consolidation log entry                         │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │  RETRIEVAL ROUTER                                             │     │
│  │                                                               │     │
│  │  Query → classify: specific recent vs. general knowledge     │     │
│  │  Recent/specific → fast store (KNN)                          │     │
│  │  General/conceptual → slow store (wiki + graph)              │     │
│  │  Both needed → parallel retrieval + merge                    │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                        │
└──────────────────────────────────────────────────────────────────────┘
```

### Salience Scoring (SWR tagging analog)

Every episode written to the fast store receives a salience score at write time:

```
salience(episode) = w1 × novelty + w2 × value + w3 × pe + w4 × recency

Where:
  novelty  = 1 - max_cosine_similarity(episode, existing_fast_store)
  value    = explicit reward signal (user approval, task completion)
  pe       = prediction error (how much the episode surprised the agent)
  recency  = exponential decay from timestamp
  w1..w4   = tunable weights (default: 0.35, 0.35, 0.15, 0.15)
```

Episodes with salience > threshold are **tagged** for consolidation (awake-SWR analog). Only tagged episodes participate in the consolidation pass.

---

## User Stories

### US-3.1: Learning from User Corrections
**As an** AI agent that makes mistakes,  
**I want to** incorporate user corrections into my behavior permanently  
**So that** I do not repeat the same mistake on future interactions.

**Acceptance criteria:**
- User correction is written immediately to fast store with high salience (value signal)
- Correction is consolidated to slow store within the next consolidation pass
- Agent behavior on similar future queries reflects the correction
- No catastrophic forgetting of unrelated knowledge during this update

### US-3.2: Gradual Domain Specialization
**As an** agent deployed for a specific customer domain,  
**I want to** become progressively more knowledgeable about that domain through interactions  
**So that** my performance improves over weeks without explicit fine-tuning.

**Acceptance criteria:**
- Agent performance on domain-specific questions measurably improves month over month
- Improvements are attributable to specific consolidated episodes (auditable)
- Knowledge of other domains is not degraded (no catastrophic forgetting)
- Performance improvement is not dependent on re-reading the same documents

### US-3.3: Fast Store vs. Slow Store Retrieval Routing
**As a** user who asks both specific recent questions and general knowledge questions,  
**I want to** always get the most relevant answer regardless of whether it's in recent memory or long-term knowledge  
**So that** I don't have to think about which "memory mode" the agent is in.

**Acceptance criteria:**
- "What did we discuss last Tuesday about the pricing model?" → routes to fast store (episodic)
- "What is the standard approach for memory consolidation in ML?" → routes to slow store (semantic)
- "How does our pricing model compare to the standard approach?" → parallel retrieval + merge
- Routing is invisible to the user; response quality is consistent

### US-3.4: Salience-Weighted Forgetting
**As an** agent with limited fast-store capacity,  
**I want to** retain high-value recent memories and gracefully forget low-value ones  
**So that** the fast store remains efficient without losing important information.

**Acceptance criteria:**
- Episodes with low salience score are evicted first when capacity is reached
- High-salience episodes are retained regardless of age, until consolidated to slow store
- Eviction never discards an episode that has been tagged for consolidation but not yet processed
- After consolidation, the original fast-store episode can be safely evicted

### US-3.5: Consolidation Transparency
**As a** developer or power user,  
**I want to** understand what the agent has learned and what it has forgotten  
**So that** I can debug unexpected behavior and audit the agent's knowledge state.

**Acceptance criteria:**
- Consolidation log shows exactly which episodes were consolidated, when, and what was added to slow store
- Developer can inspect current fast-store contents with salience scores
- Developer can inspect slow-store contents (wiki pages, graph)
- "Why did you say X?" can be traced to a specific wiki page or consolidated episode

---

## Requirements

### Functional Requirements

| ID | Requirement |
|----|------------|
| F3.1 | Fast store writes every interaction episode immediately with computed salience score |
| F3.2 | Salience score = f(novelty, value, prediction_error, recency) — all four components computed |
| F3.3 | Consolidation scheduler triggers after N interactions (configurable) or at low-activity window |
| F3.4 | Consolidation selects episodes with salience > threshold (default: top 20%) |
| F3.5 | Selected episodes are extracted to slow store: wiki page updates + knowledge graph updates |
| F3.6 | Consolidation detects contradictions between episode content and slow store |
| F3.7 | Retrieval router classifies queries as episodic/recent vs. semantic/general |
| F3.8 | Fast store capacity is bounded; eviction is LRU weighted by salience |
| F3.9 | Eviction never removes tagged-but-not-yet-consolidated episodes |
| F3.10 | All consolidation events are logged in append-only consolidation-log.md |
| F3.11 | Slow store is a combination of wiki (Setup 1) and/or knowledge graph (Setup 2) |

### Non-Functional Requirements

| ID | Requirement |
|----|------------|
| NF3.1 | Fast-store write latency: <100ms (must not slow down agent response) |
| NF3.2 | Consolidation pass processes 100 episodes in <60 seconds |
| NF3.3 | Fast store holds at least 10,000 episodes before eviction pressure begins |
| NF3.4 | Retrieval routing decision: <50ms |
| NF3.5 | Slow store is persistent across agent restarts |
| NF3.6 | Fast store is recoverable after crash (write-ahead log) |

---

## User Scenarios

### Scenario A: The Persistent Research Assistant

**Setup:** An AI research assistant used daily by a scientist over 12 months.

**Month 1:** Agent has no domain knowledge. Every query is slow; user must provide context. Fast store fills with their conversations. 40% of conversations are high-salience (new concepts, corrections, surprising results).

**After weekly consolidation passes (month 2):** Slow store has 80 wiki pages on the scientist's specific research domain. Agent stops asking basic definitional questions. User correction rate drops by 60%.

**Month 6:** User asks "how has my thinking about the hippocampal indexing hypothesis evolved since we started?" Agent traverses consolidation log, finds 12 key conversations tagged as high-salience on this topic, synthesizes an evolution narrative with dated milestones.

**Month 12:** Agent's domain-specific performance is dramatically higher than a fresh agent. An uninstructed visitor using the same agent in the same domain gets domain-specialist-level answers without any onboarding.

**Success signal:** The agent's effective "expertise" in the domain is measurably greater after 12 months vs. month 1, purely from interaction learning.

### Scenario B: The Customer Support Agent with Institutional Memory

**Setup:** Customer support agent for a SaaS product, handling 500 conversations/day.

**Fast store:** Every conversation stored. High-salience: customer corrections ("That's wrong, the new pricing is..."), novel bugs reported, edge cases that broke the agent.

**Consolidation (nightly):** Top 20% of conversations consolidated to slow store. Product FAQ pages updated with newly discovered answers. Known-bugs graph updated with new issue nodes.

**Two weeks in:** New agent instances (cold starts) begin their sessions by loading the current slow store. They immediately have institutional knowledge from 14,000 conversations without reading any of them.

**Contradiction detected:** Customer A says feature X was deprecated in v2.3; the slow store says it still exists. Contradiction flagged → human review → FAQ updated.

**Success signal:** Customer satisfaction (CSAT) improves by >15% over 30 days as agent stops giving stale/incorrect answers. Knowledge latency (time from issue reported to agent knowing about it) drops from weeks to hours.

### Scenario C: The Personal AI with Longitudinal Memory

**Setup:** A personal AI assistant used for tasks, learning, journaling, and planning over years.

**Fast store:** Captures what the user said, what they worked on, what they expressed preferences about. High salience: expressed frustration (negative value), explicit instructions ("always do X"), surprising events.

**Slow store:** Compiled user profile (preferences, working style, domain knowledge, life context), project wikis, personal knowledge domains.

**User query (month 18):** "What are my strongest areas of expertise based on our conversations?"  
Agent traverses slow store: finds 12 domain-knowledge wiki pages with dense content, identifies 3 as most developed, surfaces a ranked capability summary.

**User query:** "I need to hire someone with complementary skills — what am I missing?"  
Agent uses slow store knowledge of user's capabilities + fast store of recent project work → identifies gaps → suggests hiring profile.

---

## Success Criteria and Capabilities

### What this setup does well

| Capability | Why |
|-----------|-----|
| **Continuous learning** | CLS interleaved replay prevents catastrophic forgetting while enabling accumulation |
| **One-shot retention** | Fast store immediately captures any new fact/correction/preference |
| **Long-term specialization** | Slow store grows progressively richer through consolidation |
| **Auditable learning** | Consolidation log traces every slow-store update to source episodes |
| **Adaptive forgetting** | Low-salience episodes evicted; high-value knowledge retained |
| **Personalization** | User-specific preferences and corrections accumulate in slow store |

### Limitations

| Limitation | Mitigation |
|-----------|------------|
| **Consolidation latency** | Knowledge isn't in slow store until next consolidation pass; use fast store for recent queries |
| **Salience scoring quality** | Mis-scored episodes may be over/under-retained; tune weights domain-specifically |
| **Consolidation LLM cost** | Run during low-activity windows; batch efficiently |
| **Slow store accuracy** | Hallucinated consolidation content poisons slow store; requires lint validation |
| **Privacy** | Fast store contains verbatim conversations; encrypt and access-control carefully |

### Capability Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| Knowledge synthesis | ★★★★☆ | Strong via slow store |
| Multi-hop reasoning | ★★★★☆ | If slow store is graph-based |
| Real-time learning | ★★★★★ | Fast store = immediate capture |
| Episodic memory | ★★★★☆ | Fast store for recent; less for old |
| Contradiction handling | ★★★★☆ | Detected at consolidation time |
| Portability | ★★★☆☆ | Two-store architecture has dependencies |
| Setup complexity | ★★★☆☆ | Moderate; needs scheduler |
| Scalability | ★★★★☆ | Fast store bounded; slow store unbounded |
| Prioritized retention | ★★★★★ | Salience scoring is core to the design |
