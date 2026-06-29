# Multi-Agent Research System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A production-grade, multi-agent AI research system that autonomously plans, executes, and synthesizes comprehensive research reports. Built on a modular agent architecture with specialized **Manager**, **Researcher**, and **Reporter** agents, the system performs intelligent task planning, deep web research with hybrid retrieval, and structured report generation.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [System Components](#system-components)
  - [Agents](#agents)
  - [Processing Nodes](#processing-nodes)
  - [Schemas](#schemas)
  - [Memory Store](#memory-store)
  - [MCP Tools](#mcp-tools)
- [Evaluation](#evaluation)
- [API Reference](#api-reference)
- [Technology Stack](#technology-stack)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The Multi-Agent Research System automates the entire research workflow -- from understanding a user's query to delivering a well-structured, source-cited report. The system uses a pipeline of specialized AI agents, each responsible for a distinct phase of the research process:

1. **Planning** -- The Manager agent decomposes a user query into an actionable research plan
2. **Research** -- The Researcher agent discovers sources, reads web pages, and generates factual findings using a ReAct-style reflection loop
3. **Reporting** -- The Reporter agent synthesizes all findings into a comprehensive, structured report

The system supports **parallel research execution** across multiple topics, **hybrid retrieval** (dense + sparse), **intelligent reflection** for research quality assurance, and a **memory store** for caching and reusing prior research results.

---

## Architecture

```
User Query
    |
    v
+-----------+        +-------------------+        +------------------+
|  Manager  |------->|   Research Plan   |------->|   Researcher     |
|  Agent    |        |  (topic + points) |        |   Agent          |
+-----------+        +-------------------+        +------------------+
                                                          |
                              +---------------------------+---------------------------+
                              |                           |                           |
                              v                           v                           v
                       +-----------+             +----------------+            +-----------+
                       |  URL      |             |    Page        |            |  Chunker  |
                       | Discovery |             |    Reader      |            |           |
                       +-----------+             +----------------+            +-----------+
                              |                           |                           |
                              +---------------------------+---------------------------+
                                                          |
                                                          v
                                                   +------------+
                                                   |   Hybrid   |
                                                   |  Retriever |
                                                   | (FAISS+    |
                                                   |   BM25)    |
                                                   +------------+
                                                          |
                              +---------------------------+---------------------------+
                              |                           |                           |
                              v                           v                           v
                       +-----------+             +----------------+            +-----------+
                       | Finding   |             |   Reflection   |            |  ReAct    |
                       | Generator |             |   (Quality     |            |  Loop     |
                       |           |             |    Check)      |            |           |
                       +-----------+             +----------------+            +-----------+
                                                          |
                                                          v
                                              +---------------------+
                                              |   list[Finding]     |
                                              +---------------------+
                                                          |
                                                          v
                                              +---------------------+
                                              |      Reporter       |
                                              |      Agent          |
                                              +---------------------+
                                                          |
                                                          v
                                              +---------------------+
                                              |   Research Report   |
                                              | (sections + sources) |
                                              +---------------------+
```

---

## Key Features

### Multi-Agent Orchestration
- **Manager Agent** -- Intelligently decomposes queries into research plans using `gpt-oss-20b`
- **Researcher Agent** -- Executes parallel research across multiple topics with `ThreadPoolExecutor`
- **Reporter Agent** -- Synthesizes findings into structured reports using `llama-4-scout-17b-16e-instruct`

### Advanced Retrieval System
- **Hybrid Retrieval** -- Combines FAISS dense vector search with BM25 sparse keyword matching
- **Reranking** -- Cross-encoder reranking for improved result relevance
- **ReAct Reflection Loop** -- Self-correcting research with quality assessment and iterative refinement

### Web Research Pipeline
- **URL Discovery** -- Serper API-powered web search with deduplication
- **Page Reading** -- Trafilatura-based content extraction with metadata
- **Document Chunking** -- Intelligent text segmentation for optimal retrieval

### Memory & Caching
- **Research Memory Store** -- Persistent JSON-based storage with cosine similarity search
- **Query Deduplication** -- Automatic reuse of prior research for similar queries

### MCP (Model Context Protocol) Support
- **MCP Search Server** -- FastMCP-based web search tool server
- **MCP Search Client** -- Drop-in replacement for direct API calls via stdio transport

### Evaluation Framework
- **BEIR Benchmark Support** -- Standardized evaluation on information retrieval datasets
- **Custom Metrics** -- NDCG, MAP, and other IR metrics

---

## Project Structure

```
multi-agent-research-system/
|
|-- agents/                          # Core AI agents
|   |-- __init__.py
|   |-- manager.py                   # Manager agent - query decomposition & planning
|   |-- researcher.py                # Researcher agent - parallel research execution
|   |-- reporter.py                  # Reporter agent - report synthesis
|
|-- nodes/                           # Processing pipeline nodes
|   |-- url_discovery.py             # Web search & URL discovery
|   |-- page_reader.py               # Web page content extraction
|   |-- chunking.py                  # Document chunking & segmentation
|   |-- hybrid_retriever.py          # Dense + sparse hybrid retrieval
|   |-- retriever.py                 # Base retriever interface
|   |-- sparse_retriever.py          # BM25 sparse retrieval
|   |-- reranker.py                  # Cross-encoder result reranking
|   |-- finding_generator.py         # LLM-based finding generation
|   |-- reflect.py                   # ReAct reflection & quality check
|
|-- schemas/                         # Pydantic data models
|   |-- state.py                     # AgentState - overall workflow state
|   |-- plan.py                      # Plan - research plan schema
|   |-- findings.py                  # Finding & Fact - research findings
|   |-- report.py                    # Report - final report schema
|   |-- chunk.py                     # Chunk - document chunk schema
|   |-- source.py                    # Source - URL source schema
|   |-- retrieval.py                 # RetrievalResult - retrieval output
|   |-- reflection.py                # Reflection - quality assessment
|   |-- page.py                      # Page - web page schema
|   |-- corpus.py                    # ResearchCorpus - document corpus
|   |-- page_reader_result.py        # PageReaderResult - page reading output
|
|-- prompts/                         # LLM system prompts
|   |-- manager_prompt.py            # Manager agent prompt
|   |-- reporter_prompt.py           # Reporter agent prompt
|   |-- research_findingnode_prompt.py # Finding generator prompt
|
|-- tools/                           # Utility tools
|   |-- __init__.py
|   |-- web_search.py                # Serper API web search
|   |-- web_reader.py                # Trafilatura content extraction
|   |-- json_extractor.py            # JSON extraction from LLM output
|
|-- LLM/                             # LLM client configuration
|   |-- client_groq.py               # Groq API client setup
|
|-- memory/                          # Research memory & caching
|   |-- store.py                     # ResearchMemoryStore with similarity search
|   |-- research_history.json        # Persistent research cache
|
|-- mcp_tools/                       # MCP (Model Context Protocol) tools
|   |-- search_server.py             # FastMCP web search server
|   |-- search_client.py             # MCP client wrapper
|
|-- eval/                            # Evaluation framework
|   |-- datasets/                    # Evaluation datasets
|   |-- results/                     # Evaluation results
|   |-- beir_loader.py               # BEIR dataset loader
|   |-- eval_beir.py                 # BEIR evaluation script
|
|-- workflows/                       # Workflow orchestration
|
|-- main.py                          # Application entry point
|-- requirements.txt                 # Python dependencies
|-- .gitignore                       # Git ignore rules
|-- README.md                        # Project documentation
```

---

## Installation

### Prerequisites

- Python 3.11 or higher
- [Groq API Key](https://console.groq.com/keys) for LLM inference
- [Serper API Key](https://serper.dev/) for web search

### Clone the Repository

```bash
git clone https://github.com/kapil-chouhan-ai/multi-agent-research-system.git
cd multi-agent-research-system
```

### Create Virtual Environment

```bash
# Using venv
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `groq` | 1.4.0 | Groq API client for LLM inference |
| `langchain-core` | 1.4.1 | LangChain core framework |
| `langchain-community` | 0.4.2 | LangChain community integrations |
| `sentence-transformers` | 5.5.1 | Dense embedding models |
| `faiss-cpu` | 1.14.2 | FAISS vector search |
| `trafilatura` | 2.1.0 | Web content extraction |
| `pydantic` | 2.13.4 | Data validation |
| `python-dotenv` | 1.2.2 | Environment variable management |
| `transformers` | 5.12.0 | Hugging Face transformers |
| `torch` | 2.12.0 | PyTorch deep learning |
| `scikit-learn` | 1.9.0 | Machine learning utilities |
| `pandas` | 3.0.3 | Data manipulation |
| `numpy` | 2.0.1 | Numerical computing |

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Serper API Configuration (for web search)
SERPER_API_KEY=your_serper_api_key_here
```

### LLM Model Configuration

| Agent | Model | Purpose |
|-------|-------|---------|
| Manager | `openai/gpt-oss-20b` | Research planning & decomposition |
| Finding Generator | `openai/gpt-oss-20b` | Fact extraction from evidence |
| Reporter | `meta-llama/llama-4-scout-17b-16e-instruct` | Report synthesis |

Models are configured in their respective agent files and can be swapped by modifying the `model` parameter.

---

## Usage

### Basic Usage

Run the research system with a query:

```bash
python main.py
```

The system will prompt for a research query and execute the full pipeline:

```
Enter your research query: Latest advancements in quantum computing 2024

____Planning..._____
__Planning Done__

____Collecting Resources..._____
url_1
url_2
...
Discovered 15 unique URLs

_____Base corpus built, researching topics in parallel___
Researching topic 1: Quantum computing breakthroughs 2024
Researching topic 2: IBM quantum processor developments
Researching topic 3: Quantum error correction advances
...

_____Research Done___

___Generating Report...___

=== FINAL REPORT ===
Title: Latest Advancements in Quantum Computing (2024)
Executive Summary: [...]
Sources: [...]
```

### Researcher Agent Configuration

The `Researcher` agent accepts the following configuration parameters:

```python
from agents.researcher import Researcher

researcher = Researcher(
    url_discovery=url_discovery_node,
    page_reader=page_reader_node,
    chunker=chunker_node,
    embedding_model=embedding_model,
    finding_generator=finding_generator_node,
    reflect_node=reflection_node,
    reranker=reranker_node,          # Optional
    top_k=5,                          # Retrieval top-k
    pool_size=20,                     # Web search pool size
    rerank_top_n=5,                   # Reranking top-n
    max_react_iters=2,                # Max reflection iterations
    max_workers=4,                    # Parallel topic workers
)
```

### Using MCP Search Client

To use the MCP (Model Context Protocol) search client instead of direct API calls:

```python
from mcp_tools.search_client import MCPWebSearchTool

search_tool = MCPWebSearchTool()
results = search_tool.search("quantum computing")
```

### Memory Store

```python
from memory.store import ResearchMemoryStore

# Initialize memory store with embedding model
memory = ResearchMemoryStore(
    path="memory/research_history.json",
    embedding_model=embedding_model,
    similarity_threshold=0.86
)

# Check for similar prior research
prior_result = memory.find_similar("your query")
if prior_result:
    print("Found cached research result!")

# Save research result
memory.save("your query", agent_state)
```

---

## System Components

### Agents

#### Manager Agent (`agents/manager.py`)

The Manager agent is responsible for query understanding and research planning. It:
- Accepts a natural language research query
- Decomposes it into a structured `Plan` with a main topic and research points
- Preserves user-specified research points if explicitly provided
- Optimizes research points for web search (removes ambiguity, keeps concise)
- Enforces a maximum of 5 research points

**Input:** User query string  
**Output:** `Plan` schema with `main_topic` and `research_points`

#### Researcher Agent (`agents/researcher.py`)

The Researcher agent executes the core research pipeline with parallel topic processing:

1. **URL Discovery** -- Searches the web for each research point using Serper API
2. **Page Reading** -- Extracts clean text content from discovered URLs
3. **Chunking** -- Segments pages into searchable chunks
4. **Hybrid Retrieval** -- Uses FAISS (dense) + BM25 (sparse) for relevant chunk retrieval
5. **Reranking** -- Reorders results by relevance using cross-encoder
6. **Finding Generation** -- Extracts structured facts from evidence using LLM
7. **Reflection** -- Quality-checks findings; triggers follow-up search if insufficient

The ReAct loop allows iterative refinement: if findings are insufficient, the agent performs a refined search and re-retrieves.

**Input:** `Plan` schema  
**Output:** `list[Finding]` -- structured findings per topic

#### Reporter Agent (`agents/reporter.py`)

The Reporter agent synthesizes all findings into a comprehensive report:
- Aggregates findings from all research topics
- Generates a structured report with sections, executive summary, and source citations
- Uses `llama-4-scout-17b-16e-instruct` for high-quality report generation

**Input:** `list[Finding]`  
**Output:** `Report` schema with sections and sources

### Processing Nodes

| Node | File | Purpose |
|------|------|---------|
| URL Discovery | `nodes/url_discovery.py` | Web search via Serper API with deduplication |
| Page Reader | `nodes/page_reader.py` | Content extraction via Trafilatura |
| Chunking | `nodes/chunking.py` | Document segmentation for retrieval |
| Hybrid Retriever | `nodes/hybrid_retriever.py` | FAISS dense + BM25 sparse retrieval |
| Sparse Retriever | `nodes/sparse_retriever.py` | BM25 keyword-based retrieval |
| Reranker | `nodes/reranker.py` | Cross-encoder relevance reranking |
| Finding Generator | `nodes/finding_generator.py` | LLM-based fact extraction |
| Reflection | `nodes/reflect.py` | Quality assessment & query refinement |

### Schemas

All data structures use **Pydantic v2** for validation and serialization:

| Schema | File | Description |
|--------|------|-------------|
| `AgentState` | `schemas/state.py` | Complete workflow state container |
| `Plan` | `schemas/plan.py` | Research plan with topic and points |
| `Finding` | `schemas/findings.py` | Research finding with facts and sources |
| `Fact` | `schemas/findings.py` | Individual fact with source citations |
| `Report` | `schemas/report.py` | Final structured report |
| `Chunk` | `schemas/chunk.py` | Document chunk for retrieval |
| `Source` | `schemas/source.py` | URL source reference |
| `RetrievalResult` | `schemas/retrieval.py` | Retrieval output with chunks |
| `Reflection` | `schemas/reflection.py` | Quality assessment result |
| `Page` | `schemas/page.py` | Web page content |
| `ResearchCorpus` | `schemas/corpus.py` | Collection of chunks |
| `PageReaderResult` | `schemas/page_reader_result.py` | Page reading output |

### Memory Store (`memory/store.py`)

The `ResearchMemoryStore` provides:
- **Persistent Storage** -- JSON file-based research history
- **Similarity Search** -- Cosine similarity over query embeddings for finding related prior research
- **Exact Match Fallback** -- String comparison when no embedding model is available
- **Configurable Threshold** -- Adjustable similarity threshold (default: 0.86)

### MCP Tools (`mcp_tools/`)

The MCP (Model Context Protocol) integration provides:

- **`search_server.py`** -- FastMCP server exposing `web_search` tool via stdio transport
- **`search_client.py`** -- Async client with synchronous wrapper (`MCPWebSearchTool`)
- Drop-in replacement for `tools.web_search.WebSearchTool` with zero changes to calling code

---

## Evaluation

The retrieval pipeline is evaluated using the **BEIR (Benchmarking IR)** framework, a widely used benchmark for evaluating information retrieval systems across multiple domains.

The evaluation compares four retrieval strategies:

* **Dense Retrieval** (Sentence Transformers + FAISS)
* **Sparse Retrieval** (BM25)
* **Hybrid Retrieval** (Dense + Sparse Fusion)
* **Hybrid + Cross-Encoder Reranking**

---

## Evaluation Datasets

| Dataset  | Domain                       | Corpus Size | Sampled Queries |
| -------- | ---------------------------- | ----------: | --------------: |
| SciFact  | Scientific Literature        |       5,183 |             166 |
| NFCorpus | Medical Retrieval            |       3,633 |             166 |
| FiQA     | Financial Question Answering |      57,638 |             166 |

---

## Benchmark Results

| Dataset      | Method                |     NDCG@10 |  Recall@100 |
| ------------ | --------------------- | ----------: | ----------: |
| **SciFact**  | Dense                 |     0.68316 |     0.93072 |
|              | Sparse                |     0.58662 |     0.80703 |
|              | Hybrid                |     0.68581 |     0.93373 |
|              | **Hybrid + Reranker** | **0.69954** | **0.93373** |
| **NFCorpus** | Dense                 |     0.28512 | **0.29273** |
|              | Sparse                |     0.25162 |     0.19549 |
|              | Hybrid                |     0.28682 |     0.28595 |
|              | **Hybrid + Reranker** | **0.32894** |     0.28595 |
| **FiQA**     | Dense                 | **0.40633** | **0.72400** |
|              | Sparse                |     0.18233 |     0.36391 |
|              | Hybrid                |     0.32006 |     0.68595 |
|              | Hybrid + Reranker     |     0.39865 |     0.68595 |

---

## Observations

### SciFact

* Dense retrieval provides a strong baseline.
* Hybrid retrieval slightly improves retrieval quality.
* Cross-encoder reranking achieves the highest ranking performance.

### NFCorpus

* This is the most challenging dataset in the evaluation.
* Sparse retrieval performs noticeably worse than dense retrieval.
* Reranking improves NDCG@10 from **0.28682 → 0.32894**.

### FiQA

* Dense retrieval performs best on this dataset.
* Hybrid retrieval reduces ranking quality compared to dense retrieval.
* Cross-encoder reranking recovers most of the lost performance.

---

## Evaluation Metrics

| Metric         | Description                                                                                                                                            |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **NDCG@10**    | Measures ranking quality by rewarding relevant documents appearing near the top of the ranked list. Higher values indicate better ranking performance. |
| **Recall@100** | Measures the proportion of relevant documents retrieved within the top 100 results. Higher values indicate better retrieval coverage.                  |

---

## Reproducing Results

Run the evaluation on all supported datasets:

```bash
python -m eval.eval_beir \
    --datasets scifact nfcorpus fiqa \
    --total-queries 500
```

Evaluate a single dataset:

```bash
python -m eval.eval_beir \
    --datasets scifact \
    --total-queries 166
```

Disable cross-encoder reranking:

```bash
python -m eval.eval_beir \
    --datasets scifact \
    --no-rerank
```

---

## API Reference

### WebSearchTool (`tools/web_search.py`)

```python
from tools.web_search import WebSearchTool

tool = WebSearchTool(api_key="your_serper_api_key")
results = tool.search("quantum computing breakthroughs")
# Returns: list[dict] with keys: title, snippet, url
```

### WebReader (`tools/web_reader.py`)

```python
from tools.web_reader import WebReader

reader = WebReader()
result = reader.read("https://example.com/article")
# Returns: {success: bool, content: str, title: str}
```

### HybridRetrieverNode (`nodes/hybrid_retriever.py`)

```python
from nodes.hybrid_retriever import HybridRetrieverNode
from schemas.corpus import ResearchCorpus

retriever = HybridRetrieverNode(
    embedding_model=model,
    top_k=5,
    pool_size=20
)
retriever.build(ResearchCorpus(chunks=chunks))
result = retriever.retrieve("your query")
```

### ResearchMemoryStore (`memory/store.py`)

```python
from memory.store import ResearchMemoryStore

store = ResearchMemoryStore(
    path="memory/research_history.json",
    embedding_model=embedding_model,
    similarity_threshold=0.86
)

# Find similar research
state = store.find_similar("your query")

# Save research
store.save("your query", agent_state)
```

---

## Technology Stack

| Category | Technology |
|----------|------------|
| **Language** | Python 3.11+ |
| **LLM Framework** | Groq API |
| **LLM Models** | GPT-OSS 20B, Llama 4 Scout 17B |
| **Orchestration** | LangChain |
| **Embeddings** | Sentence Transformers |
| **Vector Search** | FAISS |
| **Sparse Retrieval** | BM25 (rank-bm25) |
| **Web Search** | Serper API |
| **Content Extraction** | Trafilatura |
| **Data Validation** | Pydantic v2 |
| **MCP Framework** | FastMCP |
| **ML Framework** | PyTorch, Transformers |
| **Evaluation** | BEIR Benchmark |

---

## Roadmap

- [x] Multi-agent architecture (Manager, Researcher, Reporter)
- [x] Hybrid retrieval (FAISS + BM25)
- [x] ReAct reflection loop
- [x] Parallel topic processing
- [x] MCP tool integration
- [x] Memory store with similarity search
- [x] BEIR evaluation framework
- [ ] Streaming report generation
- [ ] Multi-modal research (images, tables)
- [ ] Persistent vector database (Chroma, Weaviate)
- [ ] Web UI interface
- [ ] Multi-language support

---

## Acknowledgments

- [Groq](https://groq.com/) for high-speed LLM inference
- [Serper](https://serper.dev/) for web search API
- [LangChain](https://www.langchain.com/) for the orchestration framework
- [Sentence Transformers](https://www.sbert.net/) for embedding models
- [Trafilatura](https://trafilatura.readthedocs.io/) for web content extraction

---
