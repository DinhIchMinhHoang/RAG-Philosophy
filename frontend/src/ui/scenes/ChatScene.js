import { chatStream, getJob, uploadDocument, BASE_URL } from '../../api/index.js';

function processRichText(container, text) {
    let html = text.replace(/\[Trang (\d+)\]/g, (_, p1) => `<button class="citation-btn" data-page="${p1}"><span class="material-icons">find_in_page</span>Trang ${p1}</button>`);
    html = html.replace(/- ([^,\n]+),\s*Trang\s*(\d+)/g, (_, file, page) => `<button class="citation-btn" data-file="${file.trim()}" data-page="${page}"><span class="material-icons">description</span> ${file.trim()} (P. ${page})</button>`);
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
            const file = btn.getAttribute('data-file');
            const firstSource = document.querySelector('#scene-chat .source-name')?.textContent;
            showPagePreview(file || firstSource);
        });
    });
}

const viewerState = { filename: null };
let activeStreamController = null;
let setCollapsedFn = null;

export function showPagePreview(filename) {
    if (!filename) return;
    viewerState.filename = filename;

    const viewer = document.querySelector('#sourceViewer');
    const empty = viewer?.querySelector('.viewer-empty');
    const content = viewer?.querySelector('.viewer-content');
    const embed = viewer?.querySelector('#pdfViewer');
    const nameEl = viewer?.querySelector('#viewerFileName');

    if (empty) empty.style.display = 'none';
    if (content) content.style.display = 'flex';
    if (nameEl) nameEl.textContent = filename;
    if (embed) embed.src = `${BASE_URL}/documents/file/${encodeURIComponent(filename)}`;

    if (document.querySelector('.chat-shell')?.getAttribute('data-right-collapsed') === 'true') {
        if (setCollapsedFn) setCollapsedFn('right', false);
    }
}

function addMessage(chatThread, role, text) {
    if (!chatThread) return null;
    const msg = document.createElement('div');
    msg.className = role === 'ai' ? 'ai-response' : `message ${role}`;
    msg.innerHTML = `<div class="message-text"></div><div class="message-meta"></div>`;
    const textEl = msg.querySelector('.message-text');
    const metaEl = msg.querySelector('.message-meta');
    if (textEl) { if (role === 'ai') processRichText(textEl, text); else textEl.textContent = text; }
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
    const sourceList = chatScene.querySelector('.source-list');
    const sourceEmpty = chatScene.querySelector('.source-empty');
    const sourceAddButtons = chatScene.querySelectorAll('.source-add-button');
    const sourceNoteButton = chatScene.querySelector('.source-note-button');

    const handleFiles = async (files) => {
        const list = Array.from(files || []);
        for (const file of list) {
            const isPDF = file.name.toLowerCase().endsWith('.pdf');
            const icon = isPDF ? 'picture_as_pdf' : 'description';
            const meta = isPDF ? 'Uploading…' : (file.type || 'file');

            const item = document.createElement('div');
            item.className = 'source-item';
            item.style.cursor = 'pointer';
            item.innerHTML = `<div class="source-icon"><span class="material-icons">${icon}</span></div><div class="source-meta"><div class="source-name">${file.name}</div><div class="source-type uploading">${meta}</div></div>`;
            item.addEventListener('click', () => { if (isPDF) showPagePreview(file.name); });
            sourceList.appendChild(item);
            updateSourceEmpty(sourceEmpty, sourceList);

            if (isPDF) {
                const metaEl = item.querySelector('.source-type');
                try {
                    const result = await uploadDocument(file);
                    if (result.pages !== undefined || result.chunks !== undefined) {
                        setSourceMeta(metaEl, `${result.pages ?? 0} pages, ${result.chunks ?? 0} chunks`, false);
                    } else if (result.job_id) {
                        setSourceMeta(metaEl, 'Queued for indexing', true);
                        pollUploadJob(result.job_id, metaEl).catch((err) => {
                            console.error('[Upload job]', err);
                            setSourceMeta(metaEl, `Error: ${err.message}`, false);
                        });
                    } else {
                        setSourceMeta(metaEl, result.status || 'Upload accepted', false);
                    }
                } catch (err) {
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
    const chatThread = chatScene.querySelector('.chat-thread');
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
            aiMsg.innerHTML = `<div class="message-text"></div><div class="message-meta">Lumina</div>`;
            chatThread.appendChild(aiMsg);
            const textEl = aiMsg.querySelector('.message-text');
            if (!textEl) return;

            const sendBtn = chatForm.querySelector('.send-button');
            if (sendBtn) sendBtn.disabled = true;

            showThinkingIndicator(chatThread);

            let fullText = ''; let receivedFirst = false;

            activeStreamController = chatStream(text, {
                onToken(token) {
                    if (!receivedFirst) { receivedFirst = true; hideThinkingIndicator(); aiMsg.style.display = 'flex'; }
                    fullText += token;
                    textEl.innerHTML = '';
                    processRichText(textEl, fullText + ' <span class="streaming-cursor"></span>');
                    chatThread.scrollTop = chatThread.scrollHeight;
                },
                onDone() {
                    hideThinkingIndicator();
                    aiMsg.style.display = 'flex';
                    textEl.innerHTML = '';
                    processRichText(textEl, fullText);
                    aiMsg.classList.remove('streaming');
                    activeStreamController = null;
                    if (sendBtn) sendBtn.disabled = false;
                },
                onError(err) {
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
        if (chatThread) { chatThread.innerHTML = ''; addMessage(chatThread, 'ai', 'Chat cleared. How can I help next?'); }
    });
}
