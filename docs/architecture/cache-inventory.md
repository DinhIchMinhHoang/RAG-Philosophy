# Cache Inventory

## Summary

The system uses caching and short-lived state at several layers, but it does
not have one unified cache subsystem. The current cache-like behavior is split
across browser storage, in-process Python objects, retrieval memory stores,
Redis/Celery task result state, model artifact volumes, and HTTP cache-control
headers.

For notebook chat, the backend database remains the source of truth. Browser
cache is only a speed layer for restoring the latest visible notebook state.

## Cache Locations

| Layer | Location | Behavior | Purpose | Invalidation / TTL |
|---|---|---|---|---|
| Browser notebook cache | `frontend/src/ui/scenes/ChatScene.js` | `CONVERSATION_CACHE_TTL_MS`, `conversationCacheKey()`, `readCachedConversation()`, `writeCachedConversation()` store the latest notebook conversation snapshot in `localStorage`. | Show the last visible notebook conversation quickly while the UI syncs from `GET /api/notebooks/{notebook_id}/conversations/latest`. | 24 hours. Expired entries are ignored and removed from `localStorage`. |
| Browser source-selection cache | `frontend/src/ui/scenes/ChatScene.js` | `SOURCE_SELECTION_CACHE_TTL_MS`, `sourceSelectionCacheKey()`, `readCachedSourceSelection()`, `writeCachedSourceSelection()` store selected source IDs per notebook. | Preserve notebook source filters across switches/reloads. | 24 hours. Expired entries are ignored and removed from `localStorage`. |
| Browser auth token | `frontend/src/api/client.js` | `accessToken` is stored in `localStorage`. | Keep the JWT available for API requests after reload. | No client TTL. The token expires according to server-side JWT expiry; logout removes it. |
| Browser user profile | `frontend/src/state/store.js` | `currentUser` is stored in `localStorage`. Malformed JSON is cleared during load. | Restore the displayed user profile after reload. | No TTL. Logout or parse failure removes it. |
| Browser debug config | `frontend/src/utils/logger.js` | Reads `logLevel` from `localStorage`. | Persist local logging verbosity. | No TTL. |
| Admin UI memory | `frontend/src/ui/scenes/AdminScene.js` | `cachedUsers`, `cachedApiConfig`, and `cachedLibrary` keep API responses in module memory for filtering/rendering. | Avoid refetching while filtering admin lists during the same page session. | No TTL. Cleared by reload. |
| Backend Qdrant client reuse | `backend/app/ingest/qdrant_store.py` | `_cached_qdrant_client()` uses `@lru_cache(maxsize=8)` and `build_qdrant_client()` returns the cached client for the current settings. | Avoid rebuilding `QdrantClient` repeatedly. | LRU eviction after 8 setting combinations. Environment/config changes normally require process restart. |
| Core embedding object reuse | `rag_core/common/embeddings.py` | `get_embeddings()` uses `@lru_cache(maxsize=4)` keyed by model/device. | Reuse expensive `HuggingFaceEmbeddings` objects in the standalone `rag_core` path. | LRU eviction after 4 model/device combinations. Config changes normally require process restart or cache clear. |
| Embedding service model memory | `embedding_service/app/main.py` | `load_model()` loads `SentenceTransformer` once into `state.model`; requests call `_require_ready()` and `_encode()`. | Keep the embedding model resident instead of loading it per request. | Restart the embedding service. |
| Legacy backend RAG memory | `backend/app/services/rag_service.py` | `RAGService` keeps `_retriever`, `_all_child_docs`, `_all_parent_docs`, and `_source_files` in process memory. | Support the legacy singleton RAG service without rebuilding from scratch for every query. | `reset()` clears the state. Restart also clears it. |
| Core parent document store | `rag_core/step3_vector_db.py` | `_build_doc_store()` creates a LangChain `InMemoryStore` for parent documents. | Resolve child chunk hits back to parent context for `MultiVectorRetriever` and hybrid/rerank retrievers. | Ephemeral. Rebuilt when `build_vector_db()` runs; lost on process restart. |
| Core sparse retrieval index | `rag_core/hybrid_retriever.py` | `BM25ChildIndex` tokenizes child docs and keeps a BM25 index in memory. | Provide sparse candidates for hybrid/rerank retrieval. | Ephemeral. Rebuilt from child docs; lost on process restart. |
| Core dev vector store | `rag_core/config.py`, `rag_core/step3_vector_db.py` | `Config.QDRANT_LOCATION = ":memory:"` is used by the standalone core path. | Local/dev vector indexing without a persistent Qdrant service. | Lost on process restart. |
| Celery result backend | `backend/app/worker/celery_app.py` | Celery uses Redis as broker/result backend and sets `result_expires=3600`. | Hold task status/result metadata outside the worker process. | Celery result TTL is 3600 seconds. Broker queue behavior follows Redis/Celery configuration. |
| Docker model artifact cache | `docker-compose.yml`, `docker/embedding.Dockerfile` | `huggingface_cache` volume is mounted at `/cache/huggingface`; `HF_HOME`, `TRANSFORMERS_CACHE`, and `SENTENCE_TRANSFORMERS_HOME` point there. | Avoid downloading embedding model artifacts on every container rebuild/start. | No TTL. Remove the Docker volume to force a clean download. |
| Optional local LLM model cache | `docker-compose.yml` | `ollama_data` volume stores Ollama models when the `local-llm` profile is enabled. | Persist local LLM model artifacts. | No TTL. Remove the Docker volume to clear. |
| Persistent service volumes | `docker-compose.yml` | `postgres_data`, `minio_data`, and `qdrant_data` persist DB rows, uploaded objects, and vector storage. | Durable service data, not application cache. | No TTL. Remove volumes only during explicit data reset. |
| Chat SSE HTTP cache-control | `backend/app/routers/chat.py`, `docker/nginx/default.conf` | SSE responses set `Cache-Control: no-cache`; Nginx sets `proxy_cache off` and disables proxy buffering for `/api/chat/stream`. | Prevent stream caching/buffering from breaking token streaming. | No cached stream state. |
| Document serving HTTP cache-control | `backend/app/routers/documents.py` | Document responses set `Cache-Control: private, max-age=0, must-revalidate`. | Allow private browser storage only with revalidation. | Browser must revalidate before reuse. |
| Evaluation record reuse | `rag_core/ragas_eval.py` | `--records-in` loads precomputed records such as `data/ragas_records.json`. | Reuse expensive evaluation/retrieval-generation records. | Manual. No TTL. |

## What Is Not Cached

- Chat generation results are not semantically cached by question.
- Embedding vectors are not cached per input text in the application layer.
- Redis is used as Celery infrastructure state, not as a general application
  cache for API responses or retrieval answers.
- Backend database state is durable persistence, not cache. Notebook chat
  history, saved notes, ingest jobs, document metadata, and users should be
  treated as source-of-truth records.

## Operational Notes

- Browser cache can become stale. The notebook cache must stay scoped by
  notebook ID, and the backend conversation endpoint must remain the authority.
- `localStorage` is visible to browser scripts. Do not store secrets beyond the
  existing JWT token contract, and do not treat client cache as trusted input.
- Python `lru_cache` entries are per process. If Qdrant or embedding settings
  change, restart the affected backend/worker/core process unless the code
  explicitly clears the cache.
- In-memory retrieval structures are suitable for local/core flows but should
  not be confused with the persistent backend ingest path.
- Model artifact volumes improve cold-start cost but can hide stale model
  downloads. Remove `huggingface_cache` when a clean model artifact refresh is
  required.
- SSE routes intentionally avoid cache. Changing Nginx buffering or cache
  settings can regress streaming behavior.

## Existing Documentation Pointers

- Frontend cache and source-of-truth behavior: `docs/frontend/state-management.md`
- Docker volumes and deployment persistence: `docs/architecture/deployment.md`
- Core vector store behavior: `docs/rag/vector-store.md`
- Evaluation record reuse: `docs/evaluation/retrieval-metrics.md`
