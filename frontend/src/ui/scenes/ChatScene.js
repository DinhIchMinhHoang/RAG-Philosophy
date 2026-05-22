import { chatStream, getJob, uploadDocument, listSources, BASE_URL, getToken } from '../../api/index.js';
import { getLatestNotebookConversation } from '../../api/notebooks.js';

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

function escapeHtml(value) {
    return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

export function citationLabel(citation) {
    const id = citation?.citation_id || 'C?';
    const source = citation?.source || 'source';
    const page = citation?.page ? `, p. ${citation.page}` : '';
    return `${id} ${source}${page}`;
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
    html = html.replace(/📚 \*\*Nguồn tham khảo:\*\*/g, '<div class="sources-footer-title"><span class="material-icons">auto_stories</span> Nguồn tham khảo</div>');

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

function resetNotebookWorkspace({ chatThread, sourceList, sourceEmpty, chatPrompt, sourceInput, showSkeleton = false }) {
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

function renderWelcomeMessage(chatThread) {
    if (!chatThread) return;
    chatThread.innerHTML = '';
    const welcome = document.createElement('div');
    welcome.className = 'ai-response';
    welcome.innerHTML = `<div class="message-text">Hi, I can help you explore your sources. Add files on the left, then ask a question.</div><div class="message-meta">Lumina</div>`;
    chatThread.appendChild(welcome);
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

function addMessage(chatThread, role, text, citations = []) {
    if (!chatThread) return null;
    const msg = document.createElement('div');
    msg.className = role === 'ai' ? 'ai-response' : `message ${role}`;
    msg.innerHTML = `<div class="message-text"></div><div class="citation-strip"></div><div class="message-meta"></div>`;
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

const ingestStageLabels = {
    fetching_object: 'Fetching PDF',
    parsing: 'Parsing PDF',
    chunking: 'Chunking text',
    embedding: 'Embedding chunks',
    indexing_vector: 'Indexing vectors',
    persisting_metadata: 'Saving metadata',
};

function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

function setSourceMeta(metaEl, text, active = false) {
    if (!metaEl) return;
    metaEl.textContent = text;
    metaEl.classList.toggle('uploading', active);
}

function formatJobProgress(job) {
    if (job.status === 'queued') return 'Queued for indexing';

    const label = ingestStageLabels[job.stage] || 'Indexing document';
    const pct = Number(job.progress_pct);
    if (Number.isFinite(pct)) return `${label} ${pct}%`;
    return label;
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

    document.addEventListener('chat:notebookLeft', () => {
        notebookLoadVersion += 1;
        if (activeStreamController) {
            activeStreamController.abort();
            activeStreamController = null;
        }
        delete chatScene.dataset.notebookId;
        resetNotebookWorkspace({ chatThread, sourceList, sourceEmpty, chatPrompt, sourceInput });
    });

    document.addEventListener('chat:notebookChanged', async () => {
        const notebookId = chatScene.dataset.notebookId || '';
        const loadVersion = ++notebookLoadVersion;

        if (activeStreamController) {
            activeStreamController.abort();
            activeStreamController = null;
        }
        resetNotebookWorkspace({ chatThread, sourceList, sourceEmpty, chatPrompt, sourceInput, showSkeleton: Boolean(notebookId) });

        if (!notebookId) {
            setTimeout(() => {
                if (isCurrentNotebookLoad(loadVersion, notebookId)) renderWelcomeMessage(chatThread);
            }, 600);
            return;
        }

        try {
            const [convData, docsData] = await Promise.all([
                getLatestNotebookConversation(notebookId, { limit: 50 }),
                listSources(),
            ]);

            if (!isCurrentNotebookLoad(loadVersion, notebookId)) return;

            if (chatThread) {
                chatThread.innerHTML = '';
            }

            const notebookDocs = (docsData.documents || []).filter(
                d => Number(d.notebook_id) === Number(notebookId)
            );

            if (convData.has_conversation && convData.messages.length > 0) {
                activeConversationId = convData.conversation.id;
                if (chatThread) {
                    convData.messages.forEach(msg => {
                        addMessage(
                            chatThread,
                            msg.role === 'user' ? 'user' : 'ai',
                            msg.content,
                            msg.sources_used || [],
                        );
                    });
                }
            } else {
                renderWelcomeMessage(chatThread);
            }

            if (sourceList) {
                sourceList.innerHTML = '';
                notebookDocs.forEach(doc => {
                    const item = document.createElement('div');
                    item.className = 'source-item';
                    item.style.cursor = 'pointer';
                    const icon = doc.filename.toLowerCase().endsWith('.pdf') ? 'picture_as_pdf' : 'description';
                    const status = doc.latest_job?.status === 'succeeded' ? 'Ready' : (doc.latest_job?.status || 'Uploaded');
                    item.innerHTML = `<div class="source-icon"><span class="material-icons">${icon}</span></div><div class="source-meta"><div class="source-name">${escapeHtml(doc.filename)}</div><div class="source-type">${status}</div></div>`;
                    item.dataset.documentId = doc.document_id;
                    item.addEventListener('click', () => showPagePreview(doc.filename, null, doc.document_id, doc.mime_type));
                    sourceList.appendChild(item);
                });
                if (sourceEmpty) updateSourceEmpty(sourceEmpty, sourceList);
            }
        } catch (err) {
            if (!isCurrentNotebookLoad(loadVersion, notebookId)) return;
            console.error('[ChatScene] Failed to restore notebook state', err);
            renderWelcomeMessage(chatThread);
        }
    });

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

    const handleFiles = async (files) => {
        const list = Array.from(files || []);
        const uploadNotebookKey = getActiveNotebookKey();
        const uploadNotebookId = uploadNotebookKey ? Number(uploadNotebookKey) : null;
        for (const file of list) {
            if (getActiveNotebookKey() !== uploadNotebookKey) return;
            const isPDF = file.name.toLowerCase().endsWith('.pdf');
            const icon = isPDF ? 'picture_as_pdf' : 'description';
            const meta = isPDF ? 'Uploading…' : (file.type || 'file');

            const item = document.createElement('div');
            item.className = 'source-item';
            item.style.cursor = 'pointer';
            item.innerHTML = `<div class="source-icon"><span class="material-icons">${icon}</span></div><div class="source-meta"><div class="source-name">${file.name}</div><div class="source-type uploading">${meta}</div></div>`;
            item.addEventListener('click', () => { if (isPDF) showPagePreview(file.name, null, item.dataset.documentId || null, file.type || 'application/pdf'); });
            sourceList.appendChild(item);
            updateSourceEmpty(sourceEmpty, sourceList);

            if (isPDF) {
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

    if (chatForm && chatPrompt) {
        chatForm.addEventListener('submit', (ev) => {
            ev.preventDefault();
            const text = chatPrompt.value.trim();
            if (!text) return;

            if (activeStreamController) { activeStreamController.abort(); activeStreamController = null; }

            addMessage(chatThread, 'user', text);
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
                    fullText = finalText;
                    hideThinkingIndicator();
                    aiMsg.style.display = 'flex';
                    textEl.innerHTML = '';
                    processRichText(textEl, finalText, citations);
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

    clearChatBtn?.addEventListener('click', () => {
        activeConversationId = null;
        if (chatThread) { chatThread.innerHTML = ''; addMessage(chatThread, 'ai', 'Chat cleared. How can I help next?'); }
    });
}
