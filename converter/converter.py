"""
Main converter orchestrator: coordinates all converters and produces JSON output.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .sorter import FileSorter
from .docs_handling import (
    TextConverter,
    MarkdownConverter,
    DocxConverter,
    PdfConverter,
    PptxConverter,
    ExcelConverter,
)
from .images_handling import ImageConverter, ScannedPdfConverter
from .sound_handling import AudioConverter
from .types import ConvertedContent

logger = logging.getLogger(__name__)


class FileConverter:
    """Main orchestrator for file conversion."""

    def __init__(
        self,
        use_faster_whisper: bool = True,
        use_easyocr: bool = True,
        whisper_model_size: str = "small",
        language: str = "vi",
        use_gpu: bool = False,
    ):
        """
        Initialize converter with all adapters.
        
        Args:
            use_faster_whisper: Use faster-whisper for STT
            use_easyocr: Use EasyOCR for OCR
            whisper_model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
            language: Language code (e.g., 'vi' for Vietnamese)
            use_gpu: Use GPU for OCR/STT if available (default: False)
        """
        self.language = language
        self.use_gpu = use_gpu
        self.converters = [
            TextConverter(),
            MarkdownConverter(),
            DocxConverter(),
            PdfConverter(),
            PptxConverter(),
            ExcelConverter(),
            ImageConverter(use_easyocr=use_easyocr, language=language, use_gpu=use_gpu),
            AudioConverter(
                use_faster_whisper=use_faster_whisper,
                model_size=whisper_model_size,
                language=language,
                use_gpu=use_gpu,
            ),
        ]
        logger.info(
            f"FileConverter initialized with {len(self.converters)} converters (GPU: {use_gpu})"
        )

    def convert_file(self, file_path: str) -> ConvertedContent:
        """
        Convert a single file to text.
        
        Args:
            file_path: Path to the file
            
        Returns:
            ConvertedContent with text and metadata
        """
        file_path = str(file_path)
        logger.info(f"Converting: {file_path}")

        for converter in self.converters:
            if converter.can_handle(file_path):
                result = converter.convert(file_path)
                logger.info(
                    f"Converted {file_path} ({converter.__class__.__name__}): "
                    f"{'success' if result.success else 'failed'}"
                )
                return result

        # No converter found
        logger.warning(f"No converter found for {file_path}")
        return ConvertedContent(
            text="",
            metadata={
                "source_path": file_path,
                "source_type": Path(file_path).suffix.lstrip("."),
                "conversion_type": "unknown",
                "timestamp": datetime.now().isoformat(),
                "language": self.language,
            },
            success=False,
            error="No converter available for this file type",
        )

    def convert_directory(
        self, data_dir: str, output_dir: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Convert all files in a directory.
        
        Args:
            data_dir: Input directory containing files to convert
            output_dir: Output directory for JSONL results (if None, returns dict)
            
        Returns:
            Dictionary with conversion results
        """
        logger.info(f"Converting directory: {data_dir}")

        # Sort files by type
        sorted_files = FileSorter.sort_files(data_dir)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "source_dir": data_dir,
            "output_dir": output_dir,
            "conversions": [],
            "summary": {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "by_type": {},
            },
        }

        # Convert files
        for file_type, files in sorted_files.items():
            if not files:
                continue

            type_summary = {"type": file_type, "count": 0, "success": 0, "failed": 0}

            for file_path in files:
                result = self.convert_file(str(file_path))
                results["conversions"].append(result.to_dict())

                type_summary["count"] += 1
                if result.success:
                    type_summary["success"] += 1
                    results["summary"]["successful"] += 1
                else:
                    type_summary["failed"] += 1
                    results["summary"]["failed"] += 1

                results["summary"]["total"] += 1

            results["summary"]["by_type"][file_type] = type_summary

        # Save to output dir if specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Save conversions as JSONL
            jsonl_file = output_path / "conversions.jsonl"
            with open(jsonl_file, "w", encoding="utf-8") as f:
                for conv in results["conversions"]:
                    f.write(json.dumps(conv, ensure_ascii=False) + "\n")
            logger.info(f"Saved conversions to {jsonl_file}")

            # Save summary
            summary_file = output_path / "conversion_summary.json"
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved summary to {summary_file}")

        return results

    def batch_convert_files(self, file_paths: List[str]) -> List[ConvertedContent]:
        """
        Convert a batch of files.
        
        Args:
            file_paths: List of file paths to convert
            
        Returns:
            List of ConvertedContent objects
        """
        results = []
        for file_path in file_paths:
            result = self.convert_file(file_path)
            results.append(result)
        return results
