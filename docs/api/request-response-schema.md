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

### PasswordForgotRequest
```python
class PasswordForgotRequest(BaseModel):
    email: EmailStr
```

### PasswordVerifyRequest
```python
class PasswordVerifyRequest(BaseModel):
    email: EmailStr
    code: str
```

### PasswordResetRequest
```python
class PasswordResetRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str      # 6-128 characters
```

## Chat Schemas

### ChatRequest (POST /api/chat/stream)
```json
{
    "message": "What is philosophy?",
    "conversation_id": "optional-existing-conversation-id",
    "notebook_id": 1,
    "selected_source_ids": ["doc_1", "doc_2"]
}
```

Only `message` is required. The backend creates a conversation when `conversation_id` is omitted.

`selected_source_ids` is optional:

- non-empty list => retrieval is filtered to those document IDs
- empty list or omitted => explicit fallback to all notebook sources
- when `notebook_id` is provided, IDs must belong to the authenticated user and notebook, otherwise `404`

### SSE Response Format
```json
{"type": "token", "token": "chunk_of_text", "done": false}
{"type": "final", "token": "", "done": true, "answer": "... [C1]", "citations": [{"citation_id": "C1", "rank": 1, "source": "intro.pdf", "page": 12, "snippet": "...", "document_id": "uuid", "chunk_id": "uuid", "doc_id": "uuid"}], "conversation_id": "uuid", "message_id": "uuid", "rewritten_query": "..."}
{"type": "error", "token": "", "done": true, "error": "chat_stream_failed", "citations": []}
```

Final `citations` includes only citations whose marker appears in `answer`.

### Latest Notebook Conversation

`GET /api/notebooks/{notebook_id}/conversations/latest?limit=50`

```json
{
    "conversation": {"id": "uuid", "notebook_id": 1, "owner_id": 1, "created_at": "...", "updated_at": "..."},
    "messages": [{"id": "uuid", "role": "assistant", "content": "...", "sources_used": [], "rewritten_query": null, "created_at": "..."}],
    "has_conversation": true,
    "limit": 50
}
```

If the notebook has no history, `conversation` is `null` and `messages` is `[]`.

### Saved Notebook Item

`POST /api/notebooks/{notebook_id}/notes`

```json
{
    "kind": "note",
    "title": "Saved message",
    "content": "...",
    "conversation_id": "optional-uuid",
    "message_id": "optional-uuid",
    "sources_used": []
}
```

Saved items are stored separately from normal chat history so future chat TTL cleanup does not delete user-selected notes or pins.

### Error Response Format
```json
{"type": "error", "token": "", "done": true, "error": "Failed to generate answer", "citations": []}
```

## Document Schemas

### Upload Response

Supported upload file types: PDF, DOCX, HTML/HTM, and Markdown. Excel/CSV tabular ingest is temporarily disabled, so `.xlsx`, `.xls`, and `.csv` return `400 Unsupported format`.

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
{"detail": "Unsupported format: .csv. Supported: .docx, .htm, .html, .md, .pdf"}
{"detail": "Unsupported format while tabular ingest is disabled"}
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
