# Backend-RAG Boundary

## Overview

The backend (`backend/app/`) wraps the RAG core (`rag_core/`) as a service layer. The boundary is defined by `RAGService` in `backend/app/services/rag_service.py`, which acts as a singleton facade to the pipeline.

## Responsibility Separation

### Backend Responsibilities (FastAPI)

- **HTTP Handling**: Request parsing, response formatting, error handling
- **Authentication**: JWT token generation/validation, password hashing
- **File Management**: Temporary file storage for uploaded PDFs
- **SSE Streaming**: Token-by-token response streaming
- **Database**: User management via SQLite/SQLAlchemy

### RAG Core Responsibilities (Python Pipeline)

- **PDF Parsing**: Hybrid two-pass algorithm (pymupdf4llm + Ollama)
- **Text Chunking**: Parent-child splitting with doc_id management
- **Vector Indexing**: Qdrant + InMemoryStore setup
- **Retrieval**: MultiVectorRetriever execution
- **Generation**: LLM chain setup and invocation

## Interface Contract

### Backend → RAG Core

```python
# backend/app/services/rag_service.py

# Import path resolution
import sys
import os
_RAG_CORE_DIR = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "rag_core"
))
if _RAG_CORE_DIR not in sys.path:
    sys.path.insert(0, _RAG_CORE_DIR)

from rag_core.step1_parser import HybridPDFParser
from rag_core.step2_chunker import chunk_documents
from rag_core.step3_vector_db import build_vector_db
```

### RAGService Public API

| Method | Input | Output | Notes |
|--------|-------|--------|-------|
| `ingest_file(filename, file_bytes)` | str, bytes | dict with status/pages/chunks | Saves to temp, parses, rebuilds retriever |
| `stream_answer(question)` | str | AsyncGenerator[str] | Yields tokens via Gemini astream |
| `has_sources` | - | bool | Property: True if retriever initialized |
| `source_count` | - | int | Property: Number of ingested files |
| `sources` | - | List[str] | Property: List of filenames |
| `reset()` | - | None | Clears all docs and resets retriever |

## Error Handling

### RAG Core Errors
- `ValueError`: Empty documents after parsing
- `KeyError`: Missing doc_id in metadata
- Parsing exceptions are caught and logged; fallback to raw text extraction

### Backend Errors
- HTTP 400: Invalid request (empty message, non-PDF upload)
- HTTP 401: Unauthorized (invalid/missing JWT)
- HTTP 404: File not found (document reset)
- HTTP 500: Internal server error (caught and exposed)

## State Management

### RAGService Singleton Pattern

```python
# backend/app/services/rag_service.py
rag_service = RAGService()  # Module-level singleton
```

State is maintained in instance variables:
- `_retriever`: MultiVectorRetriever or None
- `_all_child_docs`: List[Document]
- `_all_parent_docs`: List[Document]
- `_source_files`: List[str]
- `_upload_dir`: str (temporary directory)

### Memory Considerations

- Qdrant uses `:memory:` location (not persisted)
- Temporary upload directory cleaned on reset
- Document lists grow with each ingestion (no eviction)

## Testing Boundary

- Backend tested via manual API calls (`/documents/upload`, `/chat/stream`)
- RAG core tested via `python rag_core/main_test.py` smoke tests
- Unit tests in `rag_core/tests/` (9 tests, all passing)