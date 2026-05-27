from __future__ import annotations

import unittest
import uuid
from unittest.mock import patch

from langchain_core.documents import Document
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app.ingest import processor
from backend.app.models import DocumentRecord, IngestJob


class IngestProcessorRetryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

        self.document = DocumentRecord(
            id=str(uuid.uuid4()),
            filename="test.pdf",
            object_key="test/test.pdf",
            mime_type="application/pdf",
            size_bytes=123,
        )
        self.session.add(self.document)
        self.session.commit()

        self.job = IngestJob(
            id=str(uuid.uuid4()),
            document_id=self.document.id,
            status="queued",
            stage="embedding",
            progress_pct=75,
            stage_detail="retrying_after_error: timeout",
            error_message="temporary outage",
            pipeline_version="1.0.0",
        )
        self.session.add(self.job)
        self.session.commit()

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_retry_restarts_existing_job_from_fetch_stage(self) -> None:
        with patch.object(
            processor.storage_client,
            "get_bytes",
            side_effect=OSError("temporary storage outage"),
        ):
            with self.assertRaisesRegex(OSError, "temporary storage outage"):
                processor.run_ingest_job(
                    self.session,
                    job_id=self.job.id,
                    document_id=self.document.id,
                    object_key=self.document.object_key,
                    pipeline_version="1.0.1",
                )

        self.session.expire_all()
        job = self.session.query(IngestJob).filter(IngestJob.id == self.job.id).first()

        self.assertIsNotNone(job)
        self.assertEqual(job.status, "running")
        self.assertEqual(job.stage, "fetching_object")
        self.assertEqual(job.progress_pct, 1)
        self.assertEqual(job.stage_detail, "fetch_started")
        self.assertIsNone(job.error_message)
        self.assertEqual(job.pipeline_version, "1.0.1")

    def test_chunk_drafts_strip_nul_characters_before_persistence(self) -> None:
        parent_doc = Document(
            page_content="parent\x00 text",
            metadata={"source": "test\x00.pdf", "page": 1, "doc_id": "doc\x00-a"},
        )
        child_doc = Document(
            page_content="child\x00 text",
            metadata={"source": "test\x00.pdf", "page": 1, "doc_id": "doc\x00-a"},
        )

        parent_drafts, child_drafts = processor._build_chunk_drafts(
            document_id=self.document.id,
            owner_id=None,
            notebook_id=None,
            job_id=self.job.id,
            pipeline_version="1.0.0",
            parent_docs=[parent_doc],
            child_docs=[child_doc],
        )

        for draft in parent_drafts + child_drafts:
            self.assertNotIn("\x00", draft.text)
            self.assertNotIn("\x00", draft.source)
            self.assertNotIn("\x00", draft.doc_id)
        self.assertEqual(parent_drafts[0].text, "parent text")
        self.assertEqual(child_drafts[0].text, "child text")
        self.assertEqual(parent_drafts[0].source, "test.pdf")
        self.assertEqual(parent_drafts[0].doc_id, "doc-a")

    def test_pdf_parse_forwards_progress_callback(self) -> None:
        callback = object()

        with patch.object(processor, "HybridPDFParser") as parser_cls:
            parser = parser_cls.return_value
            parser.parse_pdf.return_value = []

            result = processor._run_pdf_parse("tmp.pdf", progress_callback=callback)

        self.assertEqual(result, [])
        parser.parse_pdf.assert_called_once_with("tmp.pdf", progress_callback=callback)


if __name__ == "__main__":
    unittest.main()
