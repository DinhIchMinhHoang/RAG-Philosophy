import assert from 'node:assert/strict';

globalThis.localStorage = {
    getItem: () => null,
};

globalThis.CustomEvent = class {
    constructor(type, init = {}) {
        this.type = type;
        this.detail = init.detail;
    }
};

const listeners = new Map();
globalThis.document = {
    body: {
        classList: {
            add() {},
            remove() {},
        },
    },
    activeElement: null,
    addEventListener(type, handler) {
        listeners.set(type, [...(listeners.get(type) || []), handler]);
    },
    dispatchEvent(event) {
        for (const handler of listeners.get(event.type) || []) handler(event);
        return true;
    },
    getElementById: () => null,
    querySelectorAll: () => [],
};

const { TransitionManager } = await import('../src/animations/Transitions.js');

let resetEvents = 0;
document.addEventListener('chat:notebookLeft', () => {
    resetEvents += 1;
});

const manager = new TransitionManager();
manager.currentScene = 'chat';
manager.fadeOutScene = (_scene, callback) => callback();
manager.fadeNavbarIn = (callback) => callback();
manager.fadeNavbarOut = (callback) => callback();
manager.fadeInScene = (_scene, callback) => callback();

manager.transitionTo('dashboard');

assert.equal(resetEvents, 1);
