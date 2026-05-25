import assert from 'node:assert/strict';

let token = null;

globalThis.localStorage = {
    getItem: (key) => (key === 'accessToken' ? token : null),
};

const { shouldLoadNotebooks } = await import('../src/ui/scenes/DashboardScene.js');

assert.equal(shouldLoadNotebooks(), false);

token = 'test-token';
assert.equal(shouldLoadNotebooks(), true);

class FakeElement {
    constructor() {
        this.children = [];
        this.dataset = {};
        this.style = {};
        this.attributes = new Map();
        this.disabled = false;
        this.className = '';
        this.textContent = '';
        this.innerHTML = '';
        this.removed = false;
    }

    appendChild(child) {
        this.children.push(child);
        return child;
    }

    prepend(child) {
        this.children.unshift(child);
        return child;
    }

    querySelector(selector) {
        if (selector === '.notebook-empty-state') return this.emptyState || null;
        return null;
    }

    remove() {
        this.removed = true;
    }

    setAttribute(name, value) {
        this.attributes.set(name, value);
    }

    removeAttribute(name) {
        this.attributes.delete(name);
    }

    getAttribute(name) {
        return this.attributes.get(name) || null;
    }
}

const myGrid = new FakeElement();
myGrid.emptyState = new FakeElement();
const createBtn = new FakeElement();
const opened = [];
let createCalls = 0;
let resolveCreate;

globalThis.document = {
    createElement() {
        return new FakeElement();
    },
    querySelector(selector) {
        if (selector === '.my-grid') return myGrid;
        return null;
    },
};

const { createDashboardNotebook } = await import('../src/ui/scenes/DashboardScene.js');

const createNotebookFn = async () => {
    createCalls += 1;
    await new Promise((resolve) => { resolveCreate = resolve; });
    return { id: 42, title: 'Untitled notebook', owner_id: 1, is_community: false };
};

const transitionManager = {
    openNotebook(title, id) {
        opened.push({ title, id });
    },
};

const firstCreate = createDashboardNotebook({ createBtn, transitionManager, createNotebookFn });
const duplicateCreate = createDashboardNotebook({ createBtn, transitionManager, createNotebookFn });

assert.equal(createCalls, 1);
assert.equal(createBtn.disabled, true);
assert.equal(createBtn.getAttribute('aria-busy'), 'true');
assert.equal(await duplicateCreate, null);

resolveCreate();
const notebook = await firstCreate;

assert.equal(notebook.id, 42);
assert.equal(createCalls, 1);
assert.equal(opened.length, 1);
assert.deepEqual(opened[0], { title: 'Untitled notebook', id: 42 });
assert.equal(myGrid.children.length, 1);
assert.equal(myGrid.emptyState.removed, true);
assert.equal(createBtn.disabled, false);
assert.equal(createBtn.getAttribute('aria-busy'), null);
