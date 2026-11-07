# Storage: getting all three kits out of LEGO's boxes

What to put the ~1,630 pieces in, and why. Counts in this file are computed
from `kits/*/parts.txt`, not from the box blurbs.

## Why the stock boxes fail

- **Essential 45345** -- yellow box with a sorting tray. Tolerable, but bulky
  for what it holds, and the tray has no lid, so it is a spill waiting to
  happen in a car.
- **Prime 45678** -- bigger yellow box, same problem, twice the volume.
- **Expansion 45681** -- a **cardboard box with no tray at all**. This is the
  urgent one. It is 606 pieces of loose Technic.

Stacked, the three take more shelf than the parts do.

## The constraint that decides the layout

Two house rules make this a storage problem and not just a sorting problem:

1. **Class builds are Essential-only** (`context/house-rules.md`). Ian's
   Saturday ASU class uses the Essential hub and Essential parts. If 45345 is
   dumped into one big pool, you can no longer hand him a class kit or check
   that a class build is legal.
2. **BOM quantity must not exceed `kits/*/parts.txt`.** Storage that shows you
   *how many* you have is worth more here than storage that just looks tidy.

So the answer is **three physical units**, not one mega-bin:

| Unit | Holds | Why separate |
|---|---|---|
| **Class kit** | All of 45345 Essential | Travels; must stay Essential-only |
| **Technic pool** | 45678 Prime + 45681 Expansion, merged and sorted by mould | Home builds mix these freely; Expansion is parts-only |
| **Electronics case** | Both hubs, both batteries, all motors/sensors/cables | Heavy, expensive, and does not belong in a parts tray |

Merging Prime and Expansion is safe: the Expansion has no hub and no battery,
and its parts are mostly duplicates of Prime moulds. Merging Essential in is
**not** safe, for the reason above.

## What the inventory actually looks like

| Kit | Pieces | Distinct moulds | Character |
|---|---|---|---|
| 45345 Essential | 472 | 118 | System: 142 bricks, 102 plates, 113 connectors, plus 45 minifig/animal parts |
| 45678 Prime | 551 | 97 | Technic: 279 connectors, 125 beams |
| 45681 Expansion | 606 | 92 | Technic: 320 connectors, 193 beams |

Moulds, not colours -- the same beam in two colours is one compartment.

Merged Technic pool: **1,157 pieces across 144 distinct moulds.**

This matters because the distribution is extremely top-heavy. The single
biggest line is **172 friction pegs** (`61332`), then 50 3M pegs (`42924`),
30 axle pegs (`6562`). Pins and bushes alone are 446 pieces -- 39% of the
pool. Any layout that gives pins one small compartment will fail immediately.

## Recommended: Plano 3700-series trays in a crate

The fishing-tackle instinct is right, and it is what FLL teams and a
University of Idaho Extension bulletin written specifically for SPIKE Prime +
Expansion both landed on.

All 3700-series boxes share a 14 x 9.13 in footprint and are interchangeable,
so mix depths freely:

- **Plano 3700** -- 2.00 in deep, 4-24 adjustable compartments. **The
  workhorse.** Sold in 4-packs for $24-35, so about $6-9 a box.
- **Plano 3750** -- same footprint and depth, but 3-28 compartments and fewer
  fixed ribs, so it can do **full-width** bays. ~$10 each. For long and round
  things.
- **Plano 3701** -- the shallow 1.38 in version, 5-34 compartments. More slots
  per box, but only sold as singles at $13-17, and shallow slots are the one
  real weakness of tackle boxes. Skip it unless a tray needs 30+ divisions.
- A milk crate holds these upright for free; the Plano Guide Series 4-By Rack
  is the tidy version, with a handle and a drop-down door.

Earlier drafts of this file recommended the shallow 3701 as the default. Price
and depth both argue the other way: the deeper 3700 costs half as much per box
in a 4-pack, and depth is what a 446-piece pin bay actually wants.

Technic geometry is the **best case** for tackle boxes: pins, beams, axles and
gears are chunky and easy to pinch out. The known weakness of these boxes --
prying flat tiles and plates out of a shallow slot -- barely applies to the
Prime/Expansion pool, and is exactly why Essential (102 plates) stays in its
own box rather than joining the pool.

### Tray plan for the Technic pool

Computed from the merged inventory. Six trays, sized so no tray needs more
compartments than it has:

| Tray | Contents | Pieces | Moulds | Box |
|---|---|---|---|---|
| 1 | Pins, bushes, axle pegs, wire clips | 446 | 30 | 3700, double-width pin bays |
| 2 | Straight beams, 3M-15M, by length | 109 | 20 | 3700 |
| 3 | Frames, angular beams, cross blocks, angle elements | 196 | 37 | 3700, group by family |
| 4 | Axles by length, gears, conical/angled wheels, worm | 170 | 35 | 3700, group by family |
| 5 | Wheels, tyres, turntables, racks, quarter-circle racks | 46 | 18 | **3750**, full-width bays |
| 6 | System oddments: round plates, tiles, dampers, V-belts, catches | 179 | 66 | 3750, group by family |

Trays 3, 4 and 6 have more moulds than any one box has compartments, so group
them by family -- all cross blocks together, all round tiles together -- rather
than one mould per slot. Tray 1 is the opposite problem: few moulds, huge
counts, so give the friction pegs a double-width bay.

Tray 5 needs the 3750's full-width bays. The 88 mm wheels, both turntable
sizes, the 13M rack and the 11x11 quarter-circle racks are longer than a 3700's
fixed ribs allow.

### Shopping list

| Item | Qty | Approx |
|---|---|---|
| Plano 3700, 4-pack | 1 | $24-35 |
| Plano 3750 | 2 | $20 |
| Milk crate, or Plano 4-By Rack | 1 | $0-15, or $48-56 |
| Electronics case (see below) | 1 | $35 |

Call it **$80-90** with a crate you already own. Live links are in
[`context/sources.md`](../context/sources.md). Buy the 4-pack first; the
carrier can wait.

A second 4-pack ($24-35) trays out the Essential kit too, and leaves two spare
boxes for growth. That is the cheapest way to retire the yellow tubs entirely.

## The electronics do not go in a tackle tray

Across all three kits that is 2 hubs, 2 rechargeable batteries, **6 motors**
(2 small angular, 2 medium angular, 2 large), **5 sensors** (3 colour, 1
force, 1 distance), the 3x3 colour matrix, and 2 USB cables. Eighteen objects,
all bulky, all expensive, two of them lithium.

Best option here is a **Milwaukee Packout Compact Organizer** (48-22-8435,
about 9.7 x 15.2 x 4.6 in, five removable bins, clear lid, gasketed, ~$30-35).
The bins are deep enough for a hub lying flat, the lid seals each bin so a
motor cannot migrate, and the case stacks with the rest of the Packout line if
this ever grows. A plain padded tool case or camera case works too -- the
requirements are depth, a lid, and not sharing a box with 172 loose pins.

**Phoenix note:** the hubs' rechargeable packs are lithium. Do not leave the
electronics case in a parked car in summer. The parts trays do not care; the
batteries do.

## Options considered

**Akro-Mils / IRIS drawer cabinets.** The AFOL favourite, and genuinely faster
than a tackle box for active building -- you pull a drawer instead of opening,
finding, and pinching. Best-in-class if the build table is fixed. Rejected as
the *primary* here only because the Essential kit has to travel to class and
drawers do not travel. Worth revisiting for the Technic pool if that pool
lives permanently on a bench: pins and bushes in particular would be nicer in
a drawer than a slot.

**Milwaukee Packout / Stanley / DeWalt organizers.** Excellent boxes, sealed
bins, modular and stackable, and far tougher than they need to be. Roughly 3-4x
the price per compartment of a Plano, and five bins per box is too coarse for
144 moulds. Right answer for the electronics, wrong answer for the pins.

**LEGO's own sorting trays** (45495, 16-pack, fits their small/medium/large
storage boxes). This is the in-ecosystem fix for the Expansion's cardboard box.
Keeps the bulky yellow-box footprint that is the complaint in the first place,
and LEGO does not sell the 45678 tray on its own.

## The trick worth stealing

The University of Idaho bulletin's real contribution is not the boxes, it is
the **parts card in the lid**: a printed sheet, one per tray, showing each part
to scale with its name and the quantity that belongs in that slot. It turns
cleanup into matching pictures, which is the difference between a 6-year-old
putting parts back correctly and a 6-year-old putting parts back somewhere.

We already hold the data those cards need -- name, quantity, design ID, colour
-- in `kits/*/parts.txt`. Generating tray cards from the inventory is a small
tool, in the same shape as `tools/pages.py`. Not built yet.

Sources are links in `context/sources.md`.

## Snap Circuits (not LEGO)

Separate from the three LEGO units above. Two small boxes of snap blocks:
Beginner SCB-20 (14 parts) and Jr SC-100 (about 30). Keep one labelled bin
per box so a block's home is its printed ID (`kits/scb20-beginner/parts.txt`,
`kits/sc100-jr/parts.txt`), plus a "both" cup for what the boxes share:
the 3-snap wires, S1 and S2. Keep the two battery holders apart and
labelled -- B3B is 4.5 V and B1 is 3 V, and Jr blocks only go on B1
(`context/snap-circuits.md`). Spare AA batteries stay out of the bins.
