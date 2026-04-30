# Setup 2: The Hippocampal Knowledge Graph (HippoRAG)

**Inspiration:** HippoRAG (NeurIPS 2024, arXiv:2405.14831) + hippocampal indexing theory (Teyler & DiScenna 1986)  
**Neuroscience analog:** Hippocampal index + parahippocampal entity binding + neocortical content storage  
**Complexity:** Medium  
**Best scale:** Domain knowledge base, 100K–50M words; multi-hop retrieval critical

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    HIPPOCAMPAL KNOWLEDGE GRAPH                        │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  SOURCE LAYER (Neocortex analog)                                       │
│  ┌────────────────────────────────────────────────────────────┐       │
│  │  Raw documents → chunked text passages                      │       │
│  │  Each passage: {id, text, source, timestamp, embedding}    │       │
│  │  Stored in: vector store + document store                   │       │
│  └────────────────────────────────────────────────────────────┘       │
│                         ↑↓ extraction                                  │
│                                                                        │
│  KNOWLEDGE GRAPH (Hippocampal index + EC analog)                       │
│  ┌────────────────────────────────────────────────────────────┐       │
│  │  Nodes: named entities, concepts, events                   │       │
│  │  Edges: typed predicates (causes, part-of, follows, etc.)  │       │
│  │  Each node → embedding → ANN index                         │       │
│  │  Each node → list of source passage IDs (the "index")      │       │
│  │                                                             │       │
│  │  Built by: LLM extracts (S, P, O) triples from passages    │       │
│  └────────────────────────────────────────────────────────────┘       │
│                         ↑↓ personalized PageRank                       │
│                                                                        │
│  RETRIEVAL ENGINE (CA3 pattern completion analog)                      │
│  ┌────────────────────────────────────────────────────────────┐       │
│  │  Query → embed → KNN on node embeddings (seed nodes)       │       │
│  │  Seed nodes → Personalized PageRank over graph             │       │
│  │  Top-ranked nodes → fetch their source passages            │       │
│  │  Passages → LLM synthesizes answer                         │       │
│  └────────────────────────────────────────────────────────────┘       │
│                                                                        │
└──────────────────────────────────────────────────────────────────────┘
```

### Encoding Flow
```
Document corpus
    ↓
Chunking (semantic, ~500 tokens with overlap)
    ↓
LLM extracts named entities + (S,P,O) triples per chunk
    ↓
Build/update knowledge graph:
    - New entities → new nodes
    - New triples → new directed edges
    - Existing entities → append source passage IDs
    ↓
Embed all nodes → upsert to ANN index
    ↓
Store passage texts in document store with node cross-references
```

### Retrieval Flow
```
Query: "How do sharp-wave ripples relate to memory consolidation during sleep?"
    ↓
Embed query → KNN over node embeddings
    → Top seeds: {sharp-wave-ripple, memory-consolidation, NREM-sleep, hippocampus}
    ↓
Personalized PageRank from seed nodes
    → Propagates through graph: SWR → hippocampus → CA1 → theta → sleep → PFC...
    → Ranks ALL nodes by proximity to seeds
    ↓
Top-ranked nodes → retrieve their source passages (the "index pointers")
    ↓
LLM reads retrieved passages → synthesizes answer
```

### Update Flow (incremental)
```
New document arrives
    ↓
Extract new triples → merge into existing graph (no full rebuild)
    ↓
New entities → new nodes + embeddings
    ↓
Updated entities → append source passage IDs to existing nodes
    ↓
Re-run ANN index upsert for new/changed nodes only
```

---

## User Stories

### US-2.1: Multi-Hop Research Query
**As a** researcher who needs to find indirect connections between concepts,  
**I want to** ask questions that require following chains of reasoning across 3+ hops  
**So that** I discover non-obvious relationships in the literature.

**Acceptance criteria:**
- "What mechanisms connect theta oscillations to memory consolidation during slow-wave sleep?" returns an answer that traverses: theta → CA3 → SWR → NREM → SO→Spindle→Ripple chain
- Answer cites specific passages from 4+ distinct sources
- No single passage contained the full chain

### US-2.2: Entity-Centric Knowledge
**As a** researcher who wants to understand everything about a specific concept,  
**I want to** query all knowledge around an entity  
**So that** I get a comprehensive, multi-source picture of that entity.

**Acceptance criteria:**
- "Tell me everything known about Buzsáki's work on SWRs" returns synthesized findings from all papers by Buzsáki in the corpus, plus papers that cite him
- Graph traversal finds adjacent entities: lab members, collaborating labs, related concepts
- Result is structured: key claims, timeline of discoveries, open questions

### US-2.3: Incremental Corpus Growth
**As a** team managing a shared knowledge base that grows weekly,  
**I want to** add new documents without rebuilding the entire index  
**So that** the system remains current with minimal operational overhead.

**Acceptance criteria:**
- Adding 10 new papers takes <5 minutes total processing time
- New knowledge is immediately queryable after ingest
- Existing retrieval quality for old queries does not degrade

### US-2.4: Contradiction and Conflict Detection
**As a** domain expert who needs to know where the field disagrees,  
**I want to** find nodes in the knowledge graph where contradictory predicates exist  
**So that** I can surface genuine scientific controversies.

**Acceptance criteria:**
- System detects: (ripples, REQUIRED_FOR, consolidation) and (ripples, NOT_REQUIRED_FOR, consolidation) as contradiction
- Contradiction report shows both claims with source passages and dates
- Graph visualization shows contradiction nodes highlighted

### US-2.5: Cross-Domain Knowledge Transfer
**As a** AI engineer using a neuroscience knowledge base to design memory systems,  
**I want to** query for biological concepts and receive AI-engineering translations  
**So that** I can directly apply neuroscience findings to software architecture.

**Acceptance criteria:**
- "What biological mechanisms map to transformer attention?" returns a structured mapping with neuroscience → AI columns
- System recognizes "Modern Hopfield = Transformer" as a cross-domain equivalence (stored as a typed edge in the graph)
- Cross-domain edges are explicitly typed as "analogous-to" (distinct from "causes" or "part-of")

### US-2.6: Knowledge Base Audit for a New Hire
**As a** manager onboarding an engineer to a complex technical domain,  
**I want to** generate a structured reading list from the knowledge base  
**So that** the new hire builds understanding in the right order.

**Acceptance criteria:**
- System generates a topologically sorted reading list based on graph dependencies (foundational concepts first)
- Estimated reading time per item shown
- List accounts for existing knowledge (new hire can declare "I already know X" and the list adapts)

---

## Requirements

### Functional Requirements

| ID | Requirement |
|----|------------|
| F2.1 | System extracts (subject, predicate, object) triples from all ingested documents using LLM |
| F2.2 | Knowledge graph nodes are typed: Entity, Concept, Event, Claim |
| F2.3 | Knowledge graph edges are typed: causes, part-of, follows, contradicts, analogous-to, supports, refutes |
| F2.4 | Each node stores a list of source passage IDs (the hippocampal index) |
| F2.5 | All nodes have embeddings stored in an ANN index |
| F2.6 | Retrieval uses Personalized PageRank (or equivalent graph traversal) from KNN seed nodes |
| F2.7 | Incremental update: new documents merge into existing graph without full rebuild |
| F2.8 | System detects contradiction edges (A `contradicts` B where A and B are both asserted as true) |
| F2.9 | System supports typed cross-domain edges (analogous-to, maps-to) for inter-domain connections |
| F2.10 | Retrieval returns source passage IDs + passage text for all claims in the answer |

### Non-Functional Requirements

| ID | Requirement |
|----|------------|
| NF2.1 | Graph supports up to 1M nodes and 5M edges without degradation |
| NF2.2 | Query latency <3 seconds for corpora up to 10M words |
| NF2.3 | Incremental ingest of 10 documents completes <5 minutes |
| NF2.4 | Graph is exportable to standard formats (RDF, GraphML, JSON-LD) |
| NF2.5 | System is LLM-agnostic for triple extraction (swappable extractor) |
| NF2.6 | ANN index supports cosine similarity with <10ms retrieval for 1M nodes |

---

## User Scenarios

### Scenario A: The Pharma Research Team

**Scale:** 5,000 papers, 10M words. Team of 8 researchers across oncology, genomics, and drug mechanisms.

**Encoding:** Over 3 months, all papers ingested. Graph has 120K nodes, 800K edges. Node types: 30K proteins, 15K compounds, 40K mechanisms, 35K papers as event nodes.

**Query example:** "What compounds in our corpus have shown activity against KRAS G12C and have CNS penetration data?"
- Seed nodes: {KRAS-G12C, CNS-penetration, compound-activity}
- PageRank traverses: KRAS → MAPK-pathway → sotorasib → clinical-trials → CNS-penetration data
- Returns 4 relevant compounds with source citations — a query that would take a human analyst 4+ hours

**Contradiction surfaced:** Two papers make contradictory claims about compound X's half-life. System flags: "Compound-X (half-life, 4h) from Paper 2021-A vs. (half-life, 12h) from Paper 2023-B — different assay conditions (in vitro vs. in vivo)"

**Success signal:** Research team reduces time-to-answer for cross-paper synthesis questions from days to minutes.

### Scenario B: The AI Engineering Team Building on Neuroscience

**Scale:** The neuroscience memory corpus from these reports (~200 papers). Graph has ~8K nodes, ~40K edges.

**Query:** "Design a memory architecture for an agent that needs to handle both one-shot learning and multi-episode recall"
- PageRank from seeds: {one-shot-learning, episodic-memory, multi-episode, agent-architecture}
- Traverses: CLS theory → HippoRAG → CSCG → SWR selection → event boundaries
- Returns: structured architecture recommendation with biological grounding, citing 7 papers

**New paper integration:** Karpathy's LLM Wiki paper added. System: creates nodes (karpathy, llm-wiki, compiler-analogy, anti-rag), creates edge (llm-wiki, analogous-to, hippocampal-indexing), updates hippocampal-indexing node with new source passage.

**Cross-domain mapping query:** "How does the CA3 attractor map to transformer self-attention?" — System finds the (CA3-attractor, analogous-to, modern-hopfield-network) and (modern-hopfield-network, equivalent-to, transformer-attention) edges, traverses both hops, returns the mapping.

### Scenario C: The Legal Knowledge Base

**Scale:** 50,000 documents (case law, statutes, regulations). Graph organized around legal concepts, precedents, and jurisdictions.

**Multi-hop query:** "In which jurisdictions does Product Liability doctrine impose strict liability and what defenses are available?"
- Seed nodes: {Product-Liability, Strict-Liability}
- Graph traversal: Strict-Liability → Restatement-2nd → §402A → California → warnings-defect
- Returns jurisdiction-by-jurisdiction breakdown with case citations

---

## Success Criteria and Capabilities

### What this setup does well

| Capability | Why |
|-----------|-----|
| **Multi-hop reasoning** | Graph structure + PageRank naturally traverses chains |
| **Large corpora** | Graph scales to millions of nodes; ANN scales to millions of embeddings |
| **Relationship-aware retrieval** | Typed edges carry semantics that vector similarity cannot |
| **Contradiction detection** | Explicit `contradicts` edges; queryable as a graph pattern |
| **Incremental updates** | Graph merge is cheaper than full re-encoding |
| **Cross-domain transfer** | `analogous-to` edges bridge domains |
| **Explainable retrieval path** | Can show the full graph traversal path that produced an answer |

### Limitations

| Limitation | Mitigation |
|-----------|------------|
| **Triple extraction quality** limited by LLM | Multiple extraction passes; human validation for critical edges |
| **No episodic memory** | Not designed for agent interaction history |
| **No temporal ordering** | Add timestamp edges and `follows` predicates |
| **Graph can become noisy** | Periodic graph pruning pass (lint analog) |
| **Higher infrastructure** | Requires graph DB (Neo4j, Kuzu) + vector store + LLM |
| **Cold start** | Needs a full ingest pass before useful |

### Capability Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| Knowledge synthesis | ★★★★★ | Strongest at this; multi-hop synthesis |
| Multi-hop reasoning | ★★★★★ | Core design strength |
| Real-time learning | ★★★☆☆ | Incremental; not streaming |
| Episodic memory | ★★☆☆☆ | Not designed for it |
| Contradiction handling | ★★★★★ | Explicit in graph schema |
| Portability | ★★★☆☆ | Needs graph DB and vector store |
| Setup complexity | ★★★☆☆ | Moderate infrastructure |
| Scalability | ★★★★★ | Millions of nodes |
| Prioritized retention | ★★★☆☆ | Can weight edges by salience |
