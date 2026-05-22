import { isAuthenticated } from '../../api/client.js';

function updateLandingButtons() {
    const startBtn = document.querySelector('[data-scene="start"]');
    const signUpBtn = document.querySelector('[data-scene="signup"]');
    const signInBtn = document.querySelector('[data-scene="signin"]');
    const authed = isAuthenticated();

    if (startBtn) startBtn.style.display = authed ? '' : 'none';
    if (signUpBtn) signUpBtn.style.display = authed ? 'none' : '';
    if (signInBtn) signInBtn.style.display = authed ? 'none' : '';
}

export function initLandingScene(transitionManager) {
    const signUpBtn = document.querySelector('[data-scene="signup"]');
    if (signUpBtn) signUpBtn.addEventListener('click', () => transitionManager.transitionTo('signup'));

    const signInBtn = document.querySelector('[data-scene="signin"]');
    if (signInBtn) signInBtn.addEventListener('click', () => transitionManager.transitionTo('signin'));

    const startBtn = document.querySelector('[data-scene="start"]');
    if (startBtn) startBtn.addEventListener('click', () => transitionManager.transitionTo('dashboard'));

    updateLandingButtons();
    document.addEventListener('auth:changed', updateLandingButtons);
}
