# Embedding Models

## Configuration

Embedding model is configured through environment variables:

```bash
EMBEDDING_MODEL_NAME=microsoft/harrier-oss-v1-270m
EMBEDDING_DEVICE=auto
EMBEDDING_BATCH_SIZE=32
EMBEDDING_SERVICE_URL=http://embedding:8000
```

For Docker GPU runs, keep `EMBEDDING_DEVICE=auto` as the safe default and use
the GPU override variables:

```bash
GPU_EMBEDDING_DEVICE=auto
TORCH_INDEX_URL=https://download.pytorch.org/whl/cu121
```

## Model: microsoft/harrier-oss-v1-270m

- **Architecture**: Distilled transformer model
- **Parameters**: 270M (small, fast)
- **Task**: Sentence embeddings
- **Normalization**: L2-normalized outputs for cosine similarity

## Runtime Implementation

Backend and worker do not load `SentenceTransformer` directly. Docker Compose starts `rag_embedding`, which loads the model once at startup and exposes:

- `GET /health`
- `GET /info`
- `POST /embed`
- `POST /embed-batch`

`/health` returns `ready=true` only after model load and warmup complete. Backend chat uses `/embed` for query vectors. Worker ingest uses `/embed-batch` for child chunk vectors. The service uses `normalize_embeddings=True` and defaults to `EMBEDDING_BATCH_SIZE=32`.

Standalone `rag_core` scripts may still use `rag_core/common/embeddings.py` for local smoke tests and experiments. The production backend/worker path is the HTTP embedding service.

## Model Selection Rationale

| Criteria | Harrier-oss-v1-270m | Alternatives |
|----------|---------------------|--------------|
| Size | 270M (small) | sentence-transformers/all-MiniLM-L6-v2 (90M) |
| Speed | Fast on CPU | Faster than larger models |
| Quality | Good for academic text | Sufficient for philosophy domain |
| License | Open | Apache 2.0 |

## Device Configuration

- **Auto**: Default. Uses CUDA when visible to PyTorch; otherwise uses CPU.
- **CPU**: Set `EMBEDDING_DEVICE=cpu` to force CPU.
- **CUDA**: Start Compose with `docker-compose.gpu.yml` on a host with Nvidia
  Container Toolkit. The override sets `EMBEDDING_DEVICE` from
  `GPU_EMBEDDING_DEVICE`, defaulting to `auto`, and builds the embedding image
  with a CUDA PyTorch wheel.

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml build embedding
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

The `/info` endpoint reports both `configured_device` and the resolved runtime
`device`, plus CUDA availability.

## Performance Notes

- Embedding ~200 child docs: ~10-20 seconds on CPU
- Qdrant search: <100ms
- Total retrieval: dominated by embedding generation
- Docker runtime loads the embedding model once in `rag_embedding`, not separately in `rag_backend` and `rag_worker`.

## Alternative Models

To change the runtime embedding model, update `.env` and reindex any existing Qdrant collection whose vector dimension differs:

```bash
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

Other options to consider:
- `BAAI/bge-base-en-v1.5` (768-dim, higher quality)
- `intfloat/e5-small-v2` (33M, faster but less accurate)
