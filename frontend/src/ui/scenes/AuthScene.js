import { login, signup, changePassword, isAuthenticated, clearToken } from '../../api/index.js';
import { store } from '../../state/store.js';
import { isAdminEmail } from '../../utils/helpers.js';

const isValidEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

function setupEmailValidation(formSelector) {
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
            if (errorMsg) { errorMsg.textContent = 'Please enter a valid email address'; errorMsg.classList.add('show'); }
            return false;
        }
        emailInput.classList.remove('email-error');
        if (errorMsg) errorMsg.classList.remove('show');
        return true;
    };
    emailInput.addEventListener('input', validateEmail);
    emailInput.addEventListener('blur', validateEmail);
}

function showError(scene, msg) {
    const err = scene.querySelector('.form-error');
    if (err) { err.textContent = msg; err.style.display = 'block'; }
}
function clearError(scene) {
    const err = scene.querySelector('.form-error');
    if (err) { err.textContent = ''; err.style.display = 'none'; }
}
function showSuccess(scene, msg) {
    const succ = scene.querySelector('.form-success');
    if (succ) { succ.textContent = msg; succ.style.display = 'block'; setTimeout(() => { succ.style.display = 'none'; }, 3000); }
}

export function initAuthScene(transitionManager) {
    setupEmailValidation('#scene-signup .auth-form');
    setupEmailValidation('#scene-signin .auth-form');

    const accountForm = document.querySelector('#scene-account .account-form');
    if (accountForm) {
        const accountEmail = accountForm.querySelector('#account-email');
        if (accountEmail) {
            accountEmail.classList.add('email-input');
            const errDiv = document.createElement('div');
            errDiv.className = 'form-field-error';
            accountEmail.parentElement.appendChild(errDiv);
            setupEmailValidation('#scene-account .account-form');
        }
    }

    document.querySelectorAll('[data-back-to="landing"]').forEach(btn => {
        btn.addEventListener('click', () => transitionManager.transitionTo('landing'));
    });

    const signInScene = document.getElementById('scene-signin');
    if (signInScene) signInScene.addEventListener('click', (e) => { if (e.target === signInScene) transitionManager.transitionTo('landing'); });

    const signUpScene = document.getElementById('scene-signup');
    if (signUpScene) signUpScene.addEventListener('click', (e) => { if (e.target === signUpScene) transitionManager.transitionTo('landing'); });

    const accountScene = document.getElementById('scene-account');
    if (accountScene) accountScene.addEventListener('click', (e) => { if (e.target === accountScene) transitionManager.transitionTo('dashboard'); });

    const signInForm = document.querySelector('#scene-signin .auth-form');
    if (signInForm) {
        signInForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearError(signInScene);
            const email = signInForm.querySelector('.email-input')?.value.trim() || '';
            const password = signInForm.querySelector('input[type="password"]')?.value || '';

            if (!email || !password) { showError(signInScene, 'Please enter email and password'); return; }
            if (!isValidEmail(email)) { showError(signInScene, 'Please enter a valid email address'); return; }

            try {
                await login(email, password);
                const usernameGuess = email.split('@')[0] || 'user';
                store.setUser({ username: usernameGuess, email, displayName: usernameGuess, bio: '', isAdmin: isAdminEmail(email) });
                transitionManager.updateAuthUI();
                signInForm.reset();
                transitionManager.transitionTo('dashboard');
            } catch (err) {
                showError(signInScene, err.message);
                if (signInForm.querySelector('input[type="password"]')) signInForm.querySelector('input[type="password"]').value = '';
            }
        });
    }

    const signUpForm = document.querySelector('#scene-signup .auth-form');
    if (signUpForm) {
        signUpForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearError(signUpScene);
            const usernameInput = signUpForm.querySelector('input[placeholder="User name"]') || signUpForm.querySelector('input:not(.email-input)[type="text"]');
            const email = signUpForm.querySelector('.email-input')?.value.trim() || '';
            const pwInputs = signUpForm.querySelectorAll('input[type="password"]');
            const password = pwInputs[0]?.value || '';
            const confirmPassword = pwInputs[1]?.value || '';
            const username = usernameInput?.value.trim() || '';

            if (!username || !email || !password || !confirmPassword) { showError(signUpScene, 'Please fill in all fields'); return; }
            if (!isValidEmail(email)) { showError(signUpScene, 'Please enter a valid email address'); return; }
            if (password !== confirmPassword) { showError(signUpScene, 'Passwords do not match'); return; }
            if (password.length < 6) { showError(signUpScene, 'Password must be at least 6 characters'); return; }

            try {
                await signup(username, email, password);
                store.setUser({ username, email, displayName: username, bio: '', isAdmin: isAdminEmail(email) });
                transitionManager.updateAuthUI();
                signUpForm.reset();
                transitionManager.transitionTo('dashboard');
            } catch (err) {
                showError(signUpScene, err.message);
                pwInputs.forEach(input => input.value = '');
            }
        });
    }

    if (accountScene) {
        const accountForm = accountScene.querySelector('.account-form');
        const logoutBtn = accountScene.querySelector('.logout-button');
        const deleteBtn = accountScene.querySelector('.delete-account-button');
        const cancelBtn = accountScene.querySelector('[data-back-to="dashboard"]');
        const changePwdBtn = accountScene.querySelector('.change-password-button');
        const adminEntry = accountScene.querySelector('.admin-entry');
        const adminBtn = accountScene.querySelector('.admin-console-button');

        const fieldMap = {
            '#account-username': 'username',
            '#account-email': 'email',
            '#account-displayname': 'displayName',
            '#account-bio': 'bio',
        };
        Object.entries(fieldMap).forEach(([sel, key]) => {
            const el = accountScene.querySelector(sel);
            if (el) el.value = store.user[key] || '';
        });

        if (adminEntry) {
            adminEntry.style.display = store.getIsAdmin() ? 'block' : 'none';
        }

        if (adminBtn) {
            adminBtn.addEventListener('click', () => {
                transitionManager.transitionTo('admin');
            });
        }

        if (accountForm) {
            accountForm.addEventListener('submit', (e) => {
                e.preventDefault();
                store.setUser({
                    username: accountScene.querySelector('#account-username')?.value.trim() || '',
                    email: accountScene.querySelector('#account-email')?.value.trim() || '',
                    displayName: accountScene.querySelector('#account-displayname')?.value.trim() || '',
                    bio: accountScene.querySelector('#account-bio')?.value.trim() || '',
                    isAdmin: store.user.isAdmin,
                });
                transitionManager.updateAuthUI();
                transitionManager.transitionTo('dashboard');
            });
        }

        if (cancelBtn) cancelBtn.addEventListener('click', () => transitionManager.transitionTo('dashboard'));

        if (changePwdBtn) {
            changePwdBtn.addEventListener('click', async () => {
                clearError(accountScene);
                const succ = accountScene.querySelector('.form-success');
                if (succ) succ.style.display = 'none';
                const curr = accountScene.querySelector('#current-password')?.value || '';
                const newP = accountScene.querySelector('#new-password')?.value || '';
                const confirm = accountScene.querySelector('#confirm-new-password')?.value || '';
                if (!curr || !newP || !confirm) { showError(accountScene, 'Please fill in all password fields'); return; }
                if (newP !== confirm) { showError(accountScene, 'New passwords do not match'); return; }
                if (newP.length < 6) { showError(accountScene, 'New password must be at least 6 characters'); return; }
                try {
                    await changePassword(curr, newP);
                    showSuccess(accountScene, 'Password changed successfully!');
                    ['#current-password', '#new-password', '#confirm-new-password'].forEach(s => { const el = accountScene.querySelector(s); if (el) el.value = ''; });
                } catch (err) {
                    showError(accountScene, err.message);
                    const el = accountScene.querySelector('#current-password');
                    if (el) el.value = '';
                }
            });
        }

        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                clearToken();
                store.clearUser();
                transitionManager.updateAuthUI();
                transitionManager.transitionTo('landing');
            });
        }

        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => {
                if (confirm('Delete your account? This cannot be undone.')) {
                    store.clearUser();
                    transitionManager.updateAuthUI();
                    alert('Account deleted');
                    transitionManager.transitionTo('landing');
                }
            });
        }
    }
}
