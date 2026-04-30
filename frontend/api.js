// API Configuration and Authentication Helper
const API = {
    // Backend base URL - adjust this if backend runs on different host/port
    BASE_URL: 'http://localhost:8000',

    // Get stored access token
    getToken: () => {
        return localStorage.getItem('accessToken');
    },

    // Store access token
    setToken: (token) => {
        localStorage.setItem('accessToken', token);
    },

    // Clear stored token (on logout)
    clearToken: () => {
        localStorage.removeItem('accessToken');
    },

    // Make authenticated API request
    async request(endpoint, options = {}) {
        const url = `${API.BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Add authorization header if token exists
        const token = API.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            // Handle response
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const errorMsg = errorData.detail || `API Error: ${response.status}`;
                throw new Error(errorMsg);
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    },

    // Sign Up
    async signup(username, email, password) {
        const data = await API.request('/signup', {
            method: 'POST',
            body: JSON.stringify({
                username,
                email,
                password
            })
        });
        // Store token from response
        if (data.access_token) {
            API.setToken(data.access_token);
        }
        return data;
    },

    // Sign In
    async login(email, password) {
        const data = await API.request('/login', {
            method: 'POST',
            body: JSON.stringify({
                email,
                password
            })
        });
        // Store token from response
        if (data.access_token) {
            API.setToken(data.access_token);
        }
        return data;
    },

    // Change Password
    async changePassword(currentPassword, newPassword) {
        const data = await API.request('/change-password', {
            method: 'POST',
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });
        return data;
    },

    // Check if user is authenticated (has valid token)
    isAuthenticated: () => {
        return Boolean(API.getToken());
    }
};
