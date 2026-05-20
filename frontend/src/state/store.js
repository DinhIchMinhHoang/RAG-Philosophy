const STORAGE_KEY = 'currentUser';

const defaultUser = { username: '', email: '', displayName: '', bio: '', isAdmin: false };

function loadUser() {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || { ...defaultUser };
}

export const store = {
    _user: loadUser(),

    get user() { return this._user; },

    setUser(data) {
        this._user = { ...data };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this._user));
    },

    clearUser() {
        this._user = { ...defaultUser };
        localStorage.removeItem(STORAGE_KEY);
    },

    getUsername: () => store._user.username,
    getEmail: () => store._user.email,
    getDisplayName: () => store._user.displayName,
    getBio: () => store._user.bio,
    getIsAdmin: () => Boolean(store._user.isAdmin),
};
