# Active Context

## Current State
The local RAG pipeline is fully implemented and functional. Recent improvements have enhanced the PDF parsing engine (handling Vietnamese text, math, and tables), refined markdown sanitization, and migrated to a high-performance Parent-Child retrieval architecture. The system successfully processes complex academic documents through a highly modular and configurable pipeline defined centrally in `config.py`.

## Technical Pipeline Specs
* **Step 1: Parser (`step1_parser.py`)**: Implements a Hybrid Two-Pass Concurrent Parser.
    * Uses `fitz` (PyMuPDF) to evaluate page complexity.
    * **Fast Track**: Extracts simple text using `pymupdf4llm`.
    * **Heavy Track**: Uses Ollama OCR Engine (`glm-ocr` at `http://localhost:11434` with 150 DPI) concurrently via ThreadPoolExecutor for complex pages with Smart Cropping.
    * Robust Regex Markdown Sanitization.
* **Step 2: Chunker (`step2_chunker.py`)**: Hierarchical Parent-Child chunking using `RecursiveCharacterTextSplitter`.
    * **Parent Chunks**: Size = 2000, Overlap = 200 (preserves context for LLM, stored in `InMemoryStore`).
    * **Child Chunks**: Size = 500, Overlap = 100 (optimizes vector search, stored in Qdrant).
* **Step 3: Vector DB (`step3_vector_db.py`)**: 
    * **Embedding Model**: `microsoft/harrier-oss-v1-270m` (Local HuggingFace model).
    * **Storage**: Qdrant Database (Location: `:memory:`, Collection: `rag_philosophy`) linked with `InMemoryStore` via `MultiVectorRetriever`.
* **Step 4: Generator (`step4_generator.py`)**: 
    * **LLM Model**: `gemini-3.1-flash-lite-preview`.
    * Retains top `TOP_K_RESULTS = 3` context chunks.
    * Prompt enforces strict reliance on context and exact citations.

## Immediate Next Step
Phase 2: Build the FastAPI Backend. Wrap the existing local pipeline into accessible RESTful endpoints:
* `POST /upload`: Handles PDF ingestion and triggers steps 1-3.
* `POST /query`: Handles user questions and triggers step 4.