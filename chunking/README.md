# Chunking Module

Breaks converted text (from converter module) into semantic chunks suitable for embedding.

## Features

- **Paragraph-first strategy**: Splits text by paragraphs first, then by sentences if needed
- **Vietnamese-aware**: Uses `underthesea` for Vietnamese sentence tokenization
- **Token-aware**: Uses `tiktoken` for OpenAI-compatible token counting
- **Sliding window overlap**: Creates overlapping chunks for better context
- **Metadata preservation**: Tracks source file, paragraph index, token count, special content flags
- **Special content handling**: Detects and preserves code blocks and tables

## Architecture

```
Converted Text (from converter)
    ↓
Extract Paragraphs
    ↓
Vietnamese Sentence Tokenization (optional, if para too long)
    ↓
Assemble Chunks (token budget + sliding window)
    ↓
Create Metadata (chunk_id, source, para_idx, token_count, etc.)
    ↓
Output: JSONL format
```

## Configuration

```python
from chunking import ChunkingConfig, ParagraphChunker

config = ChunkingConfig(
    max_tokens=500,         # max tokens per chunk
    min_tokens=50,          # skip chunks below this
    overlap_tokens=50,      # overlap between chunks
    language="vi",          # Vietnamese
    preserve_code_blocks=True,
    preserve_tables=True,
)

chunker = ParagraphChunker(config)
```

## Usage

### Command Line

**Chunk a text file:**
```bash
python chunking/cli.py text -i data/myfile.txt -o output/chunks.jsonl
```

**Chunk conversions from converter output:**
```bash
python chunking/cli.py jsonl -i output/conversions.jsonl -o output/chunks.jsonl
```

**Custom token budget:**
```bash
python chunking/cli.py jsonl \
    -i output/conversions.jsonl \
    -o output/chunks.jsonl \
    --max-tokens 800 \
    --min-tokens 100 \
    --overlap-tokens 100
```

### Python API

```python
from chunking import ParagraphChunker, ChunkingConfig

# Initialize chunker
config = ChunkingConfig(
    max_tokens=500,
    min_tokens=50,
    overlap_tokens=50,
    language="vi",
)
chunker = ParagraphChunker(config)

# Chunk a text string
text = "Your text here..."
chunks = chunker.chunk(text, source_path="source.txt")

for chunk in chunks:
    print(chunk.text)
    print(chunk.metadata.chunk_id)
    print(f"Tokens: {chunk.metadata.token_count}")

# Or chunk directly from converter output
chunks = chunker.chunk_from_jsonl(
    jsonl_file="output/conversions.jsonl",
    output_jsonl="output/chunks.jsonl",
)
```

## Output Format

### chunks.jsonl
Each line is a JSON object representing a chunk:
```json
{
  "text": "The actual chunk text...",
  "metadata": {
    "chunk_id": "source.txt#0#abcd1234",
    "source_path": "source.txt",
    "source_type": "txt",
    "chunk_index": 0,
    "total_chunks": 5,
    "paragraph_index": 0,
    "sentence_range": null,
    "char_start": null,
    "char_end": null,
    "token_count": 487,
    "page_index": null,
    "language": "vi",
    "has_code": false,
    "has_table": false,
    "extra": {}
  }
}
```

## Requirements

See `requirements.txt`. Key ones:
- `tiktoken` - token counting
- `underthesea` - Vietnamese sentence tokenization

## Pipeline Example

Complete end-to-end pipeline:

```bash
# 1. Convert files to text
python converter/cli.py convert -i data/ -o output/converted/

# 2. Chunk the conversions
python chunking/cli.py jsonl \
    -i output/converted/conversions.jsonl \
    -o output/chunks.jsonl

# 3. (Next phase) Embed chunks
python embedding/cli.py embed -i output/chunks.jsonl -o output/embeddings.jsonl
```

## Notes

- Chunks are assembled using a **sliding window** approach to create context overlap
- Each chunk is assigned a deterministic `chunk_id` based on source path, index, and content hash
- Vietnamese sentences are tokenized using `underthesea.sent_tokenize()` for better semantic splits
- Token counts are based on OpenAI's tokenizer (via `tiktoken`)
- Code blocks and tables are detected and flagged in metadata for special handling during embedding
- Chunks below `min_tokens` are skipped to avoid noise
