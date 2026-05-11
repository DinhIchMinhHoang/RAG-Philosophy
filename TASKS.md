# Phân Công Nhiệm Vụ Nhóm (Hard Deadline 27/05/2026)
## Mục tiêu
- Chạy được toàn bộ hệ thống bằng đúng 1 lệnh `docker-compose up -d`
- Đủ kiến trúc bắt buộc: Frontend, Backend, Nginx, Queue+Worker, Postgres, MinIO, Qdrant
- Chat trả lời có trích dẫn rõ ràng (source + page + snippet)
- Không hardcode Gemini, có local fallback (Ollama)
- Có pipeline versioning, progress/stage model, logging chuẩn hóa
- Có Admin UI quản trị user + tài liệu + ingest status
## Mốc thời gian nội bộ
- 12/05/2026: Contract freeze (chốt path API, schema, enums; không đổi breaking)
- 18/05/2026: Compose skeleton (khung compose + UI mở được + API gọi được + worker chạy được)
- 23/05/2026: E2E pass (upload -> ingest nền -> chat có citations chạy thật)
- 26/05/2026: Freeze + README (đóng băng tính năng, chỉ hotfix; hoàn thiện README)
- 27/05/2026: Submit
## Điểm chung cần thống nhất (Freeze sau 12/05/2026)
### 1) Base routing
- Nginx serve UI tại `http://localhost`
- Backend đi qua prefix `/api/*` (same-origin), không gọi trực tiếp port backend từ browser
### 2) Endpoint paths tối thiểu (không đổi sau 12/05)
- `POST /api/signup`
- `POST /api/login`
- `POST /api/change-password`
- `POST /api/documents` (upload, tạo job ingest nền, trả `document_id` + `job_id`)
- `GET /api/documents` (list + status)
- `DELETE /api/documents/{document_id}`
- `POST /api/documents/{document_id}/reindex`
- `GET /api/jobs/{job_id}` (status/stage/progress/error)
- `POST /api/chat/stream` (SSE streaming)
- `POST /api/chat` (optional, non-stream cho test)
- `GET /api/admin/users`
- `POST /api/admin/users`
- `DELETE /api/admin/users/{user_id}`
- `GET /api/admin/documents`
- `GET /api/admin/jobs`
### 3) Job status/stage (chuẩn hóa)
- `job.status`: `queued`, `running`, `succeeded`, `failed`
- `job.stage`: `fetching_object`, `parsing`, `chunking`, `embedding`, `indexing_vector`, `persisting_metadata`
### 4) Field names chuẩn (snake_case)
- Bắt buộc giữ metadata keys cho citations: `source`, `page`, `doc_id`
- Job fields tối thiểu: `job_id`, `document_id`, `status`, `stage`, `progress_pct`, `stage_detail`, `error_message`, `pipeline_version`
### 5) Citation contract (frontend phải render được)
- Response chat phải có `citations` dạng array, mỗi citation tối thiểu:
- `source` (filename)
- `page` (int)
- `snippet` (text ngắn)
- Optional: `document_id`, `chunk_id`, `score`
### 6) Pipeline versioning
- Có biến `PIPELINE_VERSION` (vd `1.0.0`)
- Job, chunk, payload Qdrant đều gắn `pipeline_version`
- Query phải filter theo `pipeline_version` hoặc dùng Qdrant alias theo version
### 7) Retrieval abstraction
- Có config `RETRIEVAL_MODE=dense|hybrid`
- `dense`: Qdrant only
- `hybrid`: Dense (Qdrant) + Sparse (Postgres FTS) + merge (RRF), có thể stub ban đầu nhưng interface cố định
### 8) LLM abstraction (không hardcode Gemini)
- Có config `LLM_MODE=auto|gemini|local`
- `auto`: ưu tiên Gemini nếu cấu hình ok, fallback Ollama khi lỗi
- `gemini`: chỉ Gemini
- `local`: chỉ Ollama
### 9) Logging chuẩn hóa (backend + worker)
- Log JSON ra stdout
- Fields tối thiểu: `service`, `level`, `ts`, `request_id` (backend), `job_id` (worker), `document_id`, `pipeline_version`, `stage`, `duration_ms`, `error_message`
- Không log secrets (API key, token, password, nội dung `.env`)
### 10) Parent-child retrieval (giữ nhưng đơn giản hóa schema)
- Embed child chunks
- Payload Qdrant phải có `parent_chunk_id` để fetch parent text từ Postgres
- Schema DB ưu tiên 1 bảng `chunks` với `kind=parent|child` và `parent_chunk_id`



## Phân công theo 4 thành viên

## Thành viên A: Infra/DevOps (Compose + Nginx + Volumes + Env)
### Scope
- Docker Compose hoàn chỉnh, Nginx reverse proxy, volumes persistent, healthchecks
### Checklist
- [ ] 12/05: Tạo `docker-compose.yml` khung đủ service: nginx, backend, worker, redis, postgres, minio, qdrant, ollama
- [ ] 13/05: Volumes persistent cho postgres/minio/qdrant; networks; ports; secrets qua `.env`
- [ ] 14/05: Nginx serve frontend + proxy `/api/*` sang backend (hỗ trợ SSE)
- [ ] 15/05: Healthcheck + startup dependencies cho backend/worker
- [ ] 16/05: Chuẩn hóa `.env.example` đầy đủ biến cho toàn stack
- [ ] 18/05: Cold start test và restart test (dữ liệu không mất)
- [ ] 26/05: Tune timeout Nginx cho streaming, checklist reproducibility
### Deliverables
- Compose chạy được bằng 1 lệnh
- Nginx route đúng (UI + API)
- `.env.example` đầy đủ
### Acceptance
- `docker-compose up -d` xong mở được UI ở `http://localhost`
- API qua `http://localhost/api/...` hoạt động
- Restart compose không mất dữ liệu (volumes ok)

## Thành viên B: Backend (FastAPI API + Auth/Admin + Retrieval/LLM Abstraction)
### Scope
- API contract, auth/role admin, document lifecycle, chat endpoint, retrieval layer abstraction, LLM abstraction, logging backend
### Checklist
- [ ] 12/05: Xuất bản “Contract 1 trang” (paths + JSON mẫu + enums + env keys) và chốt freeze
- [ ] 14/05: Auth hoàn chỉnh + `is_admin` + bảo vệ `/api/admin/*`
- [ ] 16/05: `POST /api/documents` chỉ tạo job queued (không ingest đồng bộ) + `GET /api/jobs/{id}`
- [ ] 19/05: Admin APIs user/documents/jobs đáp ứng UI quản trị
- [ ] 21/05: Retrieval abstraction `dense|hybrid` (hybrid có thể stub nhưng interface cố định)
- [ ] 22/05: `POST /api/chat/stream` SSE format ổn định + citations structured
- [ ] 23/05: LLM abstraction `auto|gemini|local` + fallback Ollama; error handling sạch
- [ ] 26/05: Logging JSON chuẩn; security check (không default SECRET_KEY yếu)
### Deliverables
- Backend chạy sau Nginx với `/api/*`
- OpenAPI/Swagger đúng contract
- Chat trả citations structured (không chỉ text footer)
### Acceptance
- Upload trả job ngay, không block
- Admin endpoints hoạt động đúng role
- Chat trả lời có citations rõ, lỗi trả về nhất quán

## Thành viên C: Worker (Celery ingest + Progress/Stage + Qdrant + Postgres + Versioning)
### Scope
- Celery worker ingest nền, cập nhật progress/stage vào Postgres, upsert Qdrant, lưu chunks, pipeline_version xuyên suốt
### Checklist
- [ ] 12/05: Celery skeleton + cấu hình queue/retry/backoff + wiring Redis
- [ ] 14/05: Update `ingest_jobs` theo status/stage/progress/stage_detail
- [ ] 16/05: Fetch PDF từ MinIO, validate, stage `fetching_object`
- [ ] 18/05: Parse + chunk parent/child + lưu `chunks` vào Postgres (stage parsing/chunking)
- [ ] 20/05: Embed child + upsert Qdrant payload chuẩn (stage embedding/indexing_vector)
- [ ] 21/05: Persist metadata đầy đủ + mark succeeded; failure path mark failed có error_message rõ
- [ ] 22/05: Pipeline versioning đầy đủ (DB + Qdrant payload + job)
- [ ] 23/05: Idempotency tối thiểu cho reindex (cleanup/upsert ổn định theo document_id+version)
- [ ] 26/05: Logging JSON chuẩn + duration_ms theo stage
### Deliverables
- Worker ingest thật chạy end-to-end
- Job progress/stage hiển thị đúng cho UI/admin
- Qdrant vectors persistent, truy vấn được
### Acceptance
- Job fail có lỗi rõ, không treo trạng thái running
- Reindex không nhân đôi dữ liệu vô kiểm soát
- Backend retrieve được parent chunks + citations đúng page/source

## Thành viên D: Frontend (User Chat UI + Admin UI + Ingest Status UX)
### Scope
- UI chat cho user, UI admin quản trị user/tài liệu/job, hiển thị progress ingest, hiển thị citations rõ ràng, error handling
### Checklist
- [ ] 12/05: Tạo mock fixtures theo contract (jobs/documents/chat) để phát triển độc lập
- [ ] 14/05: Wiring auth UI (login/signup), lưu token, guard admin routes
- [ ] 16/05: Upload UI gọi `POST /api/documents` và poll `GET /api/jobs/{id}` hiển thị progress/stage
- [ ] 18/05: Admin UI: users + documents + jobs (list/detail) theo contract
- [ ] 21/05: Chat UI: gọi SSE `POST /api/chat/stream`, render stream ổn định
- [ ] 22/05: Render citations structured (source/page/snippet) rõ ràng, UX “không đủ bằng chứng”
- [ ] 23/05: Error UX: token hết hạn, job failed, backend down, đang ingest
- [ ] 26/05: Polish UI/UX + rehearsal demo flow
### Deliverables
- User flow và Admin flow demo được
- Citations hiển thị rõ theo contract
- UX trạng thái đầy đủ (loading/empty/error)
### Acceptance
- Không crash khi stream dài hoặc mạng chập chờn
- Citations hiển thị đúng và dễ đối chiếu
- Admin thao tác lifecycle tài liệu + xem ingest status dễ dàng
## Quy tắc Freeze
- Sau 12/05: Không đổi breaking API/schema/enums/field names/citation contract nếu không có đồng thuận nhóm
- Sau 26/05: Chỉ hotfix lỗi crash, lỗi citations nghiêm trọng, lỗi “không chạy được compose”
Bạn xác nhận giúp mình 1 dòng: đặt file ở docs/plans/team-assignment.md đúng không? Khi Plan Mode được tắt, mình sẽ tạo file đúng path đó.