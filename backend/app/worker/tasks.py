from __future__ import annotations

from typing import Any

from celery import Task

from ..core.settings import settings
from ..database import SessionLocal
from ..ingest.job_updater import JobUpdater
from ..ingest.logging_utils import log_event
from ..ingest.processor import run_ingest_job, run_url_ingest_job
from .celery_app import celery_app


class RetryableIngestError(Exception):
    pass


def _safe_error_message(exc: Exception) -> str:
    message = str(exc).strip()
    if message:
        return message
    return f"{exc.__class__.__name__}: {repr(exc)}"



def _is_retryable(exc: Exception) -> bool:
    retryable_types = (ConnectionError, TimeoutError, OSError)
    return isinstance(exc, retryable_types)



def _payload_from_call(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if kwargs:
        return kwargs
    if len(args) >= 4:
        return {
            "job_id": args[0],
            "document_id": args[1],
            "object_key": args[2],
            "pipeline_version": args[3],
        }
    return {}


class IngestTaskBase(Task):
    autoretry_for = (RetryableIngestError,)
    retry_backoff = True
    retry_jitter = True
    max_retries = settings.celery_max_retries
    retry_backoff_max = settings.celery_retry_backoff_max

    def on_retry(self, exc: Exception, task_id: str, args: tuple[Any, ...], kwargs: dict[str, Any], einfo: Any) -> None:
        payload = _payload_from_call(args, kwargs)
        job_id = payload.get("job_id")
        if job_id:
            db = SessionLocal()
            try:
                updater = JobUpdater(db)
                updater.set_state(
                    job_id,
                    status="queued",
                    stage_detail=f"retrying_after_error: {_safe_error_message(exc)[:200]}",
                )
            finally:
                db.close()

        log_event(
            "warning",
            "job_retry",
            job_id=payload.get("job_id"),
            document_id=payload.get("document_id"),
            pipeline_version=payload.get("pipeline_version"),
            stage="retry",
            error_message=_safe_error_message(exc),
        )

    def on_failure(self, exc: Exception, task_id: str, args: tuple[Any, ...], kwargs: dict[str, Any], einfo: Any) -> None:
        payload = _payload_from_call(args, kwargs)
        job_id = payload.get("job_id")
        if job_id:
            db = SessionLocal()
            try:
                updater = JobUpdater(db)
                updater.fail(job_id, _safe_error_message(exc))
            finally:
                db.close()

        log_event(
            "error",
            "job_failed",
            job_id=payload.get("job_id"),
            document_id=payload.get("document_id"),
            pipeline_version=payload.get("pipeline_version"),
            stage="failed",
            error_message=_safe_error_message(exc),
        )


@celery_app.task(
    bind=True,
    base=IngestTaskBase,
    name="backend.app.worker.tasks.process_ingest_job",
)
def process_ingest_job(
    self,
    *,
    job_id: str,
    document_id: str,
    object_key: str,
    pipeline_version: str,
    user_id: str = "system",
) -> dict[str, int]:
    for field_name, value in {
        "job_id": job_id,
        "document_id": document_id,
        "object_key": object_key,
        "pipeline_version": pipeline_version,
    }.items():
        if not value:
            raise ValueError(f"Missing required field: {field_name}")

    log_event(
        "info",
        "job_started",
        job_id=job_id,
        document_id=document_id,
        pipeline_version=pipeline_version,
        stage="fetching_object",
    )

    db = SessionLocal()
    try:
        result = run_ingest_job(
            db,
            job_id=job_id,
            document_id=document_id,
            object_key=object_key,
            pipeline_version=pipeline_version,
            user_id=user_id,
        )
        log_event(
            "info",
            "job_completed",
            job_id=job_id,
            document_id=document_id,
            pipeline_version=pipeline_version,
            stage="persisting_metadata",
        )
        return result
    except Exception as exc:
        if _is_retryable(exc):
            raise RetryableIngestError(str(exc)) from exc

        updater = JobUpdater(db)
        updater.fail(job_id, _safe_error_message(exc))
        raise
    finally:
        db.close()


@celery_app.task(
    bind=True,
    base=IngestTaskBase,
    name="backend.app.worker.tasks.process_url_ingest_job",
)
def process_url_ingest_job(
    self,
    *,
    job_id: str,
    document_id: str,
    url: str,
    pipeline_version: str,
    user_id: str = "system",
) -> dict[str, int]:
    for field_name, value in {
        "job_id": job_id,
        "document_id": document_id,
        "url": url,
        "pipeline_version": pipeline_version,
    }.items():
        if not value:
            raise ValueError(f"Missing required field: {field_name}")

    log_event(
        "info",
        "job_started",
        job_id=job_id,
        document_id=document_id,
        pipeline_version=pipeline_version,
        stage="fetching_object",
    )

    db = SessionLocal()
    try:
        result = run_url_ingest_job(
            db,
            job_id=job_id,
            document_id=document_id,
            url=url,
            pipeline_version=pipeline_version,
            user_id=user_id,
        )
        log_event(
            "info",
            "job_completed",
            job_id=job_id,
            document_id=document_id,
            pipeline_version=pipeline_version,
            stage="persisting_metadata",
        )
        return result
    except Exception as exc:
        if _is_retryable(exc):
            raise RetryableIngestError(str(exc)) from exc

        updater = JobUpdater(db)
        updater.fail(job_id, _safe_error_message(exc))
        raise
    finally:
        db.close()
