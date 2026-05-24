import assert from 'node:assert/strict';

globalThis.localStorage = {
    getItem: (key) => (key === 'accessToken' ? 'test-token' : null),
};

globalThis.window = {
    marked: { parse: (value) => value },
};
globalThis.marked = globalThis.window.marked;

const { processRichText, resetSourceViewer, showPagePreview, sourceFileUrl } = await import('../src/ui/scenes/ChatScene.js');

const animationFrameQueue = [];
globalThis.requestAnimationFrame = (callback) => {
    animationFrameQueue.push(callback);
    return animationFrameQueue.length;
};
globalThis.cancelAnimationFrame = () => {};

function flushAnimationFrames() {
    while (animationFrameQueue.length) {
        const callback = animationFrameQueue.shift();
        callback();
    }
}

const richTextContainer = {
    innerHTML: '',
    textContent: '',
    querySelectorAll: () => [],
};

processRichText(
    richTextContainer,
    'Giảm gánh nặng cho encoder [C1]. Huấn luyện chung [C5].',
    [
        { citation_id: 'C1', source: 'paper.pdf', page: 4, document_id: 'doc-1' },
        { citation_id: 'C5', source: 'paper.pdf', page: 9, document_id: 'doc-1' },
    ],
);

assert.match(richTextContainer.innerHTML, />Trang 4<\/button>/);
assert.match(richTextContainer.innerHTML, />Trang 9<\/button>/);
assert.doesNotMatch(richTextContainer.innerHTML, /\[C1\]/);
assert.doesNotMatch(richTextContainer.innerHTML, /\[C5\]/);
assert.doesNotMatch(richTextContainer.innerHTML, /find_in_page/);

processRichText(
    richTextContainer,
    'Thuat toan toi uu hoa de hon [C2, C5].',
    [
        { citation_id: 'C2', source: 'paper.pdf', page: 2, document_id: 'doc-1' },
        { citation_id: 'C5', source: 'paper.pdf', page: 8, document_id: 'doc-1' },
    ],
);

assert.match(richTextContainer.innerHTML, />Trang 2<\/button>/);
assert.doesNotMatch(richTextContainer.innerHTML, /\[C2, C5\]/);
assert.doesNotMatch(richTextContainer.innerHTML, />Trang 8<\/button>/);

const empty = { style: {} };
const content = { style: {} };
const embed = {
    style: {},
    removeAttribute(name) {
        if (name === 'src') delete this.src;
    },
};
const nameEl = { textContent: '' };
let fallbackEl = null;
const wrap = {
    appendChild(child) {
        fallbackEl = child;
    },
};
const viewer = {
    querySelector(selector) {
        if (selector === '.viewer-empty') return empty;
        if (selector === '.viewer-content') return content;
        if (selector === '#pdfViewer') return embed;
        if (selector === '#viewerFileName') return nameEl;
        if (selector === '.viewer-pdf-wrap') return wrap;
        if (selector === '.viewer-fallback') return fallbackEl;
        return null;
    },
};

globalThis.document = {
    createElement(tagName) {
        return {
            tagName,
            className: '',
            innerHTML: '',
            remove() {
                fallbackEl = null;
            },
        };
    },
    querySelector(selector) {
        if (selector === '#sourceViewer') return viewer;
        if (selector === '.chat-shell') return { getAttribute: () => 'false' };
        return null;
    },
};

showPagePreview('', 4, 'doc-1');
flushAnimationFrames();

assert.equal(empty.style.display, 'none');
assert.equal(content.style.display, 'flex');
assert.equal(nameEl.textContent, 'doc-1');
assert.equal(embed.src, '/api/documents/doc-1/file?token=test-token#page=4');
assert.doesNotMatch(embed.src, /page-image/);

showPagePreview('paper.pdf', 2, 'doc-1', 'application/pdf');
flushAnimationFrames();
assert.equal(embed.src, '/api/documents/doc-1/file?token=test-token#page=2');

showPagePreview('paper.pdf', 8, 'doc-1', 'application/pdf');
assert.equal(embed.src, 'about:blank');
flushAnimationFrames();
assert.equal(embed.src, '/api/documents/doc-1/file?token=test-token#page=8');

assert.equal(sourceFileUrl('paper.pdf', 8, 'doc-1', 'application/pdf'), '/api/documents/doc-1/file?token=test-token#page=8');
assert.equal(sourceFileUrl('paper.pdf', null, 'doc-1', 'application/pdf'), '/api/documents/doc-1/file?token=test-token');

showPagePreview('slides.docx', 5, 'doc-2', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');

assert.equal(nameEl.textContent, 'slides.docx - Trang 5');
assert.equal(embed.src, undefined);
assert.equal(embed.style.display, 'none');
assert.equal(fallbackEl.className, 'viewer-fallback');
assert.match(fallbackEl.innerHTML, /slides\.docx/);
assert.match(fallbackEl.innerHTML, /Open\/download/);

resetSourceViewer();

assert.equal(empty.style.display, 'flex');
assert.equal(content.style.display, 'none');
assert.equal(nameEl.textContent, 'filename.pdf');
assert.equal(embed.src, undefined);
assert.equal(fallbackEl, null);
