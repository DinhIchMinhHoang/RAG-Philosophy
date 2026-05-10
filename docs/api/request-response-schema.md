# Request/Response Schemas

## Authentication Schemas

### UserCreate (signup)
```python
class UserCreate(BaseModel):
    username: str          # Required, unique
    email: EmailStr       # Must end with @gmail.com
    password: str         # 6-128 characters
```

### UserLogin (login)
```python
class UserLogin(BaseModel):
    email: EmailStr       # Must end with @gmail.com
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

### ChatRequest (POST /chat/stream)
```json
{
    "message": "What is philosophy?"
}
```

### SSE Response Format
```json
{"token": "chunk_of_text"}
{"token": "", "done": true}
```

### Error Response Format
```json
{"token": "\n\n⚠️ Lỗi: error message", "done": true}
```

## Document Schemas

### Upload Response
```json
{
    "filename": "philosophy.pdf",
    "status": "ok",
    "pages": 45,
    "chunks": 180
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
| `email` | Must end with @gmail.com | "Hệ thống chỉ chấp nhận tài khoản @gmail.com" |
| `password` | Minimum 6 characters | "Password must be at least 6 characters" |
| `password` | Maximum 128 characters | "Password must be less than 128 characters" |
| `username` | Must be unique | "User name đã tồn tại, vui lòng chọn tên khác!" |
| `email` | Must be unique | "Email đã được sử dụng, vui lòng chọn email khác!" |