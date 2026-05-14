from __future__ import annotations

from sqlalchemy import text

from ..core.settings import settings
from ..database import SessionLocal
from .qdrant_store import build_qdrant_client



def validate_worker_environment() -> None:
    if not settings.redis_broker_url:
        raise RuntimeError("REDIS_BROKER_URL is required")
    if not settings.redis_result_backend:
        raise RuntimeError("REDIS_RESULT_BACKEND is required")
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required")
    if not settings.pipeline_version:
        raise RuntimeError("PIPELINE_VERSION is required")
    if settings.object_storage_backend not in {"local", "minio"}:
        raise RuntimeError("OBJECT_STORAGE_BACKEND must be local or minio")

    try:
        from rag_core.config import Config as RagConfig
    except Exception as exc:
        raise RuntimeError(f"Failed to load rag_core config: {exc}") from exc

    if not RagConfig.EMBEDDING_MODEL_NAME:
        raise RuntimeError("EMBEDDING_MODEL_NAME is required")

    # Validate DB connectivity eagerly to fail fast at worker startup.
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
    finally:
        db.close()

    # Validate Qdrant connectivity and collection metadata endpoint.
    client = build_qdrant_client()
    try:
        client.get_collections()
    except Exception as exc:
        raise RuntimeError(f"Qdrant connectivity check failed: {exc}") from exc
