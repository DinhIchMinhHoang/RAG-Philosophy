import os
from pathlib import Path

_ROOT_DIR = Path(__file__).resolve().parent
_DATA_ROOT = _ROOT_DIR / "data"


class Config:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    PARENT_CHUNK_SIZE: int = 2000
    PARENT_CHUNK_OVERLAP: int = 200
    CHILD_CHUNK_SIZE: int = 500
    CHILD_CHUNK_OVERLAP: int = 100
    EMBEDDING_MODEL_NAME: str = "microsoft/harrier-oss-v1-270m"
    DEVICE: str = "cpu"
    LLM_MODEL: str = "gemini-3.1-flash-lite-preview"
    QDRANT_LOCATION: str = ":memory:"
    QDRANT_COLLECTION: str = "rag_philosophy"
    TOP_K_RESULTS: int = 3
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL_NAME: str = "glm-ocr"
    OLLAMA_MAX_WORKERS: int = 5
    DPI_FOR_OCR: int = 150
    VLM_TIMEOUT_SECONDS: int = 120
    RAW_DIR: str = str(_DATA_ROOT / "raw")
    PROCESSED_DIR: str = str(_DATA_ROOT / "processed")
    VECTOR_STORE_DIR: str = str(_DATA_ROOT / "stores" / "vector_db")