# MemoryBench: Continual Learning and User Feedback Benchmark

**Paper:** arXiv 2510.17281
**OpenReview:** https://openreview.net/forum?id=wU4Tjlzg3h

---

## What Problem MemoryBench Solves

Prior benchmarks (LoCoMo, LongMemEval) focus on **reading comprehension from long documents** — the agent has all the text and needs to find the answer. They don't test whether an agent can **learn from user feedback over time** — which is the actual use case for personalized AI assistants.

MemoryBench specifically evaluates:

1. **Learning from explicit corrections** — user says "Actually, that's wrong, I prefer X"
2. **Learning from implicit feedback** — user prefers shorter answers (revealed through behavior)
3. **Retaining learned preferences** — does the agent remember what it learned from session 1 in session 10?
4. **Forgetting correctly** — does the agent forget preferences the user has changed?
5. **Cross-domain generalization** — does a learned preference generalize ("be concise" → applies to code reviews too)

---

## Dataset Structure

MemoryBench uses a **user feedback simulation framework**:

```
Phase 1: Baseline sessions (agent has no memory)
Phase 2: Feedback sessions (user provides explicit corrections/preferences)
Phase 3: Evaluation sessions (does agent apply learned preferences?)
Phase 4: Update sessions (user changes some preferences)
Phase 5: Re-evaluation (did agent correctly update?)
```

### Coverage

- **Multiple domains:** coding assistance, writing help, customer support, research
- **Multiple languages:** English, Chinese, Spanish, French (partial)
- **Multiple feedback types:** explicit ("be more concise"), implicit (user edits agent output), behavioral (user ignores certain types of responses)

---

## Key Metrics

| Metric | Description |
|--------|-------------|
| Learning Rate | % of explicit corrections correctly applied in next session |
| Retention Score | % of learned preferences still applied after 10+ sessions |
| Correct Forgetting | % of outdated preferences correctly dropped after update |
| Generalization | % of preferences correctly applied in new domains |
| Cross-domain | % of domain-specific preferences correctly *not* applied cross-domain |

---

## What MemoryBench Reveals

### Most systems are bad at correct forgetting

Systems that score 85%+ on learning and retention typically drop to 60–70% on correct forgetting. They remember that you preferred X, but when you change your mind, the old preference competes with the new one.

### Generalization is inconsistently implemented

User says: "I like concise answers" in a coding context.
Question: Should the agent also be concise in writing tasks?

There's no consensus in the field. Some systems generalize aggressively (leading to over-applied preferences), some don't generalize at all (treating each domain as isolated).

### Implicit feedback is mostly ignored

Most memory systems only capture explicit user statements. Implicit signals (the user never accepts verbose responses, always edits out the introduction paragraph) require a feedback loop that almost no production systems implement as of 2026.

---

## MemoryBench Scores (Selected Systems, 2026)

| System | Learning | Retention | Correct Forgetting | Generalization |
|--------|----------|-----------|-------------------|----------------|
| Letta + GPT-4o | 81% | 78% | 64% | 59% |
| Mem0 + GPT-4o | 83% | 81% | 67% | 61% |
| LangGraph + custom | 74% | 70% | 58% | 52% |
| Basic RAG + GPT-4o | 52% | 48% | 71%* | 38% |

*Basic RAG scores high on "correct forgetting" because it doesn't retain much to begin with.

---

## Running MemoryBench

```python
from memorybench import MemoryBenchDataset, MemoryBenchEvaluator

dataset = MemoryBenchDataset.load("v1.0")
evaluator = MemoryBenchEvaluator()

for user_scenario in dataset:
    # Initialize fresh agent for this user
    agent = MyAgent(user_id=user_scenario.user_id)
    
    # Run through all phases
    for phase in user_scenario.phases:
        for turn in phase.turns:
            response = agent.chat(turn.input)
            evaluator.record(
                phase=phase.type,
                input=turn.input,
                expected=turn.expected_behavior,
                actual=response,
                user_id=user_scenario.user_id
            )

scores = evaluator.compute_scores()
print(scores)
```

---

## Sources

- [MemoryBench: A Benchmark for Memory and Continual Learning in LLM Systems (arXiv 2510.17281)](https://arxiv.org/html/2510.17281v1)
- [MemoryBench OpenReview](https://openreview.net/forum?id=wU4Tjlzg3h)
- [Memory for Autonomous LLM Agents: Mechanisms, Evaluation, Frontiers (arXiv 2603.07670)](https://arxiv.org/html/2603.07670v1)
