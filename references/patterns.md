# Generative patterns

Starting points for common algorithms. Every snippet is **deterministic** (only `random()` and `noise()`, called after seeding) and follows the same hooks as `templates/viewer.html`: build in `buildSystem()`, draw in `drawFrame()` or `drawStatic()`, read tunables from `P`, colors from `state.colors`.

These are patterns, not recipes. Combine, distort, and layer them. A piece with one clear rule and good restraint beats five effects stacked together.

## 1. Flow field (particles follow noise)

The default piece in the template. Key points: clamp the grid index (particles leave the canvas), respawn off-canvas particles with `random()` so the sequence stays reproducible, and precompute the field once.

```js
function buildField(cell) {
  const cols = ceil(width / cell), rows = ceil(height / cell);
  const field = new Array(cols * rows);
  for (let y = 0; y < rows; y++)
    for (let x = 0; x < cols; x++)
      field[x + y * cols] = noise(x * cell * P.noiseScale, y * cell * P.noiseScale) * TWO_PI * P.swirl;
  return { field, cols, rows };
}

function fieldAngle(f, x, y, cell) {
  const cx = constrain(floor(x / cell), 0, f.cols - 1);
  const cy = constrain(floor(y / cell), 0, f.rows - 1);
  return f.field[cx + cy * f.cols];
}
```

Variations: add a second noise octave, make the angle depend on distance from a center, quantize angles (`round(a / (PI / 4)) * PI / 4`) for a woven look, vary line weight by speed.

## 2. Recursive tree

Cap `depth`: the work doubles each level, so 12 is fine and 18 will freeze the page.

```js
function branch(x, y, len, angle, depth) {
  if (depth === 0 || len < 2) return;
  const x2 = x + cos(angle) * len;
  const y2 = y + sin(angle) * len;
  strokeWeight(max(0.5, depth * 0.8));
  line(x, y, x2, y2);
  const spread = P.spread * random(0.8, 1.2);
  const shrink = random(0.66, 0.78);
  branch(x2, y2, len * shrink, angle - spread, depth - 1);
  branch(x2, y2, len * shrink, angle + spread, depth - 1);
}
// static piece:  branch(width / 2, height * 0.95, height * 0.2, -HALF_PI, 9);
```

## 3. Cellular automaton (grid)

Use flat typed arrays and a second buffer; never mutate the grid while reading it.

```js
let gridCols = 0, gridRows = 0, cells, nextCells;
const GRID_CELL = 8;

function buildGrid() {
  gridCols = floor(width / GRID_CELL);
  gridRows = floor(height / GRID_CELL);
  cells = new Uint8Array(gridCols * gridRows);
  nextCells = new Uint8Array(gridCols * gridRows);
  for (let i = 0; i < cells.length; i++) cells[i] = random() < P.density ? 1 : 0;
}

function stepGrid() {
  for (let y = 0; y < gridRows; y++) {
    for (let x = 0; x < gridCols; x++) {
      let n = 0;
      for (let dy = -1; dy <= 1; dy++)
        for (let dx = -1; dx <= 1; dx++)
          if (dx || dy) n += cells[((x + dx + gridCols) % gridCols) + ((y + dy + gridRows) % gridRows) * gridCols];
      const alive = cells[x + y * gridCols];
      nextCells[x + y * gridCols] = (alive && (n === 2 || n === 3)) || (!alive && n === 3) ? 1 : 0;
    }
  }
  [cells, nextCells] = [nextCells, cells];
}
```

For richer pictures: age cells and map age to palette color, leave ghost trails by fading the background with low alpha, or start from structured seeds instead of pure noise.

## 4. Circle packing

Grow each candidate to the largest radius that still fits. This is O(n²), fine up to a few thousand circles; cap the attempts.

```js
function packCircles(maxAttempts, minR, maxR) {
  const circles = [];
  for (let i = 0; i < maxAttempts; i++) {
    const x = random(width), y = random(height);
    let r = min(maxR, x, y, width - x, height - y);
    for (const c of circles) {
      r = min(r, dist(x, y, c.x, c.y) - c.r - 1);
      if (r < minR) break;
    }
    if (r >= minR) circles.push({ x, y, r, c: floor(random(state.colors.length)) });
  }
  return circles;
}
```

Variations: bias candidates toward a shape or noise density, draw rings instead of discs, draw nothing but the gaps.

## 5. Truchet tiles

Cheap, deterministic, and striking. Two arcs per tile; the random flip makes the pattern.

```js
function drawTruchet(cell) {
  noFill();
  for (let y = 0; y < height; y += cell) {
    for (let x = 0; x < width; x += cell) {
      push();
      translate(x + cell / 2, y + cell / 2);
      if (random() < 0.5) rotate(HALF_PI);
      arc(-cell / 2, -cell / 2, cell, cell, 0, HALF_PI);
      arc(cell / 2, cell / 2, cell, cell, PI, PI + HALF_PI);
      pop();
    }
  }
}
```

Variations: vary tile size with noise, color tiles by a noise field, use a third tile type with a diagonal.

## 6. Noise ridges (stacked contour lines)

Fill each ridge with the background color so nearer lines hide the ones behind.

```js
function drawRidges(count, amp) {
  for (let i = 0; i < count; i++) {
    const baseY = map(i, 0, count - 1, height * 0.15, height * 0.92);
    beginShape();
    vertex(0, height);
    for (let x = 0; x <= width; x += 4) {
      vertex(x, baseY - noise(x * P.noiseScale, i * 0.08) * amp);
    }
    vertex(width, height);
    endShape(CLOSE);
  }
}
// set fill(state.bg) and stroke(color) before calling
```

## Seeded utilities

```js
function pick(arr) { return arr[floor(random(arr.length))]; }

function pickWeighted(items, weights) {         // items[i] chosen with probability weights[i]
  let total = 0;
  for (const w of weights) total += w;
  let r = random(total);
  for (let i = 0; i < items.length; i++) { r -= weights[i]; if (r <= 0) return items[i]; }
  return items[items.length - 1];
}

function shuffled(arr) {                          // Fisher-Yates with the seeded generator
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = floor(random(i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;                                       // never use arr.sort(() => random() - 0.5)
}

function easeInOutCubic(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
function wrapAround(v, max) { return ((v % max) + max) % max; }
function mapRange(v, a, b, c, d) { return c + (d - c) * ((v - a) / (b - a)); }
```

## Performance rules of thumb

- Aim for 60 fps on an ordinary laptop. About 10,000 line segments per frame is the practical ceiling.
- Precompute anything that does not change per frame (fields, palettes, lookup tables).
- Use `pixelDensity(1)` and a 1000 to 1600 px canvas; CSS scales it for display.
- Avoid `loadPixels()` or `get()` every frame, and avoid creating vectors or objects inside hot loops.
- Heavy one-off work (packing, big grids) belongs in `buildSystem()`, with an attempt cap so a slider cannot freeze the page.
- Never use `Math.random()`, `Date`, or `millis()` in anything that affects the picture.
