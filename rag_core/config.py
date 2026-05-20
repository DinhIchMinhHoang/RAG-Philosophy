from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

_ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=_ROOT_DIR / ".env")

DEFAULT_LLM_MODEL = "gemini-2.5-flash"


class Config:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    OPENCODE_API_KEY: str = os.getenv("OPENCODE_API_KEY", "")
    OPENCODE_API_BASE: str = os.getenv("OPENCODE_API_BASE", "https://opencode.ai/zen/go/v1")
    OPENCODE_MODEL: str = os.getenv("OPENCODE_MODEL", "deepseek-v4-flash")
    RAGAS_MAX_CONCURRENCY: int = int(os.getenv("RAGAS_MAX_CONCURRENCY", "5"))

    PARENT_CHUNK_SIZE: int = 2000
    PARENT_CHUNK_OVERLAP: int = 200
    CHILD_CHUNK_SIZE: int = 500
    CHILD_CHUNK_OVERLAP: int = 100

    EMBEDDING_MODEL_NAME: str = "microsoft/harrier-oss-v1-270m"
    DEVICE: str = "cpu"
    LLM_MODEL: str = (os.getenv("LLM_MODEL") or DEFAULT_LLM_MODEL).strip()
    LLM_PROVIDER: str = (os.getenv("LLM_PROVIDER") or "auto").strip().lower()

    QDRANT_LOCATION: str = ":memory:"
    QDRANT_COLLECTION: str = "rag_philosophy"
    TOP_K_RESULTS: int = 3

    HYBRID_ENABLED: bool = False
    HYBRID_FINAL_K: int = 3
    HYBRID_DENSE_K: int = 5
    HYBRID_SPARSE_K: int = 10
    HYBRID_RRF_K: int = 60
    HYBRID_DENSE_WEIGHT: float = 0.7
    HYBRID_SPARSE_WEIGHT: float = 0.3
    SPARSE_MIN_TOKEN_LEN: int = 2

    # Cohere reranking (fail-open): rerank child chunks then map to parent docs.
    # When enabled, retrieval always uses dense+BM25 candidate merge.
    RERANK_ENABLED: bool = False
    RERANK_MODEL: str = os.getenv("RERANK_MODEL", "rerank-v4.0-fast")
    RERANK_CANDIDATE_K: int = int(os.getenv("RERANK_CANDIDATE_K", "8"))
    RERANK_TIMEOUT_SECONDS: float = float(os.getenv("RERANK_TIMEOUT_SECONDS", "2.0"))
    RERANK_MAX_TOKENS_PER_DOC: int = int(os.getenv("RERANK_MAX_TOKENS_PER_DOC", "1024"))

    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL_NAME: str = "glm-ocr"
    OLLAMA_MAX_WORKERS: int = 5
    DPI_FOR_OCR: int = 150
    VLM_TIMEOUT_SECONDS: int = 60
    MAX_IMAGE_LONG_EDGE: int = 1500

    _DATA_ROOT: Path = Path(__file__).resolve().parent.parent / "data"
    DATA_DIR: str = str(_DATA_ROOT)
    RAW_DIR: str = str(_DATA_ROOT / "raw")
    PROCESSED_DIR: str = str(_DATA_ROOT / "processed")
    QDRANT_PATH: str = str(_DATA_ROOT / "stores" / "qdrant")
    DOC_STORE_DIR: str = str(_DATA_ROOT / "stores" / "doc_store")

    @classmethod
    def validate(cls) -> None:
        model = (cls.LLM_MODEL or DEFAULT_LLM_MODEL).strip()
        provider = (cls.LLM_PROVIDER or "auto").strip().lower()
        if provider == "auto":
            provider = "gemini" if model.lower().startswith("gemini") else "opencode"
        if provider == "gemini" and not cls.GEMINI_API_KEY:
            raise EnvironmentError("GEMINI_API_KEY is not set.")
        if provider == "opencode" and not cls.OPENCODE_API_KEY:
            raise EnvironmentError("OPENCODE_API_KEY is not set.")
