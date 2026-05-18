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

export async function getAdminJobs() {
    return await request('/admin/jobs', { method: 'GET' });
}

export async function reindexDocument(documentId) {
    return await request(`/documents/${encodeURIComponent(documentId)}/reindex`, { method: 'POST' });
}
