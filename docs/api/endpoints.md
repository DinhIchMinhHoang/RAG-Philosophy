# API Endpoints

> Freeze note: canonical non-admin contract now lives in `docs/api/non-admin-contract-v1.md` with `/api/*` paths.

## Base URL

```
http://localhost
```

The browser and frontend client talk to the API through the Nginx entrypoint at `/api/*`.

## Authentication Endpoints

### POST /api/signup

Create a new user account.

**Request Body:**
```json
{
    "username": "johndoe",
    "email": "johndoe@gmail.com",
    "password": "securepass123"
}
```

**Response (201):**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

**Errors:**
- 400: Email already used
- 400: Username already exists
- 400: Password < 6 characters

---

### POST /api/login

Authenticate and receive JWT token.

**Request Body:**
```json
{
    "email": "johndoe@gmail.com",
    "password": "securepass123"
}
```

**Response (200):**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

**Errors:**
- 401: Invalid credentials

---

### POST /api/change-password

Change user's password (requires authentication).

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Request Body:**
```json
{
    "current_password": "oldpass123",
    "new_password": "newpass456"
}
```

**Response (200):**
```json
{
    "message": "Password changed successfully!"
}
```

**Errors:**
- 401: Invalid current password
- 400: New password same as current

---

### POST /api/password/forgot

Request a password reset code. The response is intentionally generic and does not reveal whether the email exists.

**Request Body:**
```json
{
    "email": "johndoe@gmail.com"
}
```

**Response (200):**
```json
{
    "message": "If an account exists for this email, a verification code has been sent."
}
```

---

### POST /api/password/verify

Verify a password reset code.

**Request Body:**
```json
{
    "email": "johndoe@gmail.com",
    "code": "123456"
}
```

**Response (200):**
```json
{
    "verified": true
}
```

**Errors:**
- 400: Invalid or expired code

---

### POST /api/password/reset

Reset a password using a valid reset code.

**Request Body:**
```json
{
    "email": "johndoe@gmail.com",
    "code": "123456",
    "new_password": "newpass456"
}
```

**Response (200):**
```json
{
    "message": "Password reset successful"
}
```

**Errors:**
- 400: Invalid or expired code
- 400: User not found

---

## Document Endpoints

### POST /api/documents

Upload a PDF for RAG ingestion.

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: multipart/form-data
```

**Body:**
```
file: <PDF file>
```

**Response (202):**
```json
{
    "document_id": "doc-uuid",
    "job_id": "job-uuid",
    "status": "queued",
    "pipeline_version": "v1",
    "object_key": "doc-uuid/philosophy101.pdf"
}
```

**Errors:**
- 400: No filename provided
- 400: Not a PDF file
- 500: Processing failed

---

### GET /api/documents

List currently ingested source files.

**Response (200):**
```json
[
    {
        "document_id": "doc-uuid",
        "filename": "philosophy101.pdf",
        "object_key": "doc-uuid/philosophy101.pdf",
        "mime_type": "application/pdf",
        "size_bytes": 123456,
        "created_at": "2026-05-15T10:00:00Z",
        "updated_at": "2026-05-15T10:00:00Z",
        "latest_job": {
            "job_id": "job-uuid",
            "status": "queued",
            "stage": "fetching_object",
            "progress_pct": 0,
            "stage_detail": "queued",
            "error_message": null,
            "pipeline_version": "v1",
            "queued_at": "2026-05-15T10:00:00Z",
            "started_at": null,
            "finished_at": null
        }
    }
]
```

`latest_job` is the newest ingest or reindex job for that document. During Celery retries, the same job id may temporarily move back to `queued` before the worker restarts it from `fetching_object`.

---

### DELETE /api/documents/{document_id}

Delete a document and associated vectors.

**Response (200):**
```json
{
  "document_id": "doc-uuid",
  "deleted": true,
  "status": "deleted"
}
```

### POST /api/documents/{document_id}/reindex

Start a new ingest job for an existing document.

**Request Body:**
```json
{
    "pipeline_version": "v1"
}
```

The JSON body is required, but `pipeline_version` is optional when the backend default pipeline version is acceptable.

**Response (202):**
```json
{
    "document_id": "doc-uuid",
    "job_id": "job-uuid",
    "status": "queued",
    "pipeline_version": "v1",
    "object_key": "doc-uuid/philosophy101.pdf"
}
```

---

### GET /api/documents/{document_id}/file

Stream the original stored source file for the Source Viewer.

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Range: bytes=0-99
```

The browser viewer may also authenticate with `?token=<JWT_TOKEN>` because iframe requests cannot attach custom headers.

**Response (200):**
- `Content-Type`: document `mime_type`
- `Content-Disposition`: `inline`
- `Accept-Ranges`: `bytes`
- Body: full source bytes

**Response (206):**
- `Content-Range`: requested byte range
- Body: requested byte range only

**Errors:**
- 404: File not found or not owned by the current user
- 416: Invalid or out-of-bounds range

PDF citation jumps use the browser PDF viewer fragment:

```
/api/documents/{document_id}/file?token=<JWT_TOKEN>#page=12
```

---

### GET /api/documents/{document_id}/page-image/{page_number}

Get a rendered page from a PDF as PNG.

Legacy-only preview path. The Source Viewer should use `/api/documents/{document_id}/file` and must not call this endpoint for citation clicks.

**Response (200):**
- Content-Type: image/png
- Body: PNG bytes

**Errors:**
- 404: File or page not found

Legacy aliases still exist for filename-based access:

- `GET /documents/page-image/{filename}/{page_number}`
- `GET /api/documents/page-image/{filename}/{page_number}`

---

## Chat Endpoints

### POST /api/chat/stream

Send a question and receive streamed answer via SSE.

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Request Body:**
```json
{
    "message": "What is the main argument of the text?"
}
```

**Response (200):**
```
Content-Type: text/event-stream

data: {"token": "Dựa "}
data: {"token": "trên "}
data: {"token": "tài "}
data: {"token": "liệu, "}
...
data: {"type": "final", "token": "", "done": true, "answer": "...", "citations": [], "conversation_id": "uuid", "message_id": "uuid", "rewritten_query": "..."}
data: {"type": "error", "token": "", "done": true, "error": "chat_stream_failed", "citations": []}
```

**Errors:**
- 400: Empty message
- 500: Processing error

---

### POST /api/chat

Send a question and receive a non-streamed answer.

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Request Body:**
```json
{
    "message": "What is the main argument of the text?"
}
```

**Response (200):**
```json
{
    "answer": "...",
    "citations": [],
    "conversation_id": "uuid",
    "message_id": "uuid",
    "rewritten_query": "..."
}
```

**Errors:**
- 400: Empty message
- 500: Processing error

---

### GET /api/notebooks/{notebook_id}/conversations/latest

Load the authenticated user's latest non-archived conversation for one notebook.

**Query:**
- `limit`: max messages to return, clamped to 1..100, default 50

**Response (200):**
```json
{
    "conversation": {"id": "uuid", "notebook_id": 1, "owner_id": 1, "created_at": "...", "updated_at": "..."},
    "messages": [],
    "has_conversation": false,
    "limit": 50
}
```

The endpoint returns empty state for notebooks with no history and never falls back to another notebook.

---

### POST /api/notebooks/{notebook_id}/notes

Save long-term notebook content such as pins, notes, saved conversations, or summary drafts.

**Request Body:**
```json
{
    "kind": "pin",
    "title": "Important answer",
    "content": "...",
    "conversation_id": "optional-uuid",
    "message_id": "optional-uuid",
    "sources_used": []
}
```

Saved items are separate from normal chat history and are not affected by UI cache TTL.

---

## Admin Endpoints

### GET /api/admin/users

List all users.

### POST /api/admin/users

Create a user.

### DELETE /api/admin/users/{user_id}

Delete a user by ID.

### GET /api/admin/documents

List all documents.

### GET /api/admin/jobs

List all jobs.

---

## Public Endpoints

### GET /

Health check endpoint.

**Response (200):**
```json
{
    "message": "Welcome to Lumina RAG"
}
```
