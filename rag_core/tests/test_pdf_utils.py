import os
import tempfile
import unittest

from rag_core.common.pdf_utils import collect_pdf_paths


class TestPdfUtils(unittest.TestCase):
    def test_collect_pdf_paths_target_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "sample.pdf")
            with open(pdf_path, "wb") as f:
                f.write(b"%PDF-1.4")

            result = collect_pdf_paths(pdf_path, raw_dir=tmpdir)
            self.assertEqual(result, [pdf_path])

    def test_collect_pdf_paths_target_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = os.path.join(tmpdir, "missing.pdf")
            with self.assertRaises(FileNotFoundError):
                collect_pdf_paths(missing, raw_dir=tmpdir)

    def test_collect_pdf_paths_all_pdfs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf1 = os.path.join(tmpdir, "a.pdf")
            pdf2 = os.path.join(tmpdir, "b.PDF")
            txt = os.path.join(tmpdir, "c.txt")
            for path in (pdf1, pdf2, txt):
                with open(path, "wb") as f:
                    f.write(b"data")

            result = collect_pdf_paths(None, raw_dir=tmpdir)
            self.assertCountEqual(result, [pdf1, pdf2])

    def test_collect_pdf_paths_empty_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(FileNotFoundError):
                collect_pdf_paths(None, raw_dir=tmpdir)
