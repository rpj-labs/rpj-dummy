# Comparison Matrix: Six Memory System Setups

---

## At a Glance

| | Setup 1 | Setup 2 | Setup 3 | Setup 4 | Setup 5 | Setup 6 |
|--|---------|---------|---------|---------|---------|---------|
| **Name** | LLM Wiki | HippoRAG | CLS Dual-Store | Event-Episodic | Compositional | Full Stack |
| **Inspiration** | Karpathy 2026 | HippoRAG NeurIPS 2024 | CLS Theory 1995/2025 | LC-NE + SWR 2025 | Behrens lab 2025 | All layers |
| **Neuro analog** | Hippocampal index + semantic | Hippocampal index + graph | Fast/slow CLS | Episodic segmentation | Compositional replay | Complete system |
| **Complexity** | Low | Medium | Med-High | Medium | High | Very High |
| **Scale** | 10K–500K words | 100K–50M words | Continuous interactions | Persistent agent | Multi-domain agent | Enterprise platform |

---

## Capability Comparison

| Capability | S1 Wiki | S2 Graph | S3 CLS | S4 Episodic | S5 Compositional | S6 Full |
|-----------|---------|---------|--------|------------|-----------------|---------|
| Knowledge synthesis | ★★★★★ | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★★★★ |
| Multi-hop reasoning | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★★★★ |
| Real-time learning | ★★☆☆☆ | ★★★☆☆ | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★★★★ |
| Episodic memory | ★☆☆☆☆ | ★★☆☆☆ | ★★★★☆ | ★★★★★ | ★★☆☆☆ | ★★★★★ |
| Contradiction handling | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★☆☆ | ★★★★★ |
| Portability | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | ★★★★☆ | ★★★★☆ |
| Setup complexity | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | ★★★★☆ | ★☆☆☆☆ |
| Scalability | ★★☆☆☆ | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★★☆ | ★★★★★ |
| Prioritized retention | ★★☆☆☆ | ★★★☆☆ | ★★★★★ | ★★★★★ | ★★★★☆ | ★★★★★ |
| Domain transfer | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | ★★☆☆☆ | ★★★★★ | ★★★★★ |
| Interpretability | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★★☆ | ★★★★★ | ★★★★☆ |
| Privacy controls | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★☆☆☆ | ★★★★☆ | ★★★★★ |

*★★★★★ = core strength, ★☆☆☆☆ = not designed for this*

---

## Infrastructure Requirements

| | Setup 1 | Setup 2 | Setup 3 | Setup 4 | Setup 5 | Setup 6 |
|--|---------|---------|---------|---------|---------|---------|
| Filesystem | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Vector store | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Graph DB | ✗ | ✓ | optional | optional | ✗ | ✓ |
| Embedding model | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Scheduler / cron | optional | optional | ✓ | optional | ✓ | ✓ |
| Persistent store | optional | ✓ | ✓ | ✓ | ✓ | ✓ |
| LLM API calls/day | Low | Medium | High | Medium | High | Very High |

---

## Decision Framework: Which Setup to Use

```
START
  │
  ├── Is your corpus static (documents, not conversations)?
  │     │
  │     ├── Under 500K words, need no infrastructure?
  │     │     └── → SETUP 1: LLM Wiki
  │     │
  │     └── Over 500K words, OR need multi-hop reasoning?
  │           └── → SETUP 2: HippoRAG
  │
  ├── Is your primary use case long-running agent conversations?
  │     │
  │     ├── Need "what did we discuss last week" type queries?
  │     │     └── → SETUP 4: Event-Episodic
  │     │
  │     └── Need agent to also learn and improve from interactions?
  │           └── → SETUP 3: CLS Dual-Store (combines fast+slow)
  │
  ├── Do you need the agent to transfer skills across domains?
  │     └── → SETUP 5: Compositional (pairs well with Setup 3 or 4)
  │
  └── Do you need all of the above for a production platform?
        └── → SETUP 6: Full Stack
```

---

## How Karpathy's Principles Apply Per Setup

| Karpathy Principle | S1 | S2 | S3 | S4 | S5 | S6 |
|-------------------|----|----|----|----|----|----|
| **Compile, don't just retrieve** | ★★★★★ (core) | ★★★★☆ (graph as compiled index) | ★★★★☆ (slow store compilation) | ★★☆☆☆ (episodes not compiled) | ★★★★☆ (primitives are compiled) | ★★★★★ (all layers) |
| **Separate raw from compiled** | ★★★★★ (raw/ vs wiki/) | ★★★★☆ | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★★★★ |
| **Index-first navigation** | ★★★★★ (index.md) | ★★★★★ (graph index) | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★★★★ |
| **Log everything** | ★★★★★ (log.md) | ★★★☆☆ | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★★★ |
| **Lint / health maintenance** | ★★★★★ (explicit lint) | ★★★☆☆ | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★★★★ |
| **Schema as living config** | ★★★★★ (AGENTS.md) | ★★★☆☆ | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★★★★ |
| **Portability / vendor independence** | ★★★★★ (plain markdown) | ★★★★☆ | ★★★☆☆ | ★★★☆☆ | ★★★★☆ | ★★★★☆ |

---

## How Neuroscience Findings Apply Per Setup

| Neuro Finding | Source | S1 | S2 | S3 | S4 | S5 | S6 |
|--------------|--------|----|----|----|----|----|----|
| Hippocampal indexing | Teyler 1986; HippoRAG 2024 | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★☆☆☆ | ★★★☆☆ | ★★★★★ |
| CA3 pattern completion | Cell 2024 | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★★★★ |
| CLS fast/slow | Nat Comms 2025 | ★★☆☆☆ | ★★☆☆☆ | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★★★★ |
| SWR selection | Science 2024 | ★★☆☆☆ | ★★☆☆☆ | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★★★★ |
| LC-NE event boundary | Neuron 2025 | ★☆☆☆☆ | ★☆☆☆☆ | ★★★☆☆ | ★★★★★ | ★★★☆☆ | ★★★★★ |
| vmPFC memory gating | Nat Neuro 2026 | ★★★★★ (AGENTS.md) | ★★★☆☆ | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★★★★ |
| Compositional replay | Nat Neuro 2025 | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | ★★☆☆☆ | ★★★★★ | ★★★★★ |
| CSCG state machine | Nature 2025 | ★★☆☆☆ | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | ★★★★★ | ★★★★★ |
| SO→Spindle→Ripple | Neuron 2025 | ★★☆☆☆ | ★★☆☆☆ | ★★★★☆ | ★★★☆☆ | ★★★☆☆ | ★★★★★ |
| cAMP gating | Neuron 2025 | ★☆☆☆☆ | ★☆☆☆☆ | ★★★☆☆ | ★★☆☆☆ | ★★★☆☆ | ★★★★★ |
| Predictive coding | Nature 2024, 2026 | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | ★★★★☆ | ★★★★☆ | ★★★★★ |

---

## Recommended Combinations

Most real-world deployments combine two or three setups:

| Use Case | Recommended Combination |
|---------|------------------------|
| Research assistant with conversation memory | **S1 + S4** (wiki for domain knowledge, episodic for conversation history) |
| Team knowledge base with multi-hop queries | **S1 + S2** (wiki for humans, graph for complex queries) |
| Learning agent with domain specialization | **S3 + S1** (CLS dual-store where slow store = wiki) |
| Production customer agent | **S3 + S4** (dual-store + episodic = continual learning + conversation memory) |
| Cross-domain enterprise agent | **S3 + S4 + S5** (all runtime layers) |
| Full platform | **S6** (integrates all) |

---

## Migration Path

As your agent scales, migrate up the complexity ladder:

```
MVP / Prototype:
  └─ Start with S1 (LLM Wiki)
     ← Zero infrastructure, immediate value

Growth phase (conversation history needed):
  └─ Add S4 (Episodic) alongside S1
     ← Adds persistent memory without touching knowledge base

Scale phase (multi-hop queries, large corpus):
  └─ Migrate S1 → S2 (HippoRAG graph)
     ← One-time migration; old wiki becomes input to graph encoding

Maturity phase (agent must learn from interactions):
  └─ Add S3 consolidation layer over S2 + S4
     ← S4 episodic → S3 consolidation → S2 graph slow store

Advanced phase (cross-domain transfer):
  └─ Add S5 primitive distillation from S3 slow store
     ← Primitives emerge naturally from high-volume operation

Enterprise platform:
  └─ S6 full stack with monitoring, federation, privacy controls
```

---

## Core Data Model (Shared Across All Setups)

For compatibility across setups, use this shared data model at all layers:

```typescript
// Every piece of stored knowledge
interface MemoryUnit {
  id: string;                    // UUID
  layer: 1 | 2 | 3 | 4;        // Which layer it lives in
  content: string;               // Human-readable text
  embedding: number[];           // For semantic retrieval
  salience: number;              // 0–1 priority score
  
  // Provenance
  source_ids: string[];          // IDs of lower-layer units that produced this
  created_at: Date;
  updated_at: Date;
  
  // Classification
  type: string;                  // Layer-specific type (episode, node, page, primitive)
  context_id: string;            // Which project/domain
  tags: string[];
  
  // Lifecycle
  consolidated: boolean;         // Has this been promoted to the next layer?
  deprecated: boolean;           // Soft-delete
}
```

This unified model means any layer can be queried together, provenance traced from L4 back to L1, and the system migrated between setups without data loss.
