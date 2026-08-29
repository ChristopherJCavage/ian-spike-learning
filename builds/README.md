# Builds

Original Ian + Chris projects. Not official LEGO units. Not a database.

**Kits** (`kits/`) = what we own. **Builds** (`builds/`) = what we make.
**Context** (`context/`) = words, house rules, LDraw/Figma conventions.

## Workflow

```
1. brief.md     Chris: theme, complexity, hub, sensors, done-when
2. git spec     Agent: steps.md + model.ldr + parts.txt  (grep kits first)
3. ldrcheck     `python3 tools/ldrcheck.py check builds/<slug>/model.ldr`
                must print 0 problems before any PNG is treated as proof
4. PNGs         LeoCAD CLI (if installed) -> renders/step-NNN.png
5. Figma        Clickable BI chrome; hero = PNG; URL on this build's README
6. Table        Build with Ian; patch steps/ldr; then Figma
```

Pretty 3D is **LDraw + LeoCAD/LPub3D**, not Figma drawings and not table photos.
There is no LeoCAD MCP -- see `context/ldraw.md`. Figma MCP is for page chrome.
`ldrcheck` is this repo's linter for the `.ldr` files; LeoCAD does not
check clutch. See `builds/_template/preflight.md` for what still needs a
human after the checker is green.

## Folder layout

```
builds/<slug>/
  README.md      # tags, Figma URL, hub, kits
  brief.md
  parts.txt      # BOM vs kits; LDraw names where known
  steps.md       # human connection language (same numbers as 0 STEP)
  model.ldr      # FOSS 3D
  screens.md     # step -> png -> Figma frame
  geometry.md    # measured hole maps; assertions live in model.ldr
  preflight.md   # what ldrcheck cannot see
  code.md        # Icon/Word, ports, success
  renders/       # exported PNGs (empty until LeoCAD exists)
```

## Tags (README header)

```
category: machine | vehicle | creature | story
venue:    class | home
hub:      essential | prime
kits:     45345, 45678
skills:   gears, pulleys, ...
coding:   icon | word | python
age-fit:  6
```

Class = Essential hub and Essential-only parts. Home = mix allowed, still no
`45681`.

## New build

Copy [`_template/`](_template/) to `builds/<slug>/`. Do not treat `_template` as
a real project. First real slug waits on a brief -- no default machine.
