"""
Legacy document asset helpers.

Provides read-only endpoints used by old frontend views for page preview/file fetch.
Ingestion/list/reset legacy behavior is now handled by backend.app.routers.ingest.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import FileResponse

from rag_core.config import Config
from ..services.rag_service import rag_service

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/page-image/{filename}/{page_number}")
async def get_page_image(filename: str, page_number: int):
    img_bytes = rag_service.get_page_image(filename, page_number)
    if not img_bytes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page or file not found",
        )
    return Response(content=img_bytes, media_type="image/png")


@router.get("/file/{filename}")
async def get_pdf_file(filename: str):
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
