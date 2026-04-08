"""
Converter module: convert files (txt, md, docx, pdf, pptx, xlsx, images, audio) to text.
"""

from .base import BaseConverter
from .converter import FileConverter
from .docs_handling import (
    TextConverter,
    MarkdownConverter,
    DocxConverter,
    PdfConverter,
    PptxConverter,
    ExcelConverter,
)
from .images_handling import ImageConverter, ScannedPdfConverter, OCRConverter
from .sound_handling import AudioConverter, OpenAIWhisperSTT, FasterWhisperSTT
from .sorter import FileSorter
from .types import ConvertedContent, ConversionMetadata

__all__ = [
    "BaseConverter",
    "FileConverter",
    "TextConverter",
    "MarkdownConverter",
    "DocxConverter",
    "PdfConverter",
    "PptxConverter",
    "ExcelConverter",
    "ImageConverter",
    "ScannedPdfConverter",
    "OCRConverter",
    "AudioConverter",
    "OpenAIWhisperSTT",
    "FasterWhisperSTT",
    "FileSorter",
    "ConvertedContent",
    "ConversionMetadata",
]
