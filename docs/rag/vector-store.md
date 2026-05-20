# Vector Store

## Overview

<<<<<<< HEAD
The system uses Qdrant as the vector database with an in-memory store for parent documents. The architecture uses LangChain's MultiVectorRetriever to combine both.

## Qdrant Configuration
=======
The system uses Qdrant for child vectors and an InMemoryStore for parent documents. The default retriever remains LangChain's MultiVectorRetriever, and the pipeline can optionally switch to HybridParentRetriever to fuse dense Qdrant results with sparse BM25 matches.

## Configuration
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca

```python
# rag_core/config.py

<<<<<<< HEAD
QDRANT_LOCATION: str = ":memory:"   # In-memory for development
QDRANT_COLLECTION: str = "rag_philosophy"
TOP_K_RESULTS: int = 3
=======
QDRANT_LOCATION: str = ":memory:"   # Use Config.QDRANT_LOCATION in step3
QDRANT_COLLECTION: str = "rag_philosophy"
TOP_K_RESULTS: int = 3

HYBRID_ENABLED: bool = False
HYBRID_FINAL_K: int = 3
HYBRID_DENSE_K: int = 5
HYBRID_SPARSE_K: int = 20
HYBRID_RRF_K: int = 60
HYBRID_DENSE_WEIGHT: float = 0.7
HYBRID_SPARSE_WEIGHT: float = 0.3
SPARSE_MIN_TOKEN_LEN: int = 2
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
```

## Architecture

```
<<<<<<< HEAD
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
=======
+-----------------------------------------------------------------+
� MultiVectorRetriever / HybridParentRetriever                   �
�   id_key="doc_id"                                             �
+-----------------------------------------------------------------+
                           �
          +---------------------------------+
          ?                                 ?
+-------------------------+         +-------------------------+
�   QdrantVectorStore    �         �    InMemoryStore        �
�   (child documents)    �         �   (parent documents)    �
+-------------------------�         +-------------------------�
� Location: Config.QDRANT_LOCATION � � Key: doc_id (UUID)      �
� Collection: rag_philosophy      � � Value: Parent Document  �
� Embedding: Harrier              � �                         �
+-------------------------+         +-------------------------+
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
```

## Implementation

```python
# rag_core/step3_vector_db.py

<<<<<<< HEAD
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
=======
vectorstore = QdrantVectorStore.from_documents(
    documents=child_docs,
    embedding=embeddings,
    location=Config.QDRANT_LOCATION,
    collection_name=Config.QDRANT_COLLECTION,
)

store = InMemoryStore()
store.mset([(doc.metadata["doc_id"], doc) for doc in parent_docs])

if Config.HYBRID_ENABLED:
    retriever = HybridParentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        bm25_index=BM25ChildIndex.from_documents(child_docs),
        id_key="doc_id",
    )
else:
    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        docstore=store,
        id_key="doc_id",
        search_kwargs={"k": Config.TOP_K_RESULTS},
    )
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
```

## Retrieval Flow

<<<<<<< HEAD
1. **Query embedding**: User query → Harrier → 384-dim vector
2. **Child search**: Qdrant returns top-3 child docs by cosine similarity
3. **Parent lookup**: Each child doc contains doc_id → InMemoryStore lookup
4. **Output**: Parent documents (full context) returned to LLM
=======
1. Dense search in Qdrant over child documents.
2. Sparse search with BM25 over the in-memory child index.
3. Weighted Reciprocal Rank Fusion (RRF) combines both rankings: `score(doc_id) += weight / (HYBRID_RRF_K + rank)`.
4. The top child doc_ids are resolved through the parent InMemoryStore.

## Notes

- `rank_bm25` is used when available; the code falls back to a lightweight token-overlap scorer if the package is missing.
- Tokenization uses a regex word tokenizer with `SPARSE_MIN_TOKEN_LEN` as the minimum token length.
- `BM25ChildIndex` is rebuilt in memory on ingest, so sparse state is not persisted across restarts.
- `doc_id` is required on both child and parent documents; step3 validates it before indexing.
- `Config.QDRANT_LOCATION` is the canonical setting for Qdrant storage location.
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca

## Persistence

- **Development**: `:memory:` - all data lost on restart
<<<<<<< HEAD
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
=======
- **Production**: set `Config.QDRANT_LOCATION` to a Qdrant URL or file path

## Metrics

- **Index size**: ~2000 vectors � 384 dimensions � 3MB
- **Search latency**: <50ms on CPU for dense-only retrieval
- **Hybrid overhead**: extra BM25 scoring proportional to child document count
- **Memory usage**: ~50MB for 2000 child docs
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
