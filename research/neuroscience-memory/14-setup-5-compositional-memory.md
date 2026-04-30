# Setup 5: Compositional Memory (Primitive-Binding System)

**Inspiration:** Bakermans, Warren, Whittington, Behrens — *"Constructing future behavior through composition and replay"* (Nature Neuroscience 28:1061, 2025); Clone-Structured Causal Graph (CSCG) model (Nature 2025, Janelia)  
**Neuroscience analog:** Hippocampal replay binding known primitives into novel compositions; orthogonalized state machine  
**Complexity:** High  
**Best scale:** Agents that must generalize across many domains; zero-shot task transfer; multi-domain knowledge base

---

## Core Principle

The hippocampus does not store entire novel experiences from scratch. Instead, it **binds known primitives** (elementary behavioral/spatial/conceptual motifs) into new compositions. This allows:

1. Immediate competence in novel environments by composing familiar primitives in new configurations
2. No gradient learning required for the composition itself — only for learning new primitives
3. Memory organized as a **latent state machine** (CSCG) where the same sensory cue maps to different hidden states depending on which context/composition is active

For AI agents: store **reusable knowledge primitives** explicitly. New tasks and domains are handled by composing primitives in new configurations, not by writing new memories from scratch.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    COMPOSITIONAL MEMORY SYSTEM                        │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  PRIMITIVE LIBRARY (Cortical building blocks analog)                   │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │  Primitives = reusable, named, parameterized knowledge units │     │
│  │                                                               │     │
│  │  Types:                                                       │     │
│  │    Procedural: "authenticate_with_oauth(provider, scope)"    │     │
│  │    Factual:    "rate_limiting_pattern(service, max_rps)"      │     │
│  │    Relational: "entity_A owns_many entity_B via join_table"  │     │
│  │    Heuristic:  "when perf_regression, first_check(N-query)"  │     │
│  │                                                               │     │
│  │  Each primitive:                                              │     │
│  │  {                                                            │     │
│  │    id: str,          name: str,                              │     │
│  │    type: enum,       content: str,                           │     │
│  │    parameters: [...],                                        │     │
│  │    embedding: vector,                                         │     │
│  │    usage_count: int, success_rate: float,                    │     │
│  │    domains: [...],   source_episodes: [...]                  │     │
│  │  }                                                            │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                    ↕ compose / decompose                               │
│                                                                        │
│  COMPOSITION ENGINE (Hippocampal binding analog)                       │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │  Given new task: find relevant primitives + compose them     │     │
│  │                                                               │     │
│  │  Composition record:                                          │     │
│  │  {                                                            │     │
│  │    task_id,                                                   │     │
│  │    primitives_used: [...],    ← which primitives             │     │
│  │    binding: {...},            ← how parameters are bound     │     │
│  │    ordering: [...],           ← sequence/dependency          │     │
│  │    outcome: str,              ← what happened                │     │
│  │    success: bool                                              │     │
│  │  }                                                            │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                    ↕ extraction                                         │
│                                                                        │
│  LATENT STATE TRACKER (CSCG / orthogonalized state machine analog)    │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │  Tracks current "hidden state" = which composition context  │     │
│  │  is active                                                    │     │
│  │                                                               │     │
│  │  Same observation → different primitives activated           │     │
│  │  depending on which state we're in                           │     │
│  │                                                               │     │
│  │  Example:                                                     │     │
│  │    Observation: "API returns 429"                             │     │
│  │    State A (rate_limit_context): → retry_with_backoff         │     │
│  │    State B (quota_exceeded_context): → request_quota_increase │     │
│  │    State C (auth_error_context): → refresh_token              │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                    ↕ background                                         │
│                                                                        │
│  PRIMITIVE DISTILLATION (Replay → new primitive extraction analog)    │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │  From high-salience episodes:                                │     │
│  │    - Identify reusable patterns (appeared in 2+ contexts)    │     │
│  │    - Parameterize them (generalize from specific to general) │     │
│  │    - Add to primitive library with source_episodes noted     │     │
│  │    - Tag with domain labels + usage statistics               │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                        │
└──────────────────────────────────────────────────────────────────────┘
```

### Task Execution Flow
```
New task arrives
    ↓
1. Parse task into sub-goals and context signals
    ↓
2. Latent state tracker: identify which composition context we're in
    ↓
3. Retrieve relevant primitives (KNN on task embedding)
    ↓
4. Composition engine: bind primitives to task parameters
    ↓
5. Execute composition
    ↓
6. Observe outcome → update primitive success_rate
    ↓
7. If novel elements: write episode for potential primitive extraction
```

### Primitive Distillation Flow (background)
```
High-salience episodes (from Setup 3 or 4)
    ↓
LLM reviews episode set for recurring patterns:
    "This pattern of [A then B given condition C] appeared 3 times"
    ↓
Parameterize: A(param1, param2) → B given condition(param3)
    ↓
Check: does this generalize across 2+ domains? If yes → primitive
    ↓
Add to library with: name, content, parameters, source episodes, domains
```

---

## User Stories

### US-5.1: Zero-Shot Domain Transfer
**As an** AI agent trained primarily on software engineering tasks,  
**I want to** apply engineering reasoning primitives to a new domain (e.g., legal analysis)  
**So that** I can immediately be productive in the new domain without domain-specific training.

**Acceptance criteria:**
- Agent identifies applicable primitives from its library ("systematic decomposition", "edge case analysis", "version/precedent lookup")
- Composes them into a legal analysis workflow in <30 seconds
- Performance on the new domain task is meaningfully above baseline (unstructured LLM with no primitives)
- Agent explicitly notes which primitives it applied and from what original domain

### US-5.2: Primitive Discovery from Experience
**As an** agent that has executed 1,000 diverse tasks,  
**I want** the system to automatically identify and name recurring patterns in my past work  
**So that** I build a library of reusable patterns without manual curation.

**Acceptance criteria:**
- Distillation pass identifies patterns that appeared in 3+ distinct task contexts
- Each discovered primitive is correctly parameterized (generalizes beyond the specific instances)
- Discovered primitives are human-readable and auditable
- Primitive library grows over time without manual intervention

### US-5.3: Composition for Novel Tasks
**As a** user who presents the agent with a genuinely novel task type,  
**I want the** agent to construct a plan by composing its known primitives  
**So that** it can handle tasks it has never seen before.

**Acceptance criteria:**
- Agent explicitly identifies which primitives are being composed and in what order
- Composition plan is shown to user before execution (transparency)
- Success rate on novel task types is higher than without compositional memory
- When composition fails, agent identifies which primitive failed and why

### US-5.4: State-Dependent Primitive Selection
**As a** user in a complex multi-step workflow,  
**I want the** agent to correctly identify which context it's in  
**So that** the same surface-level cue ("error 429") is handled correctly in different situations.

**Acceptance criteria:**
- Agent maintains a latent state (current composition context)
- Same surface observation triggers different primitive in different states
- State transitions are logged (for debugging)
- Agent can explain its current state: "I'm in a rate-limiting context, so I'm applying backoff rather than token refresh"

### US-5.5: Primitive Portfolio Inspection
**As a** developer who wants to understand what an agent "knows how to do",  
**I want to** browse the primitive library  
**So that** I understand the agent's repertoire and identify gaps.

**Acceptance criteria:**
- Primitive library is browsable and searchable by domain, type, usage frequency
- Each primitive shows: definition, parameters, usage count, success rate, source episodes
- Developer can manually add, edit, deprecate, or delete primitives
- Usage frequency and success rate are updated automatically

### US-5.6: Cross-Agent Primitive Sharing
**As an** organization running multiple AI agents on related tasks,  
**I want** primitives discovered by agent A to be available to agent B  
**So that** agents benefit from each other's experience.

**Acceptance criteria:**
- Primitive library can be exported in a portable format (JSON/markdown)
- Importing a primitive library merges with the agent's existing library (deduplication)
- Cross-agent usage statistics tracked separately (so agent A's success rate doesn't pollute agent B's)

---

## Requirements

### Functional Requirements

| ID | Requirement |
|----|------------|
| F5.1 | Primitive library stores: id, name, type, content, parameters, embedding, usage_count, success_rate, domains, source_episodes |
| F5.2 | Primitive types: Procedural, Factual, Relational, Heuristic, Compositional (composed of other primitives) |
| F5.3 | Composition engine takes task + relevant primitives → produces composition plan |
| F5.4 | Composition plan records: task_id, primitives_used, binding, ordering, outcome, success |
| F5.5 | Latent state tracker maintains current composition context; disambiguates same-surface-cue responses |
| F5.6 | Primitive distillation: background process identifying patterns in high-salience episodes |
| F5.7 | Distillation criterion: pattern appeared in 2+ distinct domain contexts |
| F5.8 | Primitives are parameterized (generalized), not specific to source instances |
| F5.9 | Primitive library is searchable by embedding KNN and by metadata filters |
| F5.10 | Primitive usage and success_rate updated after every task execution |
| F5.11 | Primitives are exportable/importable in JSON + markdown format |

### Non-Functional Requirements

| ID | Requirement |
|----|------------|
| NF5.1 | Primitive library scales to 100K primitives without retrieval degradation |
| NF5.2 | Composition plan generation: <3 seconds for up to 10-primitive compositions |
| NF5.3 | Distillation pass processes 1000 episodes in <5 minutes |
| NF5.4 | All primitives are human-readable (no opaque embeddings as primary representation) |
| NF5.5 | Primitive library portable across LLM backends (not tied to one model's latent space) |

---

## User Scenarios

### Scenario A: The Multi-Domain Technical Agent

**Library at month 6 (500 tasks executed across 8 domains):**
Primitive library has 340 entries across: software architecture (89), data engineering (67), debugging (54), API integration (44), security (38), testing (32), DevOps (28), documentation (18).

**Novel task:** "Analyze the security posture of this new IoT firmware."  
Agent has no IoT-specific primitives but has:
- Security primitives: `threat_modeling`, `attack_surface_analysis`, `credential_audit`
- Debugging primitives: `systematic_decomposition`, `boundary_condition_check`
- From firmware context: `embedded_constraint_analysis`

Composition: `systematic_decomposition(IoT_firmware)` → `threat_modeling(embedded_system)` → `attack_surface_analysis(network_interfaces + firmware_update_mechanism)` → `credential_audit(hardcoded_credentials, cert_pinning)`

**Result:** Agent produces a structured IoT security review that would normally require a specialist — from zero IoT-specific training, using composed general primitives.

**Success signal:** Security review quality rated "good" by a domain expert despite agent having no IoT training.

### Scenario B: The Code Review Agent Growing Across a Codebase

**Setup:** Agent reviews PRs across a 500K-line codebase over 6 months.

**Primitive discovery (month 3):** Distillation finds that 3 separate high-salience code review episodes all involved the same pattern: "N+1 query in ORM-heavy code → recommend eager loading + add DB query count assertion." This becomes a named primitive: `detect_n_plus_one_query(orm_framework)`.

**Month 6 review:** Agent encounters the pattern in a new service using a different ORM framework. Latent state tracker identifies context: "ORM-heavy service, no query optimization." `detect_n_plus_one_query` primitive activates with new parameter binding.

**Cross-agent export:** This agent's primitive library exported and imported to the new code review agent for a different product. New agent immediately has the N+1 detection capability from day 1.

**Success signal:** Review quality on month-1 PRs for the imported-library agent is equivalent to the source agent's month-4 quality.

### Scenario C: The Scientific Discovery Agent

**Setup:** Research agent exploring a scientific domain over 18 months.

**Primitive library includes:** `hypothesis_formulation`, `experimental_design`, `statistical_significance_check`, `confound_identification`, `replication_criterion_check`, `effect_size_estimation`.

**Novel domain entry:** Agent is asked to evaluate a new field (computational archaeology). Has no archaeology primitives. Composes: `literature_synthesis` → `confound_identification(archaeological_context)` → `replication_criterion_check(field_data)` → `effect_size_estimation(archaeological_sample_size)`.

**State-dependent activation:** When in `peer_review_mode` state, `replication_criterion_check` is weighted highest. When in `grant_proposal_mode`, `hypothesis_formulation` is weighted highest. Same domain knowledge, different primitive ordering based on latent state.

---

## Success Criteria and Capabilities

### What this setup does well

| Capability | Why |
|-----------|-----|
| **Zero-shot domain transfer** | Primitives are explicitly domain-tagged; composition is cross-domain |
| **Interpretable reasoning** | Composition plan shows exactly which primitives were applied |
| **Growing competence** | Primitive library grows from experience; more tasks = richer library |
| **State-dependent behavior** | Latent state tracker enables context-appropriate responses to ambiguous cues |
| **Portable expertise** | Primitive libraries can be shared across agents and teams |
| **Automatic skill discovery** | Distillation extracts primitives without manual curation |

### Limitations

| Limitation | Mitigation |
|-----------|------------|
| **Cold start** | Library is empty initially; requires substantial interaction history to become useful |
| **Distillation quality** | LLM may over-generalize or mis-parameterize primitives; requires validation |
| **Primitive granularity** | Too coarse: no useful decomposition; too fine: combinatorial explosion |
| **No episodic memory** | Pair with Setup 3 or 4 for episodic layer |
| **Latent state complexity** | State space can grow unboundedly; needs pruning |

### Capability Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| Knowledge synthesis | ★★★★☆ | Strong via primitive composition |
| Multi-hop reasoning | ★★★★☆ | Primitive chains = multi-hop |
| Real-time learning | ★★★☆☆ | Distillation is background, not immediate |
| Episodic memory | ★★☆☆☆ | Not designed for it |
| Contradiction handling | ★★★☆☆ | At primitive level; not episodic |
| Portability | ★★★★☆ | Primitive library is portable markdown/JSON |
| Setup complexity | ★★★★☆ | High; requires distillation pipeline |
| Scalability | ★★★★☆ | Scales to 100K+ primitives |
| Prioritized retention | ★★★★☆ | Success-rate-weighted; low-success primitives deprecated |
