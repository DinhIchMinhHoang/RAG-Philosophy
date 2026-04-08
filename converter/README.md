# Converter Module

Converts files from various formats (text, documents, images, audio) to plain text output with metadata. The output is ready for the chunking module.

## Supported Formats

### Text and Documents
- Plain text (`.txt`)
- Markdown (`.md`)
- Word documents (`.docx`, `.doc`)
- PDF (text-based and scanned)
- PowerPoint (`.pptx`, `.ppt`)
- Excel (`.xlsx`, `.xls`, `.csv`)

### Images (OCR)
- PNG, JPEG, GIF, BMP, HEIC, WebP
- Uses **EasyOCR** or **Tesseract** with Vietnamese language support

### Audio (STT)
- MP3, WAV, M4A, FLAC, OGG, WMA, AAC, M4B
- Uses **Whisper** (OpenAI or faster-whisper) with Vietnamese support

## Architecture

```
Data Folder
    ↓
FileSorter (organize by type)
    ↓
FileConverter (dispatches to specific converters)
    ├── TextConverter
    ├── DocxConverter
    ├── PdfConverter
    ├── PptxConverter
    ├── ExcelConverter
    ├── ImageConverter (OCR)
    └── AudioConverter (STT)
    ↓
ConvertedContent (text + metadata)
    ↓
Output: JSONL format
```

## Usage

### Command Line

**Convert all files in a directory:**
```bash
python converter/cli.py convert -i data/ -o output/
```

**Sort files by type (without converting):**
```bash
python converter/cli.py sorter -i data/
```

**With custom settings:**
```bash
python converter/cli.py convert \
    -i data/ \
    -o output/ \
    --language vi \
    --whisper-model small \
    --no-easyocr  # use Tesseract instead
```

### Python API

```python
from converter import FileConverter, FileSorter

# Initialize converter
converter = FileConverter(
    use_faster_whisper=True,    # faster STT
    use_easyocr=True,           # better OCR
    whisper_model_size="small", # model size
    language="vi"               # Vietnamese
)

# Convert single file
result = converter.convert_file("data/doc.pdf")
print(result.text)
print(result.metadata)

# Convert entire directory
results = converter.convert_directory(
    data_dir="data/",
    output_dir="output/"  # saves conversions.jsonl + summary
)

# Sort files by type
sorted_files = FileSorter.sort_files("data/")
```

## Output Format

### conversions.jsonl
Each line is a JSON object with converted content and metadata:
```json
{
  "text": "...",
  "metadata": {
    "source_path": "data/doc.pdf",
    "source_type": "pdf",
    "conversion_type": "text",
    "timestamp": "2026-04-08T...",
    "page_index": null,
    "language": "vi",
    "confidence": null,
    "extra": {}
  },
  "success": true,
  "error": null
}
```

### conversion_summary.json
Summary statistics and per-type breakdowns.

## Requirements

See `requirements.txt` for all dependencies. Key ones:
- **Documents**: `python-docx`, `python-pptx`, `openpyxl`, `pandas`, `PyMuPDF`, `pdfplumber`
- **OCR**: `pytesseract`, `easyocr`, `Pillow`
- **STT**: `openai-whisper`, `faster-whisper`
- **NLP**: `underthesea` (Vietnamese sentence tokenization)

## Installation

```bash
pip install -r requirements.txt

# System dependencies (for Windows):
choco install tesseract ffmpeg
```

## Notes

- All text is normalized to NFC Unicode form
- Vietnamese text is handled with language-specific tokenizers
- Confidence scores from OCR/STT are preserved in metadata
- Scanned PDFs are detected and OCR'd automatically
- Output is JSONL for streaming processing
