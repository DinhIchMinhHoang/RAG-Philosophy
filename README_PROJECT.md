# RAG Philosophy Project

A RAG (Retrieval-Augmented Generation) pipeline for processing Vietnamese philosophical texts, converting them to text, and preparing them for embedding and semantic retrieval.

## Project Structure

```
RAG-Philosophy/
├── converter/           # Convert files to text (docs, images, audio)
│   ├── __init__.py
│   ├── base.py         # Base converter interface
│   ├── converter.py    # Main orchestrator
│   ├── docs_handling.py    # txt, md, docx, pdf, pptx, xlsx
│   ├── images_handling.py  # OCR for images
│   ├── sound_handling.py   # STT for audio
│   ├── sorter.py       # File sorting by type
│   ├── types.py        # Data classes
│   ├── cli.py          # Command-line interface
│   └── README.md
│
├── chunking/           # Chunk text for embedding
│   ├── __init__.py
│   ├── base.py         # Base chunker interface
│   ├── paragraph_chunker.py  # Vietnamese-aware paragraph chunking
│   ├── types.py        # Data classes
│   ├── cli.py          # Command-line interface
│   └── README.md
│
├── data/               # Input files (put your docs, images, audio here)
├── output/             # Output files
│
├── example_pipeline.py # End-to-end example
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Features

### Converter Module
- **Text formats**: `.txt`, `.md`
- **Documents**: `.docx`, `.pdf`, `.pptx`, `.xlsx`, `.xls`
- **Images**: PNG, JPEG, GIF, BMP, HEIC (OCR with Vietnamese support)
- **Audio**: MP3, WAV, M4A, FLAC, OGG (STT with Whisper)
- **Metadata preservation**: Source path, format, page/slide info, language, confidence scores
- **Output**: JSONL format with text and metadata

### Chunking Module
- **Paragraph-first strategy**: Splits by paragraphs, then sentences if needed
- **Vietnamese sentence tokenization**: Uses `underthesea` for smart splits
- **Token-aware**: Uses `tiktoken` for OpenAI-compatible token counting
- **Sliding window overlap**: Creates overlapping chunks for context
- **Special content detection**: Flags code blocks and tables
- **Output**: JSONL with chunk metadata, source tracking, token counts

## Installation

### 1. Create Virtual Environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Unix/Mac:
source .venv/bin/activate
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install System Dependencies (Windows)
```bash
choco install tesseract ffmpeg
# Or download:
# - Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
# - FFmpeg: https://ffmpeg.org/download.html
```

## Quick Start

### Step 1: Prepare Input Files
Place your files in the `data/` folder:
```
data/
├── document1.pdf
├── image1.png
├── audio1.mp3
└── text1.txt
```

### Step 2: Convert Files to Text
```bash
python converter/cli.py convert -i data/ -o output/converted/
```

This creates:
- `output/converted/conversions.jsonl` - Converted text with metadata
- `output/converted/conversion_summary.json` - Summary statistics

### Step 3: Chunk for Embedding
```bash
python chunking/cli.py jsonl -i output/converted/conversions.jsonl -o output/chunks.jsonl
```

This creates:
- `output/chunks.jsonl` - Chunks with semantic boundaries

### Step 4 (Next Phase): Embed Chunks
*(To be implemented)*
```bash
python embedding/cli.py embed -i output/chunks.jsonl -o output/embeddings.jsonl
```

## Command Line Usage

### Converter

**Sort files by type (preview):**
```bash
python converter/cli.py sorter -i data/
```

**Convert with custom settings:**
```bash
python converter/cli.py convert \
    -i data/ \
    -o output/converted/ \
    --language vi \
    --whisper-model small \
    --no-easyocr
```

### Chunker

**Chunk a text file:**
```bash
python chunking/cli.py text -i data/myfile.txt -o output/chunks.jsonl
```

**Chunk conversions (from converter output):**
```bash
python chunking/cli.py jsonl \
    -i output/converted/conversions.jsonl \
    -o output/chunks.jsonl \
    --max-tokens 800 \
    --overlap-tokens 100
```

## Python API

### Convert Files
```python
from converter import FileConverter

converter = FileConverter(
    use_faster_whisper=True,
    use_easyocr=True,
    whisper_model_size="small",
    language="vi"
)

# Single file
result = converter.convert_file("data/document.pdf")
print(result.text)
print(result.metadata)

# Directory
results = converter.convert_directory("data/", "output/converted/")

# Batch
files = ["data/file1.txt", "data/file2.pdf"]
results = converter.batch_convert_files(files)
```

### Chunk Text
```python
from chunking import ParagraphChunker, ChunkingConfig

config = ChunkingConfig(
    max_tokens=500,
    min_tokens=50,
    overlap_tokens=50,
    language="vi"
)

chunker = ParagraphChunker(config)

# Chunk a string
chunks = chunker.chunk("Your text here...", source_path="source.txt")

# Chunk from converter output
chunks = chunker.chunk_from_jsonl(
    "output/converted/conversions.jsonl",
    "output/chunks.jsonl"
)

for chunk in chunks:
    print(f"ID: {chunk.metadata.chunk_id}")
    print(f"Tokens: {chunk.metadata.token_count}")
    print(f"Text: {chunk.text}")
```

## End-to-End Example

Run the complete pipeline:
```bash
python example_pipeline.py
```

This will:
1. Convert all files in `data/` to text
2. Chunk the conversions
3. Show sample chunk and statistics

## Output Formats

### conversions.jsonl (from converter)
```json
{
  "text": "Converted text content...",
  "metadata": {
    "source_path": "data/doc.pdf",
    "source_type": "pdf",
    "conversion_type": "text",
    "timestamp": "2026-04-08T...",
    "language": "vi",
    "extra": {}
  },
  "success": true,
  "error": null
}
```

### chunks.jsonl (from chunker)
```json
{
  "text": "Chunk text...",
  "metadata": {
    "chunk_id": "data/doc.pdf#0#abcd1234",
    "source_path": "data/doc.pdf",
    "chunk_index": 0,
    "total_chunks": 5,
    "token_count": 487,
    "language": "vi",
    "has_code": false,
    "has_table": false,
    "extra": {}
  }
}
```

## Key Libraries

- **Document parsing**: python-docx, python-pptx, openpyxl, pandas, PyMuPDF, pdfplumber
- **OCR**: pytesseract, easyocr
- **STT**: whisper, faster-whisper
- **NLP**: underthesea (Vietnamese tokenization), tiktoken (token counting)
- **CLI**: rich, tqdm
- **Audio**: pydub

See `requirements.txt` for full list with descriptions.

## Configuration

Both modules use configuration objects for customization:

### Converter Config
```python
from converter import FileConverter

converter = FileConverter(
    use_faster_whisper=True,      # Use faster STT
    use_easyocr=True,             # Use better OCR
    whisper_model_size="small",   # Model size
    language="vi"                 # Vietnamese
)
```

### Chunker Config
```python
from chunking import ChunkingConfig, ParagraphChunker

config = ChunkingConfig(
    max_tokens=500,              # Max chunk size
    min_tokens=50,               # Min chunk size
    overlap_tokens=50,           # Overlap for context
    language="vi",               # Vietnamese
    preserve_code_blocks=True,
    preserve_tables=True,
    merge_short_paras=True,
)

chunker = ParagraphChunker(config)
```

## Roadmap

- [x] **Phase 1**: Converter module (files → text)
- [x] **Phase 2**: Chunking module (text → semantic chunks)
- [ ] **Phase 3**: Embedding module (chunks → vectors)
- [ ] **Phase 4**: Vector store (embeddings → retrieval)
- [ ] **Phase 5**: RAG (retrieval + generation)

## Notes

- **Vietnamese support**: All components handle Vietnamese text
- **Metadata preservation**: Full traceability from original files to chunks
- **Scalability**: JSONL format supports streaming large datasets
- **Customizable**: All converters and chunkers can be extended
- **Language-agnostic architecture**: Can be adapted for other languages

## Troubleshooting

**ImportError: No module named 'converter'**
- Ensure you're running from project root
- Add project root to PYTHONPATH: `export PYTHONPATH=${PYTHONPATH}:/path/to/project`

**Tesseract not found**
- Install Tesseract: `choco install tesseract` (Windows)
- Configure path: Set `pytesseract.pytesseract.tesseract_cmd`

**No OCR results**
- Use EasyOCR instead: `--no-easyocr` (uses Tesseract fallback)
- Install `torch`: `pip install torch`

**Memory issues with large audio files**
- Use `faster-whisper` (more efficient)
- Try smaller model: `--whisper-model tiny` or `base`

## License

[Add your license here]

## Contact

[Add contact info]
