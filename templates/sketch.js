/**
 * Plain p5.js sketch (no UI). Paste into the p5 web editor, OpenProcessing, or any p5 page.
 * Change SEED to get a different, fully reproducible piece. Same SEED = same artwork.
 *
 * Determinism rules: use only random(), randomGaussian() and noise() (never Math.random,
 * Date or millis); use the `t` counter instead of frameCount; build everything in build().
 */

const SEED = 12345;
const SIZE = 1000;

const P = {                       // every tunable value lives here
  particleCount: 3000,
  noiseScale: 0.003,
  swirl: 2,
  flowSpeed: 0.8,
  lineAlpha: 85,
  lineWeight: 1
};

const BG = '#faf9f5';
const COLORS = ['#d97757', '#6a9bcc', '#788c5d', '#b0aea5'];

const CELL = 10;
let particles = [], field = [], cols = 0, rows = 0, t = 0;

function setup() {
  pixelDensity(1);
  createCanvas(SIZE, SIZE);
  randomSeed(SEED);
  noiseSeed(SEED);
  background(BG);
  build();
}

function draw() {
  strokeWeight(P.lineWeight);
  for (const p of particles) { p.step(); p.show(); }
  t++;
}

function build() {
  cols = ceil(width / CELL);
  rows = ceil(height / CELL);
  field = new Array(cols * rows);
  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      field[x + y * cols] = noise(x * CELL * P.noiseScale, y * CELL * P.noiseScale) * TWO_PI * P.swirl;
    }
  }
  particles = Array.from({ length: P.particleCount }, (_, i) => new Particle(i));
}

class Particle {
  constructor(i) {
    const hex = COLORS[i % COLORS.length];
    this.rgb = [parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16)];
    this.spawn();
  }
  spawn() {
    this.x = random(width);
    this.y = random(height);
    this.px = this.x;
    this.py = this.y;
  }
  step() {
    this.px = this.x;
    this.py = this.y;
    const cx = constrain(floor(this.x / CELL), 0, cols - 1);
    const cy = constrain(floor(this.y / CELL), 0, rows - 1);
    const a = field[cx + cy * cols];
    this.x += cos(a) * P.flowSpeed * 2;
    this.y += sin(a) * P.flowSpeed * 2;
    if (this.x < 0 || this.x > width || this.y < 0 || this.y > height) this.spawn();
  }
  show() {
    stroke(this.rgb[0], this.rgb[1], this.rgb[2], P.lineAlpha);
    line(this.px, this.py, this.x, this.y);
  }
}

function keyPressed() {
  if (key === 's' || key === 'S') saveCanvas('piece-' + SEED, 'png');
}
