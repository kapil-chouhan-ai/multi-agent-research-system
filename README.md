# Multi-Agent Research System

> **v2.0.0** — Plain Python. No agent frameworks. Typed schemas between agents. Retrieval-based research pipeline.

A multi-agent research system that takes a user query, decomposes it into research tasks, retrieves grounded information from the web, and produces a structured research report.

---
## Architecture
<img width="1536" alt="Architecture" src="https://github.com/user-attachments/assets/e26068e7-bc86-4dbd-a2f4-7081afd246ec" />

---
### v2.0.0 output :
<img width="790" alt="Architecture" src="https://github.com/user-attachments/assets/de22a950-3a30-49be-a13f-1b9c2355b5ad" />

---

## Agents

### Manager Agent

Receives the raw user query and creates a structured research plan.

**Input:** `str`
**Output:** `Plan`

Responsibilities:

* Identify the main topic
* Break the problem into focused research points
* Produce a structured plan for downstream agents

---

### Researcher Agent

Executes the research plan through a retrieval pipeline.

**Input:** `Plan`
**Output:** `list[Finding]`

Responsibilities:

* Discover relevant URLs using web search
* Read full web page content
* Chunk documents
* Build a retrieval corpus
* Retrieve evidence relevant to each research point
* Generate grounded findings with source attribution

Unlike V1, the Researcher does not rely only on search snippets.

---

### Reporter Agent

Transforms findings into a structured report.

**Input:** `list[Finding]`
**Output:** `Report`

Responsibilities:

* Generate a descriptive title
* Create an executive summary
* Organize findings into topic-specific sections
* Preserve source traceability

The Reporter only works from findings produced by the Researcher.

---

## Research Pipeline

The Researcher is internally composed of multiple nodes:

```text
Research Point
      │
      ▼
URL Discovery
      │
      ▼
Page Reader
      │
      ▼
Chunking
      │
      ▼
Research Corpus
      │
      ▼
Embedding + Retrieval
      │
      ▼
Relevant Chunks
      │
      ▼
Finding Generator
      │
      ▼
Finding
```

This architecture grounds report generation on retrieved page content instead of directly prompting an LLM with search results.

---

## Schemas (Pydantic Contracts)

Agent-to-agent communication is validated at every stage.

```python
class Plan(BaseModel):
    main_topic: str
    research_points: list[str]


class Fact(BaseModel):
    statement: str
    sources: list[str]


class Finding(BaseModel):
    topic: str
    facts: list[Fact]


class ReportSection(BaseModel):
    topic: str
    content: str
    sources: list[str]


class Report(BaseModel):
    title: str
    summary: str
    sections: list[ReportSection]


class AgentState(BaseModel):
    query: str
    plan: Plan | None = None
    findings: list[Finding] = []
    report: Report | None = None
```

Malformed agent output fails at schema boundaries instead of silently propagating through the system.

---

## Project Structure

```text
multi-agent-research-system/
│
├── LLM/
│   └── client_groq.py
│
├── agents/
│   ├── manager.py
│   ├── researcher.py
│   └── reporter.py
│
├── nodes/
│   ├── url_discovery.py
│   ├── page_reader.py
│   ├── chunking.py
│   ├── retriever.py
│   └── finding_generator.py
│
├── prompts/
│   ├── manager_prompt.py
│   ├── finding_generator_prompt.py
│   └── reporter_prompt.py
│
├── schemas/
│   ├── state.py
│   ├── plan.py
│   ├── finding.py
│   ├── report.py
│   ├── chunk.py
│   ├── page.py
│   ├── source.py
│   ├── corpus.py
│   └── retrieval.py
│
├── tools/
│   ├── web_search.py
│   └── web_reader.py
│
├── workflows/
│   └── orchestrator.py
│
├── testing/
│
├── main.py
├── requirements.txt
└── README.md
```

---

## Setup

### Prerequisites

* Python 3.10+
* Groq API key
* Serper API key

### Install

```bash
git clone https://github.com/kapil-chouhan-ai/multi-agent-research-system.git

cd multi-agent-research-system

pip install -r requirements.txt
```

### Configure Environment

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
SERPER_API_KEY=your_serper_api_key
```

### Run

```bash
python main.py
```

Example query:

```text
Research NVIDIA: LLMs, GPUs, AI Chips
```

---

## Tech Stack

| Component       | Tool                  |
| --------------- | --------------------- |
| LLM Inference   | Groq API              |
| Search          | Serper API            |
| Page Extraction | Trafilatura           |
| Embeddings      | Sentence Transformers |
| Vector Search   | FAISS                 |
| Validation      | Pydantic              |
| Orchestration   | Plain Python          |

---

## What's New in v2.0.0

* Full web page extraction instead of search-snippet-only research
* Retrieval-based research pipeline
* Recursive document chunking
* Embedding-based retrieval using FAISS
* Grounded finding generation from retrieved evidence
* Source attribution preserved throughout the pipeline
* Structured report generation with topic-level sections
* Stronger schema boundaries between components

---

## Current Limitations

* Research points are processed sequentially
* No reranking stage after retrieval
* No retry strategy for failed page extraction
* No domain filtering during URL discovery
* No memory across sessions
* Retrieval quality depends on embedding model quality

---

## Roadmap

v1.0  Basic Multi-Agent Research System
v2.0  Retrieval + Reranking
v2.1  Multi-Query Retrieval
v2.2  Parallel Research
v2.3  ReAct Agent
v2.4  Human-in-the-Loop
v2.5  Persistent Memory
v2.6  Multi-Session Memory

---

## Goal

Understand multi-agent systems from first principles:

* Schema design
* State management
* Prompt engineering
* Tool usage
* Retrieval pipelines
* Agent orchestration

before introducing frameworks such as LangGraph or other agent abstractions.
