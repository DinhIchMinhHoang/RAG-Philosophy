#!/usr/bin/env python3
"""
CLI for converter module: convert files from data/ to text format.
"""
import logging
import argparse
import sys
from pathlib import Path

from converter import FileConverter, FileSorter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def cmd_convert(args):
    """Convert files from input directory to text output."""
    logger.info(f"Converting files from: {args.input}")

    converter = FileConverter(
        use_faster_whisper=not args.no_faster_whisper,
        use_easyocr=not args.no_easyocr,
        whisper_model_size=args.whisper_model,
        language=args.language,
    )

    results = converter.convert_directory(
        data_dir=args.input,
        output_dir=args.output,
    )

    # Print summary
    summary = results["summary"]
    print(f"\n{'='*60}")
    print(f"Conversion Summary")
    print(f"{'='*60}")
    print(f"Total files: {summary['total']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"\nBy type:")
    for file_type, type_summary in summary["by_type"].items():
        if type_summary["count"] > 0:
            print(
                f"  {file_type:10s}: {type_summary['count']:3d} "
                f"(✓ {type_summary['success']} / ✗ {type_summary['failed']})"
            )
    print(f"{'='*60}")

    if args.output:
        print(f"\nOutput saved to: {args.output}")

    return 0


def cmd_sorter(args):
    """Sort files by type without converting."""
    logger.info(f"Sorting files in: {args.input}")

    sorted_files = FileSorter.sort_files(args.input)

    print(f"\n{'='*60}")
    print(f"File Sorter Results")
    print(f"{'='*60}")
    for file_type, files in sorted_files.items():
        if files:
            print(f"\n{file_type.upper()} ({len(files)} files):")
            for f in files[:10]:  # Show first 10
                print(f"  - {f}")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more")

    print(f"{'='*60}\n")
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RAG Converter: Convert files to text for chunking and embedding"
    )

    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert files to text")
    convert_parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Input directory containing files",
    )
    convert_parser.add_argument(
        "-o",
        "--output",
        help="Output directory for converted files (JSONL format)",
    )
    convert_parser.add_argument(
        "--language",
        default="vi",
        help="Language code for OCR/STT (default: vi for Vietnamese)",
    )
    convert_parser.add_argument(
        "--whisper-model",
        default="small",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: small)",
    )
    convert_parser.add_argument(
        "--no-faster-whisper",
        action="store_true",
        help="Use openai-whisper instead of faster-whisper",
    )
    convert_parser.add_argument(
        "--no-easyocr",
        action="store_true",
        help="Use Tesseract instead of EasyOCR",
    )
    convert_parser.set_defaults(func=cmd_convert)

    # Sorter command
    sorter_parser = subparsers.add_parser("sorter", help="Sort files by type")
    sorter_parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Input directory to sort",
    )
    sorter_parser.set_defaults(func=cmd_sorter)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
