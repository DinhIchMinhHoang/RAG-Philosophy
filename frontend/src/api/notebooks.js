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

export async function getLatestNotebookConversation(id, { limit = 50 } = {}) {
    const query = `?limit=${encodeURIComponent(limit)}`;
    return await request(`/notebooks/${encodeURIComponent(id)}/conversations/latest${query}`, { method: 'GET' });
}

export async function createSavedNotebookItem(id, payload) {
    return await request(`/notebooks/${encodeURIComponent(id)}/notes`, {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}
