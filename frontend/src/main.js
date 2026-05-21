import { App } from './App.js';
import { setupCanvases } from './animations/CanvasManager.js';
import { MorphingBlob, advancePalette } from './animations/Blob.js';
import { initDotGrid, drawDotGrid, updatePointerFromEvent, clearPointer } from './animations/DotGrid.js';
import { gradientCanvas, dotCanvas, dotCtx, blobs } from './animations/CanvasManager.js';

document.addEventListener('DOMContentLoaded', () => {
    setupCanvases();
    initDotGrid(window.innerWidth, window.innerHeight);

    const ctx = gradientCanvas.getContext('2d');
    for (let i = 0; i < 10; i++) {
        blobs.push(new MorphingBlob(gradientCanvas));
    }

    let frameCounter = 0;

    window.addEventListener('mousemove', (e) => updatePointerFromEvent(e, dotCanvas));
    window.addEventListener('touchmove', (e) => { updatePointerFromEvent(e, dotCanvas); e.preventDefault(); }, { passive: false });
    window.addEventListener('mouseout', clearPointer);

    function animate() {
        ctx.fillStyle = '#020617';
        ctx.fillRect(0, 0, gradientCanvas.width, gradientCanvas.height);
        ctx.filter = 'blur(50px)';

        advancePalette();
        blobs.forEach(blob => blob.update());
        frameCounter++;
        if (frameCounter % 8 === 0) blobs.sort((a, b) => a.z - b.z);
        blobs.forEach(blob => blob.draw(ctx));

        ctx.filter = 'none';
        drawDotGrid(dotCtx, dotCanvas.width, dotCanvas.height);

        requestAnimationFrame(animate);
    }

    animate();

    const app = new App();
    app.init();
});
