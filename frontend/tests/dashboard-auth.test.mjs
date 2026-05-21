import assert from 'node:assert/strict';

let token = null;

globalThis.localStorage = {
    getItem: (key) => (key === 'accessToken' ? token : null),
};

const { shouldLoadNotebooks } = await import('../src/ui/scenes/DashboardScene.js');

assert.equal(shouldLoadNotebooks(), false);

token = 'test-token';
assert.equal(shouldLoadNotebooks(), true);
