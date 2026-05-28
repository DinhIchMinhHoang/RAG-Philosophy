# RAG-Philosophy — Giải Thích Dự Án

## 1. Tổng Quan

**RAG-Philosophy (Lumina Notebook)** là hệ thống **Retrieval-Augmented Generation (RAG)** cho phép upload tài liệu học tập và đặt câu hỏi, nhận câu trả lời có **trích dẫn nguồn** (citation) kèm số trang.

Mục tiêu: Xây dựng nền tảng hỏi đáp thông minh dựa trên tài liệu gốc, đảm bảo mọi câu trả lời đều có căn cứ, phục vụ sinh viên tra cứu giáo trình triết học.

---

## 2. Kiến Trúc Tổng Thể (4 tầng)

```
[Frontend] ──HTTP/SSE──▶ [Nginx] ──proxy──▶ [FastAPI Backend] ──▶ [RAG Core]
                                                    │
                                          ┌─────────┼──────────┐
                                          ▼         ▼          ▼
                                      [PostgreSQL] [Qdrant]  [MinIO]
                                                          (vector DB) (object storage)
                                          │
                                      [Redis] ◀── [Celery Worker]
```

- **Frontend** (Vanilla JS ES Modules) — Giao diện người dùng
- **Nginx** — Reverse proxy, serve frontend tĩnh, route API
- **Backend** (FastAPI) — 7 router modules xử lý logic nghiệp vụ
- **RAG Core** (Python) — Pipeline xử lý tài liệu: Parse → Chunk → Embed → Retrieve → Generate

---

## 3. Backend (FastAPI) — `backend/app/`

### 3.1 Entry Point (`main.py`)

Khởi tạo FastAPI app, CORS middleware, request logging, error envelope cho mọi response, và đăng ký **7 routers**:

| Router | Endpoints chính |
|--------|----------------|
| **auth** | `POST /api/signup`, `/api/login`, `/api/change-password`, `GET /api/auth/me` |
| **chat** | `POST /api/chat`, `POST /api/chat/stream` (SSE streaming) |
| **ingest** | `POST /api/documents` (upload), `GET`, `DELETE`, reindex, URL ingest, job status |
| **documents** | Page image rendering, file download với HTTP Range support |
| **notebooks** | CRUD notebooks, conversations, notes/pins, file management, copy notebook |
| **admin** | Quản lý users/documents/notebooks, xem cấu hình .env (ẩn secret) |
| **password_reset** | 3-step: forgot → verify code → reset |

### 3.2 Services Layer

- **`chat_runtime.py`** — Runtime quan trọng nhất: embed câu hỏi → search Qdrant → map child→parent trong SQL → xây context với citation markers [C1] → gửi LLM → stream token. Hỗ trợ auto-fallback: Gemini → OpenCode → local Ollama
- **`chat_history.py`** — Lưu lịch sử chat vào PostgreSQL
- **`embedding_client.py`** — HTTP client gọi embedding service riêng

### 3.3 Ingestion Pipeline (`backend/app/ingest/`)

14 modules xử lý background ingest:
- `processor.py`: Pipeline chính — fetch object → parse → chunk → embed → index vector → persist metadata
- `qdrant_store.py`: Kết nối Qdrant, upsert vectors bằng deterministic UUID5 point ID
- `storage.py`: Object storage (local filesystem hoặc MinIO S3)
- `deletion.py`: Soft-delete + cleanup Qdrant/object storage
- `idempotency.py`: Content hash SHA-256 để tránh upload trùng
- `runtime.py`: Job runner — sync (threadpool) hoặc async (Celery)
- `excel_ingestor.py`: Xử lý file Excel/CSV

### 3.4 Models (SQLAlchemy ORM)

10 tables:

| Table | Mục đích |
|-------|----------|
| `users` | Tài khoản: username, email, hashed_password (Argon2) |
| `notebooks` | Notebook: title, owner, cover, is_community |
| `documents` | Document metadata: filename, object_key, content_hash, soft-delete |
| `ingest_jobs` | Job tracking: status, stage, progress_pct, error_message |
| `document_chunks` | Parent & child chunks: kind, text, source, page, doc_id, pipeline_version |
| `conversations` | Hội thoại: owner, notebook, archived_at |
| `chat_messages` | Tin nhắn: role, content, sources_used (JSON), rewritten_query |
| `saved_notebook_items` | Ghi chú/pin/summary: kind, title, content |
| `excel_table_records` | Metadata bảng Excel: sheet_name, column_schema |
| `password_reset_codes` | Mã xác thực: email, code, expires_at |

### 3.5 Core Modules

- **`security.py`** — JWT (HS256, PyJWT) + Argon2 via passlib
- **`settings.py`** — 50+ biến cấu hình runtime từ .env
- **`dependencies.py`** — FastAPI DI: get current user, get DB session

---

## 4. RAG Core Pipeline — `rag_core/`

### Step 1: Parser (`step1_parser.py`)

**HybridPDFParser** — Parser PDF 2-pass:

- **Pass 1**: Phân loại trang — simple (text thuần) hay complex (có ảnh, bảng, ký hiệu toán học)
- **Pass 2**:
  - *Fast Track*: `pymupdf4llm.to_markdown()` cho simple pages
  - *Heavy Track*: Render page → base64 → gửi Z.AI GLM-OCR API → nhận Markdown
  - Fallback: pymupdf4llm hoặc raw text nếu OCR fail
- Output: `List[Document]` với metadata `{source, page}`

Ngoài ra còn parser cho DOCX (pypandoc/LibreOffice), HTML (BeautifulSoup + readability), MD.

### Step 2: Chunker (`step2_chunker.py`)

**Parent-Child Chunking** — Chia nhỏ văn bản 2 tầng:

```
Page Document
  ├── Parent Chunk #1 (2000 ký tự, 200 overlap) — doc_id = UUIDv5(source, page, 0)
  │   ├── Child #1 (500 ký tự, 100 overlap) — kế thừa doc_id
  │   ├── Child #2
  │   └── Child #3
  ├── Parent Chunk #2
  │   ├── Child #1
  │   └── Child #2
```

**Logic**: Child chunks (ngắn) → embed vào Qdrant để search chính xác. Parent chunks (dài) → context đầy đủ cho LLM. `doc_id` là khóa liên kết child→parent.

**Điểm mạnh**: `doc_id` là **UUID5 deterministic** — cùng source + page + chunk index → luôn ra cùng doc_id. Đảm bảo idempotent khi reindex.

### Step 3: Vector DB (`step3_vector_db.py`)

Child chunks → **Qdrant** (vector search, Cosine distance, 640-dim). Parent chunks → **InMemoryStore** (tra cứu bằng doc_id). `MultiVectorRetriever` liên kết child→parent.

### Step 4: Generator (`step4_generator.py`)

Build LLM chain với LangChain. Hỗ trợ 3 provider:
- **Gemini** (`langchain-google-genai`)
- **OpenCode/OpenAI-compatible** (`langchain-openai`)
- **Local Ollama** (`ChatOllama`)

Prompt hệ thống yêu cầu trích dẫn nguồn kiểu `[C1]`, `[C2]`.

### Modules bổ sung

| Module | Chức năng |
|--------|-----------|
| `common/embeddings.py` | HuggingFace embeddings (`microsoft/harrier-oss-v1-270m`) |
| `common/llm.py` | LLM provider factory: auto-detect Gemini vs OpenCode |
| `common/prompts.py` | Prompt templates (system prompt, citation instructions) |
| `pipeline.py` | Orchestrator: `ingest()` → `build_pipeline()` → `query()` |
| `hybrid_retriever.py` | Thí nghiệm hybrid: BM25 + dense search với RRF |
| `rerank_retriever.py` | Thí nghiệm rerank với Cohere API |
| `cohere_reranker.py` | Cohere reranker (fail-open) |
| `ragas_eval.py` | Evaluation với RAGAS framework |

---

## 5. Frontend — `frontend/`

**Vanilla JavaScript ES Modules** — không React, không build tool.

```
frontend/
├── index.html            # Single page với scene management
├── src/
│   ├── App.js            # Scene manager: landing → auth → dashboard → chat
│   ├── api/client.js     # API client, BASE_URL='/api', token management
│   ├── api/auth.js       # signup, login, changePassword
│   ├── api/rag.js        # upload, listSources, getJob, chatStream
│   ├── api/notebooks.js  # notebook/conversation API
│   ├── api/admin.js      # Admin API
│   ├── state/store.js    # localStorage state
│   ├── ui/               # UI components
│   └── animations/       # Gradient canvas effects
├── styles/               # CSS
└── assets/               # Logo, icons
```

Chat streaming dùng **ReadableStream** + SSE. Render Markdown (marked.js) + KaTeX (toán học).

---

## 6. Data Flow Chi Tiết

### Luồng Upload & Ingest

```
User upload file (.pdf/.docx/.html/.md)
  → POST /api/documents (multipart/form-data)
  → Backend:
      1. Validate file type & size (max 20MB)
      2. Tính content_hash SHA-256 → check duplicate
      3. Lưu file vào object storage (MinIO hoặc local)
      4. Tạo DocumentRecord + IngestJob
      5. Enqueue Celery task (hoặc chạy sync nếu queue idle)
  → Worker:
      1. Fetch file từ storage
      2. Parse → Chunk → Embed
      3. Upsert vectors vào Qdrant (UUID5 deterministic)
      4. Persist chunk metadata vào PostgreSQL
  → Frontend poll GET /api/jobs/{job_id} để xem progress
```

### Luồng Chat

```
User gửi câu hỏi
  → POST /api/chat/stream { message, conversation_id?, notebook_id? }
  → Backend:
      1. Validate JWT → xác định user_id
      2. Load lịch sử chat
      3. Rewrite câu hỏi bằng LLM
      4. Embed câu hỏi → 640-dim vector
      5. Search Qdrant với filter (pipeline_version, kind=child, owner_id, notebook_id)
      6. Map child hits → parent chunks trong SQL
      7. Xây context block với [C1], [C2], ...
      8. Gửi context + history → LLM
      9. Stream tokens về client qua SSE
  → Frontend:
      - Render từng token (Markdown + KaTeX)
      - Final event → hiển thị citations + nguồn
```

---

## 7. Infrastructure & Docker Compose

| Container | Image | Vai trò | RAM | CPU |
|-----------|-------|---------|-----|-----|
| nginx | nginx:1.27-alpine | Reverse proxy, serve frontend | 128 MB | 0.1 |
| backend | custom (GHCR) | FastAPI app | 768 MB | 0.6 |
| worker | custom (GHCR) | Celery worker ingest | 1.28 GB | 0.7 |
| embedding | custom (GHCR) | HuggingFace embedding service | 2 GB | 0.7 |
| postgres | postgres:16-alpine | Relational DB | 768 MB | 0.3 |
| redis | redis:7-alpine | Celery broker | 256 MB | 0.15 |
| minio | minio:RELEASE.2023-10 | S3 object storage | 256 MB | 0.15 |
| qdrant | qdrant/qdrant:v1.13.4 | Vector DB | 1.5 GB | 0.4 |

**CI/CD**: GitHub Actions — Python tests + Frontend tests + Integration tests → Build Docker → Push GHCR → SSH deploy VM → 3 health checks → rollback nếu fail.

---

## 8. Security

- JWT token HS256, 60 phút hết hạn
- Password hash Argon2
- API keys trong .env (`GEMINI_API_KEY`, `OPENCODE_API_KEY`, `SECRET_KEY`)
- Weak SECRET_KEY tự động detect khi production
- Admin role: email phải kết thúc bằng `@lumina.com.vn`

---

## 9. Công Nghệ Sử Dụng

| Thành phần | Công nghệ |
|-----------|-----------|
| Backend | FastAPI + Uvicorn (Python 3.11) |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (HS256) + Argon2 |
| Vector DB | Qdrant 1.13.4 (Cosine, 640-dim) |
| Relational DB | PostgreSQL 16 (prod) / SQLite (dev) |
| Object storage | MinIO (prod) / local filesystem (dev) |
| Queue | Celery + Redis 7 |
| PDF parsing | PyMuPDF + pymupdf4llm |
| OCR | Z.AI GLM-OCR (VLM-based) |
| Embeddings | HuggingFace Transformers (harrier-oss-v1-270m) |
| LLM | Gemini, OpenCode/OpenAI, Ollama |
| RAG framework | LangChain |
| Frontend | Vanilla JS ES Modules |
| Container | Docker Compose (8 services) |
| CI/CD | GitHub Actions |

---

## 10. Các Docs Quan Trọng

| File | Mô tả |
|------|-------|
| `API_SPECIFICATION.md` | Full REST API spec |
| `CI_CD_PIPELINE.md` | CI/CD pipeline, Docker architecture |
| `DATABASE_ARCHITECTURE.md` | PostgreSQL schema, Qdrant payload |
| `docs/PROJECT_OVERVIEW.md` | Comprehensive project analysis |
| `docs/rag/retrieval-pipeline.md` | Chi tiết retrieval pipeline |
| `docs/rag/llm-provider-switch.md` | Cách switching LLM providers |
| `docs/api/non-admin-contract-v1.md` | API contract chuẩn |
| `README.md` | Tổng quan dự án (tiếng Việt) |
