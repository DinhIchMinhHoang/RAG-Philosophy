const COLORS = ['#7C3AED', '#6D28D9', '#06B6D4', '#0891B2', '#3B82F6', '#2563EB', '#5B21B6', '#0E7490', '#1E40AF'];
const MOVEMENT_TYPES = ['lavaLamp', 'lavaLamp', 'lavaLamp', 'orbital', 'sine'];

let paletteProgress = 0;

function hexToRgb(hex) {
    const h = hex.replace('#', '');
    const bigint = parseInt(h, 16);
    return { r: (bigint >> 16) & 255, g: (bigint >> 8) & 255, b: bigint & 255 };
}

function rgbToCss(rgb) {
    return `rgba(${Math.round(rgb.r)}, ${Math.round(rgb.g)}, ${Math.round(rgb.b)}, 1)`;
}

function lerp(a, b, t) { return a + (b - a) * t; }

function samplePalette(palette, t) {
    const n = palette.length;
    const tt = (t % n + n) % n;
    const idx = Math.floor(tt);
    const frac = tt - idx;
    const a = hexToRgb(palette[idx]);
    const b = hexToRgb(palette[(idx + 1) % n]);
    return { r: lerp(a.r, b.r, frac), g: lerp(a.g, b.g, frac), b: lerp(a.b, b.b, frac) };
}

export class MorphingBlob {
    constructor(canvas) {
        this.canvas = canvas;
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.baseRadius = (60 + Math.random() * 200) * 2;
        this.radius = this.baseRadius;
        this.color = COLORS[Math.floor(Math.random() * COLORS.length)];
        this.movementType = MOVEMENT_TYPES[Math.floor(Math.random() * MOVEMENT_TYPES.length)];
        this.vx = (Math.random() - 0.5) * 1.5;
        this.vy = (Math.random() - 0.5) * 1.5;

        this.lavaProgress = Math.random();
        this.lavaDuration = 12 + Math.random() * 18;
        this.lavaSpeed = 1 / (this.lavaDuration * 60);
        this.lavaSwayFreq = 0.5 + Math.random() * 1.5;
        this.lavaSwayAmplitude = 30 + Math.random() * 80;
        this.lavaStartX = this.x;
        this.lavaStartOffset = 80 + Math.random() * 160;
        this.lavaDir = 1;

        this.z = Math.random();
        this.phaseOffset = Math.random();
        this.shapeScale = 1;
        this.targetShapeScale = 0.9 + Math.random() * 0.3;
        this.shapeScaleLerp = 0.002 + Math.random() * 0.008;

        this.orbitCenterX = this.x;
        this.orbitCenterY = this.y;
        this.orbitRadius = 50 + Math.random() * 150;
        this.orbitSpeed = 0.005 + Math.random() * 0.01;
        this.orbitAngle = Math.random() * Math.PI * 2;

        this.sineTime = 0;
        this.sineFrequency = 0.008 + Math.random() * 0.012;
        this.sineAmplitude = 20 + Math.random() * 60;

        this.bounceVx = (Math.random() - 0.5) * 2;
        this.bounceVy = (Math.random() - 0.5) * 2;
        this.bounce = 0.95;

        this.spiralTime = 0;
        this.spiralSpeed = 0.003 + Math.random() * 0.006;

        this.blobPoints = this.generateBlobPoints(20);
        this.targetBlobPoints = this.generateBlobPoints(20);
        this.morphProgress = 0;
        this.morphSpeed = 0.004 + Math.random() * 0.008;
        this.shapeChangeTimer = 0;
        this.shapeChangeInterval = 120 + Math.random() * 180;

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
            points.push({ angle, distance, targetDistance: distance, variance: 0 });
        }
        return points;
    }

    updateBlobShape() {
        this.morphProgress += this.morphSpeed;
        if (this.morphProgress >= 1) {
            this.morphProgress = 0;
            for (let i = 0; i < this.blobPoints.length; i++) {
                this.blobPoints[i].targetDistance = this.baseRadius * (0.75 + Math.random() * 0.35);
            }
        }
        for (let i = 0; i < this.blobPoints.length; i++) {
            this.blobPoints[i].distance += (this.blobPoints[i].targetDistance - this.blobPoints[i].distance) * this.morphSpeed * 2;
        }
    }

    updateMovement() {
        this.time += 1;
        switch (this.movementType) {
            case 'lavaLamp':
                this.lavaProgress += this.lavaSpeed * this.lavaDir;
                if (this.lavaProgress >= 1) {
                    this.lavaProgress = 1; this.lavaDir = -1;
                } else if (this.lavaProgress <= 0) {
                    this.lavaProgress = 0; this.lavaDir = 1;
                    this.lavaDuration = 12 + Math.random() * 18;
                    this.lavaSpeed = 1 / (this.lavaDuration * 60);
                    this.lavaSwayFreq = 0.5 + Math.random() * 1.5;
                    this.lavaSwayAmplitude = 30 + Math.random() * 80;
                    this.lavaStartOffset = 80 + Math.random() * 160;
                }
                const startY = this.canvas.height + this.lavaStartOffset;
                const endY = -this.radius * 2;
                const t = this.lavaProgress;
                const smoothT = t * t * (3 - 2 * t);
                this.y = startY + (endY - startY) * smoothT;
                const sway = Math.sin(smoothT * Math.PI * 2 * this.lavaSwayFreq) * this.lavaSwayAmplitude;
                this.x = this.lavaStartX + sway;
                break;
            case 'orbital':
                this.orbitAngle += this.orbitSpeed;
                this.x = this.orbitCenterX + Math.cos(this.orbitAngle) * this.orbitRadius;
                this.y = this.orbitCenterY + Math.sin(this.orbitAngle) * this.orbitRadius;
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
                if (spiralRadius > 400) this.spiralTime = 0;
                break;
        }
        if (['linear', 'sine'].includes(this.movementType)) {
            if (this.x - this.radius < 0) { this.x = this.radius; this.vx *= -0.8; }
            if (this.x + this.radius > this.canvas.width) { this.x = this.canvas.width - this.radius; this.vx *= -0.8; }
            if (this.y - this.radius < 0) { this.y = this.radius; this.vy *= -0.8; }
            if (this.y + this.radius > this.canvas.height) { this.y = this.canvas.height - this.radius; this.vy *= -0.8; }
        }
        if (this.movementType === 'orbital') {
            this.orbitCenterX = Math.max(this.radius, Math.min(this.canvas.width - this.radius, this.orbitCenterX));
            this.orbitCenterY = Math.max(this.radius, Math.min(this.canvas.height - this.radius, this.orbitCenterY));
        }
    }

    update() {
        this.updateMovement();
        this.updateBlobShape();
        this.shapeScale += (this.targetShapeScale - this.shapeScale) * this.shapeScaleLerp;
        if (Math.abs(this.targetShapeScale - this.shapeScale) < 0.01) {
            this.targetShapeScale = 0.9 + Math.random() * 0.3;
        }
        this.radius += this.radiusChangeRate * 0.3;
        this.radiusChangeRate += (Math.random() - 0.5) * 0.1;
        if (this.radius <= this.minRadius || this.radius >= this.maxRadius) {
            this.radiusChangeRate *= -1;
        }
    }

    draw(ctx) {
        ctx.save();
        ctx.globalAlpha = 0.55 + this.z * 0.45;
        const t = (paletteProgress + this.phaseOffset) * COLORS.length;
        const rgb = samplePalette(COLORS, t);
        ctx.fillStyle = rgbToCss(rgb);
        ctx.translate(this.x, this.y);
        ctx.scale(this.shapeScale, this.shapeScale);
        ctx.beginPath();
        for (let i = 0; i < this.blobPoints.length; i++) {
            const point = this.blobPoints[i];
            const nextPoint = this.blobPoints[(i + 1) % this.blobPoints.length];
            const x = Math.cos(point.angle) * point.distance;
            const y = Math.sin(point.angle) * point.distance;
            const nextX = Math.cos(nextPoint.angle) * nextPoint.distance;
            const nextY = Math.sin(nextPoint.angle) * nextPoint.distance;
            const cpX = (x + nextX) / 2;
            const cpY = (y + nextY) / 2;
            if (i === 0) ctx.moveTo(x, y); else ctx.quadraticCurveTo(x, y, cpX, cpY);
        }
        ctx.closePath();
        ctx.fill();
        ctx.restore();
    }
}

export function advancePalette() {
    paletteProgress = (paletteProgress + 0.0006) % 1;
    return paletteProgress;
}

export function getPaletteProgress() { return paletteProgress; }
