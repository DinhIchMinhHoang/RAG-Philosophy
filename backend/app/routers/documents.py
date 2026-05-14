"""
documents.py — Router for document/source upload.

POST /documents/upload  — Accept PDF files, ingest them into the RAG pipeline.
GET  /documents/sources — List currently ingested sources.
POST /documents/reset   — Clear all ingested sources and reset the pipeline.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Response
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List

from rag_core.config import Config
# Import rag_service lazily inside endpoints to avoid heavy rag_core imports at module import time.

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/page-image/{filename}/{page_number}")
async def get_page_image(filename: str, page_number: int):
    """Serve a specific page of a PDF as an image."""
    from ..services.rag_service import rag_service
    img_bytes = rag_service.get_page_image(filename, page_number)
    if not img_bytes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page or file not found",
        )
    return Response(content=img_bytes, media_type="image/png")


@router.get("/file/{filename}")
async def get_pdf_file(filename: str):
    """Serve the raw PDF file for native viewer."""
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


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF document to be ingested into the RAG pipeline.
    The file is parsed, chunked, and indexed into the vector store.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided.",
        )

    # Only accept PDF files
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    try:
        file_bytes = await file.read()
        from ..services.rag_service import rag_service
        result = rag_service.ingest_file(file.filename, file_bytes)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}",
        )


@router.get("/sources")
async def list_sources():
    """Return the list of currently ingested source filenames."""
    from ..services.rag_service import rag_service
    return {
        "sources": rag_service.sources,
        "count": rag_service.source_count,
        "has_sources": rag_service.has_sources,
    }


@router.post("/reset")
async def reset_sources():
    """Clear all ingested documents and reset the RAG pipeline."""
    from ..services.rag_service import rag_service
    rag_service.reset()
    return {"message": "All sources cleared. Pipeline reset."}
