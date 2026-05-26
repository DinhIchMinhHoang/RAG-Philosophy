"""CI integration test — upload generated fixtures, verify pipeline end-to-end."""

import json
import os
import sys
import time
import uuid
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

import fitz
import docx
from qdrant_client import QdrantClient

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
API = f"{BASE_URL}/api"
QDRANT_HOST = os.environ.get("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
COLLECTION = os.environ.get("QDRANT_COLLECTION", "rag_philosophy")
POLL_TIMEOUT = int(os.environ.get("CI_POLL_TIMEOUT", "180"))
UPLOAD_TIMEOUT = int(os.environ.get("CI_UPLOAD_TIMEOUT", "300"))

passed = 0
failed = 0


def _check(description: str, ok: bool, detail: str = ""):
    global passed, failed
    if ok:
        passed += 1
        print(f"  PASS  {description}")
    else:
        failed += 1
        print(f"  FAIL  {description}  {detail}")


def _req(method: str, path: str, *, headers=None, body=None, timeout=60):
    url = f"{API}{path}"
    req = Request(url, data=body, method=method)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            ct = resp.headers.get("Content-Type", "")
            if "application/json" in ct:
                return resp.status, json.loads(data)
            return resp.status, data.decode()
    except HTTPError as e:
        body = e.read()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body.decode()


def _multipart(fields: dict, file_field: str, file_path: str, file_mime: str):
    boundary = "----" + uuid.uuid4().hex
    lines = []
    for k, v in fields.items():
        if v is not None:
            lines.append(f"--{boundary}".encode())
            lines.append(f'Content-Disposition: form-data; name="{k}"'.encode())
            lines.append(b"")
            lines.append(str(v).encode())
    fname = Path(file_path).name
    lines.append(f"--{boundary}".encode())
    lines.append(f'Content-Disposition: form-data; name="{file_field}"; filename="{fname}"'.encode())
    lines.append(f"Content-Type: {file_mime}".encode())
    lines.append(b"")
    with open(file_path, "rb") as f:
        lines.append(f.read())
    lines.append(f"--{boundary}--".encode())
    lines.append(b"")
    body = b"\r\n".join(lines)
    ct = f"multipart/form-data; boundary={boundary}"
    return body, ct


def gen_fixtures(tmp_dir: Path):
    fixtures = []

    pdf_path = tmp_dir / "test_fixture.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 100),
        "This is a test PDF document for CI integration testing. "
        "It contains sample text about philosophy and knowledge.",
        fontsize=12,
    )
    doc.save(str(pdf_path))
    doc.close()
    fixtures.append(("pdf", str(pdf_path), "application/pdf"))

    docx_path = tmp_dir / "test_fixture.docx"
    d = docx.Document()
    d.add_paragraph(
        "This is a test DOCX document for CI integration testing. "
        "It discusses the nature of knowledge and belief."
    )
    d.save(str(docx_path))
    fixtures.append(
        (
            "docx",
            str(docx_path),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    )

    html_path = tmp_dir / "test_fixture.html"
    html_content = (
        "<html><body><h1>Test HTML</h1>"
        "<p>This is a test HTML document for CI integration testing.</p>"
        "</body></html>"
    )
    html_path.write_text(html_content, encoding="utf-8")
    fixtures.append(("html", str(html_path), "text/html"))

    md_path = tmp_dir / "test_fixture.md"
    md_content = (
        "# Test Markdown\n\n"
        "This is a test Markdown document for CI integration testing.\n\n"
        "- Item 1\n- Item 2"
    )
    md_path.write_text(md_content, encoding="utf-8")
    fixtures.append(("md", str(md_path), "text/markdown"))

    return fixtures


def register_user():
    username = f"citest_{uuid.uuid4().hex[:6]}"
    email = f"{username}@gmail.com"
    password = "CiTest123!"
    body = json.dumps({"username": username, "email": email, "password": password}).encode()
    status, data = _req("POST", "/signup", headers={"Content-Type": "application/json"}, body=body, timeout=30)
    return status, data


def login_user(email, password):
    body = json.dumps({"email": email, "password": password}).encode()
    status, data = _req("POST", "/login", headers={"Content-Type": "application/json"}, body=body, timeout=30)
    return status, data


def upload_doc(token, filepath, mime):
    fields = {"notebook_id": None, "pipeline_version": None}
    body, ct = _multipart(fields, "file", filepath, mime)
    status, data = _req(
        "POST", "/documents",
        headers={"Authorization": f"Bearer {token}", "Content-Type": ct},
        body=body,
        timeout=UPLOAD_TIMEOUT,
    )
    return status, data


def get_job(token, job_id):
    status, data = _req(
        "GET", f"/jobs/{job_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    return status, data


def check_qdrant():
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        collections = client.get_collections()
        for c in collections.collections:
            if c.name == COLLECTION:
                info = client.get_collection(COLLECTION)
                return info.points_count
        return 0
    except Exception as e:
        print(f"  QDRANT ERROR: {e}")
        return None


def wait_for_job(token, job_id):
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        status, data = get_job(token, job_id)
        if status != 200:
            time.sleep(2)
            continue
        s = data.get("status", "")
        if s == "completed":
            return data
        if s == "failed":
            print(f"  JOB FAILED: {data.get('error_message', 'unknown error')}")
            return data
        time.sleep(2)
    print(f"  TIMEOUT waiting for job {job_id}")
    return None


def main():
    print(f"\nIntegration Tests — {BASE_URL}")
    print("=" * 60)

    print("\n[0] Qdrant baseline check")
    q_count = check_qdrant()
    _check("Qdrant accessible", q_count is not None,
           detail=f"count={q_count}" if q_count is not None else "connection failed")

    print("\n[1] Generate fixtures")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        fixtures = gen_fixtures(tmp_dir)
        _check("Fixtures generated", len(fixtures) == 4,
               detail=f"got {len(fixtures)} fixtures")

        print("\n[2] Register test user")
        status, data = register_user()
        if isinstance(data, dict) and "access_token" in data:
            token = data["access_token"]
            _check("User registered", True, detail=f"status={status}")
        else:
            _check("User registered", False, detail=str(data))
            _check("SKIPPING remaining tests", False, detail="no token")
            print_summary()
            sys.exit(1)

        print("\n[3] Upload fixtures & verify ingest")
        upload_results = []
        for label, fpath, mime in fixtures:
            print(f"  Uploading {label}...")
            status, data = upload_doc(token, fpath, mime)
            if status in (200, 201, 202):
                if isinstance(data, dict) and data.get("status") == "completed":
                    chunks = data.get("chunks", 0) or data.get("pages", 0) or 0
                    upload_results.append(chunks)
                    _check(f"Upload {label}", chunks > 0,
                           detail=f"chunks={chunks}")
                elif isinstance(data, dict) and data.get("status") == "queued":
                    job_id = data.get("job_id", "")
                    print(f"  Job queued: {job_id}, waiting...")
                    result = wait_for_job(token, job_id)
                    if result and result.get("status") == "completed":
                        _check(f"Upload {label}", True,
                               detail="async completed")
                    else:
                        _check(f"Upload {label}", False,
                               detail=f"async failed: {result}")
                else:
                    _check(f"Upload {label}", False,
                           detail=str(data)[:200])
            else:
                _check(f"Upload {label}", False,
                       detail=f"HTTP {status}: {str(data)[:200]}")

        print("\n[4] Qdrant post-ingest check")
        q_count2 = check_qdrant()
        if q_count2 is not None:
            _check("Qdrant has points", q_count2 > 0,
                   detail=f"count={q_count2}")
        else:
            _check("Qdrant has points", False, detail="connection failed")

    print_summary()
    if failed > 0:
        sys.exit(1)


def print_summary():
    total = passed + failed
    print(f"\n{'=' * 60}")
    print(f"  {passed}/{total} passed  ({failed} failed)")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
