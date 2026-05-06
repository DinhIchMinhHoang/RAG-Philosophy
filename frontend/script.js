// Colors for the blobs - Following new palette with variations
const COLORS = [
    '#7C3AED',  // Primary - Purple
    '#6D28D9',  // Primary darker - Deep Purple
    '#06B6D4',  // Secondary - Cyan
    '#0891B2',  // Secondary darker - Teal
    '#3B82F6',  // Tertiary - Blue
    '#2563EB',  // Tertiary darker - Deep Blue
    '#5B21B6',  // Purple variant
    '#0E7490',  // Cyan variant
    '#1E40AF'   // Blue variant
];

// Movement types - Lava lamp focused
const MOVEMENT_TYPES = ['lavaLamp', 'lavaLamp', 'lavaLamp', 'orbital', 'sine'];

// Helper: convert hex color (#rrggbb) to {r,g,b}
function hexToRgb(hex) {
    const h = hex.replace('#', '');
    const bigint = parseInt(h, 16);
    return {
        r: (bigint >> 16) & 255,
        g: (bigint >> 8) & 255,
        b: bigint & 255
    };
}

function rgbToCss(rgb) {
    return `rgba(${Math.round(rgb.r)}, ${Math.round(rgb.g)}, ${Math.round(rgb.b)}, 1)`;
}

function lerp(a, b, t) { return a + (b - a) * t; }

// Sample the palette smoothly: t in [0, paletteLength) where fractional part interpolates
function samplePalette(palette, t) {
    const n = palette.length;
    const tt = (t % n + n) % n; // wrap
    const idx = Math.floor(tt);
    const frac = tt - idx;
    const a = hexToRgb(palette[idx]);
    const b = hexToRgb(palette[(idx + 1) % n]);
    return {
        r: lerp(a.r, b.r, frac),
        g: lerp(a.g, b.g, frac),
        b: lerp(a.b, b.b, frac)
    };
}

// Advanced morphing blob configuration
class MorphingBlob {
    constructor(canvas) {
        this.canvas = canvas;
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        
        this.baseRadius = (60 + Math.random() * 200) * 2;
        this.radius = this.baseRadius;
        this.color = COLORS[Math.floor(Math.random() * COLORS.length)];
        
        // Movement behavior
        this.movementType = MOVEMENT_TYPES[Math.floor(Math.random() * MOVEMENT_TYPES.length)];
        this.vx = (Math.random() - 0.5) * 1.5;
        this.vy = (Math.random() - 0.5) * 1.5;

        // Lava lamp parameters - progress-based vertical motion and smooth sway
        // Use a normalized progress [0..1] so travel time is consistent across blobs.
        this.lavaProgress = Math.random(); // start at random point in cycle
        this.lavaDuration = 12 + Math.random() * 18; // seconds to travel from bottom to top
        this.lavaSpeed = 1 / (this.lavaDuration * 60); // progress increment per frame (approx at 60fps)
        this.lavaSwayFreq = 0.5 + Math.random() * 1.5; // number of sideways oscillations during travel
        this.lavaSwayAmplitude = 30 + Math.random() * 80; // horizontal sway amplitude in px
        this.lavaStartX = this.x; // base horizontal center for sway
        this.lavaStartOffset = 80 + Math.random() * 160; // how far below the bottom the blob starts
        this.lavaDir = 1; // 1 = rising, -1 = sinking (ping-pong)

        // Layer (z) and shape scale for depth/shape dynamics
        // Depth (z) kept static to avoid pop/reorder; use for subtle alpha/depth cue
        this.z = Math.random(); // current normalized depth 0..1 (static)
        // per-blob phase offset used for color sampling so blobs change together but slightly offset
        this.phaseOffset = Math.random();

        this.shapeScale = 1;
        this.targetShapeScale = 0.9 + Math.random() * 0.3; // 0.9..1.2
        this.shapeScaleLerp = 0.002 + Math.random() * 0.008;

        // Orbital motion parameters
        this.orbitCenterX = this.x;
        this.orbitCenterY = this.y;
        this.orbitRadius = 50 + Math.random() * 150;
        this.orbitSpeed = 0.005 + Math.random() * 0.01;
        this.orbitAngle = Math.random() * Math.PI * 2;
        
        // Sine wave parameters
        this.sineTime = 0;
        this.sineFrequency = 0.008 + Math.random() * 0.012;
        this.sineAmplitude = 20 + Math.random() * 60;
        
        // Bounce parameters
        this.bounceVx = (Math.random() - 0.5) * 2;
        this.bounceVy = (Math.random() - 0.5) * 2;
        this.bounce = 0.95;
        
        // Spiral parameters
        this.spiralTime = 0;
        this.spiralSpeed = 0.003 + Math.random() * 0.006;
        
        // Shape morphing
        this.blobPoints = this.generateBlobPoints(20);
        this.targetBlobPoints = this.generateBlobPoints(20);
        this.morphProgress = 0;
        this.morphSpeed = 0.004 + Math.random() * 0.008;
        this.shapeChangeTimer = 0;
        this.shapeChangeInterval = 120 + Math.random() * 180;
        
        // Size oscillation
        this.radiusChangeRate = (Math.random() - 0.5) * 2;
        this.minRadius = this.baseRadius * 0.5;
        this.maxRadius = this.baseRadius * 1.5;
        this.targetRadius = this.baseRadius;
        
        this.time = 0;
    }

    generateBlobPoints(count) {
        const points = [];
        for (let i = 0; i < count; i++) {
            const angle = (i / count) * Math.PI * 2;
            const distance = this.baseRadius * (0.75 + Math.random() * 0.35);
            points.push({
                angle: angle,
                distance: distance,
                targetDistance: distance,
                variance: 0
            });
        }
        return points;
    }

    updateBlobShape() {
        this.morphProgress += this.morphSpeed;
        
        // Smooth continuous morphing
        if (this.morphProgress >= 1) {
            this.morphProgress = 0;
            // Generate new target, but with smoother variations
            for (let i = 0; i < this.blobPoints.length; i++) {
                const current = this.blobPoints[i];
                // Generate new target distance with minimal variation
                const angle = (i / this.blobPoints.length) * Math.PI * 2;
                current.targetDistance = this.baseRadius * (0.75 + Math.random() * 0.35);
            }
        }

        // Smooth linear interpolation between current and target
        for (let i = 0; i < this.blobPoints.length; i++) {
            const current = this.blobPoints[i];
            // Smooth approach to target
            current.distance += (current.targetDistance - current.distance) * this.morphSpeed * 2;
        }
    }

    updateMovement() {
        this.time += 1;

        switch (this.movementType) {
            case 'lavaLamp':
                // Progress-based vertical motion (ping-pong): lavaProgress moves between 0 and 1
                this.lavaProgress += this.lavaSpeed * this.lavaDir;

                // Clamp and reverse direction at endpoints
                if (this.lavaProgress >= 1) {
                    this.lavaProgress = 1;
                    this.lavaDir = -1; // start sinking
                } else if (this.lavaProgress <= 0) {
                    this.lavaProgress = 0;
                    this.lavaDir = 1; // start rising
                    // Randomize parameters for the next rise cycle, but keep lavaStartX to avoid horizontal teleport
                    this.lavaDuration = 12 + Math.random() * 18;
                    this.lavaSpeed = 1 / (this.lavaDuration * 60);
                    this.lavaSwayFreq = 0.5 + Math.random() * 1.5;
                    this.lavaSwayAmplitude = 30 + Math.random() * 80;
                    this.lavaStartOffset = 80 + Math.random() * 160;
                }

                // Vertical position: lerp from just-below-bottom to just-above-top using smoothstep easing
                const startY = this.canvas.height + this.lavaStartOffset;
                const endY = -this.radius * 2;
                const t = this.lavaProgress;
                const smoothT = t * t * (3 - 2 * t);
                this.y = startY + (endY - startY) * smoothT;

                // Horizontal sway around lavaStartX using smooth sine oscillation
                const sway = Math.sin(smoothT * Math.PI * 2 * this.lavaSwayFreq) * this.lavaSwayAmplitude;
                this.x = this.lavaStartX + sway;
                break;
                
            case 'orbital':
                this.orbitAngle += this.orbitSpeed;
                this.x = this.orbitCenterX + Math.cos(this.orbitAngle) * this.orbitRadius;
                this.y = this.orbitCenterY + Math.sin(this.orbitAngle) * this.orbitRadius;
                // Slowly drift orbit center
                this.orbitCenterX += this.vx * 0.1;
                this.orbitCenterY += this.vy * 0.1;
                break;
                
            case 'sine':
                this.sineTime += this.sineFrequency;
                this.x += this.vx;
                this.y += this.vy + Math.sin(this.sineTime) * this.sineAmplitude * 0.1;
                break;
                
            case 'bounce':
                this.x += this.bounceVx;
                this.y += this.bounceVy;
                
                if (this.x - this.radius < 0 || this.x + this.radius > this.canvas.width) {
                    this.bounceVx *= -this.bounce;
                    this.x = Math.max(this.radius, Math.min(this.canvas.width - this.radius, this.x));
                }
                if (this.y - this.radius < 0 || this.y + this.radius > this.canvas.height) {
                    this.bounceVy *= -this.bounce;
                    this.y = Math.max(this.radius, Math.min(this.canvas.height - this.radius, this.y));
                }
                break;
                
            case 'spiral':
                this.spiralTime += this.spiralSpeed;
                const spiralRadius = 50 + this.spiralTime * 2;
                this.x = this.canvas.width / 2 + Math.cos(this.spiralTime) * spiralRadius;
                this.y = this.canvas.height / 2 + Math.sin(this.spiralTime) * spiralRadius;
                
                if (spiralRadius > 400) {
                    this.spiralTime = 0;
                }
                break;
        }

        // Boundary handling: clamp and gently reflect velocities instead of wrapping
        if (['linear', 'sine'].includes(this.movementType)) {
            if (this.x - this.radius < 0) {
                this.x = this.radius;
                this.vx *= -0.8;
            }
            if (this.x + this.radius > this.canvas.width) {
                this.x = this.canvas.width - this.radius;
                this.vx *= -0.8;
            }
            if (this.y - this.radius < 0) {
                this.y = this.radius;
                this.vy *= -0.8;
            }
            if (this.y + this.radius > this.canvas.height) {
                this.y = this.canvas.height - this.radius;
                this.vy *= -0.8;
            }
        }

        if (this.movementType === 'orbital') {
            // Keep orbit center in bounds so orbital motion remains visible
            this.orbitCenterX = Math.max(this.radius, Math.min(this.canvas.width - this.radius, this.orbitCenterX));
            this.orbitCenterY = Math.max(this.radius, Math.min(this.canvas.height - this.radius, this.orbitCenterY));
        }
    }

    update() {
        this.updateMovement();
        this.updateBlobShape();

        // Depth is static now (no timed transitions) to avoid popping/reordering

        // Smoothly interpolate overall shape scale for gentle shape variation
        this.shapeScale += (this.targetShapeScale - this.shapeScale) * this.shapeScaleLerp;
        if (Math.abs(this.targetShapeScale - this.shapeScale) < 0.01) {
            this.targetShapeScale = 0.9 + Math.random() * 0.3;
        }

        // Size oscillation without mouse interaction
        this.radius += this.radiusChangeRate * 0.3;
        this.radiusChangeRate += (Math.random() - 0.5) * 0.1;

        if (this.radius <= this.minRadius || this.radius >= this.maxRadius) {
            this.radiusChangeRate *= -1;
        }
    }

    draw(ctx) {
        ctx.save();
        // use shapeScale for gentle scaling, and z to affect opacity for depth perception
        ctx.globalAlpha = 0.55 + this.z * 0.45;
        // compute color from shared paletteProgress plus this blob's phase offset
        const t = (paletteProgress + this.phaseOffset) * COLORS.length;
        const rgb = samplePalette(COLORS, t);
        ctx.fillStyle = rgbToCss(rgb);
        ctx.translate(this.x, this.y);
        ctx.scale(this.shapeScale, this.shapeScale);
        ctx.beginPath();

        // Draw morphing blob shape around origin (0,0)
        for (let i = 0; i < this.blobPoints.length; i++) {
            const point = this.blobPoints[i];
            const nextPoint = this.blobPoints[(i + 1) % this.blobPoints.length];

            const x = Math.cos(point.angle) * point.distance;
            const y = Math.sin(point.angle) * point.distance;

            const nextX = Math.cos(nextPoint.angle) * nextPoint.distance;
            const nextY = Math.sin(nextPoint.angle) * nextPoint.distance;

            const cpX = (x + nextX) / 2;
            const cpY = (y + nextY) / 2;

            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.quadraticCurveTo(x, y, cpX, cpY);
            }
        }

        ctx.closePath();
        ctx.fill();
        ctx.restore();
    }
}

// Initialize canvas and blobs
const canvas = document.getElementById('gradientCanvas');
const ctx = canvas.getContext('2d');

function resizeCanvas() {
    // handled by resizeCanvases which sets up HiDPI scaling
    resizeCanvases();
}

// --- Dot grid overlay canvas (interactive) ---------------------------------
const dotCanvas = document.createElement('canvas');
dotCanvas.id = 'dotCanvas';
dotCanvas.style.position = 'fixed';
dotCanvas.style.top = '0';
dotCanvas.style.left = '0';
dotCanvas.style.width = '100%';
dotCanvas.style.height = '100%';
dotCanvas.style.pointerEvents = 'none';
dotCanvas.style.zIndex = '15'; // above gradient canvas, below UI (.scene is z-index:20)
document.body.appendChild(dotCanvas);
const dotCtx = dotCanvas.getContext('2d');

// Grid configuration (match previous CSS: 15px spacing, 0.75px dot)
let GRID_SPACING = 15; // pixels
let DOT_RADIUS = 0.75; // css pixels
const DOT_BASE_ALPHA = 0.25; // default alpha for a dot
let SPOT_RADIUS = 300; // radius of the mouse spotlight in pixels (increased for larger effect)

let mouseX = -9999, mouseY = -9999;
// Grid points for interactive displacement
let gridPoints = [];

function resizeCanvases() {
    // gradient canvas (main blobs)
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    canvas.style.width = window.innerWidth + 'px';
    canvas.style.height = window.innerHeight + 'px';

    // dot overlay canvas (grid)
    dotCanvas.width = window.innerWidth;
    dotCanvas.height = window.innerHeight;
    dotCanvas.style.width = window.innerWidth + 'px';
    dotCanvas.style.height = window.innerHeight + 'px';

    // rebuild grid points to match new size
    initDotGrid();
}

// Initialize grid points array
function initDotGrid() {
    gridPoints = [];
    const w = window.innerWidth;
    const h = window.innerHeight;
    for (let y = 0; y <= h; y += GRID_SPACING) {
        for (let x = 0; x <= w; x += GRID_SPACING) {
            gridPoints.push({
                x0: x, y0: y, // original position
                x: x, y: y,   // current position
                vx: 0, vy: 0  // velocity
            });
        }
    }
}

// wire resize
resizeCanvases();
window.addEventListener('resize', resizeCanvases);

// Frame counter used to reduce how often we reorder draw layers
let frameCounter = 0;
let paletteProgress = 0;

// Mouse / touch handling for the spotlight
function updatePointerFromEvent(e) {
    const rect = dotCanvas.getBoundingClientRect();
    if (e.touches && e.touches.length) {
        mouseX = e.touches[0].clientX - rect.left;
        mouseY = e.touches[0].clientY - rect.top;
    } else {
        mouseX = e.clientX - rect.left;
        mouseY = e.clientY - rect.top;
    }
}

window.addEventListener('mousemove', (e) => updatePointerFromEvent(e));
window.addEventListener('touchmove', (e) => { updatePointerFromEvent(e); e.preventDefault(); }, { passive: false });
window.addEventListener('mouseout', () => { mouseX = -9999; mouseY = -9999; });

// Draw the dot grid with a radial spotlight blend where the dot alpha moves
function drawDotGrid() {
    const w = window.innerWidth;
    const h = window.innerHeight;

    dotCtx.clearRect(0, 0, w, h);

    // physics parameters
    const baseAlpha = DOT_BASE_ALPHA;
    const spotR = SPOT_RADIUS;
    const ATTRACTION_STRENGTH = 0.35; // how strongly dots are pulled
    const RETURN_FORCE = 0.02; // spring force back to origin
    const DAMPING = 0.88; // velocity damping
    const MAX_DISPLACE = GRID_SPACING * 1.8; // cap displacement

    // If mouse is out of bounds, use a large distance so attraction is zero
    const hasPointer = mouseX >= 0 && mouseY >= 0 && mouseX < w && mouseY < h;

    // Update physics & draw
    for (let i = 0; i < gridPoints.length; i++) {
        const p = gridPoints[i];

        // Attraction toward mouse (blackhole-like)
        if (hasPointer) {
            const dx = mouseX - p.x;
            const dy = mouseY - p.y;
            const dist = Math.sqrt(dx * dx + dy * dy) + 0.0001;

            if (dist < spotR * 1.2) {
                const falloff = 1 - (dist / (spotR * 1.2));
                const force = ATTRACTION_STRENGTH * falloff;
                // accelerate toward mouse
                p.vx += (dx / dist) * force;
                p.vy += (dy / dist) * force;
            }
        }

        // Spring back to origin
        const sx = p.x0 - p.x;
        const sy = p.y0 - p.y;
        p.vx += sx * RETURN_FORCE;
        p.vy += sy * RETURN_FORCE;

        // Integrate
        p.vx *= DAMPING;
        p.vy *= DAMPING;
        p.x += p.vx;
        p.y += p.vy;

        // Limit displacement from origin
        const odx = p.x - p.x0;
        const ody = p.y - p.y0;
        const odist = Math.sqrt(odx * odx + ody * ody);
        if (odist > MAX_DISPLACE) {
            const scale = MAX_DISPLACE / odist;
            p.x = p.x0 + odx * scale;
            p.y = p.y0 + ody * scale;
            p.vx = 0;
            p.vy = 0;
        }

        // compute alpha blended by spotlight relative to original grid position
        let alpha = baseAlpha;
        if (hasPointer) {
            const dx0 = p.x0 - mouseX;
            const dy0 = p.y0 - mouseY;
            const dist0 = Math.sqrt(dx0 * dx0 + dy0 * dy0);
            if (dist0 < spotR) {
                const intensity = 1 - (dist0 / spotR);
                alpha = baseAlpha + intensity * (1 - baseAlpha);
            }
        }

        dotCtx.beginPath();
        dotCtx.fillStyle = `rgba(255,255,255,${alpha.toFixed(3)})`;
        dotCtx.arc(p.x, p.y, DOT_RADIUS, 0, Math.PI * 2);
        dotCtx.fill();
    }
}

// Create morphing blobs (keep a compact set for performance/visual clarity)
const blobs = [];
for (let i = 0; i < 10; i++) {
    blobs.push(new MorphingBlob(canvas));
}

// Animation loop
function animate() {
    // Clear canvas with neutral background
    ctx.fillStyle = '#020617';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Apply strong blur filter for smooth, glassy effect
    ctx.filter = 'blur(50px)';

    // Update and draw blobs (back to front for layering)
    // advance palette progress for synchronized smooth color cycling
    paletteProgress = (paletteProgress + 0.0006) % 1;
    // Update z/shape first then occasionally sort by z to draw back-to-front
    blobs.forEach(blob => blob.update());
    frameCounter++;
    // Sort only every 8 frames to prevent rapid reordering visual pops
    if (frameCounter % 8 === 0) {
        blobs.sort((a, b) => a.z - b.z);
    }
    blobs.forEach(blob => blob.draw(ctx));

    // Reset filter
    ctx.filter = 'none';

    // Draw interactive dot grid overlay
    drawDotGrid();

    requestAnimationFrame(animate);
}

// Start animation
animate();
