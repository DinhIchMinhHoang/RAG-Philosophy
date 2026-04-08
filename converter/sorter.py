"""
Sorter: organize files from data/ folder by type.
"""
import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class FileSorter:
    """Sort files by type."""

    # File type mappings
    TEXT_EXTENSIONS = {".txt", ".md", ".log", ".rst"}
    DOCX_EXTENSIONS = {".docx", ".doc"}
    PDF_EXTENSIONS = {".pdf"}
    PPTX_EXTENSIONS = {".pptx", ".ppt"}
    EXCEL_EXTENSIONS = {".xlsx", ".xls", ".csv"}
    IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".heic", ".webp"}
    AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".wma", ".aac", ".m4b"}

    @staticmethod
    def get_file_type(file_path: str) -> str:
        """Determine file type from extension."""
        ext = Path(file_path).suffix.lower()

        if ext in FileSorter.TEXT_EXTENSIONS:
            return "text"
        elif ext in FileSorter.DOCX_EXTENSIONS:
            return "docx"
        elif ext in FileSorter.PDF_EXTENSIONS:
            return "pdf"
        elif ext in FileSorter.PPTX_EXTENSIONS:
            return "pptx"
        elif ext in FileSorter.EXCEL_EXTENSIONS:
            return "excel"
        elif ext in FileSorter.IMAGE_EXTENSIONS:
            return "image"
        elif ext in FileSorter.AUDIO_EXTENSIONS:
            return "audio"
        else:
            return "unknown"

    @staticmethod
    def sort_files(data_dir: str) -> Dict[str, List[Path]]:
        """
        Sort all files in data_dir by type.
        
        Returns:
            Dictionary mapping file type to list of Path objects
        """
        data_path = Path(data_dir)
        sorted_files: Dict[str, List[Path]] = {
            "text": [],
            "docx": [],
            "pdf": [],
            "pptx": [],
            "excel": [],
            "image": [],
            "audio": [],
            "unknown": [],
        }

        if not data_path.exists():
            logger.warning(f"Data directory does not exist: {data_path}")
            return sorted_files

        # Recursively find all files
        for file_path in data_path.rglob("*"):
            if file_path.is_file():
                file_type = FileSorter.get_file_type(str(file_path))
                sorted_files[file_type].append(file_path)
                logger.debug(f"Sorted {file_path.name} as {file_type}")

        # Log summary
        logger.info(f"Files sorted in {data_path}:")
        for file_type, files in sorted_files.items():
            if files:
                logger.info(f"  {file_type}: {len(files)} files")

        return sorted_files

    @staticmethod
    def get_files_by_type(data_dir: str, file_type: str) -> List[Path]:
        """Get all files of a specific type from data_dir."""
        sorted_files = FileSorter.sort_files(data_dir)
        return sorted_files.get(file_type, [])
