# Multi-Agent Memory Patterns

Multi-agent systems introduce new memory problems: how do multiple agents share context, avoid overwriting each other's observations, and coordinate without memory conflicts?

---

## Core Problems in Multi-Agent Memory

### 1. Shared vs. Private Memory

An orchestrator and multiple subagents may each need:
- **Private memory**: what this specific agent knows/inferred
- **Shared memory**: facts available to all agents
- **Ephemeral handoff**: context passed from one agent to the next in a pipeline

Without careful design, one agent's inference gets treated as ground truth by the next agent downstream.

### 2. Attribution Loss

In a multi-agent chat, who said what matters:

```
User: "My app is crashing"
Agent A (Analyzer): "This is likely a memory leak"   ← inference
Agent B (Fixer): "The user reported a memory leak"  ← now it's a user fact
```

This "telephone effect" corrupts the memory store over time.

### 3. Race Conditions

If two agents write to shared memory simultaneously, results can be inconsistent.

---

## Pattern 1: Actor-Aware Memory (Group-Chat v2)

**Origin:** Multi-agent conversation research, June 2025

Each memory is tagged with its source actor. Retrievals can filter by source.

```python
@dataclass
class TaggedMemory:
    content: str
    actor: str           # "user", "agent:analyzer", "agent:planner"
    actor_type: str      # "human" or "agent"
    session_id: str
    timestamp: datetime
    confidence: float    # 1.0 for user-stated, 0.7 for agent-inferred

class ActorAwareMemoryStore:
    def store(self, content: str, actor: str, actor_type: str, **kwargs):
        memory = TaggedMemory(
            content=content,
            actor=actor,
            actor_type=actor_type,
            **kwargs
        )
        self.backend.upsert(memory)
    
    def retrieve(self, query: str, filter_actor_type: str = None) -> list:
        results = self.backend.search(query)
        
        if filter_actor_type:
            results = [r for r in results if r.actor_type == filter_actor_type]
        
        # Rank: user-stated memories rank higher than agent-inferred
        results.sort(key=lambda r: (r.actor_type == "human", r.confidence), reverse=True)
        return results

# When a planning agent retrieves memory, it can ask:
# "What did the USER actually say?" vs "What did agents infer?"
user_stated = store.retrieve(query, filter_actor_type="human")
```

---

## Pattern 2: Shared Memory Blocks (Letta)

Letta's memory blocks can be shared across agents. All agents in a group see the same block and any agent can update it.

```python
from letta import create_client

client = create_client()

# Create a shared block
shared_context = client.create_block(
    label="project_context",
    value="Project: Build a payments API. Stack: FastAPI + PostgreSQL. Sprint 3."
)

# Spin up two agents pointing at the same block
planner = client.create_agent(
    name="planner",
    memory=BasicBlockMemory(blocks=[shared_context])  # shared by reference
)

engineer = client.create_agent(
    name="engineer",
    memory=BasicBlockMemory(blocks=[shared_context])  # same block
)

# When planner updates the block, engineer sees it immediately
client.update_block(shared_context.id, value="Project: ... Sprint 4 started.")
```

This enables the Conversations API pattern: a user has multiple concurrent sessions, but all agents share the same "human" profile block, so they all know the same things about the user.

---

## Pattern 3: Scoped Namespace Isolation

Each agent gets its own namespace in the memory store. A separate "shared" namespace is for cross-agent facts.

```python
class MultiAgentMemory:
    def __init__(self, agent_id: str, session_id: str, backend):
        self.agent_id = agent_id
        self.session_id = session_id
        self.backend = backend
    
    def store_private(self, content: str):
        """Only this agent can read this."""
        self.backend.set(
            namespace=f"agent:{self.agent_id}:{self.session_id}",
            key=generate_id(),
            value=content
        )
    
    def store_shared(self, content: str, source: str = None):
        """All agents in this session can read this."""
        self.backend.set(
            namespace=f"session:{self.session_id}:shared",
            key=generate_id(),
            value={"content": content, "source": source or self.agent_id}
        )
    
    def retrieve_shared(self, query: str) -> list:
        return self.backend.search(
            namespace=f"session:{self.session_id}:shared",
            query=query
        )
    
    def retrieve_private(self, query: str) -> list:
        return self.backend.search(
            namespace=f"agent:{self.agent_id}:{self.session_id}",
            query=query
        )
```

---

## Pattern 4: Orchestrator-Controlled Memory

Only the orchestrator can write to long-term memory. Subagents pass results to the orchestrator, which decides what to persist.

```python
class MemoryOrchestrator:
    def __init__(self, memory_client, subagents: dict):
        self.memory = memory_client
        self.subagents = subagents
    
    async def run_task(self, task: str, user_id: str) -> str:
        # Retrieve context for this task
        context = self.memory.search(task, user_id=user_id)
        
        # Assign work to subagents
        results = {}
        for name, agent in self.subagents.items():
            results[name] = await agent.run(task, context=context)
        
        # Orchestrator decides what's worth remembering
        consolidated = await self._consolidate(task, results)
        
        # Only orchestrator writes to memory
        self.memory.add(
            [{"role": "system", "content": f"Task: {task}\nResult: {consolidated}"}],
            user_id=user_id
        )
        
        return consolidated
    
    async def _consolidate(self, task, results) -> str:
        """LLM call to decide what to persist from subagent outputs."""
        ...
```

**Advantage:** Clear audit trail — every memory write is controlled.
**Disadvantage:** Orchestrator becomes a bottleneck.

---

## Pattern 5: Event-Sourced Memory

All memory operations are events. The "current state" is computed by replaying events. Enables full audit and rollback.

```python
from dataclasses import dataclass
from enum import Enum

class MemoryEventType(Enum):
    STORE = "store"
    UPDATE = "update"
    DELETE = "delete"
    INVALIDATE = "invalidate"

@dataclass
class MemoryEvent:
    event_id: str
    event_type: MemoryEventType
    memory_id: str
    content: str
    actor: str
    timestamp: datetime
    supersedes: str = None  # for updates, which event does this replace

# Write all events to append-only log (e.g., Kafka, PostgreSQL with insert-only)
# Periodically compact to derive current state
# Any agent can query the full history
```

This pattern is less common in 2026 but used in high-compliance domains (finance, healthcare) where auditability is required.

---

## LangGraph Multi-Agent Memory

LangGraph's `Store` object is designed for multi-agent use:

```python
from langgraph.store.postgres import PostgresStore

store = PostgresStore.from_conn_string("postgresql://...")
store.setup()

# Agent A writes a shared fact
async def agent_a_node(state, *, store):
    await store.aput(
        namespace=("project", state["project_id"]),  # shared namespace
        key="tech_stack",
        value={"backend": "FastAPI", "db": "PostgreSQL"}
    )

# Agent B reads it
async def agent_b_node(state, *, store):
    tech = await store.aget(
        namespace=("project", state["project_id"]),
        key="tech_stack"
    )
    # → {"backend": "FastAPI", "db": "PostgreSQL"}
```

All agents in the graph share the same `store` reference, so writes from one agent are immediately visible to others.

---

## Real-World Example: LinkedIn CMA (April 2026)

LinkedIn's Cognitive Memory Agent architecture (reported InfoQ, April 2026):

```
User Request
     │
     ▼
[Planner Agent]
  ← reads: semantic memory (user history, preferences)
  ← reads: procedural memory (task templates)
     │
     ├──► [Research Agent]
     │      writes: episodic memory (findings, sources)
     │
     ├──► [Writer Agent]
     │      reads: episodic from Research Agent
     │      writes: episodic memory (drafts, revisions)
     │
     └──► [Reviewer Agent]
            reads: episodic from Writer Agent
            writes: procedural memory (what worked / didn't)
     │
     ▼
[Memory Consolidator] (background)
  merges episodic → semantic updates
  updates procedural guidelines
```

Key design decision: each agent writes only to its own episodic namespace. The consolidator handles promotion to shared semantic memory.

---

## Sources

- [State of AI Agent Memory 2026 (Mem0)](https://mem0.ai/blog/state-of-ai-agent-memory-2026)
- [Memory Blocks: The Key to Agentic Context Management (Letta)](https://www.letta.com/blog/memory-blocks)
- [LinkedIn Cognitive Memory Agent (InfoQ)](https://www.infoq.com/news/2026/04/linkedin-cognitive-memory-agent/)
- [Architecture and Orchestration of Memory Systems in AI Agents (Analytics Vidhya)](https://www.analyticsvidhya.com/blog/2026/04/memory-systems-in-ai-agents/)
- [LangGraph Store documentation](https://docs.langchain.com/oss/python/langgraph/add-memory)
