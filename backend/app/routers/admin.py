from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from .. import database, models
from ..core.dependencies import require_admin_user
from ..core.security import get_password_hash

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


class AdminJobResponse(BaseModel):
    job_id: str
    document_id: str
    status: str
    stage: str
    progress_pct: int
    stage_detail: str | None
    error_message: str | None
    pipeline_version: str
    queued_at: str | None
    started_at: str | None
    finished_at: str | None


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
    db.delete(user)
    db.commit()
    return {"deleted": True, "user_id": user_id}


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


@router.get("/jobs", response_model=list[AdminJobResponse])
def list_jobs(
    _admin_user: models.User = Depends(require_admin_user),
    db: Session = Depends(database.get_db),
):
    jobs = db.query(models.IngestJob).order_by(models.IngestJob.created_at.desc()).all()
    return [
        AdminJobResponse(
            job_id=job.id,
            document_id=job.document_id,
            status=job.status,
            stage=job.stage,
            progress_pct=job.progress_pct,
            stage_detail=job.stage_detail,
            error_message=job.error_message,
            pipeline_version=job.pipeline_version,
            queued_at=job.queued_at.isoformat() if job.queued_at else None,
            started_at=job.started_at.isoformat() if job.started_at else None,
            finished_at=job.finished_at.isoformat() if job.finished_at else None,
        )
        for job in jobs
    ]
