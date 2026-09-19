# Instruction screens (Figma)

Kid-facing pages should look like **pretty LEGO Building Instructions**, but
they are **clickable Figma frames**, not a PDF booklet.

Pretty 3D is a **PNG** from LeoCAD or LPub3D (`builds/<name>/renders/`).
Figma is **chrome + prototype**. Figma does not invent the isometric model.

## Page chrome (one component, instanced per step)

Suggested frame: **landscape tablet**, e.g. 1920x1080 (or 1536x1024). White
background. Reuse one Figma component.

| Region | Content |
|---|---|
| Top-left | Step number in a colored badge (big, like official BI) |
| Top-right | Bin hint: Essential / Prime / both |
| Left rail | New-parts callout: qty + color swatch + "looks like" name. No element IDs. |
| Center | Hero: `renders/step-NNN.png` (isometric, optional fade of previous parts) |
| Bottom-left | Optional: rotation icon or "try with your hand" |
| Bottom-right | **Next** (and Back on the prototype) |

Official-BI recipe we are copying as *layout*, not as stolen art:

- White page, one action
- New parts obvious (callout box and/or highlighted in the render)
- Camera shows where the new piece sits

## Prototype

- Frame 1 -> N: Next.
- Back on every page after 1.
- Optional overlay: "Stuck? Ask Chris" -- do not auto-advance.
- Coding pages **after** the last build step: the `program.svg` from
  `python3 tools/blocks.py render`, plus port letters and what success
  looks like. Do not screenshot the SPIKE App if the SVG exists.

## Story slides (`story.md`)

Optional, and only for builds that want them. The SPIKE App opens a project
with a few narrative pages before step 1; this is ours. One row per slide:

```
slide | figma_frame | art | who | copy | camera | overlay
2 | Chameleon/S2-colour | renders/story-02.png | Daniel | "Daniel counted the colours." | -      | -
5 | Chameleon/S5-build  | renders/story-05.png | Maria  | "Build one."                  | 25 250 | renders/story-peek.png
```

`camera` is what makes a slide a **render** instead of an illustration. A
slide with a camera is drawn from `model.ldr` at its final step by
`pages.py render`, exactly like a step hero; a slide with `-` is drawn art
that lives in git.

`overlay` is an optional second image laid on the corner of the art. It
exists for the handoff from story to bricks: the last drawn animal, cut
out and leaning on the corner of the first photo of the model, carries the
child across the seam where the drawing stops. Keep it on a corner so it
never covers the thing being copied.

Story slides carry **no Back/Next**. They get printed. `preview.html` still
pages through them for review (click anywhere, or use the arrow keys) and
its print stylesheet lays the whole deck out one page per sheet.

Rules that `pages.py check` enforces:

- Slides are numbered **1..N on their own track**, never folded into the
  step numbers. `screens.md` row N is rendered with LeoCAD `-f N`, so a page
  inserted ahead of row 1 would quietly render the wrong bricks.
- Every `art` path must exist. Any `renders/story-*.png` that no slide
  points at is an error, so deleting a slide cannot leave a stray image.
- Story art with no `story.md` is an error.
- A slide with a camera must point at `renders/story-NN.png`. Aiming one at
  a `check-*.png` would have `render` overwrite that check view.

Rules for humans:

- Cast from the **Essential four** -- Leo, Maria, Daniel, Sofie. Parts for
  all four are in `45345`, so the figure on the screen is a figure Ian can
  pick up. Their bios are LEGO Education's and are linked in `sources.md`.
  Use the characters; do not copy a unit (see house rules).
- Three or four slides. One idea each. Last slide is the call to build.
- **The last slide shows a real render, not an illustration.** Give it a
  camera so `pages.py render` keeps it in step with the model. The
  no-fake-3D rule below applies hardest here: this is the picture the kid
  is trying to match.
- Pick that camera lower and more side-on than the `55 225` step default.
  The step heroes look down so you can see where a piece goes; this one has
  to look like the animal or vehicle, not like a pile of bricks.
- LeoCAD PNGs are **transparent and drawn for a white page**. Story chrome
  is dark, so a render on a story slide needs a white plate behind it or
  the black pegs and dark grey parts disappear. `preview.html` adds one for
  any slide with a camera; do the same in Figma.
- Story heroes render **without `--fade-steps`**. Step heroes grey out the
  history on purpose, so reusing that command for the finished model gives
  a ghost-white animal with one brightly coloured part -- the piece from
  the last step. `pages.py` handles this; if a render ever comes back
  washed out, that is the flag.
- Illustrations carry **no baked-in words**. Copy is a text layer in Figma
  (and an overlay in `preview.html`), so it stays editable and translatable.
- Art at 1536x1024 drops into the landscape tablet frame with no resampling.

## `screens.md` table

One row per instruction page. `camera` is two LeoCAD angles (`lat lon`) or
a `--viewpoint` name. `highlight` is `yes` so the new piece is outlined.

```
step | figma_frame | png | parts_added | camera | highlight | copy
12 | Crane/12-hoist-axle | renders/step-012.png | 7M axle black | 55 225 | yes | Slide the axle through the big motor.
```

Repo stores the **Figma file URL** on the build README. Do not commit `.fig`.

## Click through before Figma

Figma is chrome around a page list that has stopped moving. After the
PNGs exist, generate a local flipbook and actually click it:

```
python3 tools/pages.py check builds/<slug>
python3 tools/pages.py preview builds/<slug>
```

Open `preview.html` in a browser (white page, faded history, Next/Back,
arrow keys). If a page is unreadable here, it will be unreadable in
Figma -- split the `0 STEP` or change the camera in `screens.md`, then
`python3 tools/pages.py render builds/<slug>`.

The PNGs are RGBA with a transparent background. There is no LeoCAD CLI
flag for background colour, and `0 !LEOCAD MODEL BACKGROUND COLOR` is not
in the installed binary.

## Making the new piece obvious

A step page has to answer one question for a five-to-seven-year-old:
*which piece is new, and where does it go?* Four things move that needle,
in the order they matter. All of them live in `tools/pages.py`.

**1. Fill the page.** This is the big one and it is not a LeoCAD setting.
LeoCAD frames every step against the *finished* model's extent, so early
steps land at 11% of the canvas and print as a speck in a sea of white.
`pages.py` trims each render to its own drawn pixels and pads it back to
one hero size. Because the PNG is RGBA, the trim is exact.

**2. Ghost the history, keep true colours.** `--fade-steps-color #60FFFFFF`
washes out everything already built, so the new part is the only saturated
thing on the page and needs no false colour to stand out. Lower alpha is
more ghosted; below about `#40` the page prints too faint, and faded parts
turn translucent enough that parts hidden behind them show through tinted.
Leave `--highlight` off. Painting the new part magenta makes it pop, but a
six-year-old then goes looking for a magenta piece. The real colour is the
information they need.

**3. Point the camera at the new piece.** The most common reason a page is
hard to follow is that the new part is behind the hub. Two habits fix
almost all of it: pick the angle that shows *every* copy of a repeated
part (four pegs, four feet), and hold that angle still for the whole
sub-assembly so consecutive pages are comparable. Overhead (`70 180`)
tends to win whenever parts are mirrored on both sides.

**4. Bold lines and clean edges.** `--line-width 2` and `--aa-samples 8`
give a cartoon-weight outline that survives print.

If a page is *still* unclear after all four, the step is doing too much --
split the `0 STEP`.

## Kid copy

- Color + everyday name ("black stick with ridges" only if Ian lacks the word
  *axle*; prefer axle/beam once taught).
- One verb per page.
- After gears/pulleys: a page with no new parts -- "turn it with your hand."
- Combined kits: "this piece is in the Prime tray."

## Visual source order

1. LeoCAD CLI PNG of that STEP (preferred).
2. LPub3D page PNG (if we want callouts already in the render).
3. **Do not** use messy table photos as the hero if we want "pretty LEGO."
4. Do not image-gen fake bricks as the primary 3D.

The line is *what the picture is for*. A story slide is scenery and mood, so
it may be illustrated. Anything the kid is meant to copy brick-for-brick --
every step hero, and the finished model on the last story slide -- comes out
of LeoCAD, because a drawing of a model cannot be checked by `ldrcheck` and
will drift the first time a part moves.

If `renders/` is empty, Figma frames can still exist as chrome + placeholder
("PNG pending LeoCAD"). Do not ship a fake isometric.

## Agent + Figma MCP

- Create/instance the page component.
- Fill step badge, rail text from `screens.md`.
- Place PNG if the file exists.
- Wire Next/Back.
- Match `steps.md` numbers; if they drift, fix git first, then Figma.
