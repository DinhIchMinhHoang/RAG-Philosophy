# Authentication Notes

## JWT Configuration

```python
# backend/app/core/security.py

SECRET_KEY = os.getenv("SECRET_KEY", "khoa_du_phong_neu_quen_tao_env")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
```

## Token Structure

JWT payload contains:
```json
{
    "exp": 1699999999,    # Expiration timestamp (UTC)
    "sub": "johndoe"      # Username (subject)
}
```

## Password Hashing

Uses Argon2 via passlib:

```python
# backend/app/core/security.py
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Hash
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Verify
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

## Authorization Header

Client must send:
```
Authorization: Bearer <JWT_TOKEN>
```

## Protected Endpoints

All `/api/documents/*` and `/api/chat/*` endpoints require valid JWT:
- `/api/documents`
- `/api/documents/{document_id}`
- `/api/chat/stream`

The `get_current_user` dependency validates the token and retrieves the user from the database.

## Token Validation Flow

1. Client sends `Authorization: Bearer <token>`
2. `get_current_user` extracts token (strips "Bearer ")
3. `decode_access_token` verifies JWT signature and expiration
4. Extracts `sub` (username) from payload
5. Queries SQLite `users` table for user
6. Returns user object to endpoint

## Frontend Token Storage

```javascript
// frontend/api.js

API.setToken(token)   // localStorage.setItem('accessToken', token)
API.getToken()       // localStorage.getItem('accessToken')
API.clearToken()     // localStorage.removeItem('accessToken')
```

## Expiration Handling

- Tokens expire after 60 minutes
- Client must re-login when token expires
- No refresh token mechanism (simplified for this project)

## Security Considerations

1. **HTTPS**: In production, always use HTTPS
2. **Secret Key**: Set via `SECRET_KEY` environment variable
3. **CORS**: Currently allows all origins (`allow_origins=["*"]`) - restrict in production
4. **Password Requirements**: Minimum 6 characters enforced by Pydantic
