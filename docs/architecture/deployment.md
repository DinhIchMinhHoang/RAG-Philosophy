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
4. `redis`
5. `postgres`
6. `minio`
7. `qdrant`
8. `ollama`

Notes:

- Browser/API access is Nginx-only (`http://localhost`).
- Use `/api/*` from frontend/client calls.
- Backend container is not published directly to host.

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

## Streaming (SSE) Validation

Nginx is configured for streaming-safe proxying on `/api/chat/stream`:

- `proxy_http_version 1.1`
- `proxy_buffering off`
- extended `proxy_read_timeout` and `proxy_send_timeout`

Test endpoint:

```bash
curl -N http://localhost/api/chat/stream \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"hello\"}"
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
   - Ollama models (`ollama_data` volume)

## Logs and Health Debugging

```bash
docker compose logs -f nginx
docker compose logs -f backend
docker compose logs -f worker
docker compose logs -f qdrant
```

If one service is unhealthy, inspect healthcheck status:

```bash
docker inspect --format='{{json .State.Health}}' rag_backend
```

## Lưu ý để OCR thực sự hoạt động (không chỉ fallback)

- Pull model trong container ollama:

```bash
docker compose exec ollama ollama pull glm-ocr
```