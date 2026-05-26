from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models import DocumentRecord, IngestJob, JobStatus
from .logging_utils import log_event


@dataclass
class IngestCancelled(Exception):
    job_id: str
    document_id: str
    stage: str
    reason: str
    skipped_chunks: int = 0
    skipped_batches: int = 0

    def __str__(self) -> str:
        return self.reason


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def mark_job_cancelled(
    db: Session,
    job_id: str,
    *,
    stage_detail: str = "ingest_cancelled",
) -> IngestJob | None:
    job = db.query(IngestJob).filter(IngestJob.id == job_id).first()
    if job is None:
        db.rollback()
        return None

    now = _utc_now()
    job.status = JobStatus.CANCELLED.value
    job.progress_pct = max(job.progress_pct or 0, 100)
    job.stage_detail = stage_detail
    job.error_message = None
    if job.finished_at is None:
        job.finished_at = now

    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def assert_ingest_not_cancelled(
    db: Session,
    *,
    job_id: str,
    document_id: str,
    stage: str,
    skipped_chunks: int = 0,
    skipped_batches: int = 0,
) -> None:
    job = db.query(IngestJob).filter(IngestJob.id == job_id).first()
    document = db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()

    reason: str | None = None
    if job is None:
        reason = "ingest job missing"
    elif job.status == JobStatus.CANCELLED.value:
        reason = "ingest job cancelled"
    elif document is None:
        reason = "document missing during ingest"
    elif document.delete_requested_at is not None:
        reason = "document delete requested during ingest"
    elif document.deleted_at is not None:
        reason = "document deleted during ingest"

    if reason is None:
        db.rollback()
        return

    if job is not None and job.status != JobStatus.CANCELLED.value:
        now = _utc_now()
        job.status = JobStatus.CANCELLED.value
        job.progress_pct = max(job.progress_pct or 0, 100)
        job.stage_detail = f"cancelled_at_{stage}"
        job.error_message = None
        if job.finished_at is None:
            job.finished_at = now
        db.add(job)
        db.commit()
    else:
        db.rollback()

    log_event(
        "info",
        "ingest_cancelled_no_retry",
        job_id=job_id,
        document_id=document_id,
        stage=stage,
        stage_detail=reason,
        skipped_chunks=skipped_chunks,
        skipped_batches=skipped_batches,
    )
    raise IngestCancelled(
        job_id=job_id,
        document_id=document_id,
        stage=stage,
        reason=reason,
        skipped_chunks=skipped_chunks,
        skipped_batches=skipped_batches,
    )
