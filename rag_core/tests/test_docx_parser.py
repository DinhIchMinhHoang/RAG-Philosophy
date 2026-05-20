import gc
import os
import tempfile
import unittest

from docx import Document

try:
    from rag_core.docx_parser import (
        parse_docx,
        _magic_check,
        _build_virtual_pages,
        _parse_paragraph,
        _serialize_table_md,
        _extract_images,
        _detect_page_breaks,
        _split_by_wordcount,
        _extract_comments,
        _pages_to_documents,
    )
except ImportError:
    from docx_parser import (
        parse_docx,
        _magic_check,
        _build_virtual_pages,
        _parse_paragraph,
        _serialize_table_md,
        _extract_images,
        _detect_page_breaks,
        _split_by_wordcount,
        _extract_comments,
        _pages_to_documents,
    )


def _create_docx(paragraphs: list, use_styles: bool = False) -> str:
    doc = Document()
    for p in paragraphs:
        if isinstance(p, tuple):
            text, level = p
            doc.add_heading(text, level=level)
        else:
            doc.add_paragraph(p)
    path = tempfile.mktemp(suffix='.docx')
    doc.save(path)
    return path


def _create_docx_with_table(headers: list, rows: list) -> str:
    doc = Document()
    table = doc.add_table(rows=1, cols=len(headers))
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
    for row_data in rows:
        row_cells = table.add_row().cells
        for i, val in enumerate(row_data):
            row_cells[i].text = str(val)
    path = tempfile.mktemp(suffix='.docx')
    doc.save(path)
    return path


def _create_docx_with_pagebreak(paragraphs: list) -> str:
    doc = Document()
    for idx, text in enumerate(paragraphs):
        doc.add_paragraph(text)
        if idx < len(paragraphs) - 1:
            para = doc.add_paragraph()
            run = para.add_run()
            run.add_break(Document().element.BREAK_PAGE)
    path = tempfile.mktemp(suffix='.docx')
    doc.save(path)
    return path


def _create_docx_long(word_count: int) -> str:
    doc = Document()
    words = ["word"] * word_count
    text = " ".join(words)
    doc.add_paragraph(text)
    path = tempfile.mktemp(suffix='.docx')
    doc.save(path)
    return path


class TestMagicCheck(unittest.TestCase):
    def test_rejects_binary_ole_file(self):
        with tempfile.NamedTemporaryFile(suffix='.doc', delete=False) as tmp:
            tmp.write(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1')
            tmp_path = tmp.name
        try:
            with self.assertRaises(ValueError) as ctx:
                parse_docx(tmp_path)
            self.assertIn("file signature does not match", str(ctx.exception))
        finally:
            os.unlink(tmp_path)

    def test_rejects_empty_file(self):
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            tmp.write(b'')
            tmp_path = tmp.name
        try:
            with self.assertRaises(ValueError):
                parse_docx(tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_accepts_valid_docx(self):
        path = _create_docx(["Test content"])
        try:
            docs = parse_docx(path)
            self.assertIsInstance(docs, list)
        finally:
            os.unlink(path)


class TestPlainTextParsing(unittest.TestCase):
    def test_parse_returns_non_empty_list(self):
        path = _create_docx([
            "Paragraph 1 content here.",
            "Paragraph 2 content here.",
            "Paragraph 3 content here.",
        ])
        try:
            docs = parse_docx(path)
            self.assertGreater(len(docs), 0)
            full_text = "\n".join(d.page_content for d in docs)
            self.assertIn("Paragraph 1", full_text)
            self.assertIn("Paragraph 2", full_text)
            self.assertIn("Paragraph 3", full_text)
        finally:
            os.unlink(path)


class TestHeadingsParsing(unittest.TestCase):
    def test_heading_levels_extracted(self):
        path = _create_docx([
            ("Heading 1 Text", 1),
            ("Heading 2 Text", 2),
            ("Heading 3 Text", 3),
            "Normal paragraph.",
        ], use_styles=True)
        try:
            docs = parse_docx(path)
            full_text = "\n".join(d.page_content for d in docs)
            self.assertIn("# Heading 1 Text", full_text)
            self.assertIn("## Heading 2 Text", full_text)
            self.assertIn("### Heading 3 Text", full_text)
            self.assertIn("Normal paragraph", full_text)
        finally:
            os.unlink(path)

    def test_paragraph_return_tuple(self):
        path = _create_docx(["Normal paragraph text."])
        try:
            doc = Document(path)
            para = doc.paragraphs[0]
            text, heading = _parse_paragraph(para)
            self.assertIsNotNone(text)
            self.assertIsNone(heading)
        finally:
            os.unlink(path)


class TestMarkdownTableSerialization(unittest.TestCase):
    def test_table_serialize_md_format(self):
        path = _create_docx_with_table(
            headers=["Name", "Age", "City"],
            rows=[["Alice", "25", "Hanoi"], ["Bob", "30", "HCMC"]],
        )
        try:
            docs = parse_docx(path)
            full_text = "\n".join(d.page_content for d in docs)
            self.assertIn("| Name | Age | City |", full_text)
            self.assertIn("| --- | --- | --- |", full_text)
            self.assertIn("| Alice | 25 | Hanoi |", full_text)
            self.assertIn("| Bob | 30 | HCMC |", full_text)
        finally:
            os.unlink(path)

    def test_serialize_table_md_function(self):
        doc = Document()
        table = doc.add_table(rows=2, cols=2)
        table.rows[0].cells[0].text = "A"
        table.rows[0].cells[1].text = "B"
        table.rows[1].cells[0].text = "1"
        table.rows[1].cells[1].text = "2"
        result = _serialize_table_md(table)
        self.assertIn("| A | B |", result)
        self.assertIn("| --- | --- |", result)
        self.assertIn("| 1 | 2 |", result)


class TestPageBreakSplit(unittest.TestCase):
    def test_detect_page_breaks(self):
        path = _create_docx_with_pagebreak(["Page 1 content", "Page 2 content"])
        try:
            doc = Document(path)
            breaks = _detect_page_breaks(doc)
            self.assertIsInstance(breaks, list)
        finally:
            os.unlink(path)


class TestWordCountFallback(unittest.TestCase):
    def test_long_doc_splits_into_multiple_pages(self):
        path = _create_docx_long(2000)
        try:
            docs = parse_docx(path)
            self.assertGreater(len(docs), 1)
        finally:
            os.unlink(path)

    def test_split_by_wordcount(self):
        contents = ["word " * 500]
        pages = _split_by_wordcount(contents, [], 700)
        self.assertGreater(len(pages), 0)
        for page in pages:
            self.assertGreater(len(page.content), 0)


class TestImageExtraction(unittest.TestCase):
    def test_extract_images_from_docx(self):
        path = _create_docx(["Test"])
        try:
            doc = Document(path)
            images = _extract_images(doc)
            self.assertIsInstance(images, list)
            self.assertEqual(len(images), 0)
        finally:
            os.unlink(path)


class TestMemoryCleanup(unittest.TestCase):
    def test_del_doc_and_gc_collect(self):
        path = _create_docx(["Test content for memory cleanup"])
        try:
            doc = Document(path)
            del doc
            gc.collect()
        except Exception as exc:
            self.fail(f"Memory cleanup failed: {exc}")


class TestEmptyDoc(unittest.TestCase):
    def test_empty_doc_returns_empty_list(self):
        doc = Document()
        path = tempfile.mktemp(suffix='.docx')
        doc.save(path)
        try:
            docs = parse_docx(path)
            self.assertEqual(len(docs), 0)
        finally:
            os.unlink(path)


class TestCommentExtraction(unittest.TestCase):
    def test_extract_comments_no_comments(self):
        path = _create_docx(["Paragraph without comments."])
        try:
            doc = Document(path)
            comments = _extract_comments(doc)
            self.assertIsInstance(comments, list)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()