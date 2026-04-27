// Transition Manager
class TransitionManager {
    constructor() {
        this.currentScene = 'landing';
        this.isTransitioning = false;
        this.transitionDuration = 500; // milliseconds
    }

    /**
     * Transition to a new scene with fade out/in effects
     * @param {string} targetScene - The scene to transition to
     */
    transitionTo(targetScene) {
        if (this.isTransitioning || targetScene === this.currentScene) return;

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
    }
}

// Create global transition manager instance
const transitionManager = new TransitionManager();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    transitionManager.initialize();
});
