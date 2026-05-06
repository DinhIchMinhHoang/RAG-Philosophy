"""
config.py - File cấu hình trung tâm cho RAG Core.

Load biến môi trường từ file .env và khai báo các hằng số
dùng chung cho toàn bộ pipeline.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load biến môi trường từ file .env (tìm ở project root)
_ROOT_DIR = Path(__file__).resolve().parent.parent
_ENV_PATH = _ROOT_DIR / ".env"
load_dotenv(dotenv_path=_ENV_PATH)


class Config:
    """Cấu hình trung tâm cho hệ thống RAG."""

    # ── API Keys ──────────────────────────────────────────────
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # ── Chunking — Parent Chunks (bảo toàn ngữ cảnh cho LLM) ──
    PARENT_CHUNK_SIZE: int = 2000    # Kích thước tối đa mỗi Parent Chunk
    PARENT_CHUNK_OVERLAP: int = 200  # Chồng lấp giữa các Parent Chunk

    # ── Chunking — Child Chunks (tối ưu tìm kiếm vector) ────
    CHILD_CHUNK_SIZE: int = 500      # Kích thước tối đa mỗi Child Chunk
    CHILD_CHUNK_OVERLAP: int = 100   # Chồng lấp giữa các Child Chunk

    # ── Embedding Model ──────────────────────────────────────
    EMBEDDING_MODEL_NAME: str = "microsoft/harrier-oss-v1-270m"

    # ── LLM (Generator) ─────────────────────────────────────
    LLM_MODEL: str = "gemini-3.1-flash-lite-preview"

    # ── Vector Database (Qdrant) ─────────────────────────────
    QDRANT_LOCATION: str = ":memory:"   # ":memory:" cho local test, URL cho production
    QDRANT_COLLECTION: str = "rag_philosophy"
    TOP_K_RESULTS: int = 3          # Số kết quả trả về khi truy xuất


    # ── Ollama OCR Engine (Heavy Track) ────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL_NAME: str = "glm-ocr"
    OLLAMA_MAX_WORKERS: int = 5          # ThreadPoolExecutor concurrency
    DPI_FOR_OCR: int = 150               # Resolution khi render trang → ảnh
    VLM_TIMEOUT_SECONDS: int = 60        # Hard timeout per page for VLM call
    MAX_IMAGE_LONG_EDGE: int = 1500      # Max px on longest edge before b64 encode

    # ── Đường dẫn dữ liệu ───────────────────────────────────
    _DATA_ROOT: Path = Path(__file__).resolve().parent.parent / "data"

    DATA_DIR: str       = str(_DATA_ROOT)
    RAW_DIR: str        = str(_DATA_ROOT / "raw")            # PDF, Slide gốc
    PROCESSED_DIR: str  = str(_DATA_ROOT / "processed")      # Markdown sau parse
    QDRANT_PATH: str    = str(_DATA_ROOT / "stores" / "qdrant")      # Vector DB
    DOC_STORE_DIR: str  = str(_DATA_ROOT / "stores" / "doc_store")   # Parent Chunks (JSON)

    @classmethod
    def validate(cls) -> None:
        """Kiểm tra các biến môi trường bắt buộc đã được thiết lập chưa."""
        if not cls.GEMINI_API_KEY:
            raise EnvironmentError(
                "GEMINI_API_KEY chưa được thiết lập. "
                "Hãy thêm vào file .env hoặc đặt biến môi trường."
            )

    def __repr__(self) -> str:
        return (
            f"Config(\n"
            f"  PARENT_CHUNK_SIZE={self.PARENT_CHUNK_SIZE},\n"
            f"  PARENT_CHUNK_OVERLAP={self.PARENT_CHUNK_OVERLAP},\n"
            f"  CHILD_CHUNK_SIZE={self.CHILD_CHUNK_SIZE},\n"
            f"  CHILD_CHUNK_OVERLAP={self.CHILD_CHUNK_OVERLAP},\n"
            f"  EMBEDDING_MODEL_NAME='{self.EMBEDDING_MODEL_NAME}',\n"
            f"  LLM_MODEL='{self.LLM_MODEL}',\n"
            f"  QDRANT_LOCATION='{self.QDRANT_LOCATION}',\n"
            f"  QDRANT_COLLECTION='{self.QDRANT_COLLECTION}',\n"
            f"  DATA_DIR='{self.DATA_DIR}'\n"
            f")"
        )

