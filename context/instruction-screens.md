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
- Coding pages **after** the last build step: port letter, Icon/Word screenshot
  or block names, what success looks like.

## `screens.md` table

One row per Figma frame:

```
step | figma_frame | png | parts_added | copy
12 | Crane/12-hoist-axle | renders/step-012.png | 7M axle black | Slide the axle through the big motor.
```

Repo stores the **Figma file URL** on the build README. Do not commit `.fig`.

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

If `renders/` is empty, Figma frames can still exist as chrome + placeholder
("PNG pending LeoCAD"). Do not ship a fake isometric.

## Agent + Figma MCP

- Create/instance the page component.
- Fill step badge, rail text from `screens.md`.
- Place PNG if the file exists.
- Wire Next/Back.
- Match `steps.md` numbers; if they drift, fix git first, then Figma.
