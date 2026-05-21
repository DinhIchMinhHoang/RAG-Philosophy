const GRID_SPACING = 15;
const DOT_RADIUS = 0.75;
const DOT_BASE_ALPHA = 0.25;
const SPOT_RADIUS = 300;
const ATTRACTION_STRENGTH = 0.35;
const RETURN_FORCE = 0.02;
const DAMPING = 0.88;
const MAX_DISPLACE = GRID_SPACING * 1.8;

let mouseX = -9999, mouseY = -9999;
let gridPoints = [];

export function initDotGrid(w, h) {
    gridPoints = [];
    for (let y = 0; y <= h; y += GRID_SPACING) {
        for (let x = 0; x <= w; x += GRID_SPACING) {
            gridPoints.push({ x0: x, y0: y, x, y, vx: 0, vy: 0 });
        }
    }
}

export function updatePointerFromEvent(e, canvas) {
    const rect = canvas.getBoundingClientRect();
    if (e.touches && e.touches.length) {
        mouseX = e.touches[0].clientX - rect.left;
        mouseY = e.touches[0].clientY - rect.top;
    } else {
        mouseX = e.clientX - rect.left;
        mouseY = e.clientY - rect.top;
    }
}

export function clearPointer() { mouseX = -9999; mouseY = -9999; }

export function drawDotGrid(dotCtx, w, h) {
    dotCtx.clearRect(0, 0, w, h);
    const hasPointer = mouseX >= 0 && mouseY >= 0 && mouseX < w && mouseY < h;

    for (let i = 0; i < gridPoints.length; i++) {
        const p = gridPoints[i];
        if (hasPointer) {
            const dx = mouseX - p.x;
            const dy = mouseY - p.y;
            const dist = Math.sqrt(dx * dx + dy * dy) + 0.0001;
            if (dist < SPOT_RADIUS * 1.2) {
                const falloff = 1 - (dist / (SPOT_RADIUS * 1.2));
                const force = ATTRACTION_STRENGTH * falloff;
                p.vx += (dx / dist) * force;
                p.vy += (dy / dist) * force;
            }
        }
        const sx = p.x0 - p.x;
        const sy = p.y0 - p.y;
        p.vx += sx * RETURN_FORCE;
        p.vy += sy * RETURN_FORCE;
        p.vx *= DAMPING;
        p.vy *= DAMPING;
        p.x += p.vx;
        p.y += p.vy;
        const odx = p.x - p.x0;
        const ody = p.y - p.y0;
        const odist = Math.sqrt(odx * odx + ody * ody);
        if (odist > MAX_DISPLACE) {
            const scale = MAX_DISPLACE / odist;
            p.x = p.x0 + odx * scale;
            p.y = p.y0 + ody * scale;
            p.vx = 0; p.vy = 0;
        }
        let alpha = DOT_BASE_ALPHA;
        if (hasPointer) {
            const dx0 = p.x0 - mouseX;
            const dy0 = p.y0 - mouseY;
            const dist0 = Math.sqrt(dx0 * dx0 + dy0 * dy0);
            if (dist0 < SPOT_RADIUS) {
                alpha = DOT_BASE_ALPHA + (1 - DOT_BASE_ALPHA) * (1 - dist0 / SPOT_RADIUS);
            }
        }
        dotCtx.beginPath();
        dotCtx.fillStyle = `rgba(255,255,255,${alpha.toFixed(3)})`;
        dotCtx.arc(p.x, p.y, DOT_RADIUS, 0, Math.PI * 2);
        dotCtx.fill();
    }
}
