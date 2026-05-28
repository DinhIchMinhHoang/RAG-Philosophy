# Agent Guide

## Overview

This document guides AI agents (like OpenCode) working on the RAG-Philosophy project.

## Project Context

The RAG-Philosophy project is a Question-Answering system for course materials:
- **Purpose**: Answer student questions with citations from uploaded documents
- **Domain**: Philosophy (Marxism, ethics, epistemology)
- **Language**: Vietnamese

## Architecture Summary

```
Frontend (Vanilla JS ES Modules)
        | HTTP/SSE (via Nginx)
FastAPI Backend (Port 8000)
        | Import + Celery
RAG Core Pipeline (Python)
  +-- step1_parser.py  (PDF -> Documents)
  +-- step2_chunker.py (Documents -> Parent/Child chunks)
  +-- step3_vector_db.py (Chunks -> Qdrant vectors)
  +-- step4_generator.py (Retriever + LLM -> Answer)
```

## Key Files to Know

| File | Purpose |
|------|---------|
| rag_core/config.py | Core RAG configuration (chunk sizes, models, paths) |
| rag_core/pipeline.py | Orchestrator: ingest, build_pipeline, query |
| backend/app/core/settings.py | Service runtime configuration |
| backend/app/routers/chat.py | SSE streaming endpoint |
| frontend/src/api/client.js | Frontend API client |

## Common Tasks

### Adding a New Feature

1. Use config.py or settings.py for new parameters
2. Add to appropriate module
3. Write/update tests
4. Update relevant docs

### Fixing a Bug

1. Check logs
2. Write a test case reproducing the bug
3. Fix and verify

### Running Tests

```bash
# Python compile check
python -m compileall backend rag_core -q

# RAG core tests
python -m unittest discover rag_core/tests -v

# Backend tests
python -m unittest discover backend/tests -v

# Pipeline smoke test
python rag_core/main_test.py
```

## Important Conventions

- **No hardcoding**: All config in rag_core/config.py or backend/app/core/settings.py
- **Metadata preservation**: source, page, doc_id always present
- **Security**: Never commit API keys

## Getting Help

- Read docs/ directory for specific topics
- Review docs/PROJECT_OVERVIEW.md for comprehensive status