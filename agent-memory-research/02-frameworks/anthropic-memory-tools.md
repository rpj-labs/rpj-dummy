# Anthropic's Native Memory Systems

Anthropic has shipped memory across three separate surfaces in 2025–2026: Claude Code (the CLI/IDE tool), the Claude API (the `memory_20250818` tool), and Claude Managed Agents (persistent memory in the agent platform). Each is designed differently and serves a different use case.

---

## Surface 1: Claude Code Memory (CLAUDE.md + Auto Memory)

### How Claude Code Reads Memory

Claude Code has a layered memory system based on **CLAUDE.md files** and an **auto memory directory**. Both are markdown files on your local filesystem, never uploaded to git by default.

#### CLAUDE.md Files

CLAUDE.md files give Claude persistent instructions and context for a project. Claude reads them at the start of every session. They cascade:

```
~/.claude/CLAUDE.md          ← global (applies to all projects)
~/projects/myapp/CLAUDE.md   ← project-level
~/projects/myapp/src/CLAUDE.md ← subdirectory-level (if exists)
```

Claude reads all applicable CLAUDE.md files and merges them into its working context. The most specific file (subdirectory) takes precedence.

**What to put in CLAUDE.md:**
```markdown
# Project: Payments API

## Stack
- Python 3.12, FastAPI, PostgreSQL 16
- Tests: pytest with asyncio
- Linting: ruff, mypy strict

## Conventions
- All endpoints use async/await
- Database sessions injected via dependency
- Error responses: {"error": "...", "code": "..."}

## Don't do
- Never use sync SQLAlchemy sessions
- No print() statements, use structlog

## Current sprint focus
- Implementing idempotency keys on POST /charges
```

#### Auto Memory Directory

Claude Code also maintains a memory directory at:
```
~/.claude/projects/<encoded-path>/memory/
```

This is where Claude can write and read its own notes across sessions. The first 200 lines of `MEMORY.md` in this directory are loaded into every session automatically. Content beyond line 200 is invisible unless Claude explicitly reads further.

**Key constraint:** The 200-line limit means MEMORY.md must stay curated. Claude can and should consolidate and prune it.

---

### Auto Dream: Memory Consolidation for Claude Code

"Auto Dream" is Claude Code's background memory consolidation feature — named as an analogy to REM sleep, when humans consolidate memories.

When triggered (manually or automatically at session end), Auto Dream:

1. Reads the full memory directory and builds a mental map of what's stored
2. Converts relative date references to absolute dates ("Yesterday we decided X" → "On 2026-03-15 we decided X")
3. Merges new session notes into existing topic files
4. Removes redundant or stale notes
5. Maintains cross-references between topic files
6. Compresses old entries to free up the 200-line budget for new content

```markdown
# Example memory directory after Auto Dream

/memory/
├── MEMORY.md           ← index file, always loaded first
├── architecture.md     ← decisions about the codebase
├── in-progress.md      ← current work state
├── gotchas.md          ← things that tripped us up
└── user-preferences.md ← operator/user style preferences
```

**MEMORY.md index example:**
```markdown
# Memory Index
Last dream: 2026-03-15 14:30

## Topics
- architecture.md: payment flow design, async patterns, DB schema decisions
- in-progress.md: idempotency key implementation, ~60% done
- gotchas.md: SQLAlchemy async gotchas, pytest async fixture setup
- user-preferences.md: prefers concise summaries, snake_case everywhere

## Recent decisions
- 2026-03-14: Switched from sync to async session management
- 2026-03-15: Decided to use ULID for idempotency keys, not UUID
```

---

### Claude-Mem: Community Plugin

The `claude-mem` plugin (community project) extends Claude Code's memory capabilities:

```bash
# Install
claude code plugin install claude-mem
```

Features:
- Automatically captures everything Claude does during coding sessions
- Compresses with AI using the Agent SDK
- Injects relevant context back into future sessions
- Built on top of Claude's native memory directory

**GitHub:** https://github.com/thedotmack/claude-mem

---

## Surface 2: The Memory Tool API (`memory_20250818`)

### What It Is

The Memory Tool is a client-side tool for the Claude API that gives Claude the ability to read and write files in a `/memories` directory you control. Claude automatically checks memory before starting tasks and writes what it learns as it works.

It's the primitive for **just-in-time context retrieval**: instead of loading all relevant information upfront, Claude stores what it learns and pulls it back on demand.

### Tool Type

```json
{
  "type": "memory_20250818",
  "name": "memory"
}
```

### Supported Commands

| Command | Purpose |
|---------|---------|
| `view` | List directory contents or read file with line numbers |
| `create` | Create a new file |
| `str_replace` | Replace text in a file (like a targeted edit) |
| `insert` | Insert text at a specific line |
| `delete` | Delete a file or directory |
| `rename` | Rename or move a file |

### What Claude Does Automatically

When the memory tool is enabled, the system prompt instructs Claude:

```
IMPORTANT: ALWAYS VIEW YOUR MEMORY DIRECTORY BEFORE DOING ANYTHING ELSE.
MEMORY PROTOCOL:
1. Use the `view` command to check for earlier progress.
2. ... (work on the task) ...
   - As you make progress, record status/progress/thoughts in your memory.
ASSUME INTERRUPTION: Your context window might be reset at any moment,
so you risk losing any progress not recorded in memory.
```

This turns Claude into a **self-journaling agent** that never loses progress across context resets.

### Python Implementation

```python
import anthropic
import os
import json
from pathlib import Path

MEMORY_DIR = Path("./memories")
MEMORY_DIR.mkdir(exist_ok=True)

client = anthropic.Anthropic()

def handle_memory_tool_call(tool_call: dict) -> str:
    """Execute memory tool commands on the local filesystem."""
    cmd = tool_call["input"]["command"]
    
    if cmd == "view":
        path = Path(tool_call["input"]["path"])
        # Security: ensure path is within /memories
        if not str(path).startswith(str(MEMORY_DIR)):
            return f"Error: Path {path} is outside memory directory"
        
        if path.is_dir():
            lines = [f"Here're the files and directories up to 2 levels deep in {path}:"]
            for item in sorted(path.rglob("*")):
                if not item.name.startswith("."):
                    size = item.stat().st_size if item.is_file() else 0
                    lines.append(f"{size}\t{item}")
            return "\n".join(lines)
        else:
            if not path.exists():
                return f"The path {path} does not exist."
            content = path.read_text()
            lines = content.split("\n")
            numbered = "\n".join(f"{i+1:6}\t{line}" for i, line in enumerate(lines))
            return f"Here's the content of {path} with line numbers:\n{numbered}"
    
    elif cmd == "create":
        path = Path(tool_call["input"]["path"])
        if path.exists():
            return f"Error: File {path} already exists"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(tool_call["input"]["file_text"])
        return f"File created successfully at: {path}"
    
    elif cmd == "str_replace":
        path = Path(tool_call["input"]["path"])
        if not path.exists():
            return f"Error: The path {path} does not exist."
        content = path.read_text()
        old_str = tool_call["input"]["old_str"]
        new_str = tool_call["input"]["new_str"]
        count = content.count(old_str)
        if count == 0:
            return f"No replacement was performed, old_str `{old_str}` did not appear verbatim in {path}."
        if count > 1:
            return f"No replacement was performed. Multiple occurrences of old_str `{old_str}` found."
        path.write_text(content.replace(old_str, new_str, 1))
        return "The memory file has been edited."
    
    elif cmd == "delete":
        path = Path(tool_call["input"]["path"])
        if not path.exists():
            return f"Error: The path {path} does not exist"
        if path.is_dir():
            import shutil
            shutil.rmtree(path)
        else:
            path.unlink()
        return f"Successfully deleted {path}"
    
    return f"Unknown command: {cmd}"


def run_agent_with_memory(user_message: str, session_id: str) -> str:
    """Run Claude with memory tool enabled."""
    messages = [{"role": "user", "content": user_message}]
    
    while True:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            tools=[{"type": "memory_20250818", "name": "memory"}],
            messages=messages,
        )
        
        if response.stop_reason == "end_turn":
            # Extract text response
            return next(
                block.text for block in response.content
                if hasattr(block, "text")
            )
        
        # Handle tool calls
        tool_results = []
        for block in response.content:
            if block.type == "tool_use" and block.name == "memory":
                result = handle_memory_tool_call({
                    "name": block.name,
                    "input": block.input
                })
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })
        
        # Continue the loop
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})
```

### Multi-Session Software Development Pattern

Anthropic's own recommended pattern for long-running software projects:

**Session 1 (Initializer):**
```
memory/
├── PROGRESS.md    ← what's done, what's next, current blockers
├── FEATURES.md    ← checklist of all features in scope
└── STARTUP.sh     ← script to initialize environment (install deps, etc.)
```

**Every subsequent session:**
1. Claude reads PROGRESS.md → recovers full project state in seconds
2. Works on next item in FEATURES.md
3. Updates PROGRESS.md with what was completed and what's next
4. Marks features complete only after end-to-end verification

**Result:** Each new session has a complete, accurate handoff — no re-exploration needed.

### Security: Path Traversal Protection

The API docs explicitly warn about path traversal attacks:

```python
from pathlib import Path

MEMORY_BASE = Path("./memories").resolve()

def safe_path(user_path: str) -> Path:
    """Validate path is within /memories directory."""
    full_path = (MEMORY_BASE / user_path.lstrip("/")).resolve()
    
    # Critical: check resolved path is still within memory dir
    if not str(full_path).startswith(str(MEMORY_BASE)):
        raise ValueError(f"Path traversal attempt detected: {user_path}")
    
    return full_path
```

### Pairing with Compaction

The memory tool is designed to work alongside Anthropic's compaction API:

- **Compaction:** server-side summarization of old conversation turns when approaching context limit
- **Memory tool:** client-side persistence of important facts across compaction boundaries

Together: compaction keeps the active context window manageable; memory files preserve critical information that compaction might summarize away.

---

## Surface 3: Claude Managed Agents Memory (Public Beta)

Anthropic's managed agents platform now supports persistent memory across sessions, available in public beta.

### How It Works

- Memories are stored as files in a filesystem managed by Anthropic
- Developers can read, edit, and delete memory files via the Claude Console or API
- Multiple agents can share memory (one agent writes, another reads)
- Supports learning from past sessions: agents improve at recurring workflows

### What's Different from the Memory Tool API

| Dimension | Memory Tool API | Managed Agents Memory |
|-----------|----------------|----------------------|
| Hosting | Your infrastructure | Anthropic-hosted |
| Control | Full client-side | Console + API |
| Multi-agent sharing | Manual | Built-in |
| Setup | You implement handlers | Zero config |
| ZDR support | Yes | Enterprise option |

### Use Case

The primary use case is enterprise agents that need to:
- Remember company-specific guidelines across sessions
- Share learned workflows between multiple agent instances
- Track in-progress work without losing state on restart

---

## Claude Code Memory vs. the Memory Tool API

These are separate systems for separate contexts:

| | Claude Code memory | Memory Tool API |
|-|--------------------|-----------------|
| **Who it's for** | Developers using Claude Code CLI/IDE | Developers building Claude API apps |
| **File location** | `~/.claude/projects/.../memory/` | Your `/memories` dir (you choose) |
| **Auto-loaded** | Yes (first 200 lines of MEMORY.md) | No (Claude calls `view` command) |
| **Format** | Markdown | Any text format |
| **MCP compatible** | Yes (via settings.json) | Via API |
| **Auto Dream** | Yes (built-in consolidation) | You implement consolidation |

---

## Sources

- [Memory Tool - Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)
- [How Claude remembers your project - Claude Code Docs](https://code.claude.com/docs/en/memory)
- [Claude Code Dreams: Anthropic's New Memory Feature (claudefa.st)](https://claudefa.st/blog/guide/mechanics/auto-dream)
- [Anthropic adds memory to Claude Managed Agents (SD Times)](https://sdtimes.com/anthropic/anthropic-adds-memory-to-claude-managed-agents/)
- [Anthropic launches Memory in Claude Agents for enterprise (TestingCatalog)](https://www.testingcatalog.com/anthropic-launches-memory-in-claude-agents-for-enterprise/)
- [Claude Code Memory System Explained (Milvus Blog)](https://milvus.io/blog/claude-code-memory-memsearch.md)
- [Claude Code Memory Guide 2026: CLAUDE.md vs Auto Memory (LaoZhang AI Blog)](https://blog.laozhang.ai/en/posts/claude-code-memory)
- [GitHub: thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)
- [Inside Claude Code: Architecture Behind Tools, Memory, Hooks, MCP (Penligent)](https://www.penligent.ai/hackinglabs/inside-claude-code-the-architecture-behind-tools-memory-hooks-and-mcp/)
