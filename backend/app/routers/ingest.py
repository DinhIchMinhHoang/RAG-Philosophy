from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.dependencies import get_current_user
from ..core.settings import settings
from ..database import SessionLocal, get_db
from ..ingest.logging_utils import log_event
from ..ingest.qdrant_store import build_qdrant_client, delete_vectors_for_document
from ..ingest.storage import storage_client
from ..models import DocumentRecord, IngestJob, JobStage, JobStatus, User

router = APIRouter(prefix="/api", tags=["Ingest"])

ALLOWED_EXTENSIONS = {'.pdf', '.xlsx', '.xls', '.csv', '.docx', '.html', '.htm', '.md'}
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "20"))

MIME_TYPES = {
    '.pdf': 'application/pdf',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xls': 'application/vnd.ms-excel',
    '.csv': 'text/csv',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.html': 'text/html',
    '.htm': 'text/html',
    '.md': 'text/markdown',
}




class ReindexRequest(BaseModel):
    pipeline_version: str | None = None


class JobResponse(BaseModel):
    job_id: str
    document_id: str
    status: str
    stage: str
    progress_pct: int
    stage_detail: str | None
    error_message: str | None
    pipeline_version: str
    queued_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None


class LatestJobSummary(BaseModel):
    job_id: str
    status: str
    stage: str
    progress_pct: int
    stage_detail: str | None
    error_message: str | None
    pipeline_version: str
    queued_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None


class DocumentListItem(BaseModel):
    document_id: str
    filename: str
    object_key: str
    mime_type: str
    size_bytes: int
    created_at: datetime
    updated_at: datetime
    latest_job: LatestJobSummary | None


class DeleteDocumentResponse(BaseModel):
    document_id: str
    deleted: bool
    status: str
    cleanup: dict[str, bool]
    cleanup_errors: list[str]


def _enqueue_ingest(job_id: str, document_id: str, object_key: str, pipeline_version: str, user_id: str) -> None:
    try:
        from ..worker.celery_app import celery_app
    except ModuleNotFoundError as exc:
        raise RuntimeError("Celery is not installed. Run `pip install -r requirements.txt`.") from exc

    celery_app.send_task(
        "backend.app.worker.tasks.process_ingest_job",
        kwargs={
            "job_id": job_id,
            "document_id": document_id,
            "object_key": object_key,
            "pipeline_version": pipeline_version,
            "user_id": user_id,
        },
        queue=settings.celery_ingest_queue,
    )


def _create_job(db: Session, document_id: str, pipeline_version: str) -> IngestJob:
    job = IngestJob(
        id=str(uuid.uuid4()),
        document_id=document_id,
        status=JobStatus.QUEUED.value,
        stage=JobStage.FETCHING_OBJECT.value,
        progress_pct=0,
        stage_detail="queued",
        pipeline_version=pipeline_version,
        queued_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


async def _create_document_impl(file: UploadFile, pipeline_version: str | None = None, current_user: User | None = None) -> dict:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {ext}. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    payload = await file.read()

    max_size = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(payload) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large: {len(payload)/1024/1024:.1f}MB (max: {MAX_UPLOAD_SIZE_MB}MB)"
        )

    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    version = (pipeline_version or settings.pipeline_version).strip()
    if not version:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="pipeline_version is required")

    document_id = str(uuid.uuid4())
    object_key = f"{document_id}/{Path(file.filename).name}"
    user_id = current_user.username if current_user else "system"

    db = SessionLocal()
    try:
        storage_client.put_bytes(object_key, payload, file.content_type or MIME_TYPES.get(ext, 'application/octet-stream'))

        document = DocumentRecord(
            id=document_id,
            filename=file.filename,
            object_key=object_key,
            mime_type=file.content_type or MIME_TYPES.get(ext, 'application/octet-stream'),
            size_bytes=len(payload),
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        job = _create_job(db, document_id=document.id, pipeline_version=version)
        _enqueue_ingest(job.id, document.id, document.object_key, version, user_id)

        return {
            "document_id": document.id,
            "job_id": job.id,
            "status": job.status,
            "pipeline_version": version,
            "object_key": document.object_key,
        }
    except HTTPException:
        raise
    except Exception as exc:
        log_event(
            "error",
            "enqueue_failed",
            document_id=document_id,
            pipeline_version=version,
            stage="enqueue",
            error_message=str(exc),
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to enqueue document: {exc}")
    finally:
        db.close()


def _serialize_job(job: IngestJob) -> JobResponse:
    return JobResponse(
        job_id=job.id,
        document_id=job.document_id,
        status=job.status,
        stage=job.stage,
        progress_pct=job.progress_pct,
        stage_detail=job.stage_detail,
        error_message=job.error_message,
        pipeline_version=job.pipeline_version,
        queued_at=job.queued_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
    )


def _get_job_impl(job_id: str) -> JobResponse:
    db = SessionLocal()
    try:
        job = db.query(IngestJob).filter(IngestJob.id == job_id).first()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        return _serialize_job(job)
    finally:
        db.close()


def _list_documents_impl(db: Session) -> list[DocumentListItem]:
    rows = db.query(DocumentRecord).order_by(DocumentRecord.created_at.desc()).all()
    output: list[DocumentListItem] = []
    for row in rows:
        latest_job = (
            db.query(IngestJob)
            .filter(IngestJob.document_id == row.id)
            .order_by(IngestJob.created_at.desc())
            .first()
        )
        output.append(
            DocumentListItem(
                document_id=row.id,
                filename=row.filename,
                object_key=row.object_key,
                mime_type=row.mime_type,
                size_bytes=row.size_bytes,
                created_at=row.created_at,
                updated_at=row.updated_at,
                latest_job=LatestJobSummary(
                    job_id=latest_job.id,
                    status=latest_job.status,
                    stage=latest_job.stage,
                    progress_pct=latest_job.progress_pct,
                    stage_detail=latest_job.stage_detail,
                    error_message=latest_job.error_message,
                    pipeline_version=latest_job.pipeline_version,
                    queued_at=latest_job.queued_at,
                    started_at=latest_job.started_at,
                    finished_at=latest_job.finished_at,
                )
                if latest_job
                else None,
            )
        )
    return output


def _delete_document_impl(db: Session, document_id: str) -> DeleteDocumentResponse:
    cleanup = {
        "metadata_deleted": False,
        "chunks_deleted": False,
        "vectors_deleted": False,
        "object_deleted": False,
        "excel_tables_dropped": 0,
    }
    cleanup_errors: list[str] = []

    document = db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()
    if not document:
        return DeleteDocumentResponse(
            document_id=document_id,
            deleted=False,
            status="not_found",
            cleanup=cleanup,
            cleanup_errors=[],
        )

    object_key = document.object_key

    try:
        storage_client.delete(object_key)
        cleanup["object_deleted"] = True
    except Exception as exc:
        cleanup_errors.append(f"object_storage: {exc}")

    try:
        client = build_qdrant_client()
        delete_vectors_for_document(client, document_id)
        cleanup["vectors_deleted"] = True
    except Exception as exc:
        cleanup_errors.append(f"qdrant: {exc}")

    chunk_count = len(document.chunks)
    cleanup["chunks_deleted"] = chunk_count > 0

    try:
        from ..ingest.excel_ingestor import drop_excel_tables
        dropped = drop_excel_tables(db, document_id)
        cleanup["excel_tables_dropped"] = dropped
    except Exception as exc:
        cleanup_errors.append(f"excel_cleanup: {exc}")

    try:
        db.delete(document)
        db.commit()
        cleanup["metadata_deleted"] = True
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete metadata for document {document_id}: {exc}",
        )

    return DeleteDocumentResponse(
        document_id=document_id,
        deleted=True,
        status="deleted",
        cleanup=cleanup,
        cleanup_errors=cleanup_errors,
    )


def _reindex_document_impl(document_id: str, request: ReindexRequest) -> dict:
    db = SessionLocal()
    try:
        document = db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        version = (request.pipeline_version or settings.pipeline_version).strip()
        if not version:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="pipeline_version is required")

        job = _create_job(db, document_id=document.id, pipeline_version=version)
        _enqueue_ingest(job.id, document.id, document.object_key, version)

        return {
            "document_id": document.id,
            "job_id": job.id,
            "status": job.status,
            "pipeline_version": version,
            "object_key": document.object_key,
        }
    except HTTPException:
        raise
    except Exception as exc:
        log_event(
            "error",
            "reindex_enqueue_failed",
            document_id=document_id,
            stage="enqueue",
            error_message=str(exc),
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to enqueue reindex: {exc}")
    finally:
        db.close()


@router.post("/documents", status_code=status.HTTP_202_ACCEPTED)
async def create_document(
    file: UploadFile = File(...),
    pipeline_version: str | None = None,
    current_user: User = Depends(get_current_user),
):
    return await _create_document_impl(file=file, pipeline_version=pipeline_version, current_user=current_user)


@router.get("/documents", response_model=list[DocumentListItem])
def list_documents(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return _list_documents_impl(db)


@router.delete("/documents/{document_id}", response_model=DeleteDocumentResponse)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return _delete_document_impl(db, document_id)


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str,
    _current_user: User = Depends(get_current_user),
):
    return _get_job_impl(job_id)


@router.post("/documents/{document_id}/reindex", status_code=status.HTTP_202_ACCEPTED)
def reindex_document(
    document_id: str,
    request: ReindexRequest,
    _current_user: User = Depends(get_current_user),
):
    return _reindex_document_impl(document_id=document_id, request=request)

