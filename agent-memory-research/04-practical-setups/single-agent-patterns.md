# Single-Agent Memory Patterns

Practical patterns for adding memory to a single-agent system, ordered from simplest to most complete.

---

## Pattern 1: Sliding Window (No Persistent Memory)

The simplest approach. Keep the last N messages in context. No external storage needed.

```python
from collections import deque

class SimpleContextWindow:
    def __init__(self, max_messages=20):
        self.history = deque(maxlen=max_messages)
    
    def add(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
    
    def get_context(self) -> list:
        return list(self.history)

# Usage
ctx = SimpleContextWindow(max_messages=20)
ctx.add("user", "My name is Alice")
ctx.add("assistant", "Hello Alice!")
messages = ctx.get_context()
```

**When to use:** Short sessions, no cross-session memory needed, zero latency requirement.
**Limitation:** Context evaporates at session end. Agent forgets everything.

---

## Pattern 2: Conversation Summarization

Compress old messages when context fills up, rather than dropping them.

```python
async def summarize_old_messages(messages: list, llm) -> str:
    """Compress the oldest half of messages into a summary."""
    to_summarize = messages[:len(messages)//2]
    
    prompt = f"""Summarize this conversation segment into 3-5 bullet points.
Preserve: names, preferences, decisions made, key facts mentioned.

Conversation:
{format_messages(to_summarize)}

Summary:"""
    
    return await llm.invoke(prompt)

async def manage_context(messages: list, max_tokens: int, llm) -> list:
    if count_tokens(messages) > max_tokens * 0.8:
        summary = await summarize_old_messages(messages, llm)
        # Replace old messages with summary
        return [
            {"role": "system", "content": f"[Earlier conversation summary]:\n{summary}"}
        ] + messages[len(messages)//2:]
    return messages
```

**When to use:** Long single sessions, moderate context length, no cross-session requirements.

---

## Pattern 3: Post-Session Memory Extraction (Recommended Baseline)

Extract and store key facts after each session ends. Retrieve them at the start of the next session.

```python
from mem0 import Memory

class AgentWithMemory:
    def __init__(self, user_id: str, llm):
        self.user_id = user_id
        self.llm = llm
        self.memory = Memory()
        self.session_messages = []

    def get_system_prompt(self) -> str:
        """Build system prompt with injected memories."""
        memories = self.memory.search(
            "user preferences, background, recent topics",
            user_id=self.user_id,
            limit=10
        )
        
        if not memories:
            return "You are a helpful assistant."
        
        memory_text = "\n".join([f"- {m['memory']}" for m in memories])
        return f"""You are a helpful assistant.
        
What you know about this user:
{memory_text}

Use this context naturally. Don't enumerate it unless relevant."""

    async def chat(self, user_message: str) -> str:
        # Build messages with memory context
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            *self.session_messages[-10:],  # last 10 turns
            {"role": "user", "content": user_message}
        ]
        
        response = await self.llm.invoke(messages)
        
        # Track session
        self.session_messages.append({"role": "user", "content": user_message})
        self.session_messages.append({"role": "assistant", "content": response})
        
        return response

    async def end_session(self):
        """Call this when user session ends."""
        if len(self.session_messages) >= 2:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.memory.add(self.session_messages, user_id=self.user_id)
            )
        self.session_messages = []
```

**When to use:** Most production use cases. Good balance of simplicity and memory quality.

---

## Pattern 4: Per-Turn Memory Retrieval

Instead of injecting all memories at session start, retrieve relevant memories on every turn. Better for large memory stores.

```python
class PerTurnMemoryAgent:
    def __init__(self, user_id, llm, memory_client):
        self.user_id = user_id
        self.llm = llm
        self.memory = memory_client
        self.session_messages = []

    async def chat(self, user_message: str) -> str:
        # Retrieve memories specific to THIS message
        relevant_memories = self.memory.search(
            user_message,
            user_id=self.user_id,
            limit=5
        )
        
        memory_block = ""
        if relevant_memories:
            facts = "\n".join([f"• {m['memory']}" for m in relevant_memories])
            memory_block = f"\n\nRelevant context about this user:\n{facts}"
        
        messages = [
            {"role": "system", "content": f"You are a helpful assistant.{memory_block}"},
            *self.session_messages[-6:],
            {"role": "user", "content": user_message}
        ]
        
        response = await self.llm.invoke(messages)
        
        self.session_messages.extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": response}
        ])
        
        # Optionally: write immediately (async, non-blocking)
        asyncio.create_task(
            self._async_store([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": response}
            ])
        )
        
        return response

    async def _async_store(self, messages):
        self.memory.add(messages, user_id=self.user_id)
```

**When to use:** Large memory stores (thousands of memories), where injecting all memories would overflow context.

---

## Pattern 5: Letta-Style Self-Managing Memory

Agent actively manages its own memory via tool calls. Full Letta implementation, or a lightweight equivalent:

```python
import json

MEMORY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "memory_search",
            "description": "Search your long-term memory for relevant information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_store",
            "description": "Save important information to long-term memory",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "What to remember"},
                    "importance": {"type": "number", "description": "0-1 scale"}
                },
                "required": ["content"]
            }
        }
    }
]

async def handle_tool_call(tool_name, args, memory_client, user_id):
    if tool_name == "memory_search":
        results = memory_client.search(args["query"], user_id=user_id)
        return json.dumps([r["memory"] for r in results])
    elif tool_name == "memory_store":
        memory_client.add(
            [{"role": "assistant", "content": args["content"]}],
            user_id=user_id
        )
        return "Stored."
```

**When to use:** When you want the agent to decide what's worth remembering. Requires a capable model (GPT-4o or better).

---

## Decision Tree

```
Do you need memory across sessions?
├── No → Pattern 1 (sliding window) or Pattern 2 (summarization)
└── Yes
    │
    Do you have > 1000 memories per user?
    ├── No → Pattern 3 (post-session extraction, inject all at start)
    └── Yes
        │
        Do you want the agent to control its own memory?
        ├── Yes → Pattern 5 (self-managing, or use Letta)
        └── No → Pattern 4 (per-turn retrieval)
```

---

## Sources

- [A Practical Guide to Memory for Autonomous LLM Agents (TDS)](https://towardsdatascience.com/a-practical-guide-to-memory-for-autonomous-llm-agents/)
- [A memory architecture for agentic system (GitHub Gist)](https://gist.github.com/spikelab/7551c6368e23caa06a4056350f6b2db3)
- [Agent Memory: How to Build Agents that Learn and Remember (Letta)](https://www.letta.com/blog/agent-memory)
- [Mem0: Building Production-Ready AI Agents (arXiv 2504.19413)](https://arxiv.org/abs/2504.19413)
