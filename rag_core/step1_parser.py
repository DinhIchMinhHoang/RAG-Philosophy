"""
step1_parser.py - Module phân tích tài liệu (Document Parsing).

Kiến trúc Page-Level Router:
  1. Duyệt qua từng trang PDF bằng PyMuPDF (fitz).
  2. Phân loại trang (Router Logic):
     - Fast Track: Nếu trang chủ yếu là text thường -> Lấy raw text và heal text.
     - Heavy Track: Nếu trang có nhiều công thức Toán hoặc Bảng (nhiều vector graphics)
       -> Trích xuất trang đó ra file tạm và chạy Docling để lấy Markdown/LaTeX chuẩn.
  3. Gộp kết quả các trang thành 1 file Markdown hoàn chỉnh.
"""

import os
import re
import json
import logging
import time
import tempfile

import fitz  # PyMuPDF
import pdfplumber
import torch
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorOptions
from docling.datamodel.base_models import InputFormat

from config import Config

# ── Logging ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ── Đường dẫn file trạng thái ───────────────────────────────────────
_PROCESSED_FILES_PATH: str = os.path.join(Config.DATA_DIR, "processed_files.json")


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
        text = re.sub(r'(?m)^\s*(MỤC LỤC|DANH SÁCH HÌNH|DANH SÁCH BẢNG|DANH MỤC|TÀI LIỆU THAM KHẢO)\s*$', '', text, flags=re.IGNORECASE)
        # Remove common academic running headers/footers (e.g., "12 CHƯƠNG 1...", "12 PHẦN...")
        text = re.sub(r'(?m)^\s*\d+\s+(CHƯƠNG|PHẦN)\s+.*$', '', text, flags=re.IGNORECASE)

        # 1. Remove Page Numbers
        text = re.sub(r'(?m)^\s*(?:Trang\s+|Page\s+)?\d+\s*$', '', text)

        # 2. Convert Fake Headings to Real Markdown Headings
        # Header 1: Chương \d+ or Phần [IVXLCDM\d]+
        text = re.sub(r'(?m)^(\s*)(Chương\s+\d+|Phần\s+[IVXLCDM\d]+)[ \t:\.]*(.*)', r'\1# \2 \3', text, flags=re.IGNORECASE)
        
        # Header 3: \d+\.\d+\.\d+ (e.g., 1.1.1)
        text = re.sub(r'(?m)^(\s*)(\d+\.\d+\.\d+)(?!\.\d)[ \t:\.]*(.*)', r'\1### \2 \3', text)
        
        # Header 2: \d+\.\d+ (e.g., 1.1, 2.3)
        text = re.sub(r'(?m)^(\s*)(\d+\.\d+)(?!\.\d)[ \t:\.]*(.*)', r'\1## \2 \3', text)

        # 2.5 Split Inline Headings (CRITICAL)
        lines = text.split('\n')
        for i in range(len(lines)):
            if lines[i].lstrip().startswith('#'):
                lines[i] = MarkdownSanitizer._split_inline_heading(lines[i])
        text = '\n'.join(lines)

        # 3. Fix Hard Line Breaks
        text = MarkdownSanitizer._fix_hard_line_breaks(text)

        # 4. TOC Truncation (The RAG Savior)
        match = re.search(r'^#\s+(Chương\s+1|Phần\s+(?:1|I))\b', text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            start_idx = match.start()
            nearest_tag = text.rfind('<!--', 0, start_idx)
            if nearest_tag != -1:
                text = text[nearest_tag:]
            else:
                text = text[start_idx:]

        # Clean up excessive empty lines
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    @staticmethod
    def _split_inline_heading(line: str) -> str:
        """
        Helper method to split inline headings where paragraph text is merged with the heading.
        Finds a sentence boundary (?, ., or :) followed by an Uppercase Vietnamese character.
        """
        upper_chars = "A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲỴÝỶỸ"
        pattern = r'([?\.:])\s+([' + upper_chars + r'])'
        
        match = re.search(pattern, line)
        if match:
            split_idx = match.start(2)
            # Insert \n\n to push the body text to a new paragraph
            return line[:split_idx].strip() + "\n\n" + line[split_idx:]
        return line

    @staticmethod
    def _fix_hard_line_breaks(text: str) -> str:
        paragraphs = text.split('\n\n')
        fixed_paragraphs = []
        for p in paragraphs:
            lines = p.split('\n')
            if not lines:
                continue
            
            merged_lines = [lines[0]]
            for i in range(1, len(lines)):
                prev_line = merged_lines[-1].rstrip()
                curr_line = lines[i].lstrip()
                
                if not prev_line or not curr_line:
                    merged_lines.append(curr_line)
                    continue

                # Don't merge if prev line ends with end-of-sentence punctuation
                if prev_line[-1] in ['.', '?', '!', ':', '>', ']']:
                    merged_lines.append(curr_line)
                    continue
                
                # Don't merge if curr line is a numbered list (\d+\.)
                if re.match(r'^\d+\.', curr_line):
                    merged_lines.append(curr_line)
                    continue
                
                # Don't merge if prev line or curr line is a special markdown element (including "- ")
                if (prev_line.startswith(('#', '<!--', '-', '*', '>')) or
                    curr_line.startswith(('#', '<!--', '-', '*', '>'))):
                    merged_lines.append(curr_line)
                    continue
                
                # Otherwise, merge them securely into a single continuous sentence
                merged_lines[-1] = prev_line + ' ' + curr_line
            
            fixed_paragraphs.append('\n'.join(merged_lines))
            
        return '\n\n'.join(fixed_paragraphs)


class SmartDocumentParser:
    """
    Bộ phân tích tài liệu thông minh với Page-Level Router.
    """
    X_TOLERANCE = 2.0

    def __init__(self):
        self._docling_converter = None

    # ================================================================
    # 1. CƠ CHẾ QUẢN LÝ TRẠNG THÁI (Incremental Processing)
    # ================================================================

    @staticmethod
    def _load_processed_list() -> list[str]:
        if not os.path.exists(_PROCESSED_FILES_PATH):
            return []
        try:
            with open(_PROCESSED_FILES_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            return []
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(f"[State] Không đọc được processed_files.json: {exc}")
            return []

    @staticmethod
    def _save_processed_list(processed: list[str]) -> None:
        os.makedirs(os.path.dirname(_PROCESSED_FILES_PATH), exist_ok=True)
        with open(_PROCESSED_FILES_PATH, "w", encoding="utf-8") as f:
            json.dump(processed, f, ensure_ascii=False, indent=2)
        logger.info(f"[State] Đã cập nhật processed_files.json ({len(processed)} file)")


    # ================================================================
    # 3. PAGE-LEVEL ROUTER LOGIC
    # ================================================================

    def _is_complex_page(self, page: fitz.Page, raw_text: str) -> bool:
        """
        Heuristic function để xác định xem trang có phức tạp không.
        Trả về True nếu chứa nhiều ký hiệu Toán học hoặc có khả năng chứa Bảng.
        """
        # Kiểm tra ký hiệu Toán học
        math_symbols = ['∑', '∫', 'lim', '∆', '∈', '∀', '∃', '≤', '≥', '≈', '∞', '∏', '√', '∂', 'µ', 'σ', 'θ']
        math_count = sum(raw_text.count(sym) for sym in math_symbols)
        
        if math_count > 3:
            return True

        # Kiểm tra Vector Graphics (dấu hiệu của Bảng biểu hoặc Hình vẽ phức tạp)
        try:
            drawings = page.get_drawings()
            if len(drawings) > 15:
                return True
        except Exception:
            pass

        return False

    def heal_vietnamese_text(self, text: str) -> str:
        """
        Làm sạch text, sửa lỗi xuống dòng và khoảng trắng.
        """
        # Thay thế nhiều khoảng trắng hoặc tab bằng 1 khoảng trắng
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Sửa lỗi đứt dòng: nếu xuống dòng đơn (1 dấu \n) mà không kết thúc bằng dấu câu, ta thay bằng khoảng trắng.
        # Ở đây ta giữ lại đoạn văn nếu có 2 dấu \n (đoạn mới).
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        
        # Xóa các khoảng trắng ở đầu và cuối
        return text.strip()

    # ================================================================
    # 4. HÀM CHÍNH — PARSE DOC
    # ================================================================

    def parse_doc(self, file_path: str) -> str | None:
        """
        Hàm public duy nhất — Phân tích PDF → Markdown bằng Router Architecture.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

        source_filename: str = os.path.basename(file_path)

        # Kiểm tra Incremental Processing
        processed_list: list[str] = self._load_processed_list()
        if source_filename in processed_list:
            logger.info(f"⏭️ Bỏ qua file cũ (đã được xử lý): {source_filename}")
            return None

        final_markdown_blocks = []
        doc = fitz.open(file_path)
        pdfplumber_doc = pdfplumber.open(file_path)
        
        logger.info(f"🚀 Bắt đầu parse file: {source_filename} ({doc.page_count} trang)")

        try:
            for i, page in enumerate(doc):
                raw_text_fitz = page.get_text("text")
                is_complex = self._is_complex_page(page, raw_text_fitz)

                if is_complex:
                    print(f"[Page {i+1}] -> Heavy Track (Math/Table detected)")
                    # --- HEAVY TRACK ---
                    # Trích xuất riêng trang này thành 1 file PDF tạm
                    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
                        tmp_path = tmp_pdf.name
                    
                    try:
                        tmp_doc = fitz.open()
                        tmp_doc.insert_pdf(doc, from_page=i, to_page=i)
                        tmp_doc.save(tmp_path)
                        tmp_doc.close()

                        # Chạy Docling
                        if self._docling_converter is None:
                            logger.info("[Init] Khởi tạo Docling engine lần đầu tiên (Lazy Load)...")
                            if torch.cuda.is_available():
                                device = "cuda"
                            elif torch.backends.mps.is_available():
                                device = "mps"
                            else:
                                device = "cpu"
                            
                            pipeline_options = PdfPipelineOptions()
                            pipeline_options.do_table_structure = True
                            pipeline_options.do_ocr = True
                            num_threads = 1 if device == "cuda" else 4
                            pipeline_options.accelerator_options = AcceleratorOptions(num_threads=num_threads, device=device)

                            self._docling_converter = DocumentConverter(
                                format_options={
                                    InputFormat.PDF: PdfFormatOption(
                                        pipeline_options=pipeline_options,
                                    ),
                                }
                            )
                        else:
                            logger.info("[Heavy Track] Tái sử dụng Docling engine có sẵn...")

                        result = self._docling_converter.convert(tmp_path)
                        page_md = result.document.export_to_markdown()
                        final_markdown_blocks.append(f"<!-- Page {i+1} (Heavy) -->\n" + page_md)
                    
                    except Exception as e:
                        logger.error(f"❌ Lỗi Heavy Track ở trang {i+1}: {e}. Fallback sang Fast Track.")
                        # Nếu Docling lỗi, lùi về Fast Track cho trang đó
                        raw_text_plumber = pdfplumber_doc.pages[i].extract_text(x_tolerance=self.X_TOLERANCE) or ""
                        healed_text = self.heal_vietnamese_text(raw_text_plumber)
                        final_markdown_blocks.append(f"<!-- Page {i+1} (Fallback) -->\n" + healed_text)
                    
                    finally:
                        # Dọn dẹp file tạm
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)
                
                else:
                    print(f"[Page {i+1}] -> Fast Track")
                    # --- FAST TRACK ---
                    raw_text_plumber = pdfplumber_doc.pages[i].extract_text(x_tolerance=self.X_TOLERANCE) or ""
                    healed_text = self.heal_vietnamese_text(raw_text_plumber)
                    final_markdown_blocks.append(f"<!-- Page {i+1} -->\n" + healed_text)
        finally:
            doc.close()
            pdfplumber_doc.close()

        final_markdown = "\n\n".join(final_markdown_blocks)
        
        # Tích hợp MarkdownSanitizer tại đây (trước khi lưu/trả về)
        final_markdown = MarkdownSanitizer.sanitize(final_markdown)

        if final_markdown:
            processed_list.append(source_filename)
            self._save_processed_list(processed_list)

        return final_markdown

    # ================================================================
    # LƯU MARKDOWN → data/processed/
    # ================================================================

    @staticmethod
    def save_markdown(markdown_text: str, source_filename: str) -> str:
        os.makedirs(Config.PROCESSED_DIR, exist_ok=True)
        md_filename: str = os.path.splitext(source_filename)[0] + ".md"
        output_path: str = os.path.join(Config.PROCESSED_DIR, md_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)

        logger.info(f"💾 Đã lưu Markdown → {output_path}")
        return output_path


if __name__ == "__main__":
    # ================================================================
    # SELF-TESTING BLOCK
    # ================================================================
    # Để chạy block này, mở terminal và gõ lệnh:
    # python d:\RAG-Philosophy\rag_core\step1_parser.py
    
    print("=" * 60)
    print("🧪 KHỞI ĐỘNG BÀI KIỂM TRA PAGE-LEVEL ROUTER")
    print("=" * 60)

    # Chọn 1 file PDF làm mẫu test (chỉnh tên file theo thực tế trong Config.RAW_DIR)
    # Ví dụ: "SML (1).pdf" hoặc "Deep Learning.pdf"
    sample_pdf_name = "Triết_Mác_Lenin.pdf"
    sample_pdf_path = os.path.join(Config.RAW_DIR, sample_pdf_name)
    
    # Nếu không tìm thấy Deep Learning.pdf, thử với SML (1).pdf
    if not os.path.exists(sample_pdf_path):
        sample_pdf_name = "SML (1).pdf"
        sample_pdf_path = os.path.join(Config.RAW_DIR, sample_pdf_name)

    if not os.path.exists(sample_pdf_path):
        print(f"❌ Không tìm thấy file test nào trong: {Config.RAW_DIR}")
    else:
        print(f"📄 Đang xử lý file test: {sample_pdf_path}")
        parser = SmartDocumentParser()
        
        # Bỏ qua cơ chế Incremental Processing trong lúc test để luôn phân tích lại
        # Xóa file khỏi processed_files.json nếu tồn tại
        processed = parser._load_processed_list()
        if sample_pdf_name in processed:
            processed.remove(sample_pdf_name)
            parser._save_processed_list(processed)

        start_time = time.time()
        
        markdown_result = parser.parse_doc(sample_pdf_path)
        
        execution_time = time.time() - start_time
        
        print("-" * 60)
        print(f"⏱️ Tổng thời gian chạy: {execution_time:.2f} giây")
        
        if markdown_result:
            output_file = parser.save_markdown(markdown_result, sample_pdf_name)
            print(f"✅ Quá trình phân tích thành công. Kích thước file: {len(markdown_result):,} ký tự")
            print(f"📂 File lưu tại: {output_file}")
        else:
            print("⚠️ Quá trình phân tích không trả về kết quả.")
            
    print("=" * 60)

    # LỆNH THỰC THI (TERMINAL COMMAND):
    # python d:\RAG-Philosophy\rag_core\step1_parser.py
