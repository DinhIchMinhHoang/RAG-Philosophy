import { store } from '../../state/store.js';
import { getAdminUsers, createAdminUser, deleteAdminUser, getAdminDocuments, reindexDocument, getAdminJobs } from '../../api/admin.js';

const emptyStateMessages = {
    users: 'No users found. Create the first user.',
    documents: 'No documents found. Upload a document to begin.',
    jobs: 'No jobs running yet. Ingest a document to see jobs.'
};

let cachedUsers = [];
let cachedDocuments = [];
let cachedJobs = [];

function debounce(fn, delay = 180) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

function filterUsers(users, query) {
    if (!query) return users;
    const q = query.toLowerCase();
    return users.filter(u =>
        (u.username || '').toLowerCase().includes(q) ||
        (u.email || '').toLowerCase().includes(q)
    );
}

function filterDocuments(documents, query) {
    if (!query) return documents;
    const q = query.toLowerCase();
    return documents.filter(d =>
        (d.filename || '').toLowerCase().includes(q) ||
        (d.document_id || '').toLowerCase().includes(q) ||
        (d.id || '').toLowerCase().includes(q)
    );
}

function filterJobs(jobs, query) {
    if (!query) return jobs;
    const q = query.toLowerCase();
    return jobs.filter(j =>
        (j.job_id || '').toLowerCase().includes(q) ||
        (j.id || '').toLowerCase().includes(q) ||
        (j.document_id || '').toLowerCase().includes(q) ||
        (j.status || '').toLowerCase().includes(q)
    );
}

function setFeedback(target, message, type = 'info') {
    if (!target) return;
    target.textContent = message || '';
    target.dataset.state = type;
}

function formatDate(value) {
    if (!value) return '—';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return '—';
    return date.toLocaleString();
}

function createMetaLine(label, value) {
    const div = document.createElement('div');
    div.className = 'list-meta';
    const name = document.createElement('span');
    name.className = 'meta-label';
    name.textContent = label;
    const content = document.createElement('span');
    content.className = 'meta-value';
    content.textContent = value || '—';
    div.appendChild(name);
    div.appendChild(content);
    return div;
}

function updateEmptyState(list, type, hasItems) {
    const empty = list?.querySelector(`[data-empty="${type}"]`);
    if (!empty) return;
    empty.textContent = emptyStateMessages[type] || 'Nothing here yet.';
    empty.style.display = hasItems ? 'none' : 'flex';
}

function renderUsers(list, users) {
    if (!list) return;
    list.querySelectorAll('.list-item').forEach(el => el.remove());
    const items = Array.isArray(users) ? users : [];
    updateEmptyState(list, 'users', items.length > 0);

    items.forEach(user => {
        const item = document.createElement('div');
        item.className = 'list-item';

        const identity = document.createElement('div');
        identity.className = 'list-identity';

        const name = document.createElement('div');
        name.className = 'list-title';
        name.textContent = user.username || user.display_name || user.email || 'Unknown user';

        const email = document.createElement('div');
        email.className = 'list-subtitle';
        email.textContent = user.email || '—';

        identity.appendChild(name);
        identity.appendChild(email);

        const meta = document.createElement('div');
        meta.className = 'list-meta-grid';
        meta.appendChild(createMetaLine('User ID', user.id ? String(user.id) : '—'));
        meta.appendChild(createMetaLine('Role', (user.email || '').toLowerCase().endsWith('@lumina.com.vn') ? 'Admin' : 'Member'));

        const actions = document.createElement('div');
        actions.className = 'list-actions';
        const delButton = document.createElement('button');
        delButton.className = 'auth-button is-ghost danger';
        delButton.type = 'button';
        delButton.textContent = 'Delete';
        delButton.dataset.action = 'delete-user';
        delButton.dataset.userId = user.id;
        actions.appendChild(delButton);

        item.appendChild(identity);
        item.appendChild(meta);
        item.appendChild(actions);
        list.appendChild(item);
    });
}

function renderDocuments(list, documents) {
    if (!list) return;
    list.querySelectorAll('.list-item').forEach(el => el.remove());
    const items = Array.isArray(documents) ? documents : [];
    updateEmptyState(list, 'documents', items.length > 0);

    items.forEach(doc => {
        const item = document.createElement('div');
        item.className = 'list-item';

        const identity = document.createElement('div');
        identity.className = 'list-identity';

        const name = document.createElement('div');
        name.className = 'list-title';
        name.textContent = doc.filename || doc.name || 'Untitled document';

        const subtitle = document.createElement('div');
        subtitle.className = 'list-subtitle';
        subtitle.textContent = doc.document_id || doc.id || '—';

        identity.appendChild(name);
        identity.appendChild(subtitle);

        const meta = document.createElement('div');
        meta.className = 'list-meta-grid';
        meta.appendChild(createMetaLine('Status', doc.latest_job?.status || '—'));
        meta.appendChild(createMetaLine('Updated', formatDate(doc.updated_at || doc.updatedAt)));

        const actions = document.createElement('div');
        actions.className = 'list-actions';
        const reindexButton = document.createElement('button');
        reindexButton.className = 'auth-button is-ghost';
        reindexButton.type = 'button';
        reindexButton.textContent = 'Reindex';
        reindexButton.dataset.action = 'reindex-doc';
        reindexButton.dataset.documentId = doc.document_id || doc.id;
        actions.appendChild(reindexButton);

        item.appendChild(identity);
        item.appendChild(meta);
        item.appendChild(actions);
        list.appendChild(item);
    });
}

function renderJobs(list, jobs) {
    if (!list) return;
    list.querySelectorAll('.list-item').forEach(el => el.remove());
    const items = Array.isArray(jobs) ? jobs : [];
    updateEmptyState(list, 'jobs', items.length > 0);

    items.forEach(job => {
        const item = document.createElement('div');
        item.className = 'list-item';

        const identity = document.createElement('div');
        identity.className = 'list-identity';

        const name = document.createElement('div');
        name.className = 'list-title';
        name.textContent = job.job_id || job.id || 'Job';

        const subtitle = document.createElement('div');
        subtitle.className = 'list-subtitle';
        subtitle.textContent = job.document_id || '—';

        identity.appendChild(name);
        identity.appendChild(subtitle);

        const meta = document.createElement('div');
        meta.className = 'list-meta-grid';
        meta.appendChild(createMetaLine('Status', job.status || '—'));
        meta.appendChild(createMetaLine('Stage', job.stage || '—'));
        meta.appendChild(createMetaLine('Progress', job.progress_pct != null ? `${job.progress_pct}%` : '—'));

        if (job.error_message) {
            const err = document.createElement('div');
            err.className = 'list-error';
            err.textContent = job.error_message;
            meta.appendChild(err);
        }

        item.appendChild(identity);
        item.appendChild(meta);
        list.appendChild(item);
    });
}

let currentUserQuery = '';
let currentDocQuery = '';
let currentJobQuery = '';

async function refreshUsers(list, feedback, preserveQuery = true) {
    try {
        setFeedback(feedback, 'Loading users...', 'loading');
        const users = await getAdminUsers();
        cachedUsers = Array.isArray(users) ? users : [];
        const filtered = filterUsers(cachedUsers, preserveQuery ? currentUserQuery : '');
        renderUsers(list, filtered);
        setFeedback(feedback, '', '');
    } catch (err) {
        setFeedback(feedback, err.message || 'Failed to load users', 'error');
    }
}

async function refreshDocuments(list, feedback, preserveQuery = true) {
    try {
        setFeedback(feedback, 'Loading documents...', 'loading');
        const documents = await getAdminDocuments();
        cachedDocuments = Array.isArray(documents) ? documents : (documents.documents || []);
        const filtered = filterDocuments(cachedDocuments, preserveQuery ? currentDocQuery : '');
        renderDocuments(list, filtered);
        setFeedback(feedback, '', '');
    } catch (err) {
        setFeedback(feedback, err.message || 'Failed to load documents', 'error');
    }
}

async function refreshJobs(list, feedback, preserveQuery = true) {
    try {
        setFeedback(feedback, 'Loading jobs...', 'loading');
        const jobs = await getAdminJobs();
        cachedJobs = Array.isArray(jobs) ? jobs : (jobs.jobs || []);
        const filtered = filterJobs(cachedJobs, preserveQuery ? currentJobQuery : '');
        renderJobs(list, filtered);
        setFeedback(feedback, '', '');
    } catch (err) {
        setFeedback(feedback, err.message || 'Failed to load jobs', 'error');
    }
}

export function initAdminScene(transitionManager) {
    const adminScene = document.getElementById('scene-admin');
    if (!adminScene) return;

    const tabs = Array.from(adminScene.querySelectorAll('.admin-tab'));
    const panels = Array.from(adminScene.querySelectorAll('.admin-panel'));
    const backButton = adminScene.querySelector('.admin-back-button');

    if (backButton) {
        backButton.addEventListener('click', (e) => {
            e.preventDefault();
            transitionManager.transitionTo('dashboard');
        });
    }

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const target = tab.dataset.tab;
            panels.forEach(panel => {
                panel.classList.toggle('active', panel.dataset.panel === target);
            });
        });
    });

    const userList = adminScene.querySelector('[data-list="users"]');
    const docList = adminScene.querySelector('[data-list="documents"]');
    const jobList = adminScene.querySelector('[data-list="jobs"]');
    const feedback = adminScene.querySelector('[data-feedback="create-user"]');

    const userSearchInput = adminScene.querySelector('[data-search="users"]');
    const docSearchInput = adminScene.querySelector('[data-search="documents"]');
    const jobSearchInput = adminScene.querySelector('[data-search="jobs"]');

    const handleUserSearch = debounce((query) => {
        currentUserQuery = query;
        const filtered = filterUsers(cachedUsers, query);
        renderUsers(userList, filtered);
    }, 180);

    const handleDocSearch = debounce((query) => {
        currentDocQuery = query;
        const filtered = filterDocuments(cachedDocuments, query);
        renderDocuments(docList, filtered);
    }, 180);

    const handleJobSearch = debounce((query) => {
        currentJobQuery = query;
        const filtered = filterJobs(cachedJobs, query);
        renderJobs(jobList, filtered);
    }, 180);

    if (userSearchInput) {
        userSearchInput.addEventListener('input', (e) => handleUserSearch(e.target.value));
    }
    if (docSearchInput) {
        docSearchInput.addEventListener('input', (e) => handleDocSearch(e.target.value));
    }
    if (jobSearchInput) {
        jobSearchInput.addEventListener('input', (e) => handleJobSearch(e.target.value));
    }

    const syncSearchInputs = () => {
        if (userSearchInput) userSearchInput.value = currentUserQuery;
        if (docSearchInput) docSearchInput.value = currentDocQuery;
        if (jobSearchInput) jobSearchInput.value = currentJobQuery;
    };

    adminScene.querySelectorAll('.admin-refresh').forEach(btn => {
        btn.addEventListener('click', async () => {
            const action = btn.dataset.action;
            if (action === 'refresh-users') await refreshUsers(userList, feedback, true);
            if (action === 'refresh-documents') await refreshDocuments(docList, feedback, true);
            if (action === 'refresh-jobs') await refreshJobs(jobList, feedback, true);
        });
    });

    adminScene.addEventListener('click', async (ev) => {
        const target = ev.target.closest('button');
        if (!target) return;
        const action = target.dataset.action;
        if (action === 'delete-user') {
            ev.preventDefault();
            const userId = target.dataset.userId;
            if (!userId) return;
            if (!confirm('Delete this user?')) return;
            try {
                await deleteAdminUser(userId);
                await refreshUsers(userList, feedback);
            } catch (err) {
                setFeedback(feedback, err.message || 'Failed to delete user', 'error');
            }
        }
        if (action === 'reindex-doc') {
            ev.preventDefault();
            const documentId = target.dataset.documentId;
            if (!documentId) return;
            try {
                await reindexDocument(documentId);
                setFeedback(feedback, 'Reindex job created.', 'success');
            } catch (err) {
                setFeedback(feedback, err.message || 'Failed to reindex document', 'error');
            }
        }
    });

    const createForm = adminScene.querySelector('[data-form="create-user"]');
    if (createForm) {
        createForm.addEventListener('submit', async (ev) => {
            ev.preventDefault();
            const formData = new FormData(createForm);
            const payload = {
                username: String(formData.get('username') || '').trim(),
                email: String(formData.get('email') || '').trim(),
                password: String(formData.get('password') || ''),
            };
            if (!payload.username || !payload.email || !payload.password) {
                setFeedback(feedback, 'Fill in all fields to create a user.', 'error');
                return;
            }
            try {
                setFeedback(feedback, 'Creating user...', 'loading');
                await createAdminUser(payload);
                createForm.reset();
                setFeedback(feedback, 'User created.', 'success');
                await refreshUsers(userList, feedback);
            } catch (err) {
                setFeedback(feedback, err.message || 'Failed to create user', 'error');
            }
        });
    }

    const refreshAll = () => {
        if (!store.getIsAdmin()) return;
        refreshUsers(userList, feedback);
        refreshDocuments(docList, feedback);
        refreshJobs(jobList, feedback);
    };

    document.addEventListener('admin:show', () => {
        refreshAll();
        syncSearchInputs();
    });
    refreshAll();
    syncSearchInputs();
}
