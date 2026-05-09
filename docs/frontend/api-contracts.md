# API Contracts

## API Object (frontend/api.js)

```javascript
const API = {
    BASE_URL: 'http://localhost:8000',

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
- **Endpoint**: POST /signup
- **Request**: `{username, email, password}`
- **Response**: `{access_token, token_type}`
- **Side Effect**: Stores token in localStorage

### login(email, password)
- **Endpoint**: POST /login
- **Request**: `{email, password}`
- **Response**: `{access_token, token_type}`
- **Side Effect**: Stores token in localStorage

### changePassword(currentPassword, newPassword)
- **Endpoint**: POST /change-password
- **Headers**: Authorization: Bearer token
- **Request**: `{current_password, new_password}`
- **Response**: `{message: "Password changed successfully!"}`

### uploadDocument(file)
- **Endpoint**: POST /documents/upload
- **Headers**: Authorization: Bearer token
- **Body**: multipart/form-data with 'file' field
- **Response**: `{filename, status, pages, chunks}`

### listSources()
- **Endpoint**: GET /documents/sources
- **Response**: `{sources: [], count: 0, has_sources: false}`

### chatStream(message, callbacks)
- **Endpoint**: POST /chat/stream
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

// Chat with streaming
API.chatStream("What is philosophy?", {
    onToken: (token) => document.getElementById('chat').innerHTML += token,
    onDone: () => console.log('Complete'),
    onError: (err) => console.error(err)
});
```