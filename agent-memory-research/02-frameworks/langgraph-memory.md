# LangGraph Memory: Checkpointing and Persistent Stores

**Repository:** https://github.com/langchain-ai/langgraph
**Docs:** https://docs.langchain.com/oss/python/langgraph/add-memory

---

## Overview

LangGraph is LangChain's graph-based agent framework. Its memory model is built around two distinct concepts that serve different purposes:

1. **Checkpointers** — short-term state persistence across turns within a thread
2. **Stores** — long-term memory that persists across threads and sessions

These serve complementary roles and are typically used together.

---

## Checkpointers (Short-Term / Thread-Level Memory)

A checkpointer saves the graph's state after every node execution. This enables:

- Resuming a conversation exactly where it left off
- Multiple parallel threads (users) with isolated state
- Time-travel debugging (inspect/restore any past state)
- Human-in-the-loop interrupts (pause, wait for approval, resume)

### Available backends

| Checkpointer | Storage | Best For |
|--------------|---------|----------|
| `InMemorySaver` | Python dict | Development only |
| `SqliteSaver` | SQLite file | Single-process local |
| `PostgresSaver` | PostgreSQL | Production multi-instance |
| `RedisSaver` | Redis | Production, low latency |
| `MongoDBSaver` | MongoDB | Production, document-centric |
| `AgentCoreMemorySaver` (AWS) | Bedrock AgentCore | AWS-hosted agents |

### Basic usage

```python
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, MessagesState

# Set up checkpointer
conn_string = "postgresql://user:pass@localhost:5432/agent_db"
checkpointer = PostgresSaver.from_conn_string(conn_string)
checkpointer.setup()  # creates checkpoint tables

# Build graph
builder = StateGraph(MessagesState)
# ... add nodes ...
graph = builder.compile(checkpointer=checkpointer)

# Run with thread_id for conversation continuity
config = {"configurable": {"thread_id": "user-alice-session-42"}}
result = graph.invoke({"messages": [{"role": "user", "content": "Hello"}]}, config)

# Same thread_id resumes the conversation
result2 = graph.invoke({"messages": [{"role": "user", "content": "What did I just say?"}]}, config)
```

### Time-travel

```python
# List all past states for a thread
history = list(graph.get_state_history(config))

# Restore to a specific past state
past_config = history[3].config
graph.update_state(past_config, {"messages": [...]})
```

---

## Stores (Long-Term / Cross-Thread Memory)

Stores persist information that should survive beyond individual sessions and be shared across thread IDs. This is where semantic and episodic long-term memory lives.

### Available backends

| Store | Notes |
|-------|-------|
| `InMemoryStore` | Development only |
| `PostgresStore` | Production default |
| `RedisStore` | Fast access |
| `MongoDBStore` | Document-centric |

### Setup and usage

```python
from langgraph.store.postgres import PostgresStore

store = PostgresStore.from_conn_string("postgresql://...")
store.setup()

# Compile graph with both checkpointer and store
graph = builder.compile(checkpointer=checkpointer, store=store)

# Inside a graph node — access the store
async def my_node(state, *, store):
    # Write a memory
    await store.aput(
        namespace=("user_profiles", state["user_id"]),
        key="preferences",
        value={"style": "brief", "language": "python"}
    )
    
    # Read a memory
    profile = await store.aget(
        namespace=("user_profiles", state["user_id"]),
        key="preferences"
    )
    return {"profile": profile}
```

---

## Redis Integration (2025)

The `langgraph-checkpoint-redis` package provides both checkpointing and store capabilities backed by Redis:

```bash
pip install langgraph-checkpoint-redis
```

```python
from langgraph_checkpoint_redis import RedisSaver
from langgraph_store_redis import RedisStore

checkpointer = RedisSaver(redis_url="redis://localhost:6379")
store = RedisStore(redis_url="redis://localhost:6379")

graph = builder.compile(checkpointer=checkpointer, store=store)
```

**Why Redis?** For high-throughput agents (many concurrent users), Redis provides:
- Sub-millisecond checkpoint reads
- Atomic operations for safe concurrent updates
- TTL support for automatic cleanup of old sessions

---

## Integrating Mem0 with LangGraph

For semantic memory (not just state persistence), LangGraph agents commonly delegate to Mem0:

```python
from mem0 import Memory
from langgraph.graph import StateGraph, MessagesState

mem = Memory()

def recall_memories(state: MessagesState):
    """Node: retrieve relevant memories and inject into context."""
    user_message = state["messages"][-1].content
    memories = mem.search(user_message, user_id=state.get("user_id"))
    memory_context = "\n".join([m["memory"] for m in memories[:5]])
    return {"memory_context": memory_context}

def store_memories(state: MessagesState):
    """Node: store new memories from this exchange."""
    conversation = [{"role": m.type, "content": m.content} 
                    for m in state["messages"][-4:]]
    mem.add(conversation, user_id=state.get("user_id"))
    return {}
```

---

## AWS AgentCore Integration (2026)

Amazon launched Bedrock AgentCore in 2026, which includes a managed memory service that integrates directly with LangGraph:

```python
from bedrock_agentcore.memory import AgentCoreMemorySaver

# Zero-config setup — AWS handles the infrastructure
checkpointer = AgentCoreMemorySaver()

graph = builder.compile(checkpointer=checkpointer)
```

State is automatically persisted per `actor_id` + `session_id`, with no additional database management needed.

---

## Best Practices (2026)

1. **Always use a persistent checkpointer in production.** `InMemorySaver` loses state on restart.
2. **Separate thread_id and user_id.** A user can have multiple threads; the store is keyed by user_id.
3. **Use PostgresSaver for durability, RedisSaver for speed.** PostgreSQL is more durable; Redis is faster.
4. **Add memory compaction nodes.** When conversations get long, add a node that summarizes old messages before the checkpointer saves them.
5. **Namespace your store keys.** Use `(user_id, memory_type)` as namespace to avoid collisions in multi-tenant setups.

---

## Sources

- [Memory - LangGraph Docs](https://docs.langchain.com/oss/python/langgraph/add-memory)
- [LangGraph & Redis: Build smarter AI agents with memory (Redis blog)](https://redis.io/blog/langgraph-redis-build-smarter-ai-agents-with-memory-persistence/)
- [Powering Long-Term Memory with LangGraph and MongoDB (MongoDB)](https://www.mongodb.com/company/blog/product-release-announcements/powering-long-term-memory-for-agents-langgraph)
- [Integrate AgentCore Memory with LangGraph (AWS)](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory-integrate-lang.html)
- [Mastering LangGraph Checkpointing: Best Practices for 2025](https://sparkco.ai/blog/mastering-langgraph-checkpointing-best-practices-for-2025)
