# API Endpoints

> Freeze note: canonical non-admin contract now lives in `docs/api/non-admin-contract-v1.md` with `/api/*` paths.

## Base URL

```
http://localhost:8000
```

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

---

### GET /documents/page-image/{filename}/{page_number}

Get a rendered page from a PDF as PNG.

**Response (200):**
- Content-Type: image/png
- Body: PNG bytes

**Errors:**
- 404: File or page not found

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
data: {"token": "", "done": true}
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
    "citations": []
}
```

**Errors:**
- 400: Empty message
- 500: Processing error

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
    "message": "Chào mừng đến hệ thống Lumina RAG"
}
```
