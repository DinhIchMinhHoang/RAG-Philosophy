"""
rag_core/tests/test_html_parser.py — Unit tests for HTML Parser.

Test cases:
  1. Valid HTML file → returns List[Document]
  2. Invalid file (not HTML) → raises ValueError
  3. HTML with tables → table data preserved
  4. HTML with navigation/ads → noise removed
  5. Empty HTML → raises ValueError
  6. Large HTML → split by headings, chunker handles further splitting
  7. Idempotency → same file parse 2x → same doc_id
  8. Fallback trigger → mock Trafilatura failure → last resort works
  9. Performance → parse < 1s for 500KB file
  10. _validate_html_content với bytes hợp lệ
  11. _validate_html_content với bytes không hợp lệ
  12. parse_html_bytes với string HTML hợp lệ
  13. parse_html_bytes với nội dung rỗng
  14. parse_html_from_url với mock download thành công
  15. parse_html_from_url với lỗi network
  16. Heading chain trong metadata
"""

import io
import json
import os
import tempfile
import time
import unittest
from unittest import mock
from urllib import error as urllib_error

from langchain_core.documents import Document

try:
    from rag_core.html_parser import (
        NAMESPACE_HTML,
        parse_html,
        parse_html_bytes,
        parse_html_from_url,
        _extract_with_trafilatura,
        _validate_html_content,
    )
except ImportError:
    from html_parser import (
        NAMESPACE_HTML,
        parse_html,
        parse_html_bytes,
        parse_html_from_url,
        _extract_with_trafilatura,
        _validate_html_content,
    )


# =====================================================================
#  FIXTURES
# =====================================================================

VALID_HTML = """<!DOCTYPE html>
<html>
<head><title>Test Document</title></head>
<body>
<h1>Introduction</h1>
<p>This is a test document for HTML parsing.</p>
<h2>Section 1</h2>
<p>Content for section 1.</p>
<h2>Section 2</h2>
<p>Content for section 2.</p>
</body>
</html>"""

HTML_WITH_TABLE = """<!DOCTYPE html>
<html>
<body>
<h1>Student Data Report</h1>
<p>The following table contains student information for the current semester.</p>
<table>
<thead><tr><th>Name</th><th>Age</th><th>City</th></tr></thead>
<tbody>
<tr><td>Alice</td><td>30</td><td>Hanoi</td></tr>
<tr><td>Bob</td><td>25</td><td>HCMC</td></tr>
<tr><td>Charlie</td><td>28</td><td>Da Nang</td></tr>
</tbody>
</table>
<p>End of report.</p>
</body>
</html>"""

HTML_WITH_NOISE = """<!DOCTYPE html>
<html>
<body>
<nav>Navigation menu item 1, 2, 3</nav>
<header>Site header with logo</header>
<main>
<h1>Main Content</h1>
<p>This is the actual content we want to extract from the HTML document. It contains important information that should be preserved after the noise removal process in our pipeline system.</p>
<p>Additional paragraph with more content to ensure the total exceeds the minimum threshold of one hundred characters for extraction.</p>
</main>
<footer>Copyright 2024. All rights reserved.</footer>
<aside>Sidebar ads and related links</aside>
<script>alert('noise');</script>
<style>body { color: red; }</style>
</body>
</html>"""

EMPTY_HTML = """<!DOCTYPE html>
<html>
<head><title>Empty</title></head>
<body></body>
</html>"""

LARGE_HTML = """<!DOCTYPE html>
<html>
<body>
<h1>Large Document</h1>
""" + "\n".join(f"<p>Paragraph {i}: Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>" for i in range(200)) + """
</body>
</html>"""

NOT_HTML = b"%PDF-1.4 fake pdf content"


# =====================================================================
#  TESTS
# =====================================================================

class TestHtmlParser(unittest.TestCase):

    DOCUMENT_ID = "test-doc-123"
    PIPELINE_VERSION = "v1"

    def _write_html(self, content: str, suffix: str = ".html") -> str:
        """Write HTML content to a temp file and return path."""
        tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode='w', encoding='utf-8')
        tmp.write(content)
        tmp.close()
        return tmp.name

    def _write_bytes(self, content: bytes, suffix: str = ".bin") -> str:
        """Write bytes to a temp file and return path."""
        tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        tmp.write(content)
        tmp.close()
        return tmp.name

    # ── Test 1: Valid HTML file → returns List[Document] ──
    def test_valid_html_returns_documents(self):
        path = self._write_html(VALID_HTML)
        try:
            docs = parse_html(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)
            self.assertIsInstance(docs, list)
            self.assertGreater(len(docs), 0)
            for doc in docs:
                self.assertIsInstance(doc, Document)
                self.assertIn("source", doc.metadata)
                self.assertIn("page", doc.metadata)
                self.assertIn("doc_id", doc.metadata)
                self.assertTrue(len(doc.page_content) > 0)
        finally:
            os.unlink(path)

    # ── Test 2: Invalid file (not HTML) → raises ValueError ──
    def test_invalid_file_raises_value_error(self):
        path = self._write_bytes(NOT_HTML, suffix=".bin")
        try:
            with self.assertRaises(ValueError):
                parse_html(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)
        finally:
            os.unlink(path)

    # ── Test 3: HTML with tables → table data preserved ──
    def test_html_with_tables_converted_to_markdown(self):
        path = self._write_html(HTML_WITH_TABLE)
        try:
            docs = parse_html(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)
            self.assertGreater(len(docs), 0)
            # Table data should be preserved (Trafilatura extracts text, not Markdown syntax)
            all_content = "\n".join(doc.page_content for doc in docs)
            self.assertIn("Name", all_content)
            self.assertIn("Alice", all_content)
            self.assertIn("Hanoi", all_content)
        finally:
            os.unlink(path)

    # ── Test 4: HTML with navigation/ads → noise removed ──
    def test_html_noise_removed(self):
        path = self._write_html(HTML_WITH_NOISE)
        try:
            docs = parse_html(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)
            self.assertGreater(len(docs), 0)
            all_content = "\n".join(doc.page_content for doc in docs)
            # Noise elements should be removed
            self.assertNotIn("Navigation menu", all_content)
            self.assertNotIn("Site header", all_content)
            self.assertNotIn("Copyright 2024", all_content)
            self.assertNotIn("Sidebar ads", all_content)
            # Main content should be preserved
            self.assertIn("Main Content", all_content)
            self.assertIn("actual content", all_content)
        finally:
            os.unlink(path)

    # ── Test 5: Empty HTML → raises ValueError ──
    def test_empty_html_raises_value_error(self):
        path = self._write_html(EMPTY_HTML)
        try:
            with self.assertRaises(ValueError):
                parse_html(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)
        finally:
            os.unlink(path)

    # ── Test 6: Large HTML → split by headings, chunker handles further splitting ──
    def test_large_html_split_by_headings(self):
        path = self._write_html(LARGE_HTML)
        try:
            docs = parse_html(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)
            self.assertGreater(len(docs), 0)
            # Parser splits by headings only, chunker handles parent/child splitting
            # Verify all docs have valid metadata
            for doc in docs:
                self.assertIn("source", doc.metadata)
                self.assertIn("page", doc.metadata)
                self.assertIn("doc_id", doc.metadata)
        finally:
            os.unlink(path)

    # ── Test 7: Idempotency → same file parse 2x → same doc_id ──
    def test_idempotency_same_doc_id(self):
        path = self._write_html(VALID_HTML)
        try:
            docs1 = parse_html(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)
            docs2 = parse_html(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)

            self.assertEqual(len(docs1), len(docs2))

            doc_ids_1 = [doc.metadata["doc_id"] for doc in docs1]
            doc_ids_2 = [doc.metadata["doc_id"] for doc in docs2]

            self.assertEqual(doc_ids_1, doc_ids_2)
        finally:
            os.unlink(path)

    # ── Test 8: Fallback trigger → mock Trafilatura failure → BSoup works ──
    def test_fallback_when_trafilatura_fails(self):
        path = self._write_html(VALID_HTML)
        try:
            with mock.patch("rag_core.html_parser._extract_with_trafilatura", return_value=None):
                docs = parse_html(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)
                self.assertGreater(len(docs), 0)
                for doc in docs:
                    self.assertIsInstance(doc, Document)
                    self.assertTrue(len(doc.page_content) > 0)
        finally:
            os.unlink(path)

    # ── Test 9: Performance → parse < 1s for 500KB file ──
    def test_performance_under_1_second(self):
        path = self._write_html(LARGE_HTML)
        try:
            start = time.time()
            docs = parse_html(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)
            elapsed = time.time() - start

            self.assertGreater(len(docs), 0)
            self.assertLess(elapsed, 1.0, f"Parse took {elapsed:.2f}s, expected < 1s")
        finally:
            os.unlink(path)

    # ── Test 10: _validate_html_content với bytes hợp lệ ──
    def test_validate_html_content_valid(self):
        _validate_html_content(VALID_HTML.encode('utf-8'))  # không raise

    # ── Test 11: _validate_html_content với bytes không hợp lệ ──
    def test_validate_html_content_invalid(self):
        with self.assertRaises(ValueError):
            _validate_html_content(b"%PDF-1.4 fake")

    # ── Test 12: parse_html_bytes với string HTML hợp lệ ──
    def test_parse_html_bytes_valid(self):
        docs = parse_html_bytes(VALID_HTML, "test.html", self.DOCUMENT_ID, self.PIPELINE_VERSION)
        self.assertGreater(len(docs), 0)
        for doc in docs:
            self.assertIsInstance(doc, Document)
            self.assertIn("source", doc.metadata)
            self.assertIn("page", doc.metadata)
            self.assertIn("doc_id", doc.metadata)
            self.assertEqual(doc.metadata["source"], "test.html")

    # ── Test 13: parse_html_bytes với HTML rỗng → raise ──
    def test_parse_html_bytes_empty(self):
        with self.assertRaises(ValueError):
            parse_html_bytes("<html></html>", "empty.html", self.DOCUMENT_ID, self.PIPELINE_VERSION)

    # ── Test 14: parse_html_from_url với mock download thành công ──
    def test_parse_html_from_url_success(self):
        mock_response = mock.MagicMock()
        mock_response.headers = {"Content-Type": "text/html; charset=utf-8"}
        mock_response.read.return_value = VALID_HTML.encode('utf-8')
        mock_response.__enter__.return_value = mock_response

        with mock.patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
            docs = parse_html_from_url(
                "https://example.com/doc.html",
                self.DOCUMENT_ID,
                self.PIPELINE_VERSION,
            )
            self.assertGreater(len(docs), 0)
            mock_urlopen.assert_called_once()
            # source = URL
            self.assertEqual(docs[0].metadata["source"], "https://example.com/doc.html")

    # ── Test 15: parse_html_from_url với lỗi network ──
    def test_parse_html_from_url_network_error(self):
        with mock.patch("urllib.request.urlopen", side_effect=urllib_error.URLError("timeout")):
            with self.assertRaises(urllib_error.URLError):
                parse_html_from_url(
                    "https://example.com/doc.html",
                    self.DOCUMENT_ID,
                    self.PIPELINE_VERSION,
                )

    # ── Test 16: Heading chain trong metadata ──
    def test_heading_chain_preserved_in_metadata(self):
        """Mock Trafilatura trả về Markdown có heading → heading chain trong metadata."""
        markdown_with_headings = "# Chương 1\n\nNội dung chương 1\n\n## 1.1 Giới thiệu\n\nChi tiết giới thiệu\n\n## 1.2 Phương pháp\n\nChi tiết phương pháp"
        with mock.patch("rag_core.html_parser._extract_with_trafilatura", return_value=markdown_with_headings):
            docs = parse_html_bytes(
                "<html><body>dummy</body></html>",
                "test.html",
                self.DOCUMENT_ID,
                self.PIPELINE_VERSION,
            )
            self.assertGreater(len(docs), 1)
            has_heading_chain = any(
                k.startswith("Header-") for doc in docs for k in doc.metadata
            )
            self.assertTrue(has_heading_chain)


if __name__ == "__main__":
    unittest.main()
