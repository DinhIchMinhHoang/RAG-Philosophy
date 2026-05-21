import { request } from './client.js';

export async function getAdminUsers() {
    return await request('/admin/users', { method: 'GET' });
}

export async function createAdminUser(payload) {
    return await request('/admin/users', {
        method: 'POST',
        body: JSON.stringify(payload)
    });
}

export async function deleteAdminUser(userId) {
    return await request(`/admin/users/${encodeURIComponent(userId)}`, { method: 'DELETE' });
}

export async function getAdminDocuments() {
    return await request('/admin/documents', { method: 'GET' });
}

export async function getAdminLibrary() {
    return await request('/admin/library', { method: 'GET' });
}

export async function getApiConfig() {
    return await request('/admin/api-config', { method: 'GET' });
}

export async function reindexDocument(documentId) {
    return await request(`/documents/${encodeURIComponent(documentId)}/reindex`, { method: 'POST' });
}

export async function reindexAdminDocument(documentId) {
    return await request(`/admin/documents/${encodeURIComponent(documentId)}/reindex`, { method: 'POST' });
}

export async function deleteAdminNotebook(notebookId) {
    return await request(`/admin/notebooks/${encodeURIComponent(notebookId)}`, { method: 'DELETE' });
}

export async function deleteAdminDocument(documentId) {
    return await request(`/admin/documents/${encodeURIComponent(documentId)}`, { method: 'DELETE' });
}
