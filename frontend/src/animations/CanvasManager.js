let gradientCanvas, dotCanvas, dotCtx;
let blobs = [];
let frameCounter = 0;

export function setupCanvases() {
    gradientCanvas = document.getElementById('gradientCanvas');
    if (!gradientCanvas) {
        gradientCanvas = document.createElement('canvas');
        gradientCanvas.id = 'gradientCanvas';
        document.body.insertBefore(gradientCanvas, document.body.firstChild);
    }

    dotCanvas = document.createElement('canvas');
    dotCanvas.id = 'dotCanvas';
    Object.assign(dotCanvas.style, {
        position: 'fixed', top: '0', left: '0', width: '100%', height: '100%',
        pointerEvents: 'none', zIndex: '15'
    });
    document.body.appendChild(dotCanvas);
    dotCtx = dotCanvas.getContext('2d');

    resizeCanvases();
    window.addEventListener('resize', resizeCanvases);
}

export function resizeCanvases() {
    gradientCanvas.width = window.innerWidth;
    gradientCanvas.height = window.innerHeight;
    gradientCanvas.style.width = `${window.innerWidth}px`;
    gradientCanvas.style.height = `${window.innerHeight}px`;

    dotCanvas.width = window.innerWidth;
    dotCanvas.height = window.innerHeight;
    dotCanvas.style.width = `${window.innerWidth}px`;
    dotCanvas.style.height = `${window.innerHeight}px`;
}

export { gradientCanvas, dotCanvas, dotCtx, blobs, frameCounter };
