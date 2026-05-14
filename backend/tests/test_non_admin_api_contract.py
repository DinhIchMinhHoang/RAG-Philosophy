from __future__ import annotations

import json
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from backend.app import database, models
from backend.app.routers import auth, chat, ingest
from backend.app.services.chat_runtime import RetrievedContext


class _FakeQdrantClient:
    def delete(self, *args, **kwargs):
        return None


class NonAdminApiContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        models.Base.metadata.create_all(self.engine)

        self._orig_ingest_session_local = ingest.SessionLocal
        ingest.SessionLocal = self.SessionLocal

        app = FastAPI()
        app.include_router(auth.router)
        app.include_router(chat.router)
        app.include_router(ingest.router)
        app.include_router(ingest.legacy_router)

        def override_get_db():
            db = self.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[database.get_db] = override_get_db
        app.dependency_overrides[chat.get_db] = override_get_db
        app.dependency_overrides[ingest.get_db] = override_get_db

        self.client = TestClient(app)

    def tearDown(self) -> None:
        ingest.SessionLocal = self._orig_ingest_session_local
        self.engine.dispose()

    def _signup_and_get_token(self) -> str:
        response = self.client.post(
            "/api/signup",
            json={
                "username": "tester",
                "email": "tester@gmail.com",
                "password": "password123",
            },
        )
        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertIn("access_token", payload)
        return payload["access_token"]

    def test_auth_contract_and_legacy_aliases(self) -> None:
        token = self._signup_and_get_token()

        login_response = self.client.post(
            "/login",
            json={"email": "tester@gmail.com", "password": "password123"},
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access_token", login_response.json())

        change_pwd_response = self.client.post(
            "/api/change-password",
            json={"current_password": "password123", "new_password": "password456"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(change_pwd_response.status_code, 200)
        self.assertEqual(change_pwd_response.json()["message"], "Password changed successfully")

    def test_document_lifecycle_contract(self) -> None:
        token = self._signup_and_get_token()
        headers = {"Authorization": f"Bearer {token}"}

        with patch("backend.app.routers.ingest._enqueue_ingest", return_value=None), patch(
            "backend.app.routers.ingest.build_qdrant_client", return_value=_FakeQdrantClient()
        ):
            upload_response = self.client.post(
                "/api/documents",
                headers=headers,
                files={"file": ("sample.pdf", b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n", "application/pdf")},
            )
            self.assertEqual(upload_response.status_code, 202)
            upload_payload = upload_response.json()
            document_id = upload_payload["document_id"]
            job_id = upload_payload["job_id"]

            job_response = self.client.get(f"/api/jobs/{job_id}", headers=headers)
            self.assertEqual(job_response.status_code, 200)
            self.assertEqual(job_response.json()["document_id"], document_id)

            list_response = self.client.get("/api/documents", headers=headers)
            self.assertEqual(list_response.status_code, 200)
            docs = list_response.json()
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0]["document_id"], document_id)
            self.assertIn("latest_job", docs[0])

            delete_response = self.client.delete(f"/api/documents/{document_id}", headers=headers)
            self.assertEqual(delete_response.status_code, 200)
            self.assertTrue(delete_response.json()["deleted"])

            delete_again_response = self.client.delete(f"/api/documents/{document_id}", headers=headers)
            self.assertEqual(delete_again_response.status_code, 200)
            self.assertFalse(delete_again_response.json()["deleted"])
            self.assertEqual(delete_again_response.json()["status"], "not_found")

    def test_chat_contract_non_stream_and_sse(self) -> None:
        token = self._signup_and_get_token()
        headers = {"Authorization": f"Bearer {token}"}

        contexts = [
            RetrievedContext(
                document_id="doc-1",
                chunk_id="chunk-1",
                source="intro.pdf",
                page=3,
                score=0.91,
                snippet="Snippet text",
                text="Full context text",
            )
        ]

        async def _fake_stream_answer(*args, **kwargs):
            for token_value in ["Hello", " world"]:
                yield token_value

        with patch.object(chat.chat_runtime_service, "retrieve", return_value=contexts), patch.object(
            chat.chat_runtime_service,
            "citations_from_context",
            return_value=[
                {
                    "source": "intro.pdf",
                    "page": 3,
                    "snippet": "Snippet text",
                    "document_id": "doc-1",
                    "chunk_id": "chunk-1",
                    "score": 0.91,
                }
            ],
        ), patch.object(chat.chat_runtime_service, "answer", new=AsyncMock(return_value=("Hello world", "gemini"))), patch.object(
            chat.chat_runtime_service, "stream_answer", side_effect=_fake_stream_answer
        ):
            chat_response = self.client.post("/api/chat", headers=headers, json={"message": "test"})
            self.assertEqual(chat_response.status_code, 200)
            payload = chat_response.json()
            self.assertEqual(payload["answer"], "Hello world")
            self.assertEqual(payload["citations"][0]["source"], "intro.pdf")

            sse_response = self.client.post("/api/chat/stream", headers=headers, json={"message": "test"})
            self.assertEqual(sse_response.status_code, 200)
            lines = [line for line in sse_response.text.splitlines() if line.startswith("data: ")]
            self.assertGreaterEqual(len(lines), 2)
            final_payload = json.loads(lines[-1].replace("data: ", ""))
            self.assertTrue(final_payload["done"])
            self.assertEqual(final_payload["type"], "final")
            self.assertIn("citations", final_payload)
            self.assertEqual(final_payload["citations"][0]["source"], "intro.pdf")


if __name__ == "__main__":
    unittest.main()
