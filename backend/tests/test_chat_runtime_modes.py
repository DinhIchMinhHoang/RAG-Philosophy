from __future__ import annotations

import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from backend.app.services import chat_runtime
from backend.app.services.chat_runtime import ChatRuntimeService, RetrievedContext


class ChatRuntimeModeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ChatRuntimeService()
        self.contexts = [
            RetrievedContext(
                document_id="doc-1",
                chunk_id="chunk-1",
                doc_id="doc-key-1",
                source="s.pdf",
                page=1,
                score=0.8,
                snippet="snippet",
                text="context",
            )
        ]

    def test_answer_auto_fallback_to_local(self) -> None:
        fake_settings = SimpleNamespace(
            llm_mode="auto",
            retrieval_mode="dense",
            retrieval_top_k=5,
            qdrant_collection="rag",
            local_llm_base_url="http://localhost:11434",
            local_llm_model="llama3.1:8b",
        )

        with patch.object(chat_runtime, "settings", fake_settings), patch.object(
            self.service,
            "_invoke_provider",
            new=AsyncMock(side_effect=[RuntimeError("gemini unavailable"), "local answer"]),
        ) as invoke_mock:
            answer, provider = asyncio.run(self.service.answer("q", self.contexts))

        self.assertEqual(answer, "local answer")
        self.assertEqual(provider, "local")
        self.assertEqual(invoke_mock.await_count, 2)
        self.assertEqual(invoke_mock.await_args_list[0].args[0], "gemini")
        self.assertEqual(invoke_mock.await_args_list[1].args[0], "local")

    def test_retrieve_hybrid_calls_hybrid_path(self) -> None:
        fake_settings = SimpleNamespace(
            llm_mode="auto",
            retrieval_mode="hybrid",
            retrieval_top_k=5,
            qdrant_collection="rag",
            local_llm_base_url="http://localhost:11434",
            local_llm_model="llama3.1:8b",
        )

        with patch.object(chat_runtime, "settings", fake_settings), patch.object(
            self.service,
            "_retrieve_hybrid",
            return_value=self.contexts,
        ) as hybrid_mock:
            result = self.service.retrieve(db=object(), question="q", pipeline_version="1.0.0")

        self.assertEqual(result, self.contexts)
        hybrid_mock.assert_called_once()

    def test_citations_from_context_assigns_stable_ids_and_dedupes(self) -> None:
        duplicate = RetrievedContext(
            document_id="doc-1",
            chunk_id="chunk-1",
            doc_id="doc-key-1",
            source="s.pdf",
            page=1,
            score=0.7,
            snippet="duplicate",
            text="duplicate context",
        )
        second = RetrievedContext(
            document_id="doc-2",
            chunk_id="chunk-2",
            doc_id="doc-key-2",
            source="other.pdf",
            page=4,
            score=None,
            snippet="other",
            text="other context",
        )

        citations = self.service.citations_from_context([self.contexts[0], duplicate, second])

        self.assertEqual([item["citation_id"] for item in citations], ["C1", "C2"])
        self.assertEqual([item["rank"] for item in citations], [1, 2])
        self.assertEqual(citations[0]["source"], "s.pdf")
        self.assertEqual(citations[0]["page"], 1)
        self.assertEqual(citations[0]["doc_id"], "doc-key-1")
        self.assertEqual(citations[0]["chunk_id"], "chunk-1")

    def test_build_context_uses_citation_ids(self) -> None:
        context_text = self.service._build_context(self.contexts)

        self.assertIn("[C1] source=s.pdf page=1 doc_id=doc-key-1 chunk_id=chunk-1", context_text)
        self.assertNotIn("[Doc 1", context_text)

    def test_filter_citations_for_answer_keeps_only_used_markers(self) -> None:
        citations = [
            {"citation_id": "C1", "source": "one.pdf"},
            {"citation_id": "C2", "source": "two.pdf"},
            {"citation_id": "C3", "source": "three.pdf"},
        ]

        filtered = self.service.filter_citations_for_answer("Có ý A [C1]. Có ý C [C3].", citations)

        self.assertEqual([item["citation_id"] for item in filtered], ["C1", "C3"])

    def test_filter_citations_for_answer_does_not_guess_when_answer_has_no_markers(self) -> None:
        citations = [{"citation_id": "C1", "source": "one.pdf"}]

        self.assertEqual(self.service.filter_citations_for_answer("Không có marker.", citations), [])


if __name__ == "__main__":
    unittest.main()
