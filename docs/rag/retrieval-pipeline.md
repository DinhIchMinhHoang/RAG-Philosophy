# Retrieval Pipeline

## Pipeline Overview

The retrieval pipeline transforms raw PDFs into searchable vectors and connects them to the LLM for question answering. The pipeline is orchestrated by `rag_core/pipeline.py`.

## Pipeline Stages

### Stage 1: PDF Parsing (step1_parser.py)

**HybridPDFParser** uses a two-pass approach:

```
Pass 1: Scan & Classify
├── For each page in PDF:
│   ├── Check for image blocks (> 50x50px) → complex
│   ├── Check for vector drawings (≥ 15) → complex
│   └── Check for math symbols (> 3) → complex
└── Output: (simple_pages[], complex_pages[])

Pass 2: Execute
├── Fast Track (simple): pymupdf4llm.to_markdown()
└── Heavy Track (complex): Smart Crop → render → Ollama OCR (parallel)
```

**Page Classification Heuristics:**
- Images: Check `page.get_image_info()` for blocks > 50x50px
- Drawings: Check `page.get_drawings()` count ≥ 15
- Math: Check for symbols (∑, ∫, ∈, ∀, ≤, ≥, etc.) > 3 occurrences

**Output**: `List[Document]` with metadata `{source: str, page: int}`

### Stage 2: Chunking (step2_chunker.py)

**Parent-Child Splitting** creates two levels of granularity:

```
Page Document (from Step 1)
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

### Stage 4: Generation (step4_generator.py)

**RAG Chain**:

```
User Question
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
| Indexed in | Qdrant | InMemoryStore |
| Linked by | doc_id (foreign key) | - |

When a query matches child chunks, the retriever uses the child's `doc_id` to look up the corresponding parent document in the InMemoryStore.