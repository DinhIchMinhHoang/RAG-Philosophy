# Continuous Integration and Deployment Pipeline — RAG-Philosophy

**Document Version:** 1.0  
**Last Updated:** 2026-05-27  
**Status:** Active

---

## Table of Contents

1. [Overview](#1-overview)
2. [CI Pipeline](#2-ci-pipeline)
   - 2.1 Python Tests Job
   - 2.2 Frontend Tests Job
   - 2.3 Integration Tests Job
   - 2.4 Docs-Only Skip Logic
3. [Deploy Pipeline](#3-deploy-pipeline)
   - 3.1 Image Build and Push
   - 3.2 CPU-Only Torch Optimization
   - 3.3 VM Deployment Script
   - 3.4 Health Check Suite
   - 3.5 Rollback Mechanism
4. [Container Architecture](#4-container-architecture)
   - 4.1 Production Topology
   - 4.2 Container Dependencies
   - 4.3 Resource Limits
   - 4.4 Volumes and Networks
   - 4.5 Development vs Production
5. [Security](#5-security)
6. [Appendices](#6-appendices)
   - A: Deploy Script
   - B: Image Tag Conventions

---

## 1. Overview

The CI/CD pipeline automates build, test, and deployment of the RAG-Philosophy application to a single Ubuntu 24.04 VM (2 vCPU, 8 GB RAM). It is hosted on GitHub Actions with two workflows: a CI workflow triggered on every push to `main` and every pull request, and a Deploy workflow triggered only when CI succeeds on `main`.

**Key design decisions:**

- **No GPU** — all inference runs on CPU; PyTorch is pre-installed from the CPU-only wheel index
- **Single VM** — 8 containers orchestrated via Docker Compose v1.29.2
- **GHCR-hosted images** — backend and embedding services are pre-built and pulled from GitHub Container Registry
- **Health-gated rollback** — three health checks must pass before the deploy is considered successful
- **Layer-cached builds** — `type=gha, mode=max` Buildx caching reduces rebuild time

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 40, 'rankSpacing': 70}}}%%
flowchart TB
    subgraph Developer["Developer"]
        PUSH[git push to main]
        PR[Pull Request]
    end

    subgraph CI["CI Pipeline<br/> "]
        PT["Python Tests<br/>3 suites, ~3 min"]
        FT["Frontend Tests<br/>npm test, ~2 min"]
        IT["Integration Tests<br/>real services, ~10 min"]
    end

    subgraph CD["Deploy Pipeline<br/> "]
        BUILD["Buildx Build + Push<br/>2 images, ~5 min"]
        SSH["SSH Deploy to VM<br/>pull + restart + checks"]
        HEALTH["3 Health Checks<br/>240s grace period"]
    end

    subgraph VM["Production VM<br/> "]
        COMPOSE["Docker Compose<br/>8 containers"]
    end

    PUSH --> PT
    PUSH --> FT
    PUSH --> IT
    PR --> PT
    PR --> FT
    PR --> IT
    PT --> BUILD
    FT --> BUILD
    IT --> BUILD
    BUILD --> SSH
    SSH --> HEALTH
    HEALTH -- "pass" --> COMPOSE
    HEALTH -- "fail" --> ROLLBACK["Rollback<br/>restore last-good state"]
```

**Figure 1: End-to-end CI/CD pipeline flow.**

---

## 2. CI Pipeline

**File:** `.github/workflows/ci.yml`  
**Trigger:** Push to `main`, any pull request  
**Permissions:** `contents: read`

Three job groups execute in parallel:

| Job | Runner | Dependencies | Timeout | Description |
|-----|--------|-------------|---------|-------------|
| `python-tests` | ubuntu-latest | python 3.11, pandoc | — | Compile + unit tests for rag_core, embedding_service, backend |
| `frontend-tests` | ubuntu-latest | node 20 | — | npm ci + npm test |
| `integration-tests` | ubuntu-latest | postgres, qdrant, redis | 20 min | End-to-end ingest + Qdrant point verification |

### 2.1 Python Tests Job

```mermaid
flowchart LR
    A[Checkout] --> B[Setup Python 3.11]
    B --> C[pip install -r requirements.txt]
    C --> D[Install pandoc]
    D --> E[compileall backend rag_core embedding_service]
    E --> F[unittest discover rag_core/tests]
    F --> G[unittest discover embedding_service/tests]
    G --> H[unittest discover backend/tests]
```

**Steps:**

1. **Checkout** — `actions/checkout@v4`
2. **Setup Python 3.11** — `actions/setup-python@v5` with pip cache
3. **Install dependencies** — `python -m pip install -r requirements.txt`
4. **Install pandoc** — required for DOCX to Markdown conversion
5. **Compile Python** — `python -m compileall backend rag_core embedding_service -q`
6. **RAG core tests** — semantic chunking, parsers, embeddings, pipeline
7. **Embedding service tests** — HTTP contract, model loading
8. **Backend tests** — chat runtime, ingestion, Qdrant payload, auth

### 2.2 Frontend Tests Job

1. **Checkout**
2. **Setup Node 20** — `actions/setup-node@v4` with npm cache (`frontend/package-lock.json`)
3. **`npm ci`** — clean install
4. **`npm test`** — frontend suite

### 2.3 Integration Tests Job

Real service containers are spun up via GitHub Actions `services`:

| Service | Image | Health Check | Port |
|---------|-------|-------------|------|
| postgres | `postgres:16-alpine` | `pg_isready -U postgres -d rag_db` | 5432 |
| qdrant | `qdrant/qdrant:v1.13.4` | (port exposure only) | 6333 |
| redis | `redis:7-alpine` | `redis-cli ping` | 6379 |

```mermaid
sequenceDiagram
    participant GH as GitHub Runner
    participant SV as Service Containers
    participant ES as Embedding Service
    participant API as Backend API
    participant CI as Test Script

    GH->>SV: Start postgres, qdrant, redis
    GH->>GH: pip install + pandoc
    GH->>ES: Start uvicorn (port 8001, MiniLM model)
    ES-->>GH: Wait up to 240s for health
    GH->>API: Start uvicorn (port 8000)
    API-->>GH: Wait up to 60s for /docs
    GH->>CI: Execute scripts/ci_integration_test.py
    CI->>CI: Generate 4 test fixtures (PDF, DOCX, HTML, MD)
    CI->>API: POST /signup -> JWT token
    CI->>API: POST /documents (each fixture)
    API-->>CI: Completed or queued status
    CI->>CI: Poll job completion (up to 180s)
    CI->>API: GET /jobs/{id} -> verify status=completed
    CI->>API: POST /login -> verify auth
    CI-->>SV: Query collection points count
    CI->>GH: Report pass/fail per fixture
```

**Configuration for integration tests:**
```bash
SYNC_INGEST_WHEN_QUEUE_IDLE=true
EMBEDDING_SERVICE_URL=http://localhost:8001
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag_db
OBJECT_STORAGE_BACKEND=local
BASE_URL=http://localhost:8000
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

**Model selection:** `sentence-transformers/paraphrase-MiniLM-L3-v2` (80 MB) replaces the production model (`microsoft/harrier-oss-v1-270m`, 600 MB) to reduce download time. The Hugging Face cache is persisted across runs with `actions/cache@v4`.

### 2.4 Docs-Only Skip Logic

Integration tests are skipped when changes are limited to non-functional files:

```bash
git diff --name-only HEAD~1 HEAD | while read f; do
  case "$f" in
    docs/*|README.md|*.md|frontend/*) ;;
    *) SKIP=false; break ;;
  esac
done
```

This saves ~10 minutes per CI run for documentation and frontend-only changes.

---

## 3. Deploy Pipeline

**File:** `.github/workflows/deploy.yml`  
**Trigger:** `workflow_run` on CI completion (success, main branch); `workflow_dispatch` (manual)  
**Permissions:** `contents: read`, `packages: write`

```yaml
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [main]

jobs:
  build-and-deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
```

### 3.1 Image Build and Push

Two Docker images are built and pushed to GHCR using `docker/build-push-action@v6`:

| Image | Dockerfile | GHCR Repository | Size |
|-------|-----------|-----------------|------|
| Backend | `docker/backend.Dockerfile` | `rag-philosophy-backend` | ~3.99 GB |
| Embedding | `docker/embedding.Dockerfile` | `rag-philosophy-embedding` | ~2.76 GB |

**Tagging convention:**
```yaml
tags: |
  ghcr.io/${{ steps.sha.outputs.owner }}/rag-philosophy-backend:sha-${{ steps.sha.outputs.short }}
  ghcr.io/${{ steps.sha.outputs.owner }}/rag-philosophy-backend:latest
```

**Buildx caching:**
```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- uses: docker/build-push-action@v6
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

The `mode=max` setting caches all layers including those from BuildKit's internal build.

**Commit SHA extraction:**
```yaml
- run: |
    SHA="${{ github.event.workflow_run.head_sha || github.sha }}"
    echo "full=${SHA}" >> $GITHUB_OUTPUT
    echo "short=${SHA::7}" >> $GITHUB_OUTPUT
    echo "owner=${GITHUB_REPOSITORY_OWNER,,}" >> $GITHUB_OUTPUT
```

The lowercase conversion (`,,`) is required because GHCR repository names are case-sensitive.

### 3.2 CPU-Only Torch Optimization

Both Dockerfiles pre-install CPU-only PyTorch from the official CPU wheel index before the main `pip install`. This prevents pip from resolving to the CUDA-enabled torch (6+ GB).

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends pandoc

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

RUN pip install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY backend /app/backend
COPY rag_core /app/rag_core
COPY data /app/data
```

**Embedding Dockerfile:**
```dockerfile
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV HF_HOME=/cache/huggingface TRANSFORMERS_CACHE=/cache/huggingface

RUN pip install --upgrade pip && pip install --index-url https://download.pytorch.org/whl/cpu torch>=2.0.0

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY embedding_service /app/embedding_service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

**Savings:** Image size reduced from 10.6 GB to 3.96 GB (backend), eliminating ~1.5 GB of CUDA runtime libraries.

### 3.3 VM Deployment Script

```mermaid
flowchart TD
    A[Start Deploy] --> B[Capture last-good state<br/>from .deploy_last_good files]
    B --> C[git pull --ff-only]
    C --> D[Set IMAGE_TAG env]
    D --> E[docker login ghcr.io with GHCR_PAT]
    E --> F[docker-compose pull - all 8 images]
    F --> G[docker-compose down]
    G --> H[docker system prune -af]
    H --> I[docker-compose up -d]
    I --> J[sleep 240 - embedding start_period]
    J --> K[Health Check 1: /api/docs via nginx]
    K --> L[Health Check 2: /api/openapi.json]
    L --> M[Health Check 3: Qdrant /collections]
    M --> N{All 3 OK?}
    N -->|Yes| O[Save sha-tag to .deploy_last_good]
    O --> P[Done]
    N -->|No| Q[git checkout last-good-commit]
    Q --> R[Set IMAGE_TAG = last-good-tag]
    R --> S[docker-compose down && up -d]
    S --> T[Exit 1]
```

**Figure 2: Deploy and rollback decision flow.**

### 3.4 Health Check Suite

Three checks run after a 240-second grace period. All must pass before the deploy is committed.

| Check | Endpoint | Timeout | What It Validates |
|-------|----------|---------|-------------------|
| 1/3 | `http://localhost/api/docs` — Swagger UI | 10s | Backend process is serving via nginx |
| 2/3 | `http://localhost/api/openapi.json` | 10s | Nginx proxy routes correctly to backend |
| 3/3 | `http://localhost:6333/collections` | 10s | Qdrant is accepting connections |

**Why 240s?** The embedding service has `start_period: 120s` in its Docker health check and needs to download the ~600 MB model on first start. With `depends_on: condition: service_healthy`, backend and worker will not start until embedding is healthy. Total time from `up -d` to backend responding can be 3–4 minutes.

### 3.5 Rollback Mechanism

```bash
# Captured at deploy start:
LAST_GOOD_TAG=$(cat .deploy_last_good 2>/dev/null || echo "")
LAST_GOOD_COMMIT=$(cat .deploy_last_good_commit 2>/dev/null || echo "")

if [ "$ROLLBACK" = "true" ]; then
    git checkout "$LAST_GOOD_COMMIT"
    export IMAGE_TAG="$LAST_GOOD_TAG"
    docker-compose -f docker-compose.vm.yml down
    docker-compose -f docker-compose.vm.yml up -d
fi
```

**State persistence:**

| File | Contents | Example |
|------|----------|---------|
| `.deploy_last_good` | GHCR image tag | `sha-abc1234` |
| `.deploy_last_good_commit` | Full commit SHA | `abc1234def5678...` |

These files are only overwritten after all three health checks pass. The rollback restores both the frontend code (via `git checkout`) and the backend image (via `IMAGE_TAG`).

**Caveat:** `git checkout` on the VM creates a detached HEAD state. Subsequent deploys must run `git checkout main` before `git pull --ff-only`.

---

## 4. Container Architecture

**File:** `docker-compose.vm.yml` (production) / `docker-compose.yml` (development)

### 4.1 Production Topology

```mermaid
graph LR
    subgraph app_layer["Application Layer"]
        BACKEND["backend<br/>uvicorn --workers 1<br/>768 MB, 0.6 CPU"] ~~~ WORKER["worker<br/>celery --concurrency 1<br/>1.25 GB, 0.7 CPU"] ~~~ NGINX["nginx<br/>nginx:1.27-alpine<br/>128 MB, 0.1 CPU"] ~~~ EMBEDDING["embedding<br/>uvicorn --workers 1<br/>2 GB, 0.7 CPU"]
    end

    subgraph data_layer["Data Layer"]
        POSTGRES["postgres<br/>postgres:16-alpine<br/>768 MB, 0.3 CPU"] ~~~ REDIS["redis<br/>redis:7-alpine<br/>256 MB, 0.15 CPU"] ~~~ MINIO["minio<br/>minio:RELEASE.2023-10<br/>256 MB, 0.15 CPU"] ~~~ QDRANT["qdrant<br/>qdrant/qdrant:v1.13.4<br/>1.5 GB, 0.4 CPU"]
    end

    INTERNET((Internet :80)) --- NGINX
    NGINX -.-> BACKEND

    BACKEND -->|HTTP| EMBEDDING
    WORKER -->|HTTP| EMBEDDING
    BACKEND -->|SQL| POSTGRES
    WORKER -->|SQL| POSTGRES
    BACKEND -->|Redis| REDIS
    WORKER -->|Celery| REDIS
    BACKEND -->|S3| MINIO
    WORKER -->|S3| MINIO
    BACKEND -->|REST| QDRANT
    WORKER -->|REST| QDRANT
```

**Figure 3: Container topology and inter-service communication.**

### 4.2 Container Dependencies

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 80, 'rankSpacing': 80}}}%%
flowchart LR
    REDIS[redis] -->|healthy| BACKEND[backend]
    REDIS[redis] -->|healthy| WORKER[worker]
    POSTGRES[postgres] --> BACKEND
    POSTGRES --> WORKER
    MINIO[minio] --> BACKEND
    MINIO --> WORKER
    QDRANT[qdrant] --> BACKEND
    QDRANT --> WORKER
    EMBEDDING[embedding] --> BACKEND
    EMBEDDING --> WORKER
    BACKEND --> NGINX[nginx]
```

All `depends_on` clauses use `condition: service_healthy` — Docker Compose v1 waits for each dependency's health check to pass before starting the dependent container. This yields deterministic startup order:

1. redis, postgres, minio, qdrant (5–20s start_period)
2. embedding (120s start_period — model download)
3. backend, worker (40–60s start_period)
4. nginx (10s start_period)

### 4.3 Resource Limits

| Container | CPU Limit | Memory Limit | Health Check Command | Start Period |
|-----------|-----------|-------------|---------------------|-------------|
| nginx | 0.1 | 128 MB | `wget http://127.0.0.1/` | 10s |
| backend | 0.6 | 768 MB | `python /docs` | 60s |
| worker | 0.7 | 1,280 MB | `python /proc/1/cmdline` | 40s |
| embedding | 0.7 | 2,048 MB | `python /health` | 120s |
| postgres | 0.3 | 768 MB | `pg_isready` | 10s |
| redis | 0.15 | 256 MB | `redis-cli ping` | 5s |
| minio | 0.15 | 256 MB | `curl /minio/health/live` | 20s |
| qdrant | 0.4 | 1,536 MB | `qdrant --help` | 20s |
| **Total** | **3.1** | **6,984 MB** | | |

### 4.4 Volumes and Networks

| Volume / Mount | Target | Purpose |
|---------------|--------|---------|
| `postgres_data` | `/var/lib/postgresql/data` | Persistent relational storage |
| `minio_data` | `/data` | S3-compatible object storage |
| `qdrant_data` | `/qdrant/storage` | Vector index persistence |
| `huggingface_cache` | `/cache/huggingface` | Embedding model weight cache |
| `./frontend:/usr/share/nginx/html:ro` | nginx | Static frontend files |
| `./data:/app/data` | backend, worker | Local object storage |
| `./.env:/app/.env:ro` | backend, worker | Runtime configuration |

**Network:** All containers share a single bridge network `app_net`. Host-exposed ports:

| Port | Container | Visibility |
|------|-----------|-----------|
| `80:80` | nginx | Public (internet-facing) |
| `127.0.0.1:5432` | postgres | Localhost only |
| `127.0.0.1:6379` | redis | Localhost only |
| `127.0.0.1:6333` | qdrant | Localhost only |
| `127.0.0.1:9000` | minio API | Localhost only |
| `127.0.0.1:9001` | minio console | Localhost only |

Backend port 8000 is **not** exposed to the host. All API traffic routes through nginx.

### 4.5 Development vs Production

| Aspect | Development (`docker-compose.yml`) | Production (`docker-compose.vm.yml`) |
|--------|-----------------------------------|--------------------------------------|
| Backend image | Build from source | Pull from GHCR |
| Code sync | Volume-mounted `./backend:/app/backend` | Copied in Dockerfile |
| Embedding port | Exposed `127.0.0.1:8001:8000` | Not exposed |
| Frontend | Volume-mounted | Bind-mounted (live updates) |
| Ollama | Available via `local-llm` profile | Not included |
| Restart policy | Not specified | `unless-stopped` |

---

## 5. Security

### 5.1 Secrets and Authentication

| Secret | Source | Purpose |
|--------|--------|---------|
| `VM_HOST` | GitHub secret | VM IP address |
| `VM_USER` | GitHub secret | SSH username |
| `VM_PASSWORD` | GitHub secret | SSH password |
| `GITHUB_TOKEN` | Auto-generated | GHCR push |
| `GHCR_PAT` | GitHub secret | GHCR pull on VM |

### 5.2 Secret Key Validation

On startup, the backend validates `SECRET_KEY`:

```python
_WEAK_SECRET_VALUES = {
    "", "khoa_du_phong_neu_quen_tao_env",
    "change-this-secret-in-production",
}

if settings.app_env == "production" and secret in _WEAK_SECRET_VALUES:
    raise RuntimeError("Weak SECRET_KEY detected in production")
```

### 5.3 Authentication Architecture

- **Password hashing:** Argon2 via `passlib.context.CryptContext`
- **JWT algorithm:** HS256
- **Token expiry:** 60 minutes (configurable)
- **Token claims:** `{ "sub": "username", "exp": <unix_timestamp> }`
- **Token sources:** `Authorization: Bearer <token>` header (primary) or `?token=<jwt>` query param (fallback)
- **Admin auth:** Requires user email ending with `@lumina.com.vn`

---

## 6. Appendices

### A: Deploy Script (Full)

```bash
cd ${{ secrets.VM_APP_DIR }}

LAST_GOOD_TAG=$(cat .deploy_last_good 2>/dev/null || echo "")
LAST_GOOD_COMMIT=$(cat .deploy_last_good_commit 2>/dev/null || echo "")

git pull --ff-only

export IMAGE_TAG

echo "$GHCR_PAT" | docker login ghcr.io -u ${{ steps.sha.outputs.owner }} --password-stdin
docker-compose -f docker-compose.vm.yml pull
sleep 5
docker-compose -f docker-compose.vm.yml down
docker system prune -af > /dev/null 2>&1 || true
docker-compose -f docker-compose.vm.yml up -d

sleep 240

ROLLBACK=false

curl -sf --max-time 10 http://localhost/api/docs > /dev/null \
  && echo "  OK" || { echo "  FAIL"; ROLLBACK=true; }

curl -sf --max-time 10 http://localhost/api/openapi.json > /dev/null \
  && echo "  OK" || { echo "  FAIL"; ROLLBACK=true; }

curl -sf --max-time 10 http://localhost:6333/collections > /dev/null \
  && echo "  OK" || { echo "  FAIL"; ROLLBACK=true; }

if [ "$ROLLBACK" = "true" ]; then
    if [ -n "$LAST_GOOD_TAG" ] && [ -n "$LAST_GOOD_COMMIT" ]; then
        git checkout "$LAST_GOOD_COMMIT"
        export IMAGE_TAG="$LAST_GOOD_TAG"
        docker-compose -f docker-compose.vm.yml down
        docker-compose -f docker-compose.vm.yml up -d
    fi
    exit 1
fi

echo "$IMAGE_TAG" > .deploy_last_good
echo "$COMMIT_SHA" > .deploy_last_good_commit
```

### B: Image Tag Conventions

```
ghcr.io/{owner}/rag-philosophy-backend:sha-{short_commit}
ghcr.io/{owner}/rag-philosophy-backend:latest
ghcr.io/{owner}/rag-philosophy-embedding:sha-{short_commit}
ghcr.io/{owner}/rag-philosophy-embedding:latest
```

- `sha-{short_commit}` — immutable, deterministic rollback target
- `latest` — mutable, convenience for development

---

## References

| Reference | File |
|-----------|------|
| CI workflow | `.github/workflows/ci.yml` |
| Deploy workflow | `.github/workflows/deploy.yml` |
| Production compose | `docker-compose.vm.yml` |
| Development compose | `docker-compose.yml` |
| Backend Dockerfile | `docker/backend.Dockerfile` |
| Embedding Dockerfile | `docker/embedding.Dockerfile` |
| Setup script | `deploy-vm.sh` |
| Integration test | `scripts/ci_integration_test.py` |
