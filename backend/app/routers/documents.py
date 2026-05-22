"""
Legacy document asset helpers.

Provides read-only endpoints used by old frontend views for page preview/file fetch.
Ingestion/list/reset legacy behavior is now handled by backend.app.routers.ingest.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..core.dependencies import get_current_user
from ..database import get_db
from ..ingest.storage import storage_client
from ..models import DocumentRecord, User
from rag_core.config import Config
# Import rag_service lazily inside endpoints to avoid heavy rag_core imports at module import time.

router = APIRouter(tags=["Documents"])

STREAM_CHUNK_SIZE = 1024 * 1024


def _render_pdf_page_image(pdf_bytes: bytes, page_number: int) -> bytes | None:
    import fitz

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        try:
            page_idx = page_number - 1
            if page_idx < 0 or page_idx >= doc.page_count:
                return None
            page = doc[page_idx]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            return pix.tobytes("png")
        finally:
            doc.close()
    except Exception:
        return None


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


def _inline_headers(
    filename: str,
    size: int,
    *,
    content_range: str | None = None,
    content_length: int | None = None,
) -> dict[str, str]:
    quoted_name = quote(filename)
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Disposition": f"inline; filename*=UTF-8''{quoted_name}",
        "X-Content-Type-Options": "nosniff",
        "Cache-Control": "private, max-age=0, must-revalidate",
    }
    if content_range:
        headers["Content-Range"] = content_range
    if content_length is not None:
        headers["Content-Length"] = str(content_length)
    elif size >= 0:
        headers["Content-Length"] = str(size)
    return headers


def _range_not_satisfiable(size: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_416_RANGE_NOT_SATISFIABLE,
        detail="Range Not Satisfiable",
        headers={
            "Accept-Ranges": "bytes",
            "Content-Range": f"bytes */{size}",
        },
    )


def _parse_range_header(range_header: str | None, size: int) -> tuple[int, int, int, int]:
    if not range_header:
        return 0, max(size - 1, 0), size, status.HTTP_200_OK

    if size <= 0 or not range_header.startswith("bytes=") or "," in range_header:
        raise _range_not_satisfiable(size)

    spec = range_header[6:].strip()
    if "-" not in spec:
        raise _range_not_satisfiable(size)

    start_text, end_text = spec.split("-", 1)
    try:
        if start_text == "":
            suffix_length = int(end_text)
            if suffix_length <= 0:
                raise ValueError
            start = max(size - suffix_length, 0)
            end = size - 1
        else:
            start = int(start_text)
            end = int(end_text) if end_text else size - 1
    except ValueError:
        raise _range_not_satisfiable(size) from None

    if start < 0 or end < start or start >= size:
        raise _range_not_satisfiable(size)

    end = min(end, size - 1)
    length = end - start + 1
    return start, end, length, status.HTTP_206_PARTIAL_CONTENT


def _iter_file_range(
    path: Path,
    start: int,
    length: int,
    chunk_size: int = STREAM_CHUNK_SIZE,
) -> Iterator[bytes]:
    with path.open("rb") as handle:
        handle.seek(start)
        remaining = length
        while remaining > 0:
            chunk = handle.read(min(chunk_size, remaining))
            if not chunk:
                break
            yield chunk
            remaining -= len(chunk)


def _stream_response(
    *,
    body: Iterator[bytes],
    filename: str,
    mime_type: str,
    size: int,
    start: int,
    end: int,
    length: int,
    response_status: int,
) -> StreamingResponse:
    content_range = f"bytes {start}-{end}/{size}" if response_status == status.HTTP_206_PARTIAL_CONTENT else None
    return StreamingResponse(
        body,
        status_code=response_status,
        media_type=mime_type,
        headers=_inline_headers(filename, size, content_range=content_range, content_length=length),
    )


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
    try:
        payload = storage_client.get_bytes(document.object_key)
    except FileNotFoundError:
        payload = None
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load file: {exc}",
        )

    img_bytes = _render_pdf_page_image(payload, page_number) if payload is not None else None
    if img_bytes is None:
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
async def get_document_file(
    request: Request,
    filename: str | None = None,
    document_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document_key = document_id or filename
    if not document_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    document = _authorized_document(db, document_key, current_user)
    mime_type = document.mime_type or "application/octet-stream"
    try:
        size = storage_client.get_size(document.object_key)
    except FileNotFoundError:
        size = None
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load file: {exc}",
        )

    range_header = request.headers.get("range")
    if size is not None:
        start, end, length, response_status = _parse_range_header(range_header, size)
        return _stream_response(
            body=storage_client.iter_bytes(
                document.object_key,
                start=start,
                length=length,
                chunk_size=STREAM_CHUNK_SIZE,
            ),
            filename=document.filename,
            mime_type=mime_type,
            size=size,
            start=start,
            end=end,
            length=length,
            response_status=response_status,
        )

    # Development fallback for legacy files that predate object storage metadata.
    filename = document.filename
    file_path = Path(Config.RAW_DIR) / filename
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    size = file_path.stat().st_size
    start, end, length, response_status = _parse_range_header(range_header, size)
    return _stream_response(
        body=_iter_file_range(file_path, start=start, length=length),
        filename=filename,
        mime_type=mime_type,
        size=size,
        start=start,
        end=end,
        length=length,
        response_status=response_status,
    )
