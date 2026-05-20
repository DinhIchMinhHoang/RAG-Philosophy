import unittest
from unittest.mock import MagicMock, patch

from langchain_core.documents import Document
from langchain_core.stores import InMemoryStore

from rag_core.config import Config
from rag_core.rerank_retriever import ChildRerankParentRetriever


class _StubReranker:
    def __init__(self, order):
        self._order = order

    def rerank(self, *, query: str, documents, top_n=None):
        # Return objects with .index and .relevance_score
        class R:
            def __init__(self, idx, score):
                self.index = idx
                self.relevance_score = score

        return [R(i, 1.0) for i in self._order]


class _FailingReranker:
    def rerank(self, *, query: str, documents, top_n=None):
        raise Exception("boom")


class TestRerankRetriever(unittest.TestCase):
    def _make_parent_store(self):
        store = InMemoryStore()
        store.mset(
            [
                (
                    "a",
                    Document(page_content="parent a", metadata={"source": "a.pdf", "page": 1, "doc_id": "a"}),
                ),
                (
                    "b",
                    Document(page_content="parent b", metadata={"source": "b.pdf", "page": 2, "doc_id": "b"}),
                ),
                (
                    "c",
                    Document(page_content="parent c", metadata={"source": "c.pdf", "page": 3, "doc_id": "c"}),
                ),
            ]
        )
        return store

    def test_rerank_children_maps_to_parent_order_and_dedups(self):
        store = self._make_parent_store()

        dense_children = [
            Document(page_content="dense a1", metadata={"doc_id": "a", "source": "a.pdf", "page": 1}),
            Document(page_content="dense b1", metadata={"doc_id": "b", "source": "b.pdf", "page": 2}),
        ]
        sparse_children = [
            Document(page_content="sparse b2", metadata={"doc_id": "b", "source": "b.pdf", "page": 2}),
            Document(page_content="sparse c1", metadata={"doc_id": "c", "source": "c.pdf", "page": 3}),
        ]

        vectorstore = MagicMock(similarity_search=MagicMock(return_value=dense_children))
        bm25 = MagicMock(search=MagicMock(return_value=sparse_children))

        with patch.object(Config, "RERANK_CANDIDATE_K", 8):
            retriever = ChildRerankParentRetriever(
                vectorstore=vectorstore,
                docstore=store,
                bm25_index=bm25,
                reranker=_StubReranker(order=[1, 2, 0, 3]),
                final_parent_k=3,
            )

            results = retriever.invoke("q")

        # Rerank order refers to candidate child list; we expect parents deduped by doc_id
        self.assertEqual([d.metadata["doc_id"] for d in results], ["b", "c", "a"])
        for doc in results:
            self.assertEqual(set(doc.metadata.keys()), {"source", "page", "doc_id"})

    def test_fail_open_falls_back_to_baseline(self):
        store = self._make_parent_store()

        dense_children = [
            Document(page_content="dense a1", metadata={"doc_id": "a", "source": "a.pdf", "page": 1}),
            Document(page_content="dense b1", metadata={"doc_id": "b", "source": "b.pdf", "page": 2}),
        ]
        sparse_children = [
            Document(page_content="sparse c1", metadata={"doc_id": "c", "source": "c.pdf", "page": 3}),
        ]

        vectorstore = MagicMock(similarity_search=MagicMock(return_value=dense_children))
        bm25 = MagicMock(search=MagicMock(return_value=sparse_children))

        retriever = ChildRerankParentRetriever(
            vectorstore=vectorstore,
            docstore=store,
            bm25_index=bm25,
            reranker=_FailingReranker(),
            final_parent_k=3,
        )

        results = retriever.invoke("q")

        # Baseline uses dense+sparse RRF at parent doc_id level; with defaults dense weight dominates.
        self.assertEqual([d.metadata["doc_id"] for d in results], ["a", "b", "c"])


if __name__ == "__main__":
    unittest.main()
