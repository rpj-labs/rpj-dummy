# Temporal Decay in Agent Memory

Facts don't stay true forever. An agent that learned something about a user two years ago and still treats it as current is operating on stale information. Managing temporal decay is one of the hardest problems in production agent memory.

---

## The Problem

### Information entropy over time

Different types of facts have different lifespans:

| Fact Type | Typical Lifespan | Example |
|-----------|-----------------|---------|
| Preferences (communication style) | Years | "Prefers bullet points" |
| Job/employer | 1–3 years average | "Works at Acme Corp" |
| Current project | Weeks to months | "Working on the payments API" |
| Temporary state | Hours to days | "Jet-lagged this week" |
| Core identity | Decades | "Native English speaker" |
| Tech stack in use | 6–24 months | "Uses React 18" |

Without decay, an agent's memory fills up with outdated facts that can actively mislead it.

### Real-world failure mode

```
Memory stored in 2024: "User is job searching, looking for ML roles"
State in 2026: User has been happily employed for 18 months

Agent behavior: "Since you're job searching, here are some ML job listings..."
User experience: Confusion and loss of trust in the agent
```

---

## Temporal Decay Models

### 1. Exponential Decay (most common)

Inspired by Ebbinghaus's forgetting curve. A fact's "confidence score" decays exponentially with time:

```python
import math
from datetime import datetime

def compute_decayed_score(
    base_score: float,
    created_at: datetime,
    last_accessed_at: datetime,
    decay_rate: float = 0.01,     # 0.01/hour → half-life ~69 hours
    access_boost: float = 0.1     # each access adds 0.1 to score
) -> float:
    hours_since_creation = (datetime.now() - created_at).total_seconds() / 3600
    hours_since_access = (datetime.now() - last_accessed_at).total_seconds() / 3600
    
    time_decay = math.exp(-decay_rate * hours_since_creation)
    access_decay = math.exp(-decay_rate * hours_since_access)
    
    # Use the better of creation-decay and access-decay
    # (accessing a memory resets its effective age)
    effective_score = base_score * max(time_decay, access_decay)
    
    return effective_score

# Example:
# A fact created 30 days ago, never accessed → score multiplied by ~0.07
# A fact created 30 days ago, accessed yesterday → score multiplied by ~0.79
```

The paper "SSGM" sets a decay rate of 0.01/hour, giving a half-life of ~69 hours for unaccessed facts.

### 2. Category-Based TTLs

Assign time-to-live based on fact category rather than time since creation:

```python
TTL_BY_CATEGORY = {
    "core_identity": None,           # Never expires
    "preference": 365 * 24 * 3600,  # 1 year
    "employer": 365 * 24 * 3600,    # 1 year (but check more often)
    "current_project": 30 * 24 * 3600,  # 30 days
    "temporary_state": 3 * 24 * 3600,   # 3 days
    "tech_version": 180 * 24 * 3600,    # 6 months
}

def should_expire(memory: dict) -> bool:
    category = memory.get("category", "preference")
    ttl = TTL_BY_CATEGORY.get(category)
    if ttl is None:
        return False
    age_seconds = (datetime.now() - memory["created_at"]).total_seconds()
    return age_seconds > ttl
```

### 3. Access-Frequency Weighting

Facts that are retrieved often are clearly still useful:

```python
def retention_score(memory: dict) -> float:
    """Higher score = more likely to retain."""
    recency = 1.0 / (1 + (datetime.now() - memory["created_at"]).days)
    frequency = math.log1p(memory["access_count"])  # log scale
    source_weight = 1.0 if memory["source"] == "user_stated" else 0.6
    
    return recency * 0.3 + frequency * 0.4 + source_weight * 0.3
```

---

## Implementation Patterns

### Pattern 1: Soft expiry with archiving

Don't delete — archive. Archived memories can be restored if the user references them.

```python
class TemporalMemoryManager:
    def run_expiry_sweep(self):
        """Run periodically (daily/weekly)."""
        now = datetime.now()
        
        for memory in self.store.get_all():
            score = self.compute_decayed_score(memory)
            
            if score < 0.1:
                # Archive, don't delete
                self.store.move_to_archive(memory.id, reason="temporal_decay")
            elif score < 0.3:
                # Flag as potentially stale
                self.store.flag(memory.id, flag="potentially_stale")
```

### Pattern 2: Temporal metadata in retrieval ranking

Factor time into the retrieval score:

```sql
-- When searching for memories:
SELECT content, 
       (1 - (embedding <=> $query_vec)) * temporal_weight AS final_score
FROM memories
WHERE user_id = $user_id
  AND valid_until IS NULL
ORDER BY final_score DESC
LIMIT 10;

-- temporal_weight calculation:
-- EXTRACT(EPOCH FROM NOW() - created_at) / 86400.0 = days_old
-- temporal_weight = EXP(-0.007 * days_old)  -- half-life ~99 days
```

### Pattern 3: Staleness flags in context injection

When injecting memories, flag old ones for the agent to treat with skepticism:

```python
def inject_memories_with_staleness(memories: list) -> str:
    lines = []
    for mem in memories:
        days_old = (datetime.now() - mem["created_at"]).days
        
        if days_old < 30:
            lines.append(f"• {mem['content']}")
        elif days_old < 180:
            lines.append(f"• [Recorded ~{days_old} days ago, verify if still current] {mem['content']}")
        else:
            lines.append(f"• [OLD — ~{days_old} days ago, may be outdated] {mem['content']}")
    
    return "\n".join(lines)
```

### Pattern 4: Proactive verification for high-decay categories

For categories with short lifespans (current project, employer), proactively ask the user to confirm:

```python
def should_verify_memory(memory: dict) -> bool:
    """Returns True if we should ask the user to confirm this memory."""
    high_decay = ["current_project", "employer", "tech_version"]
    days_old = (datetime.now() - memory["created_at"]).days
    
    if memory["category"] in high_decay and days_old > 90:
        return True
    return False

# In the agent's response, occasionally include:
# "Just to confirm — are you still working on [project X]?"
```

---

## The 2026 Problem: 1M Context Windows

An important 2026 development: with frontier models now supporting 1M+ token context windows, you *could* just dump the entire conversation history into context every time and skip memory retrieval entirely.

**This doesn't actually solve temporal decay:**
- The context still contains contradictory old and new facts
- The model may surface old facts as if they're current
- At 1M tokens, you're paying for a lot of tokens per request
- You still need to know *which* conversation is relevant for this user

**The current consensus (2026):**

Use long context windows for *within-session* memory (stop worrying about summarization mid-session). Use external memory systems for *cross-session* facts where temporal management matters.

---

## Sources

- [Governing Evolving Memory in LLM Agents: SSGM (arXiv 2603.11768)](https://arxiv.org/html/2603.11768)
- [Adaptive Memory Admission Control for LLM Agents (arXiv 2603.04549)](https://arxiv.org/pdf/2603.04549)
- [Memory for Autonomous LLM Agents: Mechanisms, Evaluation, Frontiers (arXiv 2603.07670)](https://arxiv.org/html/2603.07670v1)
- [State of AI Agent Memory 2026 (Mem0)](https://mem0.ai/blog/state-of-ai-agent-memory-2026)
- [MemAgents Workshop ICLR 2026](https://openreview.net/pdf?id=U51WxL382H)
