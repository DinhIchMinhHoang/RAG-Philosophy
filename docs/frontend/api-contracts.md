# API Contracts

## API Object (frontend/api.js)

```javascript
const API = {
    BASE_URL: '/api',

    // Authentication
    signup(username, email, password) -> Promise<Token>
    login(email, password) -> Promise<Token>
    changePassword(currentPassword, newPassword) -> Promise<Message>
    isAuthenticated() -> Boolean
    getToken() -> String | null
    setToken(token) -> void
    clearToken() -> void

    // RAG Documents
    uploadDocument(file: File) -> Promise<UploadResult>
    listSources() -> Promise<SourcesResponse>
    getJob(jobId: String) -> Promise<JobResponse>

    // RAG Chat
    chatStream(message: String, {
        onToken: (token: String) => void,
        onDone: () => void,
        onError: (err: Error) => void
    }) -> AbortController

    // Generic request
    request(endpoint: String, options: Object) -> Promise<any>
}
```

## Method Details

### signup(username, email, password)
- **Endpoint**: POST /api/signup
- **Request**: `{username, email, password}`
- **Response**: `{access_token, token_type}`
- **Side Effect**: Stores token in localStorage

### login(email, password)
- **Endpoint**: POST /api/login
- **Request**: `{email, password}`
- **Response**: `{access_token, token_type}`
- **Side Effect**: Stores token in localStorage

### changePassword(currentPassword, newPassword)
- **Endpoint**: POST /api/change-password
- **Headers**: Authorization: Bearer token
- **Request**: `{current_password, new_password}`
- **Response**: `{message: "Password changed successfully!"}`

### uploadDocument(file)
- **Endpoint**: POST /api/documents
- **Headers**: Authorization: Bearer token
- **Body**: multipart/form-data with 'file' field
- **Response**: `{document_id, job_id, status, pipeline_version, object_key}`

### listSources()
- **Endpoint**: GET /api/documents
- **Response**: compatibility wrapper `{sources, count, has_sources, documents}`

### getJob(jobId)
- **Endpoint**: GET /api/jobs/{jobId}
- **Response**: `{job_id, document_id, status, stage, progress_pct, stage_detail, error_message, pipeline_version, queued_at, started_at, finished_at}`

### chatStream(message, callbacks)
- **Endpoint**: POST /api/chat/stream
- **Request**: `{message: "question"}`
- **Response**: SSE stream with token events plus a final `done: true` payload
- **Callback**: `onToken` called for each chunk, `onDone` receives the final SSE payload, `onError` handles stream failures

## Error Handling

```javascript
// API request wrapper
async request(endpoint, options = {}) {
    const response = await fetch(url, {...options, headers});
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || error?.error?.message || `Error: ${response.status}`);
    }
    return response.json();
}
```

## Usage Example

```javascript
// Login and upload
await API.login(email, password);
const result = await API.uploadDocument(pdfFile);
const job = await API.getJob(result.job_id);

// Chat with streaming
API.chatStream("What is philosophy?", {
    onToken: (token) => document.getElementById('chat').innerHTML += token,
    onDone: () => console.log('Complete'),
    onError: (err) => console.error(err)
});
```
