// API Configuration and Authentication Helper
const API = {
    // Backend base URL - adjust this if backend runs on different host/port
    BASE_URL: 'http://localhost:8000',

    // Get stored access token
    getToken: () => {
        return localStorage.getItem('accessToken');
    },

    // Store access token
    setToken: (token) => {
        localStorage.setItem('accessToken', token);
    },

    // Clear stored token (on logout)
    clearToken: () => {
        localStorage.removeItem('accessToken');
    },

    // Make authenticated API request
    async request(endpoint, options = {}) {
        const url = `${API.BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Add authorization header if token exists
        const token = API.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            // Handle response
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const errorMsg = errorData.detail || `API Error: ${response.status}`;
                throw new Error(errorMsg);
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    },

    // Sign Up
    async signup(username, email, password) {
        const data = await API.request('/signup', {
            method: 'POST',
            body: JSON.stringify({
                username,
                email,
                password
            })
        });
        // Store token from response
        if (data.access_token) {
            API.setToken(data.access_token);
        }
        return data;
    },

    // Sign In
    async login(email, password) {
        const data = await API.request('/login', {
            method: 'POST',
            body: JSON.stringify({
                email,
                password
            })
        });
        // Store token from response
        if (data.access_token) {
            API.setToken(data.access_token);
        }
        return data;
    },

    // Change Password
    async changePassword(currentPassword, newPassword) {
        const data = await API.request('/change-password', {
            method: 'POST',
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });
        return data;
    },

    // Check if user is authenticated (has valid token)
    isAuthenticated: () => {
        return Boolean(API.getToken());
    },

    // ── RAG Document Upload ─────────────────────────────────────
    // Upload a PDF file to the backend for RAG ingestion.
    // Accepts a File object. Uses multipart/form-data (no JSON Content-Type).
    async uploadDocument(file) {
        const url = `${API.BASE_URL}/documents/upload`;
        const formData = new FormData();
        formData.append('file', file);

        const headers = {};
        const token = API.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        // NOTE: Do NOT set Content-Type — the browser sets the correct
        // multipart/form-data boundary automatically.

        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Upload failed: ${response.status}`);
        }

        return await response.json();
    },

    // ── RAG Chat — SSE Streaming ────────────────────────────────
    // Send a question and receive streamed answer tokens via SSE.
    // onToken(text)  — called for each text chunk
    // onDone()       — called when the stream finishes
    // onError(err)   — called on error
    // Returns an AbortController so the caller can cancel the stream.
    chatStream(message, { onToken, onDone, onError }) {
        const controller = new AbortController();
        const url = `${API.BASE_URL}/chat/stream`;

        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
            signal: controller.signal,
        })
        .then(async (response) => {
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Chat error: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });

                // Process complete SSE lines
                const lines = buffer.split('\n');
                buffer = lines.pop(); // keep incomplete line in buffer

                for (const line of lines) {
                    const trimmed = line.trim();
                    if (!trimmed || !trimmed.startsWith('data: ')) continue;

                    try {
                        const payload = JSON.parse(trimmed.slice(6));
                        if (payload.done) {
                            if (onDone) onDone();
                            return;
                        }
                        if (payload.token && onToken) {
                            onToken(payload.token);
                        }
                    } catch (e) {
                        // skip malformed SSE lines
                    }
                }
            }

            // Stream ended without explicit done signal
            if (onDone) onDone();
        })
        .catch((err) => {
            if (err.name === 'AbortError') return;
            console.error('[API.chatStream] Error:', err);
            if (onError) onError(err);
        });

        return controller;
    },

    // ── List ingested sources ───────────────────────────────────
    async listSources() {
        return await API.request('/documents/sources', { method: 'GET' });
    }
};
