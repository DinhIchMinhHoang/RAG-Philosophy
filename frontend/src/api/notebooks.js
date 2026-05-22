import { request } from './client.js';

export async function getNotebooks() {
    return await request('/notebooks', { method: 'GET' });
}

export async function createNotebook(payload) {
    return await request('/notebooks', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}

export async function updateNotebook(id, payload) {
    return await request(`/notebooks/${encodeURIComponent(id)}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
    });
}

export async function deleteNotebook(id) {
    return await request(`/notebooks/${encodeURIComponent(id)}`, { method: 'DELETE' });
}

export async function getLatestNotebookConversation(notebookId, { limit = 50 } = {}) {
    return await request(`/notebooks/${encodeURIComponent(notebookId)}/conversations/latest?limit=${limit}`, { method: 'GET' });
}