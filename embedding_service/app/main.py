from __future__ import annotations

import logging
import os
import threading
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("embedding_service")

NORMALIZE_EMBEDDINGS = True


@dataclass(frozen=True)
class EmbeddingSettings:
    model_name: str
    device: str
    batch_size: int
    warmup_text: str


@dataclass
class ModelState:
    model: SentenceTransformer | None = None
    ready: bool = False
    error: str | None = None
    dimension: int | None = None
    loaded_at: float | None = None


class EmbedRequest(BaseModel):
    text: str = Field(..., min_length=1)


class EmbedBatchRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1)
    batch_size: int | None = Field(default=None, ge=1)


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return int(raw)


def load_settings() -> EmbeddingSettings:
    return EmbeddingSettings(
        model_name=os.getenv("EMBEDDING_MODEL_NAME", "microsoft/harrier-oss-v1-270m").strip(),
        device=os.getenv("EMBEDDING_DEVICE", os.getenv("DEVICE", "cpu")).strip() or "cpu",
        batch_size=_int_env("EMBEDDING_BATCH_SIZE", 32),
        warmup_text=os.getenv("EMBEDDING_WARMUP_TEXT", "embedding warmup").strip() or "embedding warmup",
    )


settings = load_settings()
state = ModelState()
_encode_lock = threading.Lock()


def _as_vectors(value: Any) -> list[list[float]]:
    if hasattr(value, "tolist"):
        value = value.tolist()
    vectors = value if isinstance(value, list) else list(value)
    if not vectors:
        return []
    if vectors and vectors[0] and isinstance(vectors[0][0], (int, float)):
        return [[float(item) for item in vector] for vector in vectors]
    return [[float(item) for item in vectors]]


def _require_ready() -> SentenceTransformer:
    if state.model is None or not state.ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"ready": False, "error": state.error or "embedding model is not ready"},
        )
    return state.model


def _encode(texts: list[str], batch_size: int) -> list[list[float]]:
    model = _require_ready()
    started = time.perf_counter()
    try:
        with _encode_lock:
            vectors = model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=NORMALIZE_EMBEDDINGS,
            )
    except Exception:
        logger.exception("embedding_encode_failed text_count=%s batch_size=%s", len(texts), batch_size)
        raise
    latency_ms = int((time.perf_counter() - started) * 1000)
    logger.info(
        "embedding_encode_completed text_count=%s batch_size=%s latency_ms=%s",
        len(texts),
        batch_size,
        latency_ms,
    )
    return _as_vectors(vectors)


def load_model() -> None:
    started = time.perf_counter()
    logger.info(
        "embedding_model_load_started model=%s device=%s normalize_embeddings=%s",
        settings.model_name,
        settings.device,
        NORMALIZE_EMBEDDINGS,
    )
    try:
        model = SentenceTransformer(
            settings.model_name,
            device=settings.device,
            trust_remote_code=True,
        )
        with _encode_lock:
            warmup = model.encode(
                [settings.warmup_text],
                batch_size=1,
                normalize_embeddings=NORMALIZE_EMBEDDINGS,
            )
        warmup_vectors = _as_vectors(warmup)
        if not warmup_vectors or not warmup_vectors[0]:
            raise RuntimeError("embedding warmup returned an empty vector")
        state.model = model
        state.dimension = len(warmup_vectors[0])
        state.ready = True
        state.error = None
        state.loaded_at = time.time()
        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "embedding_model_ready model=%s dimension=%s device=%s normalize_embeddings=%s load_ms=%s",
            settings.model_name,
            state.dimension,
            settings.device,
            NORMALIZE_EMBEDDINGS,
            latency_ms,
        )
    except Exception as exc:
        state.ready = False
        state.error = str(exc)
        logger.exception("embedding_model_load_failed model=%s", settings.model_name)
        raise


@asynccontextmanager
async def lifespan(_: FastAPI):
    load_model()
    yield


app = FastAPI(title="RAG Embedding Service", lifespan=lifespan)


@app.middleware("http")
async def log_request_latency(request: Request, call_next):
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.exception(
            "embedding_request_failed method=%s path=%s latency_ms=%s",
            request.method,
            request.url.path,
            latency_ms,
        )
        raise
    latency_ms = int((time.perf_counter() - started) * 1000)
    logger.info(
        "embedding_request_completed method=%s path=%s status_code=%s latency_ms=%s",
        request.method,
        request.url.path,
        response.status_code,
        latency_ms,
    )
    return response


@app.get("/health")
def health(response: Response) -> dict[str, object]:
    payload: dict[str, object] = {"ready": state.ready}
    if state.error:
        payload["error"] = state.error
    if not state.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return payload


@app.get("/info")
def info() -> dict[str, object]:
    _require_ready()
    return {
        "model_name": settings.model_name,
        "embedding_dimension": state.dimension,
        "device": settings.device,
        "normalize_embeddings": NORMALIZE_EMBEDDINGS,
        "batch_size": settings.batch_size,
    }


@app.post("/embed")
def embed(payload: EmbedRequest) -> dict[str, object]:
    logger.info("embedding_embed_requested text_count=1 batch_size=1")
    vectors = _encode([payload.text], batch_size=1)
    return {
        "model_name": settings.model_name,
        "embedding_dimension": len(vectors[0]),
        "embedding": vectors[0],
    }


@app.post("/embed-batch")
def embed_batch(payload: EmbedBatchRequest) -> dict[str, object]:
    batch_size = payload.batch_size or settings.batch_size
    logger.info(
        "embedding_embed_batch_requested text_count=%s batch_size=%s",
        len(payload.texts),
        batch_size,
    )
    vectors = _encode(payload.texts, batch_size=batch_size)
    return {
        "model_name": settings.model_name,
        "embedding_dimension": len(vectors[0]) if vectors else state.dimension,
        "embeddings": vectors,
    }
