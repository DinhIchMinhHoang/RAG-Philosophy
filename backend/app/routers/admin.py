from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from .. import database, models
from ..core.dependencies import require_admin_user
from ..core.settings import settings
from ..core.security import get_password_hash
from ..ingest.qdrant_store import build_qdrant_client, delete_vectors_for_document
from ..ingest.storage import storage_client

router = APIRouter(prefix="/api/admin", tags=["Admin"])


class AdminUserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr


class AdminDocumentResponse(BaseModel):
    document_id: str
    filename: str
    object_key: str
    mime_type: str
    size_bytes: int
    created_at: str
    updated_at: str
    latest_job: dict | None


class AdminApiConfigEntry(BaseModel):
    key: str
    value: str
    sensitive: bool


class AdminApiConfigResponse(BaseModel):
    entries: list[AdminApiConfigEntry]


class AdminNotebookNode(BaseModel):
    id: int
    title: str
    owner_id: int
    is_community: bool
    cover_url: str | None
    cover_mode: str | None
    cover_color: str | None
    is_virtual: bool = False
    documents: list[AdminDocumentResponse]


class AdminUserNode(BaseModel):
    id: int
    username: str
    email: EmailStr
    notebooks: list[AdminNotebookNode]


class AdminLibraryResponse(BaseModel):
    users: list[AdminUserNode]


class AdminDeleteResponse(BaseModel):
    deleted: bool
    status: str
    cleanup_errors: list[str]


class AdminReindexRequest(BaseModel):
    pipeline_version: str | None = None


class AdminReindexResponse(BaseModel):
    document_id: str
    job_id: str
    status: str
    pipeline_version: str
    object_key: str | None = None
    url: str | None = None


def _delete_documents(db: Session, document_ids: list[str], cleanup_errors: list[str]) -> bool:
    if not document_ids:
        return False
    documents = db.query(models.DocumentRecord).filter(models.DocumentRecord.id.in_(document_ids)).all()
    if not documents:
        return False

    qdrant_client = None
    try:
        qdrant_client = build_qdrant_client()
    except Exception as exc:
        cleanup_errors.append(f"qdrant_client: {exc}")

    for doc in documents:
        if doc.object_key.startswith("url://"):
            continue
        try:
            storage_client.delete(doc.object_key)
        except Exception as exc:
            cleanup_errors.append(f"object_storage:{doc.id}: {exc}")

        if qdrant_client is not None:
            try:
                delete_vectors_for_document(qdrant_client, doc.id)
            except Exception as exc:
                cleanup_errors.append(f"qdrant:{doc.id}: {exc}")

    db.query(models.IngestJob).filter(models.IngestJob.document_id.in_(document_ids)).delete(synchronize_session=False)
    db.query(models.DocumentChunk).filter(models.DocumentChunk.document_id.in_(document_ids)).delete(synchronize_session=False)
    db.query(models.DocumentRecord).filter(models.DocumentRecord.id.in_(document_ids)).delete(synchronize_session=False)
    db.commit()
    return True


def _enqueue_ingest(job_id: str, document_id: str, object_key: str, pipeline_version: str, user_id: str = "system") -> None:
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


def _enqueue_url_ingest(job_id: str, document_id: str, url: str, pipeline_version: str, user_id: str = "system") -> None:
    try:
        from ..worker.celery_app import celery_app
    except ModuleNotFoundError as exc:
        raise RuntimeError("Celery is not installed. Run `pip install -r requirements.txt`.") from exc

    celery_app.send_task(
        "backend.app.worker.tasks.process_url_ingest_job",
        kwargs={
            "job_id": job_id,
            "document_id": document_id,
            "url": url,
            "pipeline_version": pipeline_version,
            "user_id": user_id,
        },
        queue=settings.celery_ingest_queue,
    )


def _create_job(db: Session, document_id: str, pipeline_version: str) -> models.IngestJob:
    job = models.IngestJob(
        id=str(uuid.uuid4()),
        document_id=document_id,
        status=models.JobStatus.QUEUED.value,
        stage=models.JobStage.FETCHING_OBJECT.value,
        progress_pct=0,
        stage_detail="queued",
        pipeline_version=pipeline_version,
        queued_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def _delete_conversations(db: Session, conversation_ids: list[str]) -> None:
    if not conversation_ids:
        return
    db.query(models.ChatMessage).filter(models.ChatMessage.conversation_id.in_(conversation_ids)).delete(synchronize_session=False)
    db.query(models.Conversation).filter(models.Conversation.id.in_(conversation_ids)).delete(synchronize_session=False)
    db.commit()


def _delete_notebook_content(db: Session, notebook_id: int, cleanup_errors: list[str]) -> None:
    conversation_ids = [row.id for row in db.query(models.Conversation.id).filter(models.Conversation.notebook_id == notebook_id).all()]
    _delete_conversations(db, conversation_ids)

    db.query(models.SavedNotebookItem).filter(models.SavedNotebookItem.notebook_id == notebook_id).delete(synchronize_session=False)
    db.commit()

    document_ids = [row.id for row in db.query(models.DocumentRecord.id).filter(models.DocumentRecord.notebook_id == notebook_id).all()]
    _delete_documents(db, document_ids, cleanup_errors)


def _delete_user_content(db: Session, user_id: int, cleanup_errors: list[str]) -> None:
    notebook_ids = [row.id for row in db.query(models.Notebook.id).filter(models.Notebook.owner_id == user_id).all()]
    for notebook_id in notebook_ids:
        _delete_notebook_content(db, notebook_id, cleanup_errors)

    conversation_ids = [
        row.id
        for row in db.query(models.Conversation.id)
        .filter(models.Conversation.owner_id == user_id)
        .filter(models.Conversation.notebook_id.is_(None))
        .all()
    ]
    _delete_conversations(db, conversation_ids)

    document_ids = [
        row.id
        for row in db.query(models.DocumentRecord.id)
        .filter(models.DocumentRecord.owner_id == user_id)
        .filter(models.DocumentRecord.notebook_id.is_(None))
        .all()
    ]
    _delete_documents(db, document_ids, cleanup_errors)

    db.query(models.SavedNotebookItem).filter(models.SavedNotebookItem.owner_id == user_id).delete(synchronize_session=False)
    db.commit()


@router.get("/users", response_model=list[AdminUserResponse])
def list_users(
    _admin_user: models.User = Depends(require_admin_user),
    db: Session = Depends(database.get_db),
):
    users = db.query(models.User).order_by(models.User.id.asc()).all()
    return [AdminUserResponse(id=u.id, username=u.username, email=u.email) for u in users]


@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=AdminUserResponse)
def create_user(
    payload: AdminUserCreate,
    _admin_user: models.User = Depends(require_admin_user),
    db: Session = Depends(database.get_db),
):
    if db.query(models.User).filter(models.User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already used")
    if db.query(models.User).filter(models.User.username == payload.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    user = models.User(
        username=payload.username,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return AdminUserResponse(id=user.id, username=user.username, email=user.email)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    _admin_user: models.User = Depends(require_admin_user),
    db: Session = Depends(database.get_db),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    cleanup_errors: list[str] = []
    _delete_user_content(db, user_id, cleanup_errors)

    db.delete(user)
    db.commit()
    return {"deleted": True, "user_id": user_id, "cleanup_errors": cleanup_errors}


@router.get("/library", response_model=AdminLibraryResponse)
def list_library(
    _admin_user: models.User = Depends(require_admin_user),
    db: Session = Depends(database.get_db),
):
    users = db.query(models.User).order_by(models.User.id.asc()).all()
    notebooks = db.query(models.Notebook).order_by(models.Notebook.created_at.desc()).all()
    documents = db.query(models.DocumentRecord).order_by(models.DocumentRecord.created_at.desc()).all()

    all_jobs = db.query(models.IngestJob).order_by(models.IngestJob.created_at.desc()).all()
    jobs_by_document: dict[str, models.IngestJob | None] = {}
    for job in all_jobs:
        if job.document_id not in jobs_by_document:
            jobs_by_document[job.document_id] = job

    docs_by_owner_notebook: dict[tuple[int | None, int | None], list[AdminDocumentResponse]] = {}
    for doc in documents:
        latest_job = jobs_by_document.get(doc.id)
        key = (doc.owner_id, doc.notebook_id)
        docs_by_owner_notebook.setdefault(key, []).append(
            AdminDocumentResponse(
                document_id=doc.id,
                filename=doc.filename,
                object_key=doc.object_key,
                mime_type=doc.mime_type,
                size_bytes=doc.size_bytes,
                created_at=doc.created_at.isoformat(),
                updated_at=doc.updated_at.isoformat(),
                latest_job={
                    "job_id": latest_job.id,
                    "status": latest_job.status,
                    "stage": latest_job.stage,
                    "progress_pct": latest_job.progress_pct,
                    "stage_detail": latest_job.stage_detail,
                    "error_message": latest_job.error_message,
                    "pipeline_version": latest_job.pipeline_version,
                    "queued_at": latest_job.queued_at.isoformat() if latest_job.queued_at else None,
                    "started_at": latest_job.started_at.isoformat() if latest_job.started_at else None,
                    "finished_at": latest_job.finished_at.isoformat() if latest_job.finished_at else None,
                }
                if latest_job
                else None,
            )
        )

    notebooks_by_user: dict[int, list[models.Notebook]] = {}
    for nb in notebooks:
        notebooks_by_user.setdefault(nb.owner_id, []).append(nb)

    user_nodes: list[AdminUserNode] = []
    for user in users:
        nb_nodes: list[AdminNotebookNode] = []
        user_notebooks = notebooks_by_user.get(user.id, [])
        for nb in user_notebooks:
            nb_nodes.append(
                AdminNotebookNode(
                    id=nb.id,
                    title=nb.title,
                    owner_id=nb.owner_id,
                    is_community=bool(nb.is_community),
                    cover_url=nb.cover_url,
                    cover_mode=nb.cover_mode,
                    cover_color=nb.cover_color,
                    is_virtual=False,
                    documents=docs_by_owner_notebook.get((user.id, nb.id), []),
                )
            )
        unfiled_docs = docs_by_owner_notebook.get((user.id, None), [])
        if unfiled_docs:
            nb_nodes.append(
                AdminNotebookNode(
                    id=0,
                    title="Unfiled",
                    owner_id=user.id,
                    is_community=False,
                    cover_url=None,
                    cover_mode=None,
                    cover_color=None,
                    is_virtual=True,
                    documents=unfiled_docs,
                )
            )
        user_nodes.append(AdminUserNode(id=user.id, username=user.username, email=user.email, notebooks=nb_nodes))

    return AdminLibraryResponse(users=user_nodes)


@router.delete("/documents/{document_id}", response_model=AdminDeleteResponse)
def delete_document_admin(
    document_id: str,
    _admin_user: models.User = Depends(require_admin_user),
    db: Session = Depends(database.get_db),
):
    cleanup_errors: list[str] = []
    deleted = _delete_documents(db, [document_id], cleanup_errors)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return AdminDeleteResponse(deleted=True, status="deleted", cleanup_errors=cleanup_errors)


@router.delete("/notebooks/{notebook_id}", response_model=AdminDeleteResponse)
def delete_notebook_admin(
    notebook_id: int,
    _admin_user: models.User = Depends(require_admin_user),
    db: Session = Depends(database.get_db),
):
    notebook = db.query(models.Notebook).filter(models.Notebook.id == notebook_id).first()
    if not notebook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    cleanup_errors: list[str] = []
    _delete_notebook_content(db, notebook_id, cleanup_errors)
    db.delete(notebook)
    db.commit()
    return AdminDeleteResponse(deleted=True, status="deleted", cleanup_errors=cleanup_errors)


@router.get("/documents", response_model=list[AdminDocumentResponse])
def list_documents(
    _admin_user: models.User = Depends(require_admin_user),
    db: Session = Depends(database.get_db),
):
    rows = db.query(models.DocumentRecord).order_by(models.DocumentRecord.created_at.desc()).all()
    output = []
    for doc in rows:
        latest_job = (
            db.query(models.IngestJob)
            .filter(models.IngestJob.document_id == doc.id)
            .order_by(models.IngestJob.created_at.desc())
            .first()
        )
        output.append(
            AdminDocumentResponse(
                document_id=doc.id,
                filename=doc.filename,
                object_key=doc.object_key,
                mime_type=doc.mime_type,
                size_bytes=doc.size_bytes,
                created_at=doc.created_at.isoformat(),
                updated_at=doc.updated_at.isoformat(),
                latest_job={
                    "job_id": latest_job.id,
                    "status": latest_job.status,
                    "stage": latest_job.stage,
                    "progress_pct": latest_job.progress_pct,
                    "stage_detail": latest_job.stage_detail,
                    "error_message": latest_job.error_message,
                    "pipeline_version": latest_job.pipeline_version,
                    "queued_at": latest_job.queued_at.isoformat() if latest_job.queued_at else None,
                    "started_at": latest_job.started_at.isoformat() if latest_job.started_at else None,
                    "finished_at": latest_job.finished_at.isoformat() if latest_job.finished_at else None,
                }
                if latest_job
                else None,
            )
        )
    return output


_SENSITIVE_PATTERNS = ["API_KEY", "SECRET", "PASSWORD", "TOKEN", "ACCESS_KEY"]


def _is_sensitive_key(key: str) -> bool:
    return any(p in key.upper() for p in _SENSITIVE_PATTERNS)


def _mask_value(value: str) -> str:
    if len(value) <= 8:
        return "***"
    return value[:6] + "***"


def _parse_env_file() -> list[AdminApiConfigEntry]:
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if not env_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=".env file not found")
    entries: list[AdminApiConfigEntry] = []
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, raw_value = stripped.partition("=")
        key = key.strip()
        value = raw_value.strip().strip("\"'")
        sensitive = _is_sensitive_key(key)
        display = _mask_value(value) if sensitive else value
        entries.append(AdminApiConfigEntry(key=key, value=display, sensitive=sensitive))
    return entries


@router.get("/api-config", response_model=AdminApiConfigResponse)
def get_api_config(
    _admin_user: models.User = Depends(require_admin_user),
):
    return AdminApiConfigResponse(entries=_parse_env_file())


@router.post("/documents/{document_id}/reindex", status_code=status.HTTP_202_ACCEPTED, response_model=AdminReindexResponse)
def reindex_document_admin(
    document_id: str,
    request: AdminReindexRequest,
    _admin_user: models.User = Depends(require_admin_user),
    db: Session = Depends(database.get_db),
):
    document = db.query(models.DocumentRecord).filter(models.DocumentRecord.id == document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    version = (request.pipeline_version or settings.pipeline_version).strip()
    if not version:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="pipeline_version is required")

    user_id = _admin_user.username if _admin_user else "system"
    job = _create_job(db, document_id=document.id, pipeline_version=version)

    if document.object_key.startswith("url://"):
        url = document.object_key[6:]
        _enqueue_url_ingest(job.id, document.id, url, version, user_id)
        return AdminReindexResponse(
            document_id=document.id,
            job_id=job.id,
            status=job.status,
            pipeline_version=version,
            url=url,
        )
    else:
        _enqueue_ingest(job.id, document.id, document.object_key, version, user_id)
        return AdminReindexResponse(
            document_id=document.id,
            job_id=job.id,
            status=job.status,
            pipeline_version=version,
            object_key=document.object_key,
        )
