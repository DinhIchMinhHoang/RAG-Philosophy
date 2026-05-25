"""
step1_parser.py - Hybrid two-pass PDF parser.

Pass 1 scans each page and classifies it as simple or complex.
Pass 2 extracts simple pages with pymupdf4llm and sends rendered complex pages
to the configured OCR provider, falling back to pymupdf4llm/raw text when OCR
is disabled or fails.

Output is a list of LangChain Document objects with {source, page} metadata.
"""

from __future__ import annotations

import base64
import io
import json
import os
import re
import socket
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError, as_completed
from typing import List, Optional, Protocol
from urllib import error as urllib_error
from urllib import request as urllib_request

import fitz
import pymupdf4llm
from langchain_core.documents import Document
from PIL import Image

try:
    from .common.logging_utils import configure_logging, get_logger
    from .config import Config
except ImportError:  # pragma: no cover
    from common.logging_utils import configure_logging, get_logger
    from config import Config

configure_logging()
logger = get_logger(__name__)


class MarkdownSanitizer:
    """Generic Markdown cleanup for parsed PDF text."""

    @staticmethod
    def sanitize(text: str) -> str:
        if not text:
            return ""

        text = MarkdownSanitizer._normalize_bullets(text)
        text = MarkdownSanitizer._remove_control_characters(text)
        text = text.replace("``", "")
        text = re.sub(
            r"(?m)^\s*(?:(?:Page|Trang)\s+)?\d+\s*$",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = MarkdownSanitizer._normalize_numeric_headings(text)
        text = MarkdownSanitizer._fix_hard_line_breaks(text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def _normalize_bullets(text: str) -> str:
        text = re.sub(r"(?m)^(\s*)[•▪‣◦]\s+", r"\1- ", text)
        return re.sub(r"(?m)^(\s*)o\s+", r"\1- ", text)

    @staticmethod
    def _remove_control_characters(text: str) -> str:
        text = text.replace("\x0c", "")
        return re.sub(r"[\x00-\x08\x0b\x0e-\x1f\x7f]", "", text)

    @staticmethod
    def _normalize_numeric_headings(text: str) -> str:
        text = re.sub(
            r"(?m)^(\s*)(\d+\.\d+\.\d+)(?!\.\d)[ \t:\.]*(\S.*)$",
            r"\1### \2 \3",
            text,
        )
        return re.sub(
            r"(?m)^(\s*)(\d+\.\d+)(?!\.\d)[ \t:\.]*(\S.*)$",
            r"\1## \2 \3",
            text,
        )

    @staticmethod
    def _fix_hard_line_breaks(text: str) -> str:
        paragraphs = text.split("\n\n")
        fixed: list[str] = []

        for paragraph in paragraphs:
            lines = paragraph.split("\n")
            if not lines:
                continue

            merged = [lines[0]]
            for line in lines[1:]:
                prev = merged[-1].rstrip()
                curr = line.lstrip()
                if not prev or not curr:
                    merged.append(curr)
                    continue
                if prev[-1] in ".?!:>]":
                    merged.append(curr)
                    continue
                if re.match(r"^\d+\.", curr):
                    merged.append(curr)
                    continue
                if prev.startswith(("#", "<!--", "-", "*", ">")) or curr.startswith(
                    ("#", "<!--", "-", "*", ">")
                ):
                    merged.append(curr)
                    continue
                merged[-1] = f"{prev} {curr}"

            fixed.append("\n".join(merged))

        return "\n\n".join(fixed)


class OCREngine(Protocol):
    def ocr_page_image(self, image_b64: str) -> str:
        ...


class ZaiLayoutParsingOCREngine:
    """Z.AI GLM-OCR layout parsing adapter."""

    def __init__(self) -> None:
        self._disabled_reason: Optional[str] = None
        self._disabled_logged = False

    def _get_disabled_reason(self) -> Optional[str]:
        provider = Config.OCR_PROVIDER.strip().lower()
        if provider != "zai":
            return f"unsupported OCR_PROVIDER={Config.OCR_PROVIDER!r}"
        if not Config.OCR_API_KEY:
            return "OCR_API_KEY is empty"
        if not Config.OCR_API_BASE_URL:
            return "OCR_API_BASE_URL is empty"
        if not Config.OCR_MODEL:
            return "OCR_MODEL is empty"
        return None

    @staticmethod
    def _build_payload(image_b64: str) -> dict[str, str]:
        return {
            "model": Config.OCR_MODEL,
            "file": f"data:image/png;base64,{image_b64}",
        }

    @staticmethod
    def _build_headers() -> dict[str, str]:
        return {
            "Authorization": f"Bearer {Config.OCR_API_KEY}",
            "Content-Type": "application/json",
        }

    def ocr_page_image(self, image_b64: str) -> str:
        reason = self._disabled_reason or self._get_disabled_reason()
        if reason:
            self._disabled_reason = reason
            self._log_disabled_once(reason)
            return ""

        payload = json.dumps(self._build_payload(image_b64)).encode("utf-8")
        req = urllib_request.Request(
            Config.OCR_API_BASE_URL,
            data=payload,
            method="POST",
            headers=self._build_headers(),
        )

        try:
            with urllib_request.urlopen(req, timeout=Config.OCR_TIMEOUT_SECONDS) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            md_text = body.get("md_results", "")
            if isinstance(md_text, str) and md_text.strip():
                logger.info("[ZaiOCR] OK - %d chars", len(md_text))
                return md_text.strip()
            logger.warning("[ZaiOCR] empty md_results")
            return ""
        except urllib_error.HTTPError as exc:
            logger.warning("[ZaiOCR] HTTP %s: %s", exc.code, exc)
            return ""
        except (urllib_error.URLError, TimeoutError, socket.timeout) as exc:
            logger.warning(
                "[ZaiOCR] request failed after %ss: %s",
                Config.OCR_TIMEOUT_SECONDS,
                exc,
            )
            return ""
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.warning("[ZaiOCR] invalid response: %s", exc)
            return ""

    def _log_disabled_once(self, reason: str) -> None:
        if not self._disabled_logged:
            logger.warning("[ZaiOCR] disabled: %s", reason)
            self._disabled_logged = True


class HybridPDFParser:
    """Hybrid two-pass PDF parser with provider-backed OCR for complex pages."""

    _MATH_SYMBOLS: tuple[str, ...] = (
        "∑",
        "∫",
        "lim",
        "∆",
        "∈",
        "∀",
        "∃",
        "≤",
        "≥",
        "≈",
        "∞",
        "∏",
        "√",
        "∂",
        "µ",
        "σ",
        "θ",
        "λ",
        "⊂",
        "⊃",
        "∪",
        "∩",
        "⇒",
        "⇔",
        "→",
        "←",
    )

    def __init__(self, ocr_engine: Optional[OCREngine] = None) -> None:
        self._ocr_engine = ocr_engine or ZaiLayoutParsingOCREngine()

    @staticmethod
    def _classify_page(page: fitz.Page) -> bool:
        for img in page.get_image_info():
            bbox = img.get("bbox")
            if not bbox:
                continue
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            if width > Config.OCR_MIN_IMAGE_WIDTH and height > Config.OCR_MIN_IMAGE_HEIGHT:
                return True

        try:
            if len(page.get_drawings()) >= Config.OCR_MIN_VECTOR_DRAWINGS:
                return True
        except Exception:
            logger.debug("Could not inspect vector drawings", exc_info=True)

        raw_text = page.get_text("text")
        math_count = sum(raw_text.count(symbol) for symbol in HybridPDFParser._MATH_SYMBOLS)
        return math_count > Config.OCR_MIN_MATH_SYMBOLS

    def _scan_and_classify(self, doc: fitz.Document) -> tuple[list[int], list[int]]:
        simple_pages: list[int] = []
        complex_pages: list[int] = []

        for page_idx in range(doc.page_count):
            if self._classify_page(doc[page_idx]):
                complex_pages.append(page_idx)
            else:
                simple_pages.append(page_idx)

        logger.info(
            "Pass 1 classification: %d simple, %d complex",
            len(simple_pages),
            len(complex_pages),
        )
        return simple_pages, complex_pages

    @staticmethod
    def _extract_fast_track(doc: fitz.Document, page_indices: list[int]) -> dict[int, str]:
        if not page_indices:
            return {}

        results: dict[int, str] = {}
        try:
            chunks = pymupdf4llm.to_markdown(
                doc,
                pages=page_indices,
                page_chunks=True,
            )
            for chunk in chunks:
                page_num = chunk.get("metadata", {}).get("page", 0) - 1
                if page_num in page_indices:
                    results[page_num] = chunk.get("text", "")

            for page_num in set(page_indices) - set(results):
                logger.warning(
                    "pymupdf4llm missed page %d; falling back to raw text",
                    page_num + 1,
                )
                results[page_num] = doc[page_num].get_text("text")
        except Exception as exc:
            logger.warning(
                "pymupdf4llm batch failed: %s; falling back to raw text",
                exc,
            )
            for page_num in page_indices:
                results[page_num] = doc[page_num].get_text("text")

        return results

    @staticmethod
    def _compute_content_bbox(page: fitz.Page) -> fitz.Rect:
        blocks = page.get_text("blocks")
        if not blocks:
            return page.rect

        content_blocks = [block for block in blocks if len(block) > 6 and block[6] in (0, 1)]
        if not content_blocks:
            return page.rect

        min_x = min(block[0] for block in content_blocks)
        min_y = min(block[1] for block in content_blocks)
        max_x = max(block[2] for block in content_blocks)
        max_y = max(block[3] for block in content_blocks)
        padding = Config.OCR_CROP_PADDING_POINTS

        return fitz.Rect(
            max(min_x - padding, page.rect.x0),
            max(min_y - padding, page.rect.y0),
            min(max_x + padding, page.rect.x1),
            min(max_y + padding, page.rect.y1),
        )

    @staticmethod
    def _downscale_image_bytes(png_bytes: bytes, max_long_edge: int) -> bytes:
        image = Image.open(io.BytesIO(png_bytes))
        width, height = image.size
        longest = max(width, height)
        if longest <= max_long_edge:
            return png_bytes

        scale = max_long_edge / longest
        new_size = (int(width * scale), int(height * scale))
        image = image.resize(new_size, Image.LANCZOS)
        buf = io.BytesIO()
        image.save(buf, format="PNG", optimize=True)
        logger.debug("Downscaled image %sx%s -> %sx%s", width, height, *new_size)
        return buf.getvalue()

    def _ocr_single_page(self, doc: fitz.Document, page_idx: int) -> tuple[int, str]:
        page = doc[page_idx]
        content_rect = self._compute_content_bbox(page)

        dpi = Config.OCR_RENDER_DPI
        matrix = fitz.Matrix(
            dpi / Config.PDF_POINTS_PER_INCH,
            dpi / Config.PDF_POINTS_PER_INCH,
        )
        pix = page.get_pixmap(matrix=matrix, clip=content_rect)
        image_bytes = pix.tobytes("png")
        image_bytes = self._downscale_image_bytes(image_bytes, Config.OCR_MAX_IMAGE_LONG_EDGE)
        image_b64 = base64.b64encode(image_bytes).decode("ascii")

        try:
            md_text = self._ocr_engine.ocr_page_image(image_b64)
            if md_text:
                logger.info("OCR page %d: %d chars", page_idx + 1, len(md_text))
                return page_idx, md_text
            logger.warning("OCR returned empty for page %d; using fallback", page_idx + 1)
        except Exception as exc:
            logger.warning("OCR failed for page %d: %s; using fallback", page_idx + 1, exc)

        return page_idx, self._fallback_pymupdf(doc, page_idx)

    @staticmethod
    def _fallback_pymupdf(doc: fitz.Document, page_idx: int) -> str:
        logger.info("Fallback pymupdf4llm for page %d", page_idx + 1)
        try:
            return pymupdf4llm.to_markdown(doc, pages=[page_idx])
        except Exception:
            return doc[page_idx].get_text("text")

    def _extract_heavy_track(self, doc: fitz.Document, complex_pages: list[int]) -> dict[int, str]:
        if not complex_pages:
            return {}

        results: dict[int, str] = {}
        max_workers = min(Config.OCR_MAX_WORKERS, len(complex_pages))
        timeout = Config.OCR_TIMEOUT_SECONDS

        logger.info(
            "Heavy track: %d pages, max_workers=%d, timeout=%ss/page",
            len(complex_pages),
            max_workers,
            timeout,
        )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_page = {
                executor.submit(self._ocr_single_page, doc, page_idx): page_idx
                for page_idx in complex_pages
            }

            for future in as_completed(future_to_page):
                submitted_page = future_to_page[future]
                try:
                    page_idx, md_text = future.result(timeout=timeout)
                    results[page_idx] = md_text
                except FutureTimeoutError:
                    logger.error(
                        "Timeout after %ss on page %d; using fallback",
                        timeout,
                        submitted_page + 1,
                    )
                    future.cancel()
                    results[submitted_page] = self._fallback_pymupdf(doc, submitted_page)
                except Exception as exc:
                    logger.error(
                        "Heavy track failed on page %d: %s; using fallback",
                        submitted_page + 1,
                        exc,
                    )
                    results[submitted_page] = self._fallback_pymupdf(doc, submitted_page)

        return results

    def parse_pdf(self, file_path: str) -> List[Document]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF not found: {file_path}")

        source_filename = os.path.basename(file_path)
        doc = fitz.open(file_path)
        total_pages = doc.page_count
        logger.info("Start parsing %s (%d pages)", source_filename, total_pages)

        try:
            simple_pages, complex_pages = self._scan_and_classify(doc)
            page_results: dict[int, str] = {}

            if simple_pages:
                logger.info("Fast track: %d pages via pymupdf4llm", len(simple_pages))
                page_results.update(self._extract_fast_track(doc, simple_pages))

            if complex_pages:
                page_results.update(self._extract_heavy_track(doc, complex_pages))
        finally:
            doc.close()

        documents: List[Document] = []
        for page_idx in range(total_pages):
            raw_md = page_results.get(page_idx, "")
            if not raw_md or not raw_md.strip():
                continue

            clean_md = MarkdownSanitizer.sanitize(raw_md)
            if not clean_md:
                continue

            documents.append(
                Document(
                    page_content=clean_md,
                    metadata={
                        "source": source_filename,
                        "page": page_idx + 1,
                    },
                )
            )

        logger.info("Parse complete: %s -> %d documents", source_filename, len(documents))
        return documents

    @staticmethod
    def save_markdown(documents: List[Document], source_filename: str) -> str:
        os.makedirs(Config.PROCESSED_DIR, exist_ok=True)
        md_filename = os.path.splitext(source_filename)[0] + ".md"
        output_path = os.path.join(Config.PROCESSED_DIR, md_filename)

        full_text = "\n\n".join(doc.page_content for doc in documents)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_text)

        logger.info("Saved Markdown -> %s", output_path)
        return output_path


def parse_pdf(file_path: str) -> List[Document]:
    parser = HybridPDFParser()
    return parser.parse_pdf(file_path)


if __name__ == "__main__":
    print("=" * 60)
    print("HYBRID TWO-PASS PDF PARSER - SELF TEST")
    print("=" * 60)

    sample_pdf_name = "1706.03762v7.pdf"
    sample_pdf_path = os.path.join(Config.RAW_DIR, sample_pdf_name)

    if not os.path.exists(sample_pdf_path):
        print(f"PDF not found: {sample_pdf_path}")
        import glob

        pdfs = glob.glob(os.path.join(Config.RAW_DIR, "*.pdf"))
        if pdfs:
            sample_pdf_path = pdfs[0]
            sample_pdf_name = os.path.basename(sample_pdf_path)
            print(f"Using fallback PDF: {sample_pdf_name}")
        else:
            print(f"No PDF files found in: {Config.RAW_DIR}")
            raise SystemExit(1)

    print(f"\nProcessing: {sample_pdf_path}")

    parser = HybridPDFParser()
    start_time = time.time()
    docs = parser.parse_pdf(sample_pdf_path)
    elapsed = time.time() - start_time

    print("-" * 60)
    print(f"Elapsed: {elapsed:.2f}s")
    print(f"Document objects: {len(docs)}")

    if docs:
        total_chars = sum(len(doc.page_content) for doc in docs)
        print(f"Total chars: {total_chars:,}")
        out_file = parser.save_markdown(docs, sample_pdf_name)
        print(f"Markdown output: {out_file}")
        print(f"\nFirst document metadata: {docs[0].metadata}")
        print(docs[0].page_content[:300])
    else:
        print("No documents were created.")

    print("=" * 60)
