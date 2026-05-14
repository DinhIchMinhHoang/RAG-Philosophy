from __future__ import annotations

import unittest
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app.ingest.idempotency import delete_chunks_for_document_version
from backend.app.models import DocumentChunk, DocumentRecord


class IdempotencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

        self.document = DocumentRecord(
            id=str(uuid.uuid4()),
            filename="test.pdf",
            object_key="doc/test.pdf",
            mime_type="application/pdf",
            size_bytes=64,
        )
        self.session.add(self.document)
        self.session.commit()

        self.session.add_all(
            [
                DocumentChunk(
                    id=str(uuid.uuid4()),
                    document_id=self.document.id,
                    job_id=None,
                    kind="parent",
                    parent_chunk_id=None,
                    chunk_order=0,
                    text="a",
                    source="test.pdf",
                    page=1,
                    doc_id="doc-a",
                    pipeline_version="1.0.0",
                ),
                DocumentChunk(
                    id=str(uuid.uuid4()),
                    document_id=self.document.id,
                    job_id=None,
                    kind="child",
                    parent_chunk_id="p",
                    chunk_order=1,
                    text="b",
                    source="test.pdf",
                    page=1,
                    doc_id="doc-a",
                    pipeline_version="1.0.0",
                ),
                DocumentChunk(
                    id=str(uuid.uuid4()),
                    document_id=self.document.id,
                    job_id=None,
                    kind="child",
                    parent_chunk_id="p",
                    chunk_order=2,
                    text="c",
                    source="test.pdf",
                    page=2,
                    doc_id="doc-a",
                    pipeline_version="2.0.0",
                ),
            ]
        )
        self.session.commit()

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_delete_chunks_scoped_by_document_and_version(self) -> None:
        deleted = delete_chunks_for_document_version(self.session, self.document.id, "1.0.0")

        self.assertEqual(deleted, 2)
        remaining = self.session.query(DocumentChunk).all()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].pipeline_version, "2.0.0")


if __name__ == "__main__":
    unittest.main()
