# Common Errors

## Backend Errors

### 401 Unauthorized

**Symptom**: API returns 401 error

**Causes**:
1. Missing Authorization header
2. Invalid/malformed JWT token
3. Token expired (60 minutes)

**Fix**:
```javascript
// Include token in request
headers: { 'Authorization': `Bearer ${API.getToken()}` }
```

### 400 Bad Request - Empty Message

**Symptom**: `{"detail": "Message cannot be empty."}`

**Cause**: Chat message is empty or whitespace-only

**Fix**: Ensure message.trim().length > 0

### 400 Bad Request - Not a PDF

**Symptom**: `{"detail": "Only PDF files are supported."}`

**Cause**: Uploaded file doesn't end with .pdf

**Fix**: Verify file type before upload

## Python/Import Errors

### ModuleNotFoundError: No module named 'rag_core'

**Cause**: Python path doesn't include rag_core directory

**Fix**: `rag_service.py` handles this via sys.path manipulation

### EnvironmentError: GEMINI_API_KEY not set

**Cause**: Missing .env file or key not loaded

**Fix**: Create .env with `GEMINI_API_KEY=your_key`

## RAG Pipeline Errors

### ValueError: No documents parsed from PDFs

**Cause**: PDF parsing failed or returned empty

**Fix**: Check PDF is valid and not password-protected

### KeyError: parent_docs[x] missing 'doc_id'

**Cause**: chunk_documents failed to add doc_id

**Fix**: Check step2_chunker.py logic

## Frontend Errors

### SSE Not Receiving Data

**Cause**: Server not streaming correctly

**Fix**: Check browser console for errors, verify backend running

### localStorage Not Working

**Cause**: Third-party cookies blocked or private browsing

**Fix**: Check browser privacy settings