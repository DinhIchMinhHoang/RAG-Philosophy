from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import DocumentChunk



def delete_chunks_for_document_version(db: Session, document_id: str, pipeline_version: str) -> int:
    deleted = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document_id,
            DocumentChunk.pipeline_version == pipeline_version,
        )
        .delete(synchronize_session=False)
    )
    db.commit()
    return int(deleted or 0)
