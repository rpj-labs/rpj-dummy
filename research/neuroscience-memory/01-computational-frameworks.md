# Computational Frameworks for Memory (2024–2026)

---

## 1. CA3 as Content-Addressable Attractor

### Key Paper
**Maurer et al., Cell, October 2024**  
*"Mechanisms of memory-supporting neuronal dynamics in hippocampal area CA3"*  
DOI: 10.1016/j.cell.2024.09 | Cell 188, 2024

### Findings
- Intracellular recordings + optogenetics in behaving mice showed CA3 place-field activity is produced by **behavioral timescale synaptic plasticity (BTSP)** at recurrent CA3–CA3 synapses
- A computational model incorporating BTSP with an external updating input reproduces attractor dynamics under online learning
- CA3 pyramidal neurons connect at ~10x higher rates than previously assumed — sufficient to support robust pattern completion
- Storage capacity exceeds classic Hopfield models for correlated input patterns

### Mechanism
```
Partial input cue
    ↓
CA3 recurrent synapses (BTSP-strengthened)
    ↓ [pattern completion]
Full stored pattern reinstated
    ↓
CA1 output comparator
    ↓ [match detected → suppress novelty signal]
Neocortical reinstatement via ripple
```

### 2025 Refinement
Selective inhibition in CA3 via **heterosynaptic plasticity at E-to-I synapses** provides stable pattern completion more biologically realistic than global-inhibition-only models (*PLOS Computational Biology*, 2025).

### AI Design Principle
CA3 is the biological implementation of **approximate nearest-neighbor retrieval** — but with learned, weight-matrix-encoded memories rather than a stored vector database. The attractor pull toward stored patterns is equivalent to energy minimization in Hopfield networks.

---

## 2. Modern Hopfield Networks: Optimal Capacity and Transformer Connection

### Key Paper
**Hu, Nguyen, Le et al., NeurIPS 2024**  
*"Provably Optimal Memory Capacity for Modern Hopfield Models: Transformer-Compatible Dense Associative Memories as Spherical Codes"*  
arXiv:2410.23126

### Core Results

| Result | Significance |
|--------|-------------|
| **Kernelized Hopfield Models (KHMs)** achieve provably optimal asymptotic capacity | First tight bound on modern Hopfield memory capacity |
| Memory configurations correspond to **spherical codes** | Connects to classical information theory; keys on the hypersphere maximize capacity |
| Sub-linear retrieval algorithm **U-Hop+** achieves optimal capacity | Practical implementation |
| KHMs are **formally equivalent to transformer attention** | Grounds attention mechanism in associative memory theory |

### Capacity Scaling
- Classical Hopfield: O(N) patterns for N neurons
- Modern Hopfield (dense): O(N^p) for polynomial kernel of degree p — superlinear
- Optimal capacity achieved when keys are arranged as spherical codes (maximally separated on hypersphere)

### Related 2024–2025 Papers

**Hopfield-Fenchel-Young Networks (arXiv:2411.08590, 2024)**  
Generalizes modern Hopfield to a broader family of energy functions using Fenchel-Young losses. Unifies sparse attention, α-entmax, and standard softmax as special cases.

**Modern Hopfield Networks with Continuous-Time Memories (arXiv:2502.10122, 2025)**  
Inspired by psychological theories of continuous neural resource allocation in working memory. Compresses large discrete Hopfield memories into smaller continuous-time representations — analogous to memory compression during sleep consolidation.

**Input-Driven Plasticity (IDP) for Hopfield Retrieval (Science Advances, 2025)**  
Proposes a biased self-attention mechanism generalizing classical Hopfield retrieval. Connects external-input-driven retrieval to hippocampal CA3 backprojections from EC.

### AI Design Principle
**Transformer attention IS a modern Hopfield retrieval step.** The key/query/value decomposition in attention directly maps to the Hopfield energy function. Optimizing key representations to be spherical codes (unit-normalized, maximally separated) maximizes associative memory capacity — which is why L2 normalization before attention helps.

---

## 3. Complementary Learning Systems (CLS) Theory: 2024–2025 Updates

### Origin
McClelland, McNaughton & O'Reilly (1995): Fast hippocampal encoding + slow neocortical generalization. The hippocampus learns episodes rapidly (one-shot); neocortex extracts statistical regularities slowly to avoid catastrophic interference.

### 2025 Neural Network Implementation
**"Hybrid corticohippocampal networks for continual learning"**  
*Nature Communications*, 2025

- Neural networks emulating dual CLS representations significantly mitigate catastrophic forgetting in both task-incremental and class-incremental settings
- The fast system (hippocampal analog) provides a rehearsal buffer; the slow system (neocortical analog) integrates across many examples
- Key insight: **interleaved replay** between fast and slow systems is the critical mechanism, not just having two systems

### 2025 Meta-Learning Discovery
**"A gradient of complementary learning systems emerges through meta-learning"**  
bioRxiv, 2025

- CLS-like specialization (fast vs. slow learner) **emerges naturally from meta-learning** optimization over lifelong learning objectives
- Does not need to be hand-engineered — the gradient of plasticity from hippocampus to neocortex is a learned solution to the stability-plasticity dilemma
- Plasticity gradient: early sensory cortex updates over days; CA1/CA3 can update within one theta cycle (~125 ms)

### AI Design Principle
```
Fast system (hippocampal):       Slow system (neocortical):
- RAG / vector store             - Fine-tuned model weights
- One-shot write                 - Batch gradient update
- High specificity               - High generalization
- Short lifetime (evicts)        - Long lifetime (parametric)
- Retrieval-augmented            - Embedded in weights
```

Interleaved replay between the two systems — not just having both — is what prevents catastrophic forgetting.

---

## 4. Predictive Coding and Sequence Learning

### Hippocampus as Next-State Predictor

**"Predictive sequence learning in the hippocampal formation"**  
*Neuron*, June 2024

A predictive autoencoder model of the hippocampus (EC→DG→CA3→CA1 trisynaptic + EC→CA1 monosynaptic), with CA3 trained as a self-supervised RNN to *predict its next input*. This formalizes hippocampal sequence processing as **next-state prediction**.

### Human Evidence: Temporal Structure Encoding

**"Human hippocampal and entorhinal neurons encode the temporal structure of experience"**  
*Nature*, September 2024. DOI: 10.1038/s41586-024-07973-1

Single-neuron recordings during movie watching:
- Neurons integrate *what* and *when* to extract predictive temporal structure
- Population activity resembles the **structural graph of experienced sequences** — encodes transition probabilities, not just states
- Learning is related to spontaneous **time-compressed replay** during rest

### Reward Prediction Error via Backward Shift

**"Predictive coding of reward in the hippocampus"**  
*Nature*, January 2026. DOI: 10.1038/s41586-025-09958-0  
Yaghoubi, Kumar, Nieto-Posadas et al. (McGill/Harvard)

- Calcium imaging over weeks shows hippocampal reward-tuned neurons gradually **backward-shift their activity** from encoding the reward itself to preceding task features
- Implements a biological TD-learning analog: the predictive signal precedes the reward by a learned temporal offset
- The shift distance scales with the learned value of earlier cues

### Predictive Grid Cells (MEC, 2024)
A subset of MEC neurons represent *future projected positions* by shifting their grid fields **against** the direction of travel — "predictive grid cells" encode expected future states.

### AI Design Principle
Biological memory is **fundamentally predictive and generative**, not merely associative storage. A biologically-grounded AI memory system should:
1. Encode transition probabilities between states, not just states
2. Backward-shift value signals temporally (TD-learning)
3. Use memory to predict the next token/state, not just retrieve past context

---

## 5. Generative Models of Memory (VAE Framework)

### Key Paper
**Spens & Burgess, Nature Human Behaviour, 2024**  
*"A generative model of memory construction and consolidation"*  
DOI: 10.1038/s41562-023-01799-z

### Framework
```
Hippocampus (autoassociative):
    ├── Stores episode index + surprising sensory details
    └── Replay trains generative models in entorhinal + PFC

Entorhinal/PFC (generative, VAE-like):
    ├── Latent variables capture key facts / schema
    └── Supports semantic retrieval without full decoding
```

- Memories are compressed into **latent variables** capturing key facts; surprising sensory details stored separately as episodic specifics
- Latent variable representations support **semantic retrieval** without full decoding
- The model accounts for: imagination, episodic future thinking, schema-based memory distortions, boundary extension effects
- Consolidation = hippocampal replay training the cortical generative model

### AI Design Principle
Separate memory storage into:
1. **Schema/structural store:** High-level latent embeddings (fast to retrieve, generalizable, semantic)
2. **Episodic detail store:** Sensory-specific episodic buffers (slow to retrieve, specific, verbatim)

Analogous to a VAE latent space (schema) + stored residual (episodic detail). Retrieval = decode latent + optionally retrieve residual for high-fidelity recall.

---

## 6. Post-Standard-Model Consolidation Theory

### Key Paper
**"The post-'standard model' age: Updating theories of systems consolidation"**  
*Neuron*, February 2025. DOI: 10.1016/j.neuron.2025.01

### What Changed
The classical "standard model" held that hippocampal memories gradually transfer to neocortex and the hippocampus becomes unnecessary over time. This is now superseded:

| Old View | Updated View |
|----------|-------------|
| Hippocampus → neocortex transfer | Systems *reorganization* (qualitative change) |
| Hippocampus unnecessary for old memories | Hippocampus needed for rich contextual episodic recall indefinitely |
| Simple temporal gradient | Multiple Trace Theory: each retrieval creates a new trace |
| One-directional transfer | Bidirectional dialogue; hippocampus indexes distributed neocortical representations |

### Two Parallel Offline Processes
1. **Conservation:** Reactivation of past memories preserving them against interference
2. **Preparation:** Synaptic plasticity preparing the system for encoding future events

### cAMP Time Window Discovery
**Deng et al., Neuron, June 2025**  
cAMP levels in hippocampus and cortex exhibit **infra-slow oscillations (~0.01 Hz)** during NREM sleep driven by norepinephrine β1 receptors. Hippocampal-cortical interactions peak at cAMP maximum. Suppressing hippocampal activity during this narrow time window specifically impairs spatial memory consolidation.

### AI Design Principle
Memory consolidation in AI agents should not be a simple "write to long-term store" operation. It should be a **systems reorganization**: the agent's parametric representations (model weights or schema store) are updated based on accumulated episodic experiences, qualitatively changing how future retrieval works.
