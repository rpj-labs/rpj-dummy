# Letta (formerly MemGPT): OS-Inspired Agent Memory

**Repository:** https://github.com/letta-ai/letta
**Stars (April 2026):** ~15,000+
**Language:** Python
**License:** Apache 2.0

---

## History

- **MemGPT** was the original research paper (2023) introducing the LLM-as-OS memory paradigm
- **Letta** is the production framework that replaced the MemGPT open-source project
- MemGPT now refers specifically to the research paper's agent design pattern
- The company (Letta) maintains both the open-source framework and a managed cloud platform

---

## Core Concept: LLM as Operating System

Letta treats the LLM context window as RAM. Just as an OS manages memory by moving pages between RAM and disk, a Letta agent actively moves content between:

- **Core memory** (always in context, like RAM) — ~4K tokens
- **Archival memory** (external searchable store, like disk) — unlimited
- **Recall memory** (conversation history, like an L2 cache) — unlimited, retrieved by relevance

The agent *controls its own memory* using built-in memory tool calls.

---

## Memory Types in Letta

### Core Memory Blocks

Core memory is divided into named blocks that are always injected into the system prompt:

```python
# Core memory block structure
{
    "human": "Name: Alice. Works at Acme. Prefers brief answers.",
    "persona": "I am a helpful coding assistant with deep Python expertise.",
    "scratchpad": "<agent writes notes here mid-reasoning>"
}
```

Blocks have configurable token limits and can be read and rewritten by the agent using `core_memory_replace()`.

### Archival Memory

Archival memory is an external vector store. The agent searches and writes to it:

```python
# Agent-callable tool
memory_insert("User mentioned they're switching from AWS to GCP next quarter")
results = memory_search("user's cloud provider preferences")
```

### Recall Memory

The full conversation history, stored externally and searchable:

```python
# Agent-callable tool
messages = conversation_search("what did we discuss about the API redesign")
```

---

## Memory Blocks: The Key Innovation (2025)

Memory Blocks were the major 2025 architectural addition. Key properties:

- **Shared blocks**: Multiple agents can reference the same memory block. One agent updates it; all agents see the update.
- **Scoped blocks**: Blocks can be scoped to a user, a thread, or a group of agents
- **Programmatic blocks**: External systems can read/write blocks via the Letta API, bridging agent memory with external systems

This enables the Conversations API (January 2026): agents maintain a shared "human" memory block across parallel sessions with the same user, so context isn't siloed per thread.

---

## 2025–2026 Feature Timeline

| Date | Feature |
|------|---------|
| Oct 2025 | Letta Evals: open-source evaluation framework for stateful agents |
| Dec 2025 | Letta Code: #1 model-agnostic on Terminal-Bench coding evaluation |
| Dec 2025 | Programmatic tool calling: agents generate their own workflows |
| Jan 2026 | Conversations API: shared memory across parallel sessions |
| Q1 2026 | Multi-agent coordination via shared memory blocks |

---

## Practical Setup

### Installation

```bash
pip install letta
letta server  # starts local server on port 8283
```

### Creating an agent with memory

```python
from letta import create_client

client = create_client()

agent = client.create_agent(
    name="my-assistant",
    memory=BasicBlockMemory(
        blocks=[
            Block(label="human", value="Name: Bob. Software engineer at Stripe."),
            Block(label="persona", value="I am a concise technical assistant."),
        ]
    ),
    llm_config=LLMConfig(model="gpt-4o", model_endpoint_type="openai"),
    embedding_config=EmbeddingConfig(
        embedding_model="text-embedding-3-small",
        embedding_endpoint_type="openai"
    )
)
```

### Sending a message

```python
response = client.send_message(
    agent_id=agent.id,
    message="What do you remember about me?",
    role="user"
)
print(response.messages[-1].text)
```

### Reading memory

```python
memory = client.get_core_memory(agent_id=agent.id)
print(memory.get_block("human").value)
```

---

## Deployment Options

| Option | Best For | Notes |
|--------|----------|-------|
| Letta local server | Development, single-user | Free, full control |
| Self-hosted | Teams | Docker Compose setup, PostgreSQL backend |
| Letta Cloud | Production | Managed, scalable, SLA |

### Docker self-hosted setup

```yaml
# docker-compose.yml
services:
  letta:
    image: letta-ai/letta:latest
    ports:
      - "8283:8283"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - letta_data:/root/.letta
  postgres:
    image: postgres:16
    environment:
      - POSTGRES_DB=letta
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
```

---

## When to Choose Letta

**Choose Letta when:**
- You need agent-controlled memory (agent decides what to remember and forget)
- You have long-running, persistent agent personas
- You want multi-agent shared state via memory blocks
- You need human-in-the-loop interrupts and time-travel debugging

**Don't choose Letta when:**
- You just need to add memory to an existing agent (use Mem0 instead)
- Your agent is stateless by design
- You need sub-100ms retrieval (Letta adds tool-call overhead)

---

## Sources

- [MemGPT is now part of Letta](https://www.letta.com/blog/memgpt-and-letta)
- [Agent Memory: How to Build Agents that Learn and Remember (Letta)](https://www.letta.com/blog/agent-memory)
- [Memory Blocks: The Key to Agentic Context Management (Letta)](https://www.letta.com/blog/memory-blocks)
- [GitHub: letta-ai/letta](https://github.com/letta-ai/letta)
- [Benchmarking AI Agent Memory: Is a Filesystem All You Need? (Letta)](https://www.letta.com/blog/benchmarking-ai-agent-memory)
- [Stateful AI Agents: A Deep Dive into Letta (MemGPT) Memory Models (Medium)](https://medium.com/@piyush.jhamb4u/stateful-ai-agents-a-deep-dive-into-letta-memgpt-memory-models-a2ffc01a7ea1)
