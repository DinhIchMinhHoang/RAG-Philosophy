# Database Architecture — RAG-Philosophy

**Document Version:** 1.0  
**Last Updated:** 2026-05-27  
**Status:** Active

---

## Table of Contents

1. [Overview](#1-overview)
2. [PostgreSQL Schema](#2-postgresql-schema)
   - 2.1 Entity-Relationship Diagram
   - 2.2 Table Reference
   - 2.3 Enums and Constraints
3. [Qdrant Vector Store](#3-qdrant-vector-store)
   - 3.1 Collection Configuration
   - 3.2 Payload Schema
   - 3.3 Payload Indexes
   - 3.4 Point ID Determinism
4. [Schema Management](#4-schema-management)
   - 4.1 Automatic Schema Creation
   - 4.2 Runtime Schema Migrations
   - 4.3 Why No Alembic
5. [Connection and Session Management](#5-connection-and-session-management)
   - 5.1 Engine Configuration
   - 5.2 Session Factory
   - 5.3 FastAPI Dependency Injection
6. [Appendices](#6-appendices)
   - A: SQL DDL Equivalent

---

## 1. Overview

The application uses a dual-database architecture:

| Database | Technology | Purpose | Host |
|----------|-----------|---------|------|
| **Relational** | PostgreSQL 16 | Users, documents, notebooks, conversations, chat messages, jobs, metadata | `rag_postgres` container |
| **Vector** | Qdrant v1.13.4 | Dense vector embeddings with payload filtering for semantic retrieval | `rag_qdrant` container |

**Separation of concerns:** The relational database handles transactional data, access control, and job tracking. Qdrant handles similarity search with payload-based pre-filtering. The two are never directly joined; the application layer correlates data by `document_id`, `owner_id`, and `notebook_id`.

---

## 2. PostgreSQL Schema

**File:** `backend/app/models.py` — SQLAlchemy 2.0 declarative models  
**Base:** `sqlalchemy.orm.declarative_base()`

### 2.1 Entity-Relationship Diagram

```mermaid
erDiagram
    users ||--o{ notebooks : owns
    users ||--o{ documents : owns
    users ||--o{ conversations : owns
    users ||--o{ saved_notebook_items : owns
    notebooks ||--o{ documents : contains
    notebooks ||--o{ conversations : belongs-to
    notebooks ||--o{ saved_notebook_items : has
    conversations ||--o{ chat_messages : contains

    users {
        int id PK
        varchar username UK
        varchar email UK
        varchar hashed_password
    }

    notebooks {
        int id PK
        varchar title
        int owner_id FK
        int is_community
        varchar cover_url
        varchar cover_mode
        varchar cover_color
        datetime created_at
    }

    documents {
        varchar id PK "uuid4"
        int owner_id FK
        int notebook_id FK
        varchar filename
        varchar object_key UK
        varchar mime_type
        int size_bytes
        varchar content_hash
        datetime delete_requested_at
        datetime deleted_at
        datetime created_at
        datetime updated_at
    }

    conversations {
        varchar id PK "uuid4"
        int owner_id FK
        int notebook_id FK
        datetime created_at
        datetime updated_at
        datetime archived_at
    }

    chat_messages {
        varchar id PK "uuid4"
        varchar conversation_id FK
        varchar role
        text content
        json sources_used
        text rewritten_query
        datetime created_at
    }

    saved_notebook_items {
        varchar id PK "uuid4"
        int owner_id FK
        int notebook_id FK
        varchar conversation_id FK
        varchar message_id FK
        varchar kind "note|pin|conversation|summary"
        varchar title
        text content
        json sources_used
        datetime created_at
    }

    password_reset_codes {
        varchar id PK "uuid4"
        varchar email
        varchar verification_code
        datetime expires_at
        datetime created_at
    }
```

**Figure 1: Entity-relationship diagram — User workspace.**

```mermaid
erDiagram
    documents ||--o{ document_chunks : chunks
    documents ||--o{ ingest_jobs : tracked-by
    documents ||--o{ excel_table_records : has

    documents {
        varchar id PK "uuid4"
    }

    document_chunks {
        varchar id PK "uuid4"
        varchar document_id FK
        int owner_id FK
        int notebook_id FK
        varchar job_id FK
        varchar kind "parent|child"
        varchar parent_chunk_id
        int chunk_order
        text text
        varchar source
        int page
        varchar doc_id
        varchar pipeline_version
        datetime created_at
    }

    ingest_jobs {
        varchar id PK "uuid4"
        varchar document_id FK
        varchar status "enum"
        varchar stage "enum"
        int progress_pct
        varchar stage_detail
        text error_message
        varchar pipeline_version
        varchar celery_task_id
        datetime created_at
        datetime queued_at
        datetime started_at
        datetime finished_at
        datetime updated_at
    }

    excel_table_records {
        varchar id PK "uuid4"
        varchar document_id FK
        varchar user_id
        varchar table_name UK
        varchar sheet_name
        text column_schema
        text sample_data
        int row_count
        datetime created_at
    }
```

**Figure 2: Entity-relationship diagram — Document pipeline.**

### 2.2 Table Reference

#### `users`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `int` | PK, auto-increment | Surrogate key |
| `username` | `varchar` | NOT NULL, UNIQUE, INDEX | Display name |
| `email` | `varchar` | NOT NULL, UNIQUE, INDEX | Login identifier; only @gmail.com and @lumina.com.vn allowed |
| `hashed_password` | `varchar` | NOT NULL | Argon2 hash via passlib |

Relationships: `conversations` (cascade delete), foreign keys from `documents`, `document_chunks`, `saved_notebook_items`.

#### `notebooks`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `int` | PK, auto-increment, INDEX | Surrogate key |
| `title` | `varchar(256)` | NOT NULL | User-facing name |
| `owner_id` | `int` | NOT NULL, FK → users.id, INDEX | Creator/owner |
| `is_community` | `int` | NOT NULL, default 0 | Boolean flag (0=private, 1=community) |
| `cover_url` | `varchar(1024)` | NULLABLE | Cover image URL (for dashboard) |
| `cover_mode` | `varchar(32)` | NULLABLE | CSS background-size mode |
| `cover_color` | `varchar(32)` | NULLABLE | Solid color fallback |
| `created_at` | `datetime(tz)` | NOT NULL, server_default=now() | Timestamp |

#### `documents`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `varchar(64)` | PK | UUID4 hex string |
| `owner_id` | `int` | NULLABLE, FK → users.id (SET NULL), INDEX | Null on user deletion |
| `notebook_id` | `int` | NULLABLE, FK → notebooks.id (SET NULL), INDEX | Null on notebook deletion |
| `filename` | `varchar(512)` | NOT NULL | Original upload filename |
| `object_key` | `varchar(1024)` | NOT NULL, UNIQUE | Storage path (UUID/filename) |
| `mime_type` | `varchar(128)` | NOT NULL | e.g., application/pdf |
| `size_bytes` | `int` | NOT NULL | File size |
| `content_hash` | `varchar(64)` | NULLABLE, INDEX | SHA-256 for dedup |
| `delete_requested_at` | `datetime(tz)` | NULLABLE, INDEX | Soft-delete request timestamp |
| `deleted_at` | `datetime(tz)` | NULLABLE, INDEX | Actual deletion timestamp |
| `created_at` | `datetime(tz)` | NOT NULL | Upload time |
| `updated_at` | `datetime(tz)` | NOT NULL, onupdate=now() | Last modification |

Relationships: `ingest_jobs` (cascade delete), `document_chunks` (cascade delete).

#### `ingest_jobs`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `varchar(64)` | PK | UUID4 hex string |
| `document_id` | `varchar(64)` | NOT NULL, FK → documents.id (CASCADE), INDEX | Owning document |
| `status` | `varchar(32)` | NOT NULL, default 'queued' | `queued`, `running`, `succeeded`, `failed`, `cancelled` |
| `stage` | `varchar(64)` | NOT NULL, default 'fetching_object' | Pipeline stage enum |
| `progress_pct` | `int` | NOT NULL, default 0 | 0–100 |
| `stage_detail` | `varchar(512)` | NULLABLE | Human-readable stage info |
| `error_message` | `text` | NULLABLE | Failure reason |
| `pipeline_version` | `varchar(64)` | NOT NULL | Version tag for reproducibility |
| `celery_task_id` | `varchar(128)` | NULLABLE, INDEX | Celery task tracking |
| `created_at` | `datetime(tz)` | NOT NULL | Record creation |
| `queued_at` | `datetime(tz)` | NULLABLE | Enqueue time |
| `started_at` | `datetime(tz)` | NULLABLE | Processing start |
| `finished_at` | `datetime(tz)` | NULLABLE | Completion time |
| `updated_at` | `datetime(tz)` | NOT NULL, onupdate=now() | Last update |

#### `document_chunks`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `varchar(64)` | PK | UUID4 hex string |
| `document_id` | `varchar(64)` | NOT NULL, FK → documents.id (CASCADE), INDEX | Owning document |
| `owner_id` | `int` | NULLABLE, FK → users.id (SET NULL), INDEX | Denormalized for access control |
| `notebook_id` | `int` | NULLABLE, FK → notebooks.id (SET NULL), INDEX | Denormalized for access control |
| `job_id` | `varchar(64)` | NULLABLE, FK → ingest_jobs.id (SET NULL), INDEX | Creating job |
| `kind` | `varchar(16)` | NOT NULL, INDEX | `parent` or `child` |
| `parent_chunk_id` | `varchar(64)` | NULLABLE, INDEX | Link child → parent for retrieval |
| `chunk_order` | `int` | NOT NULL | Position within parent |
| `text` | `text` | NOT NULL | Chunk content |
| `source` | `varchar(512)` | NOT NULL | Filename |
| `page` | `int` | NOT NULL | Source page number |
| `doc_id` | `varchar(64)` | NOT NULL, INDEX | Deterministic UUID5 for Qdrant sync |
| `pipeline_version` | `varchar(64)` | NOT NULL, INDEX | Enables versioned reindex |
| `created_at` | `datetime(tz)` | NOT NULL | Insertion time |

**Chunking strategy:**
- `kind="parent"` — a coarse chunk (~512 tokens) stored in PostgreSQL for display
- `kind="child"` — a finer sub-chunk stored in BOTH PostgreSQL AND Qdrant
- Retrieval searches child vectors, groups by `parent_chunk_id`, then returns parent-level contexts

#### `conversations`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `varchar(64)` | PK | UUID4 hex string |
| `owner_id` | `int` | NOT NULL, FK → users.id (CASCADE), INDEX | Conversation owner |
| `notebook_id` | `int` | NULLABLE, FK → notebooks.id (SET NULL), INDEX | Scoped to notebook |
| `created_at` | `datetime(tz)` | NOT NULL | Creation time |
| `updated_at` | `datetime(tz)` | NOT NULL, onupdate=now() | Last message time |
| `archived_at` | `datetime(tz)` | NULLABLE, INDEX | Hidden from dashboard |

#### `chat_messages`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `varchar(64)` | PK | UUID4 hex string |
| `conversation_id` | `varchar(64)` | NOT NULL, FK → conversations.id (CASCADE), INDEX | Parent conversation |
| `role` | `varchar(16)` | NOT NULL, INDEX | `user` or `assistant` |
| `content` | `text` | NOT NULL | Message text |
| `sources_used` | `json` | NULLABLE | Citation metadata array |
| `rewritten_query` | `text` | NULLABLE | LLM-rewritten retrieval query |
| `created_at` | `datetime(tz)` | NOT NULL | Message timestamp |

#### `saved_notebook_items`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `varchar(64)` | PK | UUID4 hex string |
| `owner_id` | `int` | NOT NULL, FK → users.id (CASCADE), INDEX | Owner |
| `notebook_id` | `int` | NOT NULL, FK → notebooks.id (CASCADE), INDEX | Parent notebook |
| `conversation_id` | `varchar(64)` | NULLABLE, FK → conversations.id (SET NULL), INDEX | Source conversation |
| `message_id` | `varchar(64)` | NULLABLE, FK → chat_messages.id (SET NULL), INDEX | Source message |
| `kind` | `varchar(32)` | NOT NULL, INDEX | `note`, `pin`, `conversation`, `summary` |
| `title` | `varchar(256)` | NULLABLE | Item title |
| `content` | `text` | NOT NULL | Saved content |
| `sources_used` | `json` | NULLABLE | Citation metadata |
| `created_at` | `datetime(tz)` | NOT NULL | Save time |

#### `excel_table_records`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `varchar(64)` | PK | UUID4 hex string |
| `document_id` | `varchar(64)` | NOT NULL, FK → documents.id (CASCADE), INDEX | Owning spreadsheet |
| `user_id` | `varchar(256)` | NOT NULL, INDEX | Owner identifier |
| `table_name` | `varchar(256)` | NOT NULL, UNIQUE | Auto-generated name |
| `sheet_name` | `varchar(256)` | NOT NULL | Source sheet |
| `column_schema` | `text` | NOT NULL | JSON column profile |
| `sample_data` | `text` | NULLABLE | Representative rows |
| `row_count` | `int` | NOT NULL, default 0 | Total rows |
| `created_at` | `datetime(tz)` | NOT NULL | Insertion time |

Additional constraint: `UNIQUE(user_id, document_id, table_name)`

#### `password_reset_codes`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `varchar(64)` | PK | UUID4 hex string |
| `email` | `varchar(256)` | NOT NULL, INDEX | Target email |
| `verification_code` | `varchar(32)` | NOT NULL | 4-digit numeric code |
| `expires_at` | `datetime(tz)` | NOT NULL | 15-minute TTL |
| `created_at` | `datetime(tz)` | NOT NULL | Issue time |

### 2.3 Enums and Constraints

**JobStatus enum (string-based in Python):**
```python
class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

**JobStage enum (string-based in Python):**
```python
class JobStage(str, enum.Enum):
    FETCHING_OBJECT = "fetching_object"
    PARSING = "parsing"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING_VECTOR = "indexing_vector"
    PERSISTING_METADATA = "persisting_metadata"
    LOADING_SQL = "loading_sql"
```

**Unique constraints:**
- `users.username` — unique index
- `users.email` — unique index
- `documents.object_key` — unique
- `excel_table_records.table_name` — unique
- `excel_table_records`: `UNIQUE(user_id, document_id, table_name)`

**Soft-delete pattern** (documents table):
- `delete_requested_at` — set when user requests deletion; allows cancellation
- `deleted_at` — set when the async cleanup completes
- Documents with `deleted_at IS NOT NULL` are filtered from all queries

---

## 3. Qdrant Vector Store

**File:** `backend/app/ingest/qdrant_store.py`

Qdrant stores child-level chunk vectors for dense retrieval. Each point in the collection maps to a `document_chunks` row with `kind="child"`.

### 3.1 Collection Configuration

| Parameter | Value | Notes |
|-----------|-------|-------|
| Collection name | `rag_philosophy` | Configurable via `QDRANT_COLLECTION` |
| Vector size | 640 | Float32, determined by embedding model |
| Distance metric | `Cosine` | Range [-1, 1] |
| Point ID | UUID5 | Deterministic for idempotent upserts |

```python
from qdrant_client.http import models as rest

def ensure_collection(client, vector_size: int):
    collections = client.get_collections().collections
    names = {c.name for c in collections}

    if COLLECTION not in names:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=rest.VectorParams(
                size=vector_size,
                distance=rest.Distance.COSINE,
            ),
        )
```

### 3.2 Payload Schema

Each point carries the following payload fields for filtering and post-retrieval processing:

```python
def build_qdrant_payload(chunk: DocumentChunk) -> dict:
    return {
        "document_id": chunk.document_id,
        "owner_id": chunk.owner_id,
        "notebook_id": chunk.notebook_id,
        "doc_id": chunk.doc_id,
        "parent_chunk_id": chunk.parent_chunk_id,
        "source": chunk.source,
        "page": chunk.page,
        "pipeline_version": chunk.pipeline_version,
        "chunk_id": chunk.id,
        "kind": chunk.kind,
        "text": chunk.text,
    }
```

**Payload field reference:**

| Field | Type | Purpose | Query Use |
|-------|------|---------|-----------|
| `document_id` | `str` | Links to PostgreSQL `documents.id` | Filter by document |
| `owner_id` | `int or null` | Access control | Filter by owner |
| `notebook_id` | `int or null` | Access control | Filter by notebook |
| `doc_id` | `str` | Deterministic UUID5 for dedup | Group by doc |
| `parent_chunk_id` | `str or null` | Groups child hits to parent for dedup | Post-filter |
| `source` | `str` | Filename for citation | Display |
| `page` | `int` | Page number for citation | Display |
| `pipeline_version` | `str` | Version tag for reindex | Filter by version |
| `chunk_id` | `str` | UUID4 from PostgreSQL | Point-source link |
| `kind` | `str` | Always `"child"` | Filter by type |
| `text` | `str` | Chunk plaintext | Snippet extraction |

### 3.3 Payload Indexes

Payload indexes are created on fields used in `must` filters during retrieval:

```python
index_specs = {
    "document_id": rest.PayloadSchemaType.KEYWORD,
    "owner_id": rest.PayloadSchemaType.INTEGER,
    "notebook_id": rest.PayloadSchemaType.INTEGER,
    "pipeline_version": rest.PayloadSchemaType.KEYWORD,
    "kind": rest.PayloadSchemaType.KEYWORD,
}
```

### 3.4 Point ID Determinism

Point IDs are generated deterministically to support idempotent upserts:

```python
def deterministic_point_id(document_id: str, pipeline_version: str, chunk_id: str) -> str:
    return str(uuid.uuid5(
        uuid.NAMESPACE_URL,
        f"{document_id}:{pipeline_version}:{chunk_id}",
    ))
```

This means:
- Re-running the same ingest job replaces (does not duplicate) existing points
- Reindexing with the same pipeline_version overwrites vectors without ghost data
- Different pipeline_version values create separate point sets (may coexist for A/B testing)

### 3.5 Key Functions

| Function | Signature | Purpose |
|----------|-----------|---------|
| `build_qdrant_client()` | `() -> QdrantClient` | Creates cached client from settings |
| `ensure_collection(client, vector_size)` | `(QdrantClient, int) -> None` | Creates collection if missing |
| `validate_collection_vector_size(client, vector_size)` | `(QdrantClient, int) -> bool` | Checks existing collection dimension |
| `deterministic_point_id(...)` | `(str, str, str) -> str` | UUID5 point ID |
| `build_qdrant_payload(chunk)` | `(DocumentChunk) -> dict` | Payload builder |
| `upsert_child_vectors(client, chunks, vectors)` | `(QdrantClient, list, list) -> None` | Batch upsert |
| `delete_vectors_for_document(client, document_id)` | `(QdrantClient, str) -> None` | Full cleanup |
| `delete_vectors_for_document_version(client, document_id, pipeline_version)` | `(QdrantClient, str, str) -> None` | Versioned cleanup |

---

## 4. Schema Management

### 4.1 Automatic Schema Creation

On application startup, all tables are created automatically:

```python
# backend/app/main.py
models.Base.metadata.create_all(bind=engine)
```

`Base.metadata.create_all()` is idempotent — it checks for existing tables and only creates missing ones. This is safe for repeated application restarts.

### 4.2 Runtime Schema Migrations

A `ensure_runtime_schema()` function handles additive column changes for local deployments:

```python
def ensure_runtime_schema(engine: Engine) -> None:
    """Apply small additive schema updates without Alembic."""
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    required_columns = {
        "documents": {
            "owner_id": "INTEGER",
            "notebook_id": "INTEGER",
            "content_hash": "VARCHAR(64)",
            "delete_requested_at": "TIMESTAMP",
            "deleted_at": "TIMESTAMP",
        },
        "ingest_jobs": {
            "celery_task_id": "VARCHAR(128)",
        },
        "document_chunks": {
            "owner_id": "INTEGER",
            "notebook_id": "INTEGER",
        },
        "conversations": {
            "archived_at": "TIMESTAMP",
        },
        "excel_table_records": {
            "sample_data": "TEXT",
        },
    }

    for table, columns in required_columns.items():
        if table not in table_names:
            continue
        existing = {c["name"] for c in inspector.get_columns(table)}
        for col, col_type in columns.items():
            if col not in existing:
                with engine.begin() as conn:
                    conn.execute(text(
                        f'ALTER TABLE "{table}" ADD COLUMN {col} {col_type}'
                    ))
```

This handles the case where a table was created by an older version of the code and needs additional columns. It never drops or alters existing columns.

### 4.3 Why No Alembic

The project intentionally does not use Alembic for migrations because:

1. **Single deployment** — only one production database exists; no multi-environment migration coordination
2. **Additive-only changes** — all schema modifications are backward-compatible column additions
3. **Code-is-schema** — `create_all()` ensures the schema always matches the model definitions on fresh deployments
4. **Minimal surface area** — the schema has 10 tables with stable relationships; breaking changes are rare

This approach works because the project uses String UUIDs for all primary keys (no auto-increment dependencies) and nullable foreign keys with `SET NULL` on delete (reducing cascade complexity).

---

## 5. Connection and Session Management

### 5.1 Engine Configuration

```python
# backend/app/database.py
def _build_engine():
    connect_args = {}
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(settings.database_url, connect_args=connect_args)

engine = _build_engine()
```

The engine uses the `DATABASE_URL` from settings, which defaults to `sqlite:///./rag_system.db` for local development and `postgresql+psycopg2://postgres:postgres@postgres:5432/rag_db` for production.

### 5.2 Session Factory

```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

Standard SQLAlchemy sessionmaker with:
- `autocommit=False` — explicit `db.commit()` required
- `autoflush=False` — no automatic flush before queries (avoids unexpected writes)

### 5.3 FastAPI Dependency Injection

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

All routers use `db: Session = Depends(get_db)` to obtain a fresh session per request. The session is automatically closed when the request finishes.

---

## 6. Appendices

### A: SQL DDL Equivalent

While the project uses SQLAlchemy ORM (no raw DDL scripts), the equivalent SQL for the current schema is:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL UNIQUE,
    email VARCHAR NOT NULL UNIQUE,
    hashed_password VARCHAR NOT NULL
);
CREATE INDEX ix_users_email ON users (email);
CREATE INDEX ix_users_username ON users (username);

CREATE TABLE notebooks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_community INTEGER NOT NULL DEFAULT 0,
    cover_url VARCHAR(1024),
    cover_mode VARCHAR(32),
    cover_color VARCHAR(32),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_notebooks_id ON notebooks (id);
CREATE INDEX ix_notebooks_owner_id ON notebooks (owner_id);

CREATE TABLE documents (
    id VARCHAR(64) PRIMARY KEY,
    owner_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    notebook_id INTEGER REFERENCES notebooks(id) ON DELETE SET NULL,
    filename VARCHAR(512) NOT NULL,
    object_key VARCHAR(1024) NOT NULL UNIQUE,
    mime_type VARCHAR(128) NOT NULL,
    size_bytes INTEGER NOT NULL,
    content_hash VARCHAR(64),
    delete_requested_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_documents_owner_id ON documents (owner_id);
CREATE INDEX ix_documents_notebook_id ON documents (notebook_id);
CREATE INDEX ix_documents_content_hash ON documents (content_hash);
CREATE INDEX ix_documents_delete_requested_at ON documents (delete_requested_at);
CREATE INDEX ix_documents_deleted_at ON documents (deleted_at);

CREATE TABLE ingest_jobs (
    id VARCHAR(64) PRIMARY KEY,
    document_id VARCHAR(64) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    status VARCHAR(32) NOT NULL DEFAULT 'queued',
    stage VARCHAR(64) NOT NULL DEFAULT 'fetching_object',
    progress_pct INTEGER NOT NULL DEFAULT 0,
    stage_detail VARCHAR(512),
    error_message TEXT,
    pipeline_version VARCHAR(64) NOT NULL,
    celery_task_id VARCHAR(128),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    queued_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    finished_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_ingest_jobs_document_id ON ingest_jobs (document_id);
CREATE INDEX ix_ingest_jobs_celery_task_id ON ingest_jobs (celery_task_id);

CREATE TABLE document_chunks (
    id VARCHAR(64) PRIMARY KEY,
    document_id VARCHAR(64) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    owner_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    notebook_id INTEGER REFERENCES notebooks(id) ON DELETE SET NULL,
    job_id VARCHAR(64) REFERENCES ingest_jobs(id) ON DELETE SET NULL,
    kind VARCHAR(16) NOT NULL,
    parent_chunk_id VARCHAR(64),
    chunk_order INTEGER NOT NULL,
    text TEXT NOT NULL,
    source VARCHAR(512) NOT NULL,
    page INTEGER NOT NULL,
    doc_id VARCHAR(64) NOT NULL,
    pipeline_version VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_document_chunks_document_id ON document_chunks (document_id);
CREATE INDEX ix_document_chunks_owner_id ON document_chunks (owner_id);
CREATE INDEX ix_document_chunks_notebook_id ON document_chunks (notebook_id);
CREATE INDEX ix_document_chunks_job_id ON document_chunks (job_id);
CREATE INDEX ix_document_chunks_kind ON document_chunks (kind);
CREATE INDEX ix_document_chunks_parent_chunk_id ON document_chunks (parent_chunk_id);
CREATE INDEX ix_document_chunks_doc_id ON document_chunks (doc_id);
CREATE INDEX ix_document_chunks_pipeline_version ON document_chunks (pipeline_version);

CREATE TABLE conversations (
    id VARCHAR(64) PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notebook_id INTEGER REFERENCES notebooks(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    archived_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX ix_conversations_owner_id ON conversations (owner_id);
CREATE INDEX ix_conversations_notebook_id ON conversations (notebook_id);
CREATE INDEX ix_conversations_archived_at ON conversations (archived_at);

CREATE TABLE chat_messages (
    id VARCHAR(64) PRIMARY KEY,
    conversation_id VARCHAR(64) NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(16) NOT NULL,
    content TEXT NOT NULL,
    sources_used JSON,
    rewritten_query TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_chat_messages_conversation_id ON chat_messages (conversation_id);
CREATE INDEX ix_chat_messages_role ON chat_messages (role);

CREATE TABLE saved_notebook_items (
    id VARCHAR(64) PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notebook_id INTEGER NOT NULL REFERENCES notebooks(id) ON DELETE CASCADE,
    conversation_id VARCHAR(64) REFERENCES conversations(id) ON DELETE SET NULL,
    message_id VARCHAR(64) REFERENCES chat_messages(id) ON DELETE SET NULL,
    kind VARCHAR(32) NOT NULL,
    title VARCHAR(256),
    content TEXT NOT NULL,
    sources_used JSON,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_saved_notebook_items_owner_id ON saved_notebook_items (owner_id);
CREATE INDEX ix_saved_notebook_items_notebook_id ON saved_notebook_items (notebook_id);
CREATE INDEX ix_saved_notebook_items_conversation_id ON saved_notebook_items (conversation_id);
CREATE INDEX ix_saved_notebook_items_message_id ON saved_notebook_items (message_id);
CREATE INDEX ix_saved_notebook_items_kind ON saved_notebook_items (kind);

CREATE TABLE excel_table_records (
    id VARCHAR(64) PRIMARY KEY,
    document_id VARCHAR(64) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id VARCHAR(256) NOT NULL,
    table_name VARCHAR(256) NOT NULL UNIQUE,
    sheet_name VARCHAR(256) NOT NULL,
    column_schema TEXT NOT NULL,
    sample_data TEXT,
    row_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, document_id, table_name)
);
CREATE INDEX ix_etl_doc_id ON excel_table_records (document_id);
CREATE INDEX ix_excel_table_records_user_id ON excel_table_records (user_id);

CREATE TABLE password_reset_codes (
    id VARCHAR(64) PRIMARY KEY,
    email VARCHAR(256) NOT NULL,
    verification_code VARCHAR(32) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_password_reset_codes_email ON password_reset_codes (email);
```

---

## References

| Reference | File |
|-----------|------|
| ORM models | `backend/app/models.py` |
| Database setup | `backend/app/database.py` |
| Settings | `backend/app/core/settings.py` |
| Qdrant store | `backend/app/ingest/qdrant_store.py` |
| Schema migration | `backend/app/main.py` (line 22-23) |
| Excel schema | `backend/app/services/excel_schema.py` |
