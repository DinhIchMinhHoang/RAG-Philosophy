import { BASE_URL, getToken, request } from './client.js';

export async function uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    const headers = {};
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${BASE_URL}/documents`, {
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
    const token = getToken();
    if (!token) {
        const err = new Error('Please sign in first');
        if (onError) onError(err);
        return controller;
    }

    fetch(`${BASE_URL}/chat/stream`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
        },
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
    const documents = await request('/documents', { method: 'GET' });
    if (!Array.isArray(documents)) return documents;

    const sources = documents.map((doc) => doc.filename).filter(Boolean);
    return {
        sources,
        count: sources.length,
        has_sources: sources.length > 0,
        documents,
    };
}

export async function getJob(jobId) {
    return await request(`/jobs/${encodeURIComponent(jobId)}`, { method: 'GET' });
}
