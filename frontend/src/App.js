import { TransitionManager } from './animations/Transitions.js';
import { store } from './state/store.js';
import { initLandingScene } from './ui/scenes/LandingScene.js';
import { initAuthScene } from './ui/scenes/AuthScene.js';
import { initDashboardScene } from './ui/scenes/DashboardScene.js';
import { initChatScene } from './ui/scenes/ChatScene.js';
import { initAdminScene } from './ui/scenes/AdminScene.js';

export class App {
    constructor() {
        this.transitionManager = new TransitionManager();
    }

    init() {
        this.transitionManager.updateAuthUI();
        initLandingScene(this.transitionManager);
        initAuthScene(this.transitionManager);
        initDashboardScene(this.transitionManager);
        initChatScene(this.transitionManager);
        initAdminScene(this.transitionManager);

        const chatBackBtn = document.querySelector('.chat-back-button');
        if (chatBackBtn) {
            chatBackBtn.onclick = (e) => {
                e.preventDefault();
                this.transitionManager.transitionTo('dashboard');
            };
        }
    }
}
