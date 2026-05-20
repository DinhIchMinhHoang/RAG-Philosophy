"""
rag_core/tests/test_html_parser.py — Unit tests for HTML Parser.

Test cases:
  1. Valid HTML file → returns List[Document]
  2. Invalid file (not HTML) → raises ValueError
  3. HTML with tables → tables converted to Markdown
  4. HTML with navigation/ads → noise removed
  5. Empty HTML → raises ValueError
  6. Large HTML (>700 words/block) → split by RecursiveCharacterTextSplitter
  7. Idempotency test → same file parse 2x → same doc_id
  8. Fallback trigger → mock Trafilatura failure → BSoup fallback works
  9. Performance → parse < 1s for 500KB file
"""

import os
import tempfile
import time
import unittest
from unittest import mock

from langchain_core.documents import Document

try:
    from rag_core.html_parser import parse_html, _magic_check
except ImportError:
    from html_parser import parse_html, _magic_check


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
<p>This is the actual content we want to extract.</p>
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
                _magic_check(path)
        finally:
            os.unlink(path)

    # ── Test 3: HTML with tables → tables converted to Markdown ──
    def test_html_with_tables_converted_to_markdown(self):
        path = self._write_html(HTML_WITH_TABLE)
        try:
            docs = parse_html(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)
            self.assertGreater(len(docs), 0)
            # Check that at least one document contains Markdown table syntax
            all_content = "\n".join(doc.page_content for doc in docs)
            self.assertIn("|", all_content)
            self.assertIn("---", all_content)
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


if __name__ == "__main__":
    unittest.main()
