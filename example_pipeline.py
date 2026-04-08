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
    print(f"  [1.1] Initializing converter...")
    print(f"  [1.2] Input directory: {data_dir.absolute()}")
    
    converter = FileConverter(
        use_faster_whisper=True,
        use_easyocr=True,
        whisper_model_size="small",
        language="vi",
        use_gpu=True,  # GPU enabled by default
    )

    converted_dir = output_dir / "converted"
    print(f"  [1.3] Output directory: {converted_dir.absolute()}")
    print(f"  [1.4] GPU enabled: ✓ (RTX 4050 with CUDA 12.8)")
    print(f"  [1.5] Starting conversion (faster with GPU)...\n")
    
    results = converter.convert_directory(
        data_dir=str(data_dir),
        output_dir=str(converted_dir),
    )

    # Print conversion summary
    summary = results["summary"]
    print(f"\n[STEP 1] ✓ Conversion complete!")
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

    print(f"  [2.1] Initializing chunker...")
    print(f"  [2.2] Config: max_tokens={config.max_tokens}, min_tokens={config.min_tokens}, overlap_tokens={config.overlap_tokens}")
    
    chunker = ParagraphChunker(config)
    conversions_jsonl = converted_dir / "conversions.jsonl"
    chunks_jsonl = output_dir / "chunks.jsonl"

    if conversions_jsonl.exists():
        print(f"  [2.3] Input JSONL found: {conversions_jsonl}")
        print(f"  [2.4] Reading conversions...")
        
        # Read and count conversions first
        import json
        conversion_count = 0
        with open(conversions_jsonl, "r", encoding="utf-8") as f:
            conversion_count = sum(1 for line in f if line.strip())
        
        print(f"  [2.5] Found {conversion_count} conversions to chunk")
        print(f"  [2.6] Starting chunking process (this may take time)...\n")
        
        chunks = chunker.chunk_from_jsonl(
            jsonl_file=str(conversions_jsonl),
            output_jsonl=str(chunks_jsonl),
        )

        print(f"\n[STEP 2] ✓ Chunking complete!")
        print(f"  Total chunks created: {len(chunks)}")
        if chunks:
            tokens = [c.metadata.token_count for c in chunks]
            print(f"  Avg tokens per chunk: {sum(tokens) // len(tokens)}")
            print(f"  Min/Max tokens: {min(tokens)} / {max(tokens)}")
    else:
        print(f"  [!] No conversions found at {conversions_jsonl}")
        print(f"  Make sure data/ folder has files.")
        return 1

    # Step 3: Show sample chunk
    print("\n[STEP 3] Sample chunk:\n")
    if chunks:
        sample = chunks[0]
        print(f"  Chunk ID: {sample.metadata.chunk_id}")
        print(f"  Source: {sample.metadata.source_path}")
        print(f"  Chunk {sample.metadata.chunk_index + 1}/{sample.metadata.total_chunks}")
        print(f"  Tokens: {sample.metadata.token_count}")
        print(f"  Has code: {sample.metadata.has_code}")
        print(f"  Has table: {sample.metadata.has_table}")
        print(f"\n  Text preview (first 300 chars):")
        print(f"  {sample.text[:300]}...")

    print("\n" + "="*70)
    print("✓ Pipeline complete!")
    print(f"  [Step 1] Conversions: {converted_dir}/conversions.jsonl")
    print(f"  [Step 2] Chunks: {chunks_jsonl}")
    print(f"  [Ready] For next phase: embedding")
    print("="*70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
