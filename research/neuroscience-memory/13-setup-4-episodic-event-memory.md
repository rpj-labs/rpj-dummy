# Setup 4: Event-Bounded Episodic Memory (Persistent Agent Memory)

**Inspiration:** LC-NE event boundary detection (Davachi lab, Neuron 2025); SWR experience selection (Buzsáki, Science 2024); theta-phase encoding (Nature Human Behaviour 2024)  
**Neuroscience analog:** Episodic memory system with event segmentation, temporal context, and selective consolidation  
**Complexity:** Medium  
**Best scale:** Long-running persistent agents with continuous interaction streams; chat agents; autonomous agents over days/weeks

---

## Core Principle

The brain does not store experience as a continuous stream — it segments it into **episodes** at event boundaries triggered by surprise and context shifts (LC-NE system). Within an episode, memories share a temporal context and retrieve together. Across episode boundaries, memories are orthogonalized — preventing interference.

For AI agents: treat the interaction stream as a series of distinct episodes, each with its own context, summary, and retrieval key. Never accumulate indefinitely into a single context blob.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                  EVENT-BOUNDED EPISODIC MEMORY                        │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  INTERACTION STREAM                                                    │
│  ─────────────────────────────────────────────────────────────►      │
│  [turn 1] [turn 2] │EVENT│ [turn 1'] [turn 2'] │EVENT│ [turn 1'']   │
│                    │BOUND│                     │BOUND│               │
│                    └──────────────────────────────                    │
│                                                                        │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │  EVENT BOUNDARY DETECTOR (LC-NE analog)                     │      │
│  │                                                              │      │
│  │  Monitors: perplexity, topic cosine shift, time gap,        │      │
│  │            explicit user signal ("new topic", "new task")   │      │
│  │                                                              │      │
│  │  On boundary: flush current episode buffer →                │      │
│  │               write episode to episodic store →             │      │
│  │               reset working context →                       │      │
│  │               initialize new episode                        │      │
│  └────────────────────────────────────────────────────────────┘      │
│                                                                        │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │  EPISODE STORE                                               │      │
│  │                                                              │      │
│  │  Each episode record:                                        │      │
│  │  {                                                           │      │
│  │    id: uuid,                                                │      │
│  │    start_time, end_time,                                    │      │
│  │    turns: [...],              ← verbatim content            │      │
│  │    summary: str,              ← LLM-generated               │      │
│  │    key_entities: [...],       ← extracted                   │      │
│  │    embedding: vector,         ← of summary                  │      │
│  │    salience: float,           ← novelty × value × PE        │      │
│  │    context_id: str,           ← which project/domain        │      │
│  │    prev_episode_id: uuid,     ← temporal chain              │      │
│  │    tags: [...],               ← semantic labels             │      │
│  │    consolidated: bool         ← has it been to slow store?  │      │
│  │  }                                                           │      │
│  └────────────────────────────────────────────────────────────┘      │
│                                                                        │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │  TEMPORAL CONTEXT MODEL (Time cells analog)                  │      │
│  │                                                              │      │
│  │  For each active context_id:                                │      │
│  │    - recency_vector: decaying trace of recent episodes      │      │
│  │    - context_embedding: slowly drifting topic centroid      │      │
│  │    - episode_chain: ordered list of episode IDs             │      │
│  │                                                              │      │
│  │  Used for: "what were we working on?", temporal clustering, │      │
│  │            "how has X evolved over time?"                   │      │
│  └────────────────────────────────────────────────────────────┘      │
│                                                                        │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │  RETRIEVAL ENGINE                                            │      │
│  │                                                              │      │
│  │  Query types:                                                │      │
│  │    Temporal:  "what did we discuss last week?"               │      │
│  │               → filter by time + context_id                 │      │
│  │    Semantic:  "what do I know about SWRs?"                   │      │
│  │               → KNN on episode embeddings                   │      │
│  │    Associative: "what else connects to this topic?"          │      │
│  │               → expand from episode entity graph            │      │
│  │    Narrative:  "how did we arrive at this decision?"         │      │
│  │               → traverse prev_episode_id chain              │      │
│  └────────────────────────────────────────────────────────────┘      │
│                                                                        │
└──────────────────────────────────────────────────────────────────────┘
```

### Event Boundary Detection Logic
```
For each new turn t:
    
    surprise = 1 - cosine_sim(embed(t), current_context_embedding)
    time_gap = now() - last_turn_time
    explicit_boundary = user_said_new_topic(t)
    
    boundary_score = (
        0.5 × normalize(surprise) +
        0.3 × normalize(time_gap) +
        0.2 × explicit_boundary
    )
    
    if boundary_score > THRESHOLD:
        flush_episode()
        reset_context()
        log_boundary(surprise, time_gap, explicit_boundary)
```

### Episode Summarization (at episode close)
```
When episode flushed:
    1. LLM reads all turns in episode buffer
    2. Generates: summary (200-400 words), key_entities list, tags
    3. Computes embedding of summary
    4. Scores salience (novelty vs. existing store + explicit value signals)
    5. Writes complete episode record to episode store
    6. If salience > consolidation_threshold: marks for consolidation
```

---

## User Stories

### US-4.1: Picking Up Where We Left Off
**As a** user returning to a long-running project after 3 days,  
**I want the** agent to immediately recall the context of our last session  
**So that** I don't have to re-explain what we're doing.

**Acceptance criteria:**
- Agent proactively surfaces the last 2–3 episodes in the current context_id at session start
- Summary includes: what we were working on, decisions made, open questions
- Agent does not require user to re-provide context stated in prior session
- Continuity is maintained even if the prior session was weeks ago

### US-4.2: Temporal Navigation
**As a** user who wants to understand how a project evolved,  
**I want to** ask "what has changed since last month?" and get a coherent narrative  
**So that** I can understand the progression without reading all past sessions.

**Acceptance criteria:**
- Agent retrieves episodes in the given time window for the current context_id
- Produces a structured narrative: what was decided, what was discarded, what remained stable
- Shows a "timeline" of key milestones across episodes
- References specific episodes with dates for any key claim

### US-4.3: Cross-Session Insight Discovery
**As a** user who has worked on multiple related projects,  
**I want to** find unexpected connections across different past conversations  
**So that** I benefit from insights I may have forgotten.

**Acceptance criteria:**
- Semantic retrieval surfaces episodes from different context_ids when they share relevant entities
- Agent proactively highlights: "This reminds me of a conversation about X from 3 weeks ago..."
- Connection quality: agent explains *why* episodes are related, not just that they match

### US-4.4: Decision Archaeology
**As a** user who can't remember why a particular decision was made,  
**I want to** ask "why did we decide to do X?" and get the actual reasoning  
**So that** I can evaluate whether the original rationale still applies.

**Acceptance criteria:**
- Agent traverses prev_episode_id chain to find the episode where X was decided
- Surfaces the actual conversation turns where the decision was made
- Provides the context and reasoning present at that time
- Notes if any subsequent episodes contradicted or updated the reasoning

### US-4.5: Episode Salience Review
**As a** developer or power user,  
**I want to** see which episodes the system considered most important  
**So that** I can verify the salience scoring and adjust if needed.

**Acceptance criteria:**
- Developer interface shows top-N episodes sorted by salience score
- For each episode: shows the salience breakdown (novelty, value, PE components)
- Developer can manually adjust salience scores and re-trigger consolidation
- Dashboard shows consolidation status: pending, in-progress, consolidated

### US-4.6: Context Isolation
**As a** user who works on multiple distinct projects with the same agent,  
**I want** episodes from different projects to not bleed into each other  
**So that** project A context doesn't contaminate project B answers.

**Acceptance criteria:**
- Each project has a distinct context_id
- By default, retrieval scopes to the active context_id
- Cross-context retrieval only when explicitly requested ("what did we do in project A that might apply here?")
- Context switch triggers an event boundary (episode close + new episode open in new context)

---

## Requirements

### Functional Requirements

| ID | Requirement |
|----|------------|
| F4.1 | Every turn in every interaction is buffered in the active episode buffer |
| F4.2 | Event boundary detector monitors: topic shift (cosine), time gap, explicit user signal |
| F4.3 | On boundary: flush episode → summarize → embed → score → write → reset |
| F4.4 | Episode records include: id, times, turns, summary, entities, embedding, salience, context_id, prev_id |
| F4.5 | Temporal context model tracks: recency vector, context embedding, episode chain per context_id |
| F4.6 | Retrieval engine supports: temporal filter, semantic KNN, entity expansion, narrative chain traversal |
| F4.7 | Session start: agent loads recent episodes for active context_id and surfaces summary |
| F4.8 | context_id is explicitly set per project/domain; context switch triggers boundary |
| F4.9 | Salience scoring runs at episode close (not turn-by-turn) |
| F4.10 | Episodes tagged as consolidated remain in store but deprioritized for future retrieval |

### Non-Functional Requirements

| ID | Requirement |
|----|------------|
| NF4.1 | Episode write (summarize + embed + store) completes <10 seconds |
| NF4.2 | KNN retrieval over 100K episodes: <500ms |
| NF4.3 | Episode store is persistent with WAL (crash recovery) |
| NF4.4 | Store capacity: at minimum 1M episodes per agent |
| NF4.5 | Episode summaries compressed to <500 tokens; full turns retained for high-salience episodes only |
| NF4.6 | Boundary detection adds <50ms overhead per turn |

---

## User Scenarios

### Scenario A: The Long-Running Software Development Agent

**Setup:** An AI coding assistant used by a solo developer on a complex 6-month project.

**Day 1–10:** Agent handles diverse conversations — architecture discussions, debugging sessions, code reviews. Each session = 2–8 episodes. Boundaries triggered by: topic shifts (debugging → architecture), time gaps (overnight), explicit "new task" signals.

**Day 45 query:** "Why did we switch from Postgres to MongoDB for the events table?"  
- Agent traverses context_id `project-alpha`, finds temporal chain around day 12
- Finds episode where the decision was made (high-salience: large discussion, explicit value signal)
- Surfaces the 3-turn conversation with the reasoning: "We switched because events needed flexible schema — the user mentioned varying event payload structures"

**Day 90 query:** "What are all the architectural decisions we've made on this project?"  
- Agent retrieves all high-salience episodes tagged "architecture-decision" in context_id `project-alpha`
- Returns a structured decision log with dates, reasoning, and current status (still valid / superseded)

**Success signal:** Developer never needs to maintain a separate ADR (Architecture Decision Record) document — the agent produces it on demand from episode store.

### Scenario B: The Therapy / Coaching AI

**Setup:** Mental wellness assistant used by a client 3× per week over 6 months.

**Each session:** 1–4 episodes depending on conversation flow (topic shifts = natural boundaries).

**Session 47 (week 16):** Client returns. Agent surfaces: "In our last session we were discussing your concerns about the promotion timeline. You had decided to schedule a check-in with your manager. How did that go?"

**Month 4 pattern detection:** Salience-weighted retrieval over all episodes finds: anxiety-related episodes cluster around Monday sessions (after weekend). Agent surfaces pattern: "I notice you tend to discuss stress most in our Monday sessions — does that match your experience?"

**Success signal:** Client reports feeling "understood" rather than having to re-explain history. Session quality ratings improve.

### Scenario C: The Enterprise Account Management Agent

**Setup:** AI agent managing 500 customer accounts. Each account = one context_id.

**Per account:** Episode store captures all interactions, support tickets, renewal discussions, sentiment signals.

**Account renewal prep:** "Give me a complete account health summary for ACME Corp."  
- Agent retrieves all episodes for context_id `acme-corp`, last 12 months
- Temporal narrative: initial onboarding, feature adoption milestones, support issues, sentiment trajectory
- Salience-ranked: 3 high-importance episodes (churn risk signal, expansion ask, executive sponsor change)

**Cross-account pattern query (admin):** "Which accounts have similar patterns to accounts that churned last quarter?"  
- Agent performs semantic retrieval across all context_ids
- Finds 8 accounts with high episode-similarity to churned accounts (based on entity + sentiment patterns)

---

## Success Criteria and Capabilities

### What this setup does well

| Capability | Why |
|-----------|-----|
| **Long-term persistence** | Episode store + prev_episode chain = indefinite memory |
| **Temporal reasoning** | Time-filtered retrieval + episode chains support "what happened when" |
| **Narrative continuity** | Sessions feel connected; agent picks up where it left off |
| **Context isolation** | context_id per project prevents contamination |
| **Natural episode boundaries** | Surprise-based boundaries match human memory segmentation |
| **Decision archaeology** | Episode chain traversal = exact historical reasoning |
| **Pattern detection over time** | Aggregate retrieval over temporal windows |

### Limitations

| Limitation | Mitigation |
|-----------|------------|
| **Episode summarization quality** | Bad summaries = bad retrieval; use high-quality LLM for summarization |
| **Boundary detection errors** | False boundaries fragment natural conversations; tune threshold carefully |
| **No semantic compilation** | Episodes are stored, not compiled; use Setup 3 slow store for knowledge distillation |
| **Retrieval degrades at massive scale** (10M+ episodes) | Add Setup 2 graph layer for entity-centric cross-episode retrieval |
| **Privacy** | Verbatim episode storage contains sensitive data; encrypt at rest |

### Capability Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| Knowledge synthesis | ★★★☆☆ | Good at episodic synthesis; not semantic |
| Multi-hop reasoning | ★★★☆☆ | Within episodes; across episodes with chain traversal |
| Real-time learning | ★★★★★ | Every turn captured immediately |
| Episodic memory | ★★★★★ | Core design strength |
| Contradiction handling | ★★★☆☆ | Detects within consolidation; not real-time |
| Portability | ★★★☆☆ | Needs persistent store + embedding model |
| Setup complexity | ★★★☆☆ | Medium; boundary detector needs tuning |
| Scalability | ★★★★☆ | To ~10M episodes before needing graph layer |
| Prioritized retention | ★★★★★ | Salience scoring + selective consolidation |
