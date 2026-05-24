import { store } from '../../state/store.js';
import {
    BASE_URL,
    chatStream,
    createSavedNotebookItem,
    getJob,
    getLatestNotebookConversation,
    getToken,
    listSources,
    renameSource,
    deleteSource,
    updateNotebook,
    uploadDocument,
    replaceDocument,
} from '../../api/index.js';

const CONVERSATION_CACHE_TTL_MS = 24 * 60 * 60 * 1000;
const CONVERSATION_MESSAGE_LIMIT = 50;

function renderMessageSkeleton(thread) {
    thread.innerHTML = '';
    for (let i = 0; i < 3; i++) {
        const row = document.createElement('div');
        row.className = 'message ai-response skeleton';
        row.style.cssText = 'background:transparent;padding:0 16px 12px 16px;display:flex;flex-direction:column;gap:8px;';
        row.innerHTML = `
            <div class="skeleton skeleton-text" style="width:15%;height:10px;"></div>
            <div class="skeleton skeleton-text" style="width:90%;height:12px;"></div>
            <div class="skeleton skeleton-text" style="width:75%;height:12px;"></div>
        `;
        thread.appendChild(row);
    }
}

function renderWelcomeMessage(chatThread) {
    if (!chatThread) return;
    chatThread.innerHTML = '';
    const welcome = document.createElement('div');
    welcome.className = 'ai-response';
    welcome.innerHTML = `<div class="message-text">Hi, I can help you explore your sources. Add files on the left, then ask a question.</div><div class="message-meta">Lumina</div>`;
    chatThread.appendChild(welcome);
}

function currentNotebookId(chatScene) {
    const raw = chatScene?.dataset?.notebookId;
    const value = raw ? Number(raw) : null;
    return Number.isFinite(value) && value > 0 ? value : null;
}

export function conversationCacheKey(notebookId) {
    return `notebook:${notebookId}:conversation:last`;
}

function normalizeConversationState(state = {}) {
    const conversation = state.conversation || null;
    const messages = Array.isArray(state.messages) ? state.messages : [];
    return {
        conversation,
        messages,
        has_conversation: Boolean(conversation || state.has_conversation),
        limit: Number(state.limit) || CONVERSATION_MESSAGE_LIMIT,
    };
}

export function readCachedConversation(notebookId) {
    if (!notebookId) return null;
    try {
        const raw = localStorage.getItem(conversationCacheKey(notebookId));
        if (!raw) return null;
        const parsed = JSON.parse(raw);
        if (!parsed || Date.now() - Number(parsed.cached_at || 0) > CONVERSATION_CACHE_TTL_MS) {
            localStorage.removeItem(conversationCacheKey(notebookId));
            return null;
        }
        return normalizeConversationState(parsed.state || {});
    } catch (err) {
        console.error('[Conversation cache] Failed to read cache', err);
        return null;
    }
}

export function writeCachedConversation(notebookId, state) {
    if (!notebookId) return;
    try {
        localStorage.setItem(
            conversationCacheKey(notebookId),
            JSON.stringify({ cached_at: Date.now(), state: normalizeConversationState(state) }),
        );
    } catch (err) {
        console.error('[Conversation cache] Failed to write cache', err);
    }
}

function escapeHtml(value) {
    return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

export function citationLabel(citation) {
    const source = citation?.source || '';
    const page = citation?.page ? `Trang ${citation.page}` : '';
    if (source && page) return `${source}, ${page}`;
    if (source) return source;
    if (page) return page;
    return 'Tai lieu';
}

function citationDisplayLabel(citation, fallback) {
    const page = Number(citation?.page);
    if (Number.isFinite(page) && page > 0) return `Trang ${page}`;
    return fallback;
}

function citationButtonHtml(citation, label) {
    const citationId = citation?.citation_id || '';
    const source = citation?.source || '';
    const page = citation?.page || '';
    const documentId = citation?.document_id || '';
    return `<button class="citation-btn" type="button" data-citation-id="${escapeHtml(citationId)}" data-document-id="${escapeHtml(documentId)}" data-file="${escapeHtml(source)}" data-page="${escapeHtml(page)}" title="${escapeHtml(citationLabel(citation))}">${escapeHtml(label)}</button>`;
}

export function renderCitationMarkup(text, citations = []) {
    const citationMap = new Map(citations.map((citation) => [String(citation.citation_id || '').toUpperCase(), citation]));
    let html = text.replace(/\[((?:\s*C\d+\s*(?:,\s*)?)+)\]/gi, (match, citationGroup) => {
        const citationIds = citationGroup.match(/C\d+/gi) || [];
        for (const citationId of citationIds) {
            const normalized = citationId.toUpperCase();
            const citation = citationMap.get(normalized);
            if (citation) return citationButtonHtml(citation, citationDisplayLabel(citation, `[${normalized}]`));
        }
        return match;
    });
    html = html.replace(/\[Trang (\d+)\]/g, (_, p1) => citationButtonHtml({ page: p1 }, `Trang ${p1}`));
    html = html.replace(/- ([^,\n]+),\s*Trang\s*(\d+)/g, (_, file, page) => citationButtonHtml({ source: file.trim(), page }, `${file.trim()} (P. ${page})`));
    return html;
}

function renderCitationChips(container, citations = []) {
    if (!container) return;
    container.innerHTML = '';
    if (!citations.length) {
        container.style.display = 'none';
        return;
    }

    container.style.display = 'flex';
    citations.forEach((citation) => {
        const chip = document.createElement('button');
        chip.className = 'source-chip';
        chip.type = 'button';
        chip.title = citationLabel(citation);
        chip.dataset.documentId = citation.document_id || '';
        chip.dataset.file = citation.source || '';
        chip.dataset.page = citation.page || '';
        chip.innerHTML = `<span class="material-icons">description</span><span>${escapeHtml(citationLabel(citation))}</span>`;
        chip.addEventListener('click', () => showPagePreview(citation.source, citation.page, citation.document_id, citation.mime_type));
        container.appendChild(chip);
    });
}

export function processRichText(container, text, citations = []) {
    const html = renderCitationMarkup(text, citations);
    if (window.marked) container.innerHTML = marked.parse(html);
    else container.textContent = text;

    if (window.renderMathInElement) {
        renderMathInElement(container, {
            delimiters: [
                { left: '$$', right: '$$', display: true },
                { left: '$', right: '$', display: false },
                { left: '\\(', right: '\\)', display: false },
                { left: '\\[', right: '\\]', display: true }
            ], throwOnError: false
        });
    }

    container.querySelectorAll('.citation-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const documentId = btn.getAttribute('data-document-id');
            const file = btn.getAttribute('data-file');
            const page = btn.getAttribute('data-page');
            const firstSource = document.querySelector('#scene-chat .source-name')?.textContent;
            showPagePreview(file || firstSource, page, documentId);
        });
    });
}


const viewerState = { filename: null, page: null, documentId: null, mimeType: null };
let activeStreamController = null;
let activeConversationId = null;
const activeConversationByNotebook = new Map();
const conversationStateByNotebook = new Map();
const manualNewChatByNotebook = new Set();
let setCollapsedFn = null;
let notebookLoadVersion = 0;
let viewerSrcVersion = 0;

function inferMimeType(filename, mimeType) {
    if (mimeType) return String(mimeType).toLowerCase();
    const lower = String(filename || '').toLowerCase();
    if (lower.endsWith('.pdf')) return 'application/pdf';
    if (lower.endsWith('.txt')) return 'text/plain';
    if (lower.endsWith('.md') || lower.endsWith('.markdown')) return 'text/markdown';
    if (/\.(png|jpg|jpeg|gif|webp|bmp|svg)$/.test(lower)) return 'image/*';
    return '';
}

function isBrowserNativeMime(mimeType) {
    if (!mimeType) return true;
    return mimeType === 'application/pdf'
        || mimeType.startsWith('image/')
        || mimeType === 'text/plain'
        || mimeType === 'text/markdown';
}

function supportsPdfPageFragment(filename, mimeType, page, documentId) {
    const pageNumber = Number(page);
    if (!Number.isFinite(pageNumber) || pageNumber <= 0) return false;
    const inferred = inferMimeType(filename, mimeType);
    return inferred === 'application/pdf' || (!inferred && Boolean(documentId));
}

function viewerTitle(filename, documentId, page, showPageInHeader) {
    const base = filename || documentId || 'Source';
    const pageNumber = Number(page);
    if (showPageInHeader && Number.isFinite(pageNumber) && pageNumber > 0) return `${base} - Trang ${pageNumber}`;
    return base;
}

export function sourceFileUrl(filename, page = null, documentId = null, mimeType = null) {
    if (!filename && !documentId) return '';
    const fileKey = documentId || filename;
    const filePath = documentId
        ? `/documents/${encodeURIComponent(fileKey)}/file`
        : `/documents/file/${encodeURIComponent(fileKey)}`;
    const token = getToken();
    const tokenParam = token ? `?token=${encodeURIComponent(token)}` : '';
    const pageNumber = Number(page);
    const fragment = supportsPdfPageFragment(filename, mimeType, page, documentId)
        ? `#page=${pageNumber}`
        : '';
    return `${BASE_URL}${filePath}${tokenParam}${fragment}`;
}

function clearViewerFallback(viewer, embed) {
    const fallback = viewer?.querySelector('.viewer-fallback');
    fallback?.remove();
    if (embed) {
        if (!embed.style) embed.style = {};
        embed.style.display = 'block';
    }
}

function showUnsupportedViewer(viewer, embed, fileUrl, filename, mimeType) {
    const wrap = viewer?.querySelector('.viewer-pdf-wrap');
    if (!wrap) return;
    if (embed) {
        embed.removeAttribute('src');
        if (!embed.style) embed.style = {};
        embed.style.display = 'none';
    }

    const fallback = document.createElement('div');
    fallback.className = 'viewer-fallback';
    fallback.innerHTML = `
        <span class="material-icons">draft</span>
        <div class="viewer-fallback-text">
            <strong>${escapeHtml(filename || 'Source file')}</strong>
            <span>${escapeHtml(mimeType || 'Unsupported file type')}</span>
        </div>
        <a class="auth-button viewer-open-link" href="${escapeHtml(fileUrl)}" target="_blank" rel="noopener">Open/download</a>
    `;
    wrap.appendChild(fallback);
}

function withoutFragment(url) {
    return String(url || '').split('#')[0];
}

function scheduleViewerSrc(embed, fileUrl, version) {
    const schedule = globalThis.requestAnimationFrame || ((callback) => globalThis.setTimeout(callback, 0));
    schedule(() => {
        if (version !== viewerSrcVersion) return;
        embed.src = fileUrl;
    });
}

function setViewerSrc(embed, fileUrl) {
    const currentSrc = embed.getAttribute?.('src') || embed.src || '';
    const nextVersion = ++viewerSrcVersion;
    if (currentSrc && currentSrc !== fileUrl && withoutFragment(currentSrc) === withoutFragment(fileUrl)) {
        embed.src = 'about:blank';
        scheduleViewerSrc(embed, fileUrl, nextVersion);
        return;
    }
    embed.src = fileUrl;
}

function getActiveNotebookKey() {
    return document.getElementById('scene-chat')?.dataset.notebookId || '';
}

function isCurrentNotebookLoad(version, notebookId) {
    return version === notebookLoadVersion && getActiveNotebookKey() === String(notebookId || '');
}

export function resetSourceViewer() {
    viewerSrcVersion += 1;
    viewerState.filename = null;
    viewerState.page = null;
    viewerState.documentId = null;
    viewerState.mimeType = null;

    const viewer = document.querySelector('#sourceViewer');
    const empty = viewer?.querySelector('.viewer-empty');
    const content = viewer?.querySelector('.viewer-content');
    const embed = viewer?.querySelector('#pdfViewer');
    const nameEl = viewer?.querySelector('#viewerFileName');

    if (empty) empty.style.display = 'flex';
    if (content) content.style.display = 'none';
    clearViewerFallback(viewer, embed);
    if (embed) embed.removeAttribute('src');
    if (nameEl) nameEl.textContent = 'filename.pdf';
}

function resetNotebookWorkspaceState({ chatThread, sourceList, sourceEmpty, chatPrompt, sourceInput, showSkeleton = false }) {
    hideThinkingIndicator();
    activeConversationId = null;

    if (sourceList) sourceList.innerHTML = '';
    if (sourceEmpty && sourceList) updateSourceEmpty(sourceEmpty, sourceList);
    if (chatPrompt) {
        chatPrompt.value = '';
        chatPrompt.style.height = '';
    }
    if (sourceInput) sourceInput.value = '';
    if (chatThread) {
        chatThread.innerHTML = '';
        if (showSkeleton) renderMessageSkeleton(chatThread);
    }
    resetSourceViewer();
}

export function showPagePreview(filename, page = null, documentId = null, mimeType = null) {
    if (!filename && !documentId) return;
    viewerState.filename = filename;
    viewerState.page = page;
    viewerState.documentId = documentId || null;
    viewerState.mimeType = mimeType || null;

    const viewer = document.querySelector('#sourceViewer');
    const empty = viewer?.querySelector('.viewer-empty');
    const content = viewer?.querySelector('.viewer-content');
    const embed = viewer?.querySelector('#pdfViewer');
    const nameEl = viewer?.querySelector('#viewerFileName');
    const inferredMimeType = inferMimeType(filename, mimeType);
    const fileUrl = sourceFileUrl(filename, page, documentId, mimeType);
    const canUsePageFragment = supportsPdfPageFragment(filename, mimeType, page, documentId);

    if (empty) empty.style.display = 'none';
    if (content) content.style.display = 'flex';
    if (nameEl) nameEl.textContent = viewerTitle(filename, documentId, page, !canUsePageFragment);
    clearViewerFallback(viewer, embed);
    if (embed) {
        if (isBrowserNativeMime(inferredMimeType)) {
            setViewerSrc(embed, fileUrl);
        } else {
            showUnsupportedViewer(viewer, embed, fileUrl, filename || documentId, inferredMimeType);
        }
    }

    if (document.querySelector('.chat-shell')?.getAttribute('data-right-collapsed') === 'true') {
        if (setCollapsedFn) setCollapsedFn('right', false);
    }
}

function addMessage(chatThread, role, text, citations = [], messageId = '') {
    if (!chatThread) return null;
    const msg = document.createElement('div');
    msg.className = role === 'ai' ? 'ai-response' : `message ${role}`;
    msg.dataset.role = role;
    msg.dataset.messageId = messageId || '';
    msg.innerHTML = `<div class="message-text"></div><div class="citation-strip"></div><div class="message-actions"><button class="message-action" data-action="pin-message" title="Pin message"><span class="material-icons">push_pin</span></button><button class="message-action" data-action="save-message" title="Save to Notes"><span class="material-icons">bookmark_add</span></button></div><div class="message-meta"></div>`;
    const textEl = msg.querySelector('.message-text');
    const citationsEl = msg.querySelector('.citation-strip');
    const metaEl = msg.querySelector('.message-meta');
    if (textEl) { if (role === 'ai') processRichText(textEl, text, citations); else textEl.textContent = text; }
    renderCitationChips(citationsEl, []);
    if (metaEl) metaEl.textContent = role === 'user' ? 'You' : 'Lumina';
    chatThread.appendChild(msg);
    chatThread.scrollTop = chatThread.scrollHeight;
    return msg;
}

function messageStateFromPayload(message) {
    return {
        id: message.id || message.message_id || '',
        role: message.role === 'assistant' ? 'ai' : message.role,
        content: message.content || message.answer || '',
        sources_used: Array.isArray(message.sources_used) ? message.sources_used : [],
        rewritten_query: message.rewritten_query || null,
        created_at: message.created_at || null,
    };
}

function renderConversationState(chatThread, state) {
    if (!chatThread) return;
    const normalized = normalizeConversationState(state);
    if (!normalized.messages.length) {
        renderWelcomeMessage(chatThread);
        return;
    }
    chatThread.innerHTML = '';
    normalized.messages.forEach((message) => {
        const item = messageStateFromPayload(message);
        addMessage(chatThread, item.role, item.content, item.sources_used, item.id);
    });
}

function applyConversationState(chatThread, notebookId, state) {
    const normalized = normalizeConversationState(state);
    conversationStateByNotebook.set(notebookId, normalized);
    activeConversationByNotebook.set(notebookId, normalized.conversation?.id || null);
    activeConversationId = normalized.conversation?.id || null;
    renderConversationState(chatThread, normalized);
}

function emptyConversationState() {
    return { conversation: null, messages: [], has_conversation: false, limit: CONVERSATION_MESSAGE_LIMIT };
}

function cacheConversationState(notebookId) {
    const state = conversationStateByNotebook.get(notebookId);
    if (state) writeCachedConversation(notebookId, state);
}

function showThinkingIndicator(chatThread) {
    const ind = document.createElement('div');
    ind.className = 'thinking-indicator';
    ind.id = 'thinkingIndicator';
    ind.innerHTML = `<span>Lumina is thinking...</span><div class="thinking-dots"><div class="thinking-dot"></div><div class="thinking-dot"></div><div class="thinking-dot"></div></div>`;
    chatThread.appendChild(ind);
    chatThread.scrollTop = chatThread.scrollHeight;
}

function hideThinkingIndicator() {
    document.getElementById('thinkingIndicator')?.remove();
}

function updateSourceEmpty(sourceEmpty, sourceList) {
    if (!sourceEmpty || !sourceList) return;
    sourceEmpty.style.display = sourceList.children.length ? 'none' : 'block';
}

export function resetNotebookWorkspace(chatScene) {
    if (!chatScene) return;

    renderWelcomeMessage(chatScene.querySelector('.chat-thread'));

    const sourceList = chatScene.querySelector('.source-list');
    const sourceEmpty = chatScene.querySelector('.source-empty');
    if (sourceList) sourceList.innerHTML = '';
    updateSourceEmpty(sourceEmpty, sourceList);

    const chatPrompt = chatScene.querySelector('#chatPrompt');
    if (chatPrompt) {
        chatPrompt.value = '';
        chatPrompt.style.height = '';
    }

    document.getElementById('thinkingIndicator')?.remove();
    resetSourceViewer();
}

const ingestStageLabels = {
    fetching_object: 'Fetching document',
    parsing: 'Parsing document',
    chunking: 'Chunking text',
    embedding: 'Embedding chunks',
    indexing_vector: 'Indexing vectors',
    persisting_metadata: 'Saving metadata',
    loading_sql: 'Loading spreadsheet',
};

function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

function setSourceMeta(metaEl, text, active = false) {
    if (!metaEl) return;
    metaEl.textContent = text;
    metaEl.classList.toggle('uploading', active);
}

function showReplaceConfirm(filename) {
    return new Promise((resolve) => {
        const existing = document.querySelector('.confirm-modal');
        if (existing) existing.remove();

        const overlay = document.createElement('div');
        overlay.className = 'confirm-modal open';
        overlay.innerHTML = `
            <div class="confirm-modal-backdrop"></div>
            <div class="confirm-modal-body">
                <div class="confirm-modal-title">File already exists</div>
                <div class="confirm-modal-message">"${escapeHtml(filename)}" already exists in this notebook. Replace the existing file?</div>
                <div class="confirm-modal-actions">
                    <button class="auth-button is-ghost" data-action="cancel">No</button>
                    <button class="auth-button" data-action="confirm">Yes</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        const close = (result) => {
            overlay.remove();
            resolve(result);
        };

        overlay.querySelector('[data-action="cancel"]').addEventListener('click', () => close(false));
        overlay.querySelector('[data-action="confirm"]').addEventListener('click', () => close(true));
        overlay.querySelector('.confirm-modal-backdrop').addEventListener('click', () => close(false));
    });
}

function formatJobProgress(job) {
    if (job.status === 'queued') return 'Queued for indexing';

    const label = ingestStageLabels[job.stage] || 'Indexing document';
    const pct = Number(job.progress_pct);
    if (Number.isFinite(pct)) return `${label} ${pct}%`;
    return label;
}

function formatDocumentStatus(doc) {
    const job = doc?.latest_job;
    if (!job) return 'Uploaded';
    if (job.status === 'succeeded') return 'Ready';
    if (job.status === 'failed') return `Error: ${job.error_message || 'Ingest failed'}`;
    return formatJobProgress(job);
}

async function pollUploadJob(jobId, metaEl) {
    let delayMs = 1000;

    for (let attempt = 0; attempt < 90; attempt += 1) {
        const job = await getJob(jobId);

        if (job.status === 'succeeded') {
            setSourceMeta(metaEl, 'Ready', false);
            return job;
        }

        if (job.status === 'failed') {
            setSourceMeta(metaEl, `Error: ${job.error_message || 'Ingest failed'}`, false);
            return job;
        }

        setSourceMeta(metaEl, formatJobProgress(job), true);
        await sleep(delayMs);
        delayMs = 2000;
    }

    setSourceMeta(metaEl, 'Still indexing', false);
    return null;
}

export function initChatScene(transitionManager) {
    const chatScene = document.getElementById('scene-chat');
    if (!chatScene) return;

    const chatThread = chatScene.querySelector('.chat-thread');
    const sourceList = chatScene.querySelector('.source-list');
    const sourceEmpty = chatScene.querySelector('.source-empty');

    const chatShell = chatScene.querySelector('.chat-shell');
    const chatLayout = chatScene.querySelector('.chat-layout');
    const leftPanel = chatScene.querySelector('.panel-left');
    const rightPanel = chatScene.querySelector('.panel-right');

    if (chatShell && chatLayout) {
        let leftWidth = parseInt(getComputedStyle(chatShell).getPropertyValue('--left-user-width'), 10) || 320;
        let rightWidth = parseInt(getComputedStyle(chatShell).getPropertyValue('--right-user-width'), 10) || 280;
        const resizerWidth = parseInt(getComputedStyle(chatShell).getPropertyValue('--resizer-width'), 10) || 10;
        const minSide = 200, minCenter = 320;

        const setLeftWidth = (w) => { leftWidth = w; chatShell.style.setProperty('--left-user-width', `${w}px`); };
        const setRightWidth = (w) => { rightWidth = w; chatShell.style.setProperty('--right-user-width', `${w}px`); };

        setCollapsedFn = (side, collapsed) => {
            if (side === 'left') {
                if (collapsed) { leftWidth = leftPanel?.getBoundingClientRect().width || leftWidth; chatShell.setAttribute('data-left-collapsed', 'true'); leftPanel?.classList.add('is-collapsed'); }
                else { chatShell.removeAttribute('data-left-collapsed'); leftPanel?.classList.remove('is-collapsed'); setLeftWidth(leftWidth); }
            } else if (side === 'right') {
                if (collapsed) { rightWidth = rightPanel?.getBoundingClientRect().width || rightWidth; chatShell.setAttribute('data-right-collapsed', 'true'); rightPanel?.classList.add('is-collapsed'); }
                else { chatShell.removeAttribute('data-right-collapsed'); rightPanel?.classList.remove('is-collapsed'); setRightWidth(rightWidth); }
            }
        };

        chatScene.querySelector('[data-collapse="sources"]')?.addEventListener('click', () => setCollapsedFn('left', true));
        chatScene.querySelector('[data-collapse="tools"]')?.addEventListener('click', () => setCollapsedFn('right', true));
        chatScene.querySelector('[data-expand="sources"]')?.addEventListener('click', () => setCollapsedFn('left', false));
        chatScene.querySelector('[data-expand="tools"]')?.addEventListener('click', () => setCollapsedFn('right', false));

        chatScene.querySelectorAll('.chat-resizer').forEach(resizer => {
            resizer.addEventListener('pointerdown', (ev) => {
                ev.preventDefault();
                const side = resizer.getAttribute('data-resize');
                if (!side) return;
                if (side === 'left' && chatShell.getAttribute('data-left-collapsed') === 'true') setCollapsedFn('left', false);
                if (side === 'right' && chatShell.getAttribute('data-right-collapsed') === 'true') setCollapsedFn('right', false);

                const layoutRect = chatLayout.getBoundingClientRect();
                const startX = ev.clientX;
                const startLeft = leftPanel?.getBoundingClientRect().width || leftWidth;
                const startRight = rightPanel?.getBoundingClientRect().width || rightWidth;
                const totalW = layoutRect.width;
                const resizerTotal = resizerWidth * 2;

                const onMove = (mEv) => {
                    const delta = mEv.clientX - startX;
                    if (side === 'left') { const maxL = totalW - startRight - minCenter - resizerTotal; setLeftWidth(Math.min(Math.max(startLeft + delta, minSide), maxL)); }
                    else { const maxR = totalW - startLeft - minCenter - resizerTotal; setRightWidth(Math.min(Math.max(startRight - delta, minSide), maxR)); }
                };
                const onUp = () => { document.body.classList.remove('is-resizing'); window.removeEventListener('pointermove', onMove); window.removeEventListener('pointerup', onUp); };
                document.body.classList.add('is-resizing');
                window.addEventListener('pointermove', onMove);
                window.addEventListener('pointerup', onUp, { once: true });
            });

            resizer.addEventListener('dblclick', () => {
                if (resizer.getAttribute('data-resize') === 'left') setLeftWidth(320);
                else setRightWidth(280);
            });
        });

        const clampPanels = () => {
            const lr = chatLayout.getBoundingClientRect();
            const tw = lr.width; const rt = resizerWidth * 2;
            const ml = tw - rightWidth - minCenter - rt;
            const mr = tw - leftWidth - minCenter - rt;
            if (leftWidth > ml) setLeftWidth(Math.max(minSide, ml));
            if (rightWidth > mr) setRightWidth(Math.max(minSide, mr));
        };
        window.addEventListener('resize', clampPanels);
    }

    const sourceInput = chatScene.querySelector('#sourceFileInput');
    const sourceDrop = chatScene.querySelector('.source-drop');
    const sourceAddButtons = chatScene.querySelectorAll('.source-add-button');
    const sourceNoteButton = chatScene.querySelector('.source-note-button');
    let sourceLoadToken = 0;
    let conversationLoadToken = 0;

    const shareButton = chatScene.querySelector('.chat-top-actions .panel-icon-button[title="Share"]');
    if (shareButton) {
        shareButton.addEventListener('click', async () => {
            const notebookId = currentNotebookId(chatScene);
            if (!notebookId) return;
            const title = document.querySelector('#scene-chat .chat-title')?.textContent?.trim() || '';
            if (!title || title.toLowerCase() === 'untitled notebook') {
                alert('Please name the notebook before sharing.');
                return;
            }
            const isShared = shareButton.classList.contains('active');
            try {
                await updateNotebook(notebookId, { is_community: !isShared });
                shareButton.classList.toggle('active', !isShared);
                document.dispatchEvent(new CustomEvent('notebooks:refresh'));
            } catch (err) {
                alert(err.message || 'Failed to update share status. You can only share your own notebooks.');
            }
        });
    }

    const closeAllSourceMenus = (exceptMenu = null) => {
        document.querySelectorAll('#scene-chat .source-menu').forEach((menu) => {
            if (menu !== exceptMenu) menu.style.display = 'none';
        });
    };

    document.addEventListener('click', (ev) => {
        if (ev.target.closest('.source-menu') || ev.target.closest('.source-menu-btn')) return;
        closeAllSourceMenus();
    });

    const renderPersistedSources = (documents = []) => {
        if (!sourceList) return;
        sourceList.innerHTML = '';
        documents.forEach((doc) => {
            const item = document.createElement('div');
            item.className = 'source-item';
            item.style.cursor = 'pointer';
            item.dataset.documentId = doc.document_id || '';

            // build menu button and dropdown
            const menuBtnHtml = `<button class="source-menu-btn" title="More" type="button"><span class="material-icons">more_vert</span></button>`;
            const menuHtml = `<div class="source-menu"><button class="source-menu-item" data-action="rename"><span class=\"material-icons\">edit</span> Rename</button><button class="source-menu-item" data-action="delete"><span class=\"material-icons\">delete</span> Delete</button></div>`;

            item.innerHTML = `<div class="source-icon"><span class="material-icons">picture_as_pdf</span></div><div class="source-meta"><div class="source-name">${escapeHtml(doc.filename || 'Untitled document')}</div><div class="source-type">${escapeHtml(formatDocumentStatus(doc))}</div></div>${menuBtnHtml}${menuHtml}`;

            // click on item opens preview unless clicking within menu
            item.addEventListener('click', (ev) => {
                if (ev.target.closest('.source-menu') || ev.target.closest('.source-menu-btn') || ev.target.closest('.source-rename-input') || ev.target.closest('.source-rename-actions')) return;
                closeAllSourceMenus();
                showPagePreview(doc.filename, null, doc.document_id || null, doc.mime_type);
            });

            // wire menu toggle
            const menuBtn = item.querySelector('.source-menu-btn');
            const menu = item.querySelector('.source-menu');
            if (menuBtn && menu) {
                menuBtn.addEventListener('click', (ev) => {
                    ev.stopPropagation();
                    closeAllSourceMenus(menu);
                    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
                });
            }

            // handle menu actions
            const handleRename = async () => {
                // inline edit
                const nameEl = item.querySelector('.source-name');
                const original = nameEl.textContent || '';
                // extract base name without extension
                const base = original.replace(/\.[^/.]+$/, '') || original;
                nameEl.innerHTML = `<input class="source-rename-input" type="text" value="${escapeHtml(base)}" />`;
                const input = nameEl.querySelector('.source-rename-input');
                menu.style.display = 'none';
                input.focus();

                const notebookId = currentNotebookId(chatScene);
                const fileId = doc.document_id || '';

                const cleanup = () => { nameEl.textContent = original; };
                let submitted = false;

                const submitRename = async () => {
                    const newVal = input.value.trim();
                    if (!newVal) { alert('Name cannot be empty'); return; }
                    if (newVal === base) { cleanup(); return; }
                    // simple client-side sanitization
                    if (/[\\/\.\.]/.test(newVal)) { alert('Invalid characters in name'); return; }
                    input.disabled = true;
                    try {
                        await renameSource({ notebookId, fileId, newName: newVal });
                        // update visible filename (backend preserves extension)
                        // append original extension if present
                        const extMatch = (original.match(/(\.[^/.]+)$/) || [])[0] || '';
                        nameEl.textContent = `${newVal}${extMatch}`;
                        submitted = true;
                    } catch (err) {
                        console.error('[Rename] failed', err);
                        alert(err.message || 'Rename failed');
                        cleanup();
                    }
                };

                input.addEventListener('keydown', (ev) => {
                    if (ev.key === 'Enter') {
                        ev.preventDefault();
                        submitRename();
                    }
                    if (ev.key === 'Escape') {
                        ev.preventDefault();
                        cleanup();
                    }
                });

                input.addEventListener('blur', () => {
                    if (!submitted) cleanup();
                });
            };

            const handleDelete = async () => {
                menu.style.display = 'none';
                if (!confirm('Delete this source?')) return;
                const notebookId = currentNotebookId(chatScene);
                const fileId = doc.document_id || '';
                try {
                    await deleteSource({ notebookId, fileId });
                    item.remove();
                    updateSourceEmpty(sourceEmpty, sourceList);
                } catch (err) {
                    console.error('[Delete] failed', err);
                    alert(err.message || 'Delete failed');
                }
            };

            // attach menu item handlers
            item.querySelectorAll('.source-menu-item').forEach((btn) => {
                const action = btn.getAttribute('data-action');
                btn.addEventListener('click', (ev) => {
                    ev.stopPropagation();
                    if (action === 'rename') handleRename();
                    else if (action === 'delete') handleDelete();
                });
            });

            sourceList.appendChild(item);
        });
        updateSourceEmpty(sourceEmpty, sourceList);
    };

    const loadNotebookSources = async () => {
        const token = ++sourceLoadToken;
        const notebookId = currentNotebookId(chatScene);
        if (!notebookId) {
            renderPersistedSources([]);
            return;
        }
        renderPersistedSources([]);
        try {
            const result = await listSources({ notebookId });
            if (token !== sourceLoadToken) return;
            renderPersistedSources(result.documents || []);
        } catch (err) {
            if (token !== sourceLoadToken) return;
            console.error('[Sources] Failed to load notebook sources', err);
            renderPersistedSources([]);
        }
    };

    const loadNotebookConversation = async () => {
        const token = ++conversationLoadToken;
        const notebookId = currentNotebookId(chatScene);
        if (!notebookId) {
            activeConversationId = null;
            renderWelcomeMessage(chatThread);
            return;
        }
        if (manualNewChatByNotebook.has(notebookId)) {
            applyConversationState(chatThread, notebookId, emptyConversationState());
            return;
        }

        const cached = readCachedConversation(notebookId);
        if (cached) {
            applyConversationState(chatThread, notebookId, cached);
        } else {
            applyConversationState(chatThread, notebookId, emptyConversationState());
        }

        try {
            const result = await getLatestNotebookConversation(notebookId, { limit: CONVERSATION_MESSAGE_LIMIT });
            if (token !== conversationLoadToken || notebookId !== currentNotebookId(chatScene)) return;
            const normalized = normalizeConversationState(result);
            applyConversationState(chatThread, notebookId, normalized);
            writeCachedConversation(notebookId, normalized);
        } catch (err) {
            if (token !== conversationLoadToken) return;
            console.error('[Conversation] Failed to load notebook conversation', err);
            if (!cached) applyConversationState(chatThread, notebookId, emptyConversationState());
        }
    };

    document.addEventListener('chat:notebookLeft', () => {
        notebookLoadVersion += 1;
        sourceLoadToken += 1;
        conversationLoadToken += 1;
        if (activeStreamController) {
            activeStreamController.abort();
            activeStreamController = null;
        }
        activeConversationId = null;
        delete chatScene.dataset.notebookId;
        resetNotebookWorkspace(chatScene);
    });

    document.addEventListener('chat:notebookChanged', () => {
        notebookLoadVersion += 1;
        if (shareButton) {
            shareButton.classList.remove('active');
            shareButton.style.pointerEvents = '';
            shareButton.style.opacity = '';
            shareButton.title = 'Share';

            const isShared = chatScene.dataset.isCommunity === 'true';
            if (isShared) shareButton.classList.add('active');

            const ownerId = chatScene.dataset.notebookOwnerId;
            if (ownerId && String(store.user?.id) !== ownerId) {
                shareButton.style.pointerEvents = 'none';
                shareButton.style.opacity = '0.35';
                shareButton.title = 'Only the owner can share this notebook';
            }
        }
        const settingsBtn = chatScene.querySelector('.panel-icon-button[title="Notebook settings"]');
        if (settingsBtn) {
            const ownerId = chatScene.dataset.notebookOwnerId;
            if (ownerId && String(store.user?.id) !== ownerId) {
                settingsBtn.style.display = 'none';
            } else {
                settingsBtn.style.display = '';
            }
        }
        if (activeStreamController) {
            activeStreamController.abort();
            activeStreamController = null;
        }
        activeConversationId = null;
        resetSourceViewer();
        loadNotebookSources();
        loadNotebookConversation();
    });

    const SUPPORTED_EXTENSIONS = ['.pdf', '.xlsx', '.xls', '.csv', '.docx', '.html', '.htm', '.md'];

    function getFileIcon(filename) {
        const ext = filename.toLowerCase().split('.').pop();
        const icons = { pdf: 'picture_as_pdf', xlsx: 'table_chart', xls: 'table_chart', csv: 'grid_on', docx: 'description', html: 'language', htm: 'language', md: 'article' };
        return icons[ext] || 'description';
    }

    function isSupported(filename) {
        const ext = '.' + filename.toLowerCase().split('.').pop();
        return SUPPORTED_EXTENSIONS.includes(ext);
    }

    const handleFiles = async (files) => {
        const list = Array.from(files || []);
        const uploadNotebookKey = getActiveNotebookKey();
        const uploadNotebookId = uploadNotebookKey ? Number(uploadNotebookKey) : null;
        for (const file of list) {
            if (getActiveNotebookKey() !== uploadNotebookKey) return;
            const isPDF = file.name.toLowerCase().endsWith('.pdf');
            const canUpload = isSupported(file.name);
            const icon = getFileIcon(file.name);
            const meta = canUpload ? 'Uploading…' : (file.type || 'file');

            const item = document.createElement('div');
            item.className = 'source-item';
            item.style.cursor = 'pointer';
            item.innerHTML = `<div class="source-icon"><span class="material-icons">${icon}</span></div><div class="source-meta"><div class="source-name">${file.name}</div><div class="source-type uploading">${meta}</div></div>`;
            item.addEventListener('click', () => { if (isPDF) showPagePreview(file.name, null, item.dataset.documentId || null, file.type || 'application/pdf'); });
            sourceList.appendChild(item);
            updateSourceEmpty(sourceEmpty, sourceList);

            if (canUpload) {
                const metaEl = item.querySelector('.source-type');
                try {
                    const result = await uploadDocument(file, { notebookId: uploadNotebookId });
                    if (getActiveNotebookKey() !== uploadNotebookKey) return;
                    if (result.document_id) item.dataset.documentId = result.document_id;
                    if (result.pages !== undefined || result.chunks !== undefined) {
                        setSourceMeta(metaEl, `${result.pages ?? 0} pages, ${result.chunks ?? 0} chunks`, false);
                    } else if (result.job_id) {
                        setSourceMeta(metaEl, 'Queued for indexing', true);
                        pollUploadJob(result.job_id, metaEl).catch((err) => {
                            if (getActiveNotebookKey() !== uploadNotebookKey) return;
                            console.error('[Upload job]', err);
                            setSourceMeta(metaEl, `Error: ${err.message}`, false);
                        });
                    } else {
                        setSourceMeta(metaEl, result.status || 'Upload accepted', false);
                    }
                } catch (err) {
                    if (getActiveNotebookKey() !== uploadNotebookKey) return;

                    if (err.isDuplicate) {
                        const confirmed = await showReplaceConfirm(err.filename || file.name);
                        if (confirmed) {
                            setSourceMeta(metaEl, 'Replacing…', true);
                            try {
                                const result = await replaceDocument(err.documentId, file);
                                if (getActiveNotebookKey() !== uploadNotebookKey) return;
                                if (result.document_id) item.dataset.documentId = result.document_id;
                                if (result.pages !== undefined || result.chunks !== undefined) {
                                    setSourceMeta(metaEl, `${result.pages ?? 0} pages, ${result.chunks ?? 0} chunks`, false);
                                } else if (result.job_id) {
                                    setSourceMeta(metaEl, 'Queued for indexing', true);
                                    pollUploadJob(result.job_id, metaEl).catch((err2) => {
                                        if (getActiveNotebookKey() !== uploadNotebookKey) return;
                                        console.error('[Replace job]', err2);
                                        setSourceMeta(metaEl, `Error: ${err2.message}`, false);
                                    });
                                } else {
                                    setSourceMeta(metaEl, result.status || 'Replace accepted', false);
                                }
                            } catch (replaceErr) {
                                if (getActiveNotebookKey() !== uploadNotebookKey) return;
                                console.error('[Replace]', replaceErr);
                                setSourceMeta(metaEl, `Error: ${replaceErr.message}`, false);
                            }
                        } else {
                            item.remove();
                            updateSourceEmpty(sourceEmpty, sourceList);
                        }
                        continue;
                    }

                    console.error('[Upload]', err);
                    setSourceMeta(metaEl, `Error: ${err.message}`, false);
                }
            }
        }
    };

    sourceAddButtons.forEach(btn => btn.addEventListener('click', () => sourceInput?.click()));
    sourceInput?.addEventListener('change', (ev) => { handleFiles(ev.target.files); sourceInput.value = ''; });
    if (sourceNoteButton) sourceNoteButton.addEventListener('click', () => {
        const note = prompt('New note');
        if (!note) return;
        const item = document.createElement('div');
        item.className = 'source-item';
        item.innerHTML = `<div class="source-icon"><span class="material-icons">edit_note</span></div><div class="source-meta"><div class="source-name">${note}</div><div class="source-type">Note</div></div>`;
        sourceList.appendChild(item);
        updateSourceEmpty(sourceEmpty, sourceList);
    });

    if (sourceDrop) {
        sourceDrop.addEventListener('dragover', (ev) => { ev.preventDefault(); sourceDrop.classList.add('is-dragover'); });
        sourceDrop.addEventListener('dragleave', () => sourceDrop.classList.remove('is-dragover'));
        sourceDrop.addEventListener('drop', (ev) => { ev.preventDefault(); sourceDrop.classList.remove('is-dragover'); if (ev.dataTransfer) handleFiles(ev.dataTransfer.files); });
    }
    updateSourceEmpty(sourceEmpty, sourceList);

    const chatForm = chatScene.querySelector('.chat-input');
    const chatPrompt = chatScene.querySelector('#chatPrompt');
    const clearChatBtn = chatScene.querySelector('[data-action="clear-chat"]');
    const newChatBtn = chatScene.querySelector('[data-action="new-chat"]');
    const saveConversationBtn = chatScene.querySelector('[data-action="save-conversation"]');
    const summarizeBtn = chatScene.querySelector('[data-action="summarize-to-notebook"]');

    const visibleConversationText = () => Array.from(chatThread?.querySelectorAll('.message, .ai-response') || [])
        .map((node) => {
            const role = node.dataset.role === 'user' ? 'User' : 'Lumina';
            const content = node.querySelector('.message-text')?.textContent?.trim() || '';
            return content ? `${role}: ${content}` : '';
        })
        .filter(Boolean)
        .join('\n\n');

    const saveNotebookItem = async (payload) => {
        const notebookId = currentNotebookId(chatScene);
        if (!notebookId) return;
        try {
            await createSavedNotebookItem(notebookId, payload);
        } catch (err) {
            console.error('[Notes] Failed to save notebook item', err);
        }
    };

    if (chatForm && chatPrompt) {
        chatForm.addEventListener('submit', (ev) => {
            ev.preventDefault();
            const text = chatPrompt.value.trim();
            if (!text) return;

            if (activeStreamController) { activeStreamController.abort(); activeStreamController = null; }

            addMessage(chatThread, 'user', text);
            const userMessageState = { id: '', role: 'user', content: text, sources_used: [] };
            chatPrompt.value = '';
            chatPrompt.style.height = '';

            const aiMsg = document.createElement('div');
            aiMsg.className = 'ai-response streaming';
            aiMsg.style.display = 'none';
            aiMsg.innerHTML = `<div class="message-text"></div><div class="citation-strip"></div><div class="message-meta">Lumina</div>`;
            chatThread.appendChild(aiMsg);
            const textEl = aiMsg.querySelector('.message-text');
            const citationsEl = aiMsg.querySelector('.citation-strip');
            if (!textEl) return;

            const sendBtn = chatForm.querySelector('.send-button');
            if (sendBtn) sendBtn.disabled = true;

            showThinkingIndicator(chatThread);

            let fullText = ''; let receivedFirst = false;

            const requestNotebookKey = getActiveNotebookKey();
            const requestNotebookId = requestNotebookKey ? Number(requestNotebookKey) : null;
            const requestVersion = notebookLoadVersion;
            const notebookId = requestNotebookId;
            activeStreamController = chatStream(text, {
                conversationId: activeConversationId,
                notebookId: requestNotebookId,
                onToken(token) {
                    if (!isCurrentNotebookLoad(requestVersion, requestNotebookKey)) return;
                    if (!receivedFirst) { receivedFirst = true; hideThinkingIndicator(); aiMsg.style.display = 'flex'; }
                    fullText += token;
                    textEl.innerHTML = '';
                    processRichText(textEl, fullText + ' <span class="streaming-cursor"></span>');
                    chatThread.scrollTop = chatThread.scrollHeight;
                },
                onDone(payload) {
                    if (!isCurrentNotebookLoad(requestVersion, requestNotebookKey)) return;
                    if (payload?.conversation_id) activeConversationId = payload.conversation_id;
                    const finalText = payload?.answer || fullText;
                    const citations = Array.isArray(payload?.citations) ? payload.citations : [];
                    if (notebookId) {
                        manualNewChatByNotebook.delete(notebookId);
                        const previous = normalizeConversationState(
                            conversationStateByNotebook.get(notebookId) || emptyConversationState(),
                        );
                        const conversation = previous.conversation || (payload?.conversation_id ? {
                            id: payload.conversation_id,
                            notebook_id: notebookId,
                            owner_id: null,
                            created_at: null,
                            updated_at: null,
                        } : null);
                        const assistantMessageState = {
                            id: payload?.message_id || '',
                            role: 'assistant',
                            content: finalText,
                            sources_used: citations,
                            rewritten_query: payload?.rewritten_query || null,
                        };
                        const nextState = {
                            conversation,
                            messages: [...previous.messages, userMessageState, assistantMessageState],
                            has_conversation: Boolean(conversation),
                            limit: CONVERSATION_MESSAGE_LIMIT,
                        };
                        conversationStateByNotebook.set(notebookId, nextState);
                        activeConversationByNotebook.set(notebookId, activeConversationId);
                        writeCachedConversation(notebookId, nextState);
                    }
                    fullText = finalText;
                    hideThinkingIndicator();
                    aiMsg.style.display = 'flex';
                    textEl.innerHTML = '';
                    const displayText = finalText.trim() || 'Sorry, I could not generate a response. Please check backend logs for errors.';
                    processRichText(textEl, displayText, citations);
                    renderCitationChips(citationsEl, []);
                    aiMsg.classList.remove('streaming');
                    activeStreamController = null;
                    if (sendBtn) sendBtn.disabled = false;
                },
                onError(err) {
                    if (!isCurrentNotebookLoad(requestVersion, requestNotebookKey)) return;
                    hideThinkingIndicator();
                    aiMsg.style.display = 'flex';
                    textEl.insertAdjacentText('beforeend', `\n\nError: ${err.message}`);
                    aiMsg.classList.remove('streaming');
                    activeStreamController = null;
                    if (sendBtn) sendBtn.disabled = false;
                },
            });
        });

        chatPrompt.addEventListener('keydown', (ev) => {
            if (ev.key === 'Enter' && !ev.shiftKey) { ev.preventDefault(); if (chatForm.requestSubmit) chatForm.requestSubmit(); else chatForm.dispatchEvent(new Event('submit', { cancelable: true })); }
        });
        chatPrompt.addEventListener('input', () => { chatPrompt.style.height = 'auto'; chatPrompt.style.height = `${Math.min(chatPrompt.scrollHeight, 140)}px`; });
    }

    chatThread?.addEventListener('click', (ev) => {
        const action = ev.target.closest('.message-action')?.getAttribute('data-action');
        if (!action) return;
        const messageEl = ev.target.closest('.message, .ai-response');
        const content = messageEl?.querySelector('.message-text')?.textContent?.trim();
        if (!messageEl || !content) return;
        const notebookId = currentNotebookId(chatScene);
        const state = notebookId ? conversationStateByNotebook.get(notebookId) : null;
        const messageId = messageEl.dataset.messageId || null;
        const stateMessage = state?.messages?.find((message) => message.id === messageId);
        saveNotebookItem({
            kind: action === 'pin-message' ? 'pin' : 'note',
            title: action === 'pin-message' ? 'Pinned message' : 'Saved message',
            content,
            conversation_id: activeConversationId,
            message_id: messageId,
            sources_used: stateMessage?.sources_used || [],
        });
    });

    newChatBtn?.addEventListener('click', () => {
        const notebookId = currentNotebookId(chatScene);
        activeConversationId = null;
        if (notebookId) {
            manualNewChatByNotebook.add(notebookId);
            activeConversationByNotebook.set(notebookId, null);
            conversationStateByNotebook.set(notebookId, emptyConversationState());
            writeCachedConversation(notebookId, emptyConversationState());
        }
        renderWelcomeMessage(chatThread);
        resetSourceViewer();
    });

    saveConversationBtn?.addEventListener('click', () => {
        const content = visibleConversationText();
        if (!content) return;
        saveNotebookItem({
            kind: 'conversation',
            title: document.querySelector('#scene-chat .chat-title')?.textContent || 'Saved conversation',
            content,
            conversation_id: activeConversationId,
        });
    });

    summarizeBtn?.addEventListener('click', () => {
        const content = visibleConversationText();
        if (!content) return;
        saveNotebookItem({
            kind: 'summary',
            title: 'Conversation summary draft',
            content,
            conversation_id: activeConversationId,
        });
    });

    clearChatBtn?.addEventListener('click', () => {
        const notebookId = currentNotebookId(chatScene);
        activeConversationId = null;
        if (notebookId) {
            activeConversationByNotebook.set(notebookId, null);
            conversationStateByNotebook.set(notebookId, emptyConversationState());
            writeCachedConversation(notebookId, emptyConversationState());
        }
        if (chatThread) { chatThread.innerHTML = ''; addMessage(chatThread, 'ai', 'Chat cleared. How can I help next?'); }
    });
}
