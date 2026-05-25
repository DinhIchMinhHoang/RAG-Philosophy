from __future__ import annotations

import json
import unittest
from unittest import mock
from urllib import error as urllib_error

from rag_core.config import Config
from rag_core.step1_parser import (
    HybridPDFParser,
    MarkdownSanitizer,
    ZaiLayoutParsingOCREngine,
)


class _FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


class _ConfigPatch:
    def __init__(self, **values: object) -> None:
        self._values = values
        self._originals: dict[str, object] = {}

    def __enter__(self) -> None:
        for key, value in self._values.items():
            self._originals[key] = getattr(Config, key)
            setattr(Config, key, value)

    def __exit__(self, *args: object) -> None:
        for key, value in self._originals.items():
            setattr(Config, key, value)


class TestZaiLayoutParsingOCREngine(unittest.TestCase):
    def test_builds_layout_parsing_request_and_extracts_markdown(self) -> None:
        with _ConfigPatch(
            OCR_PROVIDER="zai",
            OCR_API_BASE_URL="https://example.test/layout_parsing",
            OCR_API_KEY="test-key",
            OCR_MODEL="glm-ocr-test",
            OCR_TIMEOUT_SECONDS=17,
        ):
            captured: dict[str, object] = {}

            def fake_urlopen(req: object, timeout: int) -> _FakeResponse:
                captured["req"] = req
                captured["timeout"] = timeout
                return _FakeResponse({"md_results": "# Parsed\n\nText"})

            with mock.patch(
                "rag_core.step1_parser.urllib_request.urlopen",
                side_effect=fake_urlopen,
            ):
                result = ZaiLayoutParsingOCREngine().ocr_page_image("abc123")

        req = captured["req"]
        body = json.loads(req.data.decode("utf-8"))

        self.assertEqual(result, "# Parsed\n\nText")
        self.assertEqual(req.full_url, "https://example.test/layout_parsing")
        self.assertEqual(req.get_header("Authorization"), "Bearer test-key")
        self.assertEqual(req.get_header("Content-type"), "application/json")
        self.assertEqual(captured["timeout"], 17)
        self.assertEqual(body["model"], "glm-ocr-test")
        self.assertEqual(body["file"], "data:image/png;base64,abc123")

    def test_returns_empty_without_api_key(self) -> None:
        with _ConfigPatch(OCR_PROVIDER="zai", OCR_API_KEY=""):
            with mock.patch("rag_core.step1_parser.urllib_request.urlopen") as urlopen:
                result = ZaiLayoutParsingOCREngine().ocr_page_image("abc123")

        self.assertEqual(result, "")
        urlopen.assert_not_called()

    def test_returns_empty_on_api_error_or_timeout(self) -> None:
        with _ConfigPatch(OCR_PROVIDER="zai", OCR_API_KEY="test-key"):
            with mock.patch(
                "rag_core.step1_parser.urllib_request.urlopen",
                side_effect=urllib_error.URLError("offline"),
            ):
                self.assertEqual(ZaiLayoutParsingOCREngine().ocr_page_image("abc123"), "")

            with mock.patch(
                "rag_core.step1_parser.urllib_request.urlopen",
                side_effect=TimeoutError("slow"),
            ):
                self.assertEqual(ZaiLayoutParsingOCREngine().ocr_page_image("abc123"), "")


class TestMarkdownSanitizer(unittest.TestCase):
    def test_preserves_domain_headings_and_removes_standalone_page_numbers(self) -> None:
        raw = """TÀI LIỆU THAM KHẢO

Page 12

CHƯƠNG 1: Triết học nhập môn

This line is
wrapped mid sentence.

1.2 Numeric heading
"""

        clean = MarkdownSanitizer.sanitize(raw)

        self.assertIn("TÀI LIỆU THAM KHẢO", clean)
        self.assertIn("CHƯƠNG 1: Triết học nhập môn", clean)
        self.assertNotIn("Page 12", clean)
        self.assertIn("This line is wrapped mid sentence.", clean)
        self.assertIn("## 1.2 Numeric heading", clean)


class _FakePage:
    def __init__(
        self,
        *,
        image_bbox: tuple[float, float, float, float] | None = None,
        drawings: int = 0,
        text: str = "",
    ) -> None:
        self._image_bbox = image_bbox
        self._drawings = drawings
        self._text = text

    def get_image_info(self) -> list[dict[str, tuple[float, float, float, float]]]:
        if self._image_bbox is None:
            return []
        return [{"bbox": self._image_bbox}]

    def get_drawings(self) -> list[object]:
        return [object() for _ in range(self._drawings)]

    def get_text(self, mode: str) -> str:
        return self._text


class TestPageClassification(unittest.TestCase):
    def test_classification_uses_configured_image_thresholds(self) -> None:
        page = _FakePage(image_bbox=(0, 0, 25, 25))

        with _ConfigPatch(OCR_MIN_IMAGE_WIDTH=20, OCR_MIN_IMAGE_HEIGHT=20):
            self.assertTrue(HybridPDFParser._classify_page(page))

        with _ConfigPatch(
            OCR_MIN_IMAGE_WIDTH=30,
            OCR_MIN_IMAGE_HEIGHT=30,
            OCR_MIN_VECTOR_DRAWINGS=999,
            OCR_MIN_MATH_SYMBOLS=999,
        ):
            self.assertFalse(HybridPDFParser._classify_page(page))

    def test_classification_uses_configured_drawing_and_math_thresholds(self) -> None:
        with _ConfigPatch(OCR_MIN_VECTOR_DRAWINGS=2):
            self.assertTrue(HybridPDFParser._classify_page(_FakePage(drawings=2)))

        with _ConfigPatch(OCR_MIN_VECTOR_DRAWINGS=999, OCR_MIN_MATH_SYMBOLS=1):
            self.assertTrue(HybridPDFParser._classify_page(_FakePage(text="∑ ∫")))


if __name__ == "__main__":
    unittest.main()
