from __future__ import annotations

import unittest
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app.ingest.job_updater import JobUpdater
from backend.app.models import DocumentRecord, IngestJob


class JobUpdaterTests(unittest.TestCase):
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
            stage="fetching_object",
            progress_pct=0,
            pipeline_version="1.0.0",
        )
        self.session.add(self.job)
        self.session.commit()

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_progress_is_monotonic(self) -> None:
        updater = JobUpdater(self.session)

        updater.set_state(self.job.id, status="running", stage="parsing", progress_pct=30)
        job = updater.set_state(self.job.id, progress_pct=10)

        self.assertEqual(job.progress_pct, 30)
        self.assertEqual(job.status, "running")

    def test_advance_stage_keeps_progress_monotonic_with_detail_updates(self) -> None:
        updater = JobUpdater(self.session)

        updater.advance_stage(self.job.id, "parsing", ratio=0.8, stage_detail="parsed_pages=8/10")
        job = updater.advance_stage(self.job.id, "parsing", ratio=0.2, stage_detail="parsed_pages=2/10")

        self.assertEqual(job.progress_pct, 30)
        self.assertEqual(job.stage_detail, "parsed_pages=2/10")

    def test_rejects_backward_stage(self) -> None:
        updater = JobUpdater(self.session)

        updater.set_state(self.job.id, stage="embedding")
        with self.assertRaises(ValueError):
            updater.set_state(self.job.id, stage="parsing")

    def test_start_run_can_restart_later_stage_for_retry(self) -> None:
        updater = JobUpdater(self.session)

        updater.set_state(
            self.job.id,
            status="queued",
            stage="embedding",
            progress_pct=75,
            stage_detail="retrying_after_error: timeout",
            error_message="temporary outage",
        )
        restarted = updater.start_run(self.job.id, pipeline_version="1.0.1")

        self.assertEqual(restarted.status, "running")
        self.assertEqual(restarted.stage, "fetching_object")
        self.assertEqual(restarted.progress_pct, 0)
        self.assertEqual(restarted.stage_detail, "starting")
        self.assertIsNone(restarted.error_message)
        self.assertEqual(restarted.pipeline_version, "1.0.1")
        self.assertIsNotNone(restarted.started_at)

    def test_fail_writes_terminal_fields(self) -> None:
        updater = JobUpdater(self.session)

        failed = updater.fail(self.job.id, "parser exploded")

        self.assertEqual(failed.status, "failed")
        self.assertEqual(failed.stage_detail, "ingest_failed")
        self.assertIn("parser exploded", failed.error_message)
        self.assertIsNotNone(failed.finished_at)


if __name__ == "__main__":
    unittest.main()
