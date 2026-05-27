# REST API Specification — RAG-Philosophy

**Document Version:** 1.0  
**Last Updated:** 2026-05-27  
**Status:** Active

---

## Table of Contents

1. [Overview](#1-overview)
   - 1.1 Base URL
   - 1.2 Error Envelope
   - 1.3 Authentication
   - 1.4 Common Headers
2. [Authentication Endpoints](#2-authentication-endpoints)
   - 2.1 Signup
   - 2.2 Login
   - 2.3 Change Password
   - 2.4 Current User Info
   - 2.5 Password Reset Flow
3. [Chat Endpoints](#3-chat-endpoints)
   - 3.1 Non-Streaming Chat
   - 3.2 SSE Streaming Chat
4. [Document Management](#4-document-management)
   - 4.1 Upload Document
   - 4.2 List Documents
   - 4.3 Delete Document
   - 4.4 Replace Document
   - 4.5 Reindex Document
   - 4.6 URL Ingest
   - 4.7 Job Status
   - 4.8 Document Assets
5. [Notebook Endpoints](#5-notebook-endpoints)
   - 5.1 Notebook CRUD
   - 5.2 Conversations
   - 5.3 Notes and Pins
   - 5.4 File Management
   - 5.5 Copy Notebook
6. [Admin Endpoints](#6-admin-endpoints)
7. [Common Error Responses](#7-common-error-responses)

---

## 1. Overview

### 1.1 Base URL

Production: `http://{host}/api/` (routed through nginx)  
Development: `http://localhost:8000/api/`

All paths in this document are relative to the base URL unless otherwise noted. The underlying FastAPI application is mounted at the root (`/`) and routed under `/api/` via nginx.

### 1.2 Error Envelope

All error responses follow a consistent envelope:

```json
{
  "error": {
    "code": "http_{status_code}",
    "message": "Human-readable description",
    "request_id": "uuid-string",
    "details": null
  },
  "detail": "Human-readable description"
}
```

Validation errors additionally populate `details`:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "request_id": "uuid-string",
    "details": [
      {
        "type": "missing",
        "loc": ["body", "email"],
        "msg": "Field required",
        "input": {}
      }
    ]
  },
  "detail": "Request validation failed"
}
```

Every response includes an `X-Request-Id` header for traceability.

### 1.3 Authentication

Most endpoints require JWT bearer authentication.

**Token acquisition:** `POST /api/signup` or `POST /api/login` returns:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Token usage:** Two methods are supported:

1. **Authorization header** (preferred):
   ```
   Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
   ```

2. **Query parameter** (fallback for SSE/streaming):
   ```
   GET /api/chat/stream?token=eyJhbGciOiJIUzI1NiIs...
   ```

**Token claims:** `{ "sub": "username", "exp": <unix_timestamp> }`  
**Algorithm:** HS256  
**Default expiry:** 60 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)

### 1.4 Common Headers

| Header | Required For | Example |
|--------|-------------|---------|
| `Content-Type: application/json` | POST/PATCH with JSON body | |
| `Authorization: Bearer <token>` | Authenticated endpoints | |
| `X-Request-Id` | Optional trace ID | `uuid-string` |
| `Range: bytes=0-1023` | File streaming | `bytes=0-1023` |

Error responses if auth header is missing:
```json
{
  "error": {
    "code": "http_401",
    "message": "Missing or invalid authorization header",
    "request_id": "uuid"
  },
  "detail": "Missing or invalid authorization header"
}
```

---

## 2. Authentication Endpoints

**Router:** `backend/app/routers/auth.py`

### 2.1 Signup

**`POST /api/signup`** — Register a new user. Returns JWT token on success.

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@gmail.com",
  "password": "securePass123"
}
```

**Validation rules:**
- `email`: must end with `@gmail.com` or `@lumina.com.vn`
- `password`: 6–128 characters

**Success (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errors:** 400 (validation), 409 (duplicate email/username)

### 2.2 Login

**`POST /api/login`** — Authenticate and get JWT token.

**Request:**
```json
{
  "email": "john@gmail.com",
  "password": "securePass123"
}
```

**Success (200):** Same token format as signup.

**Errors:** 401 (invalid credentials)

### 2.3 Change Password

**`POST /api/change-password`** — Update password for authenticated user.

**Auth:** JWT required  
**Request:**
```json
{
  "current_password": "oldPass123",
  "new_password": "newSecurePass456"
}
```

**Success (200):** `{}` (empty response)

**Errors:** 400 (validation: new password 6–128 chars), 401 (wrong current password)

### 2.4 Current User Info

**`GET /api/auth/me`** — Get current user profile.

**Auth:** JWT required  
**Success (200):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@gmail.com",
  "is_admin": false
}
```

`is_admin` is `true` when `email` ends with `@lumina.com.vn`.

### 2.5 Password Reset Flow

**Router:** `backend/app/routers/password_reset.py`

Three-step flow:

#### Step 1: Request Code
**`POST /api/password/forgot`**

```json
{ "email": "john@gmail.com" }
```

Success (200): Always returns generic message (prevents user enumeration):
```json
{
  "message": "If the email exists, a verification code will be sent."
}
```

The code is 4 numeric digits, valid for 15 minutes. If SMTP is configured, the code is emailed; otherwise it is logged to console.

#### Step 2: Verify Code
**`POST /api/password/verify`**

```json
{ "email": "john@gmail.com", "code": "1234" }
```

Success (200):
```json
{ "message": "Code verified successfully" }
```

Errors: 400 (invalid/expired code)

#### Step 3: Reset Password
**`POST /api/password/reset`**

```json
{
  "email": "john@gmail.com",
  "code": "1234",
  "new_password": "newSecurePass789"
}
```

Success (200):
```json
{ "message": "Password reset successfully" }
```

Errors: 400 (invalid code, expired code, password validation)

---

## 3. Chat Endpoints

**Router:** `backend/app/routers/chat.py`  
**Service:** `backend/app/services/chat_runtime.py`

### 3.1 Non-Streaming Chat

**`POST /api/chat`** — Send a message and receive a complete answer.

**Auth:** JWT required  
**Request:**
```json
{
  "message": "What is the nature of knowledge?",
  "conversation_id": null,
  "notebook_id": 1,
  "selected_source_ids": null
}
```

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | `string` | Yes | User message (non-empty) |
| `conversation_id` | `string or null` | No | Resume existing conversation |
| `notebook_id` | `int or null` | No | Scope retrieval to notebook |
| `selected_source_ids` | `[string] or null` | No | Limit retrieval to specific documents |

**Success (200):**
```json
{
  "answer": "Knowledge is a justified true belief, as defined in [C1].",
  "citations": [
    {
      "citation_id": "C1",
      "rank": 1,
      "source": "philosophy_chapter_3.pdf",
      "page": 42,
      "snippet": "The standard analysis of knowledge as justified true belief...",
      "document_id": "abc-123",
      "chunk_id": "def-456",
      "doc_id": "ghi-789",
      "score": 0.87
    }
  ],
  "conversation_id": "conv-uuid",
  "message_id": "msg-uuid",
  "rewritten_query": "What is the nature of knowledge according to philosophy?"
}
```

**Errors:** 400 (empty message), 404 (invalid selected_source_ids), 503 (embedding service unavailable)

### 3.2 SSE Streaming Chat

**`POST /api/chat/stream`** — Server-Sent Events streaming chat.

**Auth:** JWT required (via header or `?token=` query param)  
**Response media type:** `text/event-stream`  
**Response headers:**
```
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

**Request body:** Same as non-streaming `ChatRequest`.

**SSE Events:**

```mermaid
sequenceDiagram
    participant Client as Frontend
    participant Nginx as NGINX
    participant API as Backend API
    participant ES as Embedding Service
    participant QD as Qdrant
    participant LLM as LLM Provider

    Client->>Nginx: POST /api/chat/stream
    Nginx->>API: Proxy (no buffer)
    API->>API: Validate JWT, load history
    API->>ES: POST /embed (query)
    ES-->>API: 640-dim vector
    API->>QD: Search (filter by owner/notebook)
    QD-->>API: Top-K contexts
    API->>API: Rewrite question
    API-->>Client: data: {"type":"status","stage":"accepted"}
    API->>LLM: Stream generate
    LLM-->>API: Token chunk
    API-->>Client: data: {"type":"token","token":"The"}
    LLM-->>API: Token chunk
    API-->>Client: data: {"type":"token","token":" nature"}
    LLM-->>API: Token chunk
    API-->>Client: data: {"type":"token","token":" of"}
    LLM-->>API: [DONE]
    API->>API: Normalize citations, filter used citations
    API-->>Client: data: {"type":"final","answer":"The nature of...","citations":[...]}
```

**Figure 1: SSE streaming sequence.**

#### Event: Status accepted

Sent immediately after retrieval is complete, before LLM streaming begins.

```json
{
  "type": "status",
  "token": "",
  "done": false,
  "stage": "accepted"
}
```

#### Event: Token

Sent for each token generated by the LLM.

```json
{
  "type": "token",
  "token": "The",
  "done": false
}
```

#### Event: Final

Sent once after all tokens have been streamed.

```json
{
  "type": "final",
  "token": "",
  "done": true,
  "answer": "The nature of knowledge according to Plato is justified true belief [C1].",
  "citations": [
    {
      "citation_id": "C1",
      "rank": 1,
      "source": "philosophy_chapter_3.pdf",
      "page": 42,
      "snippet": "The standard analysis of knowledge as justified true belief...",
      "document_id": "abc-123",
      "chunk_id": "def-456",
      "doc_id": "ghi-789",
      "score": 0.87
    }
  ],
  "conversation_id": "conv-uuid",
  "message_id": "msg-uuid",
  "rewritten_query": "What is the nature of knowledge according to philosophy?",
  "error": null
}
```

#### Error Event

If the embedding service is unavailable or the LLM stream fails:

```json
{
  "type": "final",
  "token": "",
  "done": true,
  "answer": "I'm sorry, but I'm unable to process your request right now.",
  "citations": [],
  "conversation_id": "conv-uuid",
  "message_id": "msg-uuid",
  "rewritten_query": "",
  "error": "embedding_service_unavailable"
}
```

Possible error values: `embedding_service_unavailable`, `chat_stream_failed`.

#### Disconnect Handling

If the client disconnects mid-stream, the server detects the closed connection and gracefully stops generation (no error event is sent).

#### Edge Cases

| Condition | Behavior |
|-----------|----------|
| Empty notebook (no processed documents) | Returns a canned answer `EMPTY_NOTEBOOK_ANSWER` with no citations |
| Embedding service timeout | Returns `EMBEDDING_ERROR_ANSWER` with status 503 |
| Invalid `selected_source_ids` | Returns HTTP 404 with specific missing document IDs |
| No relevant context found | Answer uses only LLM knowledge, no citations |

---

## 4. Document Management

### 4.1 Upload Document

**`POST /api/documents`** — Upload a file for ingestion. Supports two execution modes.

**Auth:** JWT required  
**Content-Type:** `multipart/form-data`

**Form fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | Yes | The document file |
| `notebook_id` | int | No | Target notebook for scoping |
| `pipeline_version` | str | No | Override default pipeline version |

**Allowed file types:** `.pdf`, `.docx`, `.html`, `.htm`, `.md`  
**Tabular file types:** `.xlsx`, `.xls`, `.csv`  
**Max upload size:** 20 MB (configurable via `MAX_UPLOAD_SIZE_MB`)

```mermaid
flowchart TD
    A[POST /api/documents] --> B{File extension?}
    B -->|.pdf .docx .html .md| C[Check file size]
    B -->|.xlsx .xls .csv| D[Tabular pipeline]
    C --> E{Size > MAX_UPLOAD?}
    E -->|Yes| F[413 Payload Too Large]
    E -->|No| G[Save to object storage]
    G --> H[Check content_hash duplicate]
    H -->|Duplicate in notebook| I[409 Conflict]
    H -->|Unique| J{Queue idle and<br/>sync_ingest_when_queue_idle?}
    J -->|Yes| K[Run sync in threadpool]
    J -->|No| L[Enqueue Celery task]
    K --> M[Parse -> Chunk -> Embed -> Index]
    M --> N[200: return chunks/pages]
    L --> O[202: return job_id, status=queued]
    D --> P[Tabular chunk -> Embed -> SQL]
    P --> Q[200: return tables/rows]
```

**Figure 2: Upload decision flow (sync vs async).**

#### Sync Response (200) — Regular document:
```json
{
  "document_id": "uuid",
  "job_id": "uuid",
  "status": "completed",
  "pipeline_version": "1.0.0",
  "object_key": "uuid/filename.pdf",
  "pages": 10,
  "chunks": 45
}
```

#### Sync Response (200) — Tabular document:
```json
{
  "document_id": "uuid",
  "job_id": "uuid",
  "status": "completed",
  "pipeline_version": "1.0.0",
  "object_key": "uuid/file.xlsx",
  "tables": ["sheet_table"],
  "rows": 100
}
```

#### Async Response (202):
```json
{
  "document_id": "uuid",
  "job_id": "uuid",
  "status": "queued",
  "pipeline_version": "1.0.0",
  "object_key": "uuid/filename.pdf"
}
```

#### Duplicate Response (409):
```json
{
  "error": {
    "code": "http_409",
    "message": "A document with identical content already exists in this notebook.",
    "request_id": "uuid"
  },
  "detail": "A document with identical content already exists in this notebook."
}
```

**Sync condition:** When `SYNC_INGEST_WHEN_QUEUE_IDLE=true` AND the Celery queue has no active tasks, the ingest runs directly in the backend process via `asyncio.to_thread()`. This avoids the Celery round-trip latency for single-user scenarios.

### 4.2 List Documents

**`GET /api/documents`** — List documents owned by the current user.

**Auth:** JWT required  
**Query parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `notebook_id` | int | No | Filter by notebook |

**Success (200):**
```json
[
  {
    "document_id": "uuid",
    "owner_id": 1,
    "notebook_id": 1,
    "filename": "philosophy_chapter_3.pdf",
    "object_key": "uuid/philosophy_chapter_3.pdf",
    "mime_type": "application/pdf",
    "size_bytes": 2048576,
    "created_at": "2026-05-27T10:00:00Z",
    "updated_at": "2026-05-27T10:05:00Z",
    "latest_job": {
      "job_id": "uuid",
      "status": "succeeded",
      "stage": "loading_sql",
      "progress_pct": 100,
      "stage_detail": null,
      "error_message": null,
      "pipeline_version": "1.0.0",
      "queued_at": "2026-05-27T10:00:01Z",
      "started_at": "2026-05-27T10:00:02Z",
      "finished_at": "2026-05-27T10:03:15Z"
    }
  }
]
```

Soft-deleted documents (`deleted_at IS NOT NULL`) are excluded.

### 4.3 Delete Document

**`DELETE /api/documents/{document_id}`** — Soft-delete a document and clean up resources.

**Auth:** JWT required  
**Success (200):**
```json
{
  "document_id": "uuid",
  "deleted": true,
  "status": "completed",
  "cleanup": {
    "qdrant_vectors": 45,
    "storage_object": true,
    "excel_tables": 0,
    "chunks_deleted": 45
  },
  "cleanup_errors": []
}
```

**Cleanup actions:**
1. Cancel any running ingest jobs
2. Delete Qdrant vectors for this document
3. Delete object storage file
4. Delete document chunks from PostgreSQL
5. Delete Excel table records
6. Set `deleted_at` on the document record

**Errors:** 404 (not found), 403 (not owner)

### 4.4 Replace Document

**`POST /api/documents/{document_id}`** — Replace the file content of an existing document.

**Auth:** JWT required  
**Content-Type:** `multipart/form-data`

**Form fields:** Same as upload. The document keeps its original `document_id`.

**Success (200):** Same format as upload response.

**Errors:** 404 (not found), 400 (bad file type), 413 (too large)

### 4.5 Reindex Document

**`POST /api/documents/{document_id}/reindex`** — Re-process an already-ingested document.

**Auth:** JWT required  
**Request:**
```json
{
  "pipeline_version": "1.1.0"
}
```

If `pipeline_version` is null, the current default version is used. The reindex always goes through Celery (async).

**Success (202):**
```json
{
  "document_id": "uuid",
  "job_id": "uuid",
  "status": "queued",
  "pipeline_version": "1.1.0"
}
```

**Errors:** 404 (not found), 400 (invalid version)

### 4.6 URL Ingest

**`POST /api/ingest/url`** — Ingest content from a URL.

**Auth:** JWT required  
**Request:**
```json
{
  "url": "https://example.com/article",
  "notebook_id": null
}
```

Always async (Celery). The URL is validated for safety and accessibility before enqueuing.

**Success (202):**
```json
{
  "document_id": "uuid",
  "job_id": "uuid",
  "status": "queued",
  "pipeline_version": "1.0.0",
  "url": "https://example.com/article"
}
```

**Errors:** 400 (invalid/unsafe URL), 500 (enqueue failure)

### 4.7 Job Status

**`GET /api/jobs/{job_id}`** — Poll the status of an ingest job.

**Auth:** JWT required  
**Success (200):**
```json
{
  "job_id": "uuid",
  "document_id": "uuid",
  "status": "running",
  "stage": "embedding",
  "progress_pct": 60,
  "stage_detail": "Processing batch 18/30",
  "error_message": null,
  "pipeline_version": "1.0.0",
  "queued_at": "2026-05-27T10:00:01Z",
  "started_at": "2026-05-27T10:00:02Z",
  "finished_at": null
}
```

**Status values:** `queued`, `running`, `succeeded`, `failed`, `cancelled`  
**Stage values:** `fetching_object`, `parsing`, `chunking`, `embedding`, `indexing_vector`, `persisting_metadata`, `loading_sql`

### 4.8 Document Assets

**Router:** `backend/app/routers/documents.py`

#### Page Image
**`GET /api/documents/page-image/{filename}/{page_number}`**  
**`GET /api/documents/{document_id}/page-image/{page_number}`**

Returns a PNG rendering of a specific PDF page. Supports look-up by both filename and document_id.

**Auth:** JWT required  
**Response:** `image/png` binary  
**Errors:** 404 (page not found, document not found), 500 (rendering failure)

#### File Download
**`GET /api/documents/file/{filename}`**  
**`GET /api/documents/{document_id}/file`**

Streams the original uploaded file with HTTP Range header support.

**Auth:** JWT required  
**Response:** Binary file with appropriate `Content-Type`  
**Headers:** `Accept-Ranges: bytes`  
**Range support:** Returns `206 Partial Content` for valid range requests, `200` for full file  
**Errors:** 404 (not found), 416 (range not satisfiable)

---

## 5. Notebook Endpoints

**Router:** `backend/app/routers/notebooks.py`  
**Base path:** `/api/notebooks`

### 5.1 Notebook CRUD

#### List Notebooks
**`GET /api/notebooks`**

Returns notebooks visible to the current user (own + community).

**Auth:** JWT required  
**Success (200):**
```json
[
  {
    "id": 1,
    "title": "Philosophy 101",
    "owner_id": 1,
    "is_community": false,
    "cover_url": "https://example.com/cover.jpg",
    "cover_mode": "cover",
    "cover_color": null,
    "created_at": "2026-05-27T10:00:00Z"
  }
]
```

#### Create Notebook
**`POST /api/notebooks`** — Create a new notebook.

**Auth:** JWT required  
**Request:**
```json
{
  "title": "Philosophy 101",
  "is_community": false
}
```

**Success (201):** Same format as list response.

#### Update Notebook
**`PATCH /api/notebooks/{notebook_id}`**

**Auth:** JWT required  
**Request (all fields optional):**
```json
{
  "title": "Renamed Notebook",
  "cover_url": "https://example.com/new-cover.jpg",
  "cover_mode": "contain",
  "cover_color": "#336699"
}
```

**Success (200):** Updated notebook object.

#### Delete Notebook
**`DELETE /api/notebooks/{notebook_id}`**

Deletes notebook + all contained documents, chunks, conversations, and saved items.

**Auth:** JWT required  
**Success (200):**
```json
{
  "deleted": true,
  "status": "completed",
  "cleanup_errors": []
}
```

**Errors:** 403 (not owner), 404 (not found)

### 5.2 Conversations

#### Latest Conversation
**`GET /api/notebooks/{notebook_id}/conversations/latest?limit=50`**

**Auth:** JWT required  
**Query:** `limit` (1–200, default 50) — number of recent messages to load

**Success (200):**
```json
{
  "has_conversation": true,
  "conversation": {
    "id": "conv-uuid",
    "notebook_id": 1,
    "owner_id": 1,
    "created_at": "2026-05-27T10:00:00Z",
    "updated_at": "2026-05-27T10:05:00Z"
  },
  "messages": [
    {
      "id": "msg-uuid",
      "role": "user",
      "content": "What is knowledge?",
      "sources_used": null,
      "rewritten_query": null,
      "created_at": "2026-05-27T10:00:00Z"
    },
    {
      "id": "msg-uuid-2",
      "role": "assistant",
      "content": "Knowledge is justified true belief [C1].",
      "sources_used": [
        {
          "citation_id": "C1",
          "source": "philosophy.pdf",
          "page": 42
        }
      ],
      "rewritten_query": "What is knowledge according to philosophy?",
      "created_at": "2026-05-27T10:00:05Z"
    }
  ],
  "limit": 50
}
```

### 5.3 Notes and Pins

#### Save Note/Pin/Summary
**`POST /api/notebooks/{notebook_id}/notes`**

**Auth:** JWT required  
**Request:**
```json
{
  "kind": "note",
  "content": "Key insight: Plato's theory of forms...",
  "title": "Important Note",
  "conversation_id": null,
  "message_id": null,
  "sources_used": null
}
```

**kind values:** `note`, `pin`, `conversation`, `summary`

**Success (201):**
```json
{
  "id": "item-uuid",
  "notebook_id": 1,
  "kind": "note",
  "title": "Important Note",
  "content": "Key insight: Plato's theory of forms...",
  "conversation_id": null,
  "message_id": null,
  "sources_used": null,
  "created_at": "2026-05-27T10:00:00Z"
}
```

### 5.4 File Management

#### Rename File
**`PATCH /api/notebooks/{notebook_id}/files/{file_id}/rename`**

**Auth:** JWT required  
**Request:**
```json
{
  "new_file_name": "renamed_chapter.pdf"
}
```

Updates the display name in both PostgreSQL and object storage metadata.

**Success (200):** `{"status": "ok"}`  
**Errors:** 403 (not owner), 404 (not found), 400 (invalid name)

#### Delete File
**`DELETE /api/notebooks/{notebook_id}/files/{file_id}`**

Deletes a single file from the notebook (soft-delete + cleanup).

**Auth:** JWT required  
**Success (200):**
```json
{
  "deleted": true,
  "status": "completed",
  "cleanup_errors": []
}
```

### 5.5 Copy Notebook

**`POST /api/notebooks/{notebook_id}/copy`**

Creates a copy of the notebook and all its documents. Documents are re-ingested via Celery (async).

**Auth:** JWT required  
**Success (201):**
```json
{
  "notebook": {
    "id": 2,
    "title": "Philosophy 101 (Copy)",
    "owner_id": 1,
    "is_community": false,
    "cover_url": null,
    "cover_mode": null,
    "cover_color": null,
    "created_at": "2026-05-27T11:00:00Z"
  },
  "documents_copied": 3,
  "jobs_enqueued": 3
}
```

**Errors:** 404 (not found), 500 (copy failure)

---

## 6. Admin Endpoints

**Router:** `backend/app/routers/admin.py`  
**Base path:** `/api/admin`  
**Auth:** JWT required + admin role (email must end with `@lumina.com.vn`)

| Method | Path | Description | Success |
|--------|------|-------------|---------|
| `GET` | `/api/admin/users` | List all users | 200: `[{id, username, email}]` |
| `POST` | `/api/admin/users` | Create user | 201: `{id, username, email}` |
| `DELETE` | `/api/admin/users/{user_id}` | Delete user + all content | 200: `{deleted, status}` |
| `GET` | `/api/admin/library` | Full hierarchy: users -> notebooks -> documents | 200: `{users: [{id, notebooks: [{id, documents}]}]}` |
| `GET` | `/api/admin/documents` | List all documents | 200: `[{document_id, filename, ...}]` |
| `DELETE` | `/api/admin/documents/{document_id}` | Force-delete document | 200: `{deleted, status, cleanup_errors}` |
| `DELETE` | `/api/admin/notebooks/{notebook_id}` | Force-delete notebook | 200: `{deleted, status, cleanup_errors}` |
| `GET` | `/api/admin/api-config` | Read .env (sensitive values masked) | 200: `{entries: [{key, value, sensitive}]}` |
| `POST` | `/api/admin/documents/{document_id}/reindex` | Admin reindex | 202: `{document_id, job_id, status}` |

**Admin User Create:**
```json
{
  "username": "admin_user",
  "email": "admin@lumina.com.vn",
  "password": "securePassword456"
}
```

**Library View (GET /api/admin/library):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@gmail.com",
      "notebooks": [
        {
          "id": 1,
          "title": "Philosophy 101",
          "owner_id": 1,
          "is_community": false,
          "cover_url": null,
          "cover_mode": null,
          "cover_color": null,
          "is_virtual": false,
          "documents": [
            {
              "document_id": "uuid",
              "filename": "philosophy_chapter_3.pdf",
              "object_key": "uuid/philosophy_chapter_3.pdf",
              "mime_type": "application/pdf",
              "size_bytes": 2048576,
              "created_at": "2026-05-27T10:00:00Z",
              "updated_at": "2026-05-27T10:05:00Z",
              "latest_job": {
                "job_id": "uuid",
                "status": "succeeded",
                "stage": "loading_sql",
                "progress_pct": 100,
                "stage_detail": null,
                "error_message": null,
                "pipeline_version": "1.0.0",
                "queued_at": "2026-05-27T10:00:01Z",
                "started_at": "2026-05-27T10:00:02Z",
                "finished_at": "2026-05-27T10:03:15Z"
              }
            }
          ]
        }
      ]
    }
  ]
}
```

**API Config (GET /api/admin/api-config):** Reads the .env file and returns each key with a masked value for sensitive entries:
```json
{
  "entries": [
    { "key": "APP_ENV", "value": "production", "sensitive": false },
    { "key": "GEMINI_API_KEY", "value": "----****----", "sensitive": true }
  ]
}
```

If the .env file cannot be read (e.g., not mounted in container), returns 404.

---

## 7. Common Error Responses

| Status Code | `code` | Typical Cause |
|------------|--------|---------------|
| 400 | `http_400` | Bad request (invalid file format, empty message, invalid pipeline_version) |
| 401 | `http_401` | Missing, invalid, or expired JWT token |
| 403 | `http_403` | Admin access required (non-admin email) |
| 404 | `http_404` | Resource not found (document, notebook, job, user) |
| 409 | `http_409` | Conflict (duplicate document content in notebook) |
| 413 | `http_413` | Payload too large (file exceeds `MAX_UPLOAD_SIZE_MB`) |
| 422 | `validation_error` | Request body validation failure |
| 500 | `internal_error` | Unhandled server error |
| 503 | `embedding_service_unavailable` | Embedding service is down or timing out |

**Rate limiting:** Not currently implemented.

---

## Endpoint Index

| # | Method | Path | Auth | Router | Section |
|---|--------|------|------|--------|---------|
| 1 | `GET` | `/` | None | main.py | Health check |
| 2 | `POST` | `/api/signup` | None | auth.py | 2.1 |
| 3 | `POST` | `/api/login` | None | auth.py | 2.2 |
| 4 | `POST` | `/api/change-password` | JWT | auth.py | 2.3 |
| 5 | `GET` | `/api/auth/me` | JWT | auth.py | 2.4 |
| 6 | `POST` | `/api/password/forgot` | None | password_reset.py | 2.5 |
| 7 | `POST` | `/api/password/verify` | None | password_reset.py | 2.5 |
| 8 | `POST` | `/api/password/reset` | None | password_reset.py | 2.5 |
| 9 | `POST` | `/api/chat` | JWT | chat.py | 3.1 |
| 10 | `POST` | `/api/chat/stream` | JWT | chat.py | 3.2 |
| 11 | `POST` | `/api/documents` | JWT | ingest.py | 4.1 |
| 12 | `GET` | `/api/documents` | JWT | ingest.py | 4.2 |
| 13 | `DELETE` | `/api/documents/{id}` | JWT | ingest.py | 4.3 |
| 14 | `POST` | `/api/documents/{id}` | JWT | ingest.py | 4.4 |
| 15 | `POST` | `/api/documents/{id}/reindex` | JWT | ingest.py | 4.5 |
| 16 | `POST` | `/api/ingest/url` | JWT | ingest.py | 4.6 |
| 17 | `GET` | `/api/jobs/{id}` | JWT | ingest.py | 4.7 |
| 18 | `GET` | `/documents/page-image/{filename}/{page}` | JWT | documents.py | 4.8 |
| 19 | `GET` | `/api/documents/page-image/{filename}/{page}` | JWT | documents.py | 4.8 |
| 20 | `GET` | `/api/documents/{id}/page-image/{page}` | JWT | documents.py | 4.8 |
| 21 | `GET` | `/documents/file/{filename}` | JWT | documents.py | 4.8 |
| 22 | `GET` | `/api/documents/file/{filename}` | JWT | documents.py | 4.8 |
| 23 | `GET` | `/api/documents/{id}/file` | JWT | documents.py | 4.8 |
| 24 | `GET` | `/api/notebooks` | JWT | notebooks.py | 5.1 |
| 25 | `POST` | `/api/notebooks` | JWT | notebooks.py | 5.1 |
| 26 | `PATCH` | `/api/notebooks/{id}` | JWT | notebooks.py | 5.1 |
| 27 | `DELETE` | `/api/notebooks/{id}` | JWT | notebooks.py | 5.1 |
| 28 | `POST` | `/api/notebooks/{id}/copy` | JWT | notebooks.py | 5.5 |
| 29 | `GET` | `/api/notebooks/{id}/conversations/latest` | JWT | notebooks.py | 5.2 |
| 30 | `POST` | `/api/notebooks/{id}/notes` | JWT | notebooks.py | 5.3 |
| 31 | `PATCH` | `/api/notebooks/{id}/files/{fid}/rename` | JWT | notebooks.py | 5.4 |
| 32 | `DELETE` | `/api/notebooks/{id}/files/{fid}` | JWT | notebooks.py | 5.4 |
| 33 | `GET` | `/api/admin/users` | Admin | admin.py | 6 |
| 34 | `POST` | `/api/admin/users` | Admin | admin.py | 6 |
| 35 | `DELETE` | `/api/admin/users/{id}` | Admin | admin.py | 6 |
| 36 | `GET` | `/api/admin/library` | Admin | admin.py | 6 |
| 37 | `DELETE` | `/api/admin/documents/{id}` | Admin | admin.py | 6 |
| 38 | `DELETE` | `/api/admin/notebooks/{id}` | Admin | admin.py | 6 |
| 39 | `GET` | `/api/admin/documents` | Admin | admin.py | 6 |
| 40 | `GET` | `/api/admin/api-config` | Admin | admin.py | 6 |
| 41 | `POST` | `/api/admin/documents/{id}/reindex` | Admin | admin.py | 6 |

---

## References

| Reference | File |
|-----------|------|
| App setup | `backend/app/main.py` |
| Auth router | `backend/app/routers/auth.py` |
| Chat router | `backend/app/routers/chat.py` |
| Document router | `backend/app/routers/ingest.py` |
| Legacy document assets | `backend/app/routers/documents.py` |
| Notebook router | `backend/app/routers/notebooks.py` |
| Admin router | `backend/app/routers/admin.py` |
| Password reset router | `backend/app/routers/password_reset.py` |
| Chat runtime service | `backend/app/services/chat_runtime.py` |
| Embedding client | `backend/app/services/embedding_client.py` |
| Chat history service | `backend/app/services/chat_history.py` |
| Pydantic schemas | `backend/app/schemas.py` |
| Security / JWT | `backend/app/core/security.py` |
| Auth dependencies | `backend/app/core/dependencies.py` |
| Settings | `backend/app/core/settings.py` |
