import { request, setToken } from './client.js';

export async function signup(username, email, password) {
    const data = await request('/signup', {
        method: 'POST',
        body: JSON.stringify({ username, email, password })
    });
    if (data.access_token) setToken(data.access_token);
    return data;
}

export async function login(email, password) {
    const data = await request('/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
    });
    if (data.access_token) setToken(data.access_token);
    return data;
}

export async function changePassword(currentPassword, newPassword) {
    return await request('/change-password', {
        method: 'POST',
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword })
    });
}

export async function forgotPassword(email) {
    return await request('/password/forgot', {
        method: 'POST',
        body: JSON.stringify({ email })
    });
}

export async function verifyPasswordCode(email, code) {
    return await request('/password/verify', {
        method: 'POST',
        body: JSON.stringify({ email, code })
    });
}

export async function resetPassword(email, code, newPassword) {
    return await request('/password/reset', {
        method: 'POST',
        body: JSON.stringify({ email, code, new_password: newPassword })
    });
}
