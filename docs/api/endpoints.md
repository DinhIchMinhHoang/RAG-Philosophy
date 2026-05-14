# API Endpoints

> Freeze note: canonical non-admin contract now lives in `docs/api/non-admin-contract-v1.md` with `/api/*` paths and legacy alias mapping.

## Base URL

```
http://localhost:8000
```

## Authentication Endpoints

### POST /signup

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

### POST /login

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

### POST /change-password

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

### POST /documents/upload

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

**Response (201):**
```json
{
    "filename": "philosophy101.pdf",
    "status": "ok",
    "pages": 45,
    "chunks": 180
}
```

**Errors:**
- 400: No filename provided
- 400: Not a PDF file
- 500: Processing failed

---

### GET /documents/sources

List currently ingested source files.

**Response (200):**
```json
{
    "sources": ["philosophy101.pdf", "ethics.pdf"],
    "count": 2,
    "has_sources": true
}
```

---

### POST /documents/reset

Clear all ingested documents.

**Response (200):**
```json
{
    "message": "All sources cleared. Pipeline reset."
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

### POST /chat/stream

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

## Public Endpoints

### GET /

Health check endpoint.

**Response (200):**
```json
{
    "message": "Chào mừng đến hệ thống Lumina RAG"
}
```
