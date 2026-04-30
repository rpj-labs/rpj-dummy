# AMA-Bench: Agentic Long-Horizon Memory Benchmark

**Full name:** AMA-Bench: Evaluating Long-Horizon Memory for Agentic Applications
**Paper:** arXiv 2602.22769
**Focus:** Memory across multi-step tool calls and agentic tasks (not just conversations)

---

## Why AMA-Bench Exists

LoCoMo and LongMemEval test conversational memory — the agent reads and recalls from dialogue. AMA-Bench tests something different: **memory across agentic task sequences** where the agent uses tools, writes files, browses web pages, and executes code over many steps.

In agentic tasks, memory must:
- Track the state of long multi-step workflows
- Remember what was tried and what failed
- Apply learned procedures to new but similar tasks
- Build up a knowledge base from research steps

None of the existing conversation benchmarks test this well.

---

## AMA-Bench Task Categories

### 1. Tool-Call Memory

Does the agent remember the results of earlier tool calls within a long task?

```
Step 1: agent calls search("FastAPI authentication docs") → stores results
Step 20: agent needs to implement auth → should recall step 1 results
```

Without memory, the agent re-searches at step 20. With memory, it retrieves and reuses.

### 2. Document Research Memory

Agent reads multiple documents over multiple steps. Can it synthesize knowledge built across documents?

```
Step 1-5: reads 5 papers on Kubernetes networking
Step 12: asked to recommend a networking plugin → must synthesize all 5
```

### 3. Preference Application in Multi-Step Decisions

User preference ("always use TypeScript") should propagate through all sub-decisions in a complex task.

```
Task: "Build a REST API"
Sub-decisions: language choice, framework, test setup, CI config
Preference: "use TypeScript" → should affect all sub-decisions, not just the first
```

### 4. Error Memory

Does the agent remember and avoid mistakes it made earlier in the task?

```
Step 8: tried approach X, got error "incompatible versions"
Step 15: same approach tempting again → should recall the failure and skip it
```

---

## Dataset Statistics

- 200 long-horizon agentic tasks
- Average task length: 35 steps
- Max task length: 150 steps
- Tools available: web search, code execution, file read/write, database query
- Domains: software engineering, data analysis, research synthesis

---

## Key Findings (2026)

### Finding 1: Episodic recall is the biggest gap

Agents are good at retaining user preferences (semantic memory) but poor at episodic recall in tool-call sequences. After 15+ steps, most agents forget what tool calls were made earlier.

### Finding 2: Procedural memory enables 2x speedup

Agents with procedural memory (stored task playbooks from prior tasks) complete similar tasks ~2x faster than agents without, because they skip the exploration phase.

### Finding 3: No system solves error memory well

The worst-scoring category for all systems. Agents rarely remember specific errors from earlier in a task and often retry the same failed approach.

### Finding 4: Memory injection timing matters

Injecting all memories at task start is worse than retrieving memories contextually during the task. The relevant memory at step 30 is different from the relevant memory at step 5.

---

## AMA-Bench Scores (April 2026)

| System | Tool-Call | Doc Research | Preference | Error Memory | Overall |
|--------|-----------|-------------|------------|--------------|---------|
| Letta + Claude Opus | 71% | 68% | 82% | 41% | 65% |
| Mem0 + GPT-4o | 65% | 72% | 79% | 38% | 63% |
| LangGraph + store | 58% | 61% | 74% | 32% | 56% |
| AgeMem (RL-optimized) | 76% | 74% | 84% | 52% | 72% |
| No memory baseline | 41% | 38% | 61% | 24% | 41% |

**AgeMem** (Agentic Memory, RL-optimized, discussed in emerging-research folder) is the current state-of-the-art on AMA-Bench.

---

## Sources

- [AMA-Bench: Evaluating Long-Horizon Memory for Agentic Applications (arXiv 2602.22769)](https://arxiv.org/html/2602.22769v1)
- [Memory for Autonomous LLM Agents: Mechanisms, Evaluation, Frontiers (arXiv 2603.07670)](https://arxiv.org/html/2603.07670v1)
- [Agent Memory Benchmark: A Manifesto (Hindsight)](https://hindsight.vectorize.io/blog/2026/03/23/agent-memory-benchmark)
- [Supermemory Research: State-of-the-Art Agent Memory](https://supermemory.ai/research/)
