export function initLandingScene(transitionManager) {
    const signUpBtn = document.querySelector('[data-scene="signup"]');
    if (signUpBtn) signUpBtn.addEventListener('click', () => transitionManager.transitionTo('signup'));

    const signInBtn = document.querySelector('[data-scene="signin"]');
    if (signInBtn) signInBtn.addEventListener('click', () => transitionManager.transitionTo('signin'));
}
