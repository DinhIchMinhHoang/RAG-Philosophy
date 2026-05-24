import assert from 'node:assert/strict';

globalThis.localStorage = {
    getItem: (key) => (key === 'accessToken' ? 'viewer-token' : null),
};

class FakeElement {
    constructor() {
        this._innerHTML = '';
        this.children = [];
        this.className = '';
        this.style = {};
        this.textContent = '';
        this.value = '';
    }

    get innerHTML() {
        return this._innerHTML;
    }

    set innerHTML(value) {
        this._innerHTML = value;
        this.children = value ? [{}] : [];
    }

    appendChild(child) {
        this.children.push(child);
        this._innerHTML += child.innerHTML || '';
    }

    querySelector() {
        return null;
    }

    removeAttribute(name) {
        this[name] = '';
    }
}

const embed = {
    src: '',
    style: {},
    removeAttribute(name) {
        if (name === 'src') this.src = '';
    },
};
const nameEl = { textContent: '' };
const empty = { style: { display: 'block' } };
const content = { style: { display: 'none' } };
const viewer = {
    querySelector(selector) {
        if (selector === '.viewer-empty') return empty;
        if (selector === '.viewer-content') return content;
        if (selector === '#pdfViewer') return embed;
        if (selector === '#viewerFileName') return nameEl;
        if (selector === '.viewer-pdf-wrap') return new FakeElement();
        if (selector === '.viewer-fallback') return null;
        return null;
    },
};

globalThis.document = {
    querySelector(selector) {
        if (selector === '#sourceViewer') return viewer;
        return null;
    },
    getElementById() {
        return null;
    },
    createElement() {
        return new FakeElement();
    },
};

const calls = [];
globalThis.fetch = async (url, options = {}) => {
    calls.push({ url, headers: options.headers || {} });
    return {
        ok: true,
        blob: async () => new Blob(['%PDF-1.4'], { type: 'application/pdf' }),
        json: async () => ({}),
    };
};

const { citationLabel, renderCitationMarkup, resetNotebookWorkspace, showPagePreview } = await import('../src/ui/scenes/ChatScene.js');

assert.equal(citationLabel({ citation_id: 'C2', source: 'paper.pdf', page: 6 }), 'paper.pdf, Trang 6');
assert.equal(citationLabel({ citation_id: 'C2', page: 6 }), 'Trang 6');
const groupedMarkup = renderCitationMarkup('BLEU 34.81 [C2, C4].', [
    { citation_id: 'C2', source: 'paper.pdf', page: 2, document_id: 'doc-1' },
    { citation_id: 'C4', source: 'paper.pdf', page: 6, document_id: 'doc-1' },
]);
assert.match(groupedMarkup, /Trang 2/);
assert.doesNotMatch(groupedMarkup, /Trang 6/);
assert.doesNotMatch(groupedMarkup, /\[C2, C4\]/);

showPagePreview('sample.pdf', 7, 'doc-1', 'application/pdf');

assert.equal(calls.length, 0);
assert.equal(embed.src, '/api/documents/doc-1/file?token=viewer-token#page=7');
assert.equal(nameEl.textContent, 'sample.pdf');
assert.equal(empty.style.display, 'none');
assert.equal(content.style.display, 'flex');

const chatThread = new FakeElement();
chatThread.innerHTML = '<div>old notebook chat</div>';
const sourceList = new FakeElement();
sourceList.innerHTML = '<div>old.pdf</div>';
const sourceEmpty = new FakeElement();
sourceEmpty.style.display = 'none';
const chatPrompt = new FakeElement();
chatPrompt.value = 'old prompt';
chatPrompt.style.height = '120px';
const chatScene = {
    querySelector(selector) {
        if (selector === '.chat-thread') return chatThread;
        if (selector === '.source-list') return sourceList;
        if (selector === '.source-empty') return sourceEmpty;
        if (selector === '#chatPrompt') return chatPrompt;
        return null;
    },
};

resetNotebookWorkspace(chatScene);

assert.match(chatThread.innerHTML, /Hi, I can help you explore your sources/);
assert.equal(sourceList.innerHTML, '');
assert.equal(sourceEmpty.style.display, 'block');
assert.equal(chatPrompt.value, '');
assert.equal(chatPrompt.style.height, '');
assert.equal(embed.src, '');
assert.equal(nameEl.textContent, 'filename.pdf');
assert.equal(empty.style.display, 'flex');
assert.equal(content.style.display, 'none');
