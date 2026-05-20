# Retrieval Pipeline

## Pipeline Overview

The retrieval pipeline transforms raw PDFs into searchable vectors and connects them to the LLM for question answering. The pipeline is orchestrated by `rag_core/pipeline.py`.

## Pipeline Stages

### Stage 1: PDF Parsing (step1_parser.py)

**HybridPDFParser** uses a two-pass approach:

```
Pass 1: Scan & Classify
<<<<<<< HEAD
├── For each page in PDF:
│   ├── Check for image blocks (> 50x50px) → complex
│   ├── Check for vector drawings (≥ 15) → complex
│   └── Check for math symbols (> 3) → complex
└── Output: (simple_pages[], complex_pages[])

Pass 2: Execute
├── Fast Track (simple): pymupdf4llm.to_markdown()
└── Heavy Track (complex): Smart Crop → render → Ollama OCR (parallel)
=======
+-- For each page in PDF:
�   +-- Check for image blocks (> 50x50px) ? complex
�   +-- Check for vector drawings (= 15) ? complex
�   +-- Check for math symbols (> 3) ? complex
+-- Output: (simple_pages[], complex_pages[])

Pass 2: Execute
+-- Fast Track (simple): pymupdf4llm.to_markdown()
+-- Heavy Track (complex): Smart Crop ? render ? Ollama OCR (parallel)
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
```

**Page Classification Heuristics:**
- Images: Check `page.get_image_info()` for blocks > 50x50px
<<<<<<< HEAD
- Drawings: Check `page.get_drawings()` count ≥ 15
- Math: Check for symbols (∑, ∫, ∈, ∀, ≤, ≥, etc.) > 3 occurrences
=======
- Drawings: Check `page.get_drawings()` count = 15
- Math: Check for symbols (?, ?, ?, ?, =, =, etc.) > 3 occurrences
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca

**Output**: `List[Document]` with metadata `{source: str, page: int}`

### Stage 2: Chunking (step2_chunker.py)

**Parent-Child Splitting** creates two levels of granularity:

```
Page Document (from Step 1)
<<<<<<< HEAD
       │
       ▼
┌─────────────────────────────────────────────┐
│ RecursiveCharacterTextSplitter              │
│ (chunk_size=2000, overlap=200)              │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ Parent Documents (each with doc_id=UUID)  │
│ {source, page, doc_id}                     │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ RecursiveCharacterTextSplitter             │
│ (chunk_size=500, overlap=100)              │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ Child Documents (inherit doc_id)           │
│ {source, page, doc_id}                     │
└─────────────────────────────────────────────┘
```

**Key Design**: doc_id links child→parent, enabling MultiVectorRetriever to retrieve parent context after child match.

### Stage 3: Vector Store (step3_vector_db.py)

**MultiVectorRetriever Architecture**:

```
Query ──────────────────────────────────────────▶
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────┐
│ Qdrant (in-memory)                                                 │
│ - Embeds child_docs with Harrier model                            │
│ - Performs similarity search                                      │
│ - Returns child docs with doc_id in metadata                     │
└────────────────────────┬───────────────────────────────────────────┘
                         │
                         ▼ (doc_id lookup)
┌────────────────────────────────────────────────────────────────────┐
│ InMemoryStore                                                     │
│ - Keyed by doc_id                                                 │
│ - Returns full parent documents (context)                        │
└────────────────────────┬───────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────┐
│ Output: List[Document] (PARENT level, full context)              │
└────────────────────────────────────────────────────────────────────┘
```

**Configuration**:
- Collection: "rag_philosophy"
- Top-k: 3 results
- Embedding: microsoft/harrier-oss-v1-270m (CPU)
=======
       �
       ?
+---------------------------------------------+
� RecursiveCharacterTextSplitter              �
� (chunk_size=2000, overlap=200)             �
+---------------------------------------------+
                   �
                   ?
+---------------------------------------------+
� Parent Documents (each with doc_id=UUID)   �
� {source, page, doc_id}                     �
+---------------------------------------------+
                   �
                   ?
+---------------------------------------------+
� RecursiveCharacterTextSplitter              �
� (chunk_size=500, overlap=100)              �
+---------------------------------------------+
                   �
                   ?
+---------------------------------------------+
� Child Documents (inherit doc_id)           �
� {source, page, doc_id}                     �
+---------------------------------------------+
```

**Key Design**: doc_id links child?parent, enabling MultiVectorRetriever to retrieve parent context after child match.

### Stage 3: Vector Store (step3_vector_db.py)

**Default: MultiVectorRetriever**

```
Query -----------------------------------------?
                                                �
                                                ?
+--------------------------------------------------------------------+
� Qdrant                                                             �
� - Embeds child_docs with Harrier model                             �
� - Performs dense similarity search                                 �
� - Returns child docs with doc_id in metadata                       �
+--------------------------------------------------------------------+
                         �
                         ? (doc_id lookup)
+--------------------------------------------------------------------+
� InMemoryStore                                                      �
� - Keyed by doc_id                                                  �
� - Returns full parent documents (context)                          �
+--------------------------------------------------------------------+
                         �
                         ?
+--------------------------------------------------------------------+
� Output: List[Document] (PARENT level, full context)                �
+--------------------------------------------------------------------+
```

**Hybrid Mode: HybridParentRetriever**

When `Config.HYBRID_ENABLED` is `True`, step3 builds a `HybridParentRetriever` instead of `MultiVectorRetriever`.

- `BM25ChildIndex` tokenizes `child_docs` in memory and builds a BM25 index.
- Dense candidates come from Qdrant (`HYBRID_DENSE_K`).
- Sparse candidates come from BM25 (`HYBRID_SPARSE_K`).
- Weighted RRF combines rankings:
  `score(doc_id) += weight / (HYBRID_RRF_K + rank)`
- Final parent docs are fetched from `InMemoryStore` using `doc_id`.

**Configuration references**:
- `Config.QDRANT_LOCATION`
- `Config.QDRANT_COLLECTION`
- `Config.TOP_K_RESULTS`
- `Config.HYBRID_ENABLED`
- `Config.HYBRID_FINAL_K`
- `Config.HYBRID_DENSE_K`
- `Config.HYBRID_SPARSE_K`
- `Config.HYBRID_RRF_K`
- `Config.HYBRID_DENSE_WEIGHT`
- `Config.HYBRID_SPARSE_WEIGHT`
- `Config.SPARSE_MIN_TOKEN_LEN`
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca

### Stage 4: Generation (step4_generator.py)

**RAG Chain**:

```
User Question
<<<<<<< HEAD
       │
       ▼
┌────────────────────────────────────────────────────────────────┐
│ MultiVectorRetriever.invoke(question)                         │
│ → Returns parent documents with context                      │
└────────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────────────┐
│ Context + Question → ChatPromptTemplate                      │
│                                                                  │
│ System Prompt:                                                 │
│ "Bạn là chuyên gia AI, trợ lý học tập cho sinh viên UET..."   │
│ "Hãy trả lời câu hỏi dựa TRỰC TIẾP trên các đoạn văn..."     │
│                                                                  │
│ Human: "{context}\n\n{input}"                                  │
└────────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────────────┐
│ ChatGoogleGenerativeAI (gemini-3.1-flash-lite-preview)        │
│ temperature=0.2                                               │
└────────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────────────┐
│ Output: {answer: str, sources: [{page, source}]}             │
└────────────────────────────────────────────────────────────────┘
=======
       �
       ?
+----------------------------------------------------------------+
� MultiVectorRetriever.invoke(question)                         �
� ? Returns parent documents with context                      �
+----------------------------------------------------------------+
                         �
                         ?
+----------------------------------------------------------------+
� Context + Question ? ChatPromptTemplate                      �
�                                                                  �
� System Prompt:                                                 �
� "B?n l� chuy�n gia AI, tr? l� h?c t?p cho sinh vi�n UET..."   �
� "H�y tr? l?i c�u h?i d?a TR?C TI?P tr�n c�c do?n van..."     �
�                                                                  �
� Human: "{context}\n\n{input}"                                  �
+----------------------------------------------------------------+
                         �
                         ?
+----------------------------------------------------------------+
� ChatGoogleGenerativeAI (gemini-3.1-flash-lite-preview)        �
� temperature=0.2                                               �
+----------------------------------------------------------------+
                         �
                         ?
+----------------------------------------------------------------+
� Output: {answer: str, sources: [{page, source}]}             �
+----------------------------------------------------------------+
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
```

## Pipeline API

```python
# rag_core/pipeline.py

def ingest(target_pdf: Optional[str] = None) -> PipelineArtifacts:
    """Ingest PDFs and return retriever + metadata."""
    # 1. Collect PDF paths
    # 2. Parse each PDF
    # 3. Chunk documents
    # 4. Build vector DB
    # Returns: PipelineArtifacts(retriever, child_count, parent_count, pdf_paths)

def build_pipeline(target_pdf: Optional[str] = None):
    """Build full RAG chain (retriever + LLM)."""
    artifacts = ingest(target_pdf)
    rag_chain = setup_rag_chain(artifacts.retriever)
    return artifacts, rag_chain

def query(rag_chain, question: str) -> dict:
    """Ask question, returns {answer, sources}."""
    return ask(rag_chain, question)
```

## MultiVectorRetriever Details

The key insight is that we index small child chunks (good for matching) but retrieve large parent chunks (good for context):

| Aspect | Child | Parent |
|--------|-------|--------|
| Size | 500 chars | 2000 chars |
| Use | Vector similarity search | LLM context |
<<<<<<< HEAD
| Indexed in | Qdrant | InMemoryStore |
| Linked by | doc_id (foreign key) | - |

When a query matches child chunks, the retriever uses the child's `doc_id` to look up the corresponding parent document in the InMemoryStore.
=======
| Indexed in | Qdrant / BM25ChildIndex | InMemoryStore |
| Linked by | doc_id (foreign key) | - |

`MultiVectorRetriever` remains the default. `HybridParentRetriever` is used only when `Config.HYBRID_ENABLED` is `True`.

When a query matches child chunks, the retriever uses the child's `doc_id` to look up the corresponding parent document in the InMemoryStore.
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
