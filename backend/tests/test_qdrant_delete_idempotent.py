from __future__ import annotations

import unittest

from qdrant_client.http.exceptions import ApiException

from backend.app.ingest.qdrant_store import (
    delete_vectors_for_document,
    delete_vectors_for_document_version,
)


class _FakeClient:
    def __init__(self, *, exists: bool, delete_exc: Exception | None = None):
        self._exists = exists
        self._delete_exc = delete_exc
        self.delete_called = 0

    def collection_exists(self, collection_name: str) -> bool:
        return self._exists

    def delete(self, **kwargs):
        self.delete_called += 1
        if self._delete_exc is not None:
            raise self._delete_exc
        return None


class QdrantDeleteIdempotentTests(unittest.TestCase):
    def test_skip_delete_when_collection_missing(self) -> None:
        client = _FakeClient(exists=False)
        delete_vectors_for_document_version(client, "doc-1", "1.0.0")
        delete_vectors_for_document(client, "doc-1")
        self.assertEqual(client.delete_called, 0)

    def test_ignore_not_found_error(self) -> None:
        client = _FakeClient(exists=True, delete_exc=ApiException(404, "not found"))
        delete_vectors_for_document_version(client, "doc-1", "1.0.0")
        delete_vectors_for_document(client, "doc-1")
        self.assertEqual(client.delete_called, 2)

    def test_raise_non_404_error(self) -> None:
        client = _FakeClient(exists=True, delete_exc=ApiException(500, "boom"))
        with self.assertRaises(ApiException):
            delete_vectors_for_document_version(client, "doc-1", "1.0.0")


if __name__ == "__main__":
    unittest.main()
