import { login, signup, changePassword, forgotPassword, verifyPasswordCode, resetPassword, getMe, isAuthenticated, clearToken } from '../../api/index.js';
import { store } from '../../state/store.js';

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
    setupEmailValidation('#scene-forgot .auth-form');

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
    document.querySelectorAll('[data-back-to="signin"]').forEach(btn => {
        btn.addEventListener('click', () => transitionManager.transitionTo('signin'));
    });
    document.querySelectorAll('[data-back-to="forgot"]').forEach(btn => {
        btn.addEventListener('click', () => {
            pendingResetEmail = '';
            pendingResetCode = '';
            transitionManager.transitionTo('forgot');
        });
    });

    const signInScene = document.getElementById('scene-signin');
    if (signInScene) signInScene.addEventListener('click', (e) => { if (e.target === signInScene) transitionManager.transitionTo('landing'); });

    const signUpScene = document.getElementById('scene-signup');
    if (signUpScene) signUpScene.addEventListener('click', (e) => { if (e.target === signUpScene) transitionManager.transitionTo('landing'); });

    const accountScene = document.getElementById('scene-account');
    if (accountScene) accountScene.addEventListener('click', (e) => { if (e.target === accountScene) transitionManager.transitionTo('dashboard'); });

    const forgotScene = document.getElementById('scene-forgot');
    const verifyScene = document.getElementById('scene-verify');
    const resetScene = document.getElementById('scene-reset');

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
                const me = await getMe();
                const usernameGuess = email.split('@')[0] || 'user';
                store.setUser({ id: me.id, username: me.username || usernameGuess, email, displayName: me.username || usernameGuess, bio: '', isAdmin: me.is_admin });
                transitionManager.updateAuthUI();
                document.dispatchEvent(new CustomEvent('auth:changed'));
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
                const me = await getMe();
                store.setUser({ id: me.id, username, email, displayName: username, bio: '', isAdmin: me.is_admin });
                transitionManager.updateAuthUI();
                document.dispatchEvent(new CustomEvent('auth:changed'));
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
                document.dispatchEvent(new CustomEvent('auth:changed'));
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

    document.querySelectorAll('[data-action="forgot-password"]').forEach(btn => {
        btn.addEventListener('click', () => transitionManager.transitionTo('forgot'));
    });

    let pendingResetEmail = '';
    let pendingResetCode = '';

    const forgotForm = document.getElementById('forgot-form');
    if (forgotForm && forgotScene) {
        forgotForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearError(forgotScene);
            const success = forgotScene.querySelector('.form-success');
            if (success) success.style.display = 'none';
            const email = forgotForm.querySelector('.email-input')?.value.trim() || '';
            if (!email) { showError(forgotScene, 'Please enter your email'); return; }
            if (!isValidEmail(email)) { showError(forgotScene, 'Please enter a valid email address'); return; }
            try {
                await forgotPassword(email);
                pendingResetEmail = email;
                pendingResetCode = '';
                const codeBoxes = Array.from(document.querySelectorAll('#verify-form .code-box'));
                codeBoxes.forEach((box) => { box.value = ''; });
                showSuccess(forgotScene, 'Code sent. Check your email.');
                transitionManager.transitionTo('verify');
            } catch (err) {
                showError(forgotScene, err.message);
            }
        });
    }

    const verifyForm = document.getElementById('verify-form');
    if (verifyForm && verifyScene) {
        const codeBoxes = Array.from(verifyForm.querySelectorAll('.code-box'));
        const focusBox = (idx) => { if (codeBoxes[idx]) codeBoxes[idx].focus(); };

        codeBoxes.forEach((box, idx) => {
            box.addEventListener('input', () => {
                box.value = box.value.replace(/\D/g, '').slice(0, 1);
                if (box.value && idx < codeBoxes.length - 1) focusBox(idx + 1);
            });
            box.addEventListener('keydown', (ev) => {
                if (ev.key === 'Backspace' && !box.value && idx > 0) focusBox(idx - 1);
            });
        });

        verifyForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearError(verifyScene);
            const success = verifyScene.querySelector('.form-success');
            if (success) success.style.display = 'none';
            const code = codeBoxes.map(b => b.value.trim()).join('');
            if (!pendingResetEmail) { showError(verifyScene, 'Missing email. Please restart.'); return; }
            if (code.length !== 4) { showError(verifyScene, 'Enter the 4-digit code'); return; }
            try {
                await verifyPasswordCode(pendingResetEmail, code);
                pendingResetCode = code;
                showSuccess(verifyScene, 'Code verified.');
                transitionManager.transitionTo('reset');
            } catch (err) {
                showError(verifyScene, err.message);
                codeBoxes.forEach((box) => { box.value = ''; });
                focusBox(0);
            }
        });
    }

    const resetForm = document.getElementById('reset-form');
    if (resetForm && resetScene) {
        resetForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearError(resetScene);
            const success = resetScene.querySelector('.form-success');
            if (success) success.style.display = 'none';
            const inputs = resetForm.querySelectorAll('input[type="password"]');
            const newPassword = inputs[0]?.value || '';
            const confirmPassword = inputs[1]?.value || '';
            if (!newPassword || !confirmPassword) { showError(resetScene, 'Please fill in all password fields'); return; }
            if (newPassword !== confirmPassword) { showError(resetScene, 'Passwords do not match'); return; }
            if (newPassword.length < 6) { showError(resetScene, 'Password must be at least 6 characters'); return; }
            if (!pendingResetEmail || !pendingResetCode) { showError(resetScene, 'Missing verification. Please restart.'); return; }
            try {
                await resetPassword(pendingResetEmail, pendingResetCode, newPassword);
                pendingResetCode = '';
                pendingResetEmail = '';
                inputs.forEach((input) => { input.value = ''; });
                showSuccess(resetScene, 'Password updated.');
                transitionManager.transitionTo('signin');
            } catch (err) {
                showError(resetScene, err.message);
            }
        });
    }
}
