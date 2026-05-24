const browserBaseUrl =
    typeof window !== 'undefined' && window.location?.hostname === '127.0.0.1' && window.location?.port === '5500'
        ? 'http://127.0.0.1:8000/api'
        : '/api';

export const BASE_URL =
    typeof window !== 'undefined' && window.LUMINA_API_BASE
        ? window.LUMINA_API_BASE
        : browserBaseUrl;

export function getToken() {
    return localStorage.getItem('accessToken');
}

export function setToken(token) {
    localStorage.setItem('accessToken', token);
}

export function clearToken() {
    localStorage.removeItem('accessToken');
}

export function isAuthenticated() {
    return Boolean(getToken());
}

export async function request(endpoint, options = {}) {
    const url = `${BASE_URL}${endpoint}`;
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    try {
        const response = await fetch(url, { ...options, headers });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `API Error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`API request failed: ${endpoint}`, error);
        throw error;
    }
}
