#!/usr/bin/env python3
"""
CLI for chunking module: chunk converted text for embedding.
"""
import json
import logging
import argparse
import sys
from pathlib import Path

from chunking import ParagraphChunker, ChunkingConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def cmd_chunk_text(args):
    """Chunk a text file."""
    logger.info(f"Chunking text file: {args.input}")

    config = ChunkingConfig(
        max_tokens=args.max_tokens,
        min_tokens=args.min_tokens,
        overlap_tokens=args.overlap_tokens,
        language=args.language,
    )

    chunker = ParagraphChunker(config)

    # Read input file
    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    # Chunk
    chunks = chunker.chunk(text, source_path=args.input)

    # Save output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            for chunk in chunks:
                f.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")
        logger.info(f"Saved {len(chunks)} chunks to {args.output}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"Chunking Summary")
    print(f"{'='*60}")
    print(f"Input file: {args.input}")
    print(f"Total chunks: {len(chunks)}")
    if chunks:
        tokens = [c.metadata.token_count for c in chunks]
        print(f"Avg tokens per chunk: {sum(tokens) // len(tokens)}")
        print(f"Min/Max tokens: {min(tokens)} / {max(tokens)}")
    print(f"{'='*60}\n")

    return 0


def cmd_chunk_jsonl(args):
    """Chunk conversions from JSONL file."""
    logger.info(f"Chunking conversions from: {args.input}")

    config = ChunkingConfig(
        max_tokens=args.max_tokens,
        min_tokens=args.min_tokens,
        overlap_tokens=args.overlap_tokens,
        language=args.language,
    )

    chunker = ParagraphChunker(config)

    # Process JSONL
    chunks = chunker.chunk_from_jsonl(
        jsonl_file=args.input,
        output_jsonl=args.output,
    )

    # Print summary
    print(f"\n{'='*60}")
    print(f"Chunking Summary (from JSONL)")
    print(f"{'='*60}")
    print(f"Input file: {args.input}")
    print(f"Total chunks: {len(chunks)}")
    if chunks:
        tokens = [c.metadata.token_count for c in chunks]
        print(f"Avg tokens per chunk: {sum(tokens) // len(tokens)}")
        print(f"Min/Max tokens: {min(tokens)} / {max(tokens)}")
        
        # Group by source
        by_source = {}
        for chunk in chunks:
            src = chunk.metadata.source_path
            by_source[src] = by_source.get(src, 0) + 1
        
        print(f"\nChunks by source:")
        for src, count in by_source.items():
            print(f"  {src}: {count} chunks")
    
    if args.output:
        print(f"\nOutput saved to: {args.output}")
    
    print(f"{'='*60}\n")

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RAG Chunker: Chunk converted text for embedding"
    )

    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Chunk text command
    chunk_text_parser = subparsers.add_parser(
        "text", help="Chunk a text file"
    )
    chunk_text_parser.add_argument(
        "-i", "--input", required=True, help="Input text file"
    )
    chunk_text_parser.add_argument(
        "-o", "--output", help="Output JSONL file"
    )
    chunk_text_parser.add_argument(
        "--max-tokens",
        type=int,
        default=500,
        help="Max tokens per chunk (default: 500)",
    )
    chunk_text_parser.add_argument(
        "--min-tokens",
        type=int,
        default=50,
        help="Min tokens per chunk (default: 50)",
    )
    chunk_text_parser.add_argument(
        "--overlap-tokens",
        type=int,
        default=50,
        help="Overlap tokens between chunks (default: 50)",
    )
    chunk_text_parser.add_argument(
        "--language",
        default="vi",
        help="Language code (default: vi for Vietnamese)",
    )
    chunk_text_parser.set_defaults(func=cmd_chunk_text)

    # Chunk JSONL command
    chunk_jsonl_parser = subparsers.add_parser(
        "jsonl", help="Chunk conversions from JSONL file"
    )
    chunk_jsonl_parser.add_argument(
        "-i", "--input", required=True, help="Input JSONL file (from converter)"
    )
    chunk_jsonl_parser.add_argument(
        "-o", "--output", help="Output JSONL file"
    )
    chunk_jsonl_parser.add_argument(
        "--max-tokens",
        type=int,
        default=500,
        help="Max tokens per chunk (default: 500)",
    )
    chunk_jsonl_parser.add_argument(
        "--min-tokens",
        type=int,
        default=50,
        help="Min tokens per chunk (default: 50)",
    )
    chunk_jsonl_parser.add_argument(
        "--overlap-tokens",
        type=int,
        default=50,
        help="Overlap tokens between chunks (default: 50)",
    )
    chunk_jsonl_parser.add_argument(
        "--language",
        default="vi",
        help="Language code (default: vi for Vietnamese)",
    )
    chunk_jsonl_parser.set_defaults(func=cmd_chunk_jsonl)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
