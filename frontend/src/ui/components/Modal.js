let currentTarget = null;

export function showImageModal(target) {
    currentTarget = target;
    const imageModal = document.getElementById('imageModal');
    if (!imageModal) return;

    const imagePreview = document.getElementById('imagePreview');
    const colorPreview = document.getElementById('colorPreview');
    const tabButtons = document.querySelectorAll('.image-modal-tabs .tab');
    const tabPanels = document.querySelectorAll('.tab-panel');

    if (imagePreview) { imagePreview.style.backgroundImage = ''; imagePreview.dataset.image = ''; }
    if (colorPreview) { colorPreview.style.backgroundColor = ''; colorPreview.dataset.color = ''; }

    tabButtons.forEach(tb => tb.classList.remove('active'));
    tabPanels.forEach(p => p.classList.add('hidden'));
    if (tabButtons[0]) tabButtons[0].classList.add('active');
    if (tabPanels[0]) tabPanels[0].classList.remove('hidden');

    const cover = target?.querySelector('.cover');
    if (cover) {
        const comp = window.getComputedStyle(cover);
        const inlineBg = cover.style.backgroundImage || comp.backgroundImage || '';
        const m = inlineBg.match(/^url\((?:"'|)?(.+?)(?:"'|)?\)$/);
        if (m && m[1]) {
            if (imagePreview) { imagePreview.style.backgroundImage = `url(${m[1]})`; imagePreview.dataset.image = m[1]; }
        } else {
            const bc = comp.backgroundColor || '';
            if (bc && bc !== 'rgba(0, 0, 0, 0)' && bc !== 'transparent') {
                if (colorPreview) { colorPreview.style.backgroundColor = bc; colorPreview.dataset.color = bc; }
                tabButtons.forEach(tb => tb.classList.remove('active'));
                tabPanels.forEach(p => p.classList.add('hidden'));
                const tbColor = document.querySelector('.image-modal-tabs .tab[data-tab="color"]');
                if (tbColor) tbColor.classList.add('active');
                const pnlColor = document.querySelector('.tab-panel[data-panel="color"]');
                if (pnlColor) pnlColor.classList.remove('hidden');
            }
        }
    }

    imageModal.classList.add('open');
    imageModal.style.display = 'flex';
    imageModal.setAttribute('aria-hidden', 'false');
}

export function hideImageModal() {
    currentTarget = null;
    const imageModal = document.getElementById('imageModal');
    if (!imageModal) return;
    imageModal.classList.remove('open');
    imageModal.style.display = 'none';
    imageModal.setAttribute('aria-hidden', 'true');
}

