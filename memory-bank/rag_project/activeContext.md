# Active Context

## Current State
The local RAG pipeline is fully implemented and functional. Recent improvements have enhanced the PDF parsing engine (handling Vietnamese text, math, and tables), refined markdown sanitization, and manually validated the ingestion of academic resources (`SML (1).md`). The system successfully processes Vietnamese academic documents through the following granular pipeline:

## Technical Pipeline Specs
* **Step 1: Loader (`step1_parser.py`)**: Implements a Page-Level Router architecture.
    * **Heuristics**: Uses `PyMuPDF` to evaluate page complexity.
    * **Margin Clipping**: Excludes top/bottom 10% of pages to remove running headers/footers.
    * **Fast Track**: Extracts simple text using `pdfplumber` to manage tight kerning.
    * **Heavy Track**: Uses `Docling` (with lazy initialization) for complex pages (tables, formulas).
    * **Sanitization**: `MarkdownSanitizer` cleans structural artifacts, handles inline headings, and standardizes markdown using robust regex heuristics.
* **Step 2: Chunker (`step2_chunker.py`)**: Implements hierarchical chunking. Uses `ViTokenizer` for Vietnamese word segmentation. (Parent chunks: 2000 size/200 overlap, Child chunks: 500 size/100 overlap).
* **Step 3: Vector DB (`step3_vector_db.py`)**: Embeds child chunks using local HuggingFace model (`bkai-foundation-models/vietnamese-bi-encoder`). Data is stored in Qdrant (Current config: `:memory:`).
* **Step 4: Generator (`step4_generator.py`)**: Uses LangChain retrieval connected to `gemini-3.1-flash-lite-preview`. The prompt restricts answers strictly to the provided UET context and enforces citations.

## Immediate Next Step
Phase 2: Build the FastAPI Backend. Wrap the existing local pipeline into accessible RESTful endpoints:
* `POST /upload`: Handles PDF ingestion and triggers steps 1-3.
* `POST /query`: Handles user questions and triggers step 4.