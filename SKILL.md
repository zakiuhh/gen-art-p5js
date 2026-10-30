---
name: generative-art-p5js
description: Creates interactive, reproducible p5.js generative art with seeded randomness, a schema-driven parameter UI, seed navigation, settings you can copy, and PNG export. Use when the user asks for generative art, algorithmic art, procedural visuals, creative coding, interactive sketches, flow fields, fractals, particle systems, noise art, tilings, cellular automata, circle packing, or mentions p5.js, Processing, Art Blocks, or "art with code". Delivers one self-contained HTML viewer (or a plain sketch.js for the p5 editor), checks it for reproducibility and hosting problems, and reviews it as art, not just as code.
---

# Generative Art with p5.js

Make original, reproducible generative art: one rule, many seeds, tunable controls, delivered as a single working file. "Reproducible" means the same seed and settings always draw the same piece.

## Workflow

### 1. Understand the request

Find out, using what the user already said first:

- **The idea or mood** (a subject, a feeling, an algorithm they like).
- **Static or animated.** A fixed image per seed, or something that moves.
- **Deliverable.** The interactive **viewer** (default), a plain **`sketch.js`** for the p5 web editor, or both.
- **Palette hints**, if any.

How to ask:
- **Vague request** ("make some generative art"): ask 2 or 3 short questions with concrete options, then stop and wait. Use an options or buttons tool if one is available.
- **Clear request**: don't interrogate. State your one-line concept and build.

Then write the piece in three short lines in your reply (not in the file): **the rule**, **the tension**, **the look**. See [references/art-direction.md](references/art-direction.md). If you can't state the rule in one sentence, simplify the algorithm.

### 2. Design the system

- **Pick the algorithm.** Start from [references/patterns.md](references/patterns.md): flow fields, recursive trees, cellular automata, circle packing, Truchet tiles, noise ridges, and seeded utilities. Combine or twist them; don't just paste one.
- **Define 4 to 7 parameters** with sensible ranges, a plain-words label, a good-looking default, and `regen: true` (needs a rebuild) or `regen: false` (applies live). Every parameter must visibly change the result.
- **Choose a palette:** tinted background plus 3 to 5 colors, one rare accent. Replace the template's presets with ones that suit the piece.
- **Set a performance budget** (see below).

### 3. Build

**Viewer (default):** start from [templates/viewer.html](templates/viewer.html). Edit only sections 1 to 4: `CONFIG`, `PARAMS`, `PALETTES`, and the sketch (`buildSystem`, `drawFrame` or `drawStatic`). **Leave section 5 (the engine) alone.** It already provides seeding, seed navigation, the generated parameter UI, reset, pause, PNG export, the copyable settings box, keyboard shortcuts, and reduced-motion handling. Note that the template ships with a working demo piece; replace it entirely.

**Plain sketch:** start from [templates/sketch.js](templates/sketch.js) when the user wants code for the p5 editor or OpenProcessing.

#### Determinism contract (non-negotiable)

1. Seed first: `randomSeed(seed)` and `noiseSeed(seed)` before any randomness.
2. **Only** `random()`, `randomGaussian()`, and `noise()` may influence the picture. Never `Math.random()`, `Date`, `millis()`, or `performance.now()`.
3. Use your own frame counter reset on every seed (`state.t`), not `frameCount`.
4. Build everything inside `buildSystem()`, never at load time.
5. Shuffle with a seeded Fisher-Yates (see patterns), never `sort(() => random() - 0.5)`.
6. Picking a *new seed* may use `Math.random()`. That is the one allowed exception.

#### Hosting rules (single file)

- One `.html` file, everything inline. Load p5.js only from `cdnjs.cloudflare.com` with an **exact pinned version** (the template pins 1.7.0).
- No remote images, fonts, JSON, or assets: generate them or embed small ones. Remote loads fail silently in hosted pages.
- If the page may be hosted in Claude Chat, remember downloads can be blocked: the template falls back to a "right-click, save image" message, and the settings box always works.

### 4. Verify

Run the static checker, then look at the art if you can:

```bash
python3 scripts/check_sketch.py piece.html --strict
```

It flags unseeded randomness, wall-clock use, `frameCount`, missing seed controls or required functions, blocked hosts, remote assets, unpinned p5, oversized canvases, missing `pixelDensity()`, and missing reduced-motion handling. A clean result is evidence, not proof.

If a browser or screenshot tool is available:
- Render **at least 3 to 8 seeds** and actually look at them. Reject the algorithm if more than about two look broken.
- Render the **same seed twice** and compare: they must match.
- Check slider **extremes**.

If you have no way to render, say so plainly. Don't claim it "looks good" unseen; rely on the checker and on reasoning about the algorithm.

### 5. Deliver

- If an Artifact or publishing tool is available, publish the single HTML file so the user gets a live, shareable page.
- Otherwise save the file (`.html`, or `.js` for a plain sketch) and present it.
- Add a short note: the rule in one line, the default seed, what the main sliders do, and that **Settings → Copy** captures seed + parameters + colors to reproduce an exact piece.

### 6. Iterate

When the user says "more chaotic", "calmer", or "different colors", adjust parameter ranges, defaults, or palettes first; rewrite the algorithm only if the idea itself must change. Keep the seed fixed while comparing versions so the differences are visible.

## Performance budget

| Item | Guideline |
|---|---|
| Line segments per frame | about 10,000 at most for 60 fps |
| Canvas | 1000 to 1600 px square; `pixelDensity(1)`; CSS scales it |
| Per-frame work | precompute fields and palettes; no `loadPixels()`/`get()` in `draw()` |
| Heavy setup (packing, big grids) | in `buildSystem()` with an attempt cap |
| Recursion | cap depth (about 12 for binary trees) |

## Parameter UI

`PARAMS` is the single source of truth. Each entry is `{ key, label, min, max, step, value, regen }`. The engine builds the sliders, keeps the readouts accurate, clamps values, resets to defaults, and writes the settings JSON from this list. Read values as `P.key` in the sketch. Don't hand-write controls.

## Look and feel

The template UI is neutral, themeable through CSS variables at the top of `<style>`, and supports light and dark mode. If the user wants a specific brand look, change those variables (and the palette presets). It makes no brand claims.

## Checklist

- [ ] Rule, tension, and look written in the reply
- [ ] Seeded randomness only; checker passes with `--strict`
- [ ] Same seed + settings gives the same image (verified by render if possible)
- [ ] 4 to 7 parameters, each visibly useful; sensible defaults and ranges
- [ ] Seed prev/next/random/go-to, reset, pause, save, and settings copy/apply all work
- [ ] Tinted background, 3 to 5 colors, good-looking defaults
- [ ] Smooth at default settings; counts capped
- [ ] Reduced-motion users start on a still, settled image
- [ ] Original work, not a copy of a specific artist's piece

## Files

- [templates/viewer.html](templates/viewer.html): the interactive viewer (start here)
- [templates/sketch.js](templates/sketch.js): plain sketch for the p5 editor
- [references/patterns.md](references/patterns.md): algorithms, utilities, performance
- [references/art-direction.md](references/art-direction.md): how to make it good
- `scripts/check_sketch.py`: static checks (`--json`, `--strict`)
