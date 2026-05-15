from __future__ import annotations

from sqlalchemy.orm import Session

from ..ingest.qdrant_store import build_qdrant_client
from ..models import DocumentChunk
from ..core.settings import settings
from qdrant_client.http import models as rest



def retrieve_parent_chunks_by_vector(
    db: Session,
    *,
    query_vector: list[float],
    pipeline_version: str,
    limit: int = 5,
) -> list[DocumentChunk]:
    client = build_qdrant_client()
    search_filter = rest.Filter(
        must=[
            rest.FieldCondition(key="pipeline_version", match=rest.MatchValue(value=pipeline_version)),
            rest.FieldCondition(key="kind", match=rest.MatchValue(value="child")),
        ]
    )

    hits = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_vector,
        query_filter=search_filter,
        limit=limit,
    )

    parent_ids: list[str] = []
    for hit in hits:
        payload = hit.payload or {}
        parent_chunk_id = payload.get("parent_chunk_id")
        if parent_chunk_id:
            parent_ids.append(str(parent_chunk_id))

    if not parent_ids:
        return []

    parents = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.id.in_(parent_ids),
            DocumentChunk.kind == "parent",
            DocumentChunk.pipeline_version == pipeline_version,
        )
        .all()
    )
    return parents
