"""
Legacy document asset helpers.

Provides read-only endpoints used by old frontend views for page preview/file fetch.
Ingestion/list/reset legacy behavior is now handled by backend.app.routers.ingest.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import FileResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..core.dependencies import get_current_user
from ..database import get_db
from ..ingest.storage import storage_client
from ..models import DocumentRecord, User
from rag_core.config import Config
# Import rag_service lazily inside endpoints to avoid heavy rag_core imports at module import time.

router = APIRouter(tags=["Documents"])


def _authorized_document(db: Session, document_key: str, current_user: User) -> DocumentRecord:
    document = (
        db.query(DocumentRecord)
        .filter(
            DocumentRecord.owner_id == current_user.id,
            or_(DocumentRecord.id == document_key, DocumentRecord.filename == document_key),
        )
        .order_by(DocumentRecord.created_at.desc())
        .first()
    )
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    return document


@router.get("/documents/page-image/{filename}/{page_number}")
@router.get("/api/documents/page-image/{filename}/{page_number}")
@router.get("/api/documents/{document_id}/page-image/{page_number}")
async def get_page_image(
    filename: str | None = None,
    document_id: str | None = None,
    page_number: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from ..services.rag_service import rag_service

    document_key = document_id or filename
    if not document_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    document = _authorized_document(db, document_key, current_user)
    img_bytes = rag_service.get_page_image(document.filename, page_number)
    if not img_bytes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page or file not found",
        )
    return Response(content=img_bytes, media_type="image/png")


@router.get("/documents/file/{filename}")
@router.get("/api/documents/file/{filename}")
@router.get("/api/documents/{document_id}/file")
async def get_pdf_file(
    filename: str | None = None,
    document_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document_key = document_id or filename
    if not document_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    document = _authorized_document(db, document_key, current_user)
    try:
        payload = storage_client.get_bytes(document.object_key)
    except FileNotFoundError:
        payload = None
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load file: {exc}",
        )

    if payload is not None:
        quoted_name = quote(document.filename)
        return Response(
            content=payload,
            media_type=document.mime_type or "application/pdf",
            headers={"Content-Disposition": f"inline; filename*=UTF-8''{quoted_name}"},
        )

    # Development fallback for legacy files that predate object storage metadata.
    filename = document.filename
    file_path = Path(Config.RAW_DIR) / filename
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename,
    )
