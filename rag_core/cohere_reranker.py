from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

import cohere

try:
    from .config import Config
    from .common.logging_utils import get_logger
except ImportError:  # pragma: no cover
    from config import Config
    from common.logging_utils import get_logger


logger = get_logger(__name__)


class RerankUnavailable(Exception):
    """Raised when Cohere rerank is not usable (fail-open)."""


@dataclass(frozen=True)
class CohereRerankResult:
    index: int
    relevance_score: float


class CohereReranker:
    def __init__(
        self,
        api_key: str | None = None,
        *,
        model: str | None = None,
        timeout_seconds: float | None = None,
        max_tokens_per_doc: int | None = None,
    ) -> None:
        self._api_key = (api_key if api_key is not None else Config.COHERE_API_KEY) or ""
        self._model = model if model is not None else Config.RERANK_MODEL
        self._timeout = timeout_seconds if timeout_seconds is not None else Config.RERANK_TIMEOUT_SECONDS
        self._max_tokens_per_doc = (
            max_tokens_per_doc if max_tokens_per_doc is not None else Config.RERANK_MAX_TOKENS_PER_DOC
        )

        # Fail-open: don't raise here; let caller decide.
        self._client: Optional[cohere.ClientV2] = None

    def _get_client(self) -> cohere.ClientV2:
        if self._client is not None:
            return self._client
        if not self._api_key:
            raise RerankUnavailable("COHERE_API_KEY is not set")
        self._client = cohere.ClientV2(api_key=self._api_key, timeout=self._timeout)
        return self._client

    def rerank(
        self,
        *,
        query: str,
        documents: Sequence[str],
        top_n: int | None = None,
    ) -> List[CohereRerankResult]:
        if not documents:
            return []
        try:
            client = self._get_client()
            resp = client.v2.rerank(
                model=self._model,
                query=query,
                documents=list(documents),
                top_n=top_n,
                max_tokens_per_doc=self._max_tokens_per_doc,
            )
            results = []
            for r in getattr(resp, "results", []) or []:
                results.append(
                    CohereRerankResult(
                        index=int(getattr(r, "index")),
                        relevance_score=float(getattr(r, "relevance_score")),
                    )
                )
            return results
        except RerankUnavailable:
            raise
        except Exception as e:
            # Fail-open: bubble a single typed exception.
            logger.warning("Cohere rerank unavailable (%s)", e)
            raise RerankUnavailable(str(e))
