export const scenes = {
    LANDING: 'landing',
    SIGNUP: 'signup',
    SIGNIN: 'signin',
    DASHBOARD: 'dashboard',
    ACCOUNT: 'account',
    SHOWALL: 'showall',
    CHAT: 'chat',
    ADMIN: 'admin',
};

export function getCurrentScene() {
    return document.querySelector('.scene:not([style*="display: none"])')?.id?.replace('scene-', '') || scenes.LANDING;
}

export function getSceneElement(name) {
    return document.getElementById(`scene-${name}`);
}

export function showScene(name) {
    document.querySelectorAll('.scene').forEach(s => s.style.display = 'none');
    const el = getSceneElement(name);
    if (el) el.style.display = 'flex';
}

export function hideScene(name) {
    const el = getSceneElement(name);
    if (el) el.style.display = 'none';
}

export function hideAllScenes() {
    document.querySelectorAll('.scene').forEach(s => s.style.display = 'none');
}
