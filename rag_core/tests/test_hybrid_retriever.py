import unittest
from unittest.mock import MagicMock, patch

try:
    from . import _bootstrap  # noqa: F401
except ImportError:  # pragma: no cover
    import _bootstrap  # noqa: F401

from langchain_core.documents import Document
from langchain_core.stores import InMemoryStore

from rag_core.config import Config
from rag_core.hybrid_retriever import BM25ChildIndex, HybridParentRetriever, tokenize_text
from rag_core import step3_vector_db
from rag_core.step3_vector_db import build_vector_db


class TestHybridRetriever(unittest.TestCase):
    def test_tokenizer_filters_short_tokens(self):
        self.assertEqual(tokenize_text("A bc! d2 1e foo-bar"), ["bc", "d2", "1e", "foo", "bar"])

    def test_bm25_search_returns_match(self):
        docs = [
            Document(page_content="philosophy ethics logic", metadata={"doc_id": "a", "source": "s1", "page": 1}),
            Document(page_content="biology chemistry", metadata={"doc_id": "b", "source": "s2", "page": 2}),
        ]
        index = BM25ChildIndex.from_documents(docs)
        results = index.search("logic philosophy", k=2)
        self.assertEqual([doc.metadata["doc_id"] for doc in results], ["a"])

    def test_hybrid_retriever_dedup_and_metadata(self):
        parents = {
            "a": Document(page_content="parent a", metadata={"source": "a.pdf", "page": 1, "doc_id": "a"}),
            "b": Document(page_content="parent b", metadata={"source": "b.pdf", "page": 2, "doc_id": "b"}),
            "c": Document(page_content="parent c", metadata={"source": "c.pdf", "page": 3, "doc_id": "c"}),
        }
        store = InMemoryStore()
        store.mset(list(parents.items()))

        dense_children = [
            Document(page_content="dense a1", metadata={"doc_id": "a", "source": "a.pdf", "page": 1}),
            Document(page_content="dense a2", metadata={"doc_id": "a", "source": "a.pdf", "page": 1}),
            Document(page_content="dense b1", metadata={"doc_id": "b", "source": "b.pdf", "page": 2}),
        ]
        sparse_children = [
            Document(page_content="sparse b1", metadata={"doc_id": "b", "source": "b.pdf", "page": 2}),
            Document(page_content="sparse c1", metadata={"doc_id": "c", "source": "c.pdf", "page": 3}),
            Document(page_content="sparse c2", metadata={"doc_id": "c", "source": "c.pdf", "page": 3}),
        ]

        vectorstore = MagicMock()
        vectorstore.similarity_search.return_value = dense_children
        bm25_index = MagicMock()
        bm25_index.search.return_value = sparse_children

        retriever = HybridParentRetriever(vectorstore=vectorstore, docstore=store, bm25_index=bm25_index)
        results = retriever.invoke("test query")

        self.assertEqual([doc.metadata["doc_id"] for doc in results], ["b", "a", "c"])
        for doc in results:
            self.assertEqual(set(doc.metadata.keys()), {"source", "page", "doc_id"})

    def test_hybrid_retriever_handles_empty_candidates(self):
        retriever = HybridParentRetriever(
            vectorstore=MagicMock(similarity_search=MagicMock(return_value=[])),
            docstore=InMemoryStore(),
            bm25_index=MagicMock(search=MagicMock(return_value=[])),
        )
        self.assertEqual(retriever.invoke("nothing"), [])

    @patch("rag_core.step3_vector_db.QdrantVectorStore.from_documents")
    @patch("rag_core.step3_vector_db._init_embeddings")
    def test_qdrant_store_uses_config_location(self, mock_init, mock_from_documents):
        mock_init.return_value = MagicMock()
        child_docs = [Document(page_content="child", metadata={"doc_id": "x", "source": "s", "page": 1})]

        step3_vector_db._build_qdrant_store(child_docs, mock_init.return_value, ids=["point-1"])

        _, kwargs = mock_from_documents.call_args
        self.assertEqual(kwargs["location"], Config.QDRANT_LOCATION)
        self.assertEqual(kwargs["ids"], ["point-1"])

    def test_build_vector_db_rejects_child_docs_missing_doc_id(self):
        child_docs = [Document(page_content="child", metadata={"source": "s", "page": 1})]
        parent_docs = [Document(page_content="parent", metadata={"doc_id": "x", "source": "s", "page": 1})]

        with self.assertRaises(KeyError):
            build_vector_db(child_docs, parent_docs)

    @patch("rag_core.step3_vector_db._build_doc_store")
    @patch("rag_core.step3_vector_db._build_qdrant_store")
    @patch("rag_core.step3_vector_db._init_embeddings")
    def test_build_vector_db_switches_to_hybrid(self, mock_init, mock_build_qdrant, mock_build_store):
        mock_init.return_value = MagicMock()
        mock_build_qdrant.return_value = MagicMock()
        mock_build_store.return_value = InMemoryStore()

        child_docs = [Document(page_content="child", metadata={"doc_id": "x", "source": "s", "page": 1, "_child_point_id": "point-1"})]
        parent_docs = [Document(page_content="parent", metadata={"doc_id": "x", "source": "s", "page": 1})]

        with patch.object(Config, "HYBRID_ENABLED", True):
            retriever = build_vector_db(child_docs, parent_docs)

        self.assertIsInstance(retriever, HybridParentRetriever)


if __name__ == "__main__":
    unittest.main()
