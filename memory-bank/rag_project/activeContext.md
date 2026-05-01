# Active Context

## Current State
The local RAG pipeline is fully implemented and functional. Recent improvements have enhanced the PDF parsing engine (handling Vietnamese text, math, and tables), refined markdown sanitization, and manually validated the ingestion of academic resources. The system successfully processes Vietnamese academic documents through a highly modular and configurable pipeline defined centrally in `config.py`.

## Technical Pipeline Specs
* **Step 1: Loader/Parser (`step1_loader.py` & `step1_parser.py`)**: Implements a Page-Level Router architecture.
    * Uses `PyMuPDF` to evaluate page complexity.
    * **Fast Track**: Extracts simple text using `pdfplumber`.
    * **Heavy Track**: Uses `Docling` or Ollama OCR Engine (`glm-ocr` at `http://localhost:11434` with 200 DPI) for complex pages (tables, formulas).
    * Margin Clipping (10%) and robust Regex Markdown Sanitization.
* **Step 2: Chunker (`step2_chunker.py`)**: Hierarchical chunking with `ViTokenizer` (Vietnamese word segmentation).
    * **Parent Chunks**: Size = 2000, Overlap = 200 (preserves context for LLM).
    * **Child Chunks**: Size = 500, Overlap = 100 (optimizes vector search).
* **Step 3: Vector DB (`step3_vector_db.py`)**: 
    * **Embedding Model**: `bkai-foundation-models/vietnamese-bi-encoder` (Local HuggingFace model).
    * **Storage**: Qdrant Database (Location: `:memory:`, Collection: `rag_philosophy`).
* **Step 4: Generator (`step4_generator.py`)**: 
    * **LLM Model**: `gemini-3.1-flash-lite-preview`.
    * Retains top `TOP_K_RESULTS = 3` context chunks.
    * Prompt enforces strict reliance on UET context and exact citations.

## Immediate Next Step
Phase 2: Build the FastAPI Backend. Wrap the existing local pipeline into accessible RESTful endpoints:
* `POST /upload`: Handles PDF ingestion and triggers steps 1-3.
* `POST /query`: Handles user questions and triggers step 4.