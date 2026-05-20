# Contract & Admin Design (2026-05-12)

Summary
- Single-page OpenAPI-style contract for core auth + admin paths.
- Add `is_admin` flag to User model and require admin dependency for /api/admin/*.

API base: /api

Environment keys
- SECRET_KEY (required)
- ALGORITHM (default HS256)
- ACCESS_TOKEN_EXPIRE_MINUTES (default 60)
- DATABASE_URL or SQLite file path (development)

Endpoints (high level)

POST /api/signup
Request:
{
  "username": "alice",
  "email": "alice@gmail.com",
  "password": "secret123"
}
Response 201:
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}

POST /api/login
Request:
{
  "email": "alice@gmail.com",
  "password": "secret123"
}
Response 200: Token object

POST /api/change-password
Auth: Bearer token
Request:
{ "current_password": "old", "new_password": "newpass" }

Admin (protected) — all under /api/admin and require is_admin
GET /api/admin/users -> list users (UserOut)
POST /api/admin/users -> create user
DELETE /api/admin/users/{user_id} -> delete user

Schemas
- UserCreate: username, email, password
- UserLogin: email, password
- Token: access_token, token_type
- UserOut: id, username, email, is_admin

DB changes
- models.User: add is_admin: Boolean default False
- Note: If an existing SQLite DB file exists, either run a migration or recreate DB for dev.

Auth behavior
- Tokens continue to include only subject(username).
- get_current_user decodes token and fetches user record.
- require_admin dependency checks user.is_admin and raises 403 if false.

Error codes
- 401 Unauthorized: missing/invalid token, user not found
- 403 Forbidden: admin endpoints accessed by non-admin

Example curl flows
- Signup
curl -X POST http://localhost:8000/signup -H "Content-Type: application/json" -d '{"username":"alice","email":"alice@gmail.com","password":"secret123"}'

- Login
curl -X POST http://localhost:8000/login -H "Content-Type: application/json" -d '{"email":"alice@gmail.com","password":"secret123"}'

- Admin list users (requires admin token)
curl -H "Authorization: Bearer <ADMIN_TOKEN>" http://localhost:8000/api/admin/users

Testing notes
- Manual verification steps listed in the main plan.

Migration note
- Adding non-nullable column with default to SQLite can be tricky for existing files. For local dev, simplest is removing rag_system.db and letting the app recreate tables. If not acceptable, run an ALTER TABLE sequence or a small Python migration script.

Files changed
- backend/app/models.py (+is_admin)
- backend/app/schemas.py (+UserOut)
- backend/app/routers/auth.py (+require_admin)
- backend/app/routers/admin.py (new)
- backend/app/main.py (include admin router)
- docs/superpowers/specs/2026-05-12-contract-and-admin-design.md (this file)

End of spec. Please review and tell me if you'd like any adjustments before I run a quick smoke check.
