from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from backend.app.ingest.storage import LocalStorageClient, MinioStorageClient


class _FakeStat:
    size = 10


class _FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.closed = False
        self.released = False

    def stream(self, chunk_size: int):
        for index in range(0, len(self.payload), chunk_size):
            yield self.payload[index:index + chunk_size]

    def close(self) -> None:
        self.closed = True

    def release_conn(self) -> None:
        self.released = True


class _FakeMinioClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.response = _FakeResponse(b"cdef")

    def stat_object(self, bucket: str, object_key: str) -> _FakeStat:
        self.calls.append({"method": "stat_object", "bucket": bucket, "object_key": object_key})
        return _FakeStat()

    def get_object(self, bucket: str, object_key: str, offset: int = 0, length: int | None = None) -> _FakeResponse:
        self.calls.append(
            {
                "method": "get_object",
                "bucket": bucket,
                "object_key": object_key,
                "offset": offset,
                "length": length,
            }
        )
        return self.response


class StorageRangeTests(unittest.TestCase):
    def test_local_storage_iter_bytes_reads_requested_range(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            client = LocalStorageClient(tmpdir)
            path = Path(tmpdir) / "docs" / "sample.pdf"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"0123456789")

            self.assertEqual(client.get_size("docs/sample.pdf"), 10)
            chunks = list(client.iter_bytes("docs/sample.pdf", start=2, length=4, chunk_size=2))

        self.assertEqual(chunks, [b"23", b"45"])

    def test_minio_storage_uses_ranged_object_fetch(self) -> None:
        fake = _FakeMinioClient()
        client = object.__new__(MinioStorageClient)
        client.bucket = "rag"
        client.client = fake

        self.assertEqual(client.get_size("docs/sample.pdf"), 10)
        chunks = list(client.iter_bytes("docs/sample.pdf", start=2, length=4, chunk_size=2))

        self.assertEqual(chunks, [b"cd", b"ef"])
        self.assertEqual(
            fake.calls,
            [
                {"method": "stat_object", "bucket": "rag", "object_key": "docs/sample.pdf"},
                {
                    "method": "get_object",
                    "bucket": "rag",
                    "object_key": "docs/sample.pdf",
                    "offset": 2,
                    "length": 4,
                },
            ],
        )
        self.assertTrue(fake.response.closed)
        self.assertTrue(fake.response.released)


if __name__ == "__main__":
    unittest.main()
