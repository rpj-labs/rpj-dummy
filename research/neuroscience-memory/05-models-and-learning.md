# Computational Models of Memory (2024–2026)

---

## 1. The Orthogonalized State Machine

### Key Paper
**Drieu, Bhatt, Chen et al. (Janelia Research Campus), Nature, February 2025**  
*"Learning produces an orthogonalized state machine in the hippocampus"*  
DOI: 10.1038/s41586-024-08548-w

### Experimental Setup
- Two-photon calcium imaging of thousands of CA1 neurons
- Mice learned two **similar virtual tracks** (same geometry, different visual cues)
- Tracked population dynamics over the entire learning process

### Key Findings

**What happens during learning:**
```
Early learning:
    Similar tracks → Similar, overlapping CA1 activity patterns
    Recall poor, interference high

Progressive learning:
    Activity patterns DECORRELATE across tracks
    Each track develops a distinct trajectory through neural state space

Late learning (expert):
    Activity resembles an orthogonalized state machine
    Each position = distinct state; transitions = deterministic
    Minimal overlap between tracks
```

**Best Model:** Clone-Structured Causal Graph (CSCG)

- The CSCG uniquely replicates both the **end-state** AND the step-by-step **learning trajectory**
- Other models (place cell models, RNNs) only fit the end-state
- Key property: CSCG infers *hidden discrete states* from continuous sensory observations (like an HMM with cloned states)

### What is a CSCG?

```
Standard HMM:
    Each observation → one hidden state

Clone-Structured Causal Graph (CSCG):
    Each position on Track A → unique hidden state (clone of the generic position state)
    Each position on Track B → different unique hidden state (another clone)
    
    Clones allow the same sensory observation to be associated with
    different hidden states depending on context (which track)
    
    This is how the brain orthogonalizes similar experiences:
    not by changing sensory representations, but by inferring
    different hidden states for the same sensory input
```

### Implications

1. **Hippocampal learning = latent state inference**, not just pattern association
2. The brain infers hidden discrete states from continuous sensory observations
3. Progressive orthogonalization is the signature of this inference process
4. CA1 represents the **posterior over hidden states**, not sensory features directly

### AI Design Principle
Memory should be organized as a **learned state machine** (CSCG or HMM), not a flat lookup table. Each stored experience corresponds to a latent state. Similar experiences are initially assigned similar latent states; with experience, they are progressively orthogonalized. This provides:
- Context-dependent retrieval (same cue → different memory depending on which state you're in)
- Interference prevention (similar experiences don't overwrite each other)
- Principled generalization (sharing states where appropriate, separating where not)

---

## 2. Recurrent Network Models of Planning and Replay

### Key Paper
**Jensen, Hennequin, Mattar, Nature Neuroscience, 2024**  
*"A recurrent network model of planning explains hippocampal replay and human behavior"*  
DOI: 10.1038/s41593-024-01675-7

### Model Architecture
- Meta-RL agent with a recurrent controller (PFC analog)
- Policy "rollout" planning: agent mentally simulates future trajectories using stored hippocampal maps
- Rollout patterns in the model resemble hippocampal replay timing and content

### Key Predictions (Confirmed by Data)
1. Replay duration is correlated with decision difficulty (more planning needed = more replay)
2. Replay biased toward transitions leading to reward
3. Human thinking times exhibit the same variability structure as the model's planning times
4. PFC inactivation disrupts both planning and subsequent replay content

### AI Design Principle
**Before acting in a novel situation, simulate using stored memories.** The agent's decision loop should be:
```
1. Perceive current state
2. Retrieve relevant memories (hippocampal query)
3. Mentally simulate possible futures (rollout using retrieved memories)
4. Select action based on simulated outcomes
5. Act → observe outcome → update memories
```
The number of simulation steps should scale with uncertainty/difficulty.

---

## 3. Compositional Memory Models

### Key Paper
**Bakermans, Warren, Whittington, Behrens, Nature Neuroscience 28:1061, 2025**  
*"Constructing future behavior in the hippocampal formation through composition and replay"*

### Core Insight: Primitive Building Blocks
The hippocampus doesn't store entire experiences as monolithic memories. Instead:
- **Primitives** = elementary behavioral/spatial motifs (e.g., "turn left at junction," "navigate corridor segment")
- **Episodes** = bound compositions of primitives in specific arrangements
- **New environments** = recognized as novel *compositions* of familiar primitives

### Evidence
- Replay events from newly discovered landmarks induce **new remote firing fields** at corresponding positions in known environments
- This is the mechanistic signature of binding: replaying landmark L in new context C binds L to C using the same neural "slot" as L's familiar context
- Agents immediately navigate novel environments optimally by composing familiar primitives — no new gradient learning needed

### Structured Successor Representation
The SR (Dayan, 1993) represents expected future state occupancy. Compositional extensions of SR can represent:
- SR_A + SR_B (adding two learned environments)
- SR_A ⊗ SR_B (product: navigating A while tracking state in B, e.g., social hierarchies × physical spaces)

### AI Design Principle
```
Store memories as compositions of reusable primitives:
- Primitive: a retrievable unit of knowledge that applies across contexts
- Episode: a specific binding of primitives (which primitive, in what order, with what parameters)
- Novel situation: retrieve relevant primitives, compose them in new configuration

Example for an AI coding agent:
- Primitive: "call an API with authentication"
- Primitive: "handle rate limiting with exponential backoff"
- New task: call this specific new API → compose both primitives in new parameter setting
```

---

## 4. Predictive Sequence Learning Models

### Hippocampal Predictive Autoencoder (Neuron, 2024)

Architecture based on hippocampal anatomy:
```
Sensory input
    ↓
Entorhinal Cortex (encoder)
    ↓         ↓
DG (sparse)   CA1 (target)
    ↓
CA3 (self-supervised RNN)
    - Learns to predict next EC input
    - Recurrent weights = sequence memory
    - Attractor states = compressed sequence representations
    ↓
CA1 (comparator: CA3 prediction vs. EC actual input)
    ↓
Output / novelty signal
```

CA3 is trained as a **sequence predictor**, not just a pattern associator. This is why replay is temporally structured (forward and reverse replay).

### Successor Representation

The SR provides a middle ground between model-free (Q-values) and model-based (full transition model) RL:

```
M(s, s') = E[Σ_t γ^t 𝟙(s_t = s') | s_0 = s]
```

- M encodes expected future occupancy: "if I start at state s, how much time do I expect to spend at s'?"
- Hippocampal place cells have been proposed to encode the SR
- **2024–2025 refinements:** DR (Discount Representation) incorporates explicit predictions of reward; predictive place cells represent future positions (like SR's forward projection)

### Time Cells

Time cells fire at specific delays after a triggering event, creating a temporal scaffold:
```
Event occurs at t=0
    Cell 1 fires at t=0.5s
    Cell 2 fires at t=1.0s
    Cell 3 fires at t=1.5s
    ...
    Cell N fires at t=Ns
```

This "temporal map" encodes *when* something will happen, supporting temporal sequence memory and delay conditioning. Eichenbaum (legacy) established this in hippocampus; 2024–2025 work shows time cells throughout mPFC, striatum, and cerebellum.

### AI Design Principle
Time cells = learned positional embeddings with temporal resolution. For agents that need to track "how long ago" something happened or "how long until" something will happen, learnable temporal position codes are critical.

---

## 5. Entorhinal Temporal Context Model

### Origin: Howard, Kahana, & colleagues

The **Temporal Context Model (TCM)** proposes that episodic memory retrieval is governed by a slowly drifting temporal context signal. Items encoded in similar temporal contexts are more likely to cluster in recall (temporal clustering effect).

### 2024–2025 Neural Evidence
- Human iEEG shows theta phase coherence between MTL and lateral temporal cortex drifts slowly across an episode
- Rate of drift correlates with subjective "event boundary" detection
- Sudden context resets (event boundaries) = LC-NE reset of hippocampal representations

### Continuous Attractor Dynamics for Time
MEC grid cells implement a continuous attractor network for spatial position. The same mechanism may encode **temporal position** via theta/gamma dynamics:
- Position in time = integration of temporal inputs
- Context signal = slowly decaying trace of recent inputs

---

## 6. Active Learning and Prediction Error

### Prediction Error → Memory Prioritization

**From Neuron 2025 (Davachi lab) and related 2024–2025 work:**

| PE Level | Memory Response | Neural Mechanism |
|----------|----------------|-----------------|
| None (expected) | No update; existing trace strengthened | Hebbian LTP at existing synapses |
| Small PE | Memory *updating* (revise existing trace) | CA1 mismatch signal → local plasticity in encoding CA3 attractor |
| Large PE | New episode creation | LC-NE reset; DG remapping; new CA3 attractor initialized |
| Very large PE | Memory suppression (trauma, stress) | Amygdala → DG/CA3 suppression via inhibitory interneurons |

### AI Design Principle: PE-Weighted Memory Writes

```python
# Pseudocode for PE-weighted memory writing
def write_memory(new_experience, context):
    retrieved = retrieve_most_similar(new_experience)
    pe = compute_prediction_error(new_experience, retrieved)
    
    if pe < low_threshold:
        # Expected: strengthen existing trace
        update_existing_memory(retrieved, new_experience, weight=0.1)
    elif pe < high_threshold:
        # Small surprise: update existing memory
        update_existing_memory(retrieved, new_experience, weight=0.5)
    else:
        # Large surprise: create new episode
        create_new_episode(new_experience, context)
        trigger_event_boundary()
```

---

## 7. Schema-Based Memory Models

### Schemas as Neocortical Priors
A schema is a structured body of knowledge that organizes and interprets new information:
- Physical schemas: kitchen has appliances, sink, counters
- Narrative schemas: meeting has greeting, agenda, discussion, conclusion
- Role schemas: doctor has stethoscope, lab coat, asks about symptoms

### 2024–2025 Findings
- vmPFC stores schemas and projects them to hippocampus during encoding
- New information that **fits an existing schema** is encoded faster, with less hippocampal activity (schema-assimilation)
- New information that **violates a schema** triggers stronger hippocampal encoding, creating a distinct memory trace
- Over time, the hippocampus can update the schema itself (systems reorganization, Neuron 2025)

### AI Design Principle
Schema = system prompt / template / type definition. When new information arrives:
1. Check if it fits existing schemas (vmPFC contextual gating)
2. If fits: compress into schema + delta (only store the difference)
3. If doesn't fit: store verbatim as new episodic memory + potentially update schema

---

## 8. Sleep Replay and Memory Models

### Content of Replay

What gets replayed is **not random**:
1. **Novel sequences** replayed more than familiar (novelty prioritization)
2. **Reward-adjacent experiences** replayed more (value prioritization)
3. **Sequences that violated expectations** replayed more (PE prioritization)
4. **Sequences in reverse order** also replayed (reverse replay for credit assignment)

### Reverse Replay as Credit Assignment

Reverse replay (running a sequence backward during SWRs) provides a biological implementation of **backward induction** (like value iteration in RL):
- Forward replay: plan future paths
- Reverse replay: assign credit backward from reward to earlier states

### AI Design Principle
During consolidation passes, replay should be:
- **Selective:** Not all memories; prioritize by novelty + value + PE
- **Bidirectional:** Forward (predict next) AND backward (assign credit to earlier states)
- **Compressed:** Replay at higher-than-real-time speed (biological: 6–20x; AI: compress multi-step sequences into single operations)
