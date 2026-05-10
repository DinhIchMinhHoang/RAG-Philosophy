# Vector Store

## Overview

The system uses Qdrant as the vector database with an in-memory store for parent documents. The architecture uses LangChain's MultiVectorRetriever to combine both.

## Qdrant Configuration

```python
# rag_core/config.py

QDRANT_LOCATION: str = ":memory:"   # In-memory for development
QDRANT_COLLECTION: str = "rag_philosophy"
TOP_K_RESULTS: int = 3
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ MultiVectorRetriever                                           │
│   id_key="doc_id", search_kwargs={"k": 3}                     │
└────────────────────────────┬────────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          ▼                                    ▼
┌─────────────────────────┐          ┌─────────────────────────┐
│   QdrantVectorStore    │          │    InMemoryStore        │
│   (child documents)    │          │   (parent documents)    │
├─────────────────────────┤          ├─────────────────────────┤
│ Location: :memory:      │          │ Key: doc_id (UUID)      │
│ Collection: rag_phi    │          │ Value: Parent Document  │
│ Embedding: Harrier     │          │                         │
│ Search: cosine sim     │          │                         │
└─────────────────────────┘          └─────────────────────────┘
```

## Implementation

```python
# rag_core/step3_vector_db.py

# 1. Build Qdrant store with child docs
vectorstore = QdrantVectorStore.from_documents(
    documents=child_docs,
    embedding=embeddings,
    location=":memory:",
    collection_name="rag_philosophy",
)

# 2. Build doc store with parent docs
store = InMemoryStore()
store.mset([(doc.metadata["doc_id"], doc) for doc in parent_docs])

# 3. Connect with MultiVectorRetriever
retriever = MultiVectorRetriever(
    vectorstore=vectorstore,
    docstore=doc_store,
    id_key="doc_id",
    search_kwargs={"k": TOP_K_RESULTS},
)
```

## Retrieval Flow

1. **Query embedding**: User query → Harrier → 384-dim vector
2. **Child search**: Qdrant returns top-3 child docs by cosine similarity
3. **Parent lookup**: Each child doc contains doc_id → InMemoryStore lookup
4. **Output**: Parent documents (full context) returned to LLM

## Persistence

- **Development**: `:memory:` - all data lost on restart
- **Production**: Set `QDRANT_LOCATION` to URL (e.g., "http://localhost:6333")

To enable persistence:

```python
# rag_core/config.py
QDRANT_LOCATION: str = "http://localhost:6333"
```

Or file-based:

```python
QDRANT_LOCATION: str = "./data/stores/qdrant"
```

## Collection Management

The system creates a collection "rag_philosophy" automatically on first use. If the collection exists, Qdrant will:
- Append new vectors (if schema matches)
- Error if schema differs

To reset: restart application (in-memory) or delete collection (persistent).

## Metrics

- **Index size**: ~2000 vectors × 384 dimensions ≈ 3MB
- **Search latency**: <50ms on CPU
- **Memory usage**: ~50MB for 2000 child docs