# Agent Guide

## Overview

This document guides AI agents (like OpenCode) working on the UET RAG project.

## Project Context

The UET RAG project is a Question-Answering system for philosophy course materials:
- **Purpose**: Answer student questions with citations from PDF textbooks
- **Domain**: Philosophy (Marxism, ethics, epistemology)
- **Language**: Vietnamese

## Architecture Summary

```
Frontend (Vanilla JS)
        ↓ HTTP/SSE
FastAPI Backend (Port 8000)
        ↓ Import
RAG Core Pipeline (Python)
  ├── step1_parser.py (PDF → Documents)
  ├── step2_chunker.py (Documents → Parent/Child chunks)
  ├── step3_vector_db.py (Chunks → Qdrant + InMemoryStore)
  └── step4_generator.py (Retriever + LLM → Answer)
```

## Key Files to Know

| File | Purpose |
|------|---------|
| `rag_core/config.py` | All configuration (chunk sizes, models, paths) |
| `rag_core/pipeline.py` | Main entry: `ingest()`, `build_pipeline()`, `query()` |
| `backend/app/services/rag_service.py` | Backend wrapper for pipeline |
| `backend/app/routers/chat.py` | SSE streaming endpoint |
| `frontend/api.js` | Frontend API client |

## Common Tasks

### Adding a New Feature

1. Follow brainstorming skill for design
2. Use config.py for new parameters
3. Add to appropriate step module (step1-4)
4. Write/update tests in `rag_core/tests/`

### Fixing a Bug

1. Use systematic-debugging skill
2. Check logs (logging_utils.py)
3. Add test case in tests/
4. Verify with `python rag_core/main_test.py`

### Running Tests

```bash
# Unit tests
cd rag_core/tests && python -m unittest test_logging_utils test_pdf_utils test_embeddings test_pipeline -v

# Pipeline smoke test
python rag_core/main_test.py

# Backend (manual)
uvicorn backend.app.main:app --reload
# Then test /documents/upload and /chat/stream
```

## Important Conventions

- **No hardcoding**: All config in `config.py`
- **Metadata preservation**: source, page, doc_id always present
- **Testing**: 9 unit tests must pass
- **Security**: Never commit API keys

## Agent Skills Available

- **brainstorming**: For creative/feature work
- **systematic-debugging**: For bug fixes
- **test-driven-development**: For implementations
- **requesting-code-review**: Before completing tasks

## Getting Help

- Read `AGENTS.md` in project root
- Check `memory-bank/rag_project/activeContext.md`
- Review `docs/` directory for specific topics