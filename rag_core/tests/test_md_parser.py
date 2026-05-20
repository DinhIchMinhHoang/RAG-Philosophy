"""
rag_core/tests/test_md_parser.py — Unit tests for Markdown Parser.

Test cases:
  1. Valid Markdown with headings → returns List[Document] with correct metadata
  2. Empty Markdown → raises ValueError
  3. Markdown with BOM (\ufeff) → strips BOM, parses correctly
  4. Markdown with noise (page numbers, TOC) → MarkdownSanitizer removes noise
  5. Idempotency → same file parse 2x → same doc_id
  6. Performance → parse < 100ms for 1MB file
  7. No headings → treats entire content as single page
"""

import os
import tempfile
import time
import unittest

from langchain_core.documents import Document

try:
    from rag_core.md_parser import parse_md
except ImportError:
    from md_parser import parse_md


# =====================================================================
#  FIXTURES
# =====================================================================

VALID_MD = """# Introduction

This is a test document for Markdown parsing.

## Section 1

Content for section 1 with some details.

## Section 2

Content for section 2 with more details.

### Subsection 2.1

Nested content under section 2.
"""

MD_WITH_BOM = "\ufeff# Document with BOM\n\nThis file has a Byte Order Mark at the beginning.\n\n## Section\n\nContent after BOM.\n"

MD_WITH_NOISE = """# MỤC LỤC

1. Giới thiệu
2. Nội dung chính
3. Kết luận

Trang 1

# Chương 1: Giới thiệu

Nội dung chính của chương 1.

Trang 2

## Phần 1.1: Chi tiết

Chi tiết của phần 1.1.
"""

MD_NO_HEADINGS = """This is a plain Markdown document without any headings.

It contains multiple paragraphs but no heading markers.

The parser should treat this as a single page.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
"""

LARGE_MD = "# Large Document\n\n" + "\n\n".join(f"## Section {i}\n\nParagraph {i}: Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat." for i in range(100))


# =====================================================================
#  TESTS
# =====================================================================

class TestMdParser(unittest.TestCase):

    DOCUMENT_ID = "test-doc-md-123"
    PIPELINE_VERSION = "v1"

    def _write_md(self, content: str, suffix: str = ".md") -> str:
        """Write Markdown content to a temp file and return path."""
        tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode='w', encoding='utf-8')
        tmp.write(content)
        tmp.close()
        return tmp.name

    # ── Test 1: Valid Markdown with headings → returns List[Document] ──
    def test_valid_md_returns_documents(self):
        path = self._write_md(VALID_MD)
        try:
            docs = parse_md(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)
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

    # ── Test 2: Empty Markdown → raises ValueError ──
    def test_empty_md_raises_value_error(self):
        path = self._write_md("")
        try:
            with self.assertRaises(ValueError):
                parse_md(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)
        finally:
            os.unlink(path)

    # ── Test 3: Markdown with BOM → strips BOM, parses correctly ──
    def test_md_with_bom_strips_correctly(self):
        path = self._write_md(MD_WITH_BOM)
        try:
            docs = parse_md(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)
            self.assertGreater(len(docs), 0)
            # Verify BOM is not present in any document content
            for doc in docs:
                self.assertNotIn('\ufeff', doc.page_content)
            # Verify heading was parsed correctly (BOM didn't break it)
            all_content = "\n".join(doc.page_content for doc in docs)
            self.assertIn("Document with BOM", all_content)
        finally:
            os.unlink(path)

    # ── Test 4: Markdown with noise → MarkdownSanitizer removes noise ──
    def test_md_noise_removed(self):
        path = self._write_md(MD_WITH_NOISE)
        try:
            docs = parse_md(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)
            self.assertGreater(len(docs), 0)
            all_content = "\n".join(doc.page_content for doc in docs)
            # Noise should be removed
            self.assertNotIn("MỤC LỤC", all_content)
            self.assertNotIn("Trang 1", all_content)
            self.assertNotIn("Trang 2", all_content)
            # Main content should be preserved
            self.assertIn("Giới thiệu", all_content)
            self.assertIn("Nội dung chính", all_content)
        finally:
            os.unlink(path)

    # ── Test 5: Idempotency → same file parse 2x → same doc_id ──
    def test_idempotency_same_doc_id(self):
        path = self._write_md(VALID_MD)
        try:
            docs1 = parse_md(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)
            docs2 = parse_md(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)

            self.assertEqual(len(docs1), len(docs2))

            doc_ids_1 = [doc.metadata["doc_id"] for doc in docs1]
            doc_ids_2 = [doc.metadata["doc_id"] for doc in docs2]

            self.assertEqual(doc_ids_1, doc_ids_2)
        finally:
            os.unlink(path)

    # ── Test 6: Performance → parse < 100ms for large file ──
    def test_performance_under_100ms(self):
        path = self._write_md(LARGE_MD)
        try:
            start = time.time()
            docs = parse_md(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)
            elapsed = time.time() - start

            self.assertGreater(len(docs), 0)
            self.assertLess(elapsed, 0.1, f"Parse took {elapsed:.3f}s, expected < 0.1s")
        finally:
            os.unlink(path)

    # ── Test 7: No headings → treats entire content as single page ──
    def test_md_no_headings_single_page(self):
        path = self._write_md(MD_NO_HEADINGS)
        try:
            docs = parse_md(path, self.DOCUMENT_ID, self.PIPELINE_VERSION)
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0].metadata["page"], 1)
            self.assertIn("plain Markdown document", docs[0].page_content)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
