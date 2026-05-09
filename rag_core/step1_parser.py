"""
step1_parser.py — Hybrid Two-Pass Concurrent PDF Parser.

Kiến trúc (Single Responsibility: Parse PDF → List[Document]):
  Pass 1 — Scan & Classify:
       Quét từng trang bằng fitz. Phân loại simple_pages / complex_pages
       dựa trên image blocks, table heuristics, vector drawings (toán học).
  Pass 2 — Execute:
       Fast Track  : pymupdf4llm.to_markdown() cho simple_pages.
       Heavy Track : ThreadPoolExecutor gọi Ollama (glm-ocr) song song
                     cho complex_pages với Smart Cropping bounding box.
  Output: List[Document] (langchain_core) kèm metadata {source, page}.
"""

from __future__ import annotations

import base64
import io
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
from typing import List, Optional

from PIL import Image

import fitz
import pymupdf4llm
from langchain_community.chat_models import ChatOllama
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from rag_core.common.logging_utils import configure_logging, get_logger
from rag_core.config import Config

configure_logging()
logger = get_logger(__name__)


# =====================================================================
#  MARKDOWN SANITIZER
# =====================================================================
class MarkdownSanitizer:
    """
    Xử lý và làm sạch văn bản Markdown trước khi đóng gói.
    Khắc phục lỗi đứt dòng, heading giả, số trang, và nhiễu OCR.
    """

    @staticmethod
    def sanitize(text: str) -> str:
        """Chạy toàn bộ pipeline làm sạch Markdown."""
        if not text:
            return ""

        # 0.1 Normalize Bullets
        text = re.sub(r'(?m)^(\s*)[•▪o]\s+', r'\1- ', text)

        # 0.2 Clean Noise & Aggressive Header/Footer Removal
        text = text.replace('``', '')
        text = text.replace('\x0c', '')  # Form feed
        text = re.sub(
            r'(?m)^\s*(MỤC LỤC|DANH SÁCH HÌNH|DANH SÁCH BẢNG|DANH MỤC|TÀI LIỆU THAM KHẢO)\s*$',
            '', text, flags=re.IGNORECASE,
        )
        text = re.sub(
            r'(?m)^\s*\d+\s+(CHƯƠNG|PHẦN)\s+.*$',
            '', text, flags=re.IGNORECASE,
        )

        # 1. Remove Page Numbers
        text = re.sub(r'(?m)^\s*(?:Trang\s+|Page\s+)?\d+\s*$', '', text)

        # 2. Convert Fake Headings to Real Markdown Headings
        text = re.sub(
            r'(?m)^(\s*)(Chương\s+\d+|Phần\s+[IVXLCDM\d]+)[ \t:\.]*(.*)',
            r'\1# \2 \3', text, flags=re.IGNORECASE,
        )
        text = re.sub(
            r'(?m)^(\s*)(\d+\.\d+\.\d+)(?!\.\d)[ \t:\.]*(.*)',
            r'\1### \2 \3', text,
        )
        text = re.sub(
            r'(?m)^(\s*)(\d+\.\d+)(?!\.\d)[ \t:\.]*(.*)',
            r'\1## \2 \3', text,
        )

        # 2.5 Split Inline Headings
        lines = text.split('\n')
        for i in range(len(lines)):
            if lines[i].lstrip().startswith('#'):
                lines[i] = MarkdownSanitizer._split_inline_heading(lines[i])
        text = '\n'.join(lines)

        # 3. Fix Hard Line Breaks
        text = MarkdownSanitizer._fix_hard_line_breaks(text)

        # 4. TOC Truncation (cắt bỏ mục lục đầu file)
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
        """Tách heading bị dính paragraph text trên cùng dòng."""
        upper_chars = (
            "A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯ"
            "ẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲỴÝỶỸ"
        )
        pattern = r'([?\.:])\\s+([' + upper_chars + r'])'
        m = re.search(pattern, line)
        if m:
            idx = m.start(2)
            return line[:idx].strip() + "\n\n" + line[idx:]
        return line

    @staticmethod
    def _fix_hard_line_breaks(text: str) -> str:
        """Nối các dòng bị ngắt cứng giữa chừng câu."""
        paragraphs = text.split('\n\n')
        fixed: list[str] = []
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
#  OLLAMA LLM OCR ENGINE  (Heavy Track helper)
# =====================================================================
class OllamaOCREngine:
    """
    Gọi model glm-ocr qua Ollama để trích xuất nội dung từ ảnh trang PDF.
    Sử dụng ChatOllama từ langchain_community với đúng format multimodal.
    """

    _SYSTEM_PROMPT: str = (
        '''
        Bạn là một chuyên gia số hóa tài liệu học thuật. Nhiệm vụ của bạn là trích xuất chính xác nội dung từ ảnh sang định dạng Markdown.
        1. Giữ nguyên cấu trúc phân cấp (Headers #, ##).
        2. Chuyển đổi bảng biểu sang Markdown table hoàn chỉnh.
        3. Sử dụng LaTeX: $inline$ cho công thức trong dòng và $$display$$ cho công thức độc lập.
        4. Tuyệt đối không thêm lời dẫn, không giải thích, không hội thoại dư thừa.
        '''
    )

    def __init__(self) -> None:
        self._llm: Optional[ChatOllama] = None

    def _get_llm(self) -> ChatOllama:
        """Lazy-init ChatOllama client."""
        if self._llm is None:
            logger.info(
                f"[OllamaOCR] Kết nối tới {Config.OLLAMA_BASE_URL} "
                f"model={Config.OLLAMA_MODEL_NAME}"
            )
            self._llm = ChatOllama(
                base_url=Config.OLLAMA_BASE_URL,
                model=Config.OLLAMA_MODEL_NAME,
                temperature=0.0,
            )
        return self._llm

    def ocr_page_image(self, image_b64: str) -> str:
        """
        Gửi ảnh base64 tới Ollama và trả về Markdown.

        Uses the LangChain-community ChatOllama multimodal format:
        image_url dict with data-URI string → the converter splits on
        the comma and passes the raw base64 into Ollama's 'images' field.

        Args:
            image_b64: Chuỗi base64-encoded PNG của trang PDF.

        Returns:
            Markdown text trích xuất được, hoặc chuỗi rỗng nếu lỗi.
        """
        llm = self._get_llm()
        # LangChain-community ChatOllama multimodal payload:
        #   image_url.url = "data:<mime>;base64,<data>" — the internal
        #   converter splits on ',' and feeds component[1] to Ollama.
        messages = [
            SystemMessage(content=self._SYSTEM_PROMPT),
            HumanMessage(
                content=[
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}",
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            '''
                            Hãy thực hiện OCR cho ảnh tài liệu này:
                            1. Trích xuất toàn bộ văn bản, bảng biểu và công thức toán học.
                            2. Đảm bảo các ký hiệu toán học phức tạp được chuyển sang LaTeX chính xác.
                            3. Nếu có bảng, hãy tái cấu trúc đúng định dạng bảng Markdown.
                            4. Đầu ra: Chỉ trả về nội dung Markdown.
                            '''
                        ),
                    },
                ],
            ),
        ]
        try:
            response = llm.invoke(messages)
            return (response.content or "").strip()
        except Exception as exc:
            logger.error(f"[OllamaOCR] LLM call failed: {exc}")
            return ""


# =====================================================================
#  HYBRID TWO-PASS CONCURRENT PDF PARSER
# =====================================================================
class HybridPDFParser:
    """
    Bộ phân tích PDF lai sử dụng kiến trúc Two-Pass Concurrent.

    Pass 1 — Scan & Classify:
        Quét mọi trang bằng fitz, phân loại simple / complex dựa trên:
        - Có image block hay không
        - Có nhiều vector drawings (≥ 15) → table/biểu đồ/toán
        - Có ký hiệu toán học đặc trưng hay không

    Pass 2 — Execute:
        Fast Track  : pymupdf4llm cho simple pages (tuần tự).
        Heavy Track : Smart Crop + Ollama OCR (song song qua ThreadPoolExecutor).

    Output: List[Document] với metadata {"source": ..., "page": ...}
    """

    def __init__(self) -> None:
        self._ocr_engine = OllamaOCREngine()

    # ────────────────────────────────────────────────────────────────
    #  PASS 1 — PAGE CLASSIFICATION
    # ────────────────────────────────────────────────────────────────

    @staticmethod
    def _classify_page(page: fitz.Page) -> bool:
        """
        Phân loại 1 trang: True = complex, False = simple.

        Heuristics:
          1. Trang chứa image block → complex.
          2. Trang có ≥ 15 vector drawings (đường nét, hình vẽ) → complex.
          3. Trang chứa nhiều ký hiệu toán học (> 3) → complex.
        """
        # Check 1: Image blocks (bỏ qua logo nhỏ/watermark)
        images = page.get_image_info()
        for img in images:
            bbox = img.get("bbox")
            if bbox:
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                if w > 50 and h > 50:
                    return True

        # Check 2: Vector drawings (tables, diagrams, math figures)
        try:
            drawings = page.get_drawings()
            if len(drawings) >= 15:
                return True
        except Exception:
            pass

        # Check 3: Math symbols in text layer
        raw_text = page.get_text("text")
        math_symbols = [
            '∑', '∫', 'lim', '∆', '∈', '∀', '∃', '≤', '≥',
            '≈', '∞', '∏', '√', '∂', 'µ', 'σ', 'θ', 'λ',
            '⊂', '⊃', '∪', '∩', '⇒', '⇔', '→', '←',
        ]
        math_count = sum(raw_text.count(sym) for sym in math_symbols)
        if math_count > 3:
            return True

        return False

    def _scan_and_classify(
        self, doc: fitz.Document,
    ) -> tuple[list[int], list[int]]:
        """
        Pass 1: Quét toàn bộ trang, trả về (simple_pages, complex_pages).

        Args:
            doc: fitz.Document đã mở.

        Returns:
            Tuple (simple_page_indices, complex_page_indices).
        """
        simple_pages: list[int] = []
        complex_pages: list[int] = []

        for page_idx in range(doc.page_count):
            page = doc[page_idx]
            if self._classify_page(page):
                complex_pages.append(page_idx)
            else:
                simple_pages.append(page_idx)

        logger.info(
            f"📊 Pass 1 Classification: "
            f"{len(simple_pages)} simple, {len(complex_pages)} complex"
        )
        return simple_pages, complex_pages

    # ────────────────────────────────────────────────────────────────
    #  PASS 2A — FAST TRACK  (pymupdf4llm)
    # ────────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_fast_track(
        doc: fitz.Document,
        page_indices: list[int],
    ) -> dict[int, str]:
        """
        Trích xuất Markdown từ simple pages bằng pymupdf4llm.

        Args:
            doc: fitz.Document đã mở.
            page_indices: Danh sách page index (0-based) cần xử lý.

        Returns:
            Dict {page_index: markdown_text}.
        """
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
            
            # Identify missing pages in the results due to errors
            missing = set(page_indices) - set(results.keys())
            for page_num in missing:
                logger.warning(
                    f"⚠️ pymupdf4llm thiếu trang {page_num + 1}. "
                    f"Fallback sang fitz raw text."
                )
                results[page_num] = doc[page_num].get_text("text")

        except Exception as exc:
            logger.warning(
                f"⚠️ pymupdf4llm batch processing thất bại: {exc}. "
                f"Fallback sang fitz raw text."
            )
            for page_num in page_indices:
                results[page_num] = doc[page_num].get_text("text")

        return results

    # ────────────────────────────────────────────────────────────────
    #  PASS 2B — HEAVY TRACK  (Smart Crop + Ollama OCR, Concurrent)
    # ────────────────────────────────────────────────────────────────

    @staticmethod
    def _compute_content_bbox(page: fitz.Page) -> fitz.Rect:
        """
        Smart Crop: Tính bounding box nội dung chính của trang,
        bỏ vùng header/footer nhiễu.

        Dùng page.get_text("blocks") để tìm vùng chứa nội dung thực sự,
        sau đó mở rộng thêm lề nhỏ cho an toàn.

        Args:
            page: fitz.Page cần tính bbox.

        Returns:
            fitz.Rect là vùng nội dung chính.
        """
        blocks = page.get_text("blocks")  # (x0, y0, x1, y1, text, block_no, type)
        if not blocks:
            return page.rect

        # Lọc chỉ text blocks (type == 0) và image blocks (type == 1)
        content_blocks = [b for b in blocks if b[6] in (0, 1)]
        if not content_blocks:
            return page.rect

        # Tính union bounding box của tất cả content blocks
        min_x = min(b[0] for b in content_blocks)
        min_y = min(b[1] for b in content_blocks)
        max_x = max(b[2] for b in content_blocks)
        max_y = max(b[3] for b in content_blocks)

        # Thêm padding nhỏ (5 points) để tránh cắt sát nội dung
        padding = 5.0
        content_rect = fitz.Rect(
            max(min_x - padding, page.rect.x0),
            max(min_y - padding, page.rect.y0),
            min(max_x + padding, page.rect.x1),
            min(max_y + padding, page.rect.y1),
        )
        return content_rect

    @staticmethod
    def _downscale_image_bytes(
        png_bytes: bytes, max_long_edge: int,
    ) -> bytes:
        """
        Downscale ảnh PNG nếu cạnh dài nhất vượt *max_long_edge* px.
        Trả về PNG bytes (giữ nguyên nếu đã nhỏ hơn ngưỡng).
        """
        img = Image.open(io.BytesIO(png_bytes))
        w, h = img.size
        longest = max(w, h)
        if longest <= max_long_edge:
            return png_bytes  # already within budget

        scale = max_long_edge / longest
        new_w, new_h = int(w * scale), int(h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        logger.debug(
            f"  📐 Downscaled image {w}×{h} → {new_w}×{new_h}"
        )
        return buf.getvalue()

    def _ocr_single_page(
        self,
        doc: fitz.Document,
        page_idx: int,
    ) -> tuple[int, str]:
        """
        Xử lý OCR 1 trang complex: Smart Crop → render ảnh → downscale
        → Ollama VLM → Markdown.
        Hàm này được gọi song song trong ThreadPoolExecutor.

        Args:
            doc: fitz.Document (thread-safe cho read operations).
            page_idx: Index trang (0-based).

        Returns:
            Tuple (page_idx, markdown_text).
        """
        page = doc[page_idx]

        # Smart Crop: tính bbox nội dung chính
        content_rect = self._compute_content_bbox(page)

        # Render ảnh theo bbox đã crop, sử dụng DPI từ config
        dpi = Config.DPI_FOR_OCR
        mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
        pix = page.get_pixmap(matrix=mat, clip=content_rect)
        img_bytes: bytes = pix.tobytes("png")

        # ── Image Optimization: cap longest edge ──────────────
        img_bytes = self._downscale_image_bytes(
            img_bytes, Config.MAX_IMAGE_LONG_EDGE,
        )
        image_b64: str = base64.b64encode(img_bytes).decode("ascii")

        # ── Gọi Ollama OCR với hard timeout ───────────────────
        try:
            md_text = self._ocr_engine.ocr_page_image(image_b64)
            if md_text:
                logger.info(
                    f"  ✅ OCR trang {page_idx + 1}: {len(md_text)} chars"
                )
                return page_idx, md_text
            else:
                logger.warning(
                    f"  ⚠️ VLM trả về rỗng cho trang {page_idx + 1}. "
                    f"Fallback sang pymupdf4llm."
                )
        except Exception as exc:
            logger.warning(
                f"  ⚠️ Ollama OCR lỗi trang {page_idx + 1}: {exc}. "
                f"Fallback sang pymupdf4llm."
            )

        # Fallback: pymupdf4llm
        return page_idx, self._fallback_pymupdf(doc, page_idx)

    @staticmethod
    def _fallback_pymupdf(doc: fitz.Document, page_idx: int) -> str:
        """Fallback trích xuất: pymupdf4llm → fitz raw text."""
        logger.info(f"  🔄 Fallback pymupdf4llm cho trang {page_idx + 1}")
        try:
            return pymupdf4llm.to_markdown(doc, pages=[page_idx])
        except Exception:
            return doc[page_idx].get_text("text")

    def _extract_heavy_track(
        self,
        doc: fitz.Document,
        complex_pages: list[int],
    ) -> dict[int, str]:
        """
        Heavy Track: Gọi Ollama OCR song song cho các trang complex.
        Mỗi page có hard timeout = Config.VLM_TIMEOUT_SECONDS giây.

        Args:
            doc: fitz.Document đã mở.
            complex_pages: Danh sách page index (0-based).

        Returns:
            Dict {page_index: markdown_text}.
        """
        if not complex_pages:
            return {}

        results: dict[int, str] = {}
        max_workers = min(Config.OLLAMA_MAX_WORKERS, len(complex_pages))
        timeout = Config.VLM_TIMEOUT_SECONDS

        logger.info(
            f"🏋️ Heavy Track: {len(complex_pages)} trang, "
            f"max_workers={max_workers}, timeout={timeout}s/page"
        )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_page = {
                executor.submit(
                    self._ocr_single_page, doc, page_idx,
                ): page_idx
                for page_idx in complex_pages
            }

            for future in as_completed(future_to_page):
                submitted_page = future_to_page[future]
                try:
                    # ── Hard timeout per page ─────────────────
                    page_idx, md_text = future.result(
                        timeout=timeout,
                    )
                    results[page_idx] = md_text
                except TimeoutError:
                    logger.error(
                        f"⏱️ Timeout ({timeout}s) trang "
                        f"{submitted_page + 1}. Fallback pymupdf4llm."
                    )
                    future.cancel()
                    results[submitted_page] = self._fallback_pymupdf(
                        doc, submitted_page,
                    )
                except Exception as exc:
                    logger.error(
                        f"❌ Heavy Track thất bại trang "
                        f"{submitted_page + 1}: {exc}. Fallback pymupdf4llm."
                    )
                    results[submitted_page] = self._fallback_pymupdf(
                        doc, submitted_page,
                    )

        return results

    # ────────────────────────────────────────────────────────────────
    #  PUBLIC API — parse_pdf → List[Document]
    # ────────────────────────────────────────────────────────────────

    def parse_pdf(self, file_path: str) -> List[Document]:
        """
        Hàm public chính — Parse PDF thành List[Document] của LangChain.

        Mỗi Document chứa:
          - page_content: Markdown đã sanitize.
          - metadata: {"source": tên_file, "page": số_trang_1_indexed}

        Args:
            file_path: Đường dẫn tuyệt đối tới file PDF.

        Returns:
            List[Document] — danh sách Document theo thứ tự trang.

        Raises:
            FileNotFoundError: Nếu file không tồn tại.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

        source_filename: str = os.path.basename(file_path)
        doc = fitz.open(file_path)
        total_pages = doc.page_count

        logger.info(
            f"🚀 Bắt đầu parse: {source_filename} ({total_pages} trang)"
        )

        try:
            # ── Pass 1: Scan & Classify ──────────────────────────
            simple_pages, complex_pages = self._scan_and_classify(doc)

            # ── Pass 2: Execute ──────────────────────────────────
            page_results: dict[int, str] = {}

            # Fast Track
            if simple_pages:
                logger.info(
                    f"⚡ Fast Track: {len(simple_pages)} trang "
                    f"via pymupdf4llm"
                )
                fast_results = self._extract_fast_track(doc, simple_pages)
                page_results.update(fast_results)

            # Heavy Track (concurrent)
            if complex_pages:
                heavy_results = self._extract_heavy_track(doc, complex_pages)
                page_results.update(heavy_results)

        finally:
            doc.close()

        # ── Assembly & Sanitization → List[Document] ─────────────
        documents: List[Document] = []

        for page_idx in range(total_pages):
            raw_md = page_results.get(page_idx, "")
            if not raw_md or not raw_md.strip():
                continue

            # Sanitize Markdown
            clean_md = MarkdownSanitizer.sanitize(raw_md)
            if not clean_md:
                continue

            documents.append(
                Document(
                    page_content=clean_md,
                    metadata={
                        "source": source_filename,
                        "page": page_idx + 1,     # 1-indexed cho end-user
                    },
                )
            )

        logger.info(
            f"✅ Parse hoàn tất: {source_filename} → "
            f"{len(documents)} Document objects"
        )
        return documents

    @staticmethod
    def save_markdown(documents: List[Document], source_filename: str) -> str:
        """
        Lưu danh sách Document thành một file Markdown duy nhất để kiểm tra.
        """
        os.makedirs(Config.PROCESSED_DIR, exist_ok=True)
        md_filename = os.path.splitext(source_filename)[0] + ".md"
        output_path = os.path.join(Config.PROCESSED_DIR, md_filename)

        # Nối tất cả page_content lại với nhau
        full_text = "\n\n".join(doc.page_content for doc in documents)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_text)

        logger.info(f"💾 Đã lưu Markdown → {output_path}")
        return output_path


# =====================================================================
#  CONVENIENCE FUNCTION  (cho import dễ dàng)
# =====================================================================

def parse_pdf(file_path: str) -> List[Document]:
    """
    Hàm tiện ích cấp module — tạo parser và parse ngay.

    Args:
        file_path: Đường dẫn tới file PDF.

    Returns:
        List[Document] kèm metadata {source, page}.
    """
    parser = HybridPDFParser()
    return parser.parse_pdf(file_path)


# =====================================================================
#  SELF-TEST BLOCK
# =====================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 HYBRID TWO-PASS CONCURRENT PDF PARSER — SELF TEST")
    print("=" * 60)

    sample_pdf_name = "1706.03762v7.pdf"
    sample_pdf_path = os.path.join(Config.RAW_DIR, sample_pdf_name)

    if not os.path.exists(sample_pdf_path):
        print(f"❌ Không tìm thấy file test: {sample_pdf_path}")
        # Thử file khác
        import glob
        pdfs = glob.glob(os.path.join(Config.RAW_DIR, "*.pdf"))
        if pdfs:
            sample_pdf_path = pdfs[0]
            sample_pdf_name = os.path.basename(sample_pdf_path)
            print(f"📄 Sử dụng file thay thế: {sample_pdf_name}")
        else:
            print(f"❌ Không có file PDF nào trong: {Config.RAW_DIR}")
            exit(1)

    print(f"\n📄 Đang xử lý: {sample_pdf_path}")

    parser = HybridPDFParser()

    start_time = time.time()
    docs = parser.parse_pdf(sample_pdf_path)
    elapsed = time.time() - start_time

    print("-" * 60)
    print(f"⏱️  Thời gian xử lý: {elapsed:.2f}s")
    print(f"📊 Số Document objects: {len(docs)}")

    if docs:
        total_chars = sum(len(d.page_content) for d in docs)
        print(f"📝 Tổng ký tự: {total_chars:,}")
        
        # Lưu ra file markdown
        out_file = parser.save_markdown(docs, sample_pdf_name)
        print(f"📂 Đã xuất file ra: {out_file}")

        # In mẫu Document đầu tiên
        print(f"\n📗 MẪU DOCUMENT #0:")
        print(f"   Metadata: {docs[0].metadata}")
        print(f"   Nội dung (300 ký tự đầu):")
        print(f"   {docs[0].page_content[:300]}")

        # In mẫu Document cuối
        print(f"\n📗 MẪU DOCUMENT #{len(docs) - 1} (cuối):")
        print(f"   Metadata: {docs[-1].metadata}")
        print(f"   Nội dung (300 ký tự đầu):")
        print(f"   {docs[-1].page_content[:300]}")
    else:
        print("⚠️ Không có Document nào được tạo.")

    print("=" * 60)

    # LỆNH THỰC THI:
    # python d:\RAG-Philosophy\rag_core\step1_parser.py
