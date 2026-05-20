from __future__ import annotations

import json
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from backend.app import database, models
from backend.app.routers import auth, chat, documents, ingest, notebooks
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
        app.include_router(documents.router)
        app.include_router(notebooks.router)

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

    def _signup_and_get_token(self, username: str = "tester", email: str = "tester@gmail.com") -> str:
        response = self.client.post(
            "/api/signup",
            json={
                "username": username,
                "email": email,
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
            "/api/login",
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
        notebook_response = self.client.post(
            "/api/notebooks",
            headers=headers,
            json={"title": "Upload target", "is_community": False},
        )
        self.assertEqual(notebook_response.status_code, 201)
        notebook_id = notebook_response.json()["id"]

        with patch("backend.app.routers.ingest._enqueue_ingest", return_value=None), patch(
            "backend.app.routers.ingest.build_qdrant_client", return_value=_FakeQdrantClient()
        ):
            upload_response = self.client.post(
                "/api/documents",
                headers=headers,
                data={"notebook_id": str(notebook_id)},
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
            self.assertEqual(docs[0]["notebook_id"], notebook_id)
            self.assertEqual(docs[0]["owner_id"], 1)
            self.assertIn("latest_job", docs[0])

            delete_response = self.client.delete(f"/api/documents/{document_id}", headers=headers)
            self.assertEqual(delete_response.status_code, 200)
            self.assertTrue(delete_response.json()["deleted"])

            delete_again_response = self.client.delete(f"/api/documents/{document_id}", headers=headers)
            self.assertEqual(delete_again_response.status_code, 200)
            self.assertFalse(delete_again_response.json()["deleted"])
            self.assertEqual(delete_again_response.json()["status"], "not_found")

    def test_document_job_and_file_routes_are_owner_scoped(self) -> None:
        token_a = self._signup_and_get_token("alice", "alice@gmail.com")
        token_b = self._signup_and_get_token("bob", "bob@gmail.com")
        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        db = self.SessionLocal()
        try:
            doc_a = models.DocumentRecord(
                id="doc-a",
                owner_id=1,
                filename="alice.pdf",
                object_key="doc-a/alice.pdf",
                mime_type="application/pdf",
                size_bytes=12,
            )
            doc_b = models.DocumentRecord(
                id="doc-b",
                owner_id=2,
                filename="bob.pdf",
                object_key="doc-b/bob.pdf",
                mime_type="application/pdf",
                size_bytes=12,
            )
            job_b = models.IngestJob(
                id="job-b",
                document_id="doc-b",
                status="queued",
                stage="fetching_object",
                progress_pct=0,
                pipeline_version="1.0.0",
            )
            db.add_all([doc_a, doc_b, job_b])
            db.commit()
        finally:
            db.close()

        list_a = self.client.get("/api/documents", headers=headers_a)
        self.assertEqual(list_a.status_code, 200)
        self.assertEqual([item["document_id"] for item in list_a.json()], ["doc-a"])

        list_b = self.client.get("/api/documents", headers=headers_b)
        self.assertEqual(list_b.status_code, 200)
        self.assertEqual([item["document_id"] for item in list_b.json()], ["doc-b"])

        self.assertEqual(self.client.get("/api/jobs/job-b", headers=headers_a).status_code, 404)
        self.assertEqual(self.client.post("/api/documents/doc-b/reindex", headers=headers_a, json={}).status_code, 404)

        delete_b_as_a = self.client.delete("/api/documents/doc-b", headers=headers_a)
        self.assertEqual(delete_b_as_a.status_code, 200)
        self.assertFalse(delete_b_as_a.json()["deleted"])

        with patch.object(documents.storage_client, "get_bytes", return_value=b"%PDF-1.4\n"):
            own_file = self.client.get("/api/documents/doc-a/file", headers=headers_a)
        self.assertEqual(own_file.status_code, 200)
        self.assertEqual(own_file.headers["content-type"], "application/pdf")

        forbidden_file = self.client.get("/api/documents/doc-b/file", headers=headers_a)
        self.assertEqual(forbidden_file.status_code, 404)

    def test_chat_contract_non_stream_and_sse(self) -> None:
        token = self._signup_and_get_token()
        headers = {"Authorization": f"Bearer {token}"}

        contexts = [
            RetrievedContext(
                document_id="doc-1",
                chunk_id="chunk-1",
                doc_id="doc-key-1",
                source="intro.pdf",
                page=3,
                score=0.91,
                snippet="Snippet text",
                text="Full context text",
            )
        ]

        async def _fake_stream_answer(*args, **kwargs):
            for token_value in ["Hello", " world", " [C1]"]:
                yield token_value

        with patch.object(chat.chat_runtime_service, "rewrite_question", new=AsyncMock(return_value="rewritten test")), patch.object(
            chat.chat_runtime_service, "retrieve", return_value=contexts
        ) as retrieve_mock, patch.object(
            chat.chat_runtime_service,
            "citations_from_context",
            return_value=[
                {
                    "citation_id": "C1",
                    "rank": 1,
                    "source": "intro.pdf",
                    "page": 3,
                    "snippet": "Snippet text",
                    "document_id": "doc-1",
                    "chunk_id": "chunk-1",
                    "doc_id": "doc-key-1",
                    "score": 0.91,
                }
            ],
        ), patch.object(chat.chat_runtime_service, "answer", new=AsyncMock(return_value=("Hello world [C1]", "gemini"))), patch.object(
            chat.chat_runtime_service, "stream_answer", side_effect=_fake_stream_answer
        ):
            chat_response = self.client.post("/api/chat", headers=headers, json={"message": "test"})
            self.assertEqual(chat_response.status_code, 200)
            payload = chat_response.json()
            self.assertEqual(payload["answer"], "Hello world [C1]")
            self.assertEqual(payload["citations"][0]["source"], "intro.pdf")
            self.assertEqual(payload["citations"][0]["citation_id"], "C1")
            self.assertIn("conversation_id", payload)
            self.assertIn("message_id", payload)
            self.assertEqual(payload["rewritten_query"], "rewritten test")

            sse_response = self.client.post(
                "/api/chat/stream",
                headers=headers,
                json={"message": "test", "conversation_id": payload["conversation_id"]},
            )
            self.assertEqual(sse_response.status_code, 200)
            lines = [line for line in sse_response.text.splitlines() if line.startswith("data: ")]
            self.assertGreaterEqual(len(lines), 2)
            final_payload = json.loads(lines[-1].replace("data: ", ""))
            self.assertTrue(final_payload["done"])
            self.assertEqual(final_payload["type"], "final")
            self.assertEqual(final_payload["answer"], "Hello world [C1]")
            self.assertIn("citations", final_payload)
            self.assertEqual(final_payload["citations"][0]["source"], "intro.pdf")
            self.assertEqual(final_payload["citations"][0]["citation_id"], "C1")
            self.assertEqual(final_payload["conversation_id"], payload["conversation_id"])
            self.assertEqual(final_payload["rewritten_query"], "rewritten test")

        self.assertEqual(retrieve_mock.call_args_list[0].args[1], "rewritten test")
        self.assertEqual(retrieve_mock.call_args_list[1].args[1], "rewritten test")
        self.assertEqual(retrieve_mock.call_args_list[0].kwargs["user_id"], 1)
        self.assertIsNone(retrieve_mock.call_args_list[0].kwargs["notebook_id"])

        db = self.SessionLocal()
        try:
            messages = db.query(models.ChatMessage).all()
            self.assertEqual(sum(1 for m in messages if m.role == "user"), 2)
            self.assertEqual(sum(1 for m in messages if m.role == "assistant"), 2)
            self.assertTrue(all(m.rewritten_query == "rewritten test" for m in messages if m.role == "user"))
            assistant_messages = [m for m in messages if m.role == "assistant"]
            self.assertTrue(all(m.sources_used[0]["doc_id"] == "doc-key-1" for m in assistant_messages))
        finally:
            db.close()

    def test_chat_stream_empty_notebook_returns_graceful_final_event(self) -> None:
        token = self._signup_and_get_token()
        headers = {"Authorization": f"Bearer {token}"}
        notebook_response = self.client.post(
            "/api/notebooks",
            headers=headers,
            json={"title": "Empty notebook", "is_community": False},
        )
        self.assertEqual(notebook_response.status_code, 201)
        notebook_id = notebook_response.json()["id"]

        with patch.object(chat.chat_runtime_service, "retrieve", side_effect=AssertionError("retrieve should not run")):
            response = self.client.post(
                "/api/chat/stream",
                headers=headers,
                json={"message": "What is this notebook about?", "notebook_id": notebook_id},
            )

        self.assertEqual(response.status_code, 200)
        lines = [line for line in response.text.splitlines() if line.startswith("data: ")]
        final_payload = json.loads(lines[-1].replace("data: ", ""))
        self.assertEqual(final_payload["type"], "final")
        self.assertTrue(final_payload["done"])
        self.assertEqual(final_payload["answer"], chat.EMPTY_NOTEBOOK_ANSWER)
        self.assertEqual(final_payload["citations"], [])

    def test_chat_stream_runtime_exception_returns_final_error_event(self) -> None:
        token = self._signup_and_get_token()
        headers = {"Authorization": f"Bearer {token}"}

        contexts = [
            RetrievedContext(
                document_id="doc-1",
                chunk_id="chunk-1",
                doc_id="doc-key-1",
                source="intro.pdf",
                page=3,
                score=0.91,
                snippet="Snippet text",
                text="Full context text",
            )
        ]

        async def _broken_stream(*args, **kwargs):
            raise RuntimeError("llm crashed")
            yield ""

        with patch.object(chat.chat_runtime_service, "rewrite_question", new=AsyncMock(return_value="runtime failure")), patch.object(
            chat.chat_runtime_service, "retrieve", return_value=contexts
        ), patch.object(chat.chat_runtime_service, "citations_from_context", return_value=[]), patch.object(
            chat.chat_runtime_service, "stream_answer", side_effect=_broken_stream
        ):
            response = self.client.post("/api/chat/stream", headers=headers, json={"message": "test"})

        self.assertEqual(response.status_code, 200)
        lines = [line for line in response.text.splitlines() if line.startswith("data: ")]
        final_payload = json.loads(lines[-1].replace("data: ", ""))
        self.assertEqual(final_payload["type"], "final")
        self.assertTrue(final_payload["done"])
        self.assertEqual(final_payload["answer"], chat.CHAT_ERROR_ANSWER)
        self.assertEqual(final_payload["error"], "chat_stream_failed")

        db = self.SessionLocal()
        try:
            messages = db.query(models.ChatMessage).all()
            self.assertEqual(sum(1 for m in messages if m.role == "user"), 1)
            self.assertEqual(sum(1 for m in messages if m.role == "assistant"), 0)
        finally:
            db.close()

    def test_notebook_list_uses_integer_community_flag(self) -> None:
        token = self._signup_and_get_token()
        headers = {"Authorization": f"Bearer {token}"}

        create_response = self.client.post(
            "/api/notebooks",
            headers=headers,
            json={"title": "Private notes", "is_community": False},
        )
        self.assertEqual(create_response.status_code, 201)
        self.assertFalse(create_response.json()["is_community"])

        list_response = self.client.get("/api/notebooks", headers=headers)
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.json()[0]["title"], "Private notes")

        db = self.SessionLocal()
        try:
            query = notebooks._visible_notebooks_query(db, user_id=1)
            sql = str(query.statement.compile(dialect=postgresql.dialect()))
        finally:
            db.close()

        self.assertIn("notebooks.is_community = ", sql)
        self.assertNotIn(" OR notebooks.is_community ORDER BY", sql)


if __name__ == "__main__":
    unittest.main()
