# Retrieval Failures

## Symptoms

1. **Empty retrieval**: No documents returned for query
2. **Irrelevant results**: Retrieved docs don't match question
3. **Wrong metadata**: Source/page info incorrect

## Diagnosis Steps

### 1. Check RAGService State

```python
# In rag_service.py after query
print(f"has_sources: {rag_service.has_sources}")
print(f"source_count: {rag_service.source_count}")
print(f"sources: {rag_service.sources}")
```

### 2. Test Retriever Directly

```python
# python rag_core/main_test.py
from rag_core import build_pipeline
artifacts, chain = build_pipeline()
docs = artifacts.retriever.invoke("What is philosophy?")
for doc in docs:
    print(doc.metadata)
```

### 3. Verify Document Count

Expected count: ~200 child docs per 10-page PDF

```python
print(f"child_docs: {artifacts.child_docs_count}")
print(f"parent_docs: {artifacts.parent_docs_count}")
```

## Common Causes

### No Sources Loaded

**Symptom**: `has_sources: False`

<<<<<<< HEAD
**Fix**: Upload PDF via `/documents/upload` first
=======
**Fix**: Upload PDF via `/api/documents` first
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca

### Empty Child Docs

**Symptom**: child_docs_count = 0

**Cause**: PDF parsing failed

**Fix**: Check step1_parser.py output

### Qdrant Not Indexing

**Symptom**: Embedding model loads but no vectors

**Cause**: Qdrant.from_documents failed silently

**Fix**: Check logs for Qdrant errors

<<<<<<< HEAD
=======
### Hybrid: rank_bm25 Missing

**Symptom**: Hybrid retrieval behaves like a simple token-overlap fallback

**Cause**: `rank_bm25` is not installed

**Fix**: Install `rank_bm25` and rerun the hybrid retriever tests

### Hybrid: BM25 Returns No Tokens

**Symptom**: Sparse side returns no candidates

**Cause**: Query text is empty or all terms are filtered out by `SPARSE_MIN_TOKEN_LEN`

**Fix**: Check the query text, tokenizer output, and the sparse token length config

### Hybrid: Missing doc_id

**Symptom**: `KeyError` during vector-store build

**Cause**: One or more child docs do not carry `doc_id`

**Fix**: Verify step2 chunking and step3 validation logs

>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
## Logging

Enable debug logging:

```python
# rag_core/common/logging_utils.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check for messages like:
<<<<<<< HEAD
- `[Step 3] Đang nhúng X child docs vào Qdrant`
- `[Step 3] ✅ Đã index X child docs vào Qdrant`
=======
- `[Step 3] �ang nh�ng X child docs v�o Qdrant`
- `[Step 3] ? �� index X child docs v�o Qdrant`

## Recommended Checks

- Run `python -m unittest rag_core.tests.test_hybrid_retriever -v`
- Run `python rag_core/main_test.py`
- Inspect ingest logs for BM25 tokenization and doc_id validation errors
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
