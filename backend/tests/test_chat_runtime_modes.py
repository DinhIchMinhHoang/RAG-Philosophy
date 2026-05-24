from __future__ import annotations

import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app import models
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

    def test_retrieve_filters_parent_chunks_by_owner_without_notebook(self) -> None:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        models.Base.metadata.create_all(engine)
        db = SessionLocal()
        try:
            db.add_all(
                [
                    models.DocumentChunk(
                        id="parent-1",
                        document_id="doc-1",
                        owner_id=1,
                        notebook_id=None,
                        kind="parent",
                        parent_chunk_id=None,
                        chunk_order=0,
                        text="allowed context",
                        source="allowed.pdf",
                        page=1,
                        doc_id="allowed",
                        pipeline_version="1.0.0",
                    ),
                    models.DocumentChunk(
                        id="parent-2",
                        document_id="doc-2",
                        owner_id=2,
                        notebook_id=None,
                        kind="parent",
                        parent_chunk_id=None,
                        chunk_order=0,
                        text="leaked context",
                        source="leaked.pdf",
                        page=1,
                        doc_id="leaked",
                        pipeline_version="1.0.0",
                    ),
                ]
            )
            db.commit()

            fake_hits = [
                SimpleNamespace(
                    score=0.9,
                    payload={"parent_chunk_id": "parent-1", "document_id": "doc-1"},
                ),
                SimpleNamespace(
                    score=0.8,
                    payload={"parent_chunk_id": "parent-2", "document_id": "doc-2"},
                ),
            ]

            class FakeClient:
                def __init__(self) -> None:
                    self.query_filter = None

                def search(self, **kwargs):
                    self.query_filter = kwargs.get("query_filter")
                    return fake_hits

            fake_client = FakeClient()

            with patch.object(self.service, "_get_embeddings", return_value=SimpleNamespace(embed_query=lambda _q: [0.1])), patch.object(
                chat_runtime, "build_qdrant_client", return_value=fake_client
            ):
                results = self.service.retrieve(
                    db=db,
                    question="q",
                    pipeline_version="1.0.0",
                    user_id=1,
                    notebook_id=None,
                )

            self.assertEqual([item.document_id for item in results], ["doc-1"])
            self.assertEqual(results[0].source, "allowed.pdf")
            self.assertIn("owner_id", repr(fake_client.query_filter))
            self.assertNotIn("notebook_id", repr(fake_client.query_filter))
        finally:
            db.close()
            engine.dispose()

    def test_retrieve_uses_document_filename_for_citation_source(self) -> None:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        models.Base.metadata.create_all(engine)
        db = SessionLocal()
        try:
            db.add(
                models.DocumentRecord(
                    id="doc-1",
                    owner_id=1,
                    notebook_id=7,
                    filename="original-name.pdf",
                    object_key="doc-1/original-name.pdf",
                    mime_type="application/pdf",
                    size_bytes=12,
                )
            )
            db.add(
                models.DocumentChunk(
                    id="parent-1",
                    document_id="doc-1",
                    owner_id=1,
                    notebook_id=7,
                    kind="parent",
                    parent_chunk_id=None,
                    chunk_order=0,
                    text="allowed context",
                    source="tmpabc123.pdf",
                    page=2,
                    doc_id="doc-key",
                    pipeline_version="1.0.0",
                )
            )
            db.commit()

            fake_hits = [
                SimpleNamespace(
                    score=0.9,
                    payload={"parent_chunk_id": "parent-1", "document_id": "doc-1"},
                )
            ]

            class FakeClient:
                def search(self, **kwargs):
                    return fake_hits

            with patch.object(self.service, "_get_embeddings", return_value=SimpleNamespace(embed_query=lambda _q: [0.1])), patch.object(
                chat_runtime, "build_qdrant_client", return_value=FakeClient()
            ):
                results = self.service.retrieve(
                    db=db,
                    question="q",
                    pipeline_version="1.0.0",
                    user_id=1,
                    notebook_id=7,
                )

            self.assertEqual(results[0].source, "original-name.pdf")
            self.assertEqual(results[0].page, 2)
        finally:
            db.close()
            engine.dispose()

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

    def test_grouped_citation_markers_are_normalized_to_one_marker(self) -> None:
        citations = [
            {"citation_id": "C1", "source": "one.pdf"},
            {"citation_id": "C2", "source": "two.pdf"},
            {"citation_id": "C5", "source": "five.pdf"},
        ]

        answer = "Phu thuoc ngan han [C2, C5]. Ket luan khac [C1, C5]."
        normalized = self.service.normalize_citation_markers(answer, citations)
        filtered = self.service.filter_citations_for_answer(normalized, citations)

        self.assertEqual(normalized, "Phu thuoc ngan han [C2]. Ket luan khac [C1].")
        self.assertEqual([item["citation_id"] for item in filtered], ["C1", "C2"])

    def test_filter_citations_for_answer_does_not_guess_when_answer_has_no_markers(self) -> None:
        citations = [{"citation_id": "C1", "source": "one.pdf"}]

        self.assertEqual(self.service.filter_citations_for_answer("Không có marker.", citations), [])

    def test_answer_falls_back_to_local_llm_when_primary_fails_before_tokens(self) -> None:
        fake_settings = SimpleNamespace(
            llm_mode="gemini",
            retrieval_mode="dense",
            retrieval_top_k=5,
            qdrant_collection="rag",
            local_llm_base_url="http://localhost:11434",
            local_llm_model="llama3.1:8b",
        )

        with patch.object(chat_runtime, "settings", fake_settings), patch.object(
            self.service,
            "_append_excel_context",
            return_value="[Excel Query Result — không có citation marker]\n| Số lượng |\n| --- |\n| 3 |",
        ), patch.object(
            self.service,
            "_invoke_provider",
            new=AsyncMock(side_effect=[RuntimeError("llm down"), "LLM diễn đạt tự nhiên"]),
        ):
            answer, provider = asyncio.run(self.service.answer("q", self.contexts))

        self.assertEqual(provider, "local")
        self.assertEqual(answer, "LLM diễn đạt tự nhiên")

    def test_stream_falls_back_to_local_llm_when_primary_fails_before_tokens(self) -> None:
        fake_settings = SimpleNamespace(
            llm_mode="gemini",
            retrieval_mode="dense",
            retrieval_top_k=5,
            qdrant_collection="rag",
            local_llm_base_url="http://localhost:11434",
            local_llm_model="llama3.1:8b",
        )

        async def collect():
            chunks = []
            async for token in self.service.stream_answer("q", self.contexts):
                chunks.append(token)
            return chunks

        with patch.object(chat_runtime, "settings", fake_settings), patch.object(
            self.service,
            "_append_excel_context",
            return_value="[Excel Query Result — không có citation marker]\n| Số lượng |\n| --- |\n| 3 |",
        ), patch.object(
            self.service,
            "_stream_provider",
            side_effect=RuntimeError("llm down"),
        ), patch.object(
            self.service,
            "_invoke_provider",
            new=AsyncMock(return_value="LLM diễn đạt tự nhiên"),
        ):
            chunks = asyncio.run(collect())

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], "LLM diễn đạt tự nhiên")


if __name__ == "__main__":
    unittest.main()
