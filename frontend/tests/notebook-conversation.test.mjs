import assert from 'node:assert/strict';

const storage = new Map();
globalThis.localStorage = {
    getItem: (key) => storage.get(key) || null,
    setItem: (key, value) => storage.set(key, value),
    removeItem: (key) => storage.delete(key),
};

const calls = [];
const jobResponses = new Map();
globalThis.fetch = async (url, options = {}) => {
    calls.push({ url, method: options.method || 'GET', body: options.body });
    if (url === '/api/notebooks/42/conversations/latest?limit=20') {
        return {
            ok: true,
            json: async () => ({
                conversation: { id: 'conv-42', notebook_id: 42 },
                messages: [{ id: 'm1', role: 'user', content: 'hello' }],
                has_conversation: true,
                limit: 20,
            }),
        };
    }
    if (url === '/api/notebooks/42/notes') {
        return {
            ok: true,
            json: async () => ({
                id: 'note-1',
                notebook_id: 42,
                kind: 'pin',
                content: 'important',
            }),
        };
    }
    if (String(url).startsWith('/api/jobs/')) {
        const jobId = decodeURIComponent(String(url).split('/').pop());
        const queue = jobResponses.get(jobId) || [];
        const next = queue.length > 1 ? queue.shift() : queue[0];
        if (next) {
            return {
                ok: true,
                json: async () => next,
            };
        }
    }
    return {
        ok: false,
        status: 404,
        json: async () => ({ detail: `Unexpected URL: ${url}` }),
    };
};

const { getLatestNotebookConversation, createSavedNotebookItem } = await import('../src/api/notebooks.js');
const {
    addSelectedSourceId,
    conversationCacheKey,
    formatJobProgress,
    getActiveSourceJobPollCount,
    getSelectedSourceIdsSet,
    readCachedConversation,
    readCachedSourceSelection,
    reconcileSourceSelectionForVisible,
    registerSourceJobPolling,
    resetSourceJobPollingForTests,
    sourceTypeClassForDocument,
    sourceSelectionCacheKey,
    writeCachedConversation,
    writeCachedSourceSelection,
} = await import('../src/ui/scenes/ChatScene.js');

const latest = await getLatestNotebookConversation(42, { limit: 20 });
assert.equal(calls[0].url, '/api/notebooks/42/conversations/latest?limit=20');
assert.equal(calls[0].method, 'GET');
assert.equal(latest.conversation.id, 'conv-42');
assert.equal(latest.messages[0].content, 'hello');

const saved = await createSavedNotebookItem(42, { kind: 'pin', content: 'important' });
assert.equal(calls[1].url, '/api/notebooks/42/notes');
assert.equal(calls[1].method, 'POST');
assert.deepEqual(JSON.parse(calls[1].body), { kind: 'pin', content: 'important' });
assert.equal(saved.id, 'note-1');

writeCachedConversation(42, {
    conversation: { id: 'conv-42' },
    messages: [{ id: 'm1', role: 'user', content: 'hello' }],
    has_conversation: true,
});
const key = conversationCacheKey(42);
assert.equal(key, 'notebook:42:conversation:last');
assert.equal(readCachedConversation(42).conversation.id, 'conv-42');

storage.set(key, JSON.stringify({ cached_at: 1, state: { conversation: { id: 'expired' }, messages: [] } }));
assert.equal(readCachedConversation(42), null);
assert.equal(storage.has(key), false);

reconcileSourceSelectionForVisible(101, ['doc-a', 'doc-b']);
assert.deepEqual(Array.from(getSelectedSourceIdsSet(101)).sort(), ['doc-a', 'doc-b']);
assert.equal(readCachedSourceSelection(101).explicit, false);

storage.set('notebook:104:sources:selected', JSON.stringify({
    cached_at: Date.now(),
    selected_source_ids: [],
    explicit: true,
}));
assert.equal(readCachedSourceSelection(104), null);
reconcileSourceSelectionForVisible(104, ['doc-a', 'doc-b']);
assert.deepEqual(Array.from(getSelectedSourceIdsSet(104)).sort(), ['doc-a', 'doc-b']);

writeCachedSourceSelection(102, new Set(['doc-a']), { explicit: true });
reconcileSourceSelectionForVisible(102, ['doc-a', 'doc-b']);
assert.deepEqual(Array.from(getSelectedSourceIdsSet(102)), ['doc-a']);
assert.deepEqual(readCachedSourceSelection(102).selectedIds, new Set(['doc-a']));

writeCachedSourceSelection(103, new Set(['old-doc']), { explicit: true });
assert.deepEqual(Array.from(getSelectedSourceIdsSet(103)), ['old-doc']);
addSelectedSourceId(103, 'new-doc');
assert.deepEqual(Array.from(getSelectedSourceIdsSet(103)).sort(), ['new-doc', 'old-doc']);

const sourceKey = sourceSelectionCacheKey(103);
assert.equal(sourceKey, 'notebook:103:sources:selected');
assert.equal(JSON.parse(storage.get(sourceKey)).explicit, true);
assert.equal(JSON.parse(storage.get(sourceKey)).schema_version, 2);

assert.equal(
    formatJobProgress({ status: 'running', stage: 'embedding', progress_pct: 56, stage_detail: 'embedding_batch=1/7' }),
    'Embedding chunks · 56%',
);
assert.equal(
    formatJobProgress({ status: 'running', stage: 'parsing', progress_pct: 18, stage_detail: 'parsed_pages=3/20' }),
    'Parsing document · 18%',
);
assert.equal(
    sourceTypeClassForDocument({ latest_job: { status: 'running', stage: 'embedding', progress_pct: 40 } }),
    'source-type uploading',
);
assert.equal(
    sourceTypeClassForDocument({ latest_job: { status: 'succeeded', stage: 'completed', progress_pct: 100 } }),
    'source-type',
);

const nativeSetTimeout = globalThis.setTimeout;
const nativeClearTimeout = globalThis.clearTimeout;
let nextTimerId = 1;
const timers = [];
globalThis.setTimeout = (fn, ms) => {
    const timer = { id: nextTimerId++, fn, ms, cleared: false };
    timers.push(timer);
    return timer.id;
};
globalThis.clearTimeout = (id) => {
    const timer = timers.find((candidate) => candidate.id === id);
    if (timer) timer.cleared = true;
};

globalThis.document = {
    body: {
        contains: (el) => el?.connected !== false,
    },
    getElementById: (id) => (id === 'scene-chat' ? { dataset: { notebookId: '42' } } : null),
};

function createMeta() {
    const classes = new Set();
    return {
        connected: true,
        textContent: '',
        classList: {
            toggle: (name, active) => {
                if (active) classes.add(name);
                else classes.delete(name);
            },
            contains: (name) => classes.has(name),
        },
    };
}

async function runNextTimer() {
    const timer = timers.find((candidate) => !candidate.cleared);
    assert.ok(timer, 'expected a pending timer');
    timer.cleared = true;
    await timer.fn();
}

try {
    resetSourceJobPollingForTests();
    jobResponses.set('job-rerender', [
        { job_id: 'job-rerender', status: 'running', stage: 'parsing', progress_pct: 22, stage_detail: 'parsed_pages=2/10' },
        { job_id: 'job-rerender', status: 'running', stage: 'embedding', progress_pct: 55, stage_detail: 'embedding_batch=1/4' },
        { job_id: 'job-rerender', status: 'succeeded', stage: 'completed', progress_pct: 100 },
    ]);

    const firstMeta = createMeta();
    registerSourceJobPolling('job-rerender', firstMeta, {
        notebookKey: '42',
        version: 0,
        initialJob: { job_id: 'job-rerender', status: 'queued' },
    });
    assert.equal(firstMeta.textContent, 'Queued for indexing');
    assert.equal(firstMeta.classList.contains('uploading'), true);
    assert.equal(getActiveSourceJobPollCount(), 1);

    await runNextTimer();
    assert.equal(firstMeta.textContent, 'Parsing document · 22%');
    assert.equal(firstMeta.classList.contains('uploading'), true);
    assert.equal(timers.find((timer) => !timer.cleared).ms, 1000);

    firstMeta.connected = false;
    const rerenderedMeta = createMeta();
    registerSourceJobPolling('job-rerender', rerenderedMeta, {
        notebookKey: '42',
        version: 0,
        initialJob: { job_id: 'job-rerender', status: 'queued' },
    });
    assert.equal(rerenderedMeta.textContent, 'Parsing document · 22%');
    assert.equal(rerenderedMeta.classList.contains('uploading'), true);

    await runNextTimer();
    assert.equal(rerenderedMeta.textContent, 'Embedding chunks · 55%');
    assert.equal(rerenderedMeta.classList.contains('uploading'), true);

    await runNextTimer();
    assert.equal(rerenderedMeta.textContent, 'Ready');
    assert.equal(rerenderedMeta.classList.contains('uploading'), false);
    assert.equal(getActiveSourceJobPollCount(), 0);

    const jobCalls = calls.filter((call) => call.url === '/api/jobs/job-rerender');
    assert.equal(jobCalls.length, 3);
    assert.ok(timers.every((timer) => timer.cleared));

    timers.length = 0;
    jobResponses.set('job-failed', [
        { job_id: 'job-failed', status: 'failed', stage: 'embedding', progress_pct: 44, error_message: 'Embedding failed' },
    ]);
    const failedMeta = createMeta();
    registerSourceJobPolling('job-failed', failedMeta, {
        notebookKey: '42',
        version: 0,
        initialJob: { job_id: 'job-failed', status: 'running', stage: 'embedding', progress_pct: 44 },
    });
    await runNextTimer();
    assert.equal(failedMeta.textContent, 'Error: Embedding failed');
    assert.equal(failedMeta.classList.contains('uploading'), false);
    assert.equal(getActiveSourceJobPollCount(), 0);

    timers.length = 0;
    jobResponses.set('job-cancelled', [
        { job_id: 'job-cancelled', status: 'cancelled', stage: 'parsing', progress_pct: 12 },
    ]);
    const cancelledMeta = createMeta();
    registerSourceJobPolling('job-cancelled', cancelledMeta, {
        notebookKey: '42',
        version: 0,
        initialJob: { job_id: 'job-cancelled', status: 'running', stage: 'parsing', progress_pct: 12 },
    });
    await runNextTimer();
    assert.equal(cancelledMeta.textContent, 'Cancelled');
    assert.equal(cancelledMeta.classList.contains('uploading'), false);
    assert.equal(getActiveSourceJobPollCount(), 0);
} finally {
    resetSourceJobPollingForTests();
    globalThis.setTimeout = nativeSetTimeout;
    globalThis.clearTimeout = nativeClearTimeout;
}
