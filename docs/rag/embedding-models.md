# Embedding Models

## Configuration

Embedding model is configured in `rag_core/config.py`:

```python
# Embedding Model
EMBEDDING_MODEL_NAME: str = "microsoft/harrier-oss-v1-270m"
DEVICE: str = "cpu"  # Set to 'cuda' for GPU acceleration
```

## Model: microsoft/harrier-oss-v1-270m

- **Architecture**: Distilled transformer model
- **Parameters**: 270M (small, fast)
- **Task**: Sentence embeddings
- **Normalization**: L2-normalized outputs for cosine similarity

## Implementation

```python
# rag_core/common/embeddings.py

from langchain_huggingface import HuggingFaceEmbeddings

def build_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name="microsoft/harrier-oss-v1-270m",
        model_kwargs={
            "device": "cpu",
            "trust_remote_code": True,  # Required for Harrier
        },
        encode_kwargs={
            "normalize_embeddings": True,  # L2 normalization
        },
    )
```

## Usage in Vector Store

```python
# rag_core/step3_vector_db.py

embeddings = _init_embeddings()  # Calls build_embeddings()

vectorstore = QdrantVectorStore.from_documents(
    documents=child_docs,
    embedding=embeddings,
    location=":memory:",
    collection_name="rag_philosophy",
)
```

## Model Selection Rationale

| Criteria | Harrier-oss-v1-270m | Alternatives |
|----------|---------------------|--------------|
| Size | 270M (small) | sentence-transformers/all-MiniLM-L6-v2 (90M) |
| Speed | Fast on CPU | Faster than larger models |
| Quality | Good for academic text | Sufficient for philosophy domain |
| License | Open | Apache 2.0 |

## Device Configuration

- **CPU**: Default, works on any machine without GPU
- **CUDA**: Set `DEVICE="cuda"` in config for GPU acceleration (requires CUDA toolkit and compatible GPU)

## Performance Notes

- Embedding ~200 child docs: ~10-20 seconds on CPU
- Qdrant search: <100ms
- Total retrieval: dominated by embedding generation

## Alternative Models

To change the embedding model, update `rag_core/config.py`:

```python
EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
```

Other options to consider:
- `BAAI/bge-base-en-v1.5` (768-dim, higher quality)
- `intfloat/e5-small-v2` (33M, faster but less accurate)