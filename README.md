# Ian SPIKE Learning

Grep-able notes for Ian's LEGO Education SPIKE kits and **our** builds.
Not a parts database. Not official LEGO curriculum.

| Folder | What it is |
|---|---|
| [`kits/`](kits/) | What we **own** (inventories + how the two boxes mix) |
| [`builds/`](builds/) | What we **make** (briefs, LDraw, step lists, Figma maps) |
| [`context/`](context/) | Words, house rules, LDraw/Figma conventions for the next agent |

## Kits

| Set | Name | Box piece count | Role |
|---|---|---|---|
| [45345](kits/45345-essential/) | SPIKE Essential | 449 | Saturday ASU class (Ian is 6) |
| [45678](kits/45678-prime/) | SPIKE Prime | 528 | Grow-into set -- more motors, sensors, ports |
| [45681](kits/45681-expansion/) | SPIKE Prime Expansion | 604 | Add-on: no hub, no battery. Turntables, gears, big wheels |

Same **SPIKE App**; motors/sensors mix; batteries/hubs do not. Details:
[`kits/how-the-kits-mix.md`](kits/how-the-kits-mix.md).

We are **not** using Prime's official middle-school lessons -- hardware only.

- `kits/45345-essential/parts.txt`
- `kits/45678-prime/parts.txt`
- `kits/45681-expansion/parts.txt`
- `kits/combined-electronics.txt`
- `kits/how-the-kits-mix.md`
- `kits/storage.md` -- what to put the pieces in, sized from the inventories

Piece counts in `parts.txt` come from LEGO's replacement-parts registry via
[Brickset](https://brickset.com/) (2024-10-27) and can differ from the box
blurb -- see the header in each file.

## Builds

Original projects. Copy [`builds/_template/`](builds/_template/) when a brief
exists. Pretty instruction pages: LDraw/LeoCAD PNGs + Figma chrome --
[`builds/README.md`](builds/README.md), [`context/ldraw.md`](context/ldraw.md),
[`context/instruction-screens.md`](context/instruction-screens.md).

## Context

- [`context/glossary.md`](context/glossary.md) -- Education vs catalog vs our tags
- [`context/house-rules.md`](context/house-rules.md) -- Ian, kits, what agents must not assume
- [`context/sources.md`](context/sources.md) -- links only (no dumped PDFs)
- [`context/connection-language.md`](context/connection-language.md) -- how we write steps
- [`context/ldraw.md`](context/ldraw.md) -- LDraw text + LeoCAD CLI (no MCP)
- [`context/instruction-screens.md`](context/instruction-screens.md) -- Figma BI chrome
- [`context/spike-blocks.md`](context/spike-blocks.md) -- Word/Icon/Python blocks; shape is the contract

## Setup

The checkers in [`tools/`](tools/) are stdlib-only and need nothing. Only
rendering instruction pages needs more: LeoCAD at
`/Applications/LeoCAD.app`, and

```bash
python3 -m pip install -r requirements.txt
```

## Grep

```bash
grep -i "motor" kits/*/parts.txt
grep -i "distance" kits/*/parts.txt kits/combined-electronics.txt
awk -F'|' '{print $2}' kits/45345-essential/parts.txt | sort | uniq -c
```
