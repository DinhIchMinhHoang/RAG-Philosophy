from __future__ import annotations

import re
from collections import defaultdict
from typing import Any, Iterable, List, Sequence

try:
    from rank_bm25 import BM25Okapi
except ImportError:  # pragma: no cover
    class BM25Okapi:  # type: ignore
        def __init__(self, corpus):
            self.corpus = corpus

        def get_scores(self, query):
            query_set = set(query)
            return [sum(1 for token in doc if token in query_set) for doc in self.corpus]

        def get_top_n(self, query, documents, n=5):
            query_set = set(query)
            scored = []
            for idx, doc in enumerate(self.corpus):
                score = sum(1 for token in doc if token in query_set)
                if score > 0:
                    scored.append((score, -idx, documents[idx]))
            scored.sort(reverse=True)
            return [doc for _, _, doc in scored[:n]]

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.stores import InMemoryStore
from pydantic import ConfigDict, Field

try:
    from .config import Config
except ImportError:  # pragma: no cover
    from config import Config

_TOKEN_PATTERN = re.compile(r"\w+")


def tokenize_text(text: str, min_token_len: int | None = None) -> List[str]:
    min_len = Config.SPARSE_MIN_TOKEN_LEN if min_token_len is None else min_token_len
    return [t for t in _TOKEN_PATTERN.findall((text or "").lower()) if len(t) >= min_len]


class BM25ChildIndex:
    def __init__(self, child_docs: Sequence[Document]):
        self.child_docs = list(child_docs)
        self.tokenized_docs = [tokenize_text(doc.page_content) for doc in self.child_docs]
        self._bm25 = BM25Okapi(self.tokenized_docs) if self.child_docs else None

    @classmethod
    def from_documents(cls, child_docs: Sequence[Document]) -> "BM25ChildIndex":
        return cls(child_docs)

    def search(self, query: str, k: int) -> List[Document]:
        if not self._bm25 or not self.child_docs:
            return []
        query_tokens = tokenize_text(query)
        if not query_tokens:
            return []

        scores = list(self._bm25.get_scores(query_tokens))
        if scores and max(scores) > 0:
            ranked_indices = [
                idx
                for idx, score in sorted(
                    enumerate(scores),
                    key=lambda item: (-item[1], item[0]),
                )
                if score > 0
            ]
            return [self.child_docs[idx] for idx in ranked_indices[:k]]

        query_set = set(query_tokens)
        scored: List[tuple[int, int]] = []
        for idx, doc_tokens in enumerate(self.tokenized_docs):
            overlap = sum(1 for t in doc_tokens if t in query_set)
            if overlap > 0:
                scored.append((overlap, idx))
        scored.sort(key=lambda it: (-it[0], it[1]))
        return [self.child_docs[idx] for _, idx in scored[:k]]


class HybridParentRetriever(BaseRetriever):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    vectorstore: Any = Field(...)
    docstore: Any = Field(...)
    bm25_index: Any = Field(...)
    id_key: str = "doc_id"

    def _get_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
        dense_children = []
        sparse_children = []

        if self.vectorstore is not None:
            dense_children = list(self.vectorstore.similarity_search(query, k=Config.HYBRID_DENSE_K))
        if self.bm25_index is not None:
            sparse_children = self.bm25_index.search(query, k=Config.HYBRID_SPARSE_K)

        scores: dict[str, float] = defaultdict(float)

        def add_ranks(children: Iterable[Document], weight: float) -> None:
            seen: set[str] = set()
            for rank, child in enumerate(children, start=1):
                doc_id = child.metadata.get(self.id_key)
                if not doc_id or doc_id in seen:
                    continue
                seen.add(doc_id)
                scores[doc_id] += weight / (Config.HYBRID_RRF_K + rank)

        add_ranks(dense_children, Config.HYBRID_DENSE_WEIGHT)
        add_ranks(sparse_children, Config.HYBRID_SPARSE_WEIGHT)

        ranked_doc_ids = [doc_id for doc_id, _ in sorted(scores.items(), key=lambda item: item[1], reverse=True)[: Config.HYBRID_FINAL_K]]
        if not ranked_doc_ids:
            return []

        docs = self.docstore.mget(ranked_doc_ids)
        return [doc for doc in docs if doc is not None]
