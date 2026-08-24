# Glossary

LEGO Education words vs brick-catalog words vs tags we use in this repo.
Plain language. Not a dump of official PDFs.

## LEGO Education (classroom / App)

- **Set / kit** -- the box. Ours: SPIKE Essential `45345`, SPIKE Prime `45678`.
  Expansion `45681` exists; we do not own it.
- **Hub** -- the programmable brick. Essential Small Hub: **2** I/O ports and a
  built-in **3x3** light matrix. Prime Hub: **6** ports, **5x5** matrix, speaker,
  IMU. Motors and sensors mix across hubs; battery packs do not.
- **Port** -- letter on the hub where a motor or sensor plugs in (Essential:
  A--B. Prime: A--F). Always name the port in `steps.md` and `code.md`.
- **Unit** -- a themed sequence of official lessons (e.g. Great Adventures).
  Teacher-facing. We do not copy these into this repo.
- **Lesson** -- one 45--90 min official session. Pedagogy is **5E**: Engage,
  Explore, Explain, Elaborate, Evaluate.
- **Lesson plan** -- teacher paperwork. Not a kid-facing object. Not a folder
  name here.
- **Building Instructions (BI)** -- student-facing steps (SPIKE App or PDF).
  Official look: white page, isometric 3D, new-parts callout, step badge.
- **Getting Started** -- in-app tutorials. Not a unit.
- **Model** -- the thing you build.
- **Criteria / constraints** -- design-brief language ("it has to lift a
  minifig", "only parts from these two bins").
- **Icon Blocks** -- picture coding, youngest.
- **Word Blocks** -- Scratch-like words.
- **Python** -- text coding in the same SPIKE App. Later, not Saturday class.

## Brick catalog (already in `kits/`)

- **Element ID** -- LEGO's color+mold SKU (what Pick-a-Brick uses). In
  `parts.txt`.
- **Design ID** -- the mold only, color-blind.
- **Category** (BrickLink / Rebrickable) -- *part type* (Bricks, Plates,
  Technic). That is **not** a lesson category and not our build tags.

## Fan 3D stack (FOSS)

- **LDraw** -- plaintext 3D format + community parts library. Files: `.ldr` /
  `.mpd`. This is the model the agent edits in git.
- **LeoCAD** -- GPLv2 Mac/Windows/Linux app. GUI you click; CLI the agent can
  run to export step PNGs. No MCP.
- **LPub3D** -- open-source booklet layout (isometric page, parts box). Optional.
- **Studio (BrickLink)** -- proprietary freeware. **Out of scope.** No MCP, no
  workflow in this repo.

## Our repo tags (on a build README)

- **category:** machine | vehicle | creature | story
- **venue:** class (Essential hub, Saturday-safe) | home (combined kits)
- **hub:** essential | prime
- **kits:** 45345, 45678
- **skills:** gears, pulleys, levers, color-sensor, loops, ...
- **coding:** icon | word | python
- **age-fit:** 6

## Community slang

- **MOC** -- My Own Creation (not an official set).
- **Alt build** -- different model from the same box.
- **Inventory / BOM** -- parts list. Ours stay grep-able `parts.txt`.
