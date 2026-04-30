# Key-Value Stores for Agent Memory

Key-value stores serve as the fast lookup tier in agent memory systems — retrieving structured facts, user profiles, and session state in milliseconds.

---

## Role in the Memory Stack

In a typical three-layer memory stack:

```
┌─────────────────────────────────┐
│  Key-Value Store (KV)           │
│  - User profiles                │  Fast: <5ms
│  - Explicit preferences         │  Exact lookup by key
│  - Session state                │
│  - Counters, flags              │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│  Vector DB                      │
│  - Episodic memories            │  Medium: 10–200ms
│  - Semantic facts               │  Similarity search
└─────────────────────────────────┘
┌─────────────────────────────────┐
│  Knowledge Graph                │
│  - Entity relationships         │  Slower: 50–500ms
│  - Temporal fact history        │  Graph traversal
└─────────────────────────────────┘
```

KV is used when you *know the key* and need a fast exact lookup. Vector is used when you need to *find relevant memories by content*. Graph is used when you need *relational reasoning*.

---

## Redis: The Standard Choice

Redis is the dominant KV store for agent memory in production as of 2026.

### Why Redis for agent memory

- **Microsecond latency** for in-memory data
- **Rich data structures**: strings, hashes, lists, sorted sets, JSON, streams
- **TTL support**: memories can expire automatically
- **Pub/sub**: notify agents when memory is updated
- **Persistence options**: RDB snapshots, AOF logging
- **Native vector search**: Redis also does vector search via RediSearch module (one less DB)

### Basic agent memory patterns with Redis

```python
import redis
import json
from datetime import timedelta

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Store user profile as a hash
r.hset("user:alice:profile", mapping={
    "name": "Alice",
    "employer": "Acme Corp",
    "role": "Senior Engineer",
    "language_preference": "python",
    "communication_style": "brief",
    "timezone": "America/New_York",
    "last_seen": "2026-03-15T10:30:00Z"
})

# Fast profile retrieval
profile = r.hgetall("user:alice:profile")

# Store session state (with TTL — expires after 24 hours)
r.setex(
    f"session:{session_id}:state",
    timedelta(hours=24),
    json.dumps({"current_task": "code review", "files_reviewed": 3})
)

# Maintain a sorted set of recently accessed memories (for recency boosting)
r.zadd("user:alice:memory_access", {
    "mem-001": 1710498600,   # Unix timestamp of last access
    "mem-042": 1710502200,
})
recent = r.zrevrange("user:alice:memory_access", 0, 9)  # Top 10 most recent
```

---

## Redis Stack: Vector + KV in One System

Redis Stack includes RediSearch which adds vector similarity search:

```python
from redis.commands.search.field import VectorField, TextField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
import numpy as np

# Create index with vector field
schema = (
    TextField("content"),
    TagField("user_id"),
    TagField("memory_type"),
    VectorField("embedding",
                "HNSW",
                {"TYPE": "FLOAT32", "DIM": 1536, "DISTANCE_METRIC": "COSINE"})
)

r.ft("mem_idx").create_index(
    schema,
    definition=IndexDefinition(prefix=["mem:"], index_type=IndexType.HASH)
)

# Store a memory with embedding
embedding = np.random.rand(1536).astype(np.float32)
r.hset("mem:alice:001", mapping={
    "content": "User prefers Python 3.12",
    "user_id": "alice",
    "memory_type": "preference",
    "embedding": embedding.tobytes()
})

# Hybrid search (vector + filter)
query = (
    Query("@user_id:{alice}=>[KNN 5 @embedding $query_vec AS score]")
    .return_fields("content", "score")
    .sort_by("score")
    .paging(0, 5)
    .dialect(2)
)
results = r.ft("mem_idx").search(query, query_params={"query_vec": query_embedding.tobytes()})
```

This makes Redis a viable all-in-one solution for smaller deployments, eliminating the need for a separate vector DB.

---

## LangGraph + Redis

The `langgraph-checkpoint-redis` integration uses Redis for both checkpointing and long-term stores:

```python
from langgraph_checkpoint_redis import RedisSaver
from langgraph_store_redis import RedisStore

checkpointer = RedisSaver(redis_url="redis://localhost:6379")
store = RedisStore(redis_url="redis://localhost:6379")

graph = builder.compile(checkpointer=checkpointer, store=store)
```

**Why this combo works well:**
- Checkpoints (short-term state) benefit from Redis speed
- Store (long-term facts) stays in the same system, reducing ops complexity
- Redis TTLs can auto-expire old checkpoints to save memory

---

## Amazon ElastiCache for Valkey (2025–2026)

For AWS deployments, Amazon ElastiCache for Valkey (Redis-compatible) is the recommended KV backend:

```python
import valkey  # Valkey is the Redis fork after licensing change

client = valkey.Valkey(
    host="my-cluster.cache.amazonaws.com",
    port=6379,
    ssl=True
)

# Same API as Redis
client.hset("user:alice:profile", mapping={"name": "Alice"})
```

Mem0's AWS reference architecture uses ElastiCache for Valkey as the KV tier.

---

## SQLite as a Lightweight Alternative

For single-user or local-only deployments:

```python
import sqlite3
import json

conn = sqlite3.connect("agent_memory.db")
conn.execute("""
    CREATE TABLE IF NOT EXISTS kv_store (
        namespace TEXT,
        key TEXT,
        value TEXT,
        updated_at TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (namespace, key)
    )
""")

def kv_set(namespace, key, value):
    conn.execute(
        "INSERT OR REPLACE INTO kv_store (namespace, key, value) VALUES (?, ?, ?)",
        (namespace, key, json.dumps(value))
    )
    conn.commit()

def kv_get(namespace, key):
    row = conn.execute(
        "SELECT value FROM kv_store WHERE namespace = ? AND key = ?",
        (namespace, key)
    ).fetchone()
    return json.loads(row[0]) if row else None
```

LangGraph's `SqliteSaver` uses exactly this pattern for local checkpointing.

---

## Design Patterns

### Pattern 1: Multi-tenant namespacing

Always prefix keys with `user_id` or `tenant_id`:
```
user:{user_id}:profile
user:{user_id}:preferences
session:{session_id}:state
agent:{agent_id}:working_memory
```

### Pattern 2: Profile vs preferences separation

Keep mutable preferences separate from relatively stable profile info:
```python
# Profile: changes rarely
r.hset("user:alice:profile", {"name": "Alice", "employer": "Acme"})

# Preferences: changes frequently, check often
r.hset("user:alice:preferences", {"response_length": "brief", "code_language": "python"})
```

### Pattern 3: Session windowing with TTLs

Auto-clean idle sessions:
```python
# Session expires if no activity for 2 hours
r.setex(f"session:{session_id}", timedelta(hours=2), json.dumps(state))

# Refresh TTL on each interaction
r.expire(f"session:{session_id}", timedelta(hours=2))
```

---

## Sources

- [LangGraph & Redis: Build smarter AI agents with memory (Redis)](https://redis.io/blog/langgraph-redis-build-smarter-ai-agents-with-memory-persistence/)
- [How to Build AI Agents with Redis Memory Management (Redis)](https://redis.io/blog/build-smarter-ai-agents-manage-short-term-and-long-term-memory-with-redis/)
- [AI Agent Memory: Types, Architecture & Implementation (Redis)](https://redis.io/blog/ai-agent-memory-stateful-systems/)
- [Build persistent memory with Mem0, ElastiCache for Valkey, Neptune (AWS)](https://aws.amazon.com/blogs/database/build-persistent-memory-for-agentic-ai-applications-with-mem0-open-source-amazon-elasticache-for-valkey-and-amazon-neptune-analytics/)
- [GitHub: redis-developer/langgraph-redis](https://github.com/redis-developer/langgraph-redis)
