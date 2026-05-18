# Data Flow

## Document Ingestion Flow

```
User Upload (PDF)
       │
       ▼
┌──────────────────┐
│ /api/documents  │ ◄─── FastAPI router (backend/app/routers/ingest.py)
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ RAGService.ingest_file()                                        │
│  1. Save to temp: temp/rag_uploads_*/filename.pdf               │
│  2. Call HybridPDFParser.parse_pdf()                            │
└────────┬─────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ Step 1: HybridPDFParser                                         │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Pass 1: Classify pages (simple vs complex)                │ │
│  │  - Image blocks > 50x50px → complex                        │ │
│  │  - Vector drawings ≥ 15 → complex                         │ │
│  │  - Math symbols > 3 → complex                              │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Pass 2: Execute                                            │ │
│  │  - Simple: pymupdf4llm.to_markdown()                     │ │
│  │  - Complex: Smart Crop → render → Ollama OCR (parallel)    │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  Output: List[Document] with {source, page} metadata           │
└────────┬─────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ Step 2: chunk_documents() (Parent-Child)                        │
│  - Parent: 2000 chars, 200 overlap → doc_id = UUID            │
│  - Child: 500 chars, 100 overlap → inherits doc_id            │
│  Output: (child_docs, parent_docs) tuple                       │
└────────┬─────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ Step 3: build_vector_db()                                       │
│  - child_docs → Qdrant (:memory:, collection=rag_philosophy)   │
│  - parent_docs → InMemoryStore (keyed by doc_id)               │
│  - MultiVectorRetriever: id_key="doc_id", k=3                 │
│  Output: MultiVectorRetriever                                   │
└────────┬─────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ RAGService updates internal state                              │
│  - _all_child_docs.extend(child_docs)                          │
│  - _all_parent_docs.extend(parent_docs)                        │
│  - _source_files.append(filename)                              │
│  - _retriever = build_vector_db(all_child, all_parent)        │
│  Return: {filename, status, pages, chunks}                     │
└──────────────────────────────────────────────────────────────────┘
```

## Query Flow

```
User Question (Chat Input)
        │
        ▼
┌───────────────────────┐
│ /api/chat/stream (POST)  │ ◄─── {message: "..."}
└──────────┬────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│ RAGService.stream_answer() (async generator)                   │
│                                                                  │
│ 1. Check retriever exists                                       │
│    └─ If None: yield "Chưa có tài liệu nào được tải lên..."    │
│                                                                  │
│ 2. Retrieve documents                                          │
│    retriever.invoke(question) → List[Document] (parent level)  │
│                                                                  │
│ 3. Format context with source/page                              │
│    [Tài liệu 1 — filename.pdf, Trang 5]\n                    │
│    {document_content}                                          │
│                                                                  │
│ 4. Build streaming chain                                       │
│    prompt | llm | StrOutputParser()                            │
│                                                                  │
│ 5. Stream tokens (async for chunk in chain.astream(...))      │
│    └─ yield chunk                                               │
│                                                                  │
│ 6. Append sources footer                                       │
│    📚 **Nguồn tham khảo:**\n- file1.pdf, Trang 5\n- ...       │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│ SSE Response (text/event-stream)                               │
│  data: {"token": "X"}                                          │
│  data: {"token": "Y"}                                          │
│  ...                                                            │
│  data: {"token": "", "done": true}                             │
└─────────────────────────────────────────────────────────────────┘
```

## Metadata Flow

### Document Metadata Keys

| Key | Source | Usage |
|-----|--------|-------|
| `source` | step1_parser | Filename of original PDF |
| `page` | step1_parser | Page number (1-indexed) |
| `doc_id` | step2_chunker | UUID linking child→parent |

### Metadata Preservation

- **Step 1 → Step 2**: source and page preserved in parent/child
- **Step 2 → Step 3**: doc_id added, all keys preserved
- **Step 3 → Step 4**: MultiVectorRetriever returns parent docs with full metadata

## State Transitions

### RAGService State Machine

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   EMPTY     │────▶│  LOADING     │────▶│   READY     │
│ (initial)   │     │ (ingesting)  │     │ (ready)     │
└─────────────┘     └──────────────┘     └─────────────┘
       ▲                                         │
       │                                         │
       └───────────── reset() ──────────────────┘
```

- **EMPTY**: `_retriever = None`, no sources
- **LOADING**: During `ingest_file()` call
- **READY**: After successful `build_vector_db()` call
- **RESET**: Clears all state, returns to EMPTY
