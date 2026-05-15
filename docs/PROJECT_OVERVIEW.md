# 1. Project Overview

This repository is a full-stack retrieval-augmented generation system for asking citation-grounded questions over course and reference PDFs. The current product shape is "Lumina notebook": users sign up, upload PDFs, wait for background indexing, then chat with the indexed sources through a browser UI.

The codebase currently has two related but distinct runtime paths:

- `rag_core/` is the reusable RAG pipeline. It parses PDFs, creates parent/child chunks, builds retrievers, and runs generation for local tests and experiments.
- `backend/app/` is the application service boundary. It adds authentication, document/job persistence, object storage, Celery ingest, Qdrant vector persistence, API contracts, and server-sent event streaming.

The high-level workflow is:

1. Upload a PDF through the frontend.
2. The backend stores the object, creates a `DocumentRecord`, creates an `IngestJob`, and enqueues Celery work.
3. The worker fetches the PDF, validates it, parses pages, chunks text into parent and child chunks, embeds child chunks, upserts child vectors into Qdrant, and persists parent/child chunk metadata in the database.
4. Chat retrieval embeds the user question, searches Qdrant for child chunks filtered by `pipeline_version`, maps hits back to parent chunks in SQL, and builds structured citations from the retrieved context.
5. The chat runtime sends the grounded context to the configured LLM provider and returns either a JSON answer or token-by-token SSE output.

Architecturally, this is a pragmatic transition from a notebook-style local RAG prototype into a service-oriented RAG application. The persistent backend path is the path to treat as the main application runtime. The standalone `rag_core/` path is still useful for experiments, smoke tests, and shared pipeline logic, but it is not itself a multi-instance production architecture.

# 2. Tech Stack Overview

## Backend And API

- **FastAPI + Uvicorn**: used for HTTP APIs, OpenAPI docs, dependency injection, and streaming responses.
- **Pydantic models**: used for request/response validation in routers.
- **SQLAlchemy ORM**: used for users, documents, ingest jobs, and chunk metadata.
- **JWT + Argon2**: used for bearer-token authentication and password hashing.

These choices are conventional for a Python service that needs typed APIs, simple auth, and a relational persistence layer.

## RAG And ML

- **LangChain**: used for document objects, retrievers, prompt templates, chains, Ollama chat, Gemini chat, OpenAI-compatible chat, and Qdrant integration.
- **PyMuPDF / pymupdf4llm**: used for PDF text and markdown extraction.
- **Ollama + `glm-ocr`**: used by the parser for complex pages requiring OCR/VLM extraction.
- **Hugging Face embeddings**: `microsoft/harrier-oss-v1-270m` is the current embedding model in `rag_core/config.py`.
- **Qdrant**: used as the vector database for child chunks.
- **BM25 (`rank_bm25`)**: used in `rag_core` hybrid retrieval experiments and retrievers.
- **Cohere reranking**: optional fail-open reranking support exists in `rag_core`.
- **RAGAS**: used for evaluation scripts and cached evaluation records.

The pipeline favors retrieval quality over minimum latency. Parent/child chunking and optional OCR improve answer quality for complex educational PDFs, but they add indexing cost and operational dependencies.

## LLM Providers

The project now supports two cloud provider families plus local fallback:

- **Gemini** through `langchain-google-genai`.
- **OpenCode/OpenAI-compatible APIs** through `langchain-openai`.
- **Local Ollama** through `ChatOllama`.

There are two knobs:

- `LLM_PROVIDER=auto|gemini|opencode` controls provider inference in `rag_core.common.llm`.
- `LLM_MODE=auto|gemini|opencode|local` controls backend chat runtime fallback behavior.

In `LLM_PROVIDER=auto`, model names beginning with `gemini` use Gemini; other names, such as `deepseek-v4-flash`, use the OpenCode/OpenAI-compatible path. `LLM_MODE=auto` tries the inferred cloud provider first and falls back to local Ollama if no tokens have been emitted.

## Queue, Database, And Storage

- **Celery + Redis**: used for background ingest jobs.
- **PostgreSQL**: used in Docker Compose as the service database.
- **SQLite**: still the code default if `DATABASE_URL` is not set.
- **MinIO**: used in Compose for object storage.
- **Local filesystem object storage**: still available through `OBJECT_STORAGE_BACKEND=local`.

The queue and persistence stack exists because PDF parsing, OCR, embedding, and indexing are too expensive to run synchronously inside an upload request.

## Frontend

- **Vanilla JavaScript ES modules**: used instead of React/Vue/etc.
- **Static HTML/CSS scenes**: one-page UI with scene transitions.
- **Fetch + ReadableStream**: used for HTTP and SSE-style chat streaming.
- **KaTeX and marked from CDN**: used for math and markdown rendering.
- **Material Icons from CDN**: used for UI icons.

The frontend is intentionally light on build tooling. That keeps local development simple, but it pushes more complexity into DOM manipulation and manual state management.

## Infrastructure And Dev Tooling

- **Docker Compose**: orchestrates Nginx, backend, worker, Redis, Postgres, MinIO, Qdrant, and Ollama.
- **Nginx**: serves the static frontend, proxies `/api/*`, forwards auth headers, and disables buffering for chat streaming.
- **Python `unittest`**: used for backend and `rag_core` tests.
- **Node test script**: `frontend/tests/api-rag.test.mjs` checks frontend API client behavior.

# 3. rag_core/ Analysis

`rag_core/` is the shared RAG engine. It is organized as a step pipeline:

- `step1_parser.py`: PDF parsing and OCR.
- `step2_chunker.py`: parent/child chunking.
- `step3_vector_db.py`: vector store and retriever construction.
- `step4_generator.py`: prompt and generation chain.
- `pipeline.py`: orchestration wrapper around the steps.
- `common/`: shared config-facing helpers for embeddings, LLMs, logging, and PDF path collection.

## Parsing Strategy

`HybridPDFParser` uses a two-pass strategy:

1. Scan pages with PyMuPDF and classify pages as simple or complex.
2. Extract simple pages with `pymupdf4llm`; process complex pages through rendered images and Ollama OCR, with fallback to PyMuPDF-based extraction.

The parser preserves `source` and `page` metadata. This is a strong design choice because source/page fidelity is required for citations. The tradeoff is operational cost: the OCR path depends on an available Ollama service and a pulled model, and parsing can become the slowest ingest stage.

## Chunking Strategy

`step2_chunker.py` implements manual parent-child splitting:

- Parent chunks default to 2000 characters with 200 overlap.
- Child chunks default to 500 characters with 100 overlap.
- Each parent gets a generated `doc_id`.
- Child chunks inherit the parent `doc_id`.
- Metadata is intentionally restricted to `source`, `page`, and `doc_id`.

The retrieval intent is clear: embed compact child chunks for accurate vector matching, then return larger parent chunks for generation context.

## Retrieval Architecture

There are two retrieval architectures in the repository.

In the standalone `rag_core` path:

- Child documents are embedded into Qdrant by `QdrantVectorStore.from_documents`.
- Parent documents are stored in a LangChain `InMemoryStore`.
- `MultiVectorRetriever` maps matching child chunks back to parent documents through `doc_id`.
- `Config.QDRANT_LOCATION` defaults to `:memory:`.

This is useful for local smoke tests and isolated experiments, but it is process-local. Parent context does not survive process restarts, and it is not shared across multiple API workers.

In the backend persistent path:

- Child vectors are stored in Qdrant with payload fields including `document_id`, `parent_chunk_id`, `source`, `page`, `pipeline_version`, `chunk_id`, `kind`, and `text`.
- Parent and child rows are stored in SQL as `DocumentChunk`.
- Chat retrieval searches Qdrant for child chunks and fetches parent chunk text from SQL by `parent_chunk_id`.

This is the more production-shaped path because Qdrant, SQL, and object storage can be shared by multiple processes.

## Hybrid Retrieval And Reranking Readiness

`rag_core` contains real hybrid and rerank code:

- `hybrid_retriever.py` builds a BM25 index over child docs and merges sparse/dense rankings with weighted RRF.
- `rerank_retriever.py` retrieves child candidates, reranks with Cohere, and maps back to parent docs.
- `cohere_reranker.py` is fail-open when reranking is unavailable.

However, this is not yet fully reflected in the backend production chat path. `backend/app/services/chat_runtime.py` has `RETRIEVAL_MODE=hybrid`, but `_retrieve_hybrid` currently logs a stub and delegates to dense retrieval. So hybrid retrieval is implemented in core experiments but not production-ready in the backend runtime.

## Generation And LLM Selection

`step4_generator.py` builds a citation-focused prompt and calls `build_chat_llm`. The shared LLM factory in `rag_core/common/llm.py` supports Gemini and OpenCode/OpenAI-compatible providers based on `LLM_PROVIDER` and `LLM_MODEL`.

One important inconsistency remains: some older comments and docs still describe the generator as Gemini-only, while the actual code now supports provider inference. Documentation and comments should be updated as provider switching stabilizes.

## Tests And Experiments

The `rag_core/tests/` directory covers:

- embedding construction
- LLM provider inference and construction
- pipeline orchestration
- PDF utilities
- logging utilities
- hybrid retrieval behavior
- rerank retrieval behavior

`rag_core/ragas_eval.py` provides RAGAS evaluation over `data/dataset.json` or cached records. This is valuable, but evaluation currently appears to be manually run rather than part of a continuous quality gate.

## Strengths

- Clear step-based pipeline.
- Strong metadata preservation.
- Parent-child retrieval is implemented deliberately.
- OCR fallback improves robustness for complex PDFs.
- Hybrid/rerank experiments exist and are testable.
- Shared LLM and embedding helpers reduce duplication.

## Weaknesses And Bottlenecks

- The standalone core path defaults to in-memory Qdrant and parent storage.
- OCR and embedding are expensive and can bottleneck indexing.
- The backend production retrieval path and `rag_core` retrievers are not fully unified.
- Config defaults drift across `.env.example`, `rag_core/config.py`, and backend settings.
- Generated `doc_id` values are UUIDv4 in the core chunker, so standalone core ingestion is not deterministic across rebuilds.

# 4. backend/ Analysis

`backend/app/` is the FastAPI application and the main operational runtime.

## API Structure

`backend/app/main.py` registers routers for:

- auth
- chat
- ingest
- document asset helpers

It also adds:

- CORS middleware
- request ID generation
- request completion logs
- JSON error envelopes for HTTP, validation, and unhandled exceptions
- startup security validation for weak `SECRET_KEY` outside development

Canonical non-admin endpoints are documented in `docs/api/non-admin-contract-v1.md`:

- `POST /api/signup`
- `POST /api/login`
- `POST /api/change-password`
- `POST /api/documents`
- `GET /api/documents`
- `DELETE /api/documents/{document_id}`
- `POST /api/documents/{document_id}/reindex`
- `GET /api/jobs/{job_id}`
- `POST /api/chat`
- `POST /api/chat/stream`

Legacy aliases are still active for compatibility.

## Authentication And Config

Auth uses:

- bearer JWT tokens
- `sub` set to username
- Argon2 password hashing
- `SECRET_KEY`, `ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES` from environment

This is enough for a local authenticated app, but it is not a complete production identity model. There is no refresh-token flow, no account recovery flow, and no current admin role implementation in the files inspected.

Runtime settings live in `backend/app/core/settings.py`. This is separate from `rag_core/config.py`, which creates a split configuration story:

- backend settings own database, Redis, object storage, Qdrant service URL, retrieval mode, and backend LLM mode
- `rag_core.config.Config` owns chunking, embedding, parser, core Qdrant defaults, and provider credentials/defaults

That split is workable but risky. The project guideline says `rag_core/config.py` is the single source of configuration, but the backend now has a service settings layer that is also authoritative for deployment. This should be documented or reconciled.

## Ingestion Flow

The persistent ingest flow is implemented and stateful:

1. `POST /api/documents` validates the upload and stores the object.
2. The backend creates `DocumentRecord` and `IngestJob`.
3. Celery receives `backend.app.worker.tasks.process_ingest_job`.
4. The worker executes `run_ingest_job`.
5. Job progress moves through `fetching_object`, `parsing`, `chunking`, `embedding`, `indexing_vector`, and `persisting_metadata`.
6. Qdrant vectors are deleted by document/version before reindex, then upserted with deterministic UUID5 point IDs.
7. Parent and child chunk metadata is persisted in SQL.

This is one of the strongest parts of the backend. It gives the UI real job polling and gives the system a path toward idempotent reindexing.

## Chat And Streaming

`backend/app/routers/chat.py` supports both non-streaming and streaming chat. Both require authentication and use `ChatRuntimeService`.

The chat runtime:

- embeds the question once per request
- searches Qdrant for child chunks
- filters by `pipeline_version` and `kind=child`
- maps child hits to parent SQL rows
- constructs citations from parent contexts
- sends grounded context to the selected LLM
- returns a safe no-evidence answer when retrieval is empty

The SSE contract is stable and useful:

- token event: `{"type":"token","token":"...","done":false}`
- final event: includes `answer` and `citations`
- error event: includes `error` and empty citations

This is production-shaped, but there are still risks:

- streaming errors after partial token emission cannot be cleanly retried by auto fallback
- frontend currently ignores final citations in the stream parser
- hybrid mode in backend chat is currently a dense passthrough stub

## Service Layer Organization

There are multiple service/retrieval surfaces:

- `chat_runtime.py`: current persistent chat runtime.
- `versioned_retrieval.py`: helper for parent chunk lookup by vector.
- `rag_service.py`: legacy singleton wrapping the in-memory `rag_core` pipeline.

This overlap is the main architectural risk in the backend. The persistent path and singleton path should not both be treated as first-class production retrieval systems. `rag_service.py` remains useful for legacy helpers and local behavior, but the persistent chat runtime should be the canonical backend path.

## Error Handling And Observability

Backend request logs and worker ingest logs are structured and include fields such as request ID, job ID, document ID, stage, duration, and error message. Qdrant upsert errors are wrapped with more useful status/reason/body information when possible.

This is good operational groundwork. Missing pieces include metrics, tracing, dashboarding, request-level LLM/retrieval latency breakdowns, and retrieval quality logging.

## Production Readiness

The backend is not fully production-ready yet. It is closer than the rest of the stack, but important gaps remain:

- permissive CORS
- weak development defaults
- split config authority
- no migrations framework visible in the repo
- minimal auth lifecycle
- no admin API implementation despite root task planning
- dense-only backend retrieval despite hybrid flags
- legacy route aliases removed

# 5. frontend/ Analysis

The frontend is a static single-page app implemented with HTML, CSS, and ES modules.

## UI Architecture

`frontend/index.html` contains the scene markup. `frontend/src/App.js` initializes:

- landing scene
- auth scene
- dashboard scene
- chat scene
- transition manager

State is mostly DOM-driven. `frontend/src/state/store.js` stores a user profile object in `localStorage`, and `frontend/src/api/client.js` stores the access token in `localStorage`.

This architecture is simple and build-free. The tradeoff is maintainability: as more notebook, admin, and citation UI features are added, DOM-level state coordination will become increasingly fragile.

## API Integration

`frontend/src/api/client.js` sets `BASE_URL = "/api"` and attaches bearer tokens to JSON requests. `frontend/src/api/rag.js` handles:

- `POST /api/documents` upload
- `GET /api/documents` listing
- `GET /api/jobs/{job_id}` polling
- `POST /api/chat/stream` streaming

This is aligned with the canonical backend API. The frontend also has tests for the RAG API client under `frontend/tests/`.

## Chat Flow And Streaming

The chat scene:

- lets users upload PDFs
- displays job progress by polling the backend
- sends questions over the stream endpoint
- renders streamed tokens incrementally
- supports markdown and KaTeX rendering
- includes a source viewer area for PDFs

The stream parser reads `data:` lines manually and handles token callbacks. It currently treats `done` as the end of the stream but does not appear to render the structured final citations as first-class citation cards. Some citation rendering still depends on text patterns such as `Trang`.

## Functional Versus Placeholder Areas

Functional:

- signup/login wiring
- authenticated API requests
- upload + job polling
- streaming chat
- PDF source viewer for document file endpoints

Demo or partially integrated:

- dashboard notebook management
- community notebook sections
- account profile fields beyond auth/password behavior
- admin UI, despite being listed in root planning docs
- structured citation UX from final SSE payload

The frontend is useful for demos and local E2E testing, but it is not yet a mature application shell. The chat/upload path is the real product surface; the notebook/dashboard/admin areas need backend-backed models before they should be treated as complete.

# 6. Docker / Infrastructure Analysis

## Compose Structure

`docker-compose.yml` defines:

- `nginx`
- `backend`
- `worker`
- `redis`
- `postgres`
- `minio`
- `qdrant`
- `ollama`

This matches the intended architecture in `TASKS.md`: one browser-facing entrypoint, separate API and worker processes, queue-backed ingestion, relational metadata storage, object storage, vector storage, and local model/OCR support.

## Networking And Request Flow

The browser is intended to call `http://localhost/api/*`. Nginx serves the frontend and proxies API traffic to `backend:8000`. The Nginx config explicitly forwards `Authorization`, which is required for protected chat and document APIs.

For `/api/chat/stream`, Nginx:

- uses HTTP/1.1
- disables proxy buffering
- disables cache
- sets long read/send timeouts
- forwards auth headers

This is the correct shape for SSE. Without these settings, streaming chat commonly fails through reverse proxies.

## Persistence Strategy

Compose uses named volumes for:

- Postgres data
- MinIO objects
- Qdrant storage
- Ollama model cache

Backend and worker also mount local source directories:

- `./data:/app/data`
- `./backend:/app/backend`
- `./rag_core:/app/rag_core`

The named volumes provide local durability. The source mounts make the stack convenient for development, but they also mean the running containers are not immutable production artifacts.

## Environment Variables

`.env.example` is broad and covers:

- database and Redis URLs
- Qdrant connection
- MinIO credentials
- auth settings
- LLM/provider settings
- retrieval settings
- local Ollama settings

There is visible drift:

- `rag_core/config.py` currently defaults `DEFAULT_LLM_MODEL` to `deepseek-v4-flash`.
- `.env.example` shows `LLM_MODEL=gemini-3.1-flash-lite-preview`.
- backend settings own service/runtime values that are not in `rag_core/config.py`.
- older docs still mention Gemini-only assumptions in places.

This does not prevent local operation, but it increases debugging cost. A future contributor may not know which default actually wins without reading both config modules and the Compose env file.

## Root-Level Architecture, Config, And Docs Files

Important root-level files:

- `AGENTS.md`: project rules and architecture boundaries for coding agents.
- `TASKS.md`: team plan and acceptance criteria; it includes admin goals that are not fully implemented.
- `TODO.md`: older completed pipeline refactor list; it is not a reliable current roadmap.
- `requirements.txt`: single Python dependency file for both core and backend.
- `.env.example`: main runtime template for Compose.
- `docker-compose.yml`: local orchestration contract.

The `docs/` tree is useful but partially stale:

- `docs/api/non-admin-contract-v1.md` is the best current API contract.
- `docs/rag/llm-provider-switch.md` documents recent Gemini/OpenCode switching.
- `docs/architecture/overview.md` still contains older assumptions such as simpler backend structure and Gemini-only language.
- `docs/frontend/api-contracts.md` and `docs/frontend/*` describe the client direction.
- `docs/debugging/*` and `docs/evaluation/*` support RAG troubleshooting and quality work.

The practical recommendation is to treat `docs/api/non-admin-contract-v1.md`, `.env.example`, and this overview as the current onboarding surface, while gradually pruning or updating older architecture docs.

## Deployment Readiness

The Compose stack is suitable for local development and a controlled demo. It is not yet a hardened production deployment:

- secrets are plain `.env` values
- CORS is permissive
- no TLS termination configuration is included
- backend and worker source are mounted live
- no database migrations are visible
- no autoscaling or resource limits are defined except an Ollama GPU reservation
- no centralized metrics/tracing stack is included

# 7. Current Project Status

## Working

- Canonical non-admin API contract exists and legacy aliases are removed.
- Auth, signup, login, and password change are implemented.
- Upload creates background ingest jobs instead of blocking the request.
- Celery worker performs parsing, chunking, embedding, Qdrant indexing, and metadata persistence.
- Qdrant payloads include source/page/document/chunk/version metadata.
- Chat retrieval returns parent contexts and structured citations.
- `/api/chat/stream` emits stable SSE token/final/error payloads.
- Frontend upload, job polling, and streaming chat are wired.
- Docker Compose includes the required service skeleton and persistent volumes.
- Unit/regression tests exist for important backend, frontend, and RAG behaviors.
- LLM factory can switch between Gemini and OpenCode/OpenAI-compatible providers.

## Partially Implemented

- Hybrid retrieval exists in `rag_core`, but backend `RETRIEVAL_MODE=hybrid` is currently a dense passthrough.
- Reranking exists in `rag_core`, but it is not integrated into the backend persistent chat path.
- Local LLM fallback exists in backend auto mode, but fallback after partial stream emission is intentionally limited.
- Admin functionality is planned in `TASKS.md`, but matching admin APIs/UI are not visible in the inspected backend/frontend files.
- Source/citation UI exists, but structured citation rendering from final SSE payload is not first-class yet.
- Evaluation scripts and datasets exist, but they are not a required CI gate.

## Missing Or High-Risk

- A single canonical runtime/config model.
- Database migrations.
- Production-grade secret management.
- Production CORS/TLS posture.
- Unified retrieval abstraction across `rag_core` and backend.
- Backend implementation for sparse retrieval and RRF over persistent data.
- Observability beyond structured logs.
- Clear admin/user authorization model.
- Deterministic document/chunk identity across all ingestion modes.
- Clear stale-doc cleanup policy for older docs.

The realistic assessment is that the project is a strong local/demo RAG application with meaningful backend persistence work already done. It is not yet a clean production RAG platform. The highest-risk areas are configuration drift, retrieval-path divergence, and the gap between planned admin/hybrid features and implemented runtime behavior.

# 8. Recommended Next Steps

## Immediate Fixes

1. Update stale docs and comments that still say the system is Gemini-only or purely in-memory.
2. Decide and document the canonical runtime path: backend persistent ingest should be the default for the app; `rag_core` standalone should be labeled as local/test/experimental.
3. Consolidate LLM documentation around `LLM_MODE`, `LLM_PROVIDER`, `LLM_MODEL`, `GEMINI_API_KEY`, `OPENCODE_API_KEY`, and `OPENCODE_API_BASE`.
4. Render final SSE citations in the frontend as structured citation items instead of relying mainly on text patterns.
5. Add a simple E2E smoke script for `signup -> upload -> job succeeded -> chat stream`.

## Short-Term Improvements

1. Implement real backend hybrid retrieval:
   - store or derive sparse terms for persisted child chunks
   - run dense Qdrant search plus sparse keyword/BM25 or Postgres FTS
   - merge with RRF
   - keep final output as parent chunks with citations
2. Integrate optional reranking into the backend persistent retrieval path with fail-open behavior and latency limits.
3. Add database migrations instead of relying on `Base.metadata.create_all`.
4. Tighten frontend API error states for expired tokens, failed jobs, empty retrieval, and backend downtime.
5. Add ingestion caching/idempotency tests around repeated uploads and reindexing.

## Medium-Term Architecture Goals

1. Make configuration ownership explicit. Either keep `backend/app/core/settings.py` as service runtime config and document the boundary, or move more runtime config through `rag_core/config.py` as AGENTS.md currently implies.
2. Retire or quarantine legacy singleton `RAGService` flows so production chat only uses persistent chunks and Qdrant.
3. Add observability:
   - retrieval latency
   - embedding latency
   - LLM latency
   - token streaming duration
   - ingest stage durations
   - empty-retrieval rate
4. Introduce retrieval evaluation gates using existing RAGAS and benchmark datasets.
5. Add admin/user role modeling if admin features remain in scope.
6. Harden Docker deployment:
   - remove live source mounts for production mode
   - add TLS/reverse-proxy guidance
   - define resource limits
   - move secrets out of plain examples for production documentation

## Long-Term RAG Evolution

1. Move from dense-only production retrieval to a hybrid/reranked pipeline as the default once measured quality improves.
2. Add embedding and pipeline version migration tools so old vectors/chunks can be rebuilt safely.
3. Add semantic caching for repeated questions and repeated document embeddings where appropriate.
4. Add agentic workflows only after retrieval quality is measured: examples include multi-query expansion, citation verification, and tool-assisted document comparison.
5. Add document-level access control if multi-user notebooks become real.
6. Add automated hallucination and citation-grounding checks to the release workflow.
7. Consider multi-tenant Qdrant/database partitioning if the app moves beyond a single shared knowledge base.

The next engineering milestone should be a reproducible local E2E pass through Compose, followed by unifying the backend retrieval path with the best tested `rag_core` retrieval capabilities.
