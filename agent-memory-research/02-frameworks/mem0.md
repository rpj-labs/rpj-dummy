# Mem0: Universal Memory Layer for AI Agents

**Repository:** https://github.com/mem0ai/mem0
**PyPI:** https://pypi.org/project/mem0ai/
**Stars (April 2026):** ~48,000
**Language:** Python (+ JavaScript SDK)
**License:** Apache 2.0

---

## What It Is

Mem0 is a standalone memory layer that plugs into *any* existing agent framework. It handles memory extraction, storage, deduplication, contradiction resolution, and retrieval — all outside the agent's reasoning loop.

The agent doesn't need to know about memory management. It just gets relevant context injected, or it can call `search_memory(query)` as a tool.

---

## Architecture

Mem0 maintains three parallel storage backends:

```
Mem0 Memory Layer
       │
       ├─── Vector Store ──── semantic similarity search
       │     (Qdrant default, or Pinecone/Weaviate/pgvector)
       │
       ├─── Knowledge Graph ── entity relationships
       │     (Neo4j, or in-memory for small scale)
       │
       └─── Key-Value Store ── fast user profile lookups
             (Redis, or SQLite for local)
```

When memory is written, it's stored in all three. When memory is retrieved, results from all three are merged and ranked.

---

## Memory Processing Pipeline

### Write path (after session)

```
Raw conversation
      │
      ▼
[Extractor LLM] (gpt-4o-mini by default)
  - Identifies memorable facts, preferences, events
  - Outputs structured JSON: {memory_type, content, entities}
      │
      ▼
[Deduplication check]
  - Embed new memory
  - Search existing store for near-duplicates
  - If duplicate: update existing
  - If novel: create new entry
      │
      ▼
[Contradiction check]
  - Check if new fact contradicts any existing fact about same entity
  - Resolution rule: newer + user-stated > older + agent-inferred
      │
      ▼
[Storage]
  - Write embedding to vector store
  - Update entity graph
  - Write structured profile to KV store
```

### Read path (at session start or per-turn)

```
User message
      │
      ▼
[Retriever]
  - Dense vector search (top-k by cosine similarity)
  - Sparse BM25 search (keyword match)
  - Graph traversal (for entity-linked facts)
      │
      ▼
[Merger & Ranker]
  - Deduplicate results
  - Boost by recency and access frequency
      │
      ▼
Inject top-k memories into system prompt or context
```

---

## Installation and Quick Start

### Install

```bash
pip install mem0ai
```

### Basic usage (default config, uses OpenAI)

```python
from mem0 import Memory

mem = Memory()

# Store a conversation
messages = [
    {"role": "user", "content": "Hi, I'm Alex. I work at a startup building dev tools."},
    {"role": "assistant", "content": "Great! What kind of dev tools?"},
    {"role": "user", "content": "A CLI tool for Python developers. We use FastAPI on the backend."}
]
mem.add(messages, user_id="alex")

# Retrieve relevant memories
results = mem.search("What does Alex's company build?", user_id="alex")
for r in results:
    print(r["memory"])
# → "Alex works at a startup building CLI tools for Python developers"
# → "Alex's company uses FastAPI on the backend"
```

---

## Configuration

### Custom backends

```python
from mem0 import Memory

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "agent_memories",
            "host": "localhost",
            "port": 6333,
            "embedding_model_dims": 1536
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "password"
        }
    },
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4o-mini",
            "temperature": 0.1
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small"
        }
    }
}

mem = Memory.from_config(config)
```

### AWS setup (Mem0 + ElastiCache + Neptune)

For production AWS deployments, Mem0 integrates with:
- **Amazon ElastiCache for Valkey** — key-value store backend
- **Amazon Neptune Analytics** — graph store backend
- **Amazon OpenSearch / Pinecone** — vector store backend

This is the recommended stack for enterprise AWS shops as of 2026.

---

## Deployment Options

| Mode | Setup | Best For |
|------|-------|----------|
| Library (local) | `pip install mem0ai` | Prototyping, single-user |
| Self-hosted server | Docker + external DBs | Team deployments, data control |
| Mem0 Cloud | API key only | Zero-ops, managed infrastructure |

### Self-hosted via Docker

```yaml
services:
  mem0:
    image: mem0ai/mem0:latest
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - QDRANT_URL=http://qdrant:6333
      - NEO4J_URL=bolt://neo4j:7687
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
  neo4j:
    image: neo4j:5
    environment:
      - NEO4J_AUTH=neo4j/password
```

---

## Mem0 vs Mem0g (Graph-augmented)

Mem0 ships two modes:

| Mode | Description | LLM Score | P95 Latency |
|------|-------------|-----------|-------------|
| `Mem0` | Vector + KV only | 66.9% | 1.44s |
| `Mem0g` | Vector + KV + Graph | 68.4% | 2.59s |

Enable Mem0g by adding the `graph_store` config key. Use it when:
- Your domain has complex entity relationships
- You need multi-hop reasoning ("tools used by Alex's colleagues")
- Retrieval accuracy matters more than latency

---

## 2025–2026 Platform Releases

| Date | Release |
|------|---------|
| Jun 2025 | JavaScript MCP Server for Mem0 |
| Jun 2025 | OpenMemory Cloud (hosted variant) |
| Sep 2025 | Export/import between OpenMemory instances |
| Apr 2026 | Universal long-term memory tutorial with OpenAI integration |

---

## Integration with Agent Frameworks

Mem0 works with any framework. Minimal integration:

```python
# In your LangChain/LangGraph agent
from mem0 import MemoryClient

client = MemoryClient(api_key="YOUR_KEY")

def agent_step(user_message, user_id):
    # Get relevant memories
    memories = client.search(user_message, user_id=user_id)
    memory_context = "\n".join([m["memory"] for m in memories])
    
    # Build prompt with memory injected
    messages = [
        {"role": "system", "content": f"User context:\n{memory_context}"},
        {"role": "user", "content": user_message}
    ]
    
    # Run your LLM call here...
    response = llm.invoke(messages)
    
    # Store new memories from this interaction
    client.add([
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": response.content}
    ], user_id=user_id)
    
    return response
```

---

## When to Choose Mem0

**Choose Mem0 when:**
- You want to add memory to an existing agent with minimal refactoring
- You need a universal layer that works across multiple agent frameworks
- You prefer external memory management (not agent-controlled)
- You want a managed cloud option with zero ops

**Don't choose Mem0 when:**
- You need the agent to actively control its own memory (use Letta)
- Your latency budget is under ~200ms for write processing
- You need very deep graph reasoning on memory (consider Graphiti directly)

---

## Sources

- [Mem0: Building Production-Ready AI Agents (arXiv 2504.19413)](https://arxiv.org/abs/2504.19413)
- [State of AI Agent Memory 2026 (Mem0 blog)](https://mem0.ai/blog/state-of-ai-agent-memory-2026)
- [Build persistent memory with Mem0, ElastiCache, Neptune (AWS)](https://aws.amazon.com/blogs/database/build-persistent-memory-for-agentic-ai-applications-with-mem0-open-source-amazon-elasticache-for-valkey-and-amazon-neptune-analytics/)
- [GitHub: mem0ai/mem0](https://github.com/mem0ai/mem0)
- [How to Build Universal Long-Term Memory with Mem0 and OpenAI (MarkTechPost)](https://www.marktechpost.com/2026/04/15/how-to-build-a-universal-long-term-memory-layer-for-ai-agents-using-mem0-and-openai/)
