from __future__ import annotations

import unittest
from importlib.util import find_spec
from unittest.mock import MagicMock, patch


class WorkerFailureHandlingTests(unittest.TestCase):
    @unittest.skipIf(find_spec("celery") is None, "celery is not installed in this Python environment")
    def test_mark_failed_rolls_back_failed_session_before_job_update(self) -> None:
        from backend.app.worker import tasks

        db = MagicMock()
        calls: list[str] = []
        db.rollback.side_effect = lambda: calls.append("rollback")

        updater = MagicMock()
        updater.fail.side_effect = lambda job_id, message: calls.append("fail")

        with patch.object(tasks, "JobUpdater", return_value=updater):
            tasks._mark_failed_after_exception(db, "job-1", RuntimeError("flush failed"))

        self.assertEqual(calls, ["rollback", "fail"])
        updater.fail.assert_called_once_with("job-1", "flush failed")

    @unittest.skipIf(find_spec("celery") is None, "celery is not installed in this Python environment")
    def test_exception_path_rechecks_cancellation_before_retry_or_failure(self) -> None:
        from backend.app.ingest.cancellation import IngestCancelled
        from backend.app.worker import tasks

        db = MagicMock()
        cancelled = IngestCancelled(
            job_id="job-1",
            document_id="doc-1",
            stage="exception",
            reason="document delete requested during ingest",
        )

        with patch.object(tasks, "assert_ingest_not_cancelled", side_effect=cancelled) as check:
            result = tasks._cancelled_after_exception(
                db,
                {"job_id": "job-1", "document_id": "doc-1"},
            )

        self.assertIs(result, cancelled)
        db.rollback.assert_called_once()
        check.assert_called_once()


if __name__ == "__main__":
    unittest.main()
