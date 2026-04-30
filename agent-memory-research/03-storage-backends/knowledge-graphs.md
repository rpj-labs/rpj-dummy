# Knowledge Graphs for Agent Memory

Knowledge graphs store memories as structured entities and relationships, enabling relational reasoning that flat vector search cannot provide. As of 2026, graph-based memory is the frontier for complex, entity-rich domains.

---

## When Graphs Beat Vectors

| Query | Vector Search | Graph Search |
|-------|--------------|--------------|
| "What does Alice prefer?" | Good | Good |
| "Who are Alice's colleagues?" | Weak (no explicit structure) | Excellent |
| "What tools do people on Alice's team use?" | Very weak | Excellent (2-hop traversal) |
| "What did the user believe before they changed jobs?" | Poor (no temporal edges) | Excellent (timestamped edges) |
| "List all people in the user's network" | Poor | Direct (traversal) |

---

## Neo4j: Production Standard

Neo4j is the dominant graph database in agent memory systems as of 2026, both for self-hosted and cloud deployments.

### Data model for agent memory

```cypher
// Entities
(:Person {id, name, current_employer, email})
(:Company {id, name, industry, founded_year})
(:Tool {id, name, category, version})
(:Concept {id, name, domain})

// Relationships with temporal metadata
(:Person)-[:WORKS_AT {since: date, valid_until: null}]->(:Company)
(:Person)-[:USES {frequency: "daily", since: date}]->(:Tool)
(:Person)-[:KNOWS {strength: 0.8, met_at: "Conf 2025"}]->(:Person)
(:Episode)-[:MENTIONS]->(:Person)
(:Episode)-[:MENTIONS]->(:Tool)
```

### Basic operations in Python

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

with driver.session() as session:
    # Upsert entity (merge prevents duplicates)
    session.run("""
        MERGE (p:Person {name: $name})
        ON CREATE SET p.created_at = datetime()
        ON MATCH SET p.updated_at = datetime()
        SET p.employer = $employer
    """, name="Alice", employer="Acme Corp")
    
    # Create relationship with temporal metadata
    session.run("""
        MATCH (p:Person {name: $person})
        MERGE (t:Tool {name: $tool})
        MERGE (p)-[r:USES]->(t)
        ON CREATE SET r.since = date(), r.valid_until = null
    """, person="Alice", tool="VSCode")
    
    # Multi-hop query: "what tools do Alice's colleagues use?"
    results = session.run("""
        MATCH (alice:Person {name: 'Alice'})
              -[:WORKS_AT]->(company:Company)
              <-[:WORKS_AT]-(colleague:Person)
              -[:USES]->(tool:Tool)
        WHERE colleague <> alice
        RETURN tool.name, count(colleague) as user_count
        ORDER BY user_count DESC
    """)
```

---

## Graphiti Integration Pattern

Graphiti automates most of the entity extraction and graph building work:

```python
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from datetime import datetime

graphiti = Graphiti("bolt://localhost:7687", "neo4j", "password")
await graphiti.build_indices_and_constraints()

# Feed raw conversation episodes
await graphiti.add_episode(
    name="session-20260315-morning",
    episode_body="""
        Alice mentioned she joined Acme Corp six months ago as a senior engineer.
        Her team uses FastAPI, PostgreSQL, and Kubernetes. She works closely with Bob Chen.
        They are planning to migrate their data pipeline to Apache Kafka by Q3.
    """,
    source=EpisodeType.message,
    reference_time=datetime(2026, 3, 15, 10, 30),
    source_description="onboarding session"
)

# Graphiti automatically extracts:
# - Entities: Alice, Acme Corp, Bob Chen, FastAPI, PostgreSQL, Kubernetes, Apache Kafka
# - Relationships: Alice WORKS_AT Acme Corp, Alice USES FastAPI, etc.
# - Temporal info: started 6 months ago → valid_from 2025-09

# Search
results = await graphiti.search("what technologies does Alice's team use?")
```

---

## Amazon Neptune Analytics

For AWS-hosted workloads, Amazon Neptune Analytics (launched 2025) provides managed graph + vector:

```python
import boto3

neptune = boto3.client("neptune-analytics", region_name="us-east-1")

# Neptune Analytics supports both graph queries (openCypher) and vector search
# via graph queries with built-in vector similarity functions

response = neptune.execute_query(
    graphIdentifier="my-agent-memory-graph",
    queryString="""
        MATCH (u:User {id: $user_id})-[:KNOWS]->(p:Person)
        RETURN p.name, p.role
    """,
    language="OPEN_CYPHER",
    parameters={"user_id": "alice"}
)
```

This is part of the Mem0 + AWS stack: Mem0 → ElastiCache (KV) + Neptune Analytics (graph) + OpenSearch (vector).

---

## Microsoft Agent Framework + Neo4j (2026)

Neo4j became a first-party integration in the Microsoft Agent Framework v1.0:

```python
from agent_framework.memory import Neo4jMemoryProvider

memory = Neo4jMemoryProvider(
    uri="bolt://localhost:7687",
    auth=("neo4j", "password"),
)

# Separate memory tiers backed by Neo4j
memory.short_term.add(current_message)        # In-session, high-speed
memory.long_term.semantic.add(extracted_fact) # Permanent facts
memory.long_term.episodic.add(episode)        # Conversation logs
memory.reasoning.add(tool_call)               # Agent reasoning traces
```

Also available: **Neo4j GraphRAG Context Provider** — adds retrieval to existing agents:

```python
from agent_framework.context import Neo4jGraphRAGContextProvider

context = Neo4jGraphRAGContextProvider(
    neo4j_url="bolt://...",
    vector_index="memory_embeddings",
    search_mode="hybrid",      # dense vector + BM25 fulltext
    traversal_depth=2          # follow up to 2 relationship hops
)
```

---

## MCP Server for Neo4j Memory

For Claude agents using MCP (Model Context Protocol), a Neo4j memory MCP server is available:

```json
{
  "mcpServers": {
    "neo4j-memory": {
      "command": "npx",
      "args": ["@sylweriusz/mcp-neo4j-memory-server"],
      "env": {
        "NEO4J_URL": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "password"
      }
    }
  }
}
```

---

## Graph Memory Design Patterns

### Pattern 1: Temporal edge versioning

Never delete edges — mark them expired:

```cypher
// When Alice changes employer:
MATCH (a:Person {name: "Alice"})-[r:WORKS_AT {valid_until: null}]->(old)
SET r.valid_until = date()

// Create new edge
MATCH (a:Person {name: "Alice"})
MERGE (new:Company {name: "NewCorp"})
CREATE (a)-[:WORKS_AT {since: date(), valid_until: null}]->(new)
```

### Pattern 2: Source attribution

Tag every edge with its source to distinguish user-stated vs agent-inferred:

```cypher
CREATE (a)-[:USES {
    source: "user_stated",         // vs "agent_inferred"
    episode_id: "sess-abc123",
    confidence: 1.0,
    since: datetime()
}]->(t:Tool {name: "VSCode"})
```

### Pattern 3: Contradiction detection

Before writing a new fact, check for conflicts:

```cypher
MATCH (p:Person {name: $name})-[r:WORKS_AT]->(c:Company)
WHERE r.valid_until IS NULL
RETURN c.name as current_employer
```

If it returns a different company than what you're about to write, handle the contradiction before writing.

---

## Sources

- [Graphiti: Knowledge Graph Memory for an Agentic World (Neo4j)](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/)
- [GitHub: neo4j-labs/agent-memory](https://github.com/neo4j-labs/agent-memory)
- [Neo4j Memory Provider for Agent Framework (Microsoft Learn)](https://learn.microsoft.com/en-us/agent-framework/integrations/neo4j-memory)
- [Graph-based Agent Memory: Taxonomy, Techniques, Applications (arXiv 2602.05665)](https://arxiv.org/html/2602.05665v1)
- [Build persistent memory with Mem0, ElastiCache, Neptune Analytics (AWS)](https://aws.amazon.com/blogs/database/build-persistent-memory-for-agentic-ai-applications-with-mem0-open-source-amazon-elasticache-for-valkey-and-amazon-neptune-analytics/)
- [Neo4j Knowledge Graph Memory MCP (Smithery)](https://smithery.ai/servers/@sylweriusz/mcp-neo4j-memory-server)
