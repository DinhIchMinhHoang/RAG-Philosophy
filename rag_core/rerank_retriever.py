from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Hashable, Iterable, List, Optional, Protocol, Sequence, Tuple, TypeVar, runtime_checkable

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict, Field

try:
    from .config import Config
    from .cohere_reranker import CohereReranker, RerankUnavailable
    from .common.logging_utils import get_logger
except ImportError:  # pragma: no cover
    from config import Config
    from cohere_reranker import CohereReranker, RerankUnavailable
    from common.logging_utils import get_logger


logger = get_logger(__name__)


def _child_key(doc: Document, id_key: str) -> Tuple[str, str]:
    return (str(doc.metadata.get(id_key, "")), doc.page_content or "")


TKey = TypeVar("TKey", bound=Hashable)


def _rrf_scores(items: Sequence[Document], *, id_fn, weight: float, rrf_k: int) -> Dict[TKey, float]:
    scores: Dict[TKey, float] = defaultdict(float)
    seen: set[TKey] = set()
    for rank, item in enumerate(items, start=1):
        key: TKey = id_fn(item)
        if not key or key in seen:
            continue
        seen.add(key)
        scores[key] += weight / (rrf_k + rank)
    return scores


def _dedup_keep_order(values: Iterable[str]) -> List[str]:
    out: List[str] = []
    seen: set[str] = set()
    for v in values:
        if not v or v in seen:
            continue
        seen.add(v)
        out.append(v)
    return out


@runtime_checkable
class Reranker(Protocol):
    def rerank(self, *, query: str, documents: Sequence[str], top_n: int | None = None) -> Sequence[Any]: ...


@runtime_checkable
class RerankResult(Protocol):
    index: int


class ChildRerankParentRetriever(BaseRetriever):
    """Retrieve child chunks, rerank with Cohere, then map to parent docs.

    This retriever always uses dense+BM25 candidate generation and returns
    parent-level documents from docstore.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    vectorstore: Any = Field(...)
    docstore: Any = Field(...)
    bm25_index: Any = Field(...)
    id_key: str = "doc_id"
    reranker: Optional[Reranker] = None
    final_parent_k: int = 3

    def _get_child_candidates(self, query: str) -> Tuple[List[Document], List[Document]]:
        dense_children: List[Document] = []
        sparse_children: List[Document] = []

        if self.vectorstore is not None:
            dense_children = list(self.vectorstore.similarity_search(query, k=Config.HYBRID_DENSE_K))
        if self.bm25_index is not None:
            sparse_children = list(self.bm25_index.search(query, k=Config.HYBRID_SPARSE_K))
        return dense_children, sparse_children

    def _baseline_parent_doc_ids(self, dense_children: Sequence[Document], sparse_children: Sequence[Document]) -> List[str]:
        dense_scores = _rrf_scores(
            dense_children,
            id_fn=lambda d: str(d.metadata.get(self.id_key, "")),
            weight=Config.HYBRID_DENSE_WEIGHT,
            rrf_k=Config.HYBRID_RRF_K,
        )
        sparse_scores = _rrf_scores(
            sparse_children,
            id_fn=lambda d: str(d.metadata.get(self.id_key, "")),
            weight=Config.HYBRID_SPARSE_WEIGHT,
            rrf_k=Config.HYBRID_RRF_K,
        )
        scores: Dict[str, float] = defaultdict(float)
        for k, v in dense_scores.items():
            scores[k] += v
        for k, v in sparse_scores.items():
            scores[k] += v

        ranked = [doc_id for doc_id, _ in sorted(scores.items(), key=lambda it: it[1], reverse=True)]
        return _dedup_keep_order(ranked)

    def _candidate_children_for_rerank(self, dense_children: Sequence[Document], sparse_children: Sequence[Document]) -> List[Document]:
        scores: Dict[Tuple[str, str], float] = defaultdict(float)
        child_by_key: Dict[Tuple[str, str], Document] = {}
        for child in dense_children:
            child_by_key.setdefault(_child_key(child, self.id_key), child)
        for child in sparse_children:
            child_by_key.setdefault(_child_key(child, self.id_key), child)

        for k, v in _rrf_scores(
            dense_children,
            id_fn=lambda d: _child_key(d, self.id_key),
            weight=Config.HYBRID_DENSE_WEIGHT,
            rrf_k=Config.HYBRID_RRF_K,
        ).items():
            scores[k] += v
        for k, v in _rrf_scores(
            sparse_children,
            id_fn=lambda d: _child_key(d, self.id_key),
            weight=Config.HYBRID_SPARSE_WEIGHT,
            rrf_k=Config.HYBRID_RRF_K,
        ).items():
            scores[k] += v

        ordered_keys = [k for k, _ in sorted(scores.items(), key=lambda it: (-it[1], it[0]))]

        out: List[Document] = []
        seen_child: set[Tuple[str, str]] = set()
        seen_parent: set[str] = set()

        for key in ordered_keys:
            doc = child_by_key.get(key)
            if doc is None:
                continue
            doc_id = str(doc.metadata.get(self.id_key, ""))
            if not doc_id or doc_id in seen_parent:
                continue
            if key in seen_child:
                continue
            seen_child.add(key)
            seen_parent.add(doc_id)
            out.append(doc)
            if len(out) >= Config.RERANK_CANDIDATE_K:
                return out

        for key in ordered_keys:
            doc = child_by_key.get(key)
            if doc is None or key in seen_child:
                continue
            seen_child.add(key)
            out.append(doc)
            if len(out) >= Config.RERANK_CANDIDATE_K:
                return out

        return out

    def _rerank_child_docs(self, query: str, child_docs: Sequence[Document]) -> Optional[List[Document]]:
        if not child_docs:
            return []
        rr = self.reranker
        if rr is None:
            rr = CohereReranker()

        try:
            texts = [d.page_content for d in child_docs]
            results = rr.rerank(query=query, documents=texts, top_n=min(len(texts), Config.RERANK_CANDIDATE_K))
            if not results:
                return list(child_docs)
            out: List[Document] = []
            for r in results:
                # Be defensive: reranker output is external/untrusted.
                if not isinstance(r, RerankResult) or not isinstance(getattr(r, "index", None), int):
                    raise ValueError("Invalid rerank result item: missing int 'index'")
                if 0 <= r.index < len(child_docs):
                    out.append(child_docs[r.index])
            return out
        except RerankUnavailable:
            return None
        except Exception:
            logger.exception("Child rerank failed; falling back to baseline ordering.")
            return None

    def _parents_from_doc_ids(self, doc_ids: Sequence[str]) -> List[Document]:
        if not doc_ids:
            return []
        parents = self.docstore.mget(list(doc_ids))
        return [p for p in parents if p is not None]

    def _get_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
        dense_children, sparse_children = self._get_child_candidates(query)

        baseline_parent_ids = self._baseline_parent_doc_ids(dense_children, sparse_children)
        candidate_children = self._candidate_children_for_rerank(dense_children, sparse_children)

        # Try rerank on child chunks.
        reranked_children = self._rerank_child_docs(query, candidate_children)
        if reranked_children is None:
            # Fail-open: baseline ordering only.
            final_ids = baseline_parent_ids
        else:
            reranked_ids = _dedup_keep_order([str(d.metadata.get(self.id_key, "")) for d in reranked_children])
            remainder = [i for i in baseline_parent_ids if i not in set(reranked_ids)]
            final_ids = reranked_ids + remainder

        parents = self._parents_from_doc_ids(final_ids)
        return parents[: self.final_parent_k]
