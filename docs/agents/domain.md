# Domain Docs

This repo uses a single-context domain-doc layout.

## Read order

Before changing code, relevant engineering skills should read:

- `CONTEXT.md` at the repo root, if it exists.
- `docs/adr/`, if it exists, for architectural decisions relevant to the task.
- Subsystem docs under `docs/`, following the routing rules in `AGENTS.md`.

If `CONTEXT.md` or `docs/adr/` do not exist, proceed silently.

## Current project areas

- `rag_core/`: RAG pipeline
- `backend/app/`: FastAPI backend
- `frontend/`: static frontend
- `docs/`: project documentation
