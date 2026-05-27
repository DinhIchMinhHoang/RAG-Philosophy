# Architecture Overview

## System Architecture

The RAG Philosophy system is a full-stack document question-answering application consisting of four main components:

```
+----------------------------------------------------------------------------+
|                     Frontend (Vanilla JS ES Modules)                      |
|   +-- src/App.js           - Scene manager: landing/auth/dashboard/chat   |
|   +-- src/api/client.js    - API client with SSE streaming support        |
|   +-- src/api/auth.js      - Auth: signup/login/token management          |
|   +-- src/api/rag.js       - Document upload, job polling, chat streaming |
|   +-- src/api/notebooks.js - Notebook/conversation API calls              |
|   +-- src/api/admin.js     - Admin API calls                              |
|   +-- src/state/store.js   - localStorage-based state                     |
|   +-- src/ui/              - UI component modules                         |
|   +-- src/animations/      - Animation effects                            |
+-----------------------------+----------------------------------------------+
                              | HTTP / SSE via Nginx (port 80)
                              v
+----------------------------------------------------------------------------+
|                         Nginx Reverse Proxy                                |
|  Serves static frontend, proxies /api/* to backend:8000                   |
|  Disables buffering for SSE streaming (/api/chat/stream)                  |
+-----------------------------+----------------------------------------------+
                              |
                              v
+----------------------------------------------------------------------------+
|                       FastAPI Backend (Port 8000)                         |
|   +-- main.py              - App entry, CORS, middleware, error handlers  |
|   +-- routers/                                                             |
|   |   +-- auth.py          - POST /api/signup, /api/login, /api/change-pw|
|   |   +-- chat.py          - POST /api/chat, /api/chat/stream (SSE)      |
|   |   +-- ingest.py        - POST /api/documents, GET/DELETE, reindex    |
|   |   +-- documents.py     - Page image, file download endpoints         |
|   |   +-- notebooks.py     - Notebook CRUD, conversations, notes, files  |
|   |   +-- admin.py         - Admin: users, library, documents, api-config|
|   |   +-- password_reset.py- Forgot/verify/reset flow                    |
|   +-- services/                                                            |
|   |   +-- chat_runtime.py  - Persistent retrieval and citation runtime   |
|   |   +-- chat_history.py  - Chat message history management             |
|   |   +-- embedding_client.py - HTTP client to embedding service         |
|   |   +-- rag_service.py   - Legacy singleton (not production path)      |
|   +-- core/                                                                |
|   |   +-- security.py      - JWT handling (HS256, Argon2)                |
|   |   +-- settings.py      - Service runtime configuration               |
|   |   +-- dependencies.py  - FastAPI dependency injection                |
|   +-- models.py            - SQLAlchemy ORM models                        |
|   +-- schemas.py           - Pydantic request/response schemas            |
|   +-- database.py          - SQLAlchemy engine and session factory        |
+-----------------------------+----------------------------------------------+
                              |
                              +--- Celery Worker ---> Background ingest jobs
                              |
                              v
+----------------------------------------------------------------------------+
|                    RAG Core Pipeline (rag_core/)                          |
|                                                                             |
| Parsing -> Chunking -> Embedding -> Retrieval -> Generation                |
|                                                                             |
| step1_parser.py     - HybridPDFParser (PyMuPDF + optional Z.AI OCR)      |
| step2_chunker.py    - Parent/child chunking                                |
| step3_vector_db.py  - Vector store construction                            |
| step4_generator.py  - Prompt + LLM generation chain                       |
| pipeline.py         - Orchestration wrapper                                |
| common/             - Shared helpers: embeddings, LLM, logging, prompts   |
| hybrid_retriever.py - BM25 + dense RRF experiments                        |
| rerank_retriever.py - Cohere reranking experiments                        |
+----------------------------------------------------------------------------+
```

## Infrastructure Layer

```
+----------+  +----------+  +----------+  +----------+  +----------+  +----------+
|  Redis   |  | Postgres |  |  MinIO   |  |  Qdrant  |  |Embedding |  |  Ollama  |
|7-alpine  |  |16-alpine |  |RELEASE   |  |v1.13.4   |  |Service   |  |(optional)|
|(queue)   |  |(relational)||2023-10   |  |(vectors) |  |(HF model)|  |(local LLM)|
+----------+  +----------+  +----------+  +----------+  +----------+  +----------+
```

## Key Technologies

| Component | Technology | Notes |
|-----------|-----------|-------|
| PDF Parsing | PyMuPDF + pymupdf4llm | Hybrid approach |
| OCR (optional) | Z.AI GLM-OCR Layout Parsing API | VLM-based for complex pages |
| HTML/DOCX/MD Parsing | BeautifulSoup, pypandoc, markdown | Multi-format support |
| Embeddings | HuggingFace Transformers | microsoft/harrier-oss-v1-270m (default) |
| Vector Store | Qdrant 1.13.4 | Persistent, Cosine distance, 640-dim |
| Relational DB | PostgreSQL 16 (prod) / SQLite (dev) | SQLAlchemy ORM |
| Object Storage | MinIO (prod) / local filesystem (dev) | S3-compatible |
| Queue | Celery + Redis | Background ingest jobs |
| Backend | FastAPI + Uvicorn | Python 3.11 |
| Auth | JWT (HS256, PyJWT) + Argon2 | passlib.context |
| Frontend | Vanilla JS ES modules + CSS3 | No framework, no build step |
| LLM Providers | Gemini, OpenCode/OpenAI-compatible, local Ollama | Configurable via LLM_MODE |
| Reverse Proxy | Nginx 1.27-alpine | Serves frontend, routes /api/* |

## Configuration Split

- **backend/app/core/settings.py** -- Service runtime config: database URL, Redis, MinIO, Qdrant connection, retrieval mode, LLM mode, auth secrets
- **rag_core/config.py** -- RAG core config: chunk sizes, embedding model, parser settings, OCR credentials, provider defaults

Both must be kept in sync when changing model names, retrieval parameters, or Qdrant collection.

## Data Flow

1. **Upload**: Frontend -> POST /api/documents -> Backend creates DocumentRecord + IngestJob -> stores file in object storage -> enqueues Celery task (or sync if queue idle)
2. **Ingestion**: Worker fetches file -> parses (PDF/DOCX/HTML/MD) -> chunks into parent/child -> embeds child chunks -> upserts vectors to Qdrant -> persists chunk metadata in PostgreSQL
3. **Chat**: User question -> POST /api/chat/stream -> question embedding -> Qdrant search (filtered by owner/notebook/version) -> child->parent chunk mapping in SQL -> grounded context -> LLM generation -> SSE token stream
4. **Response**: Token-by-token streaming with structured citations array in final event, each with source, page, document_id, chunk_id, doc_id, score

## Security Notes

- JWT tokens expire after 60 minutes (configurable via ACCESS_TOKEN_EXPIRE_MINUTES)
- Passwords hashed with Argon2 via passlib
- API keys stored in .env (GEMINI_API_KEY, OPENCODE_API_KEY, SECRET_KEY)
- CORS allows all origins in dev (restrict in production)
- Weak SECRET_KEY detection on production startup

## File Structure

```
RAG-Philosophy/
+-- rag_core/              # RAG pipeline steps + experiments
|   +-- config.py          # Core RAG configuration
|   +-- pipeline.py        # Orchestrator
|   +-- step1_parser.py    # Hybrid PDF parser
|   +-- step2_chunker.py   # Parent-child chunking
|   +-- step3_vector_db.py # Qdrant + retriever construction
|   +-- step4_generator.py # LLM generation chain
|   +-- common/            # Shared utilities
|   |   +-- embeddings.py  # Embedding helpers
|   |   +-- llm.py         # LLM provider factory
|   |   +-- logging_utils.py
|   |   +-- pdf_utils.py
|   |   +-- prompts.py     # Prompt templates
|   +-- hybrid_retriever.py
|   +-- rerank_retriever.py
|   +-- cohere_reranker.py
|   +-- tests/
+-- backend/               # FastAPI application
|   +-- app/
|       +-- main.py
|       +-- routers/       # auth, chat, ingest, documents, notebooks, admin, password_reset
|       +-- services/      # chat_runtime, chat_history, embedding_client, rag_service
|       +-- core/          # security, settings, dependencies
|       +-- models.py
|       +-- schemas.py
|       +-- database.py
+-- frontend/              # Vanilla JS SPA
|   +-- index.html
|   +-- src/
|       +-- App.js
|       +-- api/           # client, auth, rag, notebooks, admin
|       +-- state/         # store.js
|       +-- ui/            # UI component modules
|       +-- animations/    # Visual effects
+-- data/                  # Raw PDFs, processed markdown, object store, evaluation
+-- docker/                # Dockerfiles, Nginx config
+-- docs/                  # Architecture, API, RAG, frontend, debugging docs
```