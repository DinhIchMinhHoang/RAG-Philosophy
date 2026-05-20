from __future__ import annotations

import uuid
from functools import lru_cache
from typing import Iterable

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.http.exceptions import ApiException

from ..core.settings import settings
from ..models import DocumentChunk


def _is_not_found_api_exception(exc: ApiException) -> bool:
    status_code = getattr(exc, "status_code", None)
    if status_code == 404:
        return True
    if exc.args:
        first = exc.args[0]
        if isinstance(first, int) and first == 404:
            return True
        if "404" in str(first):
            return True
    return "404" in str(exc)


def _format_api_exception(exc: ApiException) -> str:
    status_code = getattr(exc, "status_code", None)
    reason = getattr(exc, "reason", None)
    body = getattr(exc, "body", None)
    parts = []
    if status_code is not None:
        parts.append(f"status={status_code}")
    if reason:
        parts.append(f"reason={reason}")
    if body:
        parts.append(f"body={body}")
    if not parts:
        parts.append(repr(exc))
    return "; ".join(parts)



@lru_cache(maxsize=8)
def _cached_qdrant_client(
    qdrant_url: str | None,
    qdrant_host: str,
    qdrant_port: int,
    qdrant_api_key: str | None,
) -> QdrantClient:
    api_key = qdrant_api_key or None
    # Avoid sending API key over plain HTTP; local compose usually uses no auth.
    if qdrant_url and qdrant_url.startswith("http://"):
        api_key = None

    if qdrant_url:
        return QdrantClient(url=qdrant_url, api_key=api_key)
    return QdrantClient(host=qdrant_host, port=qdrant_port, api_key=api_key)


def build_qdrant_client() -> QdrantClient:
    return _cached_qdrant_client(
        settings.qdrant_url,
        settings.qdrant_host,
        settings.qdrant_port,
        settings.qdrant_api_key,
    )


def _ensure_payload_indexes(client: QdrantClient) -> None:
    if not hasattr(client, "create_payload_index"):
        return

    index_specs = {
        "document_id": rest.PayloadSchemaType.KEYWORD,
        "owner_id": rest.PayloadSchemaType.INTEGER,
        "notebook_id": rest.PayloadSchemaType.INTEGER,
        "pipeline_version": rest.PayloadSchemaType.KEYWORD,
        "kind": rest.PayloadSchemaType.KEYWORD,
    }
    for field_name, schema in index_specs.items():
        try:
            client.create_payload_index(
                collection_name=settings.qdrant_collection,
                field_name=field_name,
                field_schema=schema,
            )
        except Exception:
            # Existing indexes and older local clients should not block ingest.
            continue


def ensure_collection(client: QdrantClient, vector_size: int) -> None:
    try:
        client.get_collection(settings.qdrant_collection)
    except Exception:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=rest.VectorParams(size=vector_size, distance=rest.Distance.COSINE),
        )
    _ensure_payload_indexes(client)



def deterministic_point_id(document_id: str, pipeline_version: str, chunk_id: str) -> str:
    raw = f"{document_id}:{pipeline_version}:{chunk_id}"
    # Qdrant accepts UUID/integer ids; UUID5 keeps determinism for idempotent upserts.
    return str(uuid.uuid5(uuid.NAMESPACE_URL, raw))



def build_qdrant_payload(chunk: DocumentChunk) -> dict:
    return {
        "document_id": chunk.document_id,
        "owner_id": chunk.owner_id,
        "notebook_id": chunk.notebook_id,
        "doc_id": chunk.doc_id,
        "parent_chunk_id": chunk.parent_chunk_id,
        "source": chunk.source,
        "page": chunk.page,
        "pipeline_version": chunk.pipeline_version,
        "chunk_id": chunk.id,
        "kind": chunk.kind,
        "text": chunk.text,
    }



def delete_vectors_for_document_version(client: QdrantClient, document_id: str, pipeline_version: str) -> None:
    if not client.collection_exists(settings.qdrant_collection):
        return

    filter_criteria = rest.Filter(
        must=[
            rest.FieldCondition(key="document_id", match=rest.MatchValue(value=document_id)),
            rest.FieldCondition(key="pipeline_version", match=rest.MatchValue(value=pipeline_version)),
        ]
    )

    try:
        client.delete(
            collection_name=settings.qdrant_collection,
            points_selector=rest.FilterSelector(filter=filter_criteria),
            wait=True,
        )
    except ApiException as exc:
        # Treat missing collection/points as idempotent delete.
        if _is_not_found_api_exception(exc):
            return
        raise


def delete_vectors_for_document(client: QdrantClient, document_id: str) -> None:
    if not client.collection_exists(settings.qdrant_collection):
        return

    filter_criteria = rest.Filter(
        must=[
            rest.FieldCondition(key="document_id", match=rest.MatchValue(value=document_id)),
        ]
    )
    try:
        client.delete(
            collection_name=settings.qdrant_collection,
            points_selector=rest.FilterSelector(filter=filter_criteria),
            wait=True,
        )
    except ApiException as exc:
        if _is_not_found_api_exception(exc):
            return
        raise



def upsert_child_vectors(client: QdrantClient, chunks: Iterable[DocumentChunk], vectors: list[list[float]]) -> None:
    chunk_list = list(chunks)
    if len(chunk_list) != len(vectors):
        raise ValueError("chunks and vectors length mismatch")
    if not chunk_list:
        return

    vector_size = len(vectors[0])
    for idx, vector in enumerate(vectors):
        if len(vector) != vector_size:
            raise ValueError(f"inconsistent vector size at index {idx}: got {len(vector)} expected {vector_size}")

    ensure_collection(client, vector_size=vector_size)

    points: list[rest.PointStruct] = []
    for chunk, vector in zip(chunk_list, vectors):
        points.append(
            rest.PointStruct(
                id=deterministic_point_id(chunk.document_id, chunk.pipeline_version, chunk.id),
                vector=vector,
                payload=build_qdrant_payload(chunk),
            )
        )

    try:
        client.upsert(
            collection_name=settings.qdrant_collection,
            points=points,
            wait=True,
        )
    except ApiException as exc:
        raise RuntimeError(f"Qdrant upsert failed: {_format_api_exception(exc)}") from exc
