# Lumina RAG Philosophy

Lumina RAG Philosophy là ứng dụng hỏi đáp tài liệu theo hướng Retrieval-Augmented Generation cho tài liệu học tập và tài liệu tham khảo. Hệ thống cho phép người dùng đăng ký, đăng nhập, tải tài liệu lên, chờ pipeline lập chỉ mục, rồi đặt câu hỏi qua giao diện web với câu trả lời có citation.

Runtime chính của ứng dụng nằm ở `backend/app/` và `frontend/`. Thư mục `rag_core/` là lõi RAG dùng chung cho parser, chunker, embedding, retriever, generator, smoke test và các thử nghiệm retrieval.

## Tính năng chính

- Xác thực người dùng bằng JWT và mật khẩu hash Argon2.
- Upload tài liệu qua API, hiện hỗ trợ `.pdf`, `.xlsx`, `.xls`, `.csv`, `.docx`, `.html`, `.htm`, `.md`.
- Ingest tài liệu theo job: lưu object, parse, chunk, embed, upsert vector vào Qdrant, lưu metadata vào SQL.
- Truy xuất dense từ Qdrant, map child chunk về parent chunk trong database.
- Chat thường và chat streaming qua SSE tại `/api/chat` và `/api/chat/stream`.
- Citation inline dạng `[C1]`, `[C2]` kèm `source`, `page`, `document_id`, `chunk_id`, `doc_id`.
- Frontend vanilla JavaScript với upload, job polling, chat streaming, notebook/conversation UI.
- Docker Compose cho Nginx, backend, worker, Redis, Postgres, MinIO, Qdrant và Ollama.

## Cấu trúc thư mục

```text
rag_core/       # Lõi RAG: parser, chunker, vector DB, generator, retriever, tests
backend/app/    # FastAPI backend, auth, ingest, chat runtime, routers, services
backend/tests/  # Unit/regression tests cho backend
frontend/       # Static SPA dùng vanilla JS/CSS
docs/           # Tài liệu kiến trúc, API, RAG, frontend, debugging, evaluation
data/           # Raw files, processed markdown, object store, Qdrant data, evaluation data
docker/         # Dockerfile, Nginx config, Ollama entrypoint
```

## Kiến trúc tổng quan

Luồng ingest:

1. Frontend gọi `POST /api/documents` với file upload.
2. Backend tạo `DocumentRecord` và `IngestJob`, lưu file vào object storage.
3. Worker hoặc đường xử lý sync khi queue idle chạy parser tương ứng theo loại file.
4. Pipeline tạo parent/child chunks và giữ metadata quan trọng: `source`, `page`, `doc_id`.
5. Child chunks được embed và lưu vào Qdrant; parent/child metadata được lưu vào SQL.

Luồng chat:

1. Người dùng gửi câu hỏi qua `/api/chat` hoặc `/api/chat/stream`.
2. Backend rewrite câu hỏi nếu có lịch sử hội thoại.
3. Chat runtime embed câu hỏi, search Qdrant với filter `pipeline_version`, `kind=child`, `owner_id`, `notebook_id`.
4. Kết quả child được map về parent chunk trong SQL.
5. Context và citation marker được đưa vào LLM.
6. API trả answer cùng danh sách citation thực sự được dùng trong câu trả lời.

## Công nghệ

- Python, FastAPI, SQLAlchemy, Celery, Redis.
- Qdrant cho vector database.
- LangChain cho document objects, retriever, prompt và LLM adapters.
- Hugging Face embeddings, mặc định `microsoft/harrier-oss-v1-270m`.
- Gemini, OpenCode/OpenAI-compatible API và local Ollama tùy cấu hình.
- PyMuPDF, pymupdf4llm, BeautifulSoup, readability-lxml, Pandoc/pypandoc cho parsing.
- Vanilla JavaScript ES modules cho frontend.

## Cấu hình

Không commit secret. Sao chép `.env.example` thành `.env` và điền giá trị cần thiết.

Nhóm biến quan trọng:

```text
DATABASE_URL
REDIS_BROKER_URL
REDIS_RESULT_BACKEND
OBJECT_STORAGE_BACKEND
MINIO_ENDPOINT
QDRANT_URL hoặc QDRANT_HOST/QDRANT_PORT
QDRANT_COLLECTION
PIPELINE_VERSION
SYNC_INGEST_WHEN_QUEUE_IDLE
RETRIEVAL_MODE
RETRIEVAL_TOP_K
LLM_MODE
LLM_PROVIDER
LLM_MODEL
GEMINI_API_KEY
OPENCODE_API_KEY
SECRET_KEY
```

Lưu ý: `backend/app/core/settings.py` đang là cấu hình runtime cho service backend/worker. `rag_core/config.py` vẫn là cấu hình lõi RAG. Hai lớp cấu hình này cần được giữ đồng bộ khi đổi model, retrieval mode hoặc Qdrant collection.

## Chạy Trên Windows Bằng start.bat

Launcher Windows chạy backend/worker/frontend bằng `.venv` local và chỉ dùng Docker cho hạ tầng Redis, Postgres, Qdrant, MinIO:

```bat
start.bat
```

Script sẽ tạo `.venv` nếu thiếu, chạy `pip install -r requirements.txt`, bật các container hạ tầng, rồi mở frontend tại `http://127.0.0.1:5500`.

## Chạy bằng Docker Compose

Nếu muốn chạy toàn bộ stack trong Docker:

```bash
docker compose up --build
```

Sau khi các service healthy:

- Frontend qua Nginx: `http://localhost`
- Backend docs: `http://localhost/api` được proxy qua Nginx; OpenAPI trực tiếp trong container backend là `/docs`
- Qdrant: `127.0.0.1:6333`
- MinIO console: `127.0.0.1:9001`

## Chạy thủ công khi phát triển

Cài dependency:

```bash
python -m pip install -r requirements.txt
```

Chạy backend:

```bash
uvicorn backend.app.main:app --reload
```

Chạy worker:

```bash
celery -A backend.app.worker.celery_app.celery_app worker -Q ingest -l info --concurrency 1
```

Chạy frontend tĩnh:

```bash
cd frontend
npm install
npm run serve
```

## API chính

Các endpoint chính nằm dưới `/api`:

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
- `GET /api/notebooks/{notebook_id}/conversations/latest`
- `POST /api/notebooks/{notebook_id}/notes`

SSE token event:

```text
data: {"type":"token","token":"...","done":false}
```

SSE final event:

```text
data: {"type":"final","token":"","done":true,"answer":"...","citations":[],"conversation_id":"...","message_id":"...","rewritten_query":"..."}
```

SSE error event:

```text
data: {"type":"error","token":"","done":true,"error":"...","citations":[]}
```

## Kiểm thử

Kiểm tra cú pháp Python:

```bash
python -m compileall backend rag_core -q
```

Chạy RAG core tests:

```bash
python -m unittest discover rag_core/tests -v
```

Chạy backend tests:

```bash
python -m unittest discover backend/tests -v
```

Chạy frontend unit tests:

```bash
cd frontend
npm test
```

Chạy RAG smoke test:

```bash
python rag_core/main_test.py
```

Chạy evaluation:

```bash
python rag_core/ragas_eval.py --dataset data/dataset.json --out data/result.csv --records-in data/ragas_records.json
```

## Trạng thái hiện tại

Đã hoạt động:

- RAG core parser/chunker/retriever/generator và test coverage cho nhiều parser.
- Backend auth, upload, ingest job, Qdrant payload, document cleanup, chat runtime và SSE.
- Frontend upload, job polling, stream parser, source viewer và notebook/conversation state cơ bản.

Đang một phần:

- `RETRIEVAL_MODE=hybrid` trong backend hiện vẫn là dense passthrough; hybrid BM25/RRF thật nằm ở `rag_core`.
- Reranking đã có trong `rag_core`, chưa tích hợp vào backend persistent retrieval path.
- Admin APIs/UI có skeleton và route đăng ký, nhưng cần kiểm tra hoàn thiện theo yêu cầu sản phẩm.
- Evaluation có script và data, chưa là quality gate tự động.

Rủi ro cần chú ý:

- Cấu hình bị chia giữa `backend/app/core/settings.py`, `rag_core/config.py`, `.env.example`.
- Chưa thấy migration framework; backend hiện dùng `Base.metadata.create_all` và schema helper runtime.
- CORS đang mở cho development.
- Backend tests phụ thuộc đúng environment packages và `.env`; nếu `.env` trỏ Postgres/MinIO thì cần cài `psycopg2-binary`, `minio` hoặc override sang SQLite/local storage khi test.

## Tài liệu liên quan

- `docs/PROJECT_OVERVIEW.md`: phân tích chi tiết trạng thái dự án.
- `docs/api/non-admin-contract-v1.md`: contract API non-admin hiện tại.
- `docs/rag/retrieval-pipeline.md`: pipeline retrieval trong `rag_core`.
- `docs/frontend/ui-architecture.md`: kiến trúc frontend.
- `docs/debugging/`: hướng dẫn debug retrieval, performance và lỗi phổ biến.
