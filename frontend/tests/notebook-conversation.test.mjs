import assert from 'node:assert/strict';

const storage = new Map();
globalThis.localStorage = {
    getItem: (key) => storage.get(key) || null,
    setItem: (key, value) => storage.set(key, value),
    removeItem: (key) => storage.delete(key),
};

const calls = [];
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
    return {
        ok: false,
        status: 404,
        json: async () => ({ detail: `Unexpected URL: ${url}` }),
    };
};

const { getLatestNotebookConversation, createSavedNotebookItem } = await import('../src/api/notebooks.js');
const { conversationCacheKey, readCachedConversation, writeCachedConversation } = await import('../src/ui/scenes/ChatScene.js');

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
