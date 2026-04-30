# Vector Databases for Agent Memory

Vector databases are the most widely used storage backend for agent memory. They enable semantic similarity search — finding memories based on meaning rather than exact keywords.

---

## How Vector Search Works in Agent Memory

1. When a memory is stored, it's converted to a dense vector embedding (e.g., 1536-dimensional float array via `text-embedding-3-small`)
2. The embedding is stored alongside the original text and metadata
3. At retrieval time, the query is embedded and the database finds the nearest vectors by cosine similarity or dot product
4. Top-k results are returned and injected into the agent's context

---

## The Options (April 2026)

### Chroma

**Best for:** Prototyping, local development, research projects

```bash
pip install chromadb
```

```python
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./agent_memory")
ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="YOUR_KEY",
    model_name="text-embedding-3-small"
)

collection = client.get_or_create_collection("memories", embedding_function=ef)

# Store memory
collection.add(
    documents=["User prefers Python over JavaScript"],
    metadatas=[{"user_id": "alice", "type": "preference", "ts": "2026-03-15"}],
    ids=["mem-001"]
)

# Retrieve
results = collection.query(
    query_texts=["what language does the user prefer?"],
    n_results=5,
    where={"user_id": "alice"}
)
```

**Pros:** Zero config, embedded, works locally, easy filtering
**Cons:** Not for production scale (single-process, no clustering)
**Scale limit:** Millions of vectors in single instance before performance degrades

---

### Qdrant

**Best for:** Production self-hosted deployments, high performance

```bash
docker run -p 6333:6333 qdrant/qdrant
pip install qdrant-client
```

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(url="http://localhost:6333")

client.create_collection(
    collection_name="agent_memories",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

# Upsert with payload (metadata)
client.upsert(
    collection_name="agent_memories",
    points=[
        PointStruct(
            id="mem-001",
            vector=[0.1, 0.2, ...],  # pre-computed embedding
            payload={
                "text": "User prefers Python",
                "user_id": "alice",
                "memory_type": "preference",
                "created_at": "2026-03-15T10:00:00Z"
            }
        )
    ]
)

# Search with filter
results = client.search(
    collection_name="agent_memories",
    query_vector=query_embedding,
    query_filter={"must": [{"key": "user_id", "match": {"value": "alice"}}]},
    limit=5
)
```

**Pros:** Rust-based (fast), strong filtering, good Kubernetes support, hybrid search
**Cons:** Self-hosted operational overhead; cloud option is newer
**Scale:** Billions of vectors

---

### Pinecone

**Best for:** Fully managed production, no-ops teams

```bash
pip install pinecone
```

```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="YOUR_KEY")
pc.create_index(
    name="agent-memory",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)

index = pc.Index("agent-memory")

# Upsert
index.upsert(vectors=[
    {
        "id": "mem-001",
        "values": embedding,
        "metadata": {"user_id": "alice", "text": "...", "type": "preference"}
    }
], namespace="alice")

# Query
results = index.query(
    vector=query_embedding,
    top_k=5,
    namespace="alice",
    include_metadata=True
)
```

**Pros:** Zero infrastructure management, auto-scaling, hybrid search (sparse + dense)
**Cons:** Cost at scale, vendor lock-in, data leaves your infra
**Scale:** Unlimited (managed)

---

### Weaviate

**Best for:** Full-featured hybrid search, native multi-modal

```python
import weaviate
from weaviate.classes.config import Configure, Property, DataType

client = weaviate.connect_to_local()

# Create memory collection
memories = client.collections.create(
    name="AgentMemory",
    vectorizer_config=Configure.Vectorizer.text2vec_openai(),
    generative_config=Configure.Generative.openai(),
    properties=[
        Property(name="content", data_type=DataType.TEXT),
        Property(name="user_id", data_type=DataType.TEXT),
        Property(name="memory_type", data_type=DataType.TEXT),
    ]
)

# Insert
memories.data.insert({
    "content": "User is building a CLI tool in Python",
    "user_id": "alice",
    "memory_type": "context"
})

# Hybrid search (vector + keyword)
results = memories.query.hybrid(
    query="what is the user building",
    filters=weaviate.classes.query.Filter.by_property("user_id").equal("alice"),
    limit=5
)
```

**Pros:** Native hybrid search, multi-modal, GraphQL API, strong ecosystem
**Cons:** Complex configuration, higher operational overhead than Qdrant

---

### pgvector (PostgreSQL Extension)

**Best for:** Teams already using PostgreSQL who want to avoid another database

```sql
-- Enable extension
CREATE EXTENSION vector;

-- Memory table
CREATE TABLE agent_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,
    memory_type TEXT,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    accessed_at TIMESTAMPTZ DEFAULT NOW(),
    access_count INT DEFAULT 0
);

-- Index for ANN search
CREATE INDEX ON agent_memories USING hnsw (embedding vector_cosine_ops);
```

```python
from pgvector.psycopg import register_vector
import psycopg

conn = psycopg.connect("postgresql://...")
register_vector(conn)

# Insert
conn.execute(
    "INSERT INTO agent_memories (user_id, content, embedding) VALUES (%s, %s, %s)",
    ("alice", "User prefers Python", embedding)
)

# Search
rows = conn.execute(
    """SELECT content, 1 - (embedding <=> %s) AS similarity
       FROM agent_memories
       WHERE user_id = %s
       ORDER BY embedding <=> %s
       LIMIT 5""",
    (query_embedding, "alice", query_embedding)
).fetchall()
```

**Pros:** One less database to manage, full SQL capabilities, ACID transactions, easy joins with user data
**Cons:** Not as performant as dedicated vector DBs at extreme scale, requires pgvector 0.8+ for HNSW

---

## 2026 Benchmark Summary

From [Vector Database Benchmarks 2026 (CallSphere)](https://callsphere.ai/blog/vector-database-benchmarks-2026-pgvector-qdrant-weaviate-milvus-lancedb):

| Database | QPS (1M vectors) | P99 Latency | Recall@10 |
|----------|-----------------|-------------|-----------|
| Qdrant | ~8,000 | 8ms | 99.2% |
| Milvus | ~7,500 | 10ms | 99.0% |
| Weaviate | ~5,000 | 15ms | 98.8% |
| pgvector 0.9 (HNSW) | ~3,000 | 25ms | 98.5% |
| Chroma | ~1,500 | 40ms | 97.9% |

*Numbers are approximate and depend heavily on hardware and configuration.*

---

## Selection Guide for Agent Memory

| Scenario | Recommended DB | Why |
|----------|---------------|-----|
| Local dev / prototype | Chroma | Zero config, in-process |
| Small-medium production (self-hosted) | Qdrant | Best perf/complexity ratio |
| Large production (no-ops) | Pinecone | Managed, auto-scales |
| Already use PostgreSQL | pgvector | One less system |
| Need hybrid search + multi-modal | Weaviate | Native support |
| Need graph + vector together | Neo4j (with vector index) | One system for both |

---

## Sources

- [Best Vector Databases 2026 (DataCamp)](https://www.datacamp.com/blog/the-top-5-vector-databases)
- [Vector Database Comparison 2026 (GroovyWeb)](https://www.groovyweb.co/blog/vector-database-comparison-2026)
- [Vector Database Benchmarks 2026 (CallSphere)](https://callsphere.ai/blog/vector-database-benchmarks-2026-pgvector-qdrant-weaviate-milvus-lancedb)
- [Vector Databases for AI Agents: 2026 Comparison](https://www.jahanzaib.ai/blog/vector-database-ai-agents-pinecone-weaviate-chroma-qdrant)
- [Implementation Blueprint for Vector Database (The Data Letter)](https://www.thedataletter.com/p/implementation-blueprint-for-vector)
