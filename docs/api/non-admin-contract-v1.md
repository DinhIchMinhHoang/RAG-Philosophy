# Non-Admin API Contract (Freeze, Dual-Compat)

Base path behind Nginx: `/api/*` (canonical).
Legacy aliases have been removed.

## Canonical Endpoints

- `POST /api/signup`
- `POST /api/login`
- `POST /api/change-password`
- `POST /api/documents`
- `GET /api/documents`
- `DELETE /api/documents/{document_id}`
- `POST /api/documents/{document_id}/reindex`
- `GET /api/jobs/{job_id}`
- `POST /api/chat`
- `POST /api/chat/stream`

## Legacy Aliases (removed)

Legacy endpoints are no longer available.

## Auth

Protected endpoints require:

`Authorization: Bearer <access_token>`

## Chat Contract

### `POST /api/chat`

Request:

```json
{
  "message": "What is the key argument?",
  "conversation_id": "optional-existing-conversation-id",
  "notebook_id": 1
}
```

Only `message` is required. If `conversation_id` is omitted, the backend creates a new conversation for the authenticated user.

Response:

```json
{
  "answer": "...",
  "conversation_id": "uuid",
  "message_id": "uuid",
  "rewritten_query": "standalone retrieval query",
  "citations": [
    {
      "citation_id": "C1",
      "rank": 1,
      "source": "intro.pdf",
      "page": 12,
      "snippet": "...",
      "document_id": "uuid",
      "chunk_id": "uuid",
      "doc_id": "uuid",
      "score": 0.81
    }
  ]
}
```

Citation fields:

- required: `source`, `page`, `snippet`
- optional: `citation_id`, `rank`, `document_id`, `chunk_id`, `doc_id`, `score`

`citations` contains only sources whose `citation_id` appears inline in `answer`, such as `[C1]`. Retrieved-but-unused sources are not returned in the user-facing citation list.

When evidence is insufficient:

- `answer` is a safe fallback message
- `citations` is `[]`

### `POST /api/chat/stream` (SSE)

Token event:

```text
data: {"type":"token","token":"...","done":false}
```

Final event:

```text
data: {"type":"final","token":"","done":true,"answer":"...","citations":[...],"conversation_id":"uuid","message_id":"uuid","rewritten_query":"standalone retrieval query"}
```

Error event:

```text
data: {"type":"error","token":"","done":true,"error":"Failed to generate answer","citations":[]}
```

Compatibility note: `token` is always present for old clients.

## Documents Contract

### `POST /api/documents`

`multipart/form-data` with `file` (PDF).

Response:

```json
{
  "document_id": "uuid",
  "job_id": "uuid",
  "status": "queued",
  "pipeline_version": "1.0.0",
  "object_key": "uuid/file.pdf"
}
```

### `GET /api/documents`

Returns documents with latest job status for tracking ingest progress.

### `DELETE /api/documents/{document_id}`

Idempotent cleanup across metadata/chunks, vectors, and object storage.

### `GET /api/jobs/{job_id}`

Job enums are unchanged:

- status: `queued`, `running`, `succeeded`, `failed`
- stage: `fetching_object`, `parsing`, `chunking`, `embedding`, `indexing_vector`, `persisting_metadata`

Retry behavior:

- transient worker failures reuse the same job row
- Celery retry marks the job `queued` with `stage_detail=retrying_after_error: ...`
- the next `start_run` rewinds the same job to `running` at `fetching_object` with `progress_pct=0`
- terminal failures keep the same job and set `status=failed`, `stage_detail=ingest_failed`, and `error_message`

## Error Envelope

All JSON errors use:

```json
{
  "error": {
    "code": "http_400",
    "message": "...",
    "request_id": "...",
    "details": []
  },
  "detail": "..."
}
```

## Runtime Env Keys

- `PIPELINE_VERSION`
- `RETRIEVAL_MODE` (`dense|hybrid`)
- `RETRIEVAL_TOP_K`
- `LLM_MODE` (`auto|gemini|opencode|local`)
- `LLM_PROVIDER` (`auto|gemini|opencode`)
- `LLM_MODEL` (`gemini-*` uses Gemini when provider is auto; non-Gemini names use OpenCode)
- `LOCAL_LLM_BASE_URL`
- `LOCAL_LLM_MODEL`
- `QDRANT_URL` / (`QDRANT_HOST`, `QDRANT_PORT`, `QDRANT_COLLECTION`, `QDRANT_API_KEY`)
- `OBJECT_STORAGE_BACKEND`, `OBJECT_STORAGE_LOCAL_ROOT`
- `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_BUCKET`, `MINIO_SECURE`
- `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- `APP_ENV` (non-dev enforces non-weak `SECRET_KEY`)
