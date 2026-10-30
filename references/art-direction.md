# Art direction for generative pieces

Code that runs is not the same as art that works. Use this guide to decide *what* to make and to review it before you ship.

## One idea, executed well

Before coding, write the piece in three short lines (in your reply, not in the file):

- **The rule**: the single process that generates everything ("particles follow a slowly turning noise field").
- **The tension**: what keeps it from being boring ("dense knots against empty air", "order that breaks near the edges").
- **The look**: palette, line quality, mood, in a few concrete words.

If you cannot say the rule in one sentence, simplify the algorithm.

## Make every seed good

A generative piece is a *family*, not a single image. Test it as one.

- Look at least **8 different seeds**. If more than about 2 look broken, empty, or muddy, fix the algorithm or narrow the parameter ranges. Do not just tell the user to try another seed.
- Check **extremes** of every slider. The minimum and maximum should still produce something presentable.
- Prefer variation that changes **composition** (where the density sits, where the focal point falls) over variation that only shifts color.

## Composition

- Give the eye a **focal region**: a density peak, a contrast spike, a single large form. Uniform noise everywhere reads as a screensaver.
- Use a **scale hierarchy**: a few big elements, more medium ones, many small ones.
- Leave **breathing room**. Empty space is part of the composition. A margin or an unfilled region often upgrades a piece immediately.
- **Layer**: a quiet background structure, a main layer, and a light accent layer. Use transparency and trails to create depth.
- Restraint with symmetry and repetition: break them on purpose, somewhere.

## Color

- Use a **tinted background** (never pure black or white) plus **3 to 5 colors**. Pick for value contrast first, hue second.
- Use one color as a **rare accent**: assign it to a small fraction of elements.
- Palettes that work for line art on light paper need *darker, more saturated* marks; on dark backgrounds, brighter, slightly desaturated marks.
- Low-opacity strokes (alpha around 30 to 90 out of 255) build tone through overlap, but check that the result is not washed out.
- Preset palettes are shipped in the template (`PALETTES`). Add 3 to 5 of your own that suit the piece instead of keeping the defaults.

## Parameters (the controls people will actually use)

- Offer **4 to 7** parameters. Every one must visibly change the result. If a slider is subtle, cut it or widen its range.
- Name them in **plain words** ("Swirl", "Density", "Line opacity"), not variable names ("noiseScale2").
- Set the **default to a good-looking value**, not the middle of the range by default.
- Choose ranges that **cannot reach ugly states**: clamp the extremes rather than hope.
- Mark each parameter `regen: true` if changing it needs a rebuild (counts, scales, anything baked into entities) and `regen: false` if it can apply live (speed, opacity, weight).
- Counts need a **ceiling** that keeps the page smooth.

## Motion (animated pieces)

- Slow beats fast. Most animated generative art looks better at half the speed you first try.
- Let it **settle**: a piece that reaches a pleasing state and then keeps evolving gently is better than one that is chaotic forever.
- Always support pause, and start paused on a settled image for users who prefer reduced motion (the template does this).
- Avoid flashing, rapid strobing, and large high-contrast full-screen changes.

## Originality

Make original work. Use general techniques (noise fields, recursion, packing, tilings), but do not reproduce a specific living artist's distinctive pieces or signature style.

## Review checklist (do this before delivering)

- [ ] The rule fits in one sentence
- [ ] 8 seeds checked, at most 1 or 2 weak
- [ ] Slider extremes still look intentional
- [ ] A clear focal region and some empty space
- [ ] Tinted background, 3 to 5 colors, one accent used sparingly
- [ ] Defaults look good the moment the page opens
- [ ] Smooth at default settings; counts capped
- [ ] Pause works; reduced-motion users get a still image
