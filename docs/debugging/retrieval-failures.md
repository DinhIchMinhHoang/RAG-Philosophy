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

**Fix**: Upload PDF via `/documents/upload` first

### Empty Child Docs

**Symptom**: child_docs_count = 0

**Cause**: PDF parsing failed

**Fix**: Check step1_parser.py output

### Qdrant Not Indexing

**Symptom**: Embedding model loads but no vectors

**Cause**: Qdrant.from_documents failed silently

**Fix**: Check logs for Qdrant errors

## Logging

Enable debug logging:

```python
# rag_core/common/logging_utils.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check for messages like:
- `[Step 3] Đang nhúng X child docs vào Qdrant`
- `[Step 3] ✅ Đã index X child docs vào Qdrant`