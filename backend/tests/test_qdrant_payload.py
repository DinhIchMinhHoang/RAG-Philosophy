from __future__ import annotations

import unittest
import uuid

from backend.app.ingest.qdrant_store import build_qdrant_payload, deterministic_point_id
from backend.app.models import DocumentChunk


class _FakeQdrantClient:
    def __init__(self, vector_size: int | None = None) -> None:
        self.vector_size = vector_size

    def get_collection(self, collection_name: str):
        if self.vector_size is not None:
            return {"config": {"params": {"vectors": {"size": self.vector_size}}}}
        return {"name": collection_name}

    def create_collection(self, **kwargs):
        return None

    def upsert(self, **kwargs):
        return None


class QdrantPayloadTests(unittest.TestCase):
    def test_payload_includes_required_fields(self) -> None:
        chunk = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id="doc-1",
            job_id="job-1",
            kind="child",
            parent_chunk_id="parent-1",
            chunk_order=1,
            text="chunk text",
            source="paper.pdf",
            page=3,
            doc_id="logical-parent",
            pipeline_version="1.2.3",
        )

        payload = build_qdrant_payload(chunk)

        for key in [
            "document_id",
            "owner_id",
            "notebook_id",
            "doc_id",
            "parent_chunk_id",
            "source",
            "page",
            "pipeline_version",
            "chunk_id",
            "kind",
            "text",
        ]:
            self.assertIn(key, payload)

        self.assertEqual(payload["pipeline_version"], "1.2.3")
        self.assertEqual(payload["source"], "paper.pdf")
        self.assertEqual(payload["page"], 3)

    def test_deterministic_point_id(self) -> None:
        first = deterministic_point_id("doc", "1.0.0", "chunk")
        second = deterministic_point_id("doc", "1.0.0", "chunk")

        self.assertEqual(first, second)
        self.assertNotEqual(first, deterministic_point_id("doc", "1.0.1", "chunk"))
        parsed_uuid = uuid.UUID(first)
        self.assertEqual(str(parsed_uuid), first)

    def test_upsert_rejects_inconsistent_vector_size(self) -> None:
        from backend.app.ingest.qdrant_store import upsert_child_vectors

        chunk = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id="doc-1",
            job_id="job-1",
            kind="child",
            parent_chunk_id="parent-1",
            chunk_order=1,
            text="chunk text",
            source="paper.pdf",
            page=3,
            doc_id="logical-parent",
            pipeline_version="1.2.3",
        )
        client = _FakeQdrantClient()
        with self.assertRaises(ValueError):
            upsert_child_vectors(client, [chunk, chunk], [[0.1, 0.2], [0.1]])

    def test_upsert_rejects_existing_collection_vector_size_mismatch(self) -> None:
        from backend.app.ingest.qdrant_store import upsert_child_vectors

        chunk = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id="doc-1",
            job_id="job-1",
            kind="child",
            parent_chunk_id="parent-1",
            chunk_order=1,
            text="chunk text",
            source="paper.pdf",
            page=3,
            doc_id="logical-parent",
            pipeline_version="1.2.3",
        )
        client = _FakeQdrantClient(vector_size=2)
        with self.assertRaisesRegex(ValueError, "vector size mismatch"):
            upsert_child_vectors(client, [chunk], [[0.1, 0.2, 0.3]])


if __name__ == "__main__":
    unittest.main()
