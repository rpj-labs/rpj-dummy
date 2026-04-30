# Setup 6: Full Neurobiological Stack (Hippocampal-Cortical Memory OS)

**Inspiration:** The complete mammalian memory system — all five setups integrated  
**Neuroscience analog:** Working memory (theta-gamma) + Episodic store + Hippocampal index + Semantic store + Consolidation hierarchy + Primitive library  
**Complexity:** Very High  
**Best scale:** Foundation agent platforms, enterprise memory OS, persistent AI companions, research infrastructure

---

## Core Principle

Each of Setups 1–5 solves one layer of the memory problem. The full neurobiological stack **integrates all layers** with a consistent data model and a consolidation pipeline that moves information from fast → indexed → semantic → compositional over time, mirroring the hippocampal-neocortical consolidation cascade (SO → Spindle → Ripple → cAMP hierarchy, Neuron 2025).

No layer is optional in this setup — each serves a function the others cannot.

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                    FULL NEUROBIOLOGICAL MEMORY STACK                            │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  LAYER 0: WORKING MEMORY  (theta-gamma multiplex analog)                        │
│  ┌──────────────────────────────────────────────────────────────────────┐      │
│  │  In-context window: current conversation turns + retrieved context   │      │
│  │  Capacity: N tokens (LLM context window)                              │      │
│  │  Lifetime: current session only                                       │      │
│  │  Structure: slot-based (active task, background context, retrieved)   │      │
│  └──────────────────────────────────────────────────────────────────────┘      │
│                    ↕ event boundary detector                                     │
│                                                                                  │
│  LAYER 1: EPISODIC STORE  (hippocampal fast-store analog)     [Setup 4]         │
│  ┌──────────────────────────────────────────────────────────────────────┐      │
│  │  Episode records: {id, turns, summary, entities, embedding,           │      │
│  │                    salience, context_id, prev_id, consolidated}       │      │
│  │  Lifetime: indefinite (evict only low-salience + consolidated)        │      │
│  │  Write: on episode boundary (LC-NE analog)                            │      │
│  │  Read: KNN + temporal filter + entity chain                           │      │
│  └──────────────────────────────────────────────────────────────────────┘      │
│                    ↕ consolidation pipeline (priority-weighted)                  │
│                                                                                  │
│  LAYER 2: KNOWLEDGE GRAPH  (hippocampal index + EC analog)    [Setup 2]         │
│  ┌──────────────────────────────────────────────────────────────────────┐      │
│  │  Typed nodes: Entity, Concept, Event, Claim                           │      │
│  │  Typed edges: causes, part-of, contradicts, analogous-to, follows    │      │
│  │  Each node → source episode IDs (the index)                          │      │
│  │  Retrieval: seed KNN → Personalized PageRank                          │      │
│  └──────────────────────────────────────────────────────────────────────┘      │
│                    ↕ schema extraction                                           │
│                                                                                  │
│  LAYER 3: COMPILED WIKI  (neocortical semantic store analog)  [Setup 1]         │
│  ┌──────────────────────────────────────────────────────────────────────┐      │
│  │  Markdown wiki pages: concept, entity, topic, decision pages          │      │
│  │  index.md: content catalog                                             │      │
│  │  log.md: append-only audit trail                                      │      │
│  │  Retrieval: index-first → page fetch → synthesis                      │      │
│  │  Maintenance: lint operation (contradictions, orphans, gaps)           │      │
│  └──────────────────────────────────────────────────────────────────────┘      │
│                    ↕ distillation                                                │
│                                                                                  │
│  LAYER 4: PRIMITIVE LIBRARY  (compositional cortex analog)    [Setup 5]         │
│  ┌──────────────────────────────────────────────────────────────────────┐      │
│  │  Typed primitives: Procedural, Factual, Relational, Heuristic         │      │
│  │  Each: {name, content, params, embedding, domains, success_rate}      │      │
│  │  Distilled from: high-salience, cross-context episodes                │      │
│  │  Retrieval: KNN + domain filter + latent state context                │      │
│  └──────────────────────────────────────────────────────────────────────┘      │
│                                                                                  │
│  CONSOLIDATION PIPELINE  (SO→Spindle→Ripple→cAMP hierarchy analog)              │
│  ┌──────────────────────────────────────────────────────────────────────┐      │
│  │  Stage 1 (L1→L2): Episode → graph triples (fast, per boundary)       │      │
│  │  Stage 2 (L2→L3): Graph section → wiki page update (batch, hourly)   │      │
│  │  Stage 3 (L3→L4): Wiki patterns → primitive extraction (daily)        │      │
│  │  Stage 4: Lint pass (weekly)                                           │      │
│  │                                                                        │      │
│  │  Each stage gated by: salience threshold + activity window            │      │
│  └──────────────────────────────────────────────────────────────────────┘      │
│                                                                                  │
│  RETRIEVAL ORCHESTRATOR  (CA1 comparator analog)                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐      │
│  │  Query → classify →                                                   │      │
│  │    recent/episodic    → L1 (episodic store)                           │      │
│  │    relational/multi-hop → L2 (knowledge graph)                        │      │
│  │    conceptual/semantic  → L3 (compiled wiki)                          │      │
│  │    procedural/transfer  → L4 (primitive library)                      │      │
│  │    complex/compound     → parallel multi-layer → merge                │      │
│  │                                                                        │      │
│  │  Post-retrieval: mismatch detection → novelty signal → L1 write       │      │
│  └──────────────────────────────────────────────────────────────────────┘      │
│                                                                                  │
└────────────────────────────────────────────────────────────────────────────────┘
```

### The Consolidation Cascade

```
TIME →

On episode boundary:    L0 (WM) → [summarize] → L1 (Episodic)
                                                 [immediate: extract entities → L2 graph]

Hourly batch:           L1 (top 20% by salience) → [extract knowledge] → L2 + L3
                                                     [detect contradictions]
                                                     [update index.md]

Daily:                  L3 (patterns appearing 3+ times) → [distill] → L4 primitives
                        L3 (lint pass on touched sections)

Weekly:                 Full lint pass: contradictions, orphans, coverage gaps
                        L4 primitive quality review: deprecate low-success primitives
                        L1 eviction: remove low-salience consolidated episodes
```

---

## User Stories

### US-6.1: The Persistent Agent That Grows Over Years
**As an** organization running a mission-critical AI agent continuously,  
**I want the** agent to become progressively smarter about our domain over time  
**So that** the agent's performance in year 3 is dramatically better than year 1.

**Acceptance criteria:**
- Year 1→3 performance improvement is measurable on standardized domain tasks
- Improvement is attributable to specific consolidated knowledge (auditable)
- No catastrophic forgetting of knowledge acquired in year 1
- Knowledge accumulated is portable: can be loaded into a new agent instance

### US-6.2: Seamless Multi-Layer Retrieval
**As a** user who asks diverse questions — some recent, some general, some procedural,  
**I want to** always get the best possible answer regardless of where the information lives  
**So that** I don't need to think about memory layers.

**Acceptance criteria:**
- "What did we decide last Thursday?" → L1 retrieval
- "What is the standard approach for X in our field?" → L3 retrieval
- "How do I implement Y pattern?" → L4 retrieval
- "What are all the factors connecting A to B in our domain?" → L2 retrieval
- All four answered correctly in <5 seconds with appropriate source attribution
- User never prompted to specify which layer to use

### US-6.3: Knowledge Provenance for Any Claim
**As a** user or auditor who needs to verify a claim the agent made,  
**I want to** trace any claim back to its origin  
**So that** I can verify accuracy and understand the confidence level.

**Acceptance criteria:**
- Every claim in an agent response carries a provenance chain: L4 primitive → L3 wiki page → L2 graph node → L1 episode → raw source
- Full trace available on request ("how do you know this?")
- Claims with low provenance (derived by LLM without grounding) are flagged as inferred
- Provenance log is immutable (cannot be retroactively edited)

### US-6.4: Multi-Agent Knowledge Federation
**As an** organization with specialized agents for different domains,  
**I want** agents to share their compiled knowledge across layers  
**So that** a specialist agent's expertise improves the generalist agent.

**Acceptance criteria:**
- Any layer (L2 graph, L3 wiki, L4 primitives) can be exported and imported
- Import merges with existing knowledge (no overwrite of conflicting entries — both retained with source tags)
- Contradictions between imported and existing knowledge are flagged for resolution
- Each agent maintains statistics separately (usage, success rates not merged)

### US-6.5: Memory Health Dashboard
**As an** operator of a production agent,  
**I want to** monitor the health and quality of all memory layers  
**So that** I can identify degradation before it affects user-facing performance.

**Acceptance criteria:**
- Dashboard shows: L1 episode count + eviction rate, L2 graph node/edge counts + contradiction count, L3 wiki page count + lint status, L4 primitive count + average success rate
- Alerting: if contradiction count grows >N/week, if lint finds >M orphan pages, if primitive success rate drops below threshold
- Historical trend charts for all metrics
- One-click triggering of maintenance operations (lint, consolidation pass, primitive review)

### US-6.6: Privacy-Preserving Layer Separation
**As an** organization with sensitive user data in conversation history,  
**I want** the episodic layer (L1) to be separately encrypted and access-controlled  
**So that** raw conversation data is never exposed when sharing compiled knowledge.

**Acceptance criteria:**
- L1 (episodic) is encrypted at rest with per-user or per-session keys
- L2/L3/L4 can be exported without including any L1 verbatim content
- Access to L1 requires explicit authorization separate from L2/L3/L4 access
- Compilation process (L1→L2, L1→L3) runs in a secure enclave and only outputs de-identified knowledge

---

## Requirements

### Functional Requirements

| ID | Requirement |
|----|------------|
| F6.1 | Four persistent memory layers: L1 (episodic), L2 (graph), L3 (wiki), L4 (primitives) |
| F6.2 | L0 working memory is the active context window; managed by retrieval orchestrator |
| F6.3 | Event boundary detector gates L0→L1 transitions |
| F6.4 | Consolidation pipeline has 4 stages with distinct timing: per-boundary, hourly, daily, weekly |
| F6.5 | Each consolidation stage is gated by salience threshold |
| F6.6 | Retrieval orchestrator classifies queries and routes to appropriate layer(s) |
| F6.7 | Mismatch detection: compare retrieved content with current input; novelty → L1 write |
| F6.8 | Every claim in a response carries a provenance chain through all layers |
| F6.9 | Any layer is independently exportable in a portable format |
| F6.10 | Imported knowledge is merged (not overwritten); conflicts flagged |
| F6.11 | Memory health metrics exposed via API: counts, contradiction rates, lint status, success rates |
| F6.12 | L1 can be encrypted independently of L2/L3/L4 |

### Non-Functional Requirements

| ID | Requirement |
|----|------------|
| NF6.1 | L1→L2 per-boundary consolidation: <30 seconds |
| NF6.2 | Hourly batch consolidation (100 episodes): <5 minutes |
| NF6.3 | Retrieval orchestration + multi-layer retrieval: <5 seconds for 95th percentile |
| NF6.4 | System handles 10M+ L1 episodes, 1M+ L2 nodes, 10K+ L3 pages, 100K+ L4 primitives |
| NF6.5 | All layers persist across restarts with crash recovery |
| NF6.6 | Memory footprint: L1 (compressed summaries + embeddings), L2 (graph DB), L3 (files), L4 (JSON) |
| NF6.7 | LLM-agnostic: swapping the underlying LLM does not invalidate any stored layer |

---

## User Scenarios

### Scenario A: The Enterprise Legal AI (3 years)

**Year 1:** Agent handles contracts and due diligence for a law firm. L1 fills with case conversations. Weekly consolidation builds L2 (legal entity graph: companies, provisions, precedents) and L3 (wiki of common clauses, jurisdiction notes, case patterns).

**Year 2:** L4 library has 200 legal primitives: `analyze_indemnification_clause`, `check_governing_law_consistency`, `identify_ipĀ_ownership_transfer`. New associates use the agent and immediately get year-1 knowledge.

**Year 3 scenario:** Complex cross-border M&A transaction. Agent retrieves:
- L1: 3 similar prior transactions from the last 6 months (episodic)
- L2: relationship graph: counterparty's prior dealings, regulatory history (relational)
- L3: wiki section on cross-border IP transfer requirements for the relevant jurisdictions (semantic)
- L4: `cross_border_compliance_checklist(jurisdictions=[US,EU,JP])` (procedural)
Synthesizes a comprehensive risk memo in 45 seconds. A junior associate would take 3 days.

### Scenario B: The Personal Life AI (ongoing)

**The pitch:** Your AI knows your life the way your best friend does — but with perfect memory.

**L1:** Every conversation since you started using it. Encrypted with your key. Only you can access it.

**L3 (your wiki):** Your values, your goals, your current projects, your relationships (names, context), your recurring themes, your health patterns, your preferences — compiled from L1, never verbatim conversations.

**L4 (your primitives):** How you make decisions, how you approach problems, what heuristics you use. Distilled from your repeated patterns.

**Query at year 3:** "Help me think through this career decision."  
Agent retrieves: L3 page on "your career values" + L3 page on "your current financial situation" + L1 episode from 8 months ago where you first mentioned wanting to try something new + L4 primitive "your decision-making framework (pros/cons + 10-year regret test)."  
Response feels like advice from someone who knows you deeply — because the agent does.

### Scenario C: The Scientific Research Infrastructure

**Setup:** National research institute deploys a shared memory stack fed by 50 researchers over 10 years.

**L1:** Experiment logs, lab meeting discussions, failure notes, serendipitous observations.  
**L2:** Research knowledge graph: genes, proteins, compounds, mechanisms, publications, experiments.  
**L3:** Living review articles, protocol wikis, method comparisons — updated as new experiments complete.  
**L4:** Research primitives: `power_analysis_for_n`, `confound_checklist(model_organism)`, `replication_protocol`.

**Discovery scenario (year 7):** New researcher asks: "Has anyone seen an unexpected immune activation with this compound class?"  
L2 PageRank from `immune_activation + compound_class_X` traverses: past experiments → notes from a postdoc 3 years ago who mentioned it in an L1 conversation but never published → retrieves the full episode → the observation is now findable.

**Success signal:** A discovery that would have been buried in a lab notebook is found in seconds. Time from observation to follow-up experiment: 3 years reduced to 1 week.

---

## Success Criteria and Capabilities

### What this setup does well

| Capability | Why |
|-----------|-----|
| **Maximum capability across all dimensions** | All four memory functions integrated |
| **Progressive improvement over time** | Consolidation cascade continuously improves all layers |
| **Provenance for all claims** | Every layer traced back to L1 source |
| **Privacy by design** | L1 independently encrypted; L2/L3/L4 can be shared |
| **Multi-agent federation** | Layer-level export/import |
| **Long-term institutional memory** | Years or decades of accumulated knowledge |
| **Full interpretability** | Every layer is readable; no black box |

### Limitations

| Limitation | Mitigation |
|-----------|------------|
| **High operational complexity** | Requires dedicated infrastructure and monitoring |
| **LLM cost at scale** | Consolidation pipeline is LLM-heavy; cost scales with episode volume |
| **Cold start investment** | Weeks before all layers are meaningfully populated |
| **Schema evolution complexity** | Changing L2/L3/L4 schema requires migration passes |
| **Failure propagation** | Bad L1 → bad L2/L3/L4 if consolidation not validated |

### Capability Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| Knowledge synthesis | ★★★★★ | L3 + L2 combined |
| Multi-hop reasoning | ★★★★★ | L2 graph traversal |
| Real-time learning | ★★★★★ | L1 immediate capture |
| Episodic memory | ★★★★★ | L1 dedicated |
| Contradiction handling | ★★★★★ | L3 lint + L2 contradiction edges |
| Portability | ★★★★☆ | Each layer portable; full stack needs infrastructure |
| Setup complexity | ★☆☆☆☆ | Very high; not for prototypes |
| Scalability | ★★★★★ | Each layer scales independently |
| Prioritized retention | ★★★★★ | Salience scoring throughout cascade |
