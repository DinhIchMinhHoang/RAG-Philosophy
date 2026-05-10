import { BASE_URL, getToken } from './client.js';

export async function uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    const headers = {};
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${BASE_URL}/documents/upload`, {
        method: 'POST', headers, body: formData
    });
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed: ${response.status}`);
    }
    return await response.json();
}

export function chatStream(message, { onToken, onDone, onError }) {
    const controller = new AbortController();
    fetch(`${BASE_URL}/chat/stream`, {
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
            const lines = buffer.split('\n');
            buffer = lines.pop();
            for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed || !trimmed.startsWith('data: ')) continue;
                try {
                    const payload = JSON.parse(trimmed.slice(6));
                    if (payload.done) { if (onDone) onDone(); return; }
                    if (payload.token && onToken) onToken(payload.token);
                } catch (e) { /* skip malformed */ }
            }
        }
        if (onDone) onDone();
    })
    .catch((err) => {
        if (err.name === 'AbortError') return;
        console.error('[API.chatStream] Error:', err);
        if (onError) onError(err);
    });
    return controller;
}

export async function listSources() {
    return await request('/documents/sources', { method: 'GET' });
}
