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

    def test_parsed_page_sources_use_original_filename(self) -> None:
        pages = [
            Document(page_content="one", metadata={"source": "tmpabc.pdf", "page": 1}),
            Document(page_content="two", metadata={"source": "tmpabc.pdf", "page": 2}),
        ]

        processor._normalize_parsed_page_sources(pages, "original.pdf")

        self.assertEqual([page.metadata["source"] for page in pages], ["original.pdf", "original.pdf"])


if __name__ == "__main__":
    unittest.main()
