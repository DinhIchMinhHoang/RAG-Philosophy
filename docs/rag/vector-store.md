# Vector Store

## Overview

The system uses Qdrant for child vectors and an InMemoryStore for parent documents. The default retriever remains LangChain's MultiVectorRetriever, and the pipeline can optionally switch to HybridParentRetriever to fuse dense Qdrant results with sparse BM25 matches.

## Configuration

```python
# rag_core/config.py

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
```

## Architecture

```
+-----------------------------------------------------------------+
¦ MultiVectorRetriever / HybridParentRetriever                   ¦
¦   id_key="doc_id"                                             ¦
+-----------------------------------------------------------------+
                           ¦
          +---------------------------------+
          ?                                 ?
+-------------------------+         +-------------------------+
¦   QdrantVectorStore    ¦         ¦    InMemoryStore        ¦
¦   (child documents)    ¦         ¦   (parent documents)    ¦
+-------------------------¦         +-------------------------¦
¦ Location: Config.QDRANT_LOCATION ¦ ¦ Key: doc_id (UUID)      ¦
¦ Collection: rag_philosophy      ¦ ¦ Value: Parent Document  ¦
¦ Embedding: Harrier              ¦ ¦                         ¦
+-------------------------+         +-------------------------+
```

## Implementation

```python
# rag_core/step3_vector_db.py

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
```

## Retrieval Flow

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

## Persistence

- **Development**: `:memory:` - all data lost on restart
- **Production**: set `Config.QDRANT_LOCATION` to a Qdrant URL or file path

## Metrics

- **Index size**: ~2000 vectors × 384 dimensions ˜ 3MB
- **Search latency**: <50ms on CPU for dense-only retrieval
- **Hybrid overhead**: extra BM25 scoring proportional to child document count
- **Memory usage**: ~50MB for 2000 child docs
