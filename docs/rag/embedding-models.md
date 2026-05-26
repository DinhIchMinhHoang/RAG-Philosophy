# Embedding Models

## Configuration

Embedding model is configured through environment variables:

```bash
EMBEDDING_MODEL_NAME=microsoft/harrier-oss-v1-270m
EMBEDDING_DEVICE=cpu
EMBEDDING_BATCH_SIZE=32
EMBEDDING_SERVICE_URL=http://embedding:8000
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

- **CPU**: Default, works on any machine without GPU
- **CUDA**: Set `EMBEDDING_DEVICE=cuda` and start Compose with `docker-compose.gpu.yml` on a host with Nvidia runtime support.

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
