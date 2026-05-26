from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    database_url: str
    app_env: str
    redis_broker_url: str
    redis_result_backend: str
    celery_ingest_queue: str
    celery_max_retries: int
    celery_retry_backoff_max: int
    sync_ingest_when_queue_idle: bool
    pipeline_version: str
    service_name: str
    api_service_name: str
    object_storage_backend: str
    object_storage_local_root: str
    minio_endpoint: Optional[str]
    minio_access_key: Optional[str]
    minio_secret_key: Optional[str]
    minio_secure: bool
    minio_bucket: Optional[str]
    qdrant_url: Optional[str]
    qdrant_host: str
    qdrant_port: int
    qdrant_api_key: Optional[str]
    qdrant_collection: str
    max_pdf_size_mb: int
    retrieval_mode: str
    retrieval_top_k: int
    embedding_service_url: str
    embedding_query_timeout_seconds: float
    embedding_query_retries: int
    embedding_batch_timeout_seconds: float
    embedding_batch_retries: int
    embedding_batch_size: int
    llm_mode: str
    local_llm_model: str
    local_llm_base_url: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_use_tls: bool
    email_from: str



def _parse_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}



_ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(dotenv_path=_ROOT_DIR / ".env", override=False)


def load_settings() -> Settings:
    project_root = Path(__file__).resolve().parents[3]
    default_storage_root = project_root / "data" / "object_store"

    pipeline_version = os.getenv("PIPELINE_VERSION", "1.0.0").strip() or "1.0.0"

    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite:///./rag_system.db"),
        app_env=os.getenv("APP_ENV", "development").strip().lower(),
        redis_broker_url=os.getenv("REDIS_BROKER_URL", "redis://localhost:6379/0"),
        redis_result_backend=os.getenv("REDIS_RESULT_BACKEND", "redis://localhost:6379/1"),
        celery_ingest_queue=os.getenv("CELERY_INGEST_QUEUE", "ingest"),
        celery_max_retries=int(os.getenv("CELERY_MAX_RETRIES", "5")),
        celery_retry_backoff_max=int(os.getenv("CELERY_RETRY_BACKOFF_MAX", "300")),
        sync_ingest_when_queue_idle=_parse_bool(os.getenv("SYNC_INGEST_WHEN_QUEUE_IDLE"), default=False),
        pipeline_version=pipeline_version,
        service_name=os.getenv("SERVICE_NAME", "ingest-worker").strip(),
        api_service_name=os.getenv("API_SERVICE_NAME", "backend-api").strip(),
        object_storage_backend=os.getenv("OBJECT_STORAGE_BACKEND", "local").strip().lower(),
        object_storage_local_root=os.getenv("OBJECT_STORAGE_LOCAL_ROOT", str(default_storage_root)),
        minio_endpoint=os.getenv("MINIO_ENDPOINT"),
        minio_access_key=os.getenv("MINIO_ACCESS_KEY"),
        minio_secret_key=os.getenv("MINIO_SECRET_KEY"),
        minio_secure=_parse_bool(os.getenv("MINIO_SECURE"), default=False),
        minio_bucket=os.getenv("MINIO_BUCKET"),
        qdrant_url=os.getenv("QDRANT_URL"),
        qdrant_host=os.getenv("QDRANT_HOST", "localhost"),
        qdrant_port=int(os.getenv("QDRANT_PORT", "6333")),
        qdrant_api_key=os.getenv("QDRANT_API_KEY"),
        qdrant_collection=os.getenv("QDRANT_COLLECTION", "rag_philosophy"),
        max_pdf_size_mb=int(os.getenv("MAX_PDF_SIZE_MB", "100")),
        retrieval_mode=os.getenv("RETRIEVAL_MODE", "dense").strip().lower(),
        retrieval_top_k=int(os.getenv("RETRIEVAL_TOP_K", "5")),
        embedding_service_url=os.getenv("EMBEDDING_SERVICE_URL", "http://localhost:8001").strip(),
        embedding_query_timeout_seconds=float(os.getenv("EMBEDDING_QUERY_TIMEOUT_SECONDS", "3.0")),
        embedding_query_retries=int(os.getenv("EMBEDDING_QUERY_RETRIES", "1")),
        embedding_batch_timeout_seconds=float(os.getenv("EMBEDDING_BATCH_TIMEOUT_SECONDS", "120.0")),
        embedding_batch_retries=int(os.getenv("EMBEDDING_BATCH_RETRIES", "2")),
        embedding_batch_size=int(os.getenv("EMBEDDING_BATCH_SIZE", "32")),
        llm_mode=os.getenv("LLM_MODE", "auto").strip().lower(),
        local_llm_model=os.getenv("LOCAL_LLM_MODEL", "llama3.1:8b").strip(),
        local_llm_base_url=os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:11434").strip(),
        smtp_host=os.getenv("SMTP_HOST", "").strip(),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER", "").strip(),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        smtp_use_tls=_parse_bool(os.getenv("SMTP_USE_TLS"), default=True),
        email_from=os.getenv("EMAIL_FROM", "").strip(),
    )


settings = load_settings()
