# LDraw and LeoCAD

How 3D exists in this repo. There is **no LeoCAD MCP**. Pretty instruction
PNGs come from CLI (or you clicking File > Export). The model the agent
edits is plaintext LDraw.

LEGO does not sponsor or endorse LDraw/LeoCAD.

## Files

- `builds/<name>/model.ldr` -- one model, `0 STEP` between instruction pages.
  Step *n* in `steps.md` = *n*th `0 STEP` (LeoCAD steps start at 1).
- Optional `.mpd` if we later split submodels; start with a single `.ldr`.
- `builds/<name>/renders/step-NNN.png` -- exported stills for Figma.

Minimal legal LDraw (placeholder until a real model exists):

```
0 Ian Crane (stub)
0 Name: model.ldr
0 Author: ian-spike-learning
0 !LICENSE Licensed as content of this repo; parts from LDraw library
0 STEP
```

A real part line looks like:

```
1 <color> <x> <y> <z> <a> <b> <c> <d> <e> <f> <g> <h> <i> <part>.dat
```

- **color** -- LDraw color code (e.g. 0 black, 15 white, 4 red). Map to names
  in `parts.txt` / `steps.md`.
- **x y z** -- LDraw units (1 brick stud pitch = 20 LDU = 8 mm).
- **a..i** -- 3x3 rotation matrix.
- **part.dat** -- LDraw design name (often matches design ID, not element ID).

Agent: author and patch these lines in git. Do not pretend clutch is proven
until someone looks at a PNG or the GUI.

## Install LeoCAD (Chris, Mac)

1. <https://www.leocad.org/> -- download the macOS app (GPLv2).
   Source: <https://github.com/leozide/leocad>
2. First launch pulls / locates the **LDraw parts library**. If parts are
   missing, set the library path in Preferences (see LeoCAD docs).
3. CLI (Homebrew cask or the app bundle binary), typical:

```bash
# One step (steps are 1-based). Exact binary path may be:
#   /Applications/LeoCAD.app/Contents/MacOS/LeoCAD
LeoCAD model.ldr -i renders/step-012.png -w 1600 -h 1100 -f 12 -t 12 --camera-angles 55 225 --fade-steps --highlight
```

Flags (see <https://www.leocad.org/docs/cli.html>):

- `-i` / `--image` -- write PNG/JPG and exit
- `-w` `-h` -- pixel size (this repo uses 1600x1100)
- `-f` / `--from` and `-t` / `--to` -- step range
- `--viewpoint home` -- isometric-ish default. Ignored if `--camera-angles`
  or `--camera` is set.
- `--camera-angles <lat> <lon>` -- per-page camera, stored in `screens.md`
- `--fade-steps` -- previous parts faded (official-BI vibe)
- `--highlight` -- outline the parts added on this step
- `-l` / `--libpath` -- parts library if not default

The exported PNG is **RGBA with a transparent background**. `--fade-steps`
writes prior parts at alpha 128. Composite onto a white page (the HTML
preview, or Figma) and the history goes grey while the new piece stays
in colour. There is no CLI background-colour flag; the installed binary
does not honour `0 !LEOCAD MODEL BACKGROUND COLOR` either.

Per-page cameras live in `screens.md`. Render them with
`python3 tools/pages.py render builds/<slug>` (LeoCAD needs to run
outside a sandbox -- it talks to WindowServer).

If `LeoCAD` is not on `PATH`, the agent should try the `.app` path once, then
stop: **do not invent PNGs**. Leave `renders/` empty.

## LPub3D (optional)

<https://trevorsandy.github.io/lpub3d/> -- open-source **booklet** pages
(callout boxes, white page). Use when we want a PDF or denser official look.
Figma can still take those page PNGs as the hero. Not required for stubs.

## SPIKE electronics gaps

The LDraw library is incomplete for Education hubs/motors/sensors. Options:

1. Community / unofficial `.dat` parts if they exist for SPIKE Prime/Essential.
2. **Proxy:** a similarly sized Technic brick + comment in `steps.md`
   ("this box is the Prime Hub; real part sits here").
3. Photo of the real hub on that Figma page only for electronics steps.

Never BOM a part we do not own just because LDraw has a pretty file.

## What the agent does vs Chris

| Job | Who |
|---|---|
| Write/patch `model.ldr` + `steps.md` | Agent |
| `python3 tools/ldrcheck.py check` until 0 problems | Agent |
| `python3 tools/ldrcheck.py steps` until 0 problems | Agent |
| `python3 tools/pages.py check` / `preview` | Agent |
| `grep` BOM against `kits/*/parts.txt` | Agent |
| Install LeoCAD + library | Chris (once) |
| `python3 tools/pages.py render` (LeoCAD CLI) | Agent, outside the sandbox |
| Drag bricks in LeoCAD GUI | Chris, if a step is nonsense |
| Figma chrome + Next | Agent (MCP) |
| Table-build with Ian | Chris + Ian |

Skip: BrickLink Studio, LDCad, committing `.fig` binaries.
