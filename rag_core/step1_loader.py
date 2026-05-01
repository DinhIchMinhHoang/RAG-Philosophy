"""
step1_loader.py — Tri-modal Element-Level Routing Pipeline.

Architecture (designed by Principal Architect):
  1. Layout Analysis : Docling (OCR disabled) → element types + bounding boxes.
  2. Tri-modal Router (per-block, top-to-bottom on each page):
       Track 1 — Native Text : PyMuPDF clip extraction (Text/Title/List).
       Track 2 — VLM         : Crop bbox → base64 → local Qwen3-VL GGUF.
       Track 3 — OCR Fallback: pytesseract, ONLY if Track 1 returns garbage.
  3. Aggregation : Y-axis stitch → MarkdownSanitizer → final Markdown.
"""

from __future__ import annotations

import os
import re
import json
import base64
import logging
import time
import unicodedata
from io import BytesIO
from dataclasses import dataclass, field
from typing import Optional

import fitz  # PyMuPDF  (pymupdf==1.25.5)
from PIL import Image
from openai import OpenAI

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling_core.types.doc import DocItemLabel, CoordOrigin

from config import Config

# ── Logging ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ── State file path ──────────────────────────────────────────────────
_PROCESSED_FILES_PATH: str = os.path.join(Config.DATA_DIR, "processed_files.json")

# ── Element type sets for routing ────────────────────────────────────
_NATIVE_TEXT_LABELS: frozenset[DocItemLabel] = frozenset({
    DocItemLabel.TEXT,
    DocItemLabel.PARAGRAPH,
    DocItemLabel.TITLE,
    DocItemLabel.SECTION_HEADER,
    DocItemLabel.LIST_ITEM,
    DocItemLabel.CAPTION,
    DocItemLabel.FOOTNOTE,
    DocItemLabel.REFERENCE,
    DocItemLabel.DOCUMENT_INDEX,
})

_VLM_LABELS: frozenset[DocItemLabel] = frozenset({
    DocItemLabel.TABLE,
    DocItemLabel.PICTURE,
    DocItemLabel.FORMULA,
    DocItemLabel.CODE,
})

_SKIP_LABELS: frozenset[DocItemLabel] = frozenset({
    DocItemLabel.PAGE_HEADER,
    DocItemLabel.PAGE_FOOTER,
})


# =====================================================================
#  DATA CLASSES
# =====================================================================
@dataclass
class PageElement:
    """A single detected element on a page with its type and position."""
    label: DocItemLabel
    bbox: fitz.Rect          # Always in top-left origin (PyMuPDF coords)
    page_index: int           # 0-indexed
    y_center: float           # For vertical ordering
    source_text: str = ""     # Docling's own text (may be empty)


# =====================================================================
#  MARKDOWN SANITIZER  (preserved from step1_parser.py)
# =====================================================================
class MarkdownSanitizer:
    """
    Xử lý và làm sạch văn bản Markdown trước khi lưu.
    Khắc phục lỗi đứt dòng, heading giả và số trang.
    """

    @staticmethod
    def sanitize(text: str) -> str:
        # 0.1 Normalize Bullets
        text = re.sub(r'(?m)^(\s*)[•▪o]\s+', r'\1- ', text)

        # 0.2 Clean Noise & Aggressive Header/Footer Removal
        text = text.replace('``', '')
        text = text.replace('\x0c', '')  # Form feed
        text = re.sub(
            r'(?m)^\s*(MỤC LỤC|DANH SÁCH HÌNH|DANH SÁCH BẢNG|DANH MỤC|TÀI LIỆU THAM KHẢO)\s*$',
            '', text, flags=re.IGNORECASE,
        )
        text = re.sub(r'(?m)^\s*\d+\s+(CHƯƠNG|PHẦN)\s+.*$', '', text, flags=re.IGNORECASE)

        # 1. Remove Page Numbers
        text = re.sub(r'(?m)^\s*(?:Trang\s+|Page\s+)?\d+\s*$', '', text)

        # 2. Convert Fake Headings to Real Markdown Headings
        text = re.sub(
            r'(?m)^(\s*)(Chương\s+\d+|Phần\s+[IVXLCDM\d]+)[ \t:\.]*(.*)',
            r'\1# \2 \3', text, flags=re.IGNORECASE,
        )
        text = re.sub(r'(?m)^(\s*)(\d+\.\d+\.\d+)(?!\.\d)[ \t:\.]*(.*)', r'\1### \2 \3', text)
        text = re.sub(r'(?m)^(\s*)(\d+\.\d+)(?!\.\d)[ \t:\.]*(.*)', r'\1## \2 \3', text)

        # 2.5 Split Inline Headings
        lines = text.split('\n')
        for i in range(len(lines)):
            if lines[i].lstrip().startswith('#'):
                lines[i] = MarkdownSanitizer._split_inline_heading(lines[i])
        text = '\n'.join(lines)

        # 3. Fix Hard Line Breaks
        text = MarkdownSanitizer._fix_hard_line_breaks(text)

        # 4. TOC Truncation
        match = re.search(
            r'^#\s+(Chương\s+1|Phần\s+(?:1|I))\b',
            text, flags=re.IGNORECASE | re.MULTILINE,
        )
        if match:
            start_idx = match.start()
            nearest_tag = text.rfind('<!--', 0, start_idx)
            text = text[nearest_tag:] if nearest_tag != -1 else text[start_idx:]

        # Clean up excessive empty lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    @staticmethod
    def _split_inline_heading(line: str) -> str:
        upper = "A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲỴÝỶỸ"
        pattern = r'([?\.:])\\s+([' + upper + r'])'
        m = re.search(pattern, line)
        if m:
            idx = m.start(2)
            return line[:idx].strip() + "\n\n" + line[idx:]
        return line

    @staticmethod
    def _fix_hard_line_breaks(text: str) -> str:
        paragraphs = text.split('\n\n')
        fixed = []
        for p in paragraphs:
            lines = p.split('\n')
            if not lines:
                continue
            merged = [lines[0]]
            for i in range(1, len(lines)):
                prev = merged[-1].rstrip()
                curr = lines[i].lstrip()
                if not prev or not curr:
                    merged.append(curr)
                    continue
                if prev[-1] in '.?!:>]':
                    merged.append(curr)
                    continue
                if re.match(r'^\d+\.', curr):
                    merged.append(curr)
                    continue
                if (prev.startswith(('#', '<!--', '-', '*', '>')) or
                        curr.startswith(('#', '<!--', '-', '*', '>'))):
                    merged.append(curr)
                    continue
                merged[-1] = prev + ' ' + curr
            fixed.append('\n'.join(merged))
        return '\n\n'.join(fixed)


# =====================================================================
#  LAYOUT ANALYZER  (Docling, OCR disabled)
# =====================================================================
class LayoutAnalyzer:
    """
    Uses Docling with OCR explicitly disabled to detect element types
    and bounding boxes.  Discards header/footer regions (top/bottom
    MARGIN_CLIP_FRACTION of each page).
    """

    def __init__(self) -> None:
        self._converter: DocumentConverter | None = None

    # ── Lazy Docling init ────────────────────────────────────────
    def _get_converter(self) -> DocumentConverter:
        if self._converter is not None:
            return self._converter

        logger.info("[LayoutAnalyzer] Initialising Docling (OCR disabled)…")
        opts = PdfPipelineOptions(do_ocr=False)
        opts.do_table_structure = True

        self._converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=opts),
            }
        )
        return self._converter

    # ── Public: run layout analysis on a whole PDF ───────────────
    def analyze(
        self,
        file_path: str,
        fitz_doc: fitz.Document,
    ) -> dict[int, list[PageElement]]:
        """
        Returns {page_index: [PageElement, …]} sorted by Y position.
        Elements in header/footer zones are discarded.
        """
        converter = self._get_converter()
        logger.info("[LayoutAnalyzer] Running Docling layout analysis…")
        result = converter.convert(file_path)

        margin_frac: float = Config.MARGIN_CLIP_FRACTION
        elements_by_page: dict[int, list[PageElement]] = {}

        for item, _level in result.document.iterate_items():
            label: DocItemLabel = item.label

            # Skip page headers/footers by label
            if label in _SKIP_LABELS:
                continue

            if not hasattr(item, 'prov') or not item.prov:
                continue

            for prov in item.prov:
                page_no: int = prov.page_no   # 1-indexed from Docling
                page_idx: int = page_no - 1
                if page_idx < 0 or page_idx >= len(fitz_doc):
                    continue

                page_height: float = fitz_doc[page_idx].rect.height
                page_width: float = fitz_doc[page_idx].rect.width
                bb = prov.bbox

                # ── Convert to top-left origin (PyMuPDF) ─────────
                if bb.coord_origin == CoordOrigin.BOTTOMLEFT:
                    rect = fitz.Rect(
                        bb.l,
                        page_height - bb.t,
                        bb.r,
                        page_height - bb.b,
                    )
                else:  # Already TOPLEFT
                    rect = fitz.Rect(bb.l, bb.t, bb.r, bb.b)

                # Normalise (ensure x0<x1, y0<y1)
                rect.normalize()

                # Clamp to page bounds
                rect &= fitz_doc[page_idx].rect

                # ── Header / Footer clipping ─────────────────────
                y_center = (rect.y0 + rect.y1) / 2.0
                top_margin = page_height * margin_frac
                bottom_margin = page_height * (1.0 - margin_frac)
                if y_center < top_margin or y_center > bottom_margin:
                    continue

                # Grab Docling's own text for the element (may be "")
                src_text = ""
                if hasattr(item, "text"):
                    src_text = item.text or ""

                elem = PageElement(
                    label=label,
                    bbox=rect,
                    page_index=page_idx,
                    y_center=y_center,
                    source_text=src_text,
                )
                elements_by_page.setdefault(page_idx, []).append(elem)

        # Sort each page's elements by vertical position (top-to-bottom)
        for page_idx in elements_by_page:
            elements_by_page[page_idx].sort(key=lambda e: e.y_center)

        logger.info(
            f"[LayoutAnalyzer] Detected elements on "
            f"{len(elements_by_page)} pages"
        )
        return elements_by_page


# =====================================================================
#  TRACK 1 — NATIVE TEXT EXTRACTOR  (PyMuPDF clip)
# =====================================================================
class NativeTextExtractor:
    """
    Extracts text natively from the PDF text layer using
    ``page.get_text("text", clip=bbox)``.
    """

    @staticmethod
    def extract(page: fitz.Page, bbox: fitz.Rect) -> str:
        text: str = page.get_text("text", clip=bbox)
        return text.strip()

    @staticmethod
    def is_garbage(text: str) -> bool:
        """
        Returns True if extracted text is empty or extreme garbage
        (indicating a scanned/image-based text block).
        """
        if not text:
            return True
        # If >50% non-printable / control chars → garbage
        printable = sum(1 for c in text if c.isprintable() or c in '\n\t ')
        return printable / max(len(text), 1) < 0.50


# =====================================================================
#  TRACK 2 — VLM EXTRACTOR  (local GGUF via OpenAI-compatible API)
# =====================================================================
class HeavyVLMExtractor:
    """
    Crops a bounding box from the page at high DPI, encodes it as
    base64 PNG, and sends it to a local Qwen3-VL GGUF endpoint
    (LMStudio / llama.cpp server) via the ``openai`` Python client.
    """

    # ── Prompt templates per element type ────────────────────────
    _PROMPTS: dict[str, str] = {
        "table": (
            "Transcribe this table into a well-formatted Markdown table. "
            "Preserve all cell values exactly. Use | delimiters. "
            "Do NOT add commentary — output ONLY the Markdown table."
        ),
        "formula": (
            "Transcribe all mathematical content in this image into LaTeX. "
            "Use $$...$$ for display equations and $...$ for inline math. "
            "Output ONLY the LaTeX — no explanation."
        ),
        "figure": (
            "Describe this figure concisely for an academic document. "
            "Output a Markdown image caption: "
            "![Figure: <brief description>](figure)\n"
            "Then describe key data/trends in 2-3 sentences."
        ),
        "code": (
            "Transcribe this code block exactly into a Markdown fenced "
            "code block with the correct language tag. "
            "Output ONLY the code block — no explanation."
        ),
    }

    _SYSTEM_PROMPT: str = (
        """
        You are a highly precise mathematical OCR engine. Your ONLY task is to extract the mathematical formula from the provided image and convert it into valid LaTeX code.
        CRITICAL RULES - YOU MUST OBEY:
        1. Output ONLY the raw LaTeX code. 
        2. NO explanations, NO conversational text, NO greetings (e.g., do not say "The formula is...", "Here is...").
        3. NEVER output Chinese characters (禁止输出中文) or any natural language words.
        4. Enclose display math in $$...$$ and inline math in $...$.
        5. If the image is blank, unreadable, or not a formula, output exactly this string: [UNREADABLE_MATH]
        """
    )

    def __init__(self) -> None:
        self._client: OpenAI | None = None

    def _get_client(self) -> OpenAI:
        if self._client is None:
            logger.info(
                f"[VLM] Connecting to local endpoint: {Config.VLM_API_BASE}"
            )
            self._client = OpenAI(
                base_url=Config.VLM_API_BASE,
                api_key="not-needed",
            )
        return self._client

    # ── Crop bbox → base64 PNG ───────────────────────────────────
    @staticmethod
    def _crop_to_base64(page: fitz.Page, bbox: fitz.Rect) -> str:
        dpi: int = Config.VLM_IMAGE_DPI
        mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
        pix = page.get_pixmap(matrix=mat, clip=bbox)
        img_bytes: bytes = pix.tobytes("png")
        return base64.b64encode(img_bytes).decode("ascii")

    # ── Public: extract one element ──────────────────────────────
    def extract(
        self,
        page: fitz.Page,
        bbox: fitz.Rect,
        label: DocItemLabel,
    ) -> str:
        """Send cropped image to VLM and return Markdown text."""
        b64 = self._crop_to_base64(page, bbox)

        # Pick the right user prompt
        label_key = {
            DocItemLabel.TABLE: "table",
            DocItemLabel.FORMULA: "formula",
            DocItemLabel.PICTURE: "figure",
            DocItemLabel.CODE: "code",
        }.get(label, "figure")
        user_prompt = self._PROMPTS[label_key]

        try:
            client = self._get_client()
            resp = client.chat.completions.create(
                model=Config.VLM_MODEL_NAME,
                max_tokens=Config.VLM_MAX_TOKENS,
                temperature=0.0,      # BẮT BUỘC: Ép model không sáng tạo
                top_p=0.1,            # BẮT BUỘC: Giảm ngẫu nhiên
                timeout=45.0,         # BẮT BUỘC: Không chờ quá 45 giây
                messages=[
                    {"role": "system", "content": self._SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{b64}",
                                },
                            },
                        ],
                    },
                ],
            )
            result = resp.choices[0].message.content or ""
            
            # Xử lý Escape Hatch nếu ảnh bị hỏng/không đọc được
            if "[UNREADABLE_MATH]" in result:
                logger.warning("[VLM] Model reported UNREADABLE_MATH. Triggering fallback.")
                return "" # Trả về rỗng để kích hoạt fallback ở router
                
            return result.strip()

        except Exception as exc: # Bắt cả lỗi Timeout
            logger.error(f"[VLM] Request failed or timed out: {exc}")
            return "" # Trả về rỗng để Router chuyển sang Track dự phòng


# =====================================================================
#  TRACK 3 — OCR FALLBACK  (pytesseract)
# =====================================================================
class OCRFallbackExtractor:
    """
    Last-resort OCR for text blocks where native extraction returned
    empty/garbage (i.e. scanned image blocks misclassified as text).
    Uses pytesseract with Vietnamese + English language packs.
    """

    @staticmethod
    def extract(page: fitz.Page, bbox: fitz.Rect) -> str:
        try:
            import pytesseract
        except ImportError:
            logger.warning(
                "[OCR] pytesseract not installed — returning empty string"
            )
            return ""

        dpi: int = Config.VLM_IMAGE_DPI
        mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
        pix = page.get_pixmap(matrix=mat, clip=bbox)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        try:
            text: str = pytesseract.image_to_string(img, lang="vie+eng")
            return text.strip()
        except Exception as exc:
            logger.error(f"[OCR] pytesseract failed: {exc}")
            return ""


# =====================================================================
#  DOCUMENT AGGREGATOR  (Orchestrator)
# =====================================================================
class DocumentAggregator:
    """
    Orchestrates the full Tri-modal pipeline:
      1. Open PDF with PyMuPDF.
      2. Run Docling layout analysis (OCR disabled).
      3. Route each element to Track 1 / 2 / 3.
      4. Stitch results in page + Y-axis order.
      5. Apply MarkdownSanitizer.

    Public API mirrors SmartDocumentParser:
      - parse_doc(file_path) → str | None
      - save_markdown(markdown_text, source_filename) → str
    """

    def __init__(self) -> None:
        self._layout = LayoutAnalyzer()
        self._vlm = HeavyVLMExtractor()

    # ── Incremental processing state ─────────────────────────────
    @staticmethod
    def _load_processed_list() -> list[str]:
        if not os.path.exists(_PROCESSED_FILES_PATH):
            return []
        try:
            with open(_PROCESSED_FILES_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(f"[State] Cannot read processed_files.json: {exc}")
            return []

    @staticmethod
    def _save_processed_list(processed: list[str]) -> None:
        os.makedirs(os.path.dirname(_PROCESSED_FILES_PATH), exist_ok=True)
        with open(_PROCESSED_FILES_PATH, "w", encoding="utf-8") as f:
            json.dump(processed, f, ensure_ascii=False, indent=2)
        logger.info(
            f"[State] Updated processed_files.json ({len(processed)} files)"
        )

    # ── Route a single element ───────────────────────────────────
    def _route_element(
        self,
        elem: PageElement,
        page: fitz.Page,
        block_idx: int,
    ) -> str:
        """Route one PageElement through the correct track."""

        # ── Track 2: VLM for visual structures ───────────────────
        if elem.label in _VLM_LABELS:
            logger.info(
                f"  [Block {block_idx}] Track 2 (VLM) — "
                f"{elem.label.value}"
            )
            result = self._vlm.extract(page, elem.bbox, elem.label)
            if result:
                return result
            # VLM failed → try native text as fallback
            logger.warning(
                f"  [Block {block_idx}] VLM returned empty, "
                f"falling back to native text"
            )

        # ── Track 1: Native text extraction ──────────────────────
        text = NativeTextExtractor.extract(page, elem.bbox)

        if not NativeTextExtractor.is_garbage(text):
            logger.info(
                f"  [Block {block_idx}] Track 1 (Native) — "
                f"{elem.label.value} — {len(text)} chars"
            )
            return text

        # ── Track 3: OCR fallback (text was garbage/empty) ───────
        logger.info(
            f"  [Block {block_idx}] Track 3 (OCR Fallback) — "
            f"{elem.label.value}"
        )
        ocr_text = OCRFallbackExtractor.extract(page, elem.bbox)
        return ocr_text

    # ── Main pipeline ────────────────────────────────────────────
    def parse_doc(self, file_path: str) -> str | None:
        """
        Parse a PDF file through the Tri-modal Element-Level Router.

        Returns:
            Cleaned Markdown string, or None if file was already processed.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        source_filename: str = os.path.basename(file_path)

        # Incremental processing check
        processed_list = self._load_processed_list()
        if source_filename in processed_list:
            logger.info(f"⏭️ Skipping (already processed): {source_filename}")
            return None

        doc = fitz.open(file_path)
        logger.info(
            f"🚀 Starting parse: {source_filename} ({doc.page_count} pages)"
        )

        try:
            # ── Stage 1: Layout Analysis ─────────────────────────
            elements_by_page = self._layout.analyze(file_path, doc)

            # ── Stage 2: Tri-modal Routing ───────────────────────
            page_markdowns: dict[int, list[str]] = {}

            for page_idx in range(doc.page_count):
                elements = elements_by_page.get(page_idx, [])
                if not elements:
                    logger.debug(f"Page {page_idx + 1}: no elements detected")
                    continue

                logger.info(
                    f"📄 Page {page_idx + 1}: "
                    f"{len(elements)} elements to route"
                )

                page_blocks: list[str] = []
                for block_idx, elem in enumerate(elements, start=1):
                    block_md = self._route_element(elem, doc[page_idx], block_idx)
                    if block_md:
                        page_blocks.append(block_md)

                if page_blocks:
                    page_markdowns[page_idx] = page_blocks

            # ── Stage 3: Aggregation ─────────────────────────────
            final_blocks: list[str] = []
            for page_idx in range(doc.page_count):
                if page_idx not in page_markdowns:
                    continue
                page_text = "\n\n".join(page_markdowns[page_idx])
                final_blocks.append(
                    f"<!-- Page {page_idx + 1} -->\n{page_text}"
                )

        finally:
            doc.close()

        final_markdown = "\n\n".join(final_blocks)

        # Post-processing
        final_markdown = MarkdownSanitizer.sanitize(final_markdown)

        if final_markdown:
            processed_list.append(source_filename)
            self._save_processed_list(processed_list)

        return final_markdown

    # ── Save to disk ─────────────────────────────────────────────
    @staticmethod
    def save_markdown(markdown_text: str, source_filename: str) -> str:
        os.makedirs(Config.PROCESSED_DIR, exist_ok=True)
        md_filename = os.path.splitext(source_filename)[0] + ".md"
        output_path = os.path.join(Config.PROCESSED_DIR, md_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)

        logger.info(f"💾 Saved Markdown → {output_path}")
        return output_path


# =====================================================================
#  SELF-TEST BLOCK
# =====================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TRI-MODAL ELEMENT-LEVEL ROUTER — SELF TEST")
    print("=" * 60)

    sample_pdf_name = "SML (1) (2).pdf"
    sample_pdf_path = os.path.join(Config.RAW_DIR, sample_pdf_name)

    if not os.path.exists(sample_pdf_path):
        print(f"❌ Test file not found: {sample_pdf_path}")
    else:
        print(f"📄 Processing: {sample_pdf_path}")
        aggregator = DocumentAggregator()

        # Reset incremental state for testing
        processed = aggregator._load_processed_list()
        if sample_pdf_name in processed:
            processed.remove(sample_pdf_name)
            aggregator._save_processed_list(processed)

        start = time.time()
        md_result = aggregator.parse_doc(sample_pdf_path)
        elapsed = time.time() - start

        print("-" * 60)
        print(f"⏱️  Elapsed: {elapsed:.2f}s")

        if md_result:
            out = aggregator.save_markdown(md_result, sample_pdf_name)
            print(f"✅ Success — {len(md_result):,} chars")
            print(f"📂 Saved to: {out}")
        else:
            print("⚠️  No output produced.")

    print("=" * 60)
