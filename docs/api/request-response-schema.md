# Request/Response Schemas

## Authentication Schemas

### UserCreate (signup)
```python
class UserCreate(BaseModel):
    username: str          # Required, unique
    email: EmailStr       # Must end with @gmail.com or @lumina.com.vn
    password: str         # 6-128 characters
```

### UserLogin (login)
```python
class UserLogin(BaseModel):
    email: EmailStr       # Must end with @gmail.com or @lumina.com.vn
    password: str
```

### Token (response)
```python
class Token(BaseModel):
    access_token: str     # JWT token
    token_type: str       # "bearer"
```

### ChangePassword
```python
class ChangePassword(BaseModel):
    current_password: str  # Current password
    new_password: str      # 6-128 characters
```

## Chat Schemas

### ChatRequest (POST /api/chat/stream)
```json
{
    "message": "What is philosophy?",
    "conversation_id": "optional-existing-conversation-id",
    "notebook_id": 1
}
```

Only `message` is required. The backend creates a conversation when `conversation_id` is omitted.

### SSE Response Format
```json
{"type": "token", "token": "chunk_of_text", "done": false}
{"type": "final", "token": "", "done": true, "answer": "... [C1]", "citations": [{"citation_id": "C1", "rank": 1, "source": "intro.pdf", "page": 12, "snippet": "...", "document_id": "uuid", "chunk_id": "uuid", "doc_id": "uuid"}], "conversation_id": "uuid", "message_id": "uuid", "rewritten_query": "..."}
{"type": "error", "token": "", "done": true, "error": "chat_stream_failed", "citations": []}
```

Final `citations` includes only citations whose marker appears in `answer`.

### Error Response Format
```json
{"type": "error", "token": "", "done": true, "error": "Failed to generate answer", "citations": []}
```

## Document Schemas

### Upload Response
```json
{
    "document_id": "doc-uuid",
    "job_id": "job-uuid",
    "status": "queued",
    "pipeline_version": "v1",
    "object_key": "doc-uuid/philosophy.pdf"
}
```

### Job Response
```json
{
    "job_id": "job-uuid",
    "document_id": "doc-uuid",
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
```

### Error Responses

**400 - Bad Request:**
```json
{"detail": "No filename provided."}
{"detail": "Only PDF files are supported."}
{"detail": "Message cannot be empty."}
```

**401 - Unauthorized:**
```json
{"detail": "Missing or invalid authorization header"}
{"detail": "Invalid token"}
{"detail": "User not found"}
```

**404 - Not Found:**
```json
{"detail": "Page or file not found"}
```

**500 - Internal Server Error:**
```json
{"detail": "Failed to process file: error message"}
```

Current backend errors are wrapped in a stable envelope:

```json
{
  "error": {
    "code": "http_400",
    "message": "Message cannot be empty",
    "request_id": "uuid",
    "details": null
  },
  "detail": "Message cannot be empty"
}
```

## Field Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| `email` | Must end with @gmail.com or @lumina.com.vn | "Hệ thống chỉ chấp nhận tài khoản @gmail.com hoặc @lumina.com.vn" |
| `password` | Minimum 6 characters | "Password must be at least 6 characters" |
| `password` | Maximum 128 characters | "Password must be less than 128 characters" |
| `username` | Must be unique | "User name đã tồn tại, vui lòng chọn tên khác!" |
| `email` | Must be unique | "Email đã được sử dụng, vui lòng chọn email khác!" |
