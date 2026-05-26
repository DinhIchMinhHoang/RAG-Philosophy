# Deployment

## Docker Compose Stack

Run full stack with a single command:

```bash
docker compose up -d
```

`docker-compose up -d` is equivalent if your environment still uses the legacy CLI name.

Services in the stack:

1. `nginx` (public entrypoint on `http://localhost`)
2. `backend` (FastAPI via Uvicorn)
3. `worker` (Celery ingest queue)
4. `embedding` / `rag_embedding` (SentenceTransformer HTTP service)
5. `redis`
6. `postgres`
7. `minio`
8. `qdrant`

Notes:

- Browser/API access is Nginx-only (`http://localhost`).
- Use `/api/*` from frontend/client calls.
- Backend container is not published directly to host.
- Backend and worker call the internal embedding service at `EMBEDDING_SERVICE_URL=http://embedding:8000`.
- The embedding service is additionally bound to `127.0.0.1:8001` for local smoke checks and local backend development; browsers should not call it directly.
- Ollama is optional and is not started by the default stack. Enable it with the `local-llm` profile only on machines with enough memory.

## First Boot

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```
2. Set required secrets/keys in `.env` (at minimum `SECRET_KEY`, `GEMINI_API_KEY`).
3. Start stack:
   ```bash
   docker compose up -d
   ```
4. Open app at `http://localhost`.

## VM Stack: 2vCPU / 8GB

Use the VM compose file on small cloud VMs:

```bash
cp .env.vm .env
docker compose -f docker-compose.vm.yml up -d
```

The VM stack keeps the same external contract (`http://localhost` through Nginx)
but uses prebuilt GHCR images and lower resource limits. It runs:

1. `nginx`
2. `backend`
3. `worker`
4. `embedding`
5. `redis`
6. `postgres`
7. `minio`
8. `qdrant`

It intentionally does not run `ollama`; use cloud LLM/OCR settings from `.env`.
Ingest is handled by the dedicated Celery worker with concurrency `1`, while
backend chat/API calls the dedicated embedding service at
`EMBEDDING_SERVICE_URL=http://embedding:8000`.

## Cold Start Checks

1. Check container health:
   ```bash
   docker compose ps
   ```
2. Confirm API through Nginx:
   ```bash
   curl http://localhost/api/login -X POST -H "Content-Type: application/json" -d "{\"email\":\"x@gmail.com\",\"password\":\"x\"}"
   ```
3. Confirm backend docs through proxy:
   ```bash
   curl -I http://localhost/api/docs
   ```
4. Confirm embedding service is healthy inside the Compose network:
   ```bash
   docker compose exec embedding python -c "import json,urllib.request; print(json.load(urllib.request.urlopen('http://localhost:8000/info')))"
   ```

## Streaming (SSE) Validation

Nginx is configured for streaming-safe proxying on `/api/chat/stream`:

- `proxy_http_version 1.1`
- `proxy_buffering off`
- extended `proxy_read_timeout` and `proxy_send_timeout`

Test endpoint:

```bash
curl -N http://localhost/api/chat/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d "{\"message\":\"hello\"}"
```

## Optional Local LLM / GPU Acceleration

The default Compose stack starts the embedding service on CPU and does not start Ollama, so CPU-only hosts can boot the app normally. OCR uses the configured `OCR_*` API settings from `.env`.

To start the optional local Ollama fallback:

```bash
docker compose --profile local-llm up -d
```

On hosts with an Nvidia runtime, enable GPU acceleration for embedding and optional Ollama with the override file:

```bash
docker compose --profile local-llm -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

## Restart / Persistence Test

1. Upload at least one document and run ingest.
2. Restart stack:
   ```bash
   docker compose down
   docker compose up -d
   ```
3. Verify data still exists:
   - Postgres data (`postgres_data` volume)
  - MinIO objects (`minio_data` volume)
  - Qdrant vectors (`qdrant_data` volume)
  - HuggingFace model cache (`huggingface_cache` volume)
  - Ollama models (`ollama_data` volume, only when `--profile local-llm` is used)

## Local SQLite Artifacts

Docker deployments use Postgres through `DATABASE_URL`; local SQLite files such as `rag_system.db` are runtime artifacts and are ignored by Git. Do not commit generated `.db` files. If a developer runs without Postgres, SQLAlchemy can recreate a local SQLite database from the ORM models, but existing local SQLite data should be backed up before deleting the file.

## Logs and Health Debugging

```bash
docker compose logs -f nginx
docker compose logs -f backend
docker compose logs -f worker
docker compose logs -f embedding
docker compose logs -f qdrant
```

For the VM stack, add the compose file flag:

```bash
docker compose -f docker-compose.vm.yml logs -f backend worker embedding
```

If one service is unhealthy, inspect healthcheck status:

```bash
docker inspect --format='{{json .State.Health}}' rag_backend
```

Expected embedding logs should show model load only in `rag_embedding`:

```bash
docker compose logs embedding | grep embedding_model_ready
docker compose logs backend worker | grep -E "SentenceTransformer|embedding_model_ready"
```

The second command should not show backend or worker loading the model locally.

## Lưu ý để OCR thực sự hoạt động (không chỉ fallback)

- Configure OCR API credentials in `.env`:

```bash
OCR_PROVIDER=zai
OCR_API_BASE_URL=https://api.z.ai/api/paas/v4/layout_parsing
OCR_API_KEY=<your-zai-api-key>
OCR_MODEL=glm-ocr
```

Backend and worker read these values through `env_file: .env`.
