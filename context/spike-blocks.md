# SPIKE App code blocks

How the SPIKE App's three canvases actually work, so a program we write
for Ian is the program the App will run. The machine-readable index is
[`tools/spike/blocks.json`](../tools/spike/blocks.json), extracted from
the live app at <https://spike.legoeducation.com/>. Re-extract with
`python3 tools/spike_extract.py` when LEGO ships a new app.

This page is the prose that makes the JSON usable. Shape is the contract.

## Three canvases, one app

The app exposes three project types. The hub you connect changes the
palette, not the app:

| Canvas | App id | Who |
|---|---|---|
| Icon Blocks | `iconBlocks` (internally "doodle" / "horizontal") | Saturday class, early readers |
| Word Blocks | `wordBlocks` | Home builds, this index's default |
| Python | `python` | Prime hub only |

Essential **streams** the program to the hub (the tablet has to stay
connected). Prime **downloads** it (the hub runs alone). That is why a
class build that worked on the carpet with a laptop next to it can
"stop working" the moment you unplug Essential.

Python in this app is the **SPIKE 3** API (`from hub import light_matrix`,
`motor`, `motor_pair`, `distance_sensor`, `runloop`). Tutorials that still
open with `from spike import PrimeHub` are teaching a retired API: the
shipped bundle has zero occurrences of it.

## Shape is the contract

A block's *shape* is what it does to the program counter. The words on
the block are decoration until you know the shape.

| Shape | Looks like | What it does |
|---|---|---|
| **hat** | Bumpy top, nothing snaps above | Starts its own stack when an event fires |
| **stack** | Puzzle notch top and bottom | A command. Runs, then the next block runs. Names that start with *start* finish immediately and leave the motor going |
| **boolean** | Hexagon | Reports true/false. Does **nothing** on its own |
| **reporter** | Oval / pill | Reports a number or string. Does **nothing** on its own |
| **C** | Mouth | `forever` / `if` / `repeat` — holds a stack inside |
| **cap** | No notch underneath | `stop all` — nothing snaps under it |

The Distance Sensor "20" at the table was this. There are three different
blocks carrying a distance number:

- `flipperevents_whenDistance` — **hat**. `[PORT] when [COMPARATOR] [VALUE] [UNIT]`. Starts its own stack. Default value **8**, default unit **percent of 200 cm** (about 16 cm), not 20 cm.
- `flippersensors_isDistance` — **boolean**. `[PORT] is [COMPARATOR] [VALUE] [UNIT]?`. Default value **15** (about 30 cm). Must be dropped inside `wait until` or `if`.
- `flippersensors_distance` — **reporter**. `[PORT] distance in [UNIT]`. Just a number.

A fourth block, the near/far hat (`whenNearOrFar`, Icon: `horizontalevents_whenCloserThan`), is the one whose *label* contains 20: `near (< 20cm)` / `far (> 20cm)`.

Dragging a hexagon onto the canvas and expecting the next block to run
when it becomes true is the bug. The hexagon never advances the stack.
`wait until` + the hexagon is the version that lives inside a driving
loop. The hat is the version that *is* the loop's start.

## One motor line moving two things

Two different mechanisms, both real, both easy to hit on a 6-port hub.

**1. The port bubble is a multi-select.** Motor Word Blocks declare their
PORT argument as a `MultiplePortSelector` (opcode family `flippermotor_*`).
Default is `A`, but the app pre-checks every motor it can see. One "start
motor" line will spin the drill *and* a wheel if both ports are ticked.
Un-tick, or write one block per port.

The multi-select widget itself is a *field*, named
`flippermotor_multiple-port-selector`. There is **no** opcode called
`flippermotor_multiple` — that name only appears if you count opcodes with
a regex that stops at the hyphen. See "Counting blocks" below.

**2. Movement blocks have no port dropdown.** `set movement motors to [PAIR]`
(`flippermove_setMovementPair`, default `AB`) names the two motors.
Every `flippermove_*` block after that drives that pair. The pair is
also why a "move forward" line moves two wheels. Without the setter,
the move block has no motors — `blocks.py` flags `MOVEMENT_PAIR`.

The blocks that were "missing" on Prime are usually behind the Extensions
tray (the puzzle piece at the bottom of the palette):

| Extension | Prefix | Why you want it |
|---|---|---|
| More Motors | `flippermoremotor_` | power, relative position, stall, acceleration |
| More Movement | `flippermoremove_` | tank drive (`startDualSpeed`), acceleration, stop method |
| More Sensors | `flippermoresensors_` | raw colour, pitch/roll/yaw, acceleration |

`blocks.py` refuses a more-* opcode unless the program header lists that
extension.

## Two hubs

| | Essential Small Hub | Prime Hub |
|---|---|---|
| Ports | A, B | A–F |
| On-hub matrix | none | 5x5 (`flipperlight_lightDisplay*` / `turn on [MATRIX]`) |
| 3x3 colour matrix | accessory on a **port** (`[PORT] turn on [MATRIX]`) | same accessory, if you plug it in |
| Speaker | no | yes (`beep`, play sound) |
| Python | no | yes |
| Run mode | streaming | download |

Motors and sensors mix. Batteries and hubs do not. One hub per model.

`flipperlight_lightDisplay*` is the Prime 5x5. `flipperlight_lightColorMatrix*`
is the 3x3 accessory. Same English word "matrix", different hardware,
different blocks. Digger's face is the 5x5.

The whole `flipperdisplay_*` family (21 opcode strings, including
`flipperdisplay_ledImage`) is the **old** naming. It has no definition class
in the shipped app; the bundle keeps it only so a project saved by an older
release can be rewritten to `flipperlight_lightDisplay*` on load. Do not
write `flipperdisplay_*` in a `program.spike` — `blocks.py check` will
reject it as UNKNOWN, which is correct.

## Counting blocks

Grepping `flipper[a-z]+_[A-Za-z0-9]+` over the bundle returns **147**
strings. That is not 147 blocks, and the difference matters when you are
about to promise Ian a block that does not exist. Four unlike things share
that shape:

| Kind | Count | What it is |
|---|---|---|
| Definition classes | **90** | The real Word Blocks. Each one is a class in the bundle with a shape, a message, and arguments |
| Field / shadow names | 21 | Always hyphenated: `flippermotor_multiple-port-selector`, `flipperlight_color-matrix-selector`. Widgets *inside* a block |
| Legacy opcodes | 46 strings with no class | `flipperdisplay_*`, `flipperevents_whenTilted` (now `whenOrientation`), `flippermoremove_startDualPower` (now `startDualSpeed`), the 7 `flippermusic_*`. Kept for loading old projects |
| Test blocks | 8 | `flippertest_assert*`. Not in any palette |

A regex that truncates the hyphenated field names invents 13 opcodes that
do not exist. `blocks.json` records them under `not_blocks.phantom_bases`
so the mistake is not available to make twice.

The index therefore holds **88** Word Blocks: 80 from the bundle's 90
definition classes (8 are test blocks, 2 are dropdown shadows whose whole
message is a bare `[COLOR]` / `[PORT]` slot), plus the 8 Scratch core
control blocks the app reuses (`control_forever`, `control_if_else`,
`control_wait_until`, …), which are real palette blocks but are defined in
Scratch rather than in LEGO's extension code.

`stats` in `blocks.json` carries that arithmetic, and it has to add up:
`definition_classes_in_bundle = from_bundle + test_classes_skipped +
unmapped_definitions`. If a future app release breaks the parser, the sum
is where it will show.

Nothing is dropped silently. Every uncovered opcode string is listed with
a reason in `not_blocks.no_definition_class`, and the app's own 207-entry
known-opcode list is used to reject any opcode the extractor cannot prove
exists.

## Icon Blocks

Extracted as 33 opcodes (`horizontal*` in the bundle). They are pictorial
tiles, not Scratch-shaped words. `blocks.py` draws them as rounded squares
in a row when the program header says `canvas: icon` (or when every opcode
starts with `horizontal`). The index lists opcode, inferred label, and
shape (hat vs stack). The near-hat is `horizontalevents_whenCloserThan`.

There is no if/else on this canvas. The colour tile
(`horizontalevents_whenColor`) is a **hat**. Two hats snapped into one
row wait for the first colour, then the second — they do not match
either colour on their own. Matching green *or* blue means two separate
stacks, not one.

## `program.spike`

Opcode-anchored, indent for nesting. Header names the hub, any
extensions, and optionally `canvas: icon` (Icon Blocks) or
`canvas: word` (default). A boolean only appears under `@condition`.

```
hub: prime
extensions:

flipperevents_whenProgramStarts
  control_forever
    control_if_else
      @condition flippersensors_isDistance PORT=D COMPARATOR=closerThan VALUE=10 UNIT=cm
      @then
        flippermotor_motorStartDirection PORT=C DIRECTION=clockwise
      @else
        flippermotor_motorStop PORT=C
```

```
python3 tools/blocks.py check builds/<slug>
python3 tools/blocks.py preview builds/<slug>
python3 tools/blocks.py render builds/<slug>
python3 tools/blocks.py fixtures
```

`check` is the linter. `preview` writes `program.html`. `render` writes
`renders/program.svg` and `renders/program.png`.

Fixtures live in `tools/spike/fixtures/`. A `good-*` program must check
clean **and** draw. A `bad-*` program must raise the specific code named in
its `# expect:` line — "it errored somehow" is not a pass, because a
negative control that trips over a typo proves nothing. The one that
encodes the table bug is `bad-boolean-as-statement.spike`.

| Fixture | Must raise |
|---|---|
| `bad-boolean-as-statement` | `BOOLEAN_AS_STATEMENT` — the hexagon used as a line |
| `bad-essential-port-c` | `PORT` — Essential has only A and B |
| `bad-essential-5x5-matrix` | `HUB_BLOCK` — the 5x5 face is Prime-only |
| `bad-extension-not-added` | `EXTENSION` — More Movement was never added |
| `bad-movement-pair-unset` | `MOVEMENT_PAIR` — a move block with no pair |
| `bad-legacy-display-opcode` | `UNKNOWN` — `flipperdisplay_ledImage` is the retired name |
| `bad-icon-hats-chained` | `HAT_NESTED` — two colour hats in one row |
