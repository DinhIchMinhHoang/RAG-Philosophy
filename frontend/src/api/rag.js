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
        const err = new Error(errorData.detail || `Upload failed: ${response.status}`);
        if (response.status === 409) {
            err.isDuplicate = true;
            err.documentId = errorData.document_id;
            err.filename = errorData.filename;
        }
        throw err;
    }
    return await response.json();
}

export async function replaceDocument(documentId, file) {
    const formData = new FormData();
    formData.append('file', file);
    const headers = {};
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${BASE_URL}/documents/${encodeURIComponent(documentId)}`, {
        method: 'POST', headers, body: formData
    });
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Replace failed: ${response.status}`);
    }
    return await response.json();
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
            let finalPayload = null;
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop();
                for (const line of lines) {
                    const trimmed = line.trim();
                    if (!trimmed || !trimmed.startsWith('data: ')) continue;
                    let streamPayload;
                    try {
                        streamPayload = JSON.parse(trimmed.slice(6));
                    } catch (e) { /* skip malformed */ }
                    if (!streamPayload) continue;
                    if (streamPayload.type === 'error' || streamPayload.error) {
                        throw new Error(streamPayload.error || 'Chat stream failed');
                    }
                    if (streamPayload.done) {
                        finalPayload = streamPayload;
                        if (onDone) onDone(streamPayload);
                        return;
                    }
                    if (streamPayload.token && onToken) onToken(streamPayload.token);
                }
            }
            if (onDone) onDone(finalPayload);
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
