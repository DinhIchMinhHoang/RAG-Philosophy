import { hideImageModal, showImageModal } from '../components/Modal.js';
import { isAuthenticated } from '../../api/client.js';
import { getNotebooks, createNotebook, updateNotebook, deleteNotebook } from '../../api/notebooks.js';

export function shouldLoadNotebooks() {
    return isAuthenticated();
}

function renderSkeletonCards(grid, count = 6) {
    grid.innerHTML = '';
    for (let i = 0; i < count; i++) {
        const card = document.createElement('div');
        card.className = 'notebook-item skeleton-card';
        card.innerHTML = `<div class="cover"></div><div class="item-title"><div class="skeleton skeleton-title" style="width:60%;height:14px;margin:0;"></div></div>`;
        grid.appendChild(card);
    }
}

function buildNotebookItem(nb) {
    const item = document.createElement('div');
    item.className = 'notebook-item';
    item.dataset.notebookId = nb.id;
    item.dataset.title = nb.title;
    if (nb.cover_url) item.dataset.cover = nb.cover_url;
    if (nb.cover_mode) item.dataset.coverMode = nb.cover_mode;
    if (nb.cover_color) item.dataset.coverColor = nb.cover_color;

    const cover = document.createElement('div');
    cover.className = 'cover';
    if (nb.cover_url) {
        cover.style.backgroundImage = `url(${nb.cover_url})`;
        cover.style.backgroundSize = nb.cover_mode || 'cover';
        cover.style.backgroundPosition = 'center';
    } else if (nb.cover_color) {
        cover.style.backgroundColor = nb.cover_color;
    }
    item.appendChild(cover);

    const title = document.createElement('div');
    title.className = 'item-title';
    title.textContent = nb.title;
    item.appendChild(title);

    const btn = document.createElement('button');
    btn.className = 'more-btn';
    btn.setAttribute('aria-label', 'More');
    btn.innerHTML = '<span class="material-icons">more_vert</span>';
    item.appendChild(btn);

    return item;
}

function renderNotebooks(grid, notebooks, emptyMessage) {
    grid.innerHTML = '';
    if (!notebooks || notebooks.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'notebook-empty-state';
        empty.textContent = emptyMessage;
        grid.appendChild(empty);
        return;
    }
    notebooks.forEach(nb => grid.appendChild(buildNotebookItem(nb)));
}

function repositionThumb(thumb, opt, pad) {
    if (!thumb || !opt) return;
    thumb.style.left = `${opt.offsetLeft + pad}px`;
    thumb.style.width = `${Math.max(24, opt.offsetWidth - pad * 2)}px`;
}

function setupThumbSwitch(switchEl, container) {
    if (!switchEl || !container) return;
    const options = Array.from(switchEl.querySelectorAll('.sort-option, .view-option'));
    const thumb = switchEl.querySelector('.sort-thumb, .view-thumb');
    const pad = parseInt(getComputedStyle(switchEl).getPropertyValue('--pad')) || 4;

    options.forEach(opt => {
        opt.addEventListener('click', () => {
            options.forEach(o => o.classList.remove('active'));
            opt.classList.add('active');
            repositionThumb(thumb, opt, pad);
            setTimeout(() => repositionThumb(thumb, opt, pad), 300);
        });
    });

    const active = switchEl.querySelector('.sort-option.active, .view-option.active') || options[0];
    if (active) { setTimeout(() => repositionThumb(thumb, active, pad), 20); setTimeout(() => repositionThumb(thumb, active, pad), 340); }

    window.addEventListener('resize', () => {
        const act = switchEl.querySelector('.sort-option.active, .view-option.active') || options[0];
        repositionThumb(thumb, act, pad);
    });
}

function setupMoreMenu(transitionManager) {
    const moreMenu = document.createElement('div');
    moreMenu.className = 'more-menu';
    moreMenu.innerHTML = `<button class="menu-item rename">Rename</button><button class="menu-item change-image">Change image</button><button class="menu-item delete">Delete</button>`;
    document.body.appendChild(moreMenu);

    let currentTarget = null;
    let lastFakeTarget = null;

    const hideMenu = () => {
        if (lastFakeTarget?.parentElement) { try { lastFakeTarget.parentElement.removeChild(lastFakeTarget); } catch (e) { } lastFakeTarget = null; }
        currentTarget = null;
        moreMenu.classList.remove('visible');
        moreMenu.style.display = 'none';
    };

    const showMenu = (target, anchor) => {
        currentTarget = target;
        moreMenu.style.display = 'block';
        moreMenu.classList.remove('visible');
        const rect = anchor.getBoundingClientRect();
        const mw = moreMenu.offsetWidth || 160;
        let left = rect.right - mw;
        if (left < 8) left = rect.left;
        if (left + mw > window.innerWidth - 8) left = window.innerWidth - mw - 8;
        moreMenu.style.left = `${Math.max(8, left)}px`;
        moreMenu.style.top = `${Math.min(window.innerHeight - 8, rect.bottom + 8)}px`;
        moreMenu.classList.add('visible');
    };

    if (document.getElementById('chooseFileBtn')) {
        const imageFileInput = document.getElementById('imageFileInput');
        const imagePreview = document.getElementById('imagePreview');
        const imageModeSelect = document.getElementById('imageMode');
        const colorPicker = document.getElementById('colorPicker');
        const colorPreview = document.getElementById('colorPreview');
        const applyCoverBtn = document.getElementById('applyCoverBtn');
        const cancelCoverBtn = document.getElementById('cancelCoverBtn');
        const tabButtons = document.querySelectorAll('.image-modal-tabs .tab');
        const tabPanels = document.querySelectorAll('.tab-panel');

        document.getElementById('chooseFileBtn')?.addEventListener('click', () => imageFileInput?.click());
        imageFileInput?.addEventListener('change', (ev) => {
            const f = ev.target.files?.[0];
            if (!f) return;
            const reader = new FileReader();
            reader.onload = (rEv) => { if (imagePreview) { imagePreview.style.backgroundImage = `url(${rEv.target.result})`; imagePreview.dataset.image = rEv.target.result; } };
            reader.readAsDataURL(f);
        });
        colorPicker?.addEventListener('input', (e) => { if (colorPreview) { colorPreview.style.backgroundColor = e.target.value; colorPreview.dataset.color = e.target.value; } });

        tabButtons.forEach(tb => tb.addEventListener('click', () => {
            const t = tb.getAttribute('data-tab');
            tabButtons.forEach(b => b.classList.remove('active'));
            tb.classList.add('active');
            tabPanels.forEach(p => { if (p.getAttribute('data-panel') === t) p.classList.remove('hidden'); else p.classList.add('hidden'); });
        }));

        if (applyCoverBtn) {
            applyCoverBtn.addEventListener('click', () => {
                if (!currentTarget) { hideImageModal(); hideMenu(); return; }
                const coverEl = currentTarget.querySelector('.cover');
                if (!coverEl) { hideImageModal(); hideMenu(); return; }
                const activeTab = document.querySelector('.image-modal-tabs .tab.active')?.getAttribute('data-tab') || 'upload';
                if (activeTab === 'upload') {
                    const data = imagePreview?.dataset?.image || '';
                    if (!data) { coverEl.style.backgroundImage = ''; coverEl.style.backgroundColor = ''; currentTarget.removeAttribute('data-cover'); currentTarget.removeAttribute('data-cover-mode'); }
                    else { coverEl.style.backgroundImage = `url(${data})`; coverEl.style.backgroundSize = (imageModeSelect ? imageModeSelect.value : 'cover'); coverEl.style.backgroundPosition = 'center'; coverEl.style.backgroundColor = ''; currentTarget.setAttribute('data-cover', data); currentTarget.setAttribute('data-cover-mode', imageModeSelect?.value || 'cover'); }
                } else {
                    const color = colorPreview?.dataset?.color || colorPicker?.value || '#000000';
                    coverEl.style.backgroundImage = ''; coverEl.style.backgroundColor = color; currentTarget.setAttribute('data-cover-color', color); currentTarget.removeAttribute('data-cover'); currentTarget.removeAttribute('data-cover-mode');
                }
                hideImageModal();
                hideMenu();
            });
        }
        cancelCoverBtn?.addEventListener('click', hideImageModal);
    }

    moreMenu.addEventListener('click', (ev) => {
        ev.stopPropagation();
        const actionEl = ev.target.closest('.menu-item');
        if (!actionEl || !currentTarget) return;
        const action = actionEl.classList.contains('rename') ? 'rename' : (actionEl.classList.contains('change-image') ? 'change-image' : 'delete');
        if (action === 'rename') {
            const newTitle = prompt('Rename notebook', currentTarget.querySelector('.item-title')?.textContent || currentTarget.getAttribute('data-title') || '');
            if (newTitle !== null) {
                const titleEl = currentTarget.querySelector('.item-title');
                if (titleEl) titleEl.textContent = newTitle;
                currentTarget.setAttribute('data-title', newTitle);
                const nbId = currentTarget.dataset.notebookId;
                if (nbId) {
                    updateNotebook(nbId, {
                        title: newTitle,
                        cover_url: currentTarget.dataset.cover || null,
                        cover_mode: currentTarget.dataset.coverMode || null,
                        cover_color: currentTarget.dataset.coverColor || null,
                    }).catch(err => console.error('[Dashboard] Rename failed', err));
                }
                if (currentTarget === lastFakeTarget) {
                    const chatTitleEl = document.querySelector('#scene-chat .chat-title');
                    if (chatTitleEl) chatTitleEl.textContent = newTitle;
                }
            }
        } else if (action === 'change-image') {
            showImageModal(currentTarget);
            return;
        } else if (action === 'delete') {
            if (confirm('Delete this notebook?')) {
                const nbId = currentTarget.dataset.notebookId;
                if (nbId) deleteNotebook(nbId).catch(err => console.error('[Dashboard] Delete failed', err));
                const parent = currentTarget.parentElement;
                if (parent) parent.removeChild(currentTarget);
            }
        }
        hideMenu();
    });

    document.addEventListener('click', (ev) => { if (!moreMenu.contains(ev.target)) hideMenu(); });
    window.addEventListener('resize', hideMenu);
    document.addEventListener('keydown', (ev) => { if (ev.key === 'Escape') hideMenu(); });

    return { moreMenu, showMenu, hideMenu, setLastFake: (t) => { lastFakeTarget = t; currentTarget = t; } };
}

export function initDashboardScene(transitionManager) {
    const dashboard = document.getElementById('scene-dashboard');
    const container = dashboard?.querySelector('.dashboard-container');

    if (dashboard && container) {
        setupThumbSwitch(dashboard.querySelector('.sort-switch'), container);

        const accountBtn = document.querySelector('[data-scene="account"]');
        if (accountBtn) accountBtn.addEventListener('click', () => {
            if (!isAuthenticated()) transitionManager.transitionTo('signin');
            else transitionManager.transitionTo('account');
        });

        const createBtn = dashboard.querySelector('.create-button');
        if (createBtn) createBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                const nb = await createNotebook({ title: 'Untitled notebook', is_community: false });
                transitionManager.openNotebook(nb.title, nb.id);
            } catch (err) {
                console.error('[Dashboard] Failed to create notebook', err);
            }
        });

        const searchButton = dashboard.querySelector('.search-button');
        const searchInput = dashboard.querySelector('.search-input');
        if (searchButton && searchInput) {
            searchButton.addEventListener('click', () => {
                const isActive = container.classList.toggle('search-active');
                const icon = searchButton.querySelector('.material-icons');
                if (isActive) { icon.textContent = 'close'; setTimeout(() => searchInput.focus(), 200); }
                else { icon.textContent = 'search'; searchInput.value = ''; }
            });
        }

        const viewToggle = dashboard.querySelector('.view-toggle');
        if (viewToggle) {
            const options = Array.from(viewToggle.querySelectorAll('.view-option'));
            const thumb = viewToggle.querySelector('.view-thumb');
            const padV = parseInt(getComputedStyle(viewToggle).getPropertyValue('--pad')) || 4;

            options.forEach(o => {
                o.addEventListener('click', () => {
                    options.forEach(opt => opt.classList.remove('active'));
                    o.classList.add('active');
                    container.setAttribute('data-view', o.getAttribute('data-view'));
                    if (thumb) { repositionThumb(thumb, o, padV); setTimeout(() => repositionThumb(thumb, o, padV), 300); }
                });
            });
            setTimeout(() => { const act = viewToggle.querySelector('.view-option.active') || options[0]; if (thumb) repositionThumb(thumb, act, padV); }, 20);
            window.addEventListener('resize', () => { const act = viewToggle.querySelector('.view-option.active') || options[0]; if (thumb) repositionThumb(thumb, act, padV); });
        }

        const menuHandlers = setupMoreMenu(transitionManager);
        const { moreMenu, showMenu, hideMenu, setLastFake } = menuHandlers;

        const attachMoreHandlers = () => {
            document.querySelectorAll('.notebook-item .more-btn').forEach(btn => {
                if (btn._hasMenuHandler) return;
                btn._hasMenuHandler = true;
                btn.addEventListener('click', (ev) => {
                    ev.stopPropagation();
                    const item = btn.closest('.notebook-item');
                    if (!item) return;
                    showMenu(item, btn);
                });
            });
        };
        attachMoreHandlers();
        const gridObserver = new MutationObserver(() => attachMoreHandlers());
        document.querySelectorAll('.notebook-grid').forEach(g => gridObserver.observe(g, { childList: true, subtree: true }));

        async function loadNotebooks() {
            const communityGrid = document.querySelector('.community-grid');
            const myGrid = document.querySelector('.my-grid');
            if (!communityGrid || !myGrid) return;

            renderSkeletonCards(communityGrid, 4);
            renderSkeletonCards(myGrid, 2);

            try {
                const notebooks = await getNotebooks();
                const community = (notebooks || []).filter(n => n.is_community);
                const mine = (notebooks || []).filter(n => !n.is_community);
                renderNotebooks(communityGrid, community, 'No community notebooks yet');
                renderNotebooks(myGrid, mine, 'No notebooks yet');
            } catch (err) {
                console.error('[Dashboard] Failed to load notebooks', err);
                communityGrid.innerHTML = '<div class="notebook-empty-state">Failed to load notebooks</div>';
                myGrid.innerHTML = '';
            }
        }
        document.addEventListener('auth:changed', () => {
            if (shouldLoadNotebooks()) loadNotebooks();
        });
        if (shouldLoadNotebooks()) loadNotebooks();

        document.addEventListener('click', (ev) => {
            const item = ev.target.closest('.notebook-item');
            if (!item) return;
            if (ev.target.closest('.more-btn') || ev.target.closest('.more-menu') || ev.target.closest('#imageModal')) return;
            const title = item.getAttribute('data-title') || item.querySelector('.item-title')?.textContent || 'Untitled notebook';
            transitionManager.openNotebook(title, item.dataset.notebookId || null);
        });

        const showAllScene = document.getElementById('scene-showall');
        const showAllGrid = document.querySelector('.showall-grid');
        const closeShowallBtn = document.querySelector('.close-showall-btn');
        let currentShowAllTarget = null;

        const getNotebookItems = (target) => {
            const grid = target === 'community' ? document.querySelector('.community-grid') : document.querySelector('.my-grid');
            return grid ? Array.from(grid.querySelectorAll('.notebook-item')) : [];
        };

        const populateShowAllGrid = (target) => {
            if (!showAllGrid) return;
            showAllGrid.innerHTML = '';
            getNotebookItems(target).forEach(item => {
                const clone = item.cloneNode(true);
                clone.querySelectorAll('.more-btn').forEach(btn => { btn._hasMenuHandler = false; });
                showAllGrid.appendChild(clone);
            });
            attachMoreHandlers();
        };

        document.querySelectorAll('.show-all-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                currentShowAllTarget = btn.getAttribute('data-target');
                populateShowAllGrid(currentShowAllTarget);
                transitionManager.transitionTo('showall');
            });
        });

        if (closeShowallBtn) closeShowallBtn.addEventListener('click', () => transitionManager.transitionTo('dashboard'));

        if (showAllScene) {
            const saContainer = showAllScene.querySelector('.dashboard-container');
            setupThumbSwitch(showAllScene.querySelector('.sort-switch'), saContainer);

            const saSearchBtn = showAllScene.querySelector('.search-button');
            const saSearchInput = showAllScene.querySelector('.search-input');
            if (saSearchBtn && saSearchInput) {
                saSearchBtn.addEventListener('click', () => {
                    const isActive = saContainer?.classList.toggle('search-active');
                    const icon = saSearchBtn.querySelector('.material-icons');
                    if (isActive) { icon.textContent = 'close'; setTimeout(() => saSearchInput.focus(), 200); }
                    else { icon.textContent = 'search'; saSearchInput.value = ''; }
                });
            }

            const saViewToggle = showAllScene.querySelector('.view-toggle');
            if (saViewToggle && saContainer) {
                const saOptions = Array.from(saViewToggle.querySelectorAll('.view-option'));
                const saThumb = saViewToggle.querySelector('.view-thumb');
                const saPadV = parseInt(getComputedStyle(saViewToggle).getPropertyValue('--pad')) || 4;
                saOptions.forEach(o => {
                    o.addEventListener('click', () => {
                        saOptions.forEach(opt => opt.classList.remove('active'));
                        o.classList.add('active');
                        saContainer.setAttribute('data-view', o.getAttribute('data-view'));
                        if (saThumb) { repositionThumb(saThumb, o, saPadV); setTimeout(() => repositionThumb(saThumb, o, saPadV), 300); }
                    });
                });
                setTimeout(() => { const act = saViewToggle.querySelector('.view-option.active') || saOptions[0]; if (saThumb) repositionThumb(saThumb, act, saPadV); }, 20);
                window.addEventListener('resize', () => { const act = saViewToggle.querySelector('.view-option.active') || saOptions[0]; if (saThumb) repositionThumb(saThumb, act, saPadV); });
            }
        }

        const chatScene = document.getElementById('scene-chat');
        if (chatScene) {
            const settingsBtn = chatScene.querySelector('.panel-icon-button[title="Notebook settings"]');
            if (settingsBtn) {
                settingsBtn.addEventListener('click', (ev) => {
                    ev.stopPropagation();
                    const chatTitle = chatScene.querySelector('.chat-title')?.textContent || 'Untitled notebook';
                    const fake = document.createElement('div');
                    fake.className = 'notebook-item';
                    fake.style.position = 'absolute'; fake.style.left = '-9999px'; fake.style.top = '-9999px';
                    if (chatScene.dataset.notebookId) fake.dataset.notebookId = chatScene.dataset.notebookId;
                    fake.innerHTML = `<div class="cover" style="background: transparent;"></div><div class="item-title">${chatTitle}</div>`;
                    document.body.appendChild(fake);
                    setLastFake(fake);
                    showMenu(fake, settingsBtn);
                });
            }
        }
    }
}
