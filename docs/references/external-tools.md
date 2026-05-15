# External Tools

## Development Tools

### Python Environment

- **Python**: 3.10+ (https://www.python.org/)
- **pip**: Package manager (included with Python)

### Required Services

| Tool | Purpose | Required |
|------|---------|----------|
| Ollama | Local LLM for OCR | Yes (glm-ocr model) |
| Qdrant | Vector database | Yes (in-memory or local) |
| SQLite | User database | Yes (file-based) |

### Optional Tools

- **GPU (CUDA)**: For faster embedding inference
- **Docker**: For containerized deployment (not configured)

## Dependencies

See `requirements.txt` for full list. Key packages:

```
langchain
langchain-core
langchain-google-genai
langchain-huggingface
langchain-qdrant
pymupdf4llm
fitz (PyMuPDF)
qdrant-client
huggingface-hub
python-dotenv
```

## Testing Tools

### Backend Testing

```bash
# Manual API testing with curl
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is philosophy?"}'
```

### Frontend Testing

- Browser DevTools (Network tab for API calls)
- Console for JavaScript errors

## Editor/IDE

- **VS Code** (recommended)
- Extensions: Python, Pylance, Live Server

## Project Context

- **Memory Bank**: `memory-bank/rag_project/`
  - `activeContext.md`: Current work
  - `productContext.md`: Product decisions
- **Docs**: This `docs/` directory
