Each arrow is a typed Pydantic schema, not a raw string or dict.

---

## Agents

### Manager Agent

Receives the raw user query. Produces a `Plan` — a structured breakdown of what needs to be
researched and in what order.

**Input:** `query: str`
**Output:** `Plan`

Key responsibility: decompose an open-ended question into focused research points that the
Researcher can execute one by one.

---

### Researcher Agent

Receives the `Plan`. For each research point, performs web searches using Serper API, extracts
factual claims, and associates each claim with its source URL.

**Input:** `Plan`
**Output:** `list[Finding]`

Key responsibility: grounded retrieval — every fact comes with a source. No hallucination from
the LLM; facts come from actual web content.

---

### Reporter Agent

Receives all findings. Synthesizes them into a coherent report with a title and summary.

**Input:** `list[Finding]`
**Output:** `Report`

Key responsibility: structure, not invention. The Reporter only works with what the Researcher
returned.

---

## Schemas (Pydantic Contracts)

Agent-to-agent communication is validated at each step.

```python
class Plan(BaseModel):
    research_points: list[str]

class Fact(BaseModel):
    statement: str
    source: str

class Finding(BaseModel):
    topic: str
    facts: list[Fact]

class Report(BaseModel):
    title: str
    summary: str

class AgentState(BaseModel):
    query: str
    plan: Plan | None = None
    findings: list[Finding] = []
    report: Report | None = None
```

Using Pydantic here means: if an agent returns malformed output, it fails loudly at the schema
boundary rather than silently corrupting downstream agents.

---

```## Project Structure
multi-agent-research-system/
│
├── LLM/                    # Groq API client wrapper and LLM call abstraction
│
├── agents/
│   ├── manager.py          # Manager agent logic
│   ├── researcher.py       # Researcher agent logic
│   └── reporter.py         # Reporter agent logic
│
├── prompts/
│   ├── manager_prompt.py   # Manager system prompt
│   ├── researcher_prompt.py
│   └── reporter_prompt.py
│
├── schemas/
│   ├── state.py            # AgentState
│   ├── plan.py             # Plan
│   ├── finding.py          # Fact, Finding
│   └── report.py           # Report
│
├── tools/
│   └── web_search.py       # Serper API wrapper
│
├── workflows/
│   └── orchestrator.py     # Runs agents in sequence, manages state
│
├── main.py                 # Entry point
├── .gitignore
└── README.md
```
---

## Setup

### Prerequisites

- Python 3.9+
- Groq API key → [console.groq.com](https://console.groq.com)
- Serper API key → [serper.dev](https://serper.dev)

### Install

```bash
git clone https://github.com/kapil-18-pythonic/multi-agent-research-system.git
cd multi-agent-research-system
pip install -r requirements.txt
```

### Configure environment

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_key_here
SERPER_API_KEY=your_serper_key_here
```

### Run

```bash
python main.py
```

You will be prompted to enter a research query. The system will:
1. Plan the research
2. Perform web searches
3. Generate a structured report

---

## Tech Stack

| Component | Tool | Reason |
|-----------|------|--------|
| LLM inference | Groq API | Fast inference via LPU hardware |
| Web search | Serper API | Google search results via API |
| Schema validation | Pydantic | Typed contracts between agents |
| Orchestration | Plain Python | No framework — explicit state passing |

---

## Current Limitations (V1)

- Researchers run sequentially, not in parallel
- No retry logic if a web search returns empty results
- No evaluation of report quality
- No memory across sessions — each run starts fresh
- LLM output parsing can fail if the model deviates from the expected schema format

---

## Roadmap

### V2 — Better Retrieval
- Read full web pages, not just search snippets
- Chunk and retrieve relevant sections
- Improve source attribution

### V3 — Parallel and Iterative
- Run multiple Researcher agents in parallel (one per research point)
- ReAct-style research loop: search → evaluate → decide to search again or stop
- Human-in-the-loop: approve the plan before research starts

### V4 — Memory and Persistence
- Persist research history across sessions
- Reuse prior findings for related queries
- Multi-session workflows

---

## Goal

Understand how multi-agent systems work at the mechanism level — schema design, prompt
construction, state management, tool calling — before adding framework abstractions on top.
