# Neuroscience of Memory: Research Reports for AI Memory System Design

**Period covered:** 2024–2026  
**Purpose:** Ground AI agent memory system design in cutting-edge neuroscience  
**Date compiled:** April 2026

---

## Report Structure

| File | Topic |
|------|-------|
| [01-computational-frameworks.md](./01-computational-frameworks.md) | Attractor networks, Hopfield models, CLS theory, predictive coding, generative models |
| [02-ecog-human-ieceg.md](./02-ecog-human-ieceg.md) | ECoG/iEEG findings: HFOs, theta precession, spectral patterns, sleep recordings |
| [03-oscillations-mechanisms.md](./03-oscillations-mechanisms.md) | Sharp-wave ripples, theta, gamma, sleep oscillatory hierarchy |
| [04-circuits-regions.md](./04-circuits-regions.md) | CA3/CA1/DG roles, entorhinal cortex, PFC-hippocampal circuit, engrams, LC |
| [05-models-and-learning.md](./05-models-and-learning.md) | Orthogonalized state machines, compositional replay, planning models, consolidation theory |
| [06-ai-design-principles.md](./06-ai-design-principles.md) | Direct mappings from biology to AI, HippoRAG, design patterns, open challenges |
| [07-key-researchers.md](./07-key-researchers.md) | Leading labs and researchers, their 2024–2026 contributions |
| [08-references.md](./08-references.md) | Complete reference list with DOIs |

---

## Five Highest-Impact Findings for AI Memory Design

1. **CA3 attractor via BTSP (Cell 2024):** Hippocampal CA3 operates as a content-addressable attractor through behavioral-timescale synaptic plasticity at recurrent synapses — the biological implementation of associative memory retrieval from partial cues.

2. **SWR-mediated experience selection (Science 2024, Buzsáki lab):** Sharp-wave ripples during reward consumption selectively *tag* experiences for consolidation during subsequent sleep — the brain's priority replay queue. Not all experiences are replayed equally.

3. **Orthogonalized state machine (Nature 2025, Janelia):** Hippocampal CA1 learning progressively decorrelates similar activity patterns into an orthogonalized state machine best described by Clone-Structured Causal Graphs — latent state inference, not flat lookup.

4. **Modern Hopfield = Transformer attention (NeurIPS 2024):** Kernelized Hopfield Models achieve provably optimal memory capacity and are formally equivalent to transformer attention — with spherical code keys maximizing capacity.

5. **HippoRAG outperforms RAG by 20% (NeurIPS 2024):** Direct implementation of hippocampal indexing theory using knowledge graphs + Personalized PageRank beats standard RAG on multi-hop QA at 10–30x lower cost.

---

## Core Conceptual Framework

```
ENCODING                    CONSOLIDATION               RETRIEVAL
────────                    ─────────────               ─────────
Theta oscillations          Sleep: SO→Spindle→Ripple    Pattern completion
LC-NE event boundaries      cAMP infra-slow (~0.01 Hz)  CA3 attractor recall
DG pattern separation       SWR selective replay        CA1 mismatch detection
CA3 autoassociation         vmPFC integration gating    Neocortical reinstatement
CA1 novelty detection       CLS slow neocortical update HFO global co-bursting
Time cells / sequences      Systems reorganization      Compositional binding
```

---

## Key Journals and Venues (2024–2026)

- **Nature, Nature Neuroscience, Nature Human Behaviour, Nature Communications**
- **Science, Cell, Neuron**
- **NeurIPS 2024** (major computational memory papers)
- **eLife, PLOS Computational Biology, Current Biology**
- **Brain** (human iEEG/ECoG)
- **arXiv/bioRxiv** (preprints from top labs)
