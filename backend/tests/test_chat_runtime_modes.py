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


if __name__ == "__main__":
    unittest.main()
