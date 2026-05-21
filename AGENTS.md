# OpenCode Project Guidelines

This document defines project-specific conventions, architecture boundaries, and documentation routing for the UET RAG project.

## Project Overview

Stack:

* Python RAG pipeline
* FastAPI backend
* Vanilla JS frontend
* Qdrant vector database
* Gemini-based generation

Primary goals:

* accurate retrieval
* citation-grounded answers
* stable streaming UX
* maintainable modular pipeline

---

# Key Directories

```text
rag_core/       # RAG pipeline
backend/app/    # FastAPI backend
frontend/       # Static frontend
docs/           # Project documentation
data/           # PDFs, stores, evaluation artifacts
```

Important:

* `rag_core/config.py` is the single source of configuration
* keep step modules single-responsibility
* shared utilities belong in `rag_core/common/`

---

# Development Rules

## Do

* Preserve metadata keys:

  * `source`
  * `page`
  * `doc_id`

* Keep prompts strict and citation-focused

* Keep `/chat/stream` SSE format stable

* Reuse embeddings/models when possible

* Prefer focused incremental changes

* Add shared pipeline logic to:

  * `rag_core/common/`
  * `rag_core/pipeline.py`

---

## Don't

* Don't hardcode API keys or model names
* Don't modify parent-child retrieval unless explicitly requested
* Don't permanently store uploads unless requested
* Don't add dependencies unnecessarily
* Don't modify unrelated files
* Don't perform broad refactors without justification

---

# Security Rules

* Never commit secrets or API keys
* Use `.env` for credentials and configuration
* Validate uploads and external inputs
* Keep auth logic centralized in:

  * `backend/app/core/security.py`

---

# Performance Rules

* Parsing and embedding are expensive
* Avoid rebuilding retrievers unnecessarily
* Keep retrieval and streaming lightweight
* Avoid unnecessary context loading

---

# Testing Rules

Primary validation methods:

* `rag_core/main_test.py`
* unit tests in `rag_core/tests/`
* manual backend API checks
* retrieval quality verification

Before completion:

* verify retrieval quality
* verify citations
* verify SSE stability
* verify no regression in API behavior

---

# Documentation Routing

Load only documentation relevant to the current subsystem.

## RAG Tasks

Read:

* `docs/rag/`
* `docs/evaluation/`
* `docs/debugging/`

Examples:

* retrieval
* embeddings
* reranking
* chunking
* hallucination analysis

---

## Backend Tasks

Read:

* `docs/api/`
* `docs/architecture/`

Examples:

* FastAPI
* auth
* endpoints
* schemas
* streaming APIs

---

## Frontend Tasks

Read:

* `docs/frontend/`
* relevant API contracts

Examples:

* UI
* state
* streaming UX
* API integration

---

## Debugging Tasks

Prioritize:

* `docs/debugging/`
* subsystem-specific documentation

Avoid loading unrelated documentation.

---

# Code Conventions

## Naming

* Python files/functions: `snake_case`
* Python classes: `PascalCase`
* Constants: `UPPER_SNAKE_CASE`
* JS variables/functions: `camelCase`
* CSS classes: `kebab-case`

---

## Style

* Python indentation: 4 spaces
* Keep formatting consistent with existing files
* Avoid mass formatting/reflow
* Prefer readable incremental edits

---

# Helpful Commands

```bash
# Install dependencies
python -m pip install -r requirements.txt

# Run RAG smoke test
python rag_core/main_test.py

# Run backend
uvicorn backend.app.main:app --reload

# Run evaluation
python rag_core/ragas_eval.py --dataset data/dataset.json --out data/result.csv --records-in data/ragas_records.json

# Run tests
cd rag_core/tests && python -m unittest test_logging_utils test_pdf_utils test_embeddings test_pipeline -v
```

---

## Agent skills

### Issue tracker

Issues and PRDs are tracked in GitHub Issues for `DinhIchMinhHoang/RAG-Philosophy`. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default five-label triage vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

This repo uses a single-context domain-doc layout. See `docs/agents/domain.md`.

---

# References

* Project documentation: `docs/`
* Active plans: `docs/plans/`
* Agent conventions: `docs/agents/`
* Architecture details: `docs/architecture/`

Keep this document aligned with project architecture and pipeline evolution.
