import { store } from '../../state/store.js';
import { getAdminUsers, createAdminUser, deleteAdminUser, getAdminLibrary, reindexAdminDocument, deleteAdminNotebook, deleteAdminDocument, getAdminJobs } from '../../api/admin.js';

const emptyStateMessages = {
    users: 'No users found. Create the first user.',
    library: 'No library data yet.',
    jobs: 'No jobs running yet. Ingest a document to see jobs.'
};

let cachedUsers = [];
let cachedJobs = [];
let cachedLibrary = [];

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

function filterLibrary(users, query) {
    if (!query) return users;
    const q = query.toLowerCase();
    return users.filter(user => {
        const userMatch = (user.username || '').toLowerCase().includes(q) || (user.email || '').toLowerCase().includes(q);
        if (userMatch) return true;
        return (user.notebooks || []).some(nb => {
            const nbMatch = (nb.title || '').toLowerCase().includes(q);
            if (nbMatch) return true;
            return (nb.documents || []).some(doc =>
                (doc.filename || '').toLowerCase().includes(q) ||
                (doc.document_id || '').toLowerCase().includes(q)
            );
        });
    });
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

function renderSkeletonRows(list, type = 'users', count = 5) {
    list.querySelectorAll('.list-item').forEach(el => el.remove());
    list.querySelectorAll('.list-skeleton').forEach(el => el.remove());
    for (let i = 0; i < count; i++) {
        const row = document.createElement('div');
        row.className = 'list-item list-skeleton';
        if (type === 'users') {
            row.innerHTML = `
                <div class="skeleton-row">
                    <div class="skeleton skeleton-avatar"></div>
                    <div style="flex:1;display:flex;flex-direction:column;gap:6px;">
                        <div class="skeleton skeleton-line short"></div>
                        <div class="skeleton skeleton-line medium"></div>
                    </div>
                </div>`;
        } else {
            row.innerHTML = `
                <div class="skeleton-row">
                    <div style="flex:1;display:flex;flex-direction:column;gap:6px;">
                        <div class="skeleton skeleton-line medium"></div>
                        <div class="skeleton skeleton-line short"></div>
                    </div>
                </div>`;
        }
        list.appendChild(row);
    }
}

function clearSkeletonRows(list) {
    list.querySelectorAll('.list-skeleton').forEach(el => el.remove());
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

function renderLibrary(list, users) {
    if (!list) return;
    list.querySelectorAll('.list-item').forEach(el => el.remove());
    const items = Array.isArray(users) ? users : [];
    updateEmptyState(list, 'library', items.length > 0);

    items.forEach(user => {
        const userRow = document.createElement('div');
        userRow.className = 'list-item';
        userRow.innerHTML = `
            <div class="list-identity">
                <div class="list-title">${user.username || user.email || 'User'}</div>
                <div class="list-subtitle">${user.email || ''}</div>
            </div>
            <div class="list-meta-grid">
                ${createMetaLine('User ID', user.id ? String(user.id) : '—').outerHTML}
                ${createMetaLine('Notebooks', String((user.notebooks || []).length)).outerHTML}
            </div>
            <div class="list-actions">
                <button class="auth-button is-ghost danger" data-action="delete-user" data-user-id="${user.id}">Delete</button>
            </div>`;
        list.appendChild(userRow);

        (user.notebooks || []).forEach(nb => {
            const nbRow = document.createElement('div');
            nbRow.className = 'list-item';
            nbRow.innerHTML = `
                <div class="list-identity">
                    <div class="list-title">${nb.title || 'Untitled notebook'}</div>
                    <div class="list-subtitle">Notebook #${nb.id}</div>
                </div>
                <div class="list-meta-grid">
                    ${createMetaLine('Community', nb.is_community ? 'Yes' : 'No').outerHTML}
                    ${createMetaLine('Documents', String((nb.documents || []).length)).outerHTML}
                </div>
                <div class="list-actions">
                    ${nb.is_virtual ? '' : `<button class="auth-button is-ghost danger" data-action="delete-notebook" data-notebook-id="${nb.id}">Delete</button>`}
                </div>`;
            list.appendChild(nbRow);

            (nb.documents || []).forEach(doc => {
                const docRow = document.createElement('div');
                docRow.className = 'list-item';
                docRow.innerHTML = `
                    <div class="list-identity">
                        <div class="list-title">${doc.filename || 'Untitled document'}</div>
                        <div class="list-subtitle">${doc.document_id || ''}</div>
                    </div>
                    <div class="list-meta-grid">
                        ${createMetaLine('Status', doc.latest_job?.status || '—').outerHTML}
                        ${createMetaLine('Updated', formatDate(doc.updated_at || doc.updatedAt)).outerHTML}
                    </div>
                    <div class="list-actions">
                        <button class="auth-button is-ghost" data-action="reindex-admin-doc" data-document-id="${doc.document_id}">Reindex</button>
                        <button class="auth-button is-ghost danger" data-action="delete-admin-doc" data-document-id="${doc.document_id}">Delete</button>
                    </div>`;
                list.appendChild(docRow);
            });
        });
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
let currentJobQuery = '';
let currentLibraryQuery = '';

async function refreshUsers(list, feedback, preserveQuery = true) {
    try {
        renderSkeletonRows(list, 'users', 5);
        const users = await getAdminUsers();
        clearSkeletonRows(list);
        cachedUsers = Array.isArray(users) ? users : [];
        const filtered = filterUsers(cachedUsers, preserveQuery ? currentUserQuery : '');
        renderUsers(list, filtered);
    } catch (err) {
        clearSkeletonRows(list);
        setFeedback(feedback, err.message || 'Failed to load users', 'error');
    }
}

async function refreshLibrary(list, feedback, preserveQuery = true) {
    try {
        renderSkeletonRows(list, 'documents', 5);
        const library = await getAdminLibrary();
        clearSkeletonRows(list);
        cachedLibrary = Array.isArray(library?.users) ? library.users : [];
        const filtered = filterLibrary(cachedLibrary, preserveQuery ? currentLibraryQuery : '');
        renderLibrary(list, filtered);
    } catch (err) {
        clearSkeletonRows(list);
        setFeedback(feedback, err.message || 'Failed to load library', 'error');
    }
}

async function refreshJobs(list, feedback, preserveQuery = true) {
    try {
        renderSkeletonRows(list, 'jobs', 5);
        const jobs = await getAdminJobs();
        clearSkeletonRows(list);
        cachedJobs = Array.isArray(jobs) ? jobs : (jobs.jobs || []);
        const filtered = filterJobs(cachedJobs, preserveQuery ? currentJobQuery : '');
        renderJobs(list, filtered);
    } catch (err) {
        clearSkeletonRows(list);
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
    const jobSearchInput = adminScene.querySelector('[data-search="jobs"]');
    const librarySearchInput = adminScene.querySelector('[data-search="library"]');

    const handleUserSearch = debounce((query) => {
        currentUserQuery = query;
        const filtered = filterUsers(cachedUsers, query);
        renderUsers(userList, filtered);
    }, 180);

    const handleJobSearch = debounce((query) => {
        currentJobQuery = query;
        const filtered = filterJobs(cachedJobs, query);
        renderJobs(jobList, filtered);
    }, 180);

    const handleLibrarySearch = debounce((query) => {
        currentLibraryQuery = query;
        const filtered = filterLibrary(cachedLibrary, query);
        renderLibrary(docList, filtered);
    }, 180);

    if (userSearchInput) {
        userSearchInput.addEventListener('input', (e) => handleUserSearch(e.target.value));
    }
    if (jobSearchInput) {
        jobSearchInput.addEventListener('input', (e) => handleJobSearch(e.target.value));
    }
    if (librarySearchInput) {
        librarySearchInput.addEventListener('input', (e) => handleLibrarySearch(e.target.value));
    }

    const syncSearchInputs = () => {
        if (userSearchInput) userSearchInput.value = currentUserQuery;
        if (librarySearchInput) librarySearchInput.value = currentLibraryQuery;
    };

    adminScene.querySelectorAll('.admin-refresh').forEach(btn => {
        btn.addEventListener('click', async () => {
            const action = btn.dataset.action;
            if (action === 'refresh-users') await refreshUsers(userList, feedback, true);
            if (action === 'refresh-library') await refreshLibrary(docList, feedback, true);
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
            if (!confirm('Delete this user and all related data?')) return;
            try {
                await deleteAdminUser(userId);
                await refreshUsers(userList, feedback);
                await refreshLibrary(docList, feedback);
            } catch (err) {
                setFeedback(feedback, err.message || 'Failed to delete user', 'error');
            }
        }
        if (action === 'reindex-admin-doc') {
            ev.preventDefault();
            const documentId = target.dataset.documentId;
            if (!documentId) return;
            try {
                await reindexAdminDocument(documentId);
                setFeedback(feedback, 'Reindex job created.', 'success');
            } catch (err) {
                setFeedback(feedback, err.message || 'Failed to reindex document', 'error');
            }
        }
        if (action === 'delete-notebook') {
            ev.preventDefault();
            const notebookId = target.dataset.notebookId;
            if (!notebookId) return;
            if (!confirm('Delete this notebook and all related data?')) return;
            try {
                await deleteAdminNotebook(notebookId);
                await refreshLibrary(docList, feedback);
            } catch (err) {
                setFeedback(feedback, err.message || 'Failed to delete notebook', 'error');
            }
        }
        if (action === 'delete-admin-doc') {
            ev.preventDefault();
            const documentId = target.dataset.documentId;
            if (!documentId) return;
            if (!confirm('Delete this document and vectors?')) return;
            try {
                await deleteAdminDocument(documentId);
                await refreshLibrary(docList, feedback);
            } catch (err) {
                setFeedback(feedback, err.message || 'Failed to delete document', 'error');
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
        refreshLibrary(docList, feedback);
        refreshJobs(jobList, feedback);
    };

    document.addEventListener('admin:show', () => {
        refreshAll();
        syncSearchInputs();
    });
    refreshAll();
    syncSearchInputs();
}
