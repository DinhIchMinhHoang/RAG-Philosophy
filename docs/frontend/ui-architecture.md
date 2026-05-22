# UI Architecture

## Overview

The frontend is a vanilla JavaScript single-page application (SPA) with scene-based navigation. It uses no frameworks, relying on native DOM manipulation and CSS transitions. Built as **ES Modules** with a modular directory structure.

## File Structure

```
frontend/
├── index.html              # Entry point + all scene HTML markup
├── package.json             # {"type": "module"} — enables ES Modules
├── src/
│   ├── main.js             # Entry: canvas setup, blob init, animation loop
│   ├── App.js              # App class: wires TransitionManager to all scene init methods
│   ├── api/
│   │   ├── client.js       # BASE_URL, getToken, setToken, clearToken, isAuthenticated, request
│   │   ├── auth.js         # signup, login, changePassword
│   │   ├── rag.js          # uploadDocument, chatStream (SSE), listSources
│   │   └── index.js        # Barrel: re-exports all api exports
│   ├── animations/
│   │   ├── Blob.js         # MorphingBlob class + advancePalette
│   │   ├── DotGrid.js      # Dot grid mouse-tracking effect
│   │   ├── CanvasManager.js # Manages gradientCanvas + dotCanvas, exports shared refs
│   │   ├── Transitions.js  # TransitionManager class: scene fades, auth guards, chat mode
│   │   └── index.js        # Barrel
│   ├── state/
│   │   ├── store.js        # User state with localStorage persistence (STORAGE_KEY='currentUser')
│   │   ├── scenes.js       # scenes const, getCurrentScene, getSceneElement, showScene, hideScene
│   │   └── index.js        # Barrel
│   ├── ui/
│   │   ├── components/
│   │   │   └── Modal.js    # showImageModal, hideImageModal (notebook cover editor)
│   │   ├── scenes/
│   │   │   ├── LandingScene.js  # Landing page: logo, blob canvas, auth buttons
│   │   │   ├── AuthScene.js      # Sign up, Sign in, Account forms with validation
│   │   │   ├── DashboardScene.js # Notebook grid, sort/view toggles, more menu, show-all
│   │   │   └── ChatScene.js     # SSE chat, panel resizer, source viewer, citations, markdown/KaTeX
│   │   └── index.js        # Barrel
│   └── utils/
│       ├── logger.js       # Browser console logger with module prefix
│       ├── helpers.js      # Utility helpers
│       └── index.js        # Barrel
├── styles/
│   ├── variables.css       # CSS custom properties (colors, spacing, typography, etc.)
│   ├── reset.css           # CSS reset
│   ├── base.css            # Base element styles
│   ├── layout.css          # Layout utilities
│   ├── components.css      # Shared component styles (buttons, forms, modals, scenes)
│   ├── scenes.css          # Scene-specific styles
│   └── main.css            # Entry point: imports all above
└── assets/
    └── logo.svg            # Lumina logo
```

**Entry point**: `index.html` → `<script type="module" src="src/main.js">`
**CSS entry**: `index.html` → `<link rel="stylesheet" href="styles/main.css">`

## Scene System

The app uses a scene-based architecture with CSS visibility transitions. All scene HTML lives in `index.html`; JS only wires behavior.

### Scenes

| Scene | Description |
|-------|-------------|
| `landing` | Welcome screen with animated morphing blobs |
| `signin` | Email/password login form |
| `signup` | Registration form |
| `dashboard` | User's notebooks/documents with grid/list toggle |
| `showall` | Full-screen view of all notebooks (community or my) |
| `account` | User profile management (name, bio, password change, delete) |
| `chat` | RAG-powered Q&A interface with sources panel and source viewer |

### Scene Transition

```javascript
// src/animations/Transitions.js
export class TransitionManager {
    constructor() {
        this.currentScene = 'landing';
        this.isTransitioning = false;
        this.transitionToken = 0;
        this.transitionDuration = 150;
    }

    transitionTo(targetScene) {
        // 1. Guard: no double transitions
        if (this.isTransitioning || targetScene === this.currentScene) return;

        // 2. Auth guard: redirect to signin if accessing account unauthenticated
        if (targetScene === 'account' && !isAuthenticated()) targetScene = 'signin';

        // 3. Increment transition token (cancels stale callbacks)
        const transitionToken = ++this.transitionToken;
        const isCurrentTransition = () => transitionToken === this.transitionToken;
        this.isTransitioning = true;

        // 4. Toggle chat-active body class (hides navbar in chat)
        if (targetScene === 'chat') document.body.classList.add('chat-active');
        else document.body.classList.remove('chat-active');

        // 5. Fade out current scene
        this.fadeOutScene(this.currentScene, () => {
            if (!isCurrentTransition()) return;

            // 6. Hide all scenes
            document.querySelectorAll('.scene').forEach(scene => {
                scene.style.display = 'none';
            });

            // 7. Update current scene
            this.currentScene = targetScene;

            // 8. Fade in new scene
            this.fadeInScene(targetScene, () => {
                if (isCurrentTransition()) this.isTransitioning = false;
            });
        });
    }
}
```

## Visual Effects

### Morphing Blobs (src/animations/Blob.js)

- **Technology**: HTML5 Canvas + requestAnimationFrame
- **Implementation**: Custom `MorphingBlob` class with:
  - 20-point polygon with quadratic curves
  - Movement types: lavaLamp (2 variants), orbital, sine
  - Color palette: Purple → Cyan → Blue gradient, cycles over time
  - Blur filter: 50px for glassy effect
  - 10 blob instances spawned in `main.js`

### Dot Grid Overlay (src/animations/DotGrid.js)

- **Technology**: Secondary `<canvas>` overlay (z-index 15, pointer-events none)
- **Interaction**: Mouse spotlight effect
- **Physics**: Dots attracted to cursor, spring back to origin
- **Configuration**: 15px spacing, 0.75px radius, 0.25 base alpha, 300px attraction radius

## Component Structure

### Chat Interface (scene-chat)

```
.scene-chat/
├── .chat-shell/
│   ├── .chat-topbar/        # Back button, notebook title, share/tune buttons
│   ├── .chat-layout/         # Three-panel layout
│   │   ├── .panel-left/      # Sources panel: file drop, source list, collapse rail
│   │   ├── .chat-resizer/    # Draggable resize handle (left)
│   │   ├── .panel-center/    # Conversation: thread + input form
│   │   ├── .chat-resizer/    # Draggable resize handle (right)
│   │   └── .panel-right/     # Source Viewer: same-origin /file iframe with unsupported-file fallback
│   └── .image-modal/         # Notebook cover image/color picker (global modal)
```

The Source Viewer opens original stored files through `/api/documents/{document_id}/file?token=...`.
PDF citations append `#page=N`; non-PDF browser-native files open without a page fragment, and unsupported MIME types show an inline fallback with an open/download action.

### Dashboard (scene-dashboard)

```
.scene-dashboard/
├── .dashboard-container/
│   ├── .dashboard-top/       # Sort switch, create button, search, view toggle
│   └── .sections/
│       ├── .community-section/  # Community notebooks grid + show-all
│       └── .my-section/         # User's notebooks grid + show-all
└── .image-modal/             # Cover image/color picker (shared global modal)
```

## State Management

### User State (src/state/store.js)

```javascript
// src/state/store.js
const STORAGE_KEY = 'currentUser';
const defaultUser = { username: '', email: '', displayName: '', bio: '' };

export const store = {
    _user: loadUser(),  // loaded from localStorage on init

    get user() { return this._user; },
    setUser(data) { /* persist to localStorage */ },
    clearUser() { /* reset to defaults, clear localStorage */ },
};
```

### Authentication State (src/api/client.js)

```javascript
// src/api/client.js
isAuthenticated()   // Returns Boolean from localStorage token
getToken()          // Gets JWT from localStorage
setToken(token)      // Stores JWT
clearToken()         // Removes JWT
```

## Event Handling

### Form Submission (src/ui/scenes/AuthScene.js)

```javascript
// src/ui/scenes/AuthScene.js — Sign in example (within initAuthScene)
signInForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    await login(email, password);
    transitionManager.transitionTo('dashboard');
});
```

### Scene Navigation

```javascript
// From any scene handler
const signUpBtn = document.querySelector('[data-scene="signup"]');
signUpBtn?.addEventListener('click', () => transitionManager.transitionTo('signup'));
```

## CSS Patterns

### Scene Visibility

```css
.scene { display: none; }  /* Hidden by default — controlled via inline style by JS */
```

### Transitions

```css
.scene > * {
    --anim-y: 0px;
    --anim-opacity: 1;
    transform: translateY(var(--anim-y));
    opacity: var(--anim-opacity);
    transition: transform 150ms, opacity 150ms;
}
```

## API Integration

### Chat Streaming (src/api/rag.js)

```javascript
// src/api/rag.js
const controller = chatStream(message, {
    onToken: (token) => appendToDisplay(token),
    onDone: () => enableInput(),
    onError: (err) => showError(err),
});
// To abort: controller.abort()
```

### Document Upload (src/api/rag.js)

```javascript
// src/api/rag.js
await uploadDocument(fileInput.files[0]);
```

### Authentication (src/api/auth.js)

```javascript
// src/api/auth.js
await signup(username, email, password);  // auto-sets token on success
await login(email, password);             // auto-sets token on success
```
