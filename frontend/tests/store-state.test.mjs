import assert from 'node:assert/strict';

const storage = new Map([['currentUser', '[object Object]']]);
globalThis.localStorage = {
    getItem: (key) => storage.get(key) || null,
    setItem: (key, value) => storage.set(key, value),
    removeItem: (key) => storage.delete(key),
};

const { store } = await import('../src/state/store.js');

assert.equal(store.user.email, '');
assert.equal(storage.has('currentUser'), false);

store.setUser({ username: 'tester', email: 'tester@gmail.com', displayName: 'Tester', bio: '', isAdmin: false });
assert.equal(JSON.parse(storage.get('currentUser')).email, 'tester@gmail.com');
