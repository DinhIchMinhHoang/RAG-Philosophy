# Product Context

## UET Project Context
This is a Retrieval-Augmented Generation (RAG) system for the "Thực hành phát triển hệ thống trí tuệ nhân tạo" course at the University of Engineering and Technology (UET). The system is designed to lookup lecture contents and PDF documents. It must be highly modular, easily configurable, and scalable for future integration with FastAPI and Celery/Redis.

## Exact UET Tech Stack
- Python 3.10+
- LangChain Ecosystem: `langchain`, `langchain-google-genai`, `langchain-community`, `langchain-qdrant`, `langchain-huggingface`, `langchain-text-splitters`
- Local Embedding: HuggingFace (`microsoft/harrier-oss-v1-270m`)
- Vector Database: Qdrant
- PDF / Document Parsing: `pymupdf`, `pymupdf4llm`, `Pillow`
- LLM / OCR Engine: Ollama (`glm-ocr`), Gemini (`gemini-3.1-flash-lite-preview`)
- Environment Management: `python-dotenv`

## Directory Structure
./
├── config.py                 # Stub config (main config is rag_core/config.py)
├── requirements.txt
├── rag_core/
│   ├── config.py             # Central configuration
│   ├── pipeline.py           # Pipeline orchestrator (ingest, build_pipeline, query)
│   ├── common/               # Shared utilities
│   │   ├── __init__.py
│   │   ├── logging_utils.py  # configure_logging(), get_logger()
│   │   ├── pdf_utils.py      # normalize_pdf_path(), collect_pdf_paths()
│   │   └── embeddings.py     # build_embeddings()
│   ├── step1_parser.py       # Hybrid Two-Pass Parser
│   ├── step2_chunker.py      # Parent-Child Text Splitter
│   ├── step3_vector_db.py     # Embedding + Qdrant storage
│   ├── step4_generator.py    # Retrieval + LLM Chain
│   ├── main_test.py          # Interactive pipeline test
│   ├── ragas_eval.py         # RAGAS evaluation script
│   └── tests/                # Unit tests
│       ├── test_logging_utils.py
│       ├── test_pdf_utils.py
│       ├── test_embeddings.py
│       └── test_pipeline.py
├── backend/app/              # FastAPI backend
├── frontend/                 # Vanilla JS frontend
├── data/                     # PDFs and stores
└── memory-bank/              # Project context

## Coding Guidelines
- **Clean Code & Modular**: Each Python file from step1 to step4 has only ONE responsibility. Define only functions/classes, no global execution.
- **Configuration Isolation**: ALL parameters (API Keys, Chunk Size, Model Name, Qdrant Collection) MUST be called from config class/variables in `config.py`. No hardcoding.
- **Logging & Error Handling**: Include clear print statements (or logging) at each step for debugging.
- **Prompt Engineering**: The LLM prompt in `step4_generator.py` must direct the AI as an academic assistant for UET students. It should use only the provided documents and admit if it doesn't know.
- **Citations Requirement**: LLM answers MUST include sources and pages extracted from LangChain metadata.
