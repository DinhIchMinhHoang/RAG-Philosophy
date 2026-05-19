"""
rag_core/parsers/__init__.py - Parser Registry

Unified parser interface with format auto-detection.
Routes files to appropriate parser based on extension.
"""

from __future__ import annotations

from typing import List

from langchain_core.documents import Document

from ..step1_parser import HybridPDFParser
from .tabular_parser import TabularParser


class ParserRegistry:
    """
    Unified parser interface with format auto-detection.
    
    Automatically routes files to:
    - HybridPDFParser for .pdf
    - TabularParser for .xlsx, .xls, .csv
    """
    
    def __init__(self):
        self._pdf_parser: HybridPDFParser | None = None
        self._tabular_parser: TabularParser | None = None
    
    @property
    def pdf_parser(self) -> HybridPDFParser:
        if self._pdf_parser is None:
            self._pdf_parser = HybridPDFParser()
        return self._pdf_parser
    
    @property
    def tabular_parser(self) -> TabularParser:
        if self._tabular_parser is None:
            self._tabular_parser = TabularParser()
        return self._tabular_parser
    
    def parse(self, file_path: str) -> List[Document]:
        """
        Auto-detect format and parse file.
        
        Args:
            file_path: Path to file (.pdf, .xlsx, .xls, .csv)
            
        Returns:
            List[Document]: Parsed documents with format-specific metadata.
            
        Raises:
            ValueError: If format is not supported.
        """
        import os
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return self.pdf_parser.parse_pdf(file_path)
        elif ext in ['.xlsx', '.xls', '.csv']:
            return self.tabular_parser.parse(file_path)
        else:
            raise ValueError(f"Unsupported format: {ext}")
    
    def get_parser_type(self, file_path: str) -> str:
        """Return parser type for a given file."""
        import os
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return 'pdf'
        elif ext in ['.xlsx', '.xls', '.csv']:
            return 'tabular'
        return 'unknown'


# Singleton instance for module-level access
parser_registry = ParserRegistry()


def parse_file(file_path: str) -> List[Document]:
    """Convenience function using singleton registry."""
    return parser_registry.parse(file_path)