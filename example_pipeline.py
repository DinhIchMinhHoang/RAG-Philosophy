#!/usr/bin/env python3
"""
Example: Complete RAG pipeline (converter + chunker).
Demonstrates converting files to text and chunking for embedding.
"""
import sys
from pathlib import Path

from converter import FileConverter
from chunking import ParagraphChunker, ChunkingConfig


def main():
    """Run converter and chunker pipeline."""
    print("="*70)
    print("RAG Philosophy: Converter + Chunker Pipeline Example")
    print("="*70)

    # Paths
    data_dir = Path("data")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Step 1: Convert files to text
    print("\n[STEP 1] Converting files...\n")
    
    converter = FileConverter(
        use_faster_whisper=True,
        use_easyocr=True,
        whisper_model_size="small",
        language="vi",
    )

    converted_dir = output_dir / "converted"
    results = converter.convert_directory(
        data_dir=str(data_dir),
        output_dir=str(converted_dir),
    )

    # Print conversion summary
    summary = results["summary"]
    print(f"\nConversion Summary:")
    print(f"  Total files: {summary['total']}")
    print(f"  ✓ Successful: {summary['successful']}")
    print(f"  ✗ Failed: {summary['failed']}")

    # Step 2: Chunk the conversions
    print("\n[STEP 2] Chunking conversions...\n")

    config = ChunkingConfig(
        max_tokens=500,
        min_tokens=50,
        overlap_tokens=50,
        language="vi",
    )

    chunker = ParagraphChunker(config)
    conversions_jsonl = converted_dir / "conversions.jsonl"
    chunks_jsonl = output_dir / "chunks.jsonl"

    if conversions_jsonl.exists():
        chunks = chunker.chunk_from_jsonl(
            jsonl_file=str(conversions_jsonl),
            output_jsonl=str(chunks_jsonl),
        )

        print(f"\nChunking Summary:")
        print(f"  Total chunks: {len(chunks)}")
        if chunks:
            tokens = [c.metadata.token_count for c in chunks]
            print(f"  Avg tokens: {sum(tokens) // len(tokens)}")
            print(f"  Min/Max: {min(tokens)} / {max(tokens)}")
    else:
        print(f"No conversions found. Make sure data/ folder has files.")
        return 1

    # Step 3: Show sample chunk
    print("\n[STEP 3] Sample chunk:\n")
    if chunks:
        sample = chunks[0]
        print(f"Chunk ID: {sample.metadata.chunk_id}")
        print(f"Source: {sample.metadata.source_path}")
        print(f"Tokens: {sample.metadata.token_count}")
        print(f"Has code: {sample.metadata.has_code}")
        print(f"Has table: {sample.metadata.has_table}")
        print(f"\nText preview (first 300 chars):")
        print(f"{sample.text[:300]}...")

    print("\n" + "="*70)
    print("✓ Pipeline complete!")
    print(f"  Conversions: {converted_dir}/conversions.jsonl")
    print(f"  Chunks: {chunks_jsonl}")
    print("="*70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
