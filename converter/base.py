"""
Base converter interface and utilities.
"""
from abc import ABC, abstractmethod
import unicodedata
from pathlib import Path
from typing import Optional

from .types import ConvertedContent, ConversionMetadata


class BaseConverter(ABC):
    """Abstract base class for all converters."""

    @abstractmethod
    def can_handle(self, file_path: str) -> bool:
        """Check if this converter can handle the given file."""
        pass

    @abstractmethod
    def convert(self, file_path: str) -> ConvertedContent:
        """Convert file to text and return ConvertedContent."""
        pass

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize Vietnamese text (and other scripts).
        - Normalize Unicode to NFC (composed form)
        - Strip extra whitespace
        """
        text = unicodedata.normalize("NFC", text)
        text = " ".join(text.split())  # collapse whitespace
        return text

    @staticmethod
    def create_metadata(
        file_path: str,
        source_type: str,
        conversion_type: str,
        language: str = "vi",
        **extra
    ) -> ConversionMetadata:
        """Helper to create metadata."""
        return ConversionMetadata(
            source_path=str(file_path),
            source_type=source_type,
            conversion_type=conversion_type,
            language=language,
            extra=extra,
        )
