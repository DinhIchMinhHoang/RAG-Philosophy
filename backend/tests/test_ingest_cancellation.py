from __future__ import annotations

import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

from langchain_core.documents import Document
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app.ingest import processor
from backend.app.ingest.cancellation import IngestCancelled
from backend.app.models import DocumentRecord, IngestJob


class IngestCancellationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

        self.document = DocumentRecord(
            id=str(uuid.uuid4()),
            owner_id=1,
            filename="cancel.pdf",
            object_key="cancel/cancel.pdf",
            mime_type="application/pdf",
            size_bytes=123,
        )
        self.session.add(self.document)
        self.session.commit()

        self.job = IngestJob(
            id=str(uuid.uuid4()),
            document_id=self.document.id,
            status="queued",
            stage="fetching_object",
            progress_pct=0,
            pipeline_version="1.0.0",
        )
        self.session.add(self.job)
        self.session.commit()

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def _parent_child_docs(self) -> tuple[list[Document], list[Document]]:
        parent = Document(
            page_content="parent text",
            metadata={"source": "cancel.pdf", "page": 1, "doc_id": "doc-a"},
        )
        child = Document(
            page_content="child text",
            metadata={"source": "cancel.pdf", "page": 1, "doc_id": "doc-a"},
        )
        return [child], [parent]

    def _mark_delete_requested(self) -> None:
        doc = self.session.query(DocumentRecord).filter(DocumentRecord.id == self.document.id).first()
        self.assertIsNotNone(doc)
        doc.delete_requested_at = datetime.now(timezone.utc)
        self.session.add(doc)
        self.session.commit()

    def test_already_cancelled_job_exits_before_fetch(self) -> None:
        self.job.status = "cancelled"
        self.session.add(self.job)
        self.session.commit()

        with patch.object(processor.storage_client, "get_bytes", side_effect=AssertionError("fetch should not run")):
            with self.assertRaises(IngestCancelled):
                processor.run_ingest_job(
                    self.session,
                    job_id=self.job.id,
                    document_id=self.document.id,
                    object_key=self.document.object_key,
                    pipeline_version="1.0.0",
                )

    def test_missing_document_row_is_cancellation_not_fetch_failure(self) -> None:
        document_id = self.document.id
        object_key = self.document.object_key
        self.session.query(DocumentRecord).filter(DocumentRecord.id == self.document.id).delete(synchronize_session=False)
        self.session.commit()

        with patch.object(processor.storage_client, "get_bytes", side_effect=AssertionError("fetch should not run")):
            with self.assertRaises(IngestCancelled):
                processor.run_ingest_job(
                    self.session,
                    job_id=self.job.id,
                    document_id=document_id,
                    object_key=object_key,
                    pipeline_version="1.0.0",
                )

        job = self.session.query(IngestJob).filter(IngestJob.id == self.job.id).first()
        self.assertEqual(job.status, "cancelled")
        self.assertIsNotNone(job.finished_at)

    def test_cancellation_after_parsing_stops_before_chunking(self) -> None:
        self._mark_delete_requested()

        with patch.object(processor, "chunk_documents", side_effect=AssertionError("chunking should not run")):
            with self.assertRaises(IngestCancelled):
                processor._process_parsed_documents(
                    self.session,
                    job_id=self.job.id,
                    document_id=self.document.id,
                    pipeline_version="1.0.0",
                    parsed_pages=[
                        Document(
                            page_content="page text",
                            metadata={"source": "tmp.pdf", "page": 1, "doc_id": "doc-a"},
                        )
                    ],
                    updater=processor.JobUpdater(self.session),
                    total_started=0.0,
                )

    def test_cancellation_after_embedding_batch_skips_upsert(self) -> None:
        child_docs, parent_docs = self._parent_child_docs()

        def embed_and_cancel(_texts: list[str]) -> list[list[float]]:
            self._mark_delete_requested()
            return [[0.1, 0.2]]

        with patch.object(processor, "chunk_documents", return_value=(child_docs, parent_docs)), patch.object(
            processor, "build_qdrant_client", return_value=object()
        ), patch.object(processor, "delete_vectors_for_document_version", return_value=None), patch.object(
            processor, "embed_texts", side_effect=embed_and_cancel
        ), patch.object(processor, "upsert_child_vectors", side_effect=AssertionError("upsert should not run")):
            with self.assertRaises(IngestCancelled):
                processor._process_parsed_documents(
                    self.session,
                    job_id=self.job.id,
                    document_id=self.document.id,
                    pipeline_version="1.0.0",
                    parsed_pages=[
                        Document(
                            page_content="page text",
                            metadata={"source": "tmp.pdf", "page": 1, "doc_id": "doc-a"},
                        )
                    ],
                    updater=processor.JobUpdater(self.session),
                    total_started=0.0,
                )

    def test_cancellation_after_qdrant_upsert_deletes_vectors_and_skips_metadata(self) -> None:
        child_docs, parent_docs = self._parent_child_docs()

        def upsert_and_cancel(*_args, **_kwargs) -> None:
            self._mark_delete_requested()

        with patch.object(processor, "chunk_documents", return_value=(child_docs, parent_docs)), patch.object(
            processor, "build_qdrant_client", return_value=object()
        ), patch.object(processor, "delete_vectors_for_document_version", return_value=None), patch.object(
            processor, "embed_texts", return_value=[[0.1, 0.2]]
        ), patch.object(processor, "upsert_child_vectors", side_effect=upsert_and_cancel), patch.object(
            processor, "delete_vectors_for_document", return_value=None
        ) as delete_vectors:
            with self.assertRaises(IngestCancelled):
                processor._process_parsed_documents(
                    self.session,
                    job_id=self.job.id,
                    document_id=self.document.id,
                    pipeline_version="1.0.0",
                    parsed_pages=[
                        Document(
                            page_content="page text",
                            metadata={"source": "tmp.pdf", "page": 1, "doc_id": "doc-a"},
                        )
                    ],
                    updater=processor.JobUpdater(self.session),
                    total_started=0.0,
                )

        delete_vectors.assert_called()
        self.assertEqual(self.session.query(processor.DocumentChunk).count(), 0)


if __name__ == "__main__":
    unittest.main()
