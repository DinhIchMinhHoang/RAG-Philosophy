from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from ..models import IngestJob
from .constants import STAGE_ORDER, VALID_JOB_STAGES, VALID_JOB_STATUSES, stage_progress


class JobUpdater:
    def __init__(self, db: Session):
        self.db = db

    def get_job(self, job_id: str) -> IngestJob:
        job = self.db.query(IngestJob).filter(IngestJob.id == job_id).first()
        if not job:
            raise ValueError(f"Job not found: {job_id}")
        return job

    def set_state(
        self,
        job_id: str,
        *,
        status: Optional[str] = None,
        stage: Optional[str] = None,
        progress_pct: Optional[int] = None,
        stage_detail: Optional[str] = None,
        error_message: Optional[str] = None,
        pipeline_version: Optional[str] = None,
    ) -> IngestJob:
        job = self.get_job(job_id)

        if status is not None and status not in VALID_JOB_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        if stage is not None and stage not in VALID_JOB_STAGES:
            raise ValueError(f"Invalid stage: {stage}")

        now = datetime.now(timezone.utc)

        if status is not None:
            job.status = status
            if status == "queued" and job.queued_at is None:
                job.queued_at = now
            if status == "running" and job.started_at is None:
                job.started_at = now
            if status in {"succeeded", "failed"}:
                job.finished_at = now

        if stage is not None:
            if job.stage in STAGE_ORDER and stage in STAGE_ORDER:
                current_idx = STAGE_ORDER.index(job.stage)
                next_idx = STAGE_ORDER.index(stage)
                if next_idx < current_idx:
                    raise ValueError(f"Stage cannot move backwards: {job.stage} -> {stage}")
            job.stage = stage

        if progress_pct is not None:
            clamped = max(0, min(100, int(progress_pct)))
            # Progress is monotonic to keep polling UX stable.
            job.progress_pct = max(job.progress_pct or 0, clamped)

        if stage_detail is not None:
            job.stage_detail = stage_detail

        if error_message is not None:
            job.error_message = error_message

        if pipeline_version is not None:
            job.pipeline_version = pipeline_version

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def start_run(self, job_id: str, *, pipeline_version: str) -> IngestJob:
        job = self.get_job(job_id)
        now = datetime.now(timezone.utc)

        # Celery retries replay the ingest pipeline from the beginning on the
        # same job row, so this is the only path allowed to rewind progress.
        job.status = "running"
        if job.started_at is None:
            job.started_at = now
        job.finished_at = None
        job.stage = STAGE_ORDER[0]
        job.progress_pct = 0
        job.stage_detail = "starting"
        job.error_message = None
        job.pipeline_version = pipeline_version

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def advance_stage(self, job_id: str, stage: str, *, ratio: float = 0.0, stage_detail: Optional[str] = None) -> IngestJob:
        progress_pct = stage_progress(stage, ratio)
        return self.set_state(
            job_id,
            stage=stage,
            progress_pct=progress_pct,
            stage_detail=stage_detail,
        )

    def fail(self, job_id: str, error_message: str) -> IngestJob:
        message = (error_message or "unknown error").strip()
        if len(message) > 2000:
            message = message[:2000]
        return self.set_state(
            job_id,
            status="failed",
            progress_pct=100,
            error_message=message,
            stage_detail="ingest_failed",
        )
