# UI Architecture

## Overview

The frontend is a vanilla JavaScript single-page application (SPA) with scene-based navigation. It uses no frameworks, relying on native DOM manipulation and CSS transitions.

## File Structure

```
frontend/
├── index.html       # Main HTML with inline CSS and scene markup
├── script.js        # Canvas animations (morphing blobs, dot grid)
├── api.js           # API client (authentication, RAG operations)
└── transitions.js   # Scene transition manager
```

## Scene System

The app uses a scene-based architecture with CSS visibility transitions:

### Scenes

| Scene | Description |
|-------|-------------|
| `landing` | Welcome screen with animated blobs |
| `signin` | Email/password login form |
| `signup` | Registration form |
| `dashboard` | User's notebooks/documents |
| `account` | User profile management |
| `chat` | RAG-powered Q&A interface |

### Scene Transition

```javascript
// frontend/transitions.js
class TransitionManager {
    transitionTo(targetScene) {
        // 1. Check if already transitioning
        if (this.isTransitioning) return;

        // 2. Fade out current scene
        this.fadeOutScene(this.currentScene, () => {
            // 3. Hide all scenes
            document.querySelectorAll('.scene').forEach(scene => {
                scene.style.display = 'none';
            });

            // 4. Update current scene
            this.currentScene = targetScene;

            // 5. Fade in new scene
            this.fadeInScene(targetScene, finish);
        });
    }
}
```

## Visual Effects

### Morphing Blobs (script.js)

- **Technology**: HTML5 Canvas + requestAnimationFrame
- **Implementation**: Custom `MorphingBlob` class with:
  - 20-point polygon with quadratic curves
  - Movement types: lavaLamp, orbital, sine, bounce, spiral
  - Color palette: Purple → Cyan → Blue gradient
  - Blur filter: 50px for glassy effect

### Dot Grid Overlay (script.js)

- **Technology**: Secondary canvas with physics simulation
- **Interaction**: Mouse spotlight effect
- **Behavior**: Dots attracted to cursor, spring back to origin
- **Configuration**: 15px spacing, 0.75px radius dots

## Component Structure

### Chat Interface

```
scene-chat/
├── chat-sidebar/         # Source documents list
├── chat-messages/        # Message display area
├── chat-input/           # Text input + submit
└── chat-title/           # Current notebook title
```

### Dashboard

```
scene-dashboard/
├── dashboard-navbar/    # Search, view toggle, create
├── dashboard-container/  # Grid/list view of notebooks
└── modal (imageModal)    # Cover image/color picker
```

## State Management

### User State

```javascript
// transitions.js
this.currentUser = JSON.parse(localStorage.getItem('currentUser')) || {
    username: '',
    email: '',
    displayName: '',
    bio: ''
};
```

### Authentication State

```javascript
// api.js
API.isAuthenticated() // Returns Boolean from localStorage token

API.getToken()        // Gets JWT from localStorage
API.setToken(token)   // Stores JWT
API.clearToken()      // Removes JWT
```

## Event Handling

### Form Submission

```javascript
// transitions.js - Sign in example
signInForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    await API.login(email, password);
    this.transitionTo('dashboard');
});
```

### Scene Navigation

```javascript
// transitions.js
const signUpBtn = document.querySelector('[data-scene="signup"]');
signUpBtn.addEventListener('click', () => this.transitionTo('signup'));
```

## CSS Patterns

### Scene Visibility

```css
.scene {
    display: none;  /* Hidden by default */
}

.scene.active {
    display: flex;
}
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

### Chat Streaming

```javascript
// api.js
const controller = API.chatStream(message, {
    onToken: (token) => appendToDisplay(token),
    onDone: () => enableInput(),
    onError: (err) => showError(err),
});
```

### Document Upload

```javascript
// api.js
await API.uploadDocument(fileInput.files[0]);
```