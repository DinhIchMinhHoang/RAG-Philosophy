"""
Image converters: OCR for png, jpeg, gif, bmp, heic, pdf scans.
"""
import logging
from pathlib import Path
from typing import Optional, List

from .base import BaseConverter
from .types import ConvertedContent, ConversionMetadata

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    import easyocr
except ImportError:
    easyocr = None

try:
    import pdf2image
except ImportError:
    pdf2image = None


logger = logging.getLogger(__name__)


class OCRConverter(BaseConverter):
    """Base OCR converter using Tesseract or EasyOCR."""

    def __init__(self, use_easyocr: bool = True, language: str = "vi"):
        """
        Initialize OCR converter.
        Args:
            use_easyocr: Use EasyOCR if True, otherwise Tesseract
            language: Language code (e.g., 'vi' for Vietnamese)
        """
        self.use_easyocr = use_easyocr
        self.language = language
        self.reader = None

        if use_easyocr and easyocr:
            try:
                self.reader = easyocr.Reader([language], gpu=False)
            except Exception as e:
                logger.warning(f"Failed to load EasyOCR: {e}. Falling back to Tesseract.")
                self.use_easyocr = False

    def _ocr_with_tesseract(self, image_path: str) -> str:
        """Extract text from image using Tesseract."""
        if not pytesseract:
            raise RuntimeError("pytesseract not installed")
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang=self.language)
            return text
        except Exception as e:
            logger.error(f"Tesseract OCR failed for {image_path}: {e}")
            raise

    def _ocr_with_easyocr(self, image_path: str) -> tuple[str, Optional[float]]:
        """Extract text from image using EasyOCR. Returns (text, confidence)."""
        if not self.reader:
            raise RuntimeError("EasyOCR reader not initialized")
        try:
            results = self.reader.readtext(image_path, detail=1)
            texts = [result[1] for result in results]
            confidences = [result[2] for result in results]
            text = " ".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else None
            return text, avg_confidence
        except Exception as e:
            logger.error(f"EasyOCR failed for {image_path}: {e}")
            raise

    def extract_text_from_image(self, image_path: str) -> tuple[str, Optional[float]]:
        """Extract text from image, return (text, confidence)."""
        if self.use_easyocr and self.reader:
            text, confidence = self._ocr_with_easyocr(image_path)
        elif pytesseract:
            text = self._ocr_with_tesseract(image_path)
            confidence = None
        else:
            raise RuntimeError("No OCR engine available (pytesseract or easyocr)")
        return text, confidence


class ImageConverter(OCRConverter):
    """Convert image files (png, jpg, gif, bmp, heic) to text via OCR."""

    IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".heic", ".webp"}

    def can_handle(self, file_path: str) -> bool:
        ext = Path(file_path).suffix.lower()
        return ext in self.IMAGE_EXTENSIONS

    def convert(self, file_path: str) -> ConvertedContent:
        try:
            ext = Path(file_path).suffix.lower()
            text, confidence = self.extract_text_from_image(file_path)
            text = self.normalize_text(text)

            metadata = self.create_metadata(
                file_path,
                ext.lstrip("."),
                "ocr",
                language=self.language,
                confidence=confidence,
                ocr_engine="easyocr" if self.use_easyocr else "tesseract",
            )
            return ConvertedContent(text=text, metadata=metadata, success=True)
        except Exception as e:
            logger.error(f"Error converting image {file_path}: {e}")
            ext = Path(file_path).suffix.lower()
            return ConvertedContent(
                text="",
                metadata=self.create_metadata(
                    file_path, ext.lstrip("."), "ocr", language=self.language
                ),
                success=False,
                error=str(e),
            )


class ScannedPdfConverter(OCRConverter):
    """Convert scanned PDF (image-based) to text via OCR."""

    def can_handle(self, file_path: str) -> bool:
        # This should be used for scanned PDFs; handled by PdfConverter for text PDFs
        return False  # Don't auto-load; explicitly instantiate for scanned PDFs

    def convert(self, file_path: str) -> ConvertedContent:
        """Convert scanned PDF to text."""
        if not pdf2image:
            return ConvertedContent(
                text="",
                metadata=self.create_metadata(
                    file_path, "pdf", "ocr", language=self.language
                ),
                success=False,
                error="pdf2image not installed (install: pip install pdf2image)",
            )

        try:
            from pdf2image import convert_from_path

            pages_imgs = convert_from_path(file_path)
            texts_by_page = []

            for page_idx, img in enumerate(pages_imgs):
                # Save temp image and OCR
                temp_path = f"/tmp/page_{page_idx}.png"
                img.save(temp_path)
                try:
                    text, _ = self.extract_text_from_image(temp_path)
                    texts_by_page.append(text)
                finally:
                    Path(temp_path).unlink(missing_ok=True)

            full_text = "\n\n".join(texts_by_page)
            full_text = self.normalize_text(full_text)
            metadata = self.create_metadata(
                file_path,
                "pdf",
                "ocr",
                language=self.language,
                num_pages=len(pages_imgs),
                method="scanned_ocr",
            )
            return ConvertedContent(text=full_text, metadata=metadata, success=True)
        except Exception as e:
            logger.error(f"Error converting scanned PDF {file_path}: {e}")
            return ConvertedContent(
                text="",
                metadata=self.create_metadata(
                    file_path, "pdf", "ocr", language=self.language
                ),
                success=False,
                error=str(e),
            )
