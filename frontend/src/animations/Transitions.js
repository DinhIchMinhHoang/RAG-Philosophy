import { getSceneElement } from '../state/scenes.js';
import { isAuthenticated } from '../api/client.js';
import { store } from '../state/store.js';

export class TransitionManager {
    constructor() {
        this.currentScene = 'landing';
        this.isTransitioning = false;
        this.transitionToken = 0;
        this.transitionDuration = 150;
    }

    transitionTo(targetScene) {
        if (this.isTransitioning || targetScene === this.currentScene) return;
        if (targetScene === 'account' && !isAuthenticated()) targetScene = 'signin';
        if (targetScene === 'admin' && (!isAuthenticated() || !store.getIsAdmin())) targetScene = 'dashboard';

        const transitionToken = ++this.transitionToken;
        const isCurrentTransition = () => transitionToken === this.transitionToken;
        this.isTransitioning = true;

        if (targetScene === 'chat') {
            document.body.classList.add('chat-active');
        } else {
            document.body.classList.remove('chat-active');
            if (document.activeElement && typeof document.activeElement.blur === 'function') {
                document.activeElement.blur();
            }
        }

        this.fadeOutScene(this.currentScene, () => {
            if (!isCurrentTransition()) return;
            document.querySelectorAll('.scene').forEach(scene => scene.style.display = 'none');
            this.currentScene = targetScene;

            const finish = () => { if (isCurrentTransition()) this.isTransitioning = false; };

            if (targetScene === 'landing' || targetScene === 'chat') {
                this.fadeNavbarOut(() => {
                    if (isCurrentTransition()) this.fadeInScene(targetScene, finish);
                }, isCurrentTransition);
            } else {
                this.fadeNavbarIn(() => {
                    if (isCurrentTransition()) this.fadeInScene(targetScene, finish);
                }, isCurrentTransition);
            }
        });
    }

    openNotebook(title) {
        const safeTitle = (title || '').trim() || 'Untitled notebook';
        const titleEl = document.querySelector('.chat-title');
        if (titleEl) titleEl.textContent = safeTitle;
        this.transitionTo('chat');
        const prompt = document.getElementById('chatPrompt');
        if (prompt) setTimeout(() => prompt.focus(), 420);
    }

    fadeOutScene(scene, callback) {
        const container = getSceneElement(scene);
        if (!container) { callback(); return; }
        const elements = Array.from(container.children).reverse();
        const total = elements.length;
        if (total === 0) { callback(); return; }

        let completed = 0;
        let safetyTimer;
        const safetyMs = this.transitionDuration + (total * 80) + 200;

        elements.forEach((el, idx) => {
            setTimeout(() => {
                el.classList.remove('pre-hidden');
                el.style.setProperty('--anim-y', '40px');
                el.style.setProperty('--anim-opacity', '0');
                let done = false;
                const onTrans = (e) => {
                    if (e.propertyName !== 'opacity') return;
                    if (done) return;
                    done = true;
                    el.removeEventListener('transitionend', onTrans);
                    completed++;
                    if (completed === total) { clearTimeout(safetyTimer); callback(); }
                };
                el.addEventListener('transitionend', onTrans);
            }, idx * 80);
        });

        safetyTimer = setTimeout(() => {
            elements.forEach(el => { el.style.setProperty('--anim-y', '40px'); el.style.setProperty('--anim-opacity', '0'); el.classList.remove('pre-hidden'); });
            callback();
        }, safetyMs);
    }

    fadeInScene(scene, callback) {
        const container = getSceneElement(scene);
        if (!container) { callback(); return; }
        const elements = Array.from(container.children);
        const total = elements.length;
        if (total === 0) { container.style.display = 'flex'; callback(); return; }

        elements.forEach(el => {
            el.classList.remove('fade-out-bottom', 'fade-in-top');
            el.classList.add('pre-hidden');
            el.style.setProperty('--anim-y', '-40px');
            el.style.setProperty('--anim-opacity', '0');
        });

        container.style.display = 'flex';
        container.offsetHeight;

        if (scene === 'account') {
            const un = container.querySelector('#account-username');
            const em = container.querySelector('#account-email');
            const dn = container.querySelector('#account-displayname');
            const bo = container.querySelector('#account-bio');
            const u = store.user;
            if (un) un.value = u.username || '';
            if (em) em.value = u.email || '';
            if (dn) dn.value = u.displayName || '';
            if (bo) bo.value = u.bio || '';
            const adminEntry = container.querySelector('.admin-entry');
            if (adminEntry) adminEntry.style.display = store.getIsAdmin() ? 'block' : 'none';
        }

        if (scene === 'admin') {
            document.dispatchEvent(new CustomEvent('admin:show'));
        }

        let completed = 0;
        let safetyTimer;
        const safetyMs = this.transitionDuration + (total * 80) + 200;

        elements.forEach((el, idx) => {
            setTimeout(() => {
                el.style.setProperty('--anim-y', '0px');
                el.style.setProperty('--anim-opacity', '1');
                let done = false;
                const onTrans = (e) => {
                    if (e.propertyName !== 'opacity') return;
                    if (done) return;
                    done = true;
                    el.removeEventListener('transitionend', onTrans);
                    el.classList.remove('pre-hidden');
                    el.style.removeProperty('--anim-y');
                    el.style.removeProperty('--anim-opacity');
                    completed++;
                    if (completed === total) { clearTimeout(safetyTimer); callback(); }
                };
                el.addEventListener('transitionend', onTrans);
            }, idx * 80);
        });

        safetyTimer = setTimeout(() => {
            elements.forEach(el => {
                el.classList.remove('pre-hidden');
                el.style.removeProperty('--anim-y');
                el.style.removeProperty('--anim-opacity');
            });
            callback();
        }, safetyMs);
    }

    fadeNavbarIn(callback, isCurrentTransition = () => true) {
        const navbar = document.querySelector('.navbar');
        if (!navbar) { callback(); return; }
        navbar.classList.remove('fade-out-bottom');
        navbar.classList.add('pre-hidden');
        navbar.style.display = 'flex';
        navbar.style.setProperty('--anim-y', '-40px');
        navbar.style.setProperty('--anim-opacity', '0');
        navbar.offsetHeight;
        navbar.style.setProperty('--anim-y', '0px');
        navbar.style.setProperty('--anim-opacity', '1');

        let safetyTimer;
        const onEnd = (e) => {
            if (e.propertyName !== 'opacity') return;
            if (!isCurrentTransition()) return;
            clearTimeout(safetyTimer);
            navbar.removeEventListener('transitionend', onEnd);
            navbar.classList.remove('pre-hidden');
            navbar.style.removeProperty('--anim-y');
            navbar.style.removeProperty('--anim-opacity');
            callback();
        };
        navbar.addEventListener('transitionend', onEnd);
        safetyTimer = setTimeout(() => { if (isCurrentTransition()) { navbar.classList.remove('pre-hidden'); navbar.style.removeProperty('--anim-y'); navbar.style.removeProperty('--anim-opacity'); callback(); } }, this.transitionDuration + 300);
    }

    fadeNavbarOut(callback, isCurrentTransition = () => true) {
        const navbar = document.querySelector('.navbar');
        if (!navbar) { callback(); return; }
        navbar.classList.remove('pre-hidden');
        navbar.style.setProperty('--anim-y', '40px');
        navbar.style.setProperty('--anim-opacity', '0');

        let safetyTimer;
        const onEnd = (e) => {
            if (e.propertyName !== 'opacity') return;
            if (!isCurrentTransition()) return;
            clearTimeout(safetyTimer);
            navbar.removeEventListener('transitionend', onEnd);
            navbar.style.display = 'none';
            navbar.style.removeProperty('--anim-y');
            navbar.style.removeProperty('--anim-opacity');
            callback();
        };
        navbar.addEventListener('transitionend', onEnd);
        safetyTimer = setTimeout(() => { if (isCurrentTransition()) { navbar.style.display = 'none'; navbar.style.removeProperty('--anim-y'); navbar.style.removeProperty('--anim-opacity'); callback(); } }, this.transitionDuration + 300);
    }

    updateAuthUI() {
        const accountBtn = document.querySelector('.account-button');
        if (accountBtn) accountBtn.style.display = isAuthenticated() ? '' : 'none';
    }
}
