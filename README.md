<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="assets/logo-light.png">
    <img alt="Generative Art p5.js logo" src="assets/logo-light.png" width="140">
  </picture>
</p>

<h1 align="center">Generative Art with p5.js</h1>

<p align="center">
  A Claude skill that makes interactive, reproducible generative art:
  seeded randomness, live controls, and a settings box that recreates any piece exactly.
</p>

---

## What it does

Ask for generative art (flow fields, fractals, particle systems, tilings, cellular automata, anything p5.js can draw) and Claude builds **one self-contained HTML file** with a full control panel, checks it, and delivers it. Same seed and settings always draw the same piece.

## What you get

| Feature | Details |
|---|---|
| **Seed controls** | Type a seed, step prev/next, or roll a random one |
| **Parameter sliders** | Generated from one `PARAMS` list: labels, ranges, defaults, reset |
| **Palettes** | Presets plus per-color pickers |
| **Pause / Play** | Reduced-motion users start paused on a settled image |
| **Save PNG** | With a clear fallback when downloads are blocked |
| **Settings box** | Copy the seed, parameters, and colors as JSON; paste and Apply to restore the exact piece |
| **Shortcuts** | ← → seed, R random, Space pause, S save |
| **Responsive and themed** | Light and dark, desktop and phone |

## How it works

| Step | What happens |
|---|---|
| **1. Understand** | Idea or mood, static or animated, viewer or plain sketch. Writes the *rule*, *tension*, and *look* |
| **2. Design** | Picks the algorithm, defines 4 to 7 parameters, chooses a palette and a performance budget |
| **3. Build** | Edits the template's sketch sections; the engine (seeding, UI, export) stays untouched |
| **4. Verify** | Runs `check_sketch.py`, then renders several seeds and compares the same seed twice, when it can |
| **5. Deliver** | Publishes or saves the file, with notes on the default seed and settings |
| **6. Iterate** | Tunes ranges, defaults, and palettes first; keeps the seed fixed to compare |

## The determinism contract

- Seed first: `randomSeed()` and `noiseSeed()`
- Only `random()`, `randomGaussian()`, `noise()` affect the picture. Never `Math.random()`, `Date`, or `millis()`
- Use a counter reset per seed, not `frameCount`
- Build everything in `buildSystem()`
- Seeded shuffles only

## The checker

```bash
python3 scripts/check_sketch.py piece.html            # readable report
python3 scripts/check_sketch.py piece.html --json     # machine-readable
python3 scripts/check_sketch.py piece.html --strict   # exit 1 on any error
```

It flags unseeded randomness, wall-clock use, `frameCount`, missing seed controls, blocked hosts and remote assets, unpinned p5.js, oversized canvases, missing `pixelDensity()`, and missing reduced-motion handling. It reads source only; it can't prove determinism or judge beauty.

## Example prompts

- "Create a flow field particle system with Perlin noise"
- "Make a recursive fractal tree with color variations"
- "Build a circle packing piece in muted earth tones"
- "A Truchet tiling that slowly changes, calm and geometric"
- "Give me a plain p5.js sketch for the web editor"

## Install

### Claude (web and apps)

1. Download this repo as a ZIP (or zip the `generative-art-p5js` folder yourself). Make sure `SKILL.md` sits at the top level of the folder inside the ZIP.
2. Open Claude's settings and find the Skills section.
3. Upload the ZIP and turn the skill on.

### Claude Code

```bash
git clone https://github.com/zakiuhh/generative-art-p5js.git
cp -r generative-art-p5js ~/.claude/skills/
```

(Change the clone URL if your repo lives somewhere else.)

## Repo structure

```
generative-art-p5js/
├── assets/
│   ├── logo-dark.png        # for dark backgrounds
│   └── logo-light.png       # for light backgrounds
├── references/
│   ├── art-direction.md     # how to make it good, not just run
│   └── patterns.md          # algorithms, utilities, performance
├── scripts/
│   └── check_sketch.py      # static reproducibility and hosting checks
├── templates/
│   ├── viewer.html          # interactive viewer (start here)
│   └── sketch.js            # plain sketch for the p5 editor
├── LICENSE                  # Apache-2.0
├── NOTICE.md                # credits and list of changes
├── README.md
├── SKILL.md                 # the actual skill
└── generative-art-p5js.skill                 #skill file(zipped)
```

## Customizing

The look is set by CSS variables at the top of `templates/viewer.html`; the palettes are in the `PALETTES` object; the controls come from `PARAMS`. Keep the `name` in the `SKILL.md` frontmatter the same as the folder name. The template loads p5.js 1.7.0 from cdnjs; if you bump the version, re-test your pieces, since p5 2.x changed some APIs.

## Credits and license

Based on the design of Anthropic's **algorithmic-art** example skill (Apache-2.0). This edition is also Apache-2.0; see [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md) for attribution and the list of changes. Not affiliated with or endorsed by Anthropic or p5.js.
