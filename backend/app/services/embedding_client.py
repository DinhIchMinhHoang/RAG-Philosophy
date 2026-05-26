from __future__ import annotations

import json
import logging
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from ..core.settings import settings

logger = logging.getLogger(__name__)


class EmbeddingServiceError(RuntimeError):
    """Base error for remote embedding failures."""


class EmbeddingServiceUnavailable(EmbeddingServiceError, ConnectionError):
    """Raised when the embedding service cannot be reached or returns 5xx."""


class EmbeddingServiceTimeout(EmbeddingServiceError, TimeoutError):
    """Raised when the embedding service request times out."""


@dataclass(frozen=True)
class EmbeddingServiceClient:
    base_url: str
    query_timeout_seconds: float
    query_retries: int
    batch_timeout_seconds: float
    batch_retries: int
    batch_size: int

    def embed_query(self, text: str) -> list[float]:
        payload = self._post_json(
            "/embed",
            {"text": text},
            timeout_seconds=self.query_timeout_seconds,
            retries=self.query_retries,
        )
        vector = payload.get("embedding")
        if not isinstance(vector, list):
            raise EmbeddingServiceError("Embedding service /embed response missing embedding vector")
        return [float(item) for item in vector]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        payload = self._post_json(
            "/embed-batch",
            {"texts": texts, "batch_size": self.batch_size},
            timeout_seconds=self.batch_timeout_seconds,
            retries=self.batch_retries,
        )
        vectors = payload.get("embeddings")
        if not isinstance(vectors, list):
            raise EmbeddingServiceError("Embedding service /embed-batch response missing embeddings")
        return [[float(item) for item in vector] for vector in vectors]

    def _post_json(
        self,
        path: str,
        payload: dict[str, Any],
        *,
        timeout_seconds: float,
        retries: int,
    ) -> dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}{path}"
        encoded = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=encoded,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        attempts = max(0, retries) + 1
        last_error: Exception | None = None

        for attempt in range(1, attempts + 1):
            started = time.perf_counter()
            try:
                with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                    raw = response.read()
                latency_ms = int((time.perf_counter() - started) * 1000)
                logger.info(
                    "embedding_service_request_completed path=%s attempt=%s latency_ms=%s",
                    path,
                    attempt,
                    latency_ms,
                )
                return json.loads(raw.decode("utf-8"))
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                message = f"Embedding service returned HTTP {exc.code} for {path}: {body[:500]}"
                last_error = exc
                if exc.code >= 500 and attempt < attempts:
                    logger.warning(
                        "embedding_service_http_retry path=%s status_code=%s attempt=%s error=%s",
                        path,
                        exc.code,
                        attempt,
                        message,
                    )
                    time.sleep(min(0.25 * attempt, 1.0))
                    continue
                if exc.code >= 500:
                    raise EmbeddingServiceUnavailable(message) from exc
                raise EmbeddingServiceError(message) from exc
            except (TimeoutError, socket.timeout) as exc:
                message = f"Embedding service timed out for {path} after {timeout_seconds}s"
                last_error = exc
                if attempt < attempts:
                    logger.warning("embedding_service_timeout_retry path=%s attempt=%s", path, attempt)
                    time.sleep(min(0.25 * attempt, 1.0))
                    continue
                raise EmbeddingServiceTimeout(message) from exc
            except urllib.error.URLError as exc:
                message = f"Embedding service unavailable for {path}: {exc.reason}"
                last_error = exc
                if attempt < attempts:
                    logger.warning(
                        "embedding_service_unavailable_retry path=%s attempt=%s error=%s",
                        path,
                        attempt,
                        exc.reason,
                    )
                    time.sleep(min(0.25 * attempt, 1.0))
                    continue
                raise EmbeddingServiceUnavailable(message) from exc
            except json.JSONDecodeError as exc:
                raise EmbeddingServiceError(f"Embedding service returned invalid JSON for {path}") from exc

        raise EmbeddingServiceUnavailable(f"Embedding service request failed for {path}: {last_error}")


def build_embedding_client() -> EmbeddingServiceClient:
    return EmbeddingServiceClient(
        base_url=settings.embedding_service_url,
        query_timeout_seconds=settings.embedding_query_timeout_seconds,
        query_retries=settings.embedding_query_retries,
        batch_timeout_seconds=settings.embedding_batch_timeout_seconds,
        batch_retries=settings.embedding_batch_retries,
        batch_size=settings.embedding_batch_size,
    )


def embed_query(text: str) -> list[float]:
    return build_embedding_client().embed_query(text)


def embed_texts(texts: list[str]) -> list[list[float]]:
    return build_embedding_client().embed_batch(texts)
