# LoCoMo: Long-Context Multi-Session Benchmark

**Full name:** Evaluating Very Long-Term Conversational Memory of LLM Agents
**Origin:** Snap Research
**Website:** https://snap-research.github.io/locomo/

---

## What LoCoMo Tests

LoCoMo evaluates an agent's ability to recall and reason over very long multi-session conversations — the kind that span weeks or months of interactions with a single user.

### Dataset structure

- ~1,500–2,000 question-answer pairs per evaluation run
- Conversations span dozens to hundreds of sessions
- Questions are evenly split across five reasoning categories:

| Category | Description | Example |
|----------|-------------|---------|
| Single-hop | Direct factual retrieval | "Where does Alice work?" |
| Multi-hop | Chain two or more events | "What did Alice use before switching to Kubernetes?" |
| Temporal | Ordering and precedence | "Did Alice mention Python before or after joining Acme?" |
| Open-domain | Requires external world knowledge | "What are the pros of FastAPI that Alice would care about?" |
| Adversarial | Misleading/unanswerable questions | "What database does Alice use?" (never mentioned) |

### Evaluation metrics

- **LLM-as-judge score** — an LLM evaluates answer quality on 0–100 scale
- **ROUGE-L** — n-gram overlap for factual recall
- **F1** — token-level precision/recall
- **Adversarial accuracy** — correctly refusing to answer unanswerable questions

---

## LoCoMo's 2026 Limitations

LoCoMo was designed when 32k token context windows were state-of-the-art. Feeding an entire conversation history into a single LLM call wasn't possible. That constraint no longer holds:

- GPT-4o: 128k context
- Claude: 200k context
- Gemini 1.5 Pro / 2.0: 1M–2M context
- Llama 3.1 405B: 128k context

The challenge LoCoMo was designed to measure — "can the agent remember X from 50 sessions ago?" — can now be trivially solved by stuffing all 50 sessions into the context window.

**Implication:** LoCoMo scores for modern memory systems are artificially inflated compared to the original baseline. A "94% on LoCoMo" in 2026 doesn't mean what it meant in 2024.

---

## LoCoMo + LongMemEval_S

LongMemEval_S (Stanford) is a companion benchmark that covers:
- Memory across tool calls
- Preference inference from indirect signals
- Behavioral consistency over long periods

Both benchmarks are frequently cited together in 2025–2026 papers as the standard evaluation suite, though both have the same long-context window limitation.

---

## Running LoCoMo Evaluation

```python
# LoCoMo evaluation pipeline (simplified)
from locomo import LoCoMoDataset, evaluate_response

dataset = LoCoMoDataset.load("locomo_v2")

results = []
for example in dataset:
    # Build conversation history (many sessions)
    history = example.conversation_history
    
    # Your memory system retrieves relevant context
    retrieved = memory_system.retrieve(example.question, history=history)
    
    # Agent generates answer with retrieved context
    answer = agent.answer(
        question=example.question,
        context=retrieved,
        history=history[-5:]  # recent turns
    )
    
    # Evaluate
    score = evaluate_response(
        question=example.question,
        ground_truth=example.answer,
        predicted=answer,
        question_type=example.question_type
    )
    results.append(score)

print(f"Overall: {sum(results)/len(results):.1f}")
```

---

## Benchmark Scores (April 2026, selected systems)

| System | Overall Score | Single-hop | Multi-hop | Temporal | Adversarial |
|--------|--------------|------------|-----------|----------|-------------|
| GPT-4o (full context) | 91.2 | 95.1 | 88.3 | 89.7 | 82.0 |
| Claude 3.5 Sonnet (full context) | 90.8 | 94.0 | 87.9 | 90.2 | 81.4 |
| Mem0g + GPT-4o | 86.4 | 92.3 | 81.2 | 83.5 | 78.9 |
| Mem0 + GPT-4o | 84.1 | 91.0 | 79.8 | 80.2 | 76.4 |
| Letta + GPT-4o | 85.7 | 91.8 | 80.5 | 82.4 | 77.2 |
| Simple RAG + GPT-4o-mini | 71.3 | 82.1 | 63.4 | 68.9 | 64.2 |

*Note: "full context" systems are not memory systems — they put entire history in context, which is not feasible for real agents with thousands of sessions.*

---

## Sources

- [Evaluating Very Long-Term Conversational Memory (Snap Research)](https://snap-research.github.io/locomo/)
- [LoCoMo and LongMemEval_S Benchmarks (EmergentMind)](https://www.emergentmind.com/topics/locomo-and-longmemeval-_s-benchmarks)
- [State of AI Agent Memory 2026 (Mem0)](https://mem0.ai/blog/state-of-ai-agent-memory-2026)
- [Agent Memory Benchmark: A Manifesto (Hindsight/Vectorize)](https://hindsight.vectorize.io/blog/2026/03/23/agent-memory-benchmark)
