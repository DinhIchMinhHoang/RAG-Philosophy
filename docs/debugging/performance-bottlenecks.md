# Performance Bottlenecks

## Known Performance Issues

### PDF Parsing (Step 1)

**Bottleneck**: Heavy track OCR (Ollama)

**Configuration**:
```python
OLLAMA_MAX_WORKERS = 5       # Parallel OCR threads
VLM_TIMEOUT_SECONDS = 60     # Per-page timeout
DPI_FOR_OCR = 150            # Rendering resolution
```

**Mitigation**:
- Page classification reduces OCR to complex pages only
- Parallel execution via ThreadPoolExecutor
- Timeout prevents stuck pages

**Expected Time**:
- Simple PDF (10 pages): ~5 seconds
- Complex PDF (10 pages): ~30-60 seconds

### Embedding (Step 3)

**Bottleneck**: Harrier model inference on CPU

**Configuration**:
```python
DEVICE = "cpu"  # Change to "cuda" for GPU
```

**Expected Time**:
- 200 child docs: ~15-20 seconds on CPU
- 200 child docs: ~2-3 seconds on GPU

**Mitigation**: Use smaller model or GPU

<<<<<<< HEAD
=======
### Hybrid Retrieval Overhead

**Bottleneck**: BM25 adds an in-memory sparse scan over child docs for each query

**Costs**:
- BM25 search is effectively O(N) over the child corpus per query
- Tokenization adds per-query CPU overhead
- The tokenized corpus increases memory usage

**Mitigations**:
- Limit `HYBRID_SPARSE_K` and `HYBRID_FINAL_K`
- Pre-tokenize on ingest when possible
- Filter candidate docs before sparse scoring
- Move to a sparse index if hybrid traffic grows

>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
### LLM Generation (Step 4)

**Bottleneck**: Gemini API latency

**Mitigation**:
- Streaming response (tokens appear as generated)
- Low temperature (0.2) reduces inference time

**Expected Time**:
- First token: ~2-3 seconds
- Full response: ~10-30 seconds

## Profiling

Add timing to pipeline:

```python
import time
start = time.time()
# ... pipeline step ...
print(f"Step took {time.time() - start:.2f}s")
```

## Memory Usage

| Component | Memory |
|-----------|--------|
| Qdrant (:memory:) | ~50MB per 2000 vectors |
| InMemoryStore | ~10MB per 100 parent docs |
| Embedding model | ~500MB |
<<<<<<< HEAD
| LLM (Gemini API) | N/A (remote) |
=======
| Hybrid BM25 token cache | Scales with child doc count |
| LLM (Gemini API) | N/A (remote) |
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
