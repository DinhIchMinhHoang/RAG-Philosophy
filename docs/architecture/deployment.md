# Deployment

<<<<<<< HEAD
## Current Environment

### Development Setup

```bash
# 1. Install dependencies
python -m pip install -r requirements.txt

# 2. Create .env file
GEMINI_API_KEY=your_key_here
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=60

# 3. Start backend
uvicorn backend.app.main:app --reload --port 8000

# 4. Start frontend (static files)
# Use VS Code Live Server or any static file server
# Serve frontend/index.html
```

## Production Considerations

### Backend

1. **Change CORS**:
   ```python
   # backend/app/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend.com"],  # Restrict
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Set Secret Key**:
   ```bash
   export SECRET_KEY=$(openssl rand -hex 32)
   ```

3. **Use Persistent Qdrant**:
   ```python
   # rag_core/config.py
   QDRANT_LOCATION: str = "http://localhost:6333"  # Or file path
   ```

4. **Production Server**: Use gunicorn with workers
   ```bash
   gunicorn backend.app.main:app --workers 4 --bind 0.0.0.0:8000
   ```

### Frontend

1. **Build**: No build step needed (static files)
2. **Host**: Any static hosting (nginx, S3, Vercel)
3. **Update BASE_URL**: Change API.BASE_URL to production backend URL

### Ollama (for OCR)

- Requires Ollama running: `ollama serve`
- Model: glm-ocr
- Port: 11434 (default)

## Docker (Future)

No Docker configuration currently. Potential setup:

```dockerfile
# Dockerfile
FROM python:3.10
# ... install deps, copy files
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0"]
```
=======
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
  -H "Authorization: Bearer <access_token>" \
  -d "{\"message\":\"hello\"}"
```

## Optional GPU Acceleration

The default Compose stack starts Ollama without a required GPU reservation, so CPU-only hosts can boot the app normally.

On hosts with an Nvidia runtime, enable GPU acceleration with the override file:

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
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
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
