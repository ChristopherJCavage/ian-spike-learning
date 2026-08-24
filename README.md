# Ian SPIKE Learning

Parts inventory and reference notes for Ian's LEGO Education SPIKE kits,
kept as flat, grep-able text files -- not a parts database, not a build
tracker. Just "what do we own and where did it come from."

## The kits

| Set | Name | Box piece count | Role |
|---|---|---|---|
| [45345](kits/45345-essential/) | SPIKE Essential | 449 | Ian's set for his Saturday ASU class (he's 6) |
| [45678](kits/45678-prime/) | SPIKE Prime | 528 | "Grow into it" set -- more motors, sensors, and hub ports |

Both kits run the **same SPIKE App**, and motors/sensors from either box
work on either hub -- see [`kits/how-the-kits-mix.md`](kits/how-the-kits-mix.md)
for the full rundown of what mixes and what doesn't.

We are **not** using Prime's official middle-school lesson plans -- just
the hardware. We do **not** own Expansion Set 45681 or any other add-on;
nothing here assumes extra parts beyond these two boxes unless a kit
folder for that set exists.

## Files

- `kits/45345-essential/parts.txt` -- full element-level parts list for
  SPIKE Essential 45345.
- `kits/45678-prime/parts.txt` -- full element-level parts list for
  SPIKE Prime 45678.
- `kits/combined-electronics.txt` -- just the motors/sensors/hubs/cables
  from both kits in one place, since those are what actually get shared
  across builds.
- `kits/how-the-kits-mix.md` -- narrative notes on how the two kits work
  together (and where they don't).

## Data source

Each `parts.txt` is built from LEGO's own Customer Service replacement-
parts registry (via [Brickset](https://brickset.com/), retrieved
2024-10-27), which lists exact element IDs, colors, and quantities. That
registry's total differs slightly from the marketing piece count on the
box (see the header comment in each file for why) -- treat `parts.txt` as
the accurate "what's in the bin" source, and the box number as the
rounded marketing figure.

## Usage

Everything is flat text on purpose, so plain `grep`/`awk` is the whole
toolkit:

```bash
# Find every motor across both kits
grep -i "motor" kits/*/parts.txt

# Find a specific sensor
grep -i "distance" kits/*/parts.txt kits/combined-electronics.txt

# Count pieces by color in one kit
awk -F'|' '{print $2}' kits/45345-essential/parts.txt | sort | uniq -c
```
