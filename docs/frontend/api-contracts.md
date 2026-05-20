# API Contracts

## API Object (frontend/api.js)

```javascript
const API = {
<<<<<<< HEAD
    BASE_URL: 'http://localhost:8000',
=======
    BASE_URL: '/api',
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca

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
<<<<<<< HEAD
=======
    getJob(jobId: String) -> Promise<JobResponse>
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca

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
<<<<<<< HEAD
- **Endpoint**: POST /signup
=======
- **Endpoint**: POST /api/signup
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
- **Request**: `{username, email, password}`
- **Response**: `{access_token, token_type}`
- **Side Effect**: Stores token in localStorage

### login(email, password)
<<<<<<< HEAD
- **Endpoint**: POST /login
=======
- **Endpoint**: POST /api/login
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
- **Request**: `{email, password}`
- **Response**: `{access_token, token_type}`
- **Side Effect**: Stores token in localStorage

### changePassword(currentPassword, newPassword)
<<<<<<< HEAD
- **Endpoint**: POST /change-password
=======
- **Endpoint**: POST /api/change-password
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
- **Headers**: Authorization: Bearer token
- **Request**: `{current_password, new_password}`
- **Response**: `{message: "Password changed successfully!"}`

### uploadDocument(file)
<<<<<<< HEAD
- **Endpoint**: POST /documents/upload
- **Headers**: Authorization: Bearer token
- **Body**: multipart/form-data with 'file' field
- **Response**: `{filename, status, pages, chunks}`

### listSources()
- **Endpoint**: GET /documents/sources
- **Response**: `{sources: [], count: 0, has_sources: false}`

### chatStream(message, callbacks)
- **Endpoint**: POST /chat/stream
=======
- **Endpoint**: POST /api/documents
- **Headers**: Authorization: Bearer token
- **Body**: multipart/form-data with 'file' field
- **Response**: `{document_id, job_id, status, pipeline_version, object_key}`

### listSources()
- **Endpoint**: GET /api/documents
- **Response**: compatibility wrapper `{sources, count, has_sources, documents}`

### getJob(jobId)
- **Endpoint**: GET /api/jobs/{jobId}
- **Response**: `{job_id, status, stage, progress_pct, stage_detail, error_message, ...}`

### chatStream(message, callbacks)
- **Endpoint**: POST /api/chat/stream
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
- **Request**: `{message: "question"}`
- **Response**: SSE stream
- **Callback**: `onToken` called for each chunk, `onDone` at end

## Error Handling

```javascript
// API request wrapper
async request(endpoint, options = {}) {
    const response = await fetch(url, {...options, headers});
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `Error: ${response.status}`);
    }
    return response.json();
}
```

## Usage Example

```javascript
// Login and upload
await API.login(email, password);
const result = await API.uploadDocument(pdfFile);
<<<<<<< HEAD
=======
const job = await API.getJob(result.job_id);
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca

// Chat with streaming
API.chatStream("What is philosophy?", {
    onToken: (token) => document.getElementById('chat').innerHTML += token,
    onDone: () => console.log('Complete'),
    onError: (err) => console.error(err)
});
<<<<<<< HEAD
```
=======
```
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
