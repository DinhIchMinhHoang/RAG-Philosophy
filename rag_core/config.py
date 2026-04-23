"""
config.py - File cấu hình trung tâm cho RAG Core.

Load biến môi trường từ file .env và khai báo các hằng số
dùng chung cho toàn bộ pipeline.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load biến môi trường từ file .env (cùng thư mục với config.py)
_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)


class Config:
    """Cấu hình trung tâm cho hệ thống RAG."""

    # ── API Keys ──────────────────────────────────────────────
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # ── Chunking (Text Splitter) ──────────────────────────────
    CHUNK_SIZE: int = 1000        # Số ký tự tối đa mỗi chunk
    CHUNK_OVERLAP: int = 200      # Số ký tự chồng lấp giữa 2 chunk liên tiếp

    # ── Embedding Model ──────────────────────────────────────
    EMBEDDING_MODEL: str = "bkai-foundation-models/vietnamese-bi-encoder"

    # ── LLM (Generator) ─────────────────────────────────────
    LLM_MODEL: str = "gemini-3.1-flash-lite-preview"

    # ── Vector Database (Qdrant) ─────────────────────────────
    QDRANT_LOCATION: str = ":memory:"   # ":memory:" cho local test, URL cho production
    QDRANT_COLLECTION: str = "rag_philosophy"
    TOP_K_RESULTS: int = 3          # Số kết quả trả về khi truy xuất

    # ── Đường dẫn dữ liệu ───────────────────────────────────
    DATA_DIR: str = str(Path(__file__).resolve().parent.parent / "data")

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
            f"  CHUNK_SIZE={self.CHUNK_SIZE},\n"
            f"  CHUNK_OVERLAP={self.CHUNK_OVERLAP},\n"
            f"  EMBEDDING_MODEL='{self.EMBEDDING_MODEL}',\n"
            f"  LLM_MODEL='{self.LLM_MODEL}',\n"
            f"  QDRANT_LOCATION='{self.QDRANT_LOCATION}',\n"
            f"  QDRANT_COLLECTION='{self.QDRANT_COLLECTION}',\n"
            f"  DATA_DIR='{self.DATA_DIR}'\n"
            f")"
        )

