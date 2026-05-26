from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models import DocumentChunk, DocumentRecord, IngestJob, JobStatus
from .qdrant_store import build_qdrant_client, delete_vectors_for_document
from .storage import storage_client


ACTIVE_JOB_STATUSES = (JobStatus.QUEUED.value, JobStatus.RUNNING.value)


@dataclass
class DocumentDeleteResult:
    cleanup: dict[str, bool | int]
    errors: list[str]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _revoke_tasks(task_ids: list[str], errors: list[str]) -> None:
    if not task_ids:
        return
    try:
        from ..worker.celery_app import celery_app
    except Exception as exc:
        errors.append(f"celery_revoke: {exc}")
        return

    for task_id in task_ids:
        try:
            celery_app.control.revoke(task_id, terminate=False)
        except Exception as exc:
            errors.append(f"celery_revoke:{task_id}: {exc}")


def cancel_and_cleanup_document(db: Session, document: DocumentRecord) -> DocumentDeleteResult:
    cleanup: dict[str, bool | int] = {
        "metadata_deleted": False,
        "chunks_deleted": False,
        "vectors_deleted": False,
        "object_deleted": False,
        "excel_tables_dropped": 0,
        "jobs_cancelled": 0,
        "tasks_revoked": 0,
    }
    errors: list[str] = []

    now = _utc_now()
    if document.delete_requested_at is None:
        document.delete_requested_at = now
    db.add(document)

    active_jobs = (
        db.query(IngestJob)
        .filter(IngestJob.document_id == document.id, IngestJob.status.in_(ACTIVE_JOB_STATUSES))
        .all()
    )
    task_ids: list[str] = []
    for job in active_jobs:
        job.status = JobStatus.CANCELLED.value
        job.progress_pct = max(job.progress_pct or 0, 100)
        job.stage_detail = "cancelled_by_delete"
        job.error_message = None
        if job.finished_at is None:
            job.finished_at = now
        if job.celery_task_id:
            task_ids.append(job.celery_task_id)
        db.add(job)
    db.commit()
    db.refresh(document)

    cleanup["jobs_cancelled"] = len(active_jobs)
    cleanup["tasks_revoked"] = len(task_ids)
    _revoke_tasks(task_ids, errors)

    if document.object_key.startswith("url://"):
        cleanup["object_deleted"] = True
    else:
        try:
            storage_client.delete(document.object_key)
            cleanup["object_deleted"] = True
        except FileNotFoundError:
            cleanup["object_deleted"] = False
        except Exception as exc:
            errors.append(f"object_storage: {exc}")

    try:
        client = build_qdrant_client()
        delete_vectors_for_document(client, document.id)
        cleanup["vectors_deleted"] = True
    except Exception as exc:
        errors.append(f"qdrant: {exc}")

    try:
        from .excel_ingestor import drop_excel_tables

        cleanup["excel_tables_dropped"] = drop_excel_tables(db, document.id)
    except Exception as exc:
        errors.append(f"excel_cleanup: {exc}")

    try:
        deleted_chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document.id)
            .delete(synchronize_session=False)
        )
        cleanup["chunks_deleted"] = deleted_chunks > 0

        document.content_hash = None
        document.deleted_at = _utc_now()
        db.add(document)
        db.commit()
        cleanup["metadata_deleted"] = True
    except Exception:
        db.rollback()
        raise

    try:
        client = build_qdrant_client()
        delete_vectors_for_document(client, document.id)
        cleanup["vectors_deleted"] = True
    except Exception as exc:
        errors.append(f"qdrant_final: {exc}")

    return DocumentDeleteResult(cleanup=cleanup, errors=errors)
