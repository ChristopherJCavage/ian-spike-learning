# Code -- Chameleon Colour-Match

SPIKE App, **Icon Blocks** (Saturday class). The runnable spec is
[`program.spike`](program.spike). Check and picture:

```
python3 tools/blocks.py check builds/rainforest-chameleon
python3 tools/blocks.py preview builds/rainforest-chameleon
python3 tools/blocks.py render builds/rainforest-chameleon
```

Open `program.html` and print it before class. The SVG in
`renders/program.svg` is what Figma imports. A Word Blocks if/else
version is in [`program-word.spike`](program-word.spike) for home.

See [`context/spike-blocks.md`](../../context/spike-blocks.md). Icon
Blocks have no if/else. The colour tile is a **hat**
(`horizontalevents_whenColor`). Two hats in one row wait for the first
colour, then the second. Matching either colour means **four separate
stacks**, one per pad.

## Ports

| Port | Device | Role |
|---|---|---|
| A | Colour Sensor | Reads the pad under the belly |
| B | 3x3 Colour Light Matrix | The chameleon's skin |

Both ports on the Essential hub are used. There is no motor on this
animal, and no on-hub matrix -- the 3x3 accessory is the whole display.
Use `horizontaldisplay_ledMatrix` (port B), never the Prime 5x5 face.

## Success

Slide a pad under the belly. The back lights the same colour (blue,
yellow, green). Slide a **bright red** pad and the back goes warning-red
instead -- the "don't eat me" idea. No pad leaves the last colour
showing: Icon Blocks have no easy "off" stack for "I see nothing."

## Program notes

Four yellow **when colour** hats, each with one purple 3x3 tile:

- green pad -> matrix all green
- blue pad -> matrix all blue
- yellow pad -> matrix all yellow
- red pad -> matrix all red (warning)

There is no "copy whatever colour you see" reporter. Do not add
`stop other stacks`, and do not hang a long "play until done" sound on
those rows -- sounds play from the tablet, not the hub.

Essential has no Python canvas.
