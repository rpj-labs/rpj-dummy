# Context Engineering: Memory Management as Context Optimization

"Context engineering" emerged in 2025–2026 as a broader framing for the problem: the goal isn't just to store and retrieve memories, it's to put exactly the right information in the LLM's context at exactly the right time.

---

## What Context Engineering Is

Traditional view: "How do we store and retrieve memories?"
Context engineering view: "What should be in the context window, and why?"

Memory is one input to context. Others include:
- Tool results
- System instructions
- In-progress reasoning
- Retrieved documents
- Current conversation

Context engineering is the discipline of managing all of these together, with memory as the primary long-term component.

---

## ACE: Agentic Context Engineering (2026)

**Paper:** Described in ICLR 2026 MemAgents Workshop

ACE proposes a three-agent loop for context management:

```
┌──────────────────────────────────────────────────┐
│                  ACE Loop                        │
│                                                  │
│  [Generator]                                     │
│    - Produces main agent response/trajectory     │
│    - Works with current context                  │
│    - Does NOT write to memory                    │
│          │                                       │
│          ▼                                       │
│  [Reflector]                                     │
│    - Reviews Generator's output                  │
│    - Identifies: errors, gaps, key learnings     │
│    - Flags what should be committed to memory    │
│          │                                       │
│          ▼                                       │
│  [Curator]                                       │
│    - Receives Reflector's analysis               │
│    - Validates against existing "context playbook"│
│    - Resolves conflicts, prevents drift          │
│    - Has sole authority to write to memory       │
└──────────────────────────────────────────────────┘
```

The **context playbook** is a living document — a structured set of facts, preferences, and guidelines that the Curator maintains. It's injected into every Generator call as the "system context."

### Results

Factory's evaluation over 36,000 real engineering session messages showed:
- Merging new summaries into persistent state produces higher accuracy, completeness, and continuity vs. replacing with new summaries
- Agents with playbooks solve repeated task patterns ~40% faster on second occurrence

---

## Anthropic's Compaction API (early 2026)

Anthropic shipped `compact-2026-01-12` — a production compaction API that automatically manages context window usage:

```python
from anthropic import Anthropic

client = Anthropic()

# Enable compaction: when context fills up, automatically summarize
# and compress old turns before hitting the context limit
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=4096,
    system="You are a helpful assistant.",
    messages=conversation_history,
    # Compaction config:
    betas=["extended-thinking-2025-01-01"],
    extra_headers={
        "anthropic-beta": "compact-2026-01-12"
    }
)
```

The compaction API:
- Works across Claude API, AWS Bedrock, Google Vertex, Microsoft Foundry
- Supports Zero Data Retention (ZDR) — compressed context doesn't persist on Anthropic's servers
- Applies **anchored iterative summarization** — maintains key facts across compressions

### ACON: Adaptive Context Compression (Feb 2026)

ACON (Adaptive Context compressiON) is a research approach that reduces memory usage 26–54% while preserving 95%+ task accuracy:

```python
# ACON-style compression
def acon_compress(messages: list, target_tokens: int, llm) -> list:
    """
    Adaptively compress messages to fit target_tokens.
    Uses failure-driven compression: only compresses when performance would degrade.
    """
    current_tokens = count_tokens(messages)
    
    if current_tokens <= target_tokens:
        return messages
    
    # Identify which messages are "anchor" messages (high importance)
    # vs. "compressible" messages (low importance)
    anchors, compressible = classify_messages(messages, llm)
    
    # Compress only compressible messages
    compressed = []
    for msg in compressible:
        if count_tokens(compressed) + count_tokens(msg) > target_tokens * 0.8:
            # Summarize this message instead of including it
            compressed.append(summarize_message(msg, llm))
        else:
            compressed.append(msg)
    
    return anchors + compressed  # anchors always included in full
```

---

## Memory as a Context Budget Problem

With memory retrieval adding context, and the LLM having a finite context window, memory management becomes a budget allocation problem:

```
Total context budget: 128,000 tokens

Allocation:
- System prompt: ~1,000 tokens (fixed)
- Current conversation: ~5,000 tokens (variable, grows)
- Recent tool results: ~10,000 tokens (variable)
- Retrieved memories: X tokens (our variable to optimize)
- Reserved for response: 4,096 tokens (fixed)

Available for memories: 128,000 - 1,000 - 5,000 - 10,000 - 4,096 = 107,904
But if we use them all for memories, no room for conversation to grow.

Practical allocation: 8,000-15,000 tokens for retrieved memories
At 200 tokens per memory chunk = 40-75 memories per call
```

This is why simply "retrieving more memories" doesn't always help — you have a hard ceiling.

---

## Redis-Based Context Compression (2026 Pattern)

Redis is increasingly used not just for KV storage but for the full context pipeline:

```python
# Pattern: Redis as context state manager
import redis
import json

r = redis.Redis()

def get_compressed_context(session_id: str, new_message: str) -> list:
    # Get current context
    context = json.loads(r.get(f"ctx:{session_id}") or "[]")
    context.append({"role": "user", "content": new_message})
    
    # If getting long, compress
    if count_tokens(context) > 50_000:
        # Summarize oldest 50% of messages
        old, recent = context[:len(context)//2], context[len(context)//2:]
        summary = summarize(old)
        context = [{"role": "system", "content": f"[Earlier: {summary}]"}] + recent
    
    # Save updated context with TTL
    r.setex(f"ctx:{session_id}", 7200, json.dumps(context))  # 2-hour TTL
    
    return context
```

---

## The Long Context Window vs. Memory Debate (2026 Status)

The central debate: with 1M+ token context windows, do you even need external memory?

**Arguments for "just use long context":**
- No retrieval latency
- No retrieval errors (wrong memories retrieved)
- Perfect recall of everything in context

**Arguments for "still need external memory":**
- Cost: 1M tokens per request × millions of users = prohibitive
- Cross-session context: you can't keep a 2-year conversation history in one context
- Multi-session, multi-thread: a user with 50 concurrent sessions can't have each one see all other sessions' context
- Structured access: "what's the user's current employer?" requires semantic search, not a 1M-token needle-in-a-haystack

**2026 consensus:** Use long context *within sessions* (stop mid-session summarization). Use external memory *across sessions*. The two are complementary.

---

## Sources

- [AI Agent Context Compression: Strategies for Long-Running Sessions (Zylos Research)](https://zylos.ai/research/2026-02-28-ai-agent-context-compression-strategies)
- [Memory for AI Agents: A New Paradigm of Context Engineering (The New Stack)](https://thenewstack.io/memory-for-ai-agents-a-new-paradigm-of-context-engineering/)
- [ICLR 2026 Workshop: MemAgents](https://openreview.net/pdf?id=U51WxL382H)
- [Building smarter AI agents: AgentCore long-term memory deep dive (AWS)](https://aws.amazon.com/blogs/machine-learning/building-smarter-ai-agents-agentcore-long-term-memory-deep-dive/)
- [How to Build AI Agents with Redis Memory Management](https://redis.io/blog/build-smarter-ai-agents-manage-short-term-and-long-term-memory-with-redis/)
