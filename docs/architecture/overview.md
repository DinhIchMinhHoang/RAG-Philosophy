# Architecture Overview

## System Architecture

The UET RAG system is a full-stack document question-answering application consisting of three main components:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Frontend (Vanilla JS)                          │
│   ├── script.js        - Morphing blob animations & UI effects         │
│   ├── api.js           - API client with SSE streaming support         │
│   ├── transitions.js   - Scene transition manager (landing/auth/chat) │
│   └── index.html       - Single-page app with scene management         │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │ HTTP/SSE
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)                         │
│   ├── main.py          - App entry, CORS, router registration          │
│   ├── routers/                                                         │
│   │   ├── auth.py      - /signup, /login, /change-password             │
│   │   ├── chat.py      - /chat/stream (SSE)                            │
│   │   └── documents.py - /documents/upload, /documents/sources        │
│   ├── services/                                                         │
│   │   └── rag_service.py - Singleton wrapping rag_core pipeline       │
│   ├── core/                                                             │
│   │   └── security.py  - JWT token handling (HS256, Argon2)           │
│   ├── models.py        - SQLAlchemy User model                        │
│   ├── schemas.py       - Pydantic request/response schemas            │
│   └── database.py      - SQLite connection                             │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │ Import
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  RAG Core Pipeline (Python)                            │
│                                                                          │
│  Step 1: Parser (HybridPDFParser)                                       │
│  ├── Fast Track: pymupdf4llm.to_markdown() for simple pages           │
│  └── Heavy Track: Ollama VLM (glm-ocr) for complex pages               │
│      → Output: List[Document] with {source, page} metadata             │
│                                                                          │
│  Step 2: Chunker (Parent-Child Splitting)                               │
│  ├── Parent Chunks: 2000 chars, 200 overlap                            │
│  ├── Child Chunks: 500 chars, 100 overlap                              │
│  └── Each chunk gets UUID doc_id for MultiVectorRetriever             │
│                                                                          │
│  Step 3: Vector DB (Qdrant + InMemoryStore)                            │
│  ├── Child docs → Qdrant (:memory:)                                    │
│  ├── Parent docs → InMemoryStore (doc_id keyed)                       │
│  └── MultiVectorRetriever links child→parent via doc_id               │
│                                                                          │
│  Step 4: Generator (LLM Chain)                                          │
│  ├── LLM: Gemini 3.1 Flash (temperature=0.2)                           │
│  ├── Embedding: microsoft/harrier-oss-v1-270m (CPU)                   │
│  └── System prompt enforces citation from provided context            │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Technologies

| Component | Technology | Version/Notes |
|-----------|------------|---------------|
| PDF Parsing | PyMuPDF (fitz) + pymupdf4llm | Hybrid approach |
| OCR | Ollama + glm-ocr | VLM-based for complex pages |
| Embeddings | HuggingFace Transformers | harrier-oss-v1-270m |
| Vector Store | Qdrant | In-memory mode for dev |
| LLM | Gemini 3.1 Flash | langchain-google-genai |
| Backend | FastAPI + Uvicorn | Python 3.10+ |
| Auth | JWT (PyJWT) + Argon2 | passlib.context |
| Database | SQLite | SQLAlchemy ORM |
| Frontend | Vanilla JS + CSS3 | No framework |

## Configuration

All configuration is centralized in `rag_core/config.py`:

- **Chunking**: PARENT_CHUNK_SIZE=2000, CHILD_CHUNK_SIZE=500
- **Embedding**: DEVICE=cpu (set to 'cuda' for GPU)
- **LLM**: gemini-3.1-flash-lite-preview
- **Vector DB**: Qdrant collection "rag_philosophy"
- **Ollama**: localhost:11434, glm-ocr model, 5 workers

## Data Flow

1. **PDF Upload**: User uploads PDF via `/documents/upload`
2. **Ingestion Pipeline**: PDF → Pages → Chunks → Vectors → Retriever
3. **Query Flow**: User question → Retriever (child→parent) → LLM → SSE Stream
4. **Response**: Token-by-token streaming with source citations

## Security Notes

- JWT tokens expire after 60 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Passwords hashed with Argon2
- API keys stored in `.env` (GEMINI_API_KEY, SECRET_KEY)
- CORS allows all origins in dev (restrict in production)

## File Structure

```
RAG-Philosophy/
├── rag_core/           # RAG pipeline
│   ├── config.py       # Central configuration
│   ├── pipeline.py    # Orchestrator (ingest, build_pipeline, query)
│   ├── step1_parser.py # Hybrid PDF parser
│   ├── step2_chunker.py # Parent-child chunking
│   ├── step3_vector_db.py # Qdrant + MultiVectorRetriever
│   ├── step4_generator.py # LLM chain with Gemini
│   ├── common/        # Shared utilities
│   │   ├── embeddings.py
│   │   ├── logging_utils.py
│   │   └── pdf_utils.py
│   └── tests/          # Unit tests (9 tests, all passing)
├── backend/           # FastAPI backend
│   └── app/
│       ├── main.py
│       ├── routers/    # auth, chat, documents
│       ├── services/   # rag_service
│       ├── core/      # security
│       ├── models.py
│       ├── schemas.py
│       └── database.py
├── frontend/          # Vanilla JS frontend
│   ├── index.html
│   ├── script.js      # Blob animations
│   ├── api.js         # API client
│   └── transitions.js # Scene manager
├── data/              # PDF storage & vector DB
│   ├── raw/           # Original PDFs
│   ├── processed/     # Markdown after parsing
│   └── stores/        # Qdrant + doc_store
└── memory-bank/       # Project context
```