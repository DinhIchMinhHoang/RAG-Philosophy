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
        this.vx = (Math.random() - 0.5) * 1.25;
        this.vy = (Math.random() - 0.5) * 1.25;
        
        // Size change rate (increased by 25%)
        this.radiusChangeRate = (Math.random() - 0.5) * 0.625;
        this.minRadius = this.baseRadius * 0.6;
        this.maxRadius = this.baseRadius * 1.4;
    }

    update() {
        // Linear movement
        this.x += this.vx;
        this.y += this.vy;

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

        // Size change with oscillation
        this.radius += this.radiusChangeRate;
        if (this.radius >= this.maxRadius || this.radius <= this.minRadius) {
            this.radiusChangeRate *= -1;
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
    ctx.filter = 'blur(50px)';

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
