# Build: rainforest-drop-zone

category: scenery
venue: class
hub: none
kits: 45345
skills: baseplates, stud-grid, tiles, minifigures, scenery, short-build
coding: none
age-fit: 6
figma: TBD

The Rainforest Drop Zone is the place the Seed Drone flies over: one white
8x16 plate stood narrow and deep, with a green wall down each long edge, a
tree at each end, grass, a frog, and a ranger holding the drone controller. A
band of red tiles crosses the lane between the walls. That red band is the
target the drone's Colour Sensor looks for.

It has no motor, no sensor and no program. That is the point: it gives the
drone somewhere to fly, and it gives a second child something to finish while
the first is still building the drone.

## Seventeen parts, because the class is 60 minutes

This build is deliberately the short one -- 17 parts and 9 steps, against the
drone's 60 and 31. Every step is a single kind of piece and nothing has to be
lined up by eye.

Cutting it down improved it, which was not the plan. The 8x16 plate is 8 studs
wide, so the two 1x16 green bricks sit one row in from each edge and leave a
lane exactly 4 studs across -- and two red 2x4 tiles fill that lane exactly,
wall to wall. On the earlier 16x16 island the red was a patch in open ground
and aiming at it was the hard part. Here the walls do the aiming: the drone
flies straight down the lane and there is no left-right error to make.

That relationship is load-bearing, so it survived a recount. The walls started
on the outermost column with a 6-stud lane and three red tiles, and there turn
out to be only two red 2x4 tiles in the box. Moving both walls in one stud kept
the property rather than the dimension -- a centred 4x4 patch with a stud of
white either side would have been the easy fix and would have handed the class
back the aiming error the layout exists to remove. The spare column outside
each wall became a verge, and the grass moved onto it.

Dropping the four orange corner marks was a second accidental gain. They used
to frame the target, and they were the one real sensor risk in the model --
red and orange, adjacent, at 1 cm. The green walls frame it better and cannot
be confused with red.

`parts.txt` lists everything that came off the longer version and why.

## The drop zone is red, and why that beats black

The obvious target colour for a burn scar is black, and that is what this
model used at first. It cannot be a LEGO part: **SPIKE Essential contains no
flat black piece at all** -- no black tile, no black plate, in any size. Every
black piece in the box is an axle, a peg, a damper, a camera or a wig. So the
target was a cut square of matte black paper.

Three Bright Red 2x4 tiles replace it, and the swap wins three ways:

- **It is a LEGO part.** Nothing to cut, nothing to tape down, and no page in
  the instructions that has no part and no picture.
- **It is a better sensor target.** Glossy black ABS bounces the Colour
  Sensor's own lamp straight back at it and can read as **none** rather than
  **black**. Red is a bright hue with no reflection failure mode.
- **It is more accurate to the story.** Cleared tropical soil is not black,
  it is orange-red -- rainforest clearing exposes laterite clay in very nearly
  this colour.

One consequence to know: the seed is red too, because Bright Red is the only
ball colour in the box. A dropped seed on white plate is a valid target, so
collect it between runs. `preflight.md` covers it.

## A trap the checker cannot catch

Six of these seventeen parts -- the trees, the grass, the frog, the ranger -- are
annotated `role: decorative` in `tools/connections.yml` with **no features at
all**. That exempts them from every joint and support check, which is correct
(a bush is not load-bearing) but means `ldrcheck` never asks whether they
landed on a stud. An earlier version of this model had grass stems and the
ranger sitting between stud rows and reported 0 problems.

So `model.ldr`'s header spells out the stud parity for each of them by hand,
and `preflight.md`'s table check 4 is "push on everything decorative." This is
the one part of the build with no machine backstop.

## A second trap: the kit list can invent parts

This build used four grass stems until someone opened the bag and counted two.
`kits/45345-essential/parts.txt` carried the stem on two rows of 2 -- design
`31576` (element 6188693) and design `2659` (element 6413056) -- as if they
were different pieces. They are one piece: a design ID and its mould revision.
LDraw settles it, because `31576.dat` is flagged `!LDRAW_ORG Part Alias` with
the title `=Plant Grass Stem`, and a leading `=` means the file redirects to
another part, here `15279.dat`.

The red tiles were a third instance, and a plainer one: the list simply said 3
where the box holds 2, with no alias involved. Three of the five recounts this
session went the same way, so the list's counts are now guilty until counted.

`ldrcheck kits` cannot catch this. It checks that every design ID a model
names exists in some kit's list; it has no way to know that two rows of that
list are the same physical brick. Two identical descriptions under different
design IDs are the signature, and the drone's rotor had the same bug in the
same session: four yellow 3M axles specified, two in the box.

Both rows are now merged, and the model names `15279.dat` -- the real part
rather than the redirect, the same rule that put `3713` and not `4265c` in the
mining truck.

## Shares nothing with the drone

Checked part by part: the diorama and the Seed Drone have **zero** LDraw parts
in common. Both models can be assembled and left on the table at the same time
out of a single 45345 box.

Only parts from `kits/45345-essential/parts.txt` are used. The finished
model has 17 parts over 9 build steps, followed by a mission page. See
`steps.md` for kid-facing instructions and `preflight.md` for the table
checks that CAD cannot prove -- above all, flying the drone across the
island at real height to confirm nothing catches the rotor.

Validate and preview everything:

```
python3 tools/ldrcheck.py check builds/rainforest-drop-zone/model.ldr
python3 tools/ldrcheck.py steps builds/rainforest-drop-zone/model.ldr
python3 tools/pages.py check builds/rainforest-drop-zone
python3 tools/pages.py preview builds/rainforest-drop-zone
```
