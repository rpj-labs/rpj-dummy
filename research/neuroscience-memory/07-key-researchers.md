# Key Researchers in Memory Neuroscience (2024–2026)

The most respected active researchers and labs, with their specific 2024–2026 contributions most relevant to AI memory design.

---

## Systems Neuroscience Labs

### György Buzsáki — NYU Langone Medical Center
**Focus:** Hippocampal oscillations, sharp-wave ripples, memory consolidation during sleep

**2024 landmark paper:** *"Selection of experience for memory by hippocampal sharp wave ripples"* (Science 2024, DOI:10.1126/science.adk8261)  
Key finding: Awake SWRs during reward consumption **tag** experiences; sleep SWRs selectively replay only tagged experiences.

**Ongoing work (2025):** Hippocampal oscillatory taxonomy; distinction between large vs. small SWRs in consolidation.

**Why follow him:** The definitive authority on SWRs and their role in memory selection. His lab's work directly answers "what gets consolidated and why."

**Key resources:** Lab at NYU Langone; book *"Rhythms of the Brain"* (foundational); Twitter/X active.

---

### Lila Davachi — Columbia University
**Focus:** Episodic memory, encoding, consolidation; hippocampal-neocortical dialogue; emotional memory

**2025 landmark paper:** *"Locus coeruleus activation 'resets' hippocampal event representations and separates adjacent memories"* (Neuron 2025)  
Key finding: LC-NE provides the event boundary signal that separates temporally adjacent memories.

**Ongoing work:** Context-dependent memory; sleep-dependent consolidation using iEEG + fMRI; neuromodulatory control of encoding.

**Why follow her:** The go-to researcher for how event boundaries structure episodic memory — directly relevant to AI episode segmentation.

---

### Charan Ranganath — UC Davis, Dynamic Memory Lab
**Focus:** Cortical networks for episodic memory; anterior temporal vs. posterior medial networks; memory differentiation

**2024:** Book *"Why We Remember"* (popular science + scientific rigor); comprehensive overview of episodic memory science.

**Key framework:** Anterior temporal network (objects, concepts, semantic) vs. Posterior medial network (spatial context, temporal structure, events). These two networks serve complementary roles, analogous to "what" vs. "where" streams.

**Why follow him:** His two-network framework is directly applicable to designing AI memory systems with separate semantic and contextual stores.

---

### Matthew Wilson — MIT Picower Institute
**Focus:** Hippocampal replay; sleep-dependent memory; theta sequences; CA1 population dynamics

**2024:** Latent learning and sleep-dependent plasticity in CA1 subpopulations — distinct cell populations encode overlapping experiences using distinct strategies.

**Key legacy:** Discovered hippocampal replay during sleep (1994, with McNaughton); continues to refine understanding of which experiences are replayed and when.

**Why follow him:** Deep technical expertise on replay mechanisms; most directly relevant to the SWR literature.

---

### Mayank Mehta — UCLA
**Focus:** Reconciling rodent vs. primate hippocampus; "Hippocampus 2.0" theory; neocortex-hippocampal dialogue

**2024–2025:** "Hippocampus 2.0" — argues that human/primate hippocampal function is fundamentally different from rodent in important ways (more neocortical input during sleep; different replay dynamics). Important for those assuming rodent data directly translates to humans/AI.

**Why follow him:** Critical voice on limitations of rodent models for human memory; important for grounding AI design in human-relevant neuroscience.

---

### Tim Behrens — Oxford / UCL
**Focus:** Cognitive maps; relational memory; schema; hippocampal-prefrontal interactions; compositional representations

**2025 landmark paper:** *"Constructing future behavior in the hippocampal formation through composition and replay"* (Nature Neuroscience 28:1061, 2025)  
Key finding: Hippocampal replay binds known primitives into novel compositions for new environments.

**Key framework:** Cognitive maps generalize beyond space to any structured relationship space (social hierarchies, abstract concepts, values).

**Why follow him:** His compositional replay work is the most direct neuroscience justification for compositional AI memory architectures.

---

### Neil Burgess — UCL Institute of Cognitive Neuroscience
**Focus:** Spatial memory; theta phase precession; grid cells; entorhinal cortex; scene construction

**2024 landmark paper:** *"A generative model of memory construction and consolidation"* (Nature Human Behaviour 2024, with Spens)  
Key finding: Hippocampal replay trains a cortical generative model (VAE-like) for semantic compression + episodic detail.

**2024:** *"Theta phase precession supports memory formation and retrieval in humans"* (Nature Human Behaviour 2024, collaborative)  
Key finding: Human confirmation of theta phase precession during naturalistic memory.

**Why follow him:** Bridges rodent spatial memory and human episodic memory; his generative model framework is highly implementable.

---

### Alcino Silva — UCLA
**Focus:** Memory allocation; synaptic tagging and capture; engram biology; PFC-hippocampal interactions

**2026 landmark paper:** *"The prefrontal cortex controls memory organization in the hippocampus"* (Nature Neuroscience 2026)  
Key finding: vmPFC controls hippocampal ensemble overlap via MEC projections and neurogliaform cells in CA1 — determining whether new experiences are integrated with or separated from existing memories.

**Key concept:** Memory allocation — which neurons encode which memories is actively controlled, not random.

**Why follow him:** His work on vmPFC control of hippocampal encoding is critical for understanding how schemas gate memory storage.

---

### Susumu Tonegawa — MIT / RIKEN BRAC
**Focus:** Engram cells; fear memory circuits; memory manipulation; hippocampal engram biology

**2024–2026:** Dynamic engram deconstruction (collaborative with Autore, Pouget); brain-wide engram mapping.

**Key discovery:** Engram cells — the specific neurons that store a memory — can be optogenetically activated to induce recall or create false memories.

**Why follow him:** Foundational engram biology; directly relevant to understanding what a "memory trace" is biologically.

---

## Computational / Theoretical Labs

### Nathaniel Daw — Princeton Neuroscience Institute
**Focus:** Reinforcement learning + episodic memory; model-based vs. model-free decisions; hippocampal-RL interaction

**2025:** One-shot RL decisions + hippocampus (CCN 2025); RL-episodic memory integration.

**Key framework:** Episodic memory provides a form of model-based control — each retrieved episode is a "simulation" of a possible outcome. The brain uses episodic memories to do mental simulation before committing to an action.

**Why follow him:** Best computational treatment of how episodic memory serves decision-making — critical for AI agents that need to act on memories.

---

### Michael Frank — Brown University
**Focus:** Basal ganglia; dopamine; cortico-striatal loops; RL; working memory

**Key contribution:** Computational models of how basal ganglia implement RL, how dopamine signals RPE, and how prefrontal cortex actively maintains working memory via striatal gating.

**Why follow him:** His gating model of working memory (BG → PFC gating which information enters WM) is directly implementable in AI agents as a learned selection mechanism for what enters context.

---

### Marcelo Mattar — NYU / UCSD
**Focus:** Planning; cognitive maps; hippocampal replay for future planning; computational psychiatry

**2024 landmark paper:** *"A recurrent network model of planning explains hippocampal replay and human behavior"* (Nature Neuroscience 27:1340, 2024)  
Key finding: A meta-RL agent whose planning rollouts resemble hippocampal replay explains the variability in human decision times.

**Why follow him:** His planning model is the most concrete computational account of what replay is *for* — forward mental simulation.

---

### Joshua Jacobs — Columbia University
**Focus:** Human iEEG; spatial cognition in humans; phase precession in humans; hippocampal oscillations

**2024:** Direct human confirmation of theta phase precession during memory tasks.

**Why follow him:** Most direct human evidence for oscillatory memory mechanisms; bridges animal models to human neuroscience.

---

### Michael Kahana — University of Pennsylvania
**Focus:** Human iEEG; oscillatory correlates of memory encoding and retrieval; RAM (Restoring Active Memory) project

**RAM Project:** Large-scale iEEG study across hundreds of patients performing memory tasks. Has produced the most comprehensive dataset on human memory oscillations.

**Key finding:** Specific patterns of theta coherence and high-gamma power during encoding reliably predict which items will be remembered — forms the basis for closed-loop memory enhancement.

**Why follow him:** The largest human iEEG memory dataset; most rigorous quantification of ECoG correlates of memory.

---

### Mark Brandon — McGill University
**Focus:** Hippocampal-entorhinal circuits; memory encoding; spatial navigation; predictive coding

**2026 landmark paper:** *"Predictive coding of reward in the hippocampus"* (Nature 2026, with Yaghoubi, Kumar et al.)  
Key finding: CA1 neurons backward-shift their reward responses over weeks, implementing biological TD-learning.

**Why follow him:** His predictive coding framework for hippocampal function; directly relevant to reward-based memory prioritization.

---

### Adrien Peyrache — McGill University  
**Focus:** Hippocampal replay; sharp-wave ripples; sleep consolidation

**2025 landmark paper:** *"Replay without sharp wave ripples in a spatial memory task"* (Nature Communications 2025)  
Key finding: Replay and ripples are dissociable — replay can occur without ripples; ripples may serve a tagging/selection function.

**Why follow him:** Important corrective to the "ripples = consolidation" equation; more nuanced understanding of what triggers consolidation.

---

## Emerging Labs to Watch (2025–2026)

| Lab | Institution | Key Work |
|-----|-------------|---------|
| **Kamran Diba** | Univ. Michigan | SWR biology; ripple content analysis |
| **Shantanu Bhatt et al.** | Janelia | Orthogonalized state machine (Nature 2025) |
| **Bakermans / Warren** | Oxford/Behrens lab | Compositional replay (Nature Neuroscience 2025) |
| **Pouget / Morier / Autore** | UCLA + RIKEN | Engram deconstruction (Nature Neuroscience 2026) |
| **Yaghoubi / Nieto-Posadas** | McGill/Harvard | Predictive reward coding (Nature 2026) |
| **Deng et al.** | Multiple | cAMP sleep consolidation window (Neuron 2025) |

---

## Key Journals to Monitor

| Journal | Relevance |
|---------|-----------|
| **Nature Neuroscience** | Circuits, mechanisms, computational models |
| **Nature** | Landmark systems neuroscience |
| **Nature Human Behaviour** | Human iEEG/ECoG, cognitive neuroscience |
| **Neuron** | Cellular/circuit mechanisms |
| **Science** | Major discoveries (SWR selection 2024) |
| **Cell** | Molecular/cellular (CA3 BTSP 2024) |
| **Brain** | Human ECoG/iEEG |
| **eLife** | Rigorous open-access; strong computational neuroscience |
| **PLOS Computational Biology** | Computational models |
| **Nature Communications** | High-volume; many solid systems neuroscience papers |
| **Current Biology** | Fast communications of important findings |
| **NeurIPS / ICLR** | Computational neuroscience–AI bridge papers |

---

## Conferences

| Conference | What to Watch |
|-----------|--------------|
| **Society for Neuroscience (SFN)** annual | Largest; cutting-edge unpublished work |
| **Cosyne** (Computational and Systems Neuroscience) | Best computational + systems work |
| **NeurIPS** | Neuroscience-inspired AI; Hopfield models |
| **ICLR** | AI memory architectures |
| **CCN** (Cognitive Computational Neuroscience) | Bridge between cognitive science and computation |
| **Gordon Research Conferences** (Memory) | Small, high-level, unpublished work |
