"""
Types and data classes for converter module.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


@dataclass
class ConversionMetadata:
    """Metadata about a converted document."""
    source_path: str
    source_type: str  # e.g., txt, docx, pdf, png, mp3, etc.
    conversion_type: str  # e.g., text, ocr, stt
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    page_index: Optional[int] = None  # for multi-page documents
    slide_index: Optional[int] = None  # for presentations
    sheet_index: Optional[int] = None  # for spreadsheets
    duration: Optional[float] = None  # for audio, in seconds
    language: str = "vi"  # default to Vietnamese
    confidence: Optional[float] = None  # for OCR/STT confidence scores
    extra: Dict[str, Any] = field(default_factory=dict)  # custom metadata


@dataclass
class ConvertedContent:
    """Output of a conversion operation."""
    text: str
    metadata: ConversionMetadata
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "text": self.text,
            "metadata": {
                "source_path": self.metadata.source_path,
                "source_type": self.metadata.source_type,
                "conversion_type": self.metadata.conversion_type,
                "timestamp": self.metadata.timestamp,
                "page_index": self.metadata.page_index,
                "slide_index": self.metadata.slide_index,
                "sheet_index": self.metadata.sheet_index,
                "duration": self.metadata.duration,
                "language": self.metadata.language,
                "confidence": self.metadata.confidence,
                "extra": self.metadata.extra,
            },
            "success": self.success,
            "error": self.error,
        }
