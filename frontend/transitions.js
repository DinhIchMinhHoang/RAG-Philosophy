// Transition Manager
class TransitionManager {
    constructor() {
        this.currentScene = 'landing';
        this.isTransitioning = false;
        this.transitionDuration = 500; // milliseconds
        // Load persisted user or use empty defaults
        this.currentUser = JSON.parse(localStorage.getItem('currentUser')) || { username: '', email: '', displayName: '', bio: '' };
    }

    /**
     * Transition to a new scene with fade out/in effects
     * @param {string} targetScene - The scene to transition to
     */
    transitionTo(targetScene) {
        if (this.isTransitioning || targetScene === this.currentScene) return;
        // Prevent accessing account scene when not authenticated
        if (targetScene === 'account' && !this.isAuthenticated()) {
            // redirect to sign-in instead
            targetScene = 'signin';
        }

        this.isTransitioning = true;

        // Step 1: Fade out current scene (bottom to top)
        this.fadeOutScene(this.currentScene, () => {
            // Step 2: Switch scenes in DOM (hide all scenes)
            this.switchScene(targetScene);

            // Step 3: Orchestrate navbar + scene fade-in so navbar appears first
            const finish = () => {
                this.currentScene = targetScene;
                this.isTransitioning = false;
            };

            if (targetScene === 'landing') {
                // When going to landing, ensure navbar fades out first then show landing
                this.fadeNavbarOut(() => {
                    this.fadeInScene(targetScene, finish);
                });
            } else {
                // For auth scenes: show navbar first, then scene children
                this.fadeNavbarIn(() => {
                    this.fadeInScene(targetScene, finish);
                });
            }
        });
    }

    isAuthenticated() {
        return Boolean(this.currentUser && (this.currentUser.email || this.currentUser.username));
    }

    updateAuthUI() {
        const accountBtn = document.querySelector('.account-button');
        if (!accountBtn) return;
        if (this.isAuthenticated()) {
            accountBtn.style.display = '';
        } else {
            accountBtn.style.display = 'none';
        }
    }

    /**
     * Fade out current scene - components disappear bottom to top
     * @param {string} scene - The scene to fade out
     * @param {function} callback - Called when fade out completes
     */
    fadeOutScene(scene, callback) {
        const container = document.getElementById(`scene-${scene}`);
        if (!container) {
            callback();
            return;
        }

        // Get all top-level children (animate all direct children)
        const elements = Array.from(container.children).reverse();
        const totalElements = elements.length;
        let completedAnimations = 0;

        if (totalElements === 0) {
            callback();
            return;
        }

        // Stagger using CSS-variable-driven transitions (move down + fade)
        let safetyTimer;
        const safetyTimeoutMs = this.transitionDuration + (totalElements * 80) + 200;

        elements.forEach((el, index) => {
            const delay = index * 80; // 80ms stagger between elements
            setTimeout(() => {
                // ensure not in pre-hidden state
                el.classList.remove('pre-hidden');
                // trigger transition: move down and fade out
                el.style.setProperty('--anim-y', '40px');
                el.style.setProperty('--anim-opacity', '0');

                let done = false;
                const onTransition = (e) => {
                    if (e.propertyName !== 'opacity') return;
                    if (done) return;
                    done = true;
                    el.removeEventListener('transitionend', onTransition);
                    completedAnimations++;
                    if (completedAnimations === totalElements) {
                        if (safetyTimer) clearTimeout(safetyTimer);
                        callback();
                    }
                };

                el.addEventListener('transitionend', onTransition);
            }, delay);
        });

        // Safety timeout: ensure callback and final state even if some transitionend events missed
        safetyTimer = setTimeout(() => {
            elements.forEach(el => {
                // force final hidden state
                el.style.setProperty('--anim-y', '40px');
                el.style.setProperty('--anim-opacity', '0');
                el.classList.remove('pre-hidden');
            });
            callback();
        }, safetyTimeoutMs);
    }

    /**
     * Fade in new scene - components appear top to bottom
     * @param {string} scene - The scene to fade in
     * @param {function} callback - Called when fade in completes
     */
    fadeInScene(scene, callback) {
        const container = document.getElementById(`scene-${scene}`);
        if (!container) {
            callback();
            return;
        }

        // Get all top-level children (animate all direct children)
        const elements = Array.from(container.children);
        const totalElements = elements.length;
        let completedAnimations = 0;

        if (totalElements === 0) {
            // show empty scene
            container.style.display = 'flex';
            callback();
            return;
        }

        // Pre-hide elements using CSS variables to ensure consistent start state
        elements.forEach(el => {
            el.classList.remove('fade-out-bottom');
            el.classList.remove('fade-in-top');
            el.classList.add('pre-hidden');
            // provide inline fallback values so browsers apply before display
            el.style.setProperty('--anim-y', '-40px');
            el.style.setProperty('--anim-opacity', '0');
        });

        // Show the scene after pre-hiding children to avoid flash
        container.style.display = 'flex';

        // Force reflow so the browser applies the pre-hidden state before animations
        // eslint-disable-next-line no-unused-expressions
        container.offsetHeight;

        // If showing dashboard, ensure toggle thumbs are positioned now that the container is visible
        if (scene === 'dashboard') {
            const dash = document.getElementById('scene-dashboard');
            if (dash) {
                const sortSwitch = dash.querySelector('.sort-switch');
                if (sortSwitch) {
                    const thumb = sortSwitch.querySelector('.sort-thumb');
                    const active = sortSwitch.querySelector('.sort-option.active') || sortSwitch.querySelector('.sort-option');
                    const pad = parseInt(getComputedStyle(sortSwitch).getPropertyValue('--pad')) || 4;
                    if (thumb && active) {
                        thumb.style.left = `${active.offsetLeft + pad}px`;
                        thumb.style.width = `${Math.max(24, active.offsetWidth - pad * 2)}px`;
                    }
                }

                const viewToggle = dash.querySelector('.view-toggle');
                if (viewToggle) {
                    const thumb = viewToggle.querySelector('.view-thumb');
                    const active = viewToggle.querySelector('.view-option.active') || viewToggle.querySelector('.view-option');
                    const padV = parseInt(getComputedStyle(viewToggle).getPropertyValue('--pad')) || 4;
                    if (thumb && active) {
                        thumb.style.left = `${active.offsetLeft + padV}px`;
                        thumb.style.width = `${Math.max(24, active.offsetWidth - padV * 2)}px`;
                    }
                }
            }
            // After labels expand (and scene children animate), recompute thumbs to match final widths
            setTimeout(() => {
                const dash2 = document.getElementById('scene-dashboard');
                if (!dash2) return;
                const ss = dash2.querySelector('.sort-switch');
                if (ss) {
                    const th = ss.querySelector('.sort-thumb');
                    const act = ss.querySelector('.sort-option.active') || ss.querySelector('.sort-option');
                    const pd = parseInt(getComputedStyle(ss).getPropertyValue('--pad')) || 4;
                    if (th && act) {
                        th.style.left = `${act.offsetLeft + pd}px`;
                        th.style.width = `${Math.max(24, act.offsetWidth - pd * 2)}px`;
                    }
                }
                const vt = dash2.querySelector('.view-toggle');
                if (vt) {
                    const thv = vt.querySelector('.view-thumb');
                    const actv = vt.querySelector('.view-option.active') || vt.querySelector('.view-option');
                    const pdv = parseInt(getComputedStyle(vt).getPropertyValue('--pad')) || 4;
                    if (thv && actv) {
                        thv.style.left = `${actv.offsetLeft + pdv}px`;
                        thv.style.width = `${Math.max(24, actv.offsetWidth - pdv * 2)}px`;
                    }
                }
            }, 360);
        }

        // If showing account scene, populate the fields from currentUser
        if (scene === 'account') {
            const unameEl = container.querySelector('#account-username');
            const emailEl = container.querySelector('#account-email');
            const displayEl = container.querySelector('#account-displayname');
            const bioEl = container.querySelector('#account-bio');
            if (unameEl) unameEl.value = this.currentUser.username || '';
            if (emailEl) emailEl.value = this.currentUser.email || '';
            if (displayEl) displayEl.value = this.currentUser.displayName || '';
            if (bioEl) bioEl.value = this.currentUser.bio || '';
        }

        // Stagger animation from top to bottom (normal order)
        let safetyTimer;
        const safetyTimeoutMs = this.transitionDuration + (totalElements * 80) + 200;

        elements.forEach((el, index) => {
            const delay = index * 80; // 80ms stagger between elements
            setTimeout(() => {
                // start transition by updating inline variables (will animate due to CSS transitions)
                el.style.setProperty('--anim-y', '0px');
                el.style.setProperty('--anim-opacity', '1');

                let done = false;
                const onTransition = (e) => {
                    if (e.propertyName !== 'opacity') return;
                    if (done) return;
                    done = true;
                    el.removeEventListener('transitionend', onTransition);
                    // cleanup
                    el.classList.remove('pre-hidden');
                    el.style.removeProperty('--anim-y');
                    el.style.removeProperty('--anim-opacity');
                    completedAnimations++;
                    if (completedAnimations === totalElements) {
                        if (safetyTimer) clearTimeout(safetyTimer);
                        callback();
                    }
                };

                el.addEventListener('transitionend', onTransition);
            }, delay);
        });

        // Safety timeout: ensure callback and cleanup if some transitionend events missed
        safetyTimer = setTimeout(() => {
            elements.forEach(el => {
                el.classList.remove('pre-hidden');
                el.style.removeProperty('--anim-y');
                el.style.removeProperty('--anim-opacity');
            });
            callback();
        }, safetyTimeoutMs);
    }

    /**
     * Switch visibility of scenes in the DOM
     * @param {string} targetScene - The scene to show
     */
    switchScene(targetScene) {
        // Hide all scenes
        document.querySelectorAll('[id^="scene-"]').forEach(scene => {
            scene.style.display = 'none';
        });
        // Note: Navbar show/hide is handled separately to control sequencing
    }

    /**
     * Fade navbar in and call callback after animation completes
     */
    fadeNavbarIn(callback) {
        const navbar = document.querySelector('.navbar');
        if (!navbar) {
            callback();
            return;
        }
        // Prepare navbar hidden state (CSS-variable-driven)
        navbar.classList.remove('fade-out-bottom');
        navbar.classList.add('pre-hidden');
        navbar.style.display = 'flex';
        navbar.style.setProperty('--anim-y', '-40px');
        navbar.style.setProperty('--anim-opacity', '0');

        // Force reflow to ensure class application
        // eslint-disable-next-line no-unused-expressions
        navbar.offsetHeight;

        // start navbar transition
        navbar.style.setProperty('--anim-y', '0px');
        navbar.style.setProperty('--anim-opacity', '1');

        let safetyTimer;
        const onEnd = (e) => {
            if (e.propertyName !== 'opacity') return;
            if (safetyTimer) clearTimeout(safetyTimer);
            navbar.removeEventListener('transitionend', onEnd);
            navbar.classList.remove('pre-hidden');
            navbar.style.removeProperty('--anim-y');
            navbar.style.removeProperty('--anim-opacity');
            callback();
        };
        navbar.addEventListener('transitionend', onEnd);

        // Safety fallback if transitionend doesn't fire
        safetyTimer = setTimeout(() => {
            navbar.classList.remove('pre-hidden');
            navbar.style.removeProperty('--anim-y');
            navbar.style.removeProperty('--anim-opacity');
            callback();
        }, this.transitionDuration + 300);
    }

    /**
     * Fade navbar out and call callback after animation completes
     */
    fadeNavbarOut(callback) {
        const navbar = document.querySelector('.navbar');
        if (!navbar) {
            callback();
            return;
        }
        navbar.classList.remove('pre-hidden');
        // trigger transition: move down and fade out
        navbar.style.setProperty('--anim-y', '40px');
        navbar.style.setProperty('--anim-opacity', '0');

        let safetyTimer;
        const onEnd = (e) => {
            if (e.propertyName !== 'opacity') return;
            if (safetyTimer) clearTimeout(safetyTimer);
            navbar.removeEventListener('transitionend', onEnd);
            navbar.style.display = 'none';
            navbar.style.removeProperty('--anim-y');
            navbar.style.removeProperty('--anim-opacity');
            callback();
        };
        navbar.addEventListener('transitionend', onEnd);

        // Safety fallback if transitionend doesn't fire
        safetyTimer = setTimeout(() => {
            navbar.style.display = 'none';
            navbar.style.removeProperty('--anim-y');
            navbar.style.removeProperty('--anim-opacity');
            callback();
        }, this.transitionDuration + 300);
    }

    /**
     * Initialize transition manager with event listeners
     */
    initialize() {
        // Sign Up button
        const signUpBtn = document.querySelector('[data-scene="signup"]');
        if (signUpBtn) {
            signUpBtn.addEventListener('click', () => this.transitionTo('signup'));
        }

        // Sign In button
        const signInBtn = document.querySelector('[data-scene="signin"]');
        if (signInBtn) {
            signInBtn.addEventListener('click', () => this.transitionTo('signin'));
        }

        // Back to landing buttons
        const backButtons = document.querySelectorAll('[data-back-to="landing"]');
        backButtons.forEach(btn => {
            btn.addEventListener('click', () => this.transitionTo('landing'));
        });

        /*
        // Sign-in form submit -> set current user and transition to dashboard
        const signInForm = document.querySelector('#scene-signin .auth-form');
        if (signInForm) {
                signInForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const emailInput = signInForm.querySelector('input[type="email"]');
                const email = emailInput ? emailInput.value.trim() : '';
                const usernameGuess = email ? (email.split('@')[0] || '') : '';
                this.currentUser = Object.assign({}, this.currentUser, {
                    username: this.currentUser.username || usernameGuess,
                    email: email,
                    displayName: this.currentUser.displayName || usernameGuess
                });
                localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
                    // update UI to reflect logged-in state
                    this.updateAuthUI();
                this.transitionTo('dashboard');
            });
        }

        // Sign-up form submit -> persist new user and transition to dashboard
        const signUpForm = document.querySelector('#scene-signup .auth-form');
        if (signUpForm) {
                signUpForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const usernameInput = signUpForm.querySelector('input[placeholder="User name"]') || signUpForm.querySelector('input[type="text"]');
                const emailInput = signUpForm.querySelector('input[type="email"]');
                const username = usernameInput ? usernameInput.value.trim() : '';
                const email = emailInput ? emailInput.value.trim() : '';
                this.currentUser = {
                    username: username || (email ? email.split('@')[0] : ''),
                    email: email,
                    displayName: username || (email ? email.split('@')[0] : ''),
                    bio: ''
                };
                localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
                    // update UI to reflect logged-in state
                    this.updateAuthUI();
                this.transitionTo('dashboard');
            });
        }
        */
       
        // Dashboard UI interactions
        const dashboard = document.getElementById('scene-dashboard');
        if (dashboard) {
            const container = dashboard.querySelector('.dashboard-container');

            // Sort switch (slide between Recently and A→Z) - dynamic thumb sizing
            const sortSwitch = dashboard.querySelector('.sort-switch');
            if (sortSwitch) {
                const options = Array.from(sortSwitch.querySelectorAll('.sort-option'));
                const thumb = sortSwitch.querySelector('.sort-thumb');
                const pad = parseInt(getComputedStyle(sortSwitch).getPropertyValue('--pad')) || 4;

                const repositionThumb = (opt) => {
                    if (!thumb || !opt) return;
                    // offsetLeft is relative to parent (sortSwitch)
                    const left = opt.offsetLeft + pad;
                    const width = Math.max(24, opt.offsetWidth - pad * 2);
                    thumb.style.left = `${left}px`;
                    thumb.style.width = `${width}px`;
                };

                const setThumb = (opt) => {
                    options.forEach(o => o.classList.remove('active'));
                    opt.classList.add('active');
                    // reposition immediately for the icon-only state
                    repositionThumb(opt);
                    // after label expansion animation completes, recompute to match final width
                    setTimeout(() => repositionThumb(opt), 300);
                };

                options.forEach(opt => {
                    opt.addEventListener('click', () => setThumb(opt));
                });

                // initialize when visible; attempt now and on resize
                const initial = sortSwitch.querySelector('.sort-option.active') || options[0];
                if (initial) {
                    // if parent not yet laid out, defer a tick; also recompute after label expansion
                    setTimeout(() => repositionThumb(initial), 20);
                    setTimeout(() => repositionThumb(initial), 340);
                }

                window.addEventListener('resize', () => {
                    const active = sortSwitch.querySelector('.sort-option.active') || options[0];
                    repositionThumb(active);
                });
            }

                // Account button (navbar) -> open account scene
                const accountBtn = document.querySelector('[data-scene="account"]');
            if (accountBtn) {
                accountBtn.addEventListener('click', () => {
                    if (!this.isAuthenticated()) {
                        // if not authed, send to sign in page
                        this.transitionTo('signin');
                        return;
                    }
                    this.transitionTo('account');
                });
            }

                // Account scene handlers (save, logout, delete)
                const accountScene = document.getElementById('scene-account');
                if (accountScene) {
                    const accountForm = accountScene.querySelector('.account-form');
                    const logoutBtn = accountScene.querySelector('.logout-button');
                    const deleteBtn = accountScene.querySelector('.delete-account-button');
                    const cancelBtn = accountScene.querySelector('[data-back-to="dashboard"]');

                    const populate = () => {
                        const uname = accountScene.querySelector('#account-username');
                        const email = accountScene.querySelector('#account-email');
                        const disp = accountScene.querySelector('#account-displayname');
                        const bio = accountScene.querySelector('#account-bio');
                        if (uname) uname.value = this.currentUser.username || '';
                        if (email) email.value = this.currentUser.email || '';
                        if (disp) disp.value = this.currentUser.displayName || '';
                        if (bio) bio.value = this.currentUser.bio || '';
                    };

                    // populate now (in case user opens immediately)
                    populate();

                    if (accountForm) {
                        accountForm.addEventListener('submit', (e) => {
                            e.preventDefault();
                            const uname = accountScene.querySelector('#account-username')?.value.trim() || '';
                            const email = accountScene.querySelector('#account-email')?.value.trim() || '';
                            const displayName = accountScene.querySelector('#account-displayname')?.value.trim() || '';
                            const bio = accountScene.querySelector('#account-bio')?.value.trim() || '';
                            this.currentUser = { username: uname, email: email, displayName: displayName, bio: bio };
                            localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
                            // update UI to reflect saved user
                            this.updateAuthUI();
                            // For now return to dashboard after save
                            this.transitionTo('dashboard');
                        });
                    }

                    if (cancelBtn) {
                        cancelBtn.addEventListener('click', () => this.transitionTo('dashboard'));
                    }

                    if (logoutBtn) {
                        logoutBtn.addEventListener('click', () => {
                            localStorage.removeItem('currentUser');
                            this.currentUser = { username: '', email: '', displayName: '', bio: '' };
                            this.updateAuthUI();
                            this.transitionTo('landing');
                        });
                    }

                    if (deleteBtn) {
                        deleteBtn.addEventListener('click', () => {
                            if (confirm('Delete your account? This cannot be undone.')) {
                                localStorage.removeItem('currentUser');
                                this.currentUser = { username: '', email: '', displayName: '', bio: '' };
                                this.updateAuthUI();
                                alert('Account deleted');
                                this.transitionTo('landing');
                            }
                        });
                    }
                }

            // Create button
            const createBtn = dashboard.querySelector('.create-button');
            if (createBtn) {
                createBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    // placeholder action
                    console.log('Create new notebook');
                });
            }

            // Search toggle (single button toggles search/close icon and expands center search input)
            const searchButton = dashboard.querySelector('.search-button');
            const searchInput = dashboard.querySelector('.search-input');
            if (searchButton && searchInput) {
                searchButton.addEventListener('click', () => {
                    const isActive = container.classList.toggle('search-active');
                    const icon = searchButton.querySelector('.material-icons');
                    if (isActive) {
                        icon.textContent = 'close';
                        setTimeout(() => searchInput.focus(), 200);
                    } else {
                        icon.textContent = 'search';
                        searchInput.value = '';
                    }
                });
            }

            // View toggle (grid/list switch) - dynamic thumb sizing
            const viewToggle = dashboard.querySelector('.view-toggle');
            if (viewToggle && container) {
                const options = Array.from(viewToggle.querySelectorAll('.view-option'));
                const thumb = viewToggle.querySelector('.view-thumb');
                const padV = parseInt(getComputedStyle(viewToggle).getPropertyValue('--pad')) || 4;

                const setView = (view) => {
                    options.forEach(o => o.classList.remove('active'));
                    const opt = viewToggle.querySelector(`.view-option[data-view="${view}"]`);
                    if (opt) {
                        opt.classList.add('active');
                        container.setAttribute('data-view', view);
                        if (opt && thumb) {
                            // immediate positioning for icon-only -> active state
                            thumb.style.left = `${opt.offsetLeft + padV}px`;
                            thumb.style.width = `${Math.max(24, opt.offsetWidth - padV * 2)}px`;
                        }
                        // recompute after label expansion finishes so thumb matches final width
                        setTimeout(() => {
                            if (opt && thumb) {
                                thumb.style.left = `${opt.offsetLeft + padV}px`;
                                thumb.style.width = `${Math.max(24, opt.offsetWidth - padV * 2)}px`;
                            }
                        }, 300);
                    } else {
                        container.setAttribute('data-view', view);
                    }
                };

                options.forEach(o => {
                    o.addEventListener('click', () => setView(o.getAttribute('data-view')));
                });

                // initialize to grid (defer to allow layout)
                setTimeout(() => setView('grid'), 20);

                window.addEventListener('resize', () => {
                    const active = viewToggle.querySelector('.view-option.active') || options[0];
                    if (active && thumb) {
                        thumb.style.left = `${active.offsetLeft + padV}px`;
                        thumb.style.width = `${Math.max(24, active.offsetWidth - padV * 2)}px`;
                    }
                });
            }
            // Ensure auth UI (account button) reflects current state on init
            this.updateAuthUI();
        }
    }
}

// Create global transition manager instance
const transitionManager = new TransitionManager();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    transitionManager.initialize();
});
