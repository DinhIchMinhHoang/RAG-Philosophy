from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import database, models
from ..core.dependencies import get_current_user
from ..core.settings import settings
from ..ingest.storage import storage_client
from ..ingest.storage import LocalStorageClient

router = APIRouter(prefix="/api/notebooks", tags=["Notebooks"])


class NotebookCreate(BaseModel):
    title: str
    is_community: bool = False


class NotebookUpdate(BaseModel):
    title: str | None = None
    is_community: bool | None = None
    cover_url: str | None = None
    cover_mode: str | None = None
    cover_color: str | None = None


class NotebookResponse(BaseModel):
    id: int
    title: str
    owner_id: int
    is_community: bool
    cover_url: str | None
    cover_mode: str | None
    cover_color: str | None
    created_at: str


class ConversationSummaryResponse(BaseModel):
    id: str
    notebook_id: int | None
    owner_id: int
    created_at: str
    updated_at: str


class ConversationMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    sources_used: list[dict] | None
    rewritten_query: str | None
    created_at: str


class LatestConversationResponse(BaseModel):
    conversation: ConversationSummaryResponse | None
    messages: list[ConversationMessageResponse]
    has_conversation: bool
    limit: int


class NotebookCopyResponse(BaseModel):
    notebook: NotebookResponse
    documents_copied: int
    jobs_enqueued: int


class SavedNotebookItemCreate(BaseModel):
    kind: Literal["note", "pin", "conversation", "summary"]
    content: str
    title: str | None = None
    conversation_id: str | None = None
    message_id: str | None = None
    sources_used: list[dict] | None = None


class SavedNotebookItemResponse(BaseModel):
    id: str
    notebook_id: int
    kind: str
    title: str | None
    content: str
    conversation_id: str | None
    message_id: str | None
    sources_used: list[dict] | None
    created_at: str


class FileRenameRequest(BaseModel):
    new_file_name: str


def _notebook_response(notebook: models.Notebook) -> NotebookResponse:
    return NotebookResponse(
        id=notebook.id,
        title=notebook.title,
        owner_id=notebook.owner_id,
        is_community=bool(notebook.is_community),
        cover_url=notebook.cover_url,
        cover_mode=notebook.cover_mode,
        cover_color=notebook.cover_color,
        created_at=notebook.created_at.isoformat(),
    )


def _conversation_response(conversation: models.Conversation) -> ConversationSummaryResponse:
    return ConversationSummaryResponse(
        id=conversation.id,
        notebook_id=conversation.notebook_id,
        owner_id=conversation.owner_id,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
    )


def _message_response(message: models.ChatMessage) -> ConversationMessageResponse:
    return ConversationMessageResponse(
        id=message.id,
        role=message.role,
        content=message.content,
        sources_used=message.sources_used,
        rewritten_query=message.rewritten_query,
        created_at=message.created_at.isoformat(),
    )


def _saved_item_response(item: models.SavedNotebookItem) -> SavedNotebookItemResponse:
    return SavedNotebookItemResponse(
        id=item.id,
        notebook_id=item.notebook_id,
        kind=item.kind,
        title=item.title,
        content=item.content,
        conversation_id=item.conversation_id,
        message_id=item.message_id,
        sources_used=item.sources_used,
        created_at=item.created_at.isoformat(),
    )


def _is_share_title_valid(title: str | None) -> bool:
    if not title:
        return False
    trimmed = title.strip()
    if not trimmed:
        return False
    return trimmed.lower() != "untitled notebook"


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


def _visible_notebooks_query(db: Session, user_id: int) -> Query[models.Notebook]:
    return db.query(models.Notebook).filter(
        (models.Notebook.owner_id == user_id) | (models.Notebook.is_community == 1)
    )


def _get_visible_notebook(db: Session, notebook_id: int, user_id: int) -> models.Notebook:
    notebook = _visible_notebooks_query(db, user_id).filter(models.Notebook.id == notebook_id).first()
    if notebook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    return notebook


def _sanitize_filename(name: str) -> str:
    # Basic sanitation: strip whitespace and disallow path separators or traversal
    if not name or not name.strip():
        raise ValueError("invalid filename")
    candidate = name.strip()
    if "/" in candidate or "\\" in candidate or ".." in candidate:
        raise ValueError("invalid filename")
    return candidate


def _get_document_for_notebook(db: Session, notebook_id: int, file_id: str, user_id: int) -> models.DocumentRecord:
    doc = (
        db.query(models.DocumentRecord)
        .filter(models.DocumentRecord.id == file_id, models.DocumentRecord.owner_id == user_id, models.DocumentRecord.notebook_id == notebook_id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return doc


@router.get("", response_model=list[NotebookResponse])
def list_notebooks(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    notebooks = _visible_notebooks_query(db, current_user.id).order_by(models.Notebook.created_at.desc()).all()
    return [_notebook_response(notebook) for notebook in notebooks]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=NotebookResponse)
def create_notebook(
    payload: NotebookCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    if payload.is_community and not _is_share_title_valid(payload.title):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Notebook title required before sharing")
    nb = models.Notebook(
        title=payload.title,
        owner_id=current_user.id,
        is_community=1 if payload.is_community else 0,
    )
    db.add(nb)
    db.commit()
    db.refresh(nb)
    return _notebook_response(nb)


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    sources_used: list[dict] | None
    rewritten_query: str | None
    created_at: str


class LatestConversationResponse(BaseModel):
    has_conversation: bool
    conversation: dict | None
    messages: list[MessageResponse]
    limit: int


@router.get("/{notebook_id}/conversations/latest", response_model=LatestConversationResponse)
def latest_notebook_conversation(
    notebook_id: int,
    limit: int = Query(50, ge=1, le=200),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    nb = db.query(models.Notebook).filter(models.Notebook.id == notebook_id).first()
    if not nb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    if nb.owner_id != current_user.id and not nb.is_community:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    conversation = (
        db.query(models.Conversation)
        .filter(
            models.Conversation.notebook_id == notebook_id,
            models.Conversation.owner_id == current_user.id,
        )
        .order_by(models.Conversation.created_at.desc())
        .first()
    )

    if not conversation:
        return LatestConversationResponse(
            has_conversation=False,
            conversation=None,
            messages=[],
            limit=limit,
        )

    messages = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.conversation_id == conversation.id)
        .order_by(models.ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )

    return LatestConversationResponse(
        has_conversation=True,
        conversation={
            "id": conversation.id,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
        },
        messages=[
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                sources_used=msg.sources_used,
                rewritten_query=msg.rewritten_query,
                created_at=msg.created_at.isoformat(),
            )
            for msg in messages
        ],
        limit=limit,
    )


@router.patch("/{notebook_id}", response_model=NotebookResponse)
def update_notebook(
    notebook_id: int,
    payload: NotebookUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    nb = db.query(models.Notebook).filter(models.Notebook.id == notebook_id).first()
    if not nb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    if nb.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not owner")
    if payload.title is not None:
        if nb.is_community and not _is_share_title_valid(payload.title):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Notebook title required before sharing")
        nb.title = payload.title
    if payload.is_community is not None:
        next_title = payload.title if payload.title is not None else nb.title
        if payload.is_community and not _is_share_title_valid(next_title):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Notebook title required before sharing")
        nb.is_community = 1 if payload.is_community else 0
    if payload.cover_url is not None:
        nb.cover_url = payload.cover_url
    if payload.cover_mode is not None:
        nb.cover_mode = payload.cover_mode
    if payload.cover_color is not None:
        nb.cover_color = payload.cover_color
    db.commit()
    db.refresh(nb)
    return _notebook_response(nb)


@router.post("/{notebook_id}/copy", status_code=status.HTTP_201_CREATED, response_model=NotebookCopyResponse)
def copy_notebook(
    notebook_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    source = _get_visible_notebook(db, notebook_id, current_user.id)
    title = (source.title or "").strip() or "Untitled notebook"
    new_notebook = models.Notebook(
        title=title,
        owner_id=current_user.id,
        is_community=0,
        cover_url=source.cover_url,
        cover_mode=source.cover_mode,
        cover_color=source.cover_color,
    )
    db.add(new_notebook)
    db.commit()
    db.refresh(new_notebook)

    documents = db.query(models.DocumentRecord).filter(models.DocumentRecord.notebook_id == source.id).all()
    pipeline_version = settings.pipeline_version
    documents_copied = 0
    jobs_enqueued = 0
    for doc in documents:
        new_document_id = str(uuid.uuid4())

        if doc.object_key.startswith("url://"):
            url = doc.object_key[6:]
            copied = models.DocumentRecord(
                id=new_document_id,
                owner_id=current_user.id,
                notebook_id=new_notebook.id,
                filename=doc.filename,
                object_key=doc.object_key,
                mime_type="text/html",
                size_bytes=0,
            )
            db.add(copied)
            db.commit()
            db.refresh(copied)
            documents_copied += 1

            try:
                job = _create_job(db, document_id=copied.id, pipeline_version=pipeline_version)
                _enqueue_url_ingest(job.id, copied.id, url, pipeline_version, current_user.username)
                jobs_enqueued += 1
            except Exception as exc:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to enqueue ingest for copied URL document: {exc}")
        else:
            try:
                payload = storage_client.get_bytes(doc.object_key)
            except Exception as exc:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to read source object: {exc}")
            filename = Path(doc.object_key).name or doc.filename
            new_object_key = f"{new_document_id}/{filename}"
            try:
                storage_client.put_bytes(new_object_key, payload, doc.mime_type)
            except Exception as exc:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to write copied object: {exc}")

            copied = models.DocumentRecord(
                id=new_document_id,
                owner_id=current_user.id,
                notebook_id=new_notebook.id,
                filename=doc.filename,
                object_key=new_object_key,
                mime_type=doc.mime_type,
                size_bytes=doc.size_bytes,
            )
            db.add(copied)
            db.commit()
            db.refresh(copied)
            documents_copied += 1

            try:
                job = _create_job(db, document_id=copied.id, pipeline_version=pipeline_version)
                _enqueue_ingest(job.id, copied.id, copied.object_key, pipeline_version, current_user.username)
                jobs_enqueued += 1
            except Exception as exc:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to enqueue ingest for copied document: {exc}")

    return NotebookCopyResponse(
        notebook=_notebook_response(new_notebook),
        documents_copied=documents_copied,
        jobs_enqueued=jobs_enqueued,
    )


@router.delete("/{notebook_id}")
def delete_notebook(
    notebook_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    nb = db.query(models.Notebook).filter(models.Notebook.id == notebook_id).first()
    if not nb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    if nb.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not owner")
    try:
        doc_ids = [row.id for row in db.query(models.DocumentRecord.id).filter(models.DocumentRecord.notebook_id == nb.id).all()]
        documents = db.query(models.DocumentRecord).filter(models.DocumentRecord.id.in_(doc_ids)).all() if doc_ids else []

        qdrant_client = None
        try:
            from ..ingest.qdrant_store import build_qdrant_client, delete_vectors_for_document
            qdrant_client = build_qdrant_client()
        except Exception:
            pass

        for doc in documents:
            if not doc.object_key.startswith("url://"):
                try:
                    storage_client.delete(doc.object_key)
                except Exception:
                    pass
            if qdrant_client is not None:
                try:
                    delete_vectors_for_document(qdrant_client, doc.id)
                except Exception:
                    pass

        if doc_ids:
            db.query(models.IngestJob).filter(models.IngestJob.document_id.in_(doc_ids)).delete(synchronize_session=False)
            db.query(models.DocumentChunk).filter(models.DocumentChunk.document_id.in_(doc_ids)).delete(synchronize_session=False)
            db.query(models.DocumentRecord).filter(models.DocumentRecord.id.in_(doc_ids)).delete(synchronize_session=False)

        conv_ids = [row.id for row in db.query(models.Conversation.id).filter(models.Conversation.notebook_id == nb.id).all()]
        if conv_ids:
            db.query(models.ChatMessage).filter(models.ChatMessage.conversation_id.in_(conv_ids)).delete(synchronize_session=False)
            db.query(models.Conversation).filter(models.Conversation.id.in_(conv_ids)).delete(synchronize_session=False)

        db.query(models.SavedNotebookItem).filter(models.SavedNotebookItem.notebook_id == nb.id).delete(synchronize_session=False)
        db.delete(nb)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete notebook: {exc}")
    return {"deleted": True}


@router.patch("/{notebook_id}/files/{file_id}/rename")
def rename_file(
    notebook_id: int,
    file_id: str,
    payload: FileRenameRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    # verify notebook ownership/visibility
    nb = db.query(models.Notebook).filter(models.Notebook.id == notebook_id).first()
    if not nb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    if nb.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not owner")

    doc = _get_document_for_notebook(db, notebook_id, file_id, current_user.id)

    try:
        new_name_base = _sanitize_filename(payload.new_file_name)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid new_file_name")

    # preserve extension
    old_filename = Path(doc.filename)
    suffix = old_filename.suffix or ""
    new_filename = f"{new_name_base}{suffix}"

    # compute new object_key: keep document id prefix if object_key follows pattern {doc.id}/{filename}
    try:
        parts = Path(doc.object_key).parts
        if parts and parts[0] == doc.id:
            new_object_key = f"{doc.id}/{new_filename}"
        else:
            # fallback: replace trailing name
            parent = Path(doc.object_key).parent
            new_object_key = str(parent / new_filename)
    except Exception:
        new_object_key = f"{doc.id}/{new_filename}"

    # perform storage rename depending on client capabilities
    try:
        if isinstance(storage_client, LocalStorageClient):
            root = storage_client.root
            old_path = (root / doc.object_key).resolve()
            new_path = (root / new_object_key).resolve()
            if not str(old_path).startswith(str(root.resolve())) or not str(new_path).startswith(str(root.resolve())):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid object path")
            # ensure target directory exists
            new_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                old_path.rename(new_path)
            except FileNotFoundError:
                # allow DB update even if file missing
                pass
        else:
            # generic client: copy bytes then delete
            try:
                payload_bytes = storage_client.get_bytes(doc.object_key)
                storage_client.put_bytes(new_object_key, payload_bytes, doc.mime_type)
                try:
                    storage_client.delete(doc.object_key)
                except Exception:
                    pass
            except FileNotFoundError:
                # missing physical file - proceed with DB update
                pass
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Storage rename failed: {exc}")

    # update DB
    try:
        doc.filename = new_filename
        doc.object_key = new_object_key
        db.commit()
        db.refresh(doc)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update metadata: {exc}")

    return {"file_id": doc.id, "filename": doc.filename, "object_key": doc.object_key}


@router.delete("/{notebook_id}/files/{file_id}")
def delete_file(
    notebook_id: int,
    file_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    # verify notebook & ownership
    nb = db.query(models.Notebook).filter(models.Notebook.id == notebook_id).first()
    if not nb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    if nb.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not owner")

    document = (
        db.query(models.DocumentRecord)
        .filter(models.DocumentRecord.id == file_id, models.DocumentRecord.owner_id == current_user.id, models.DocumentRecord.notebook_id == notebook_id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    cleanup = {"object_deleted": False, "vectors_deleted": False, "metadata_deleted": False}
    errors: list[str] = []

    # delete physical file
    if document.object_key.startswith("url://"):
        cleanup["object_deleted"] = True
    else:
        try:
            # storage_client.delete is idempotent for missing files
            storage_client.delete(document.object_key)
            cleanup["object_deleted"] = True
        except FileNotFoundError:
            # missing on disk - proceed
            cleanup["object_deleted"] = False
        except Exception as exc:
            errors.append(f"storage: {exc}")

    # delete vectors if qdrant available
    try:
        from ..ingest.qdrant_store import build_qdrant_client, delete_vectors_for_document

        client = build_qdrant_client()
        delete_vectors_for_document(client, document.id)
        cleanup["vectors_deleted"] = True
    except Exception:
        # don't fail the whole op if qdrant not configured or delete fails
        errors.append("qdrant: failed or not configured")

    # delete DB rows
    try:
        db.delete(document)
        db.commit()
        cleanup["metadata_deleted"] = True
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete metadata: {exc}")

    return {"deleted": True, "cleanup": cleanup, "errors": errors}
