# House rules

Constraints for humans and agents. If a build violates these, it is the
wrong build.

## People

- **Ian** is 6. Saturday ASU class uses **SPIKE Essential** (hub, App palette,
  and muscle memory). Keep class-safe builds Essential-only.
- **Chris** is the adult partner: bins, Figma, LeoCAD install, table check.
- Home builds may **mix** Essential + Prime parts. One hub per model.

## Hardware we actually own

- Own: Essential `45345`, Prime `45678`, Prime Expansion `45681`. See `kits/`.
- Do **not** assume any further add-on, or random bins. Grep
  `kits/*/parts.txt` for quantity and colour before designing a part in.
- The Expansion has **no hub and no battery**. It cannot power a build on
  its own; it is parts only.
- Motors/sensors mix across hubs; **battery packs do not**.
- One hub per build. Class default: Essential hub (2 ports A/B, streaming,
  no on-hub matrix). Home machines that need extra ports or torque: Prime
  hub is OK (6 ports, download, built-in 5x5). The 3x3 colour matrix is a
  port accessory, not part of either hub.

## Snap Circuits (Elenco)

- Own: Beginner SCB-20 and Jr SC-100 (Jr box arrived, not yet inventoried).
  See `kits/scb20-beginner/`, `kits/sc100-jr/` and `context/snap-circuits.md`.
  Not LEGO; no hub, no code.
- We write our own lessons. Elenco's manuals stay as links in `sources.md`;
  do not paste their pages or project drawings.
- Chris puts batteries in and checks the first ON. A wire straight across the
  battery holder is a short circuit: `tools/snap.py` refuses to draw one.
- Jr parts go on the Jr battery holder (3 V) only; the Beginner holder is
  4.5 V. The checker enforces it.
- Every picture Ian copies block-for-block comes from `circuit.snap` through
  `tools/snap.py`, the way LEGO pages come from `model.ldr`. Block sizes in
  `tools/snap/parts.json` are `measured: false` until checked on a real box;
  say so when you rely on them.
- Lessons are comics, **The Spark Detectives**: the SPIKE animal crew
  (Sully, Tika, Pip, Coco) redrawn in 2D from `context/story-cast-comic.png`,
  running a detective agency in a town at night. Not school and not the
  jungle. Otto the otter is retired. Copy Beast Academy's **format** (a
  mistake, a guess, a test, an explanation, practice with stars), never its
  characters, setting or pages. The explanation is a talk page: Pip's wrong
  idea first, then a picture he can repeat. Vary the page shape (a splash,
  a two-panel spread, a banner over three boxes). Don't make every talk a 2x2.
- Every answer in a comic (guesses, puzzles, Number Lab, missions) is worked
  out by `snap.py check` from the board. Never type an answer the checker
  could compute; if it can't, write it out and say it is unchecked.
- Fans: goggles or sunglasses, lean back, never look straight down at a
  spinning fan, aim it away from faces. Module 2 launches fans on purpose.

## Curriculum we refuse

- Do not copy official Essential or Prime **units/lessons** into this repo.
- Do not run Prime's middle-school lesson plans. Hardware only.
- Official PDFs stay as **links** in `sources.md`, never as dumped files.

## How we build original work

1. Chris writes a **brief** (theme, complexity, sensors, done-when).
2. Agent writes git spec: `steps.md` + `model.ldr` + BOM vs `kits/*/parts.txt`.
3. Pretty pictures come from **LeoCAD / LPub3D PNGs**, not table photos.
4. Clickable "pretty LEGO pages" live in **Figma**. Repo stores URL + frame map.
5. Table-check with Ian; patch `steps.md` / `model.ldr` when a step is wrong.

## Agent limits

- No BrickLink Studio MCP. No dragging bricks in LeoCAD's GUI.
- Agent **does** edit LDraw text in git. Agent **may** run LeoCAD CLI if the
  binary is installed. If it is not, stop at text; do not fake 3D renders.
- Figma is MCP: chrome + PNG assets + Next/Back. Figma cannot invent clutch.
- BOM qty must not exceed `kits/*/parts.txt`. Grep before adding a part.
- Element IDs stay in `parts.txt`. Kid-facing screens use color + "looks like".

## Complexity for Ian

- One action per instruction page (one piece or a tiny sub-assembly).
- After a mechanism (gears, pulley): a "try it with your hand" step before code.
- Coding last. Icon or Word Blocks unless the brief says otherwise. The
  program lives in `program.spike`; `python3 tools/blocks.py check` must
  pass before Figma. Shape is the contract — see `spike-blocks.md`.
- Combined-kit steps hint **which bin** (Essential tray vs Prime tray).
