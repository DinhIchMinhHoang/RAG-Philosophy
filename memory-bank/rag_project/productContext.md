# Product Context

## UET Project Context
This is a Retrieval-Augmented Generation (RAG) system for the "Thực hành phát triển hệ thống trí tuệ nhân tạo" course at the University of Engineering and Technology (UET). The system is designed to lookup lecture contents and PDF documents. It must be highly modular, easily configurable, and scalable for future integration with FastAPI and Celery/Redis.

## Tech Stack
- Python 3.13+
- LangChain (langchain, langchain-openai, langchain-community)
- Qdrant (qdrant-client)
- PyMuPDF (pymupdf)
- pdfplumber (pdfplumber)
- Docling (docling)
- python-dotenv

## Directory Structure
../rag_core/
├── .env                  # Chứa OPENAI_API_KEY
├── requirements.txt      # Chứa các dependencies
├── config.py             # File cấu hình trung tâm
├── step1_loader.py       # Tải và đọc tài liệu PDF
├── step2_chunker.py      # Chia nhỏ văn bản (Text Splitter)
├── step3_vector_db.py    # Nhúng (Embedding) và lưu vào Qdrant
├── step4_generator.py    # Truy xuất (Retriever) và sinh câu trả lời (LLM Chain)
└── main_test.py          # Kịch bản chạy thử toàn bộ pipeline

## Coding Guidelines
- **Clean Code & Modular**: Each Python file from step1 to step4 has only ONE responsibility. Define only functions/classes, no global execution.
- **Configuration Isolation**: ALL parameters (API Keys, Chunk Size, Model Name, Qdrant Collection) MUST be called from config class/variables in `config.py`. No hardcoding.
- **Logging & Error Handling**: Include clear print statements (or logging) at each step for debugging.
- **Prompt Engineering**: The LLM prompt in `step4_generator.py` must direct the AI as an academic assistant for UET students. It should use only the provided documents and admit if it doesn't know.
- **Citations Requirement**: LLM answers MUST include sources and pages extracted from LangChain metadata.
