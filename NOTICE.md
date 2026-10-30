# Notice

## This project

Generative Art with p5.js (improved edition)
Modifications Copyright 2026 Zaki (@zakiuhh)

Not affiliated with or endorsed by Anthropic or p5.js.

## Original work

This skill follows the design of Anthropic's **algorithmic-art** example skill (seeded randomness for Art Blocks-style reproducibility, a viewer template with a parameter sidebar, and a separate generator template).

**Project:** https://github.com/anthropics/skills (skills/algorithmic-art)
**Author:** Anthropic, PBC
**License:** Apache License 2.0 (the full text is in `LICENSE`)

If your copy of the original skill came from another source, check that source's license and credit it here.

The Apache License does not grant any right to use Anthropic's names, logos, or brand identity. This edition therefore removes the Anthropic branding the earlier version carried (the `--anthropic-*` color variables, the "Anthropic branding" requirement, and the Poppins/Lora UI styling) and ships a neutral, themeable interface instead.

## p5.js

The generated pieces load [p5.js](https://p5js.org) (LGPL-2.1) from a public CDN. p5.js is not bundled in this repository.

## Changes in this edition (Apache-2.0 section 4(b))

- **Rewrote** `SKILL.md`: a 6-step workflow (understand, design, build, verify, deliver, iterate), an explicit determinism contract, hosting rules, a performance budget, and a checklist.
- **Replaced** `viewer-template.html` with `templates/viewer.html`: a working demo piece instead of stubs; a schema-driven UI (one `PARAMS` list drives sliders, defaults, reset, and settings); palette presets; pause/play; PNG export with a fallback; a copy/apply settings box; keyboard shortcuts; light and dark themes; responsive layout; reduced-motion handling; and clamping of all inputs.
- **Replaced** `generator-template.js` with `templates/sketch.js` (a plain sketch for the p5 editor) and `references/patterns.md` (corrected, deterministic patterns; the original flow-field snippet could index out of bounds and used an undefined `maxSpeed`).
- **Added** `references/art-direction.md`, `scripts/check_sketch.py` (static reproducibility and hosting checker), the logos, the README, and this notice.
- **Removed** the Anthropic branding and the Poppins/Lora Google Fonts dependency.
