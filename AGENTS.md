# OpenCode Agent Guidelines

This document helps OpenCode understand your project's structure, conventions, and requirements.

## Project Overview

**Project Type**: Python RAG pipeline + FastAPI backend + vanilla JS frontend
**Purpose**: Ingest PDF course material and answer questions with citations for the UET RAG project
**Key Technologies**: Python 3.10+, LangChain, Qdrant, PyMuPDF/pymupdf4llm, Gemini (langchain-google-genai), FastAPI, SQLite, vanilla JS

## Code Conventions

### File Structure
```
config.py                 # Stub config (main config is rag_core/config.py)
rag_core/
│   ├── config.py          # Central configuration
│   ├── pipeline.py        # Pipeline orchestrator (ingest, build_pipeline, query)
│   ├── common/            # Shared utilities
│   │   ├── __init__.py
│   │   ├── logging_utils.py  # configure_logging(), get_logger()
│   │   ├── pdf_utils.py      # normalize_pdf_path(), collect_pdf_paths()
│   │   └── embeddings.py    # build_embeddings()
│   ├── step1_parser.py       # Hybrid Two-Pass Parser
│   ├── step2_chunker.py      # Parent-Child Text Splitter
│   ├── step3_vector_db.py    # Embedding + Qdrant storage
│   ├── step4_generator.py    # Retrieval + LLM Chain
│   ├── main_test.py          # Interactive pipeline test
│   ├── ragas_eval.py         # RAGAS evaluation script
│   └── tests/                # Unit tests
│       ├── test_logging_utils.py
│       ├── test_pdf_utils.py
│       ├── test_embeddings.py
│       └── test_pipeline.py
backend/app/     # FastAPI app (routers, services, auth)
frontend/        # Static HTML/CSS/JS client
data/            # PDFs and stores (raw/processed/stores)
memory-bank/     # Project context + decisions
```

### Naming Conventions
- **Python files**: snake_case (e.g., `step1_parser.py`)
- **Python classes**: PascalCase (e.g., `HybridPDFParser`)
- **Python functions**: snake_case (e.g., `build_vector_db`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `TOP_K_RESULTS`)
- **JS functions/vars**: camelCase (e.g., `chatStream`)
- **CSS classes**: kebab-case (e.g., `chat-shell`)

### Code Style
- **Indentation**: 4 spaces
- **Semicolons**: JS only (keep existing style)
- **Quotes**: JS single quotes; Python/HTML follow existing file style
- **Line length**: keep readable; avoid mass reflow
- **Trailing commas**: ok in multiline Python/JS

## Development Guidelines

### Testing
- 4 unit test files in `rag_core/tests/`: `test_logging_utils`, `test_pdf_utils`, `test_embeddings`, `test_pipeline` (9 tests, all passing)
- Use `rag_core/main_test.py` for pipeline smoke tests
- For backend, do manual API checks on `/documents/upload` and `/chat/stream`

### Error Handling
- Use `logging` in Python modules and clear HTTP errors in FastAPI routers
- Validate external inputs (PDF uploads, auth payloads, query strings)

### Security
- Never commit secrets or API keys
- Use `.env` for `GEMINI_API_KEY`, `SECRET_KEY`, and related config
- Validate upload type/size; keep JWT handling in `backend/app/core/security.py`

### Performance
- Parsing/embedding is expensive; avoid rebuilding retriever per query
- Reuse models/embeddings where possible; keep streaming responses lightweight

## Project-Specific Rules

### Do's
- Read `memory-bank/rag_project/activeContext.md` and `memory-bank/rag_project/productContext.md` at the start of new tasks
- Use `rag_core/config.py` for all parameters (no hardcoding in step modules)
- Keep step files single-responsibility (step1–step4); push shared logic to `rag_core/common/`
- Add `rag_core/common/` and `rag_core/pipeline.py` to scope when modifying pipeline utilities
- Preserve metadata keys: `source`, `page`, `doc_id`
- Keep prompts strict and citations required
- Keep SSE format stable in `/chat/stream`
- Cache RAGAS eval records to `data/ragas_records.json` and reuse with `--records-in` when possible

### Don'ts
- Don't hardcode API keys or model names outside `config.py`
- Don't change parent-child retrieval without explicit request
- Don't store uploads permanently unless requested
- Don't add dependencies without a clear need
- Don't modify unrelated files

## Common Patterns

### API Calls
```javascript
// Frontend API helper usage (see frontend/api.js)
const sources = await API.request('/documents/sources', { method: 'GET' });
```

### Component Structure
```javascript
// Scene handler pattern (see frontend/transitions.js)
const form = document.querySelector('#scene-signin .auth-form');
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    await API.login(email, password);
    transitionManager.transitionTo('dashboard');
});
```

## Tool Configuration

### Formatters
- No formatter/linter config in repo; keep existing formatting

### Build Tools
- **Backend**: FastAPI (uvicorn)
- **RAG**: run Python scripts directly
- **Frontend**: static files (serve via Live Server or similar)

## Getting Started

1. **Install dependencies**: `python -m pip install -r requirements.txt`
2. **Set environment**: add `.env` with `GEMINI_API_KEY` and backend `SECRET_KEY`
3. **Run RAG pipeline test**: `python rag_core/main_test.py`
4. **Start backend**: `uvicorn backend.app.main:app --reload`
5. **Open frontend**: serve `frontend/index.html`

## Helpful Commands

```bash
# Install deps
python -m pip install -r requirements.txt

# RAG pipeline smoke test
python rag_core/main_test.py

# Run backend
uvicorn backend.app.main:app --reload

# RAGAS eval (reuse cached records)
python rag_core/ragas_eval.py --dataset data/dataset.json --out data/result.csv --records-in data/ragas_records.json

# Unit tests
cd rag_core/tests && python -m unittest test_logging_utils test_pdf_utils test_embeddings test_pipeline -v
```

## Contact & Support

- **Team**: UET RAG project
- **Repository**: local workspace
- **Documentation**: `RAG_instruct.md`
- **Slack**: N/A

---

*Keep this document aligned with repo structure and pipeline changes.*
