# Circuits, Regions, and Memory Mechanisms (2024–2026)

---

## 1. Hippocampal Subregion Roles: Updated 2024–2026

### Overview of Trisynaptic Circuit

```
Entorhinal Cortex (EC)
    ├── Layer II → Dentate Gyrus (DG)     [perforant path, mossy fibers]
    │               ↓
    │           CA3                         [Schaffer collaterals]
    │               ↓
    ├── Layer III → CA1 ──────────────────► Subiculum → EC
    │               ↑ (monosynaptic shortcut)
    └────────────► CA1
```

### Dentate Gyrus (DG)

**Primary function:** Pattern separation — creating orthogonal (non-overlapping) representations of similar inputs

**2024–2026 Key Findings:**

| Paper | Findings |
|-------|---------|
| bioRxiv, December 2025 | DG drives *rate* remapping (different firing rates) but not *global* remapping (different place fields) in proximal CA3 |
| Cog. Neurodynamics, 2025 | Adult neurogenesis in DG optimizes separation at specific turnover rates — too fast or too slow impairs separation |
| Nature Communications, 2024 | DG inputs control **theta phase order** of CA3 cell sequences, not just which cells fire |
| 2025 | Newborn granule cells (from neurogenesis) are more excitable and provide pattern separation for recent memories; older granule cells provide stability for older memories |

**Computational property:** Sparse coding (~2–5% of DG cells active simultaneously) via feedforward inhibition and lateral inhibition from mossy cells. High expansion (EC→DG is ~5x expansion in cell count) + sparse coding = maximum pattern separation capacity.

### CA3

**Primary function:** Pattern completion (autoassociation) — retrieving full stored patterns from partial cues

**2024–2026 Key Findings:**

| Paper | Findings |
|-------|---------|
| Cell, October 2024 | BTSP at recurrent CA3–CA3 synapses creates attractor dynamics; ~10x higher recurrent connectivity than assumed |
| PLOS Computational Biology, 2025 | Heterosynaptic plasticity at E-to-I synapses in CA3 provides stable pattern completion |
| Nature Communications, 2024 | DG mossy fiber inputs control the *phase order* of CA3 cell sequences during theta; phase order encodes temporal sequence information |

**Computational property:** CA3 as an autoassociative network — recurrent synaptic weights encode memories. Retrieval = energy minimization that drives activity toward stored attractor states.

**CA3 supports two operations:**
1. **Pattern completion:** Partial input → full stored pattern (strong recurrent drive > EC input)
2. **Pattern separation** (in encoding mode): Weak EC input + strong recurrent suppression → orthogonalized output

### CA1

**Primary function:** Output comparator; novelty detection; temporal binding; indexing of cortical representations

**2024–2026 Key Findings:**

| Paper | Findings |
|-------|---------|
| Nature, February 2025 | Learning drives orthogonalization — CA1 progressively decorrelates activity patterns into an orthogonalized state machine |
| Nature Neuroscience, 2026 | Non-overlapping CA1 ensembles recruited at different acquisition phases; dynamic engram composition begins within hours |
| Nature, January 2026 | Reward-tuned CA1 neurons backward-shift their activity from reward to preceding cues over weeks (TD-learning) |

**Novelty detection mechanism:**
- CA3 input (via Schaffer collaterals) brings *retrieved expectation* (what CA3 pattern-completes)
- EC layer III input brings *current sensory input* (what is actually happening)
- CA1 detects *mismatch* between these → if large mismatch → novelty signal → triggers new encoding

---

## 2. Medial Entorhinal Cortex (MEC) and Grid Cells

### Functions
- Provides spatial/abstract metric via grid cells (hexagonal firing fields)
- Drives fast gamma input to CA1 (encoding mode)
- Fast gamma from MEC to CA1 carries current sensory information

### 2024–2026 Key Findings

**"A consistent map in medial entorhinal cortex supports spatial memory"**  
*Nature Communications*, 2024. DOI: 10.1038/s41467-024-45853-4
- A consistent MEC map develops **gradually during learning** and is necessary for spatial memory performance
- MEC representations require experience to stabilize — not pre-wired

**"One-shot entorhinal maps enable flexible navigation in novel environments"**  
*Nature*, 2024. DOI: 10.1038/s41586-024-08034-3
- MEC can form **stable maps of novel environments in a single session**
- These one-shot maps support immediate flexible navigation

**Predictive Grid Cells (2024):**
- A subset of MEC neurons represent *future projected positions* by shifting their grid fields against the direction of travel
- These "predictive grid cells" encode expected future states — not just current position
- Rate of predictive shift correlates with planning success

**Grid cells in abstract spaces:**
- Grid-like representations found in humans navigating conceptual spaces (e.g., social hierarchies, value spaces)
- MEC provides a **general-purpose metric** for any structured representational space, not just physical space

### AI Design Principle
Grid cells implement a **learned coordinate system** for abstract representational spaces. In AI memory:
- MEC → the embedding space structure itself (coordinate system)
- Grid fields → learned basis vectors that tile the representational space
- Predictive grid cells → next-state predictions in the embedding space

---

## 3. Lateral Entorhinal Cortex (LEC)

**Primary function:** Item identity and contextual information (the "what" complement to MEC's "where")

- LEC neurons represent objects, contexts, and events without metric spatial coding
- LEC → DG pathway is critical for binding contexts to items in episodic memory
- LEC provides temporal context codes that allow time-stamping of memories
- Disinhibitory circuit in LEC: VIP interneurons → SST interneurons → pyramidal cells provide **learning-driven place map stabilization** in downstream regions

---

## 4. Prefrontal-Hippocampal Circuit

### vmPFC Controls Memory Organization

**de Sousa, Zeidler, Silva et al., Nature Neuroscience, April 2026**  
*"The prefrontal cortex controls memory organization in the hippocampus"*  
DOI: 10.1038/s41593-026-02231-1

**Mechanism:**
```
vmPFC detects contextual similarity between new and stored experience
    ↓
vmPFC → medial entorhinal cortex projections
    ↓
Modulate hippocampal ensemble overlap
    ├── Similar contexts: vmPFC promotes INTEGRATION (merge memories)
    └── Dissimilar contexts: vmPFC promotes SEPARATION (new episode)

Also:
vmPFC → neurogliaform cells in dorsal CA1
    ↓
Controls memory allocation (which CA1 neurons encode new memory)
```

**Key insight:** vmPFC acts as a **contextual gate** — it determines whether a new experience should be integrated into an existing memory schema or encoded as a new distinct episode. This prevents both over-generalization (conflating different episodes) and over-specificity (failing to generalize across related episodes).

### PFC and Planning

**Jensen, Hennequin, Mattar, Nature Neuroscience, 2024**  
*"A recurrent network model of planning explains hippocampal replay and human behavior"*  
DOI: 10.1038/s41593-024-01675-7

- Meta-RL agent with policy "rollout" planning whose rollout patterns resemble hippocampal replay
- PFC controls **when to plan**; replays are both triggered by and adaptively affect prefrontal dynamics
- PFC-triggered replay = mental simulation of future scenarios using stored hippocampal maps

### AI Design Principle
```
PFC analog in AI agents:
- Executive controller that determines memory allocation
- Contextual similarity check before writing new memory
- If new_context ~ existing_context: UPDATE existing trace
- If new_context ≠ existing_context: CREATE new episode
- Threshold is a learned parameter (vmPFC "decision boundary")
```

---

## 5. Locus Coeruleus and Event Boundary Detection

### Key Paper
**Davachi lab, Neuron, 2025**  
*"Locus coeruleus activation 'resets' hippocampal event representations and separates adjacent memories"*  
DOI: 10.1016/j.neuron.2025.04

### Mechanism
```
Context shift detected
    ↓
Pupil-linked arousal response (pupillometry marker)
    ↓
Phasic LC → norepinephrine release
    ↓
NE promotes temporal pattern separation in DG
    ↓
LC activation resets CA1 representations
    ↓
Prevents interference between temporally adjacent memories
    ↓
New memory episode initialized
```

### Prediction Error Grading
- **Minor prediction error:** Memory *updating* (existing trace modified)
- **Large prediction error:** New encoding initiated (new episode created)
- The LC-NE system provides a continuous variable signal that determines which mode operates

### Context Boundary Marking
Event boundaries marked by LC-NE reset create the "episode" structure of memory. Events within a boundary share overlapping hippocampal representations; events across a boundary have orthogonalized representations.

### AI Design Principle
```
LC-NE event boundary detector in AI:
- Monitor perplexity / surprise of incoming information
- Low surprise: continue accumulating in current episode
- High surprise: 
    1. Flush working memory / summarize current episode
    2. Reset context window
    3. Begin new episode
    4. Write episode boundary marker to memory store
- Surprise threshold is tunable (analogous to NE sensitivity)
```

---

## 6. Memory Engram Biology

### Definition
An engram is the physical change in the brain that constitutes a stored memory — the specific ensemble of neurons and synaptic changes encoding a particular experience.

### Key 2026 Paper: Engram Deconstruction

**Pouget, Morier, Autore et al., Nature Neuroscience, March 2026**  
*"Deconstruction of a memory engram reveals distinct ensembles recruited at learning"*  
DOI: 10.1038/s41593-026-02230-2

**Findings:**
- Non-overlapping dorsal CA1 ensembles are recruited at **different phases of acquisition**
- Cells active during specific acquisition periods are *sufficient alone* to drive memory expression
- Engram composition begins changing **within hours of learning** (dynamic, not static)
- Inhibitory synaptic plasticity is necessary for engram selectivity (without it, engrams blur into each other)

### Distributed Engram Complex
Brain-wide mapping (Tonegawa lab and others) shows engrams for a single memory are distributed across **247+ brain regions** — "unified engram complex":
- Hippocampus: episodic index and binding
- Amygdala: emotional valence and arousal tagging
- Prefrontal cortex: executive context and schema
- Sensory areas: perceptual details

### AI Design Principle
A single memory should be stored across **multiple representation levels**, each capturing different aspects:
- Episodic index (hippocampal analog): unique identifier + associations
- Semantic content (cortical analog): concepts, entities, relationships
- Valence/importance (amygdala analog): salience score, emotional weight
- Perceptual details (sensory cortex analog): verbatim text, sensory features

---

## 7. Hippocampal Indexing Theory: 2024–2026 Status

### Original Theory
Teyler & DiScenna (1986): Hippocampus stores a sparse *index* pointing to distributed neocortical representations. Retrieval = hippocampal index reactivates the distributed cortical pattern.

### 2024–2025 Evidence Updates
- Double dissociation confirmed: early hippocampal reinstatement of item-context associations precedes later lateral temporal cortex reinstatement of item information
- Hippocampus binds objects into **relational configurations** — it's not just an index but also a *relational map*
- Can construct new situations from cortical representations by binding them in novel relational configurations

### HippoRAG: Direct Implementation (NeurIPS 2024)

**"HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models"**  
arXiv:2405.14831

| Biological Component | HippoRAG Component |
|---------------------|-------------------|
| Neocortex (knowledge storage) | LLM for knowledge extraction |
| Parahippocampal cortex (entity recognition) | Named entity recognition → knowledge graph nodes |
| Hippocampal index | Personalized PageRank over knowledge graph |

Results:
- Outperforms standard RAG by up to **20% on multi-hop QA**
- 10–30x cheaper than iterative retrieval (IRCoT)
- 6–13x faster than iterative approaches

### AI Design Principle
The indexing architecture:
```
Encoding:
    Raw text → LLM extracts (subject, predicate, object) triples
    → Add nodes/edges to knowledge graph
    → Embed each node as a vector
    
Retrieval:
    Query → embed query
    → Find similar nodes in graph (nearest neighbor)
    → Run Personalized PageRank from those seed nodes
    → Retrieve connected subgraph (the "indexed" content)
    → Provide as context
```
This gives associative, multi-hop retrieval (CA3-like pattern completion across graph structure) rather than flat vector similarity.

---

## 8. Compositional Memory and Replay

### Key Paper
**Bakermans, Warren, Whittington, Behrens, Nature Neuroscience 28:1061, 2025**  
*"Constructing future behavior in the hippocampal formation through composition and replay"*  
DOI: 10.1038/s41593-025-01908-3

**Principle:**
- State spaces are constructed **compositionally from existing building blocks** ("primitives")
- Hippocampal responses can be interpreted as binding primitives together
- Replay events from newly discovered landmarks induce new remote firing fields — creating new compositional memories
- Enables optimal behavior in new environments with **no new learning** beyond binding known primitives

**Companion paper:**  
*"Composing hippocampal maps from cortical building blocks in replay"*  
*Nature Neuroscience*, 2025

- Cortical "building blocks" (sensory/motor primitives) are assembled via hippocampal replay
- New environments are navigated by composing known primitives in new configurations

### AI Design Principle
AI memory should support **zero-shot composition**: given known primitives A, B, C and a novel situation requiring A+C, the agent can construct the appropriate memory/behavior without re-training. This maps to:
- Modular prompt composition
- Structured knowledge graphs where relationships can be traversed in novel paths
- Function composition in code generation agents
