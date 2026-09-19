# Code -- Mining Drill Truck

SPIKE App, **Word Blocks** (per brief). The runnable spec is
[`program.spike`](program.spike). Check and picture:

```
python3 tools/blocks.py check builds/mining-drill-truck
python3 tools/blocks.py preview builds/mining-drill-truck
python3 tools/blocks.py render builds/mining-drill-truck
```

Open `program.html` and click through it before Figma. The SVG in
`renders/program.svg` is what Figma imports. See
[`context/spike-blocks.md`](../../context/spike-blocks.md) for why the
Distance Sensor block with a number on it does not, by itself, move the
program to the next line.

## Ports

| Port | Device | Role |
|---|---|---|
| A | Large Motor (left) | Drives the left rear wheel |
| B | Large Motor (right) | Drives the right rear wheel |
| C | Small Angular Motor | Spins the drill bit |
| D | Distance Sensor | Watches what's in front of the drill |

Skid steer: no shared rear axle. A and B are **two separate motor
blocks**, not one multi-select line and not the pink Movement pair.
The motor port bubble is a multi-select — if both A and C are ticked on
one "start motor" block, the drill and a wheel spin together. That is
why the program names one port per line.

The hub face is the Prime **5x5** (`turn on [MATRIX]` /
`flipperlight_lightDisplayImageOn`), not the 3x3 colour-matrix accessory.

## Success

Digger rolls forward on its own. When something gets within about **4
inches (10 cm)** of its nose, the drill spins up and the hub's face
flips from a smiley to a focused/determined face. Back the object away
and the drill stops — smiley face comes back.

## Program notes

The distance test is the **boolean** `is closer than 10 cm`, dropped
inside `if / else` inside `forever`. It is not the hat "when closer
than", and it is not the oval that only reports a number. Default
units on those blocks are **percent of 200 cm**, so this program sets
`UNIT=cm` and `VALUE=10` on purpose.

Motors A and B never stop in this version — Digger just keeps rolling
forward. A future version could split their speeds to turn, or add
More Movement tank drive (`startDualSpeed`) from the Extensions tray.

Word Blocks only for this brief. Prime Python equivalent of the
distance test is `distance_sensor.distance(port.D) < 100` (millimetres).
Essential has no Python canvas.
