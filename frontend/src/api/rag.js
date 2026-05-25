import { BASE_URL, getToken, request } from './client.js';

export async function uploadDocument(file, { notebookId } = {}) {
    const formData = new FormData();
    formData.append('file', file);
    if (notebookId) formData.append('notebook_id', String(notebookId));
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

export async function ingestUrl({ url, notebookId } = {}) {
    if (!url) throw new Error('missing url');
    const payload = { url };
    if (notebookId) payload.notebook_id = notebookId;
    return await request('/ingest/url', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}

export function chatStream(message, { conversationId, notebookId, onToken, onDone, onError }) {
    const controller = new AbortController();
    const token = getToken();
    if (!token) {
        const err = new Error('Please sign in first');
        if (onError) onError(err);
        return controller;
    }

    const payload = { message };
    if (conversationId) payload.conversation_id = conversationId;
    if (notebookId) payload.notebook_id = notebookId;

    fetch(`${BASE_URL}/chat/stream`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
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
                let payload;
                try {
                    payload = JSON.parse(trimmed.slice(6));
                } catch (e) {
                    continue;
                }
                if (payload.type === 'error') {
                    throw new Error(payload.error || 'Chat stream failed');
                }
                if (payload.done) { if (onDone) onDone(payload); return; }
                if (payload.token && onToken) onToken(payload.token);
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

export async function listSources({ notebookId } = {}) {
    const query = notebookId ? `?notebook_id=${encodeURIComponent(notebookId)}` : '';
    const documents = await request(`/documents${query}`, { method: 'GET' });
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

export async function renameSource({ notebookId, fileId, newName }) {
    if (!notebookId || !fileId || !newName) throw new Error('missing parameters');
    return await request(`/notebooks/${encodeURIComponent(notebookId)}/files/${encodeURIComponent(fileId)}/rename`, {
        method: 'PATCH',
        body: JSON.stringify({ new_file_name: newName }),
    });
}

export async function deleteSource({ notebookId, fileId }) {
    if (!notebookId || !fileId) throw new Error('missing parameters');
    return await request(`/notebooks/${encodeURIComponent(notebookId)}/files/${encodeURIComponent(fileId)}`, {
        method: 'DELETE',
    });
}
