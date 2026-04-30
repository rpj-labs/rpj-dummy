# Setup 1: The LLM Wiki (Compiled Knowledge Base)

**Inspiration:** Andrej Karpathy's `llm-wiki.md` (April 2026)  
**Neuroscience analog:** Hippocampal indexing + neocortical semantic store (compiled)  
**Complexity:** Low  
**Best scale:** Personal or domain research corpus, ~10K–500K words

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        LLM WIKI SYSTEM                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  raw/                    wiki/                                     │
│  ├── paper1.pdf          ├── index.md          ← catalog          │
│  ├── article2.html       ├── log.md            ← audit trail      │
│  ├── notes3.md           ├── AGENTS.md         ← schema rules     │
│  └── video4.txt          │                                         │
│  [immutable]             ├── concepts/                             │
│                          │   ├── memory-consolidation.md           │
│                          │   ├── sharp-wave-ripples.md             │
│                          │   └── theta-oscillations.md             │
│                          │                                         │
│                          ├── entities/                             │
│                          │   ├── buzsaki-gyorgy.md                 │
│                          │   └── hippocampus.md                    │
│                          │                                         │
│                          └── topics/                               │
│                              ├── sleep-consolidation.md            │
│                              └── ai-memory-design.md               │
│                                                                    │
│  OPERATIONS:                                                        │
│  Ingest → Query → Lint                                             │
└──────────────────────────────────────────────────────────────────┘
```

### Ingest Flow
```
New source added to raw/
    ↓
LLM reads source + reads index.md
    ↓
Extracts: key concepts, entities, claims, relationships
    ↓
For each concept/entity:
    ├── Exists in wiki? → UPDATE page, add new section, update claims
    └── New?           → CREATE page with summary + cross-links
    ↓
Update index.md (add entry + brief description)
    ↓
Append to log.md (timestamp, source, pages touched, key claims added)
```

### Query Flow
```
User question
    ↓
LLM reads index.md (finds relevant pages)
    ↓
LLM reads 3–10 relevant wiki pages
    ↓
Synthesizes answer with [[wikilink]] citations
    ↓
Optionally: good answers filed as new wiki pages
```

### Lint Flow (periodic, weekly or on-demand)
```
LLM reads entire wiki (or section)
    ↓
Flags: contradictions, stale claims, orphan pages
       missing cross-references, topics lacking sources
    ↓
Produces: lint-report.md with prioritized fixes
    ↓
Agent fixes flagged issues
```

---

## User Stories

### US-1.1: Research Synthesis
**As a** researcher building a knowledge domain (neuroscience, climate, market analysis),  
**I want to** continuously add papers and articles to my corpus  
**So that** I can ask synthesis questions across all my sources without re-reading everything.

**Acceptance criteria:**
- Adding a new paper updates all relevant concept pages automatically
- A question like "how do SWRs relate to memory consolidation?" draws from 5+ sources without prompting
- Answer cites specific wiki pages, not raw source filenames

### US-1.2: Gap Detection
**As a** researcher preparing a literature review,  
**I want to** know what topics in my domain are underrepresented in my corpus  
**So that** I can identify what to read next.

**Acceptance criteria:**
- Lint operation produces a "coverage gaps" section in lint-report.md
- Agent identifies concepts referenced in multiple pages but lacking their own dedicated page
- Agent suggests specific source types to fill gaps

### US-1.3: Contradiction Resolution
**As a** researcher who has been tracking a fast-moving field over months,  
**I want to** find when two sources make conflicting claims  
**So that** I can resolve the contradiction and update my understanding.

**Acceptance criteria:**
- Lint flags direct contradictions (e.g., "Source A says X; Source B says ¬X on page Y")
- Each contradiction stored in wiki/contradictions.md with both claims and sources
- Agent can recommend resolution based on publication date, sample size, replication

### US-1.4: Onboarding a New Collaborator
**As a** team lead who has maintained an LLM wiki for 6 months,  
**I want to** give a new team member rapid access to accumulated knowledge  
**So that** they can reach productivity without reading 200 papers.

**Acceptance criteria:**
- New team member can query the wiki and get synthesis answers within minutes of access
- Wiki produces an onboarding guide (list of most important concept pages in reading order)
- All claims are citeable back to raw sources

### US-1.5: Evolving the Schema
**As a** domain expert whose understanding of the field has shifted,  
**I want to** reorganize how wiki pages are categorized  
**So that** the structure reflects current understanding, not initial assumptions.

**Acceptance criteria:**
- AGENTS.md can be edited to reflect new schema conventions
- Agent can run a migration pass that renames/restructures pages per new schema
- Migration is logged in log.md with before/after diff

---

## Requirements

### Functional Requirements

| ID | Requirement |
|----|------------|
| F1.1 | System maintains a `raw/` directory as immutable source truth |
| F1.2 | System maintains a `wiki/` directory with LLM-generated/maintained markdown |
| F1.3 | `index.md` is updated on every ingest; queryable as the first step of every retrieval |
| F1.4 | `log.md` is append-only; every operation (ingest, query, lint) appends an entry |
| F1.5 | `AGENTS.md` defines wiki schema conventions; agent reads it before any operation |
| F1.6 | Ingest creates/updates concept pages, entity pages, and topic pages as appropriate |
| F1.7 | Cross-page linking uses `[[wikilink]]` syntax; index tracks all existing pages |
| F1.8 | Query operation reads index first, then fetches 3–10 pages, then synthesizes |
| F1.9 | Lint operation detects: contradictions, orphan pages, stale claims, coverage gaps |
| F1.10 | System supports human-readable markdown (portable; no proprietary formats) |

### Non-Functional Requirements

| ID | Requirement |
|----|------------|
| NF1.1 | Ingest of a single source completes in <60 seconds for papers up to 50 pages |
| NF1.2 | Query latency <10 seconds for corpora up to 500K words |
| NF1.3 | All files are plain markdown; no database, no vector store required |
| NF1.4 | System must be LLM-agnostic (works with Claude, GPT-4o, Gemini, local models) |
| NF1.5 | Total wiki size stays <2x the raw source size (compression, not expansion) |
| NF1.6 | Human can read, edit, or delete any wiki page directly; system remains consistent |

---

## User Scenarios

### Scenario A: The Neuroscience Researcher (6-month build)

**Month 1:** Researcher adds 20 foundational papers (Buzsáki, Davachi, Eichenbaum). System creates 40 concept pages, 15 entity pages. Index has 55 entries.

**Month 3:** After adding 60 more papers, query "explain the role of theta oscillations in memory retrieval" returns a synthesized 800-word answer drawing from 8 pages, with precise wikilink citations.

**Month 6:** Lint pass finds: 3 contradictions (two papers give conflicting SWR frequency ranges), 12 orphan pages (cited but never expanded), 4 coverage gaps (entorhinal cortex subregions underrepresented). Researcher spends 2 hours resolving contradictions; adds 6 targeted papers to fill gaps.

**Success signal:** Researcher can answer a visiting colleague's complex synthesis question in <30 seconds using the wiki, without opening a single paper.

### Scenario B: The AI Product Team Knowledge Base

**Setup:** Team maintains a wiki of competitor products, user research, and internal architecture decisions. 3 team members each ingest from their respective domains.

**Daily use:** Before a design meeting, PM queries "what do users say about memory limitations in AI assistants?" Wiki synthesizes findings from 12 user interviews + 3 competitor analyses, citing specific interview pages.

**Quarterly lint:** Detects that "user persona: power user" is mentioned in 15 pages but has no dedicated entity page. Agent creates it automatically and backfills cross-links.

**Success signal:** New team member answers a product question accurately on day 2 using only the wiki, no onboarding session required.

### Scenario C: The Executive Intelligence Brief

**Setup:** Analyst ingests daily news, earnings reports, and market research into a domain wiki for a specific industry vertical.

**Weekly use:** "What are the key themes from the last 30 days?" produces a structured synthesis with claims, sources, and trend arrows — in 15 seconds vs. 4 hours of manual synthesis.

**Success signal:** Brief quality is indistinguishable from a manually written analyst report, at 1% of the time cost.

---

## Success Criteria and Capabilities

### What this setup does well

| Capability | Why |
|-----------|-----|
| **Synthesis across many sources** | Cross-links pre-built; no re-discovery per query |
| **Audit trail and explainability** | Every claim citeable to log.md + source in raw/ |
| **Portability** | Pure markdown; runs on any LLM; lives in any filesystem |
| **Human + agent collaboration** | Humans read; agents write; both can edit |
| **Contradiction detection** | Lint operation explicitly surfaces conflicting claims |
| **Coverage gap identification** | Lint produces reading recommendation list |
| **No infrastructure required** | No database, no vector store, no embeddings |
| **Schema evolution** | AGENTS.md is editable; migration passes restructure wiki |

### Limitations and Failure Modes

| Limitation | Mitigation |
|-----------|------------|
| **Scales poorly past ~500K words** (index.md becomes unwieldy) | Migrate to Setup 2 (HippoRAG) at that threshold |
| **No semantic search** (must describe what you want accurately) | Index-first navigation requires good index writing |
| **No prioritization** (all sources ingested equally) | Add salience scoring at ingest (see Setup 3) |
| **No real-time updates** (batch ingest, not streaming) | Run ingest agents on a schedule |
| **LLM errors propagate** (hallucinated cross-links in wiki pages) | Lint pass catches structural errors; citations point back to raw/ |
| **No episodic memory** (log.md is flat; no episode structure) | Use Setup 4 for long-running agent interactions |

### Capability Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| Knowledge synthesis | ★★★★★ | Core strength |
| Multi-hop reasoning | ★★★★☆ | Good via wikilinks; not as strong as graph-based |
| Real-time learning | ★★☆☆☆ | Batch ingest only |
| Episodic memory | ★☆☆☆☆ | Not designed for this |
| Contradiction handling | ★★★★☆ | Explicit lint operation |
| Portability | ★★★★★ | Pure markdown |
| Setup complexity | ★★★★★ | Trivially simple |
| Scalability | ★★☆☆☆ | Tops out ~500K words |
| Prioritized retention | ★★☆☆☆ | No salience scoring |
