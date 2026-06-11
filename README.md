# Multi-Agent Research System (V1)

A multi-agent research system built from scratch without LangChain or LangGraph.

## Overview

This project implements a simple research workflow using multiple specialized agents:

```text
User Query
    ↓
Manager Agent
    ↓ Plan
Researcher Agent
    ↓ Findings
Reporter Agent
    ↓ Report
```

Each agent communicates through structured Pydantic schemas.

---

## Architecture

### Manager Agent

Responsibilities:

* Understand user query
* Create a research plan
* Generate research points

Input:

```python
query: str
```

Output:

```python
Plan
```

---

### Researcher Agent

Responsibilities:

* Perform web searches
* Extract factual information
* Associate facts with sources

Input:

```python
Plan
```

Output:

```python
list[Finding]
```

---

### Reporter Agent

Responsibilities:

* Analyze findings
* Generate report title
* Generate final summary

Input:

```python
list[Finding]
```

Output:

```python
Report
```

---

## Project Structure

```text
multi_agents/
│
├── agents/
│   ├── manager.py
│   ├── researcher.py
│   └── reporter.py
│
├── prompts/
│   ├── manager_prompt.py
│   ├── researcher_prompt.py
│   └── reporter_prompt.py
│
├── schemas/
│   ├── state.py
│   ├── plan.py
│   ├── finding.py
│   └── report.py
│
├── tools/
│   └── web_search.py
│
├── workflows/
│   └── orchestrator.py
│
└── main.py
```

---

## Schemas

### Plan

Represents the manager's research plan.

### Fact

Represents a factual statement and supporting sources.

### Finding

Represents research findings for a specific topic.

### Report

Represents the final summarized report.

### AgentState

Stores workflow state throughout execution.

---

## Workflow State

```python
AgentState(
    query=query,
    plan=Plan,
    findings=list[Finding],
    report=Report
)
```

---

## Technologies

* Python
* Pydantic
* Groq API
* Serper API

---
### Output by v1
<img width="1554" alt="Architecture" src="https://github.com/user-attachments/assets/04b40551-871b-41c0-9726-bf114ef84177" />

## Future Improvements

### V2

* Web page reading
* Content chunking
* Relevant chunk retrieval
* Better source attribution

### V3

* Parallel researchers
* ReAct-style research loops
* Human-in-the-loop review

### V4

* Persistent memory
* Research history
* Multi-session workflows

---

## Goal

The objective of this project is to understand how agent systems work internally by building them from scratch rather than relying on agent frameworks.
