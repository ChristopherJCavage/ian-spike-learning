# Builds

Original Ian + Chris projects. Not official LEGO units. Not a database.

**Kits** (`kits/`) = what we own. **Builds** (`builds/`) = what we make.
**Context** (`context/`) = words, house rules, LDraw/Figma conventions.

## Workflow

```
0. ldrcheck kits  `python3 tools/ldrcheck.py kits`
                what the checker can and cannot see across all three kits.
                Only needed when a build reaches for an unfamiliar part.
1. brief.md     Chris: theme, complexity, hub, sensors, done-when
2. git spec     Agent: steps.md + model.ldr + parts.txt  (grep kits first)
3. ldrcheck     `python3 tools/ldrcheck.py check builds/<slug>/model.ldr`
                must print 0 problems before any PNG is treated as proof
3b. ldrcheck steps  every intermediate state is buildable; no fat pages
4. PNGs         `python3 tools/pages.py render builds/<slug>`
                per-step camera + highlight from screens.md
4b. pages check `python3 tools/pages.py check builds/<slug>`
                0 STEP, steps.md, screens.md, and renders/ agree
4c. pages preview  `python3 tools/pages.py preview builds/<slug>`
                open preview.html and click through it as Ian
4d. code        `python3 tools/blocks.py check builds/<slug>`
                `program.spike` is opcode-anchored Word or Icon Blocks; shape, ports,
                hub, and extensions must pass before the picture is proof
                `python3 tools/blocks.py preview builds/<slug>`
                colourful blocks in program.html; render writes SVG/PNG
5. Figma        Clickable BI chrome; hero = PNG; URL on this build's README
                only after 4c is something you would hand him
                coding page = `renders/program.svg` after 4d is green
6. Table        Build with Ian; patch steps/ldr; then Figma
```

Pretty 3D is **LDraw + LeoCAD/LPub3D**, not Figma drawings and not table photos.
There is no LeoCAD MCP -- see `context/ldraw.md`. Figma MCP is for page chrome.
`ldrcheck` is this repo's linter for the `.ldr` files; LeoCAD does not
check clutch. See `builds/_template/preflight.md` for what still needs a
human after the checker is green.

### Teaching the checker a new part

`ldrcheck kits` sorts every design ID in `kits/*/parts.txt` into five
buckets. Only two of them are ever work:

- **library** -- LDraw already emits the holes and studs. Nothing to do.
- **annotated** -- `tools/connections.yml` already fills the gap.
- **silent** -- the part resolves to a `.dat`, but it emits no clutch at
  all. Measure it (`ldrcheck measure`, `ldrcheck holes`) and add
  `features:`, or mark it `decorative` if it genuinely has none.
- **unmapped** -- no LDraw file at that number. LEGO renumbers moulds;
  find the original number and add it to `tools/ldraw_aliases.json`.
  See `context/sources.md` for where the cross-reference lives.
- **proxy** -- no LDraw geometry exists at all (printed heads, the dog,
  cables). These stay table-swaps forever.

`ldrcheck kits --strict` exits non-zero while anything is silent or
unmapped. As of the 45681 pass, all three kits are at zero of both.
Male shafts are always hand-written: LDraw marks holes, never shafts.

**An annotation is a claim until a fixture proves it.** The audit shows
that the checker *sees* a part, never that it sees it correctly -- a hole
on the wrong axis sits in the "annotated" column looking exactly like a
right one. So every hand-written entry gets a `good-` fixture that mates
the part the way it is meant to mate, and the family gets one `bad-`
fixture holding the same part in a wrong orientation. The negative control
is the half that matters: without it, a rule that says yes to everything
also passes. Two annotations written during the 45681 pass turned out to
be wrong, and both were found this way, not by re-reading them.

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
  code.md        # Icon/Word, ports, success; program.spike is the spec
  program.spike  # opcode-anchored Word or Icon Blocks; `python3 tools/blocks.py check`
  preview.html   # generated click-through; `python3 tools/pages.py preview`
  program.html   # generated block picture; `python3 tools/blocks.py preview`
  renders/       # exported PNGs (empty until LeoCAD exists)
```

## Tags (README header)

```
category: machine | vehicle | creature | story | scenery
venue:    class | home
hub:      essential | prime | none
kits:     45345, 45678
skills:   gears, pulleys, ...
coding:   icon | word | python | none
age-fit:  6
```

`scenery` is a build with no electronics at all -- a place for another build
to work in, like `rainforest-drop-zone`. It still gets the full treatment
(`model.ldr`, `steps.md`, `screens.md`, `parts.txt`, `preflight.md`, step
renders) because a baseplate diorama is exactly where stud-grid parity
mistakes hide: two plates can look joined in a render and hinge apart on the
table. It skips `code.md`, `program.spike` and the `blocks.py` steps.

Class = Essential hub and Essential-only parts. Home = mix allowed, still no
`45681`.

## New build

Copy [`_template/`](_template/) to `builds/<slug>/`. Do not treat `_template` as
a real project. First real slug waits on a brief -- no default machine.
