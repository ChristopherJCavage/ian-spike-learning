# House rules

Constraints for humans and agents. If a build violates these, it is the
wrong build.

## People

- **Ian** is 6. Saturday ASU class uses **SPIKE Essential** (hub, App palette,
  and muscle memory). Keep class-safe builds Essential-only.
- **Chris** is the adult partner: bins, Figma, LeoCAD install, table check.
- Home builds may **mix** Essential + Prime parts. One hub per model.

## Hardware we actually own

- Own: Essential `45345`, Prime `45678`. See `kits/`.
- Do **not** assume Expansion `45681`, extra motors, or random bins.
- Motors/sensors mix across hubs; **battery packs do not**.
- One hub per build. Class default: Essential hub. Home machines that need
  extra ports or torque: Prime hub is OK.

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
- Coding last. Icon or Word Blocks unless the brief says otherwise.
- Combined-kit steps hint **which bin** (Essential tray vs Prime tray).
