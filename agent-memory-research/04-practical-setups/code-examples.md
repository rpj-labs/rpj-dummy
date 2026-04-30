# Code Examples: Agent Memory Setups

Complete, runnable examples for common setups.

---

## Example 1: Minimal Agent with Mem0 (< 50 lines)

```python
# requirements: mem0ai openai
import os
from mem0 import Memory
from openai import OpenAI

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
memory = Memory()

def chat(user_id: str, message: str, history: list) -> str:
    # Retrieve relevant memories
    mems = memory.search(message, user_id=user_id, limit=5)
    context = "\n".join(f"- {m['memory']}" for m in mems)
    
    system = "You are a helpful assistant."
    if context:
        system += f"\n\nWhat you know about this user:\n{context}"
    
    messages = [{"role": "system", "content": system}] + history[-10:] + \
               [{"role": "user", "content": message}]
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    ).choices[0].message.content
    
    # Store new memories async (fire and forget for now)
    memory.add(
        [{"role": "user", "content": message},
         {"role": "assistant", "content": response}],
        user_id=user_id
    )
    
    return response

# Usage
history = []
response = chat("alice", "Hi! I'm a Python dev at Acme Corp.", history)
history += [{"role": "user", "content": "Hi! I'm a Python dev at Acme Corp."},
            {"role": "assistant", "content": response}]

response2 = chat("alice", "What do you know about me?", history)
print(response2)
# → "You're a Python developer at Acme Corp."
```

---

## Example 2: LangGraph Agent with PostgreSQL Checkpointing

```python
# requirements: langgraph langchain-openai psycopg2-binary
import os
from typing import Annotated
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from langchain_openai import ChatOpenAI

DB_URL = os.environ["DATABASE_URL"]  # postgresql://user:pass@host:5432/db

# Set up persistence
checkpointer = PostgresSaver.from_conn_string(DB_URL)
checkpointer.setup()

store = PostgresStore.from_conn_string(DB_URL)
store.setup()

llm = ChatOpenAI(model="gpt-4o-mini")

async def agent_node(state: MessagesState, *, store):
    user_id = state.get("user_id", "default")
    
    # Retrieve long-term memories from store
    profile = await store.aget(("users", user_id), "profile") or {}
    
    system_content = "You are a helpful assistant."
    if profile:
        facts = "; ".join(f"{k}: {v}" for k, v in profile.items())
        system_content += f"\n\nUser profile: {facts}"
    
    messages = [{"role": "system", "content": system_content}] + state["messages"]
    response = await llm.ainvoke(messages)
    
    return {"messages": [response]}

async def memory_update_node(state: MessagesState, *, store):
    """Extract and store facts from the latest exchange."""
    user_id = state.get("user_id", "default")
    
    # Simple extraction: ask LLM if there's anything worth remembering
    last_two = state["messages"][-2:]
    extract_prompt = f"""
From this exchange, extract any facts worth storing about the user.
Return JSON or null.

{last_two}
"""
    result = await llm.ainvoke([{"role": "user", "content": extract_prompt}])
    
    try:
        import json
        facts = json.loads(result.content)
        if facts:
            existing = await store.aget(("users", user_id), "profile") or {}
            existing.update(facts)
            await store.aput(("users", user_id), "profile", existing)
    except Exception:
        pass
    
    return {}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("memory_update", memory_update_node)
builder.add_edge(START, "agent")
builder.add_edge("agent", "memory_update")
builder.add_edge("memory_update", END)

graph = builder.compile(checkpointer=checkpointer, store=store)

# Run
async def main():
    config = {"configurable": {"thread_id": "alice-001", "user_id": "alice"}}
    
    result = await graph.ainvoke(
        {"messages": [{"role": "user", "content": "I work at Google on the Search team."}]},
        config=config
    )
    print(result["messages"][-1].content)
    
    # New thread, same user — profile persists in store
    config2 = {"configurable": {"thread_id": "alice-002", "user_id": "alice"}}
    result2 = await graph.ainvoke(
        {"messages": [{"role": "user", "content": "Where do I work?"}]},
        config2
    )
    print(result2["messages"][-1].content)
    # → "You work at Google on the Search team."
```

---

## Example 3: Graphiti Knowledge Graph Memory

```python
# requirements: graphiti-core neo4j
import asyncio
from datetime import datetime
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.llm_client import OpenAIClient
from graphiti_core.embedder import OpenAIEmbedder

async def setup_graphiti():
    graphiti = Graphiti(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password",
        llm_client=OpenAIClient(api_key=os.environ["OPENAI_API_KEY"]),
        embedder=OpenAIEmbedder(api_key=os.environ["OPENAI_API_KEY"])
    )
    await graphiti.build_indices_and_constraints()
    return graphiti

async def main():
    g = await setup_graphiti()
    
    # Store a conversation episode
    await g.add_episode(
        name="onboarding-call-20260315",
        episode_body="""
            Alice mentioned she's a senior engineer at Acme Corp.
            Her team of 5 engineers uses Python 3.12, FastAPI, and PostgreSQL.
            She works closely with Bob Chen (backend lead) and Carol Liu (data).
            They are planning to adopt Kubernetes by end of Q2 2026.
        """,
        source=EpisodeType.message,
        reference_time=datetime(2026, 3, 15),
        source_description="customer onboarding call"
    )
    
    # Graphiti automatically extracted:
    # Entity nodes: Alice, Acme Corp, Bob Chen, Carol Liu, FastAPI, PostgreSQL, Python 3.12, Kubernetes
    # Relationships: Alice WORKS_AT Acme, Alice KNOWS Bob, Alice KNOWS Carol,
    #                Acme USES FastAPI, Acme USES PostgreSQL, etc.
    # Temporal: Kubernetes adoption planned for Q2 2026
    
    # Search the graph
    results = await g.search("what technologies does Alice's team use?")
    for r in results:
        print(r.fact)
    # → "Alice's team uses Python 3.12"
    # → "Alice's team uses FastAPI"  
    # → "Alice's team uses PostgreSQL"
    
    # Multi-hop query (via Cypher directly)
    from neo4j import AsyncGraphDatabase
    driver = AsyncGraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    async with driver.session() as session:
        result = await session.run("""
            MATCH (alice:Person {name: 'Alice'})-[:KNOWS]->(colleague:Person)
            MATCH (colleague)-[:WORKS_ON]->(tech:Technology)
            RETURN colleague.name, collect(tech.name) as technologies
        """)
        records = await result.data()
        for r in records:
            print(f"{r['colleague.name']}: {r['technologies']}")
```

---

## Example 4: Redis-Backed Agent with Vector Search

```python
# requirements: redis openai numpy
import os
import json
import numpy as np
from openai import OpenAI
import redis
from redis.commands.search.field import VectorField, TextField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

r = redis.Redis(host="localhost", port=6379, decode_responses=False)
oai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

EMBEDDING_DIM = 1536
INDEX_NAME = "memory_idx"

def setup_index():
    try:
        r.ft(INDEX_NAME).info()
    except Exception:
        schema = (
            TextField("content"),
            TagField("user_id"),
            VectorField("embedding", "HNSW", {
                "TYPE": "FLOAT32", "DIM": EMBEDDING_DIM, "DISTANCE_METRIC": "COSINE"
            })
        )
        r.ft(INDEX_NAME).create_index(
            schema,
            definition=IndexDefinition(prefix=["mem:"], index_type=IndexType.HASH)
        )

def embed(text: str) -> np.ndarray:
    return np.array(oai.embeddings.create(
        input=text, model="text-embedding-3-small"
    ).data[0].embedding, dtype=np.float32)

def store_memory(user_id: str, content: str):
    mem_id = f"mem:{user_id}:{hash(content) & 0xFFFFFF}"
    r.hset(mem_id, mapping={
        b"content": content.encode(),
        b"user_id": user_id.encode(),
        b"embedding": embed(content).tobytes()
    })

def search_memories(user_id: str, query: str, k: int = 5) -> list[str]:
    q = (
        Query(f"@user_id:{{{user_id}}}=>[KNN {k} @embedding $vec AS score]")
        .return_fields("content", "score")
        .sort_by("score")
        .dialect(2)
    )
    results = r.ft(INDEX_NAME).search(q, query_params={"vec": embed(query).tobytes()})
    return [doc.content.decode() for doc in results.docs]

# Setup
setup_index()

# Store memories
store_memory("alice", "Alice is a senior engineer at Acme Corp")
store_memory("alice", "Alice prefers brief, technical answers")
store_memory("alice", "Alice's team uses FastAPI and PostgreSQL")

# Retrieve
memories = search_memories("alice", "what language does Alice's team use?")
print(memories)
# → ["Alice's team uses FastAPI and PostgreSQL", ...]
```

---

## Example 5: Memory Consolidation Pipeline (Background Job)

```python
# Background job: runs after each session to extract and store memories
import asyncio
from openai import AsyncOpenAI

oai = AsyncOpenAI()

EXTRACTION_PROMPT = """
Extract facts worth remembering about the user from this conversation.
Focus on: preferences, background, decisions, stated facts.
Do NOT include: trivial chitchat, session-specific tasks, things the user will change.

Output as JSON array of strings. Example: ["User is a Python developer", "User dislikes verbose output"]
If nothing is worth remembering, output: []

Conversation:
{conversation}
"""

async def extract_memories(conversation: list[dict]) -> list[str]:
    """Given a conversation (list of {role, content}), extract memorable facts."""
    formatted = "\n".join(
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in conversation
    )
    
    response = await oai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": EXTRACTION_PROMPT.format(conversation=formatted)
        }],
        temperature=0.1
    )
    
    import json
    try:
        return json.loads(response.choices[0].message.content)
    except Exception:
        return []

async def consolidate_session(user_id: str, conversation: list[dict], memory_client):
    """Full pipeline: extract → deduplicate → store."""
    new_memories = await extract_memories(conversation)
    
    for mem_text in new_memories:
        # Check for near-duplicates before storing
        existing = memory_client.search(mem_text, user_id=user_id, limit=1)
        if existing and existing[0]["score"] > 0.95:
            # Very similar to existing memory — update rather than duplicate
            memory_client.update(existing[0]["id"], mem_text, user_id=user_id)
        else:
            memory_client.add(
                [{"role": "system", "content": mem_text}],
                user_id=user_id
            )
    
    print(f"[{user_id}] Consolidated {len(new_memories)} memories from session")

# In production: trigger this as a Celery task, AWS Lambda, or async background task
# after each session ends
```

---

## Sources

- [Mem0 Documentation](https://docs.mem0.ai/platform/overview)
- [LangGraph Memory Docs](https://docs.langchain.com/oss/python/langgraph/add-memory)
- [Graphiti GitHub](https://github.com/getzep/graphiti)
- [Redis AI Agent Memory Guide](https://redis.io/blog/build-smarter-ai-agents-manage-short-term-and-long-term-memory-with-redis/)
- [How to Build Universal Long-Term Memory with Mem0 and OpenAI (MarkTechPost)](https://www.marktechpost.com/2026/04/15/how-to-build-a-universal-long-term-memory-layer-for-ai-agents-using-mem0-and-openai/)
