from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol

from ..core.settings import settings

# File validation limits
MAX_PDF_SIZE_MB = int(os.getenv("MAX_PDF_SIZE_MB", "100"))
MAX_TABULAR_SIZE_MB = int(os.getenv("MAX_TABULAR_SIZE_MB", "50"))
MAX_DOCX_SIZE_MB = int(os.getenv("MAX_DOCX_SIZE_MB", "50"))
MAX_HTML_SIZE_MB = int(os.getenv("MAX_HTML_SIZE_MB", "50"))
MAX_MD_SIZE_MB = int(os.getenv("MAX_MD_SIZE_MB", "50"))


class StorageClient(Protocol):
    def put_bytes(self, object_key: str, content: bytes, content_type: str) -> None:
        ...

    def get_bytes(self, object_key: str) -> bytes:
        ...

    def delete(self, object_key: str) -> None:
        ...


class LocalStorageClient:
    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve_key(self, object_key: str) -> Path:
        candidate = (self.root / object_key).resolve()
        if not str(candidate).startswith(str(self.root.resolve())):
            raise ValueError("Invalid object_key path")
        return candidate

    def put_bytes(self, object_key: str, content: bytes, content_type: str) -> None:
        path = self._resolve_key(object_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def get_bytes(self, object_key: str) -> bytes:
        path = self._resolve_key(object_key)
        if not path.exists():
            raise FileNotFoundError(f"Object not found: {object_key}")
        return path.read_bytes()

    def delete(self, object_key: str) -> None:
        path = self._resolve_key(object_key)
        if not path.exists():
            return
        path.unlink(missing_ok=True)
        try:
            parent = path.parent
            if parent != self.root and not any(parent.iterdir()):
                parent.rmdir()
        except Exception:
            pass


class MinioStorageClient:
    def __init__(self) -> None:
        try:
            from minio import Minio
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("minio package is required for OBJECT_STORAGE_BACKEND=minio") from exc

        if not settings.minio_endpoint or not settings.minio_access_key or not settings.minio_secret_key or not settings.minio_bucket:
            raise RuntimeError("Missing MinIO configuration: endpoint/access key/secret key/bucket")

        self.bucket = settings.minio_bucket
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def put_bytes(self, object_key: str, content: bytes, content_type: str) -> None:
        from io import BytesIO

        payload = BytesIO(content)
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_key,
            data=payload,
            length=len(content),
            content_type=content_type,
        )

    def get_bytes(self, object_key: str) -> bytes:
        response = self.client.get_object(self.bucket, object_key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def delete(self, object_key: str) -> None:
        try:
            self.client.remove_object(self.bucket, object_key)
        except Exception:
            # Keep deletion idempotent for already removed objects.
            pass



def build_storage_client() -> StorageClient:
    backend = settings.object_storage_backend
    if backend == "local":
        return LocalStorageClient(settings.object_storage_local_root)
    if backend == "minio":
        return MinioStorageClient()
    raise RuntimeError(f"Unsupported OBJECT_STORAGE_BACKEND={backend}")


storage_client = build_storage_client()



def validate_file_bytes(object_key: str, payload: bytes) -> str:
    ext = Path(object_key).suffix.lower()

    if ext not in {'.pdf', '.xlsx', '.xls', '.csv', '.docx', '.html', '.htm', '.md'}:
        raise ValueError(f"Unsupported format: {ext}")

    if ext == '.pdf':
        max_bytes = MAX_PDF_SIZE_MB * 1024 * 1024
        if len(payload) > max_bytes:
            raise ValueError(f"PDF too large (>{MAX_PDF_SIZE_MB} MB)")
        if len(payload) < 5 or payload[:4] != b"%PDF":
            raise ValueError("Invalid PDF format")
    elif ext in ['.xlsx', '.xls']:
        max_bytes = MAX_TABULAR_SIZE_MB * 1024 * 1024
        if len(payload) > max_bytes:
            raise ValueError(f"Excel file too large (>{MAX_TABULAR_SIZE_MB} MB)")
        if ext == '.xlsx' and len(payload) >= 2 and payload[:2] != b'PK':
            raise ValueError("Invalid Excel format")
    elif ext == '.docx':
        max_bytes = MAX_DOCX_SIZE_MB * 1024 * 1024
        if len(payload) > max_bytes:
            raise ValueError(f"DOCX file too large (>{MAX_DOCX_SIZE_MB} MB)")
        if len(payload) >= 2 and payload[:2] != b'PK':
            raise ValueError("Invalid DOCX format")
    elif ext == '.csv':
        max_bytes = MAX_TABULAR_SIZE_MB * 1024 * 1024
        if len(payload) > max_bytes:
            raise ValueError(f"CSV file too large (>{MAX_TABULAR_SIZE_MB} MB)")
        try:
            payload.decode('utf-8')
        except UnicodeDecodeError:
            raise ValueError("Invalid CSV encoding (expected UTF-8)")
    elif ext in ('.html', '.htm'):
        max_bytes = MAX_HTML_SIZE_MB * 1024 * 1024
        if len(payload) > max_bytes:
            raise ValueError(f"HTML file too large (>{MAX_HTML_SIZE_MB} MB)")
        try:
            text = payload[:8192].decode('utf-8', errors='ignore').lower()
            if '<html' not in text and '<!doctype' not in text:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(payload[:8192], 'html.parser')
                if not soup.find(['html', 'head', 'body']):
                    raise ValueError("Invalid HTML format")
        except UnicodeDecodeError:
            raise ValueError("Invalid HTML encoding (expected UTF-8)")
    elif ext == '.md':
        max_bytes = MAX_MD_SIZE_MB * 1024 * 1024
        if len(payload) > max_bytes:
            raise ValueError(f"Markdown file too large (>{MAX_MD_SIZE_MB} MB)")
        try:
            payload.decode('utf-8')
        except UnicodeDecodeError:
            raise ValueError("Invalid Markdown encoding (expected UTF-8)")

    return ext



