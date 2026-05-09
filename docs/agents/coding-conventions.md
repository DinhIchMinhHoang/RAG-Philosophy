# Coding Conventions

## File Naming

| Type | Convention | Example |
|------|------------|---------|
| Python files | snake_case | `step1_parser.py` |
| Python classes | PascalCase | `HybridPDFParser` |
| Python functions | snake_case | `build_vector_db` |
| Python constants | UPPER_SNAKE_CASE | `TOP_K_RESULTS` |
| JS files | camelCase | `api.js` |
| JS functions/vars | camelCase | `chatStream` |
| CSS classes | kebab-case | `chat-shell` |

## Python Style

### Imports

```python
# Standard library first
import os
import sys
from typing import List, Optional

# Third-party
import fitz
from langchain_core.documents import Document

# Local (relative)
from common.logging_utils import configure_logging, get_logger
from config import Config
```

### Docstrings

```python
def function_name(param: str) -> int:
    """
    Brief one-liner description.

    Args:
        param: Description of parameter.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param is invalid.
    """
```

### Type Hints

```python
def chunk_documents(pages: List[Document]) -> Tuple[List[Document], List[Document]]:
    """Return (child_docs, parent_docs)."""
```

## JavaScript Style

### Async/Await

```javascript
async function uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(url, {
        method: 'POST',
        body: formData,
    });
    return response.json();
}
```

### Event Handlers

```javascript
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = await API.login(email, password);
    transitionManager.transitionTo('dashboard');
});
```

## CSS Conventions

```css
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.chat-input {
    padding: 12px;
    border-radius: 8px;
}
```

## Git Commit Messages

```
<type>: <short description>

<body (optional)>

<footer (optional)>
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`

Examples:
```
feat: add PDF page image rendering endpoint

fix: resolve empty retrieval for queries with no sources

docs: document chunking strategy in docs/rag/
```

## File Organization

```
rag_core/
├── config.py              # All configuration
├── pipeline.py            # Orchestrator
├── step1_parser.py        # Single responsibility
├── step2_chunker.py       # Single responsibility
├── step3_vector_db.py     # Single responsibility
├── step4_generator.py    # Single responsibility
├── common/                # Shared utilities
│   ├── __init__.py
│   ├── logging_utils.py
│   ├── pdf_utils.py
│   └── embeddings.py
└── tests/                 # Unit tests
```