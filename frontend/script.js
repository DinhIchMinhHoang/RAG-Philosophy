// Colors for the circles
const COLORS = [
    '#007069',
    '#10637D',
    '#2097BC',
    '#24937F',
    '#2C88A6',
    '#5CB0B0',
    '#7CC4ED'
];

// Mouse position tracking
let mouseX = window.innerWidth / 2;
let mouseY = window.innerHeight / 2;
const INTERACTION_RADIUS = 200;
const SIZE_BOOST = 1.3;

// Circle configuration
class Circle {
    constructor(canvas) {
        this.canvas = canvas;
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.baseRadius = (80 + Math.random() * 150) * 1.5;
        this.radius = this.baseRadius;
        this.color = COLORS[Math.floor(Math.random() * COLORS.length)];
        
        // Linear movement velocities (increased by 25% and constrained for better coverage)
        this.vx = (Math.random() - 0.5) * 5.46875;
        this.vy = (Math.random() - 0.5) * 5.46875;
        
        // Size change rate (increased by 25%)
        this.radiusChangeRate = (Math.random() - 0.5) * 2.734375;
        this.minRadius = this.baseRadius * 0.6;
        this.maxRadius = this.baseRadius * 1.4;
        
        // Target radius for smooth size transitions
        this.targetRadius = this.baseRadius;
    }

    update() {
        // Linear movement
        this.x += this.vx;
        this.y += this.vy;

        // Mouse interaction - size change only
        const dx = this.x - mouseX;
        const dy = this.y - mouseY;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < INTERACTION_RADIUS) {
            // Size boost when near cursor
            this.targetRadius = this.baseRadius * SIZE_BOOST;
        } else {
            // Return to oscillating size
            this.targetRadius = this.baseRadius;
        }

        // Smooth radius transition
        this.radius += (this.targetRadius - this.radius) * 0.1;

        // Original oscillation
        this.targetRadius += this.radiusChangeRate;
        if (this.targetRadius >= this.maxRadius || this.targetRadius <= this.minRadius) {
            this.radiusChangeRate *= -1;
        }

        // Wrap around screen edges - only wrap based on movement direction to prevent flickering
        if (this.vx < 0 && this.x + this.radius < 0) {
            this.x = this.canvas.width + this.radius;
        } else if (this.vx > 0 && this.x - this.radius > this.canvas.width) {
            this.x = -this.radius;
        }

        if (this.vy < 0 && this.y + this.radius < 0) {
            this.y = this.canvas.height + this.radius;
        } else if (this.vy > 0 && this.y - this.radius > this.canvas.height) {
            this.y = -this.radius;
        }
    }

    draw(ctx) {
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fill();
    }
}

// Initialize canvas and circles
const canvas = document.getElementById('gradientCanvas');
const ctx = canvas.getContext('2d');

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// Track mouse movement
window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
});

// Track touch movement for mobile
window.addEventListener('touchmove', (e) => {
    if (e.touches.length > 0) {
        mouseX = e.touches[0].clientX;
        mouseY = e.touches[0].clientY;
    }
});

// Create circles
const circles = [];
for (let i = 0; i < 7; i++) {
    circles.push(new Circle(canvas));
}

// Animation loop
function animate() {
    // Clear canvas with black background
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Apply blur filter
    ctx.filter = 'blur(75px)';

    // Update and draw circles
    circles.forEach(circle => {
        circle.update();
        circle.draw(ctx);
    });

    // Reset filter for any subsequent drawing
    ctx.filter = 'none';

    requestAnimationFrame(animate);
}

// Start animation
animate();
