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
    "message": "What is philosophy?"
}
```

### SSE Response Format
```json
{"type": "token", "token": "chunk_of_text", "done": false}
{"type": "final", "token": "", "done": true, "answer": "...", "citations": []}
```

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

## Field Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| `email` | Must end with @gmail.com or @lumina.com.vn | "Hệ thống chỉ chấp nhận tài khoản @gmail.com hoặc @lumina.com.vn" |
| `password` | Minimum 6 characters | "Password must be at least 6 characters" |
| `password` | Maximum 128 characters | "Password must be less than 128 characters" |
| `username` | Must be unique | "User name đã tồn tại, vui lòng chọn tên khác!" |
| `email` | Must be unique | "Email đã được sử dụng, vui lòng chọn email khác!" |
