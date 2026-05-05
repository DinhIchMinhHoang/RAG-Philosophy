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
        return API.isAuthenticated();
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
        // Email validation helper
        const isValidEmail = (email) => {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        };

        const setupEmailValidation = (formSelector) => {
            const form = document.querySelector(formSelector);
            if (!form) return;
            const emailInput = form.querySelector('.email-input');
            const errorMsg = form.querySelector('.form-field-error');
            if (!emailInput) return;

            const validateEmail = () => {
                const email = emailInput.value.trim();
                if (!email) {
                    emailInput.classList.remove('email-error');
                    if (errorMsg) errorMsg.classList.remove('show');
                    return true;
                }
                if (!isValidEmail(email)) {
                    emailInput.classList.add('email-error');
                    if (errorMsg) {
                        errorMsg.textContent = 'Please enter a valid email address';
                        errorMsg.classList.add('show');
                    }
                    return false;
                }
                emailInput.classList.remove('email-error');
                if (errorMsg) errorMsg.classList.remove('show');
                return true;
            };

            // Real-time validation on input
            emailInput.addEventListener('input', validateEmail);
            emailInput.addEventListener('blur', validateEmail);

            // Validate on form submit
            form.addEventListener('submit', (e) => {
                if (!validateEmail()) {
                    e.preventDefault();
                }
            });
        };

        // Setup email validation for sign-up and sign-in forms
        setupEmailValidation('#scene-signup .auth-form');
        setupEmailValidation('#scene-signin .auth-form');

        // Also setup for account form email
        const accountForm = document.querySelector('#scene-account .account-form');
        if (accountForm) {
            const accountEmail = accountForm.querySelector('#account-email');
            if (accountEmail) {
                accountEmail.classList.add('email-input');
                const errorDiv = document.createElement('div');
                errorDiv.className = 'form-field-error';
                accountEmail.parentElement.appendChild(errorDiv);
                setupEmailValidation('#scene-account .account-form');
            }
        }

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

<<<<<<< HEAD
        // Click outside form to close (sign-in scene)
        const signInScene = document.getElementById('scene-signin');
        if (signInScene) {
            signInScene.addEventListener('click', (e) => {
                // Only close if clicking directly on the scene background, not on the form
                if (e.target === signInScene) {
                    this.transitionTo('landing');
                }
            });
        }

        // Click outside form to close (sign-up scene)
        const signUpScene = document.getElementById('scene-signup');
        if (signUpScene) {
            signUpScene.addEventListener('click', (e) => {
                // Only close if clicking directly on the scene background, not on the form
                if (e.target === signUpScene) {
                    this.transitionTo('landing');
                }
            });
        }

=======
<<<<<<< HEAD
        /*
        // Sign-in form submit -> set current user and transition to dashboard
=======
>>>>>>> 1d5ef64e7a5c8d30f8f050a152ebe4a9d1f13838
        // Sign-in form submit -> authenticate with backend and transition to dashboard
>>>>>>> ff54caf5fcc4b072850a25a0d1f561c441748afc
        const signInForm = document.querySelector('#scene-signin .auth-form');
        if (signInForm) {
                signInForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const signInScene = document.querySelector('#scene-signin');
                const errorDiv = signInScene.querySelector('.form-error');
                const emailInput = signInForm.querySelector('.email-input');
                const passwordInput = signInForm.querySelector('input[type="password"]');
                const email = emailInput ? emailInput.value.trim() : '';
                const password = passwordInput ? passwordInput.value : '';

                // Clear previous errors
                if (errorDiv) {
                    errorDiv.textContent = '';
                    errorDiv.style.display = 'none';
                }

                if (!email || !password) {
                    if (errorDiv) {
                        errorDiv.textContent = 'Please enter email and password';
                        errorDiv.style.display = 'block';
                    }
                    return;
                }

                // Validate email format
                if (!isValidEmail(email)) {
                    if (errorDiv) {
                        errorDiv.textContent = 'Please enter a valid email address';
                        errorDiv.style.display = 'block';
                    }
                    return;
                }

                try {
                    // Call backend login endpoint
                    const response = await API.login(email, password);
                    
                    // Extract username from email if not provided by backend
                    const usernameGuess = email.split('@')[0] || 'user';
                    
                    // Store user info
                    this.currentUser = {
                        username: usernameGuess,
                        email: email,
                        displayName: usernameGuess,
                        bio: ''
                    };
                    localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
                    
                    // Update UI to reflect logged-in state
                    this.updateAuthUI();
                    
                    // Clear form
                    signInForm.reset();
                    
                    // Transition to dashboard
                    this.transitionTo('dashboard');
                } catch (error) {
                    if (errorDiv) {
                        errorDiv.textContent = error.message;
                        errorDiv.style.display = 'block';
                    }
                    if (passwordInput) passwordInput.value = '';
                }
            });
        }

        // Sign-up form submit -> register with backend and transition to dashboard
        const signUpForm = document.querySelector('#scene-signup .auth-form');
        if (signUpForm) {
                signUpForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const signUpScene = document.querySelector('#scene-signup');
                const errorDiv = signUpScene.querySelector('.form-error');
                const usernameInput = signUpForm.querySelector('input[placeholder="User name"]') || signUpForm.querySelector('input:not(.email-input)[type="text"]');
                const emailInput = signUpForm.querySelector('.email-input');
                const passwordInputs = signUpForm.querySelectorAll('input[type="password"]');
                const password = passwordInputs[0] ? passwordInputs[0].value : '';
                const confirmPassword = passwordInputs[1] ? passwordInputs[1].value : '';
                const username = usernameInput ? usernameInput.value.trim() : '';
                const email = emailInput ? emailInput.value.trim() : '';

                // Clear previous errors
                if (errorDiv) {
                    errorDiv.textContent = '';
                    errorDiv.style.display = 'none';
                }

                // Validation
                if (!username || !email || !password || !confirmPassword) {
                    const msg = 'Please fill in all fields';
                    if (errorDiv) {
                        errorDiv.textContent = msg;
                        errorDiv.style.display = 'block';
                    }
                    return;
                }
                if (!isValidEmail(email)) {
                    const msg = 'Please enter a valid email address';
                    if (errorDiv) {
                        errorDiv.textContent = msg;
                        errorDiv.style.display = 'block';
                    }
                    return;
                }
                if (password !== confirmPassword) {
                    const msg = 'Passwords do not match';
                    if (errorDiv) {
                        errorDiv.textContent = msg;
                        errorDiv.style.display = 'block';
                    }
                    return;
                }
                if (password.length < 6) {
                    const msg = 'Password must be at least 6 characters';
                    if (errorDiv) {
                        errorDiv.textContent = msg;
                        errorDiv.style.display = 'block';
                    }
                    return;
                }

                try {
                    // Call backend signup endpoint
                    const response = await API.signup(username, email, password);
                    
                    // Store user info
                    this.currentUser = {
                        username: username,
                        email: email,
                        displayName: username,
                        bio: ''
                    };
                    localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
                    
                    // Update UI to reflect logged-in state
                    this.updateAuthUI();
                    
                    // Clear form
                    signUpForm.reset();
                    
                    // Transition to dashboard
                    this.transitionTo('dashboard');
                } catch (error) {
                    if (errorDiv) {
                        errorDiv.textContent = error.message;
                        errorDiv.style.display = 'block';
                    }
                    passwordInputs.forEach(input => input.value = '');
                }
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

                    // Password change button handler
                    const changePasswordBtn = accountScene.querySelector('.change-password-button');
                    if (changePasswordBtn) {
                        changePasswordBtn.addEventListener('click', async () => {
                            const errorDiv = accountScene.querySelector('.form-error');
                            const successDiv = accountScene.querySelector('.form-success');
                            const currentPassword = accountScene.querySelector('#current-password')?.value || '';
                            const newPassword = accountScene.querySelector('#new-password')?.value || '';
                            const confirmNewPassword = accountScene.querySelector('#confirm-new-password')?.value || '';

                            // Clear previous messages
                            if (errorDiv) { errorDiv.textContent = ''; errorDiv.style.display = 'none'; }
                            if (successDiv) { successDiv.textContent = ''; successDiv.style.display = 'none'; }

                            // Validation
                            if (!currentPassword || !newPassword || !confirmNewPassword) {
                                if (errorDiv) {
                                    errorDiv.textContent = 'Please fill in all password fields';
                                    errorDiv.style.display = 'block';
                                }
                                return;
                            }
                            if (newPassword !== confirmNewPassword) {
                                if (errorDiv) {
                                    errorDiv.textContent = 'New passwords do not match';
                                    errorDiv.style.display = 'block';
                                }
                                return;
                            }
                            if (newPassword.length < 6) {
                                if (errorDiv) {
                                    errorDiv.textContent = 'New password must be at least 6 characters';
                                    errorDiv.style.display = 'block';
                                }
                                return;
                            }

                            try {
                                const response = await API.changePassword(currentPassword, newPassword);
                                if (successDiv) {
                                    successDiv.textContent = 'Password changed successfully!';
                                    successDiv.style.display = 'block';
                                }
                                // Clear password fields
                                accountScene.querySelector('#current-password').value = '';
                                accountScene.querySelector('#new-password').value = '';
                                accountScene.querySelector('#confirm-new-password').value = '';
                                // Auto-hide success message after 3 seconds
                                setTimeout(() => {
                                    if (successDiv) {
                                        successDiv.style.display = 'none';
                                    }
                                }, 3000);
                            } catch (error) {
                                if (errorDiv) {
                                    errorDiv.textContent = error.message;
                                    errorDiv.style.display = 'block';
                                }
                                accountScene.querySelector('#current-password').value = '';
                            }
                        });
                    }

                    if (logoutBtn) {
                        logoutBtn.addEventListener('click', () => {
                            // Clear API token
                            API.clearToken();
                            // Clear localStorage
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
            // Create shared contextual menu for notebook items
            const moreMenu = document.createElement('div');
            moreMenu.className = 'more-menu';
            moreMenu.innerHTML = `
                <button class="menu-item rename">Rename</button>
                <button class="menu-item change-image">Change image</button>
                <button class="menu-item delete">Delete</button>
            `;
            document.body.appendChild(moreMenu);

            let currentMenuTarget = null;

            const hideMenu = () => {
                currentMenuTarget = null;
                moreMenu.classList.remove('visible');
                moreMenu.style.display = 'none';
            };

            // --- Image / Color picker modal wiring ---
            const imageModal = document.getElementById('imageModal');
            const imageFileInput = document.getElementById('imageFileInput');
            const imagePreview = document.getElementById('imagePreview');
            const chooseFileBtn = document.getElementById('chooseFileBtn');
            const imageModeSelect = document.getElementById('imageMode');
            const colorPicker = document.getElementById('colorPicker');
            const colorPreview = document.getElementById('colorPreview');
            const applyCoverBtn = document.getElementById('applyCoverBtn');
            const cancelCoverBtn = document.getElementById('cancelCoverBtn');
            const tabButtons = document.querySelectorAll('.image-modal-tabs .tab');
            const tabPanels = document.querySelectorAll('.tab-panel');

            let currentModalTarget = null;

            function extractUrlFromCss(cssValue) {
                if (!cssValue) return '';
                const m = cssValue.match(/^url\((?:\"|'|)?(.+?)(?:\"|'|)?\)$/);
                return m ? m[1] : '';
            }

            function showImageModal(target) {
                currentModalTarget = target;
                if (!imageModal) return;
                // reset previews
                if (imagePreview) { imagePreview.style.backgroundImage = ''; imagePreview.dataset.image = ''; }
                if (colorPreview) { colorPreview.style.backgroundColor = ''; colorPreview.dataset.color = ''; }
                // default to upload tab
                tabButtons.forEach(tb => tb.classList.remove('active'));
                tabPanels.forEach(p => p.classList.add('hidden'));
                if (tabButtons[0]) tabButtons[0].classList.add('active');
                if (tabPanels[0]) tabPanels[0].classList.remove('hidden');

                // populate from existing cover if any
                const cover = target.querySelector('.cover');
                if (cover) {
                    const comp = window.getComputedStyle(cover);
                    const inlineBg = cover.style.backgroundImage || comp.backgroundImage || '';
                    const url = extractUrlFromCss(inlineBg);
                    if (url) {
                        if (imagePreview) { imagePreview.style.backgroundImage = `url(${url})`; imagePreview.dataset.image = url; }
                        if (imageModeSelect) imageModeSelect.value = target.getAttribute('data-cover-mode') || 'cover';
                    } else {
                        const bc = comp.backgroundColor || '';
                        if (bc && bc !== 'rgba(0, 0, 0, 0)' && bc !== 'transparent') {
                            if (colorPreview) { colorPreview.style.backgroundColor = bc; colorPreview.dataset.color = bc; }
                            // switch to color tab
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

            function hideImageModal() {
                currentModalTarget = null;
                if (!imageModal) return;
                imageModal.classList.remove('open');
                imageModal.style.display = 'none';
                imageModal.setAttribute('aria-hidden', 'true');
            }

            // wire modal controls
            if (chooseFileBtn && imageFileInput) {
                chooseFileBtn.addEventListener('click', () => imageFileInput.click());
            }
            if (imageFileInput) {
                imageFileInput.addEventListener('change', (ev) => {
                    const f = ev.target.files && ev.target.files[0];
                    if (!f) return;
                    const reader = new FileReader();
                    reader.onload = (rEv) => {
                        if (imagePreview) { imagePreview.style.backgroundImage = `url(${rEv.target.result})`; imagePreview.dataset.image = rEv.target.result; }
                    };
                    reader.readAsDataURL(f);
                });
            }
            if (colorPicker) {
                colorPicker.addEventListener('input', (e) => {
                    const v = e.target.value;
                    if (colorPreview) { colorPreview.style.backgroundColor = v; colorPreview.dataset.color = v; }
                });
            }
            // tab switching
            tabButtons.forEach(tb => tb.addEventListener('click', () => {
                const t = tb.getAttribute('data-tab');
                tabButtons.forEach(b => b.classList.remove('active'));
                tb.classList.add('active');
                tabPanels.forEach(p => {
                    if (p.getAttribute('data-panel') === t) p.classList.remove('hidden'); else p.classList.add('hidden');
                });
            }));
            // apply/cancel
            if (applyCoverBtn) {
                applyCoverBtn.addEventListener('click', () => {
                    if (!currentModalTarget) { hideImageModal(); return; }
                    const coverEl = currentModalTarget.querySelector('.cover');
                    if (!coverEl) { hideImageModal(); return; }
                    const activeTab = document.querySelector('.image-modal-tabs .tab.active')?.getAttribute('data-tab') || 'upload';
                    if (activeTab === 'upload') {
                        const data = imagePreview?.dataset?.image || '';
                        if (!data) {
                            coverEl.style.backgroundImage = '';
                            coverEl.style.backgroundColor = '';
                            currentModalTarget.removeAttribute('data-cover');
                            currentModalTarget.removeAttribute('data-cover-mode');
                        } else {
                            coverEl.style.backgroundImage = `url(${data})`;
                            coverEl.style.backgroundSize = (imageModeSelect ? imageModeSelect.value : 'cover');
                            coverEl.style.backgroundPosition = 'center';
                            coverEl.style.backgroundColor = '';
                            currentModalTarget.setAttribute('data-cover', data);
                            currentModalTarget.setAttribute('data-cover-mode', imageModeSelect ? imageModeSelect.value : 'cover');
                        }
                    } else {
                        const color = colorPreview?.dataset?.color || colorPicker?.value || '#000000';
                        coverEl.style.backgroundImage = '';
                        coverEl.style.backgroundColor = color;
                        currentModalTarget.setAttribute('data-cover-color', color);
                        currentModalTarget.removeAttribute('data-cover');
                        currentModalTarget.removeAttribute('data-cover-mode');
                    }
                    hideImageModal();
                    hideMenu();
                });
            }
            if (cancelCoverBtn) { cancelCoverBtn.addEventListener('click', hideImageModal); }

            // Handle menu clicks
            moreMenu.addEventListener('click', (ev) => {
                ev.stopPropagation();
                const actionEl = ev.target.closest('.menu-item');
                if (!actionEl || !currentMenuTarget) return;
                const action = actionEl.classList.contains('rename') ? 'rename' : (actionEl.classList.contains('change-image') ? 'change-image' : 'delete');
                if (action === 'rename') {
                    const newTitle = prompt('Rename notebook', currentMenuTarget.querySelector('.item-title')?.textContent || currentMenuTarget.getAttribute('data-title') || '');
                    if (newTitle !== null) {
                        const titleEl = currentMenuTarget.querySelector('.item-title');
                        if (titleEl) titleEl.textContent = newTitle;
                        currentMenuTarget.setAttribute('data-title', newTitle);
                    }
                } else if (action === 'change-image') {
                    // open modal to allow upload or color pick
                    showImageModal(currentMenuTarget);
                } else if (action === 'delete') {
                    if (confirm('Delete this notebook?')) {
                        const parent = currentMenuTarget.parentElement;
                        if (parent) parent.removeChild(currentMenuTarget);
                    }
                }
                // ensure menu hidden
                hideMenu();
            });

            // Hide on outside click or escape
            document.addEventListener('click', (ev) => {
                if (!moreMenu.contains(ev.target)) hideMenu();
            });
            window.addEventListener('resize', hideMenu);
            document.addEventListener('keydown', (ev) => { if (ev.key === 'Escape') hideMenu(); });

            // Attach more-btn handlers for notebook items (delegation)
            const attachMoreHandlers = () => {
                document.querySelectorAll('.notebook-item .more-btn').forEach(btn => {
                    // avoid attaching multiple times
                    if (btn._hasMenuHandler) return;
                    btn._hasMenuHandler = true;
                    btn.addEventListener('click', (ev) => {
                        ev.stopPropagation();
                        const item = btn.closest('.notebook-item');
                        if (!item) return;
                        currentMenuTarget = item;
                        // show menu near button
                        moreMenu.style.display = 'block';
                        moreMenu.classList.remove('visible');
                        // position
                        const rect = btn.getBoundingClientRect();
                        // measure after display
                        const mw = moreMenu.offsetWidth || 160;
                        let left = rect.right - mw;
                        if (left < 8) left = rect.left;
                        if (left + mw > window.innerWidth - 8) left = window.innerWidth - mw - 8;
                        moreMenu.style.left = `${Math.max(8, left)}px`;
                        moreMenu.style.top = `${Math.min(window.innerHeight - 8, rect.bottom + 8)}px`;
                        moreMenu.classList.add('visible');
                    });
                });
            };

            // Initial attach and also re-attach when dynamic changes occur
            attachMoreHandlers();

            // MutationObserver to attach handlers for newly added items
            const gridObserver = new MutationObserver(() => attachMoreHandlers());
            document.querySelectorAll('.notebook-grid').forEach(g => gridObserver.observe(g, { childList: true, subtree: true }));

            // --- Show-All Scene Handling ---
            // Get all notebook items from dashboard sections (sample data)
            const getCommunityNotebooks = () => {
                const grid = document.querySelector('.community-grid');
                return grid ? Array.from(grid.querySelectorAll('.notebook-item')) : [];
            };
            const getMyNotebooks = () => {
                const grid = document.querySelector('.my-grid');
                return grid ? Array.from(grid.querySelectorAll('.notebook-item')) : [];
            };

            const showAllScene = document.getElementById('scene-showall');
            const showAllGrid = document.querySelector('.showall-grid');
            const closeShowallBtn = document.querySelector('.close-showall-btn');

            let currentShowAllTarget = null; // 'community' or 'my'

            const populateShowAllGrid = (target) => {
                if (!showAllGrid) return;
                showAllGrid.innerHTML = '';
                let items = target === 'community' ? getCommunityNotebooks() : getMyNotebooks();
                items.forEach(item => {
                    const clone = item.cloneNode(true);
                    // Reset handler flags on cloned items
                    clone.querySelectorAll('.more-btn').forEach(btn => {
                        btn._hasMenuHandler = false;
                    });
                    showAllGrid.appendChild(clone);
                });
                // Re-attach more handlers for cloned items
                attachMoreHandlers();
            };

            // Wire show-all buttons
            document.querySelectorAll('.show-all-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const target = btn.getAttribute('data-target');
                    currentShowAllTarget = target;
                    populateShowAllGrid(target);
                    // Transition to show-all scene
                    this.transitionTo('showall');
                });
            });

            // Wire close button in show-all scene
            if (closeShowallBtn) {
                closeShowallBtn.addEventListener('click', () => {
                    this.transitionTo('dashboard');
                });
            }

            // Wire controls in show-all scene (sort, search, view toggles)
            if (showAllScene) {
                const showAllContainer = showAllScene.querySelector('.dashboard-container');
                if (showAllContainer) {
                    // Sort switch in show-all scene
                    const showAllSortSwitch = showAllScene.querySelector('.sort-switch');
                    if (showAllSortSwitch) {
                        const showAllOptions = Array.from(showAllSortSwitch.querySelectorAll('.sort-option'));
                        const showAllThumb = showAllSortSwitch.querySelector('.sort-thumb');
                        const showAllPad = parseInt(getComputedStyle(showAllSortSwitch).getPropertyValue('--pad')) || 4;

                        const showAllRepositionThumb = (opt) => {
                            if (!showAllThumb || !opt) return;
                            const left = opt.offsetLeft + showAllPad;
                            const width = Math.max(24, opt.offsetWidth - showAllPad * 2);
                            showAllThumb.style.left = `${left}px`;
                            showAllThumb.style.width = `${width}px`;
                        };

                        const showAllSetThumb = (opt) => {
                            showAllOptions.forEach(o => o.classList.remove('active'));
                            opt.classList.add('active');
                            showAllRepositionThumb(opt);
                            setTimeout(() => showAllRepositionThumb(opt), 300);
                        };

                        showAllOptions.forEach(opt => {
                            opt.addEventListener('click', () => showAllSetThumb(opt));
                        });

                        const showAllInitial = showAllSortSwitch.querySelector('.sort-option.active') || showAllOptions[0];
                        if (showAllInitial) {
                            setTimeout(() => showAllRepositionThumb(showAllInitial), 20);
                            setTimeout(() => showAllRepositionThumb(showAllInitial), 340);
                        }

                        window.addEventListener('resize', () => {
                            const showAllActive = showAllSortSwitch.querySelector('.sort-option.active') || showAllOptions[0];
                            showAllRepositionThumb(showAllActive);
                        });
                    }

                    // Search toggle in show-all scene
                    const showAllSearchButton = showAllScene.querySelector('.search-button');
                    const showAllSearchInput = showAllScene.querySelector('.search-input');
                    if (showAllSearchButton && showAllSearchInput) {
                        showAllSearchButton.addEventListener('click', () => {
                            const isActive = showAllContainer.classList.toggle('search-active');
                            const icon = showAllSearchButton.querySelector('.material-icons');
                            if (isActive) {
                                icon.textContent = 'close';
                                setTimeout(() => showAllSearchInput.focus(), 200);
                            } else {
                                icon.textContent = 'search';
                                showAllSearchInput.value = '';
                            }
                        });
                    }

                    // View toggle in show-all scene
                    const showAllViewToggle = showAllScene.querySelector('.view-toggle');
                    if (showAllViewToggle && showAllContainer) {
                        const showAllViewOptions = Array.from(showAllViewToggle.querySelectorAll('.view-option'));
                        const showAllViewThumb = showAllViewToggle.querySelector('.view-thumb');
                        const showAllPadV = parseInt(getComputedStyle(showAllViewToggle).getPropertyValue('--pad')) || 4;

                        const showAllSetView = (view) => {
                            showAllViewOptions.forEach(o => o.classList.remove('active'));
                            const opt = showAllViewToggle.querySelector(`.view-option[data-view="${view}"]`);
                            if (opt) {
                                opt.classList.add('active');
                                showAllContainer.setAttribute('data-view', view);
                                if (opt && showAllViewThumb) {
                                    showAllViewThumb.style.left = `${opt.offsetLeft + showAllPadV}px`;
                                    showAllViewThumb.style.width = `${Math.max(24, opt.offsetWidth - showAllPadV * 2)}px`;
                                }
                                setTimeout(() => {
                                    if (opt && showAllViewThumb) {
                                        showAllViewThumb.style.left = `${opt.offsetLeft + showAllPadV}px`;
                                        showAllViewThumb.style.width = `${Math.max(24, opt.offsetWidth - showAllPadV * 2)}px`;
                                    }
                                }, 300);
                            } else {
                                showAllContainer.setAttribute('data-view', view);
                            }
                        };

                        showAllViewOptions.forEach(o => {
                            o.addEventListener('click', () => showAllSetView(o.getAttribute('data-view')));
                        });

                        setTimeout(() => showAllSetView('grid'), 20);

                        window.addEventListener('resize', () => {
                            const showAllActive = showAllViewToggle.querySelector('.view-option.active') || showAllViewOptions[0];
                            if (showAllActive && showAllViewThumb) {
                                showAllViewThumb.style.left = `${showAllActive.offsetLeft + showAllPadV}px`;
                                showAllViewThumb.style.width = `${Math.max(24, showAllActive.offsetWidth - showAllPadV * 2)}px`;
                            }
                        });
                    }
                }
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
