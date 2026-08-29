# Measured geometry -- Mining Drill Truck

Every number here came out of the official LDraw library via
`tools/ldrcheck.py`, not from looking at a render. Re-derive any of it with:

    python3 tools/ldrcheck.py measure 45601
    python3 tools/ldrcheck.py holes 45601

## Conventions

LDraw units, 20 LDU per Technic module. **+Y is down.** For this truck,
front is +Z, rear is -Z, and the ground plane is y = +70 (wheel radius).

## The rule that broke the last two attempts

Every hole and stud primitive in LDraw points along **its own Y axis**. A
Technic beam placed with the identity matrix therefore lies *flat*, 18 LDU
across in X, 20 LDU tall in Y, with its holes running **vertically**.

That means a beam laid out along Z with the identity matrix cannot take an
axle running along X. The axle passes through solid plastic. Both earlier
drafts did exactly this and the renders happily showed a wheel on an axle.

To run a beam along Z with its holes along X -- an on-edge side rail that can
carry a transverse axle -- rotate it 90 degrees about Z:

    1 <colour> <x> <y> <z> 0 1 0 -1 0 0 0 0 1 64871.dat

The same applies to the frames: `39790` and `39794` lie in the XZ plane, 20
thick in Y, and their face holes are vertical.

## Sizes

Size is the full bounding box. Origin is where LDraw puts (0,0,0).

| Part | LDraw | Size x,y,z | Notes |
|---|---|---|---|
| Prime Hub | 45601 | 140, 80, 220 | origin at bottom face centre; body runs y -80..0 |
| Large Motor | 54675 | 100, 80, 180 | disc at (0,-50,0), on a *long* face |
| Medium Angular Motor | 54696p01 | 60, 80, 179 | disc at (0,-50,0) |
| Small Angular Motor | 68488 | 60, 80, 99 | disc at (0,-50,0) |
| Distance Sensor | 37316 | 140, 58, 79 | eyes face -Z |
| Wheel dia 56 | 39367 | 140, 140, 35 | native axis **Z**, half-thickness 17.5 |
| Frame 11x15 | 39790 | 220, 20, 300 | open centre, ring members at x +-100 and z +-140 |
| Frame 7x11 | 39794 | 140, 20, 220 | |
| Beam frame 5x7 | 64179 | 100, 20, 140 | holes on all three axes |
| I-frame 3x5 | 14720 | 58, 20, 98 | vertical *and* horizontal holes -- the axle carrier |
| Beam 15M | 64871 | 18, 20, 298 | holes at z 0, +-20 ... +-140 |
| Beam 11M | 64290 | 18, 20, 218 | |
| Beam 7M | 32524 | 18, 20, 138 | |
| Pin 2M | 61332 | 40, 15, 16 | 20 LDU into each part |
| Pin 3M | 42924 | 60, 15, 16 | spans a 20 LDU gap |
| Bush | 4265c | 18, 18, 10 | |
| Axle 4M / 7M / 9M / 11M | 3705 / 44294 / 60485 / 23948 | 79 / 139 / 179 / 219 along **X** | |
| Cone 2x2x2 | 14918 | 40, 52, 40 | stacking pitch 48 |
| Brick 2x2x3 | 30145 | 40, 76, 40 | |
| Plate 2x8 | 3738 | 160, 12, 40 | |

## Where the mounting holes are

Hub `45601`, relative to its origin at the bottom face:

- **Sides** (x = +-70), axis X: y = -10 with z = -80, -40, 40, 80; y = -30 and
  y = -50 with z = -80, 80. Eight per side.
- **Bottom** (y = 0), axis Y: x = +-60 with z = +-60 and +-100; x = +-20 with
  z = +-100. Twelve total.
- **Ends** (z = +-110), axis Z: x = +-40, y = -10, -30, -50.
- **Top** (y = -80), axis Y: x = +-60, z = +-100.

Large Motor `54675`, relative to its origin:

- **Disc face** (y = -50): four holes at (+-20, -50, 0) and (0, -50, +-20).
- **Sides** (x = +-50), axis X: y = +-20, z = -20, 20, 100, 140.
- **Back** (y = 30): x = +-40, z = 0, 80, 120.

I-frame `14720` is a converter with both vertical and horizontal holes, but
this truck does not hang it under the Hub: the 50 LDU drop from the Hub
bottom (y = -50) to the axle (y = 0) is not a pin-hole grid. The 5x7 frame
`64179` on the Hub **front face** is the carrier instead (see below).

## Hub side-hole map, in this truck's world coordinates

This Hub sits at world y = -50 (see the verified core below), so its local
side-hole rows (listed above relative to the Hub's own origin) land at:

| World y | Local y | z available | Holes per side |
|---|---|---|---|
| -60 | -10 | -80, -40, 40, 80 | **four** |
| -80 | -30 | -80, 80 | two |
| -100 | -50 | -80, 80 | two |

The sensor gantry's rails were first pinned to the Hub at y = -80 with one
pin each, where each side offers only the z = ±80 pair -- one usable line,
so both rails landed on the *same* z and the only way to reach the sensor
beyond them was a second pin further out on that identical line. Collinear
pins, and per "Rigidity is a property of the subassembly, not the part" in
`context/ldraw-connections.md`, a hinge.

The fix used two pins per rail instead of a second rail: y = -60 reaches
the four-hole row, so z = -80 and z = 40 give two pins per side on
genuinely different lines and the gantry cannot hinge -- but that row sits
*inside* the front wheels. The wheels are 56 dia. discs, solid most of the
way through, spanning world y = -70..70; a rail at y = -60 runs its entire
length flush against wheel material (measured: the rail's outer face and
the wheel's inner face land on the exact same x = 90 plane, zero
clearance -- `CONTACT WITHOUT JOINT` catches this, but it is really a
moving-part hazard, not a static seam). y = -80 and y = -100 both clear
the wheels' y ≤ -70 edge (by 10 and 30 LDU), which is why the finished
gantry uses those two rows instead, one rail per row, each pinned at that
row's own z = -80 and z = 80 holes. The catch: reaching z = -80 *and*
z = 80 *and* the z = 200 hand-off to the sensor needs a beam long enough
to span all three -- a 9M beam (180 LDU) covers z = 80 through 200 but
falls short of z = -80 entirely, so both rails are the kit's longest beam,
a 15M (298 LDU).

## Two findings that change the plan

**1. The Large Motor cannot coaxially drive a transverse rear axle here.**

The output disc sits on a long face, so its axis is perpendicular to the
motor's 180 LDU length. Putting the disc on an axle that runs along X forces
that 180 length to run fore-aft. The Hub is another 220 fore-aft. 180 + 220 =
400, and the longest beam in the kit is 298. The motor also cannot tuck under
the Hub: mounted coaxially it straddles the axle line from y -50 to +50, and
the Hub's underside is only 60 LDU above the ground.

So "Large Motor drives the rear axle" is not buildable as written, no matter
how the coordinates are nudged. **Decided instead: two Large Motors, one per
side, each driving its own rear wheel off its output disc.** Skid steer, so
the truck can turn, and the Hub bolts straight down onto the two motor tops.

**2. Wheels and side rails compete for the same space.**

Rails pinned to the Hub's side holes sit at x = +-80 and occupy 70..90. A
wheel is 35 thick, so its centre cannot come inboard of 107.5. An 11M axle
only reaches 109.5, leaving 19.5 LDU of axle inside a 35 LDU wheel. It holds,
but the wheels want to be carried by something narrower than the Hub -- for
example an I-frame `14720` hung under the Hub's bottom holes.

## The verified core

These eleven lines (plus six hub-tie pins) pass `ldrcheck check` with
zero problems as a core -- the model header carries `0 !LDRCHECK GROUND 70`.
Build the rest of the truck outward from them and do not move the motors,
rear axles, wheels, or Hub.

    1 16 -40 0 -80 0 1 0 -1 0 0 0 0 1 54675.dat
    1 16 40 0 -80 0 -1 0 1 0 0 0 0 1 54675.dat
    1 14 -90 0 -80 1 0 0 0 1 0 0 0 1 4519.dat
    1 14 90 0 -80 1 0 0 0 1 0 0 0 1 4519.dat
    1 16 -107.5 0 -80 0 0 1 0 1 0 -1 0 0 39367.dat
    1 16 107.5 0 -80 0 0 1 0 1 0 -1 0 0 39367.dat
    1 0 -60 -50 -100 0 1 0 1 0 0 0 0 -1 61332.dat
    1 0 -60 -50 -60 0 1 0 1 0 0 0 0 -1 61332.dat
    1 0 -20 -50 -100 0 1 0 1 0 0 0 0 -1 61332.dat
    1 0 60 -50 -100 0 1 0 1 0 0 0 0 -1 61332.dat
    1 0 60 -50 -60 0 1 0 1 0 0 0 0 -1 61332.dat
    1 0 20 -50 -100 0 1 0 1 0 0 0 0 -1 61332.dat
    1 16 0 -50 0 1 0 0 0 1 0 0 0 1 45601.dat

What that gives, in world coordinates:

- Motors occupy x -90..-10 and 10..90, y -50..50, z -110..70. Discs face
  outward at x = +-90, on the rear axle line z = -80.
- The wheel hub is recessed 7.5 LDU, so a wheel cannot sit flat against the
  flush disc. The 3M axles bridge that gap and run through the whole hub.
  Leaving them out leaves the wheels floating -- the checker catches it.
- Hub bottom lands on the motor tops at y = -50 and spans y -130..-50, so
  the whole truck is 200 LDU tall on a ground plane of y = +70.
- Six vertical pins tie the Hub down (three per motor). The Hub's bottom
  holes at z = 60, x = +-60 stay empty so the sensor rails can pass.

The front axle is **not** hung from the remaining bottom holes. Those sit
at y = -50; the axle line is at y = 0; that 50 LDU drop is not a pin-hole
grid. Instead a 5x7 frame `64179` stands on the Hub's **front face**
(holes at world (+-40, -60, 110) axis Z), pinned with two 2M pegs. The
frame centre is at y = -40 so its bottom (y = 30) clears the ground plane
(y = 70) by 40 LDU -- at y = 0 the frame sat on the floor. Side holes at
y = 0, z = 120 (two hole-rows below the new centre) still carry the 11M
front axle. The drill motor pins to a
7M beam on that frame, entirely in front of the axle so the two do not
share volume.

Cab furniture uses real stud clutch. The seat (`4079`) sits 8 LDU above the
front deck so its annotated underside tubes occupy the plate's studs, not
the plate's own volume. The round dish (`35394`) lies flat on a rear-deck
stud; standing it on its rim cannot attach to anything. The minifig has no
clutch primitives -- it stands on the deck beside the seat, facing +Z, and
is marked decorative so a missing Technic joint is not a defect. Sit the
figure in the seat at the table. Numeric claims about this geometry live in
`0 !LDRCHECK` assertions at the top of `model.ldr`, not only in comments.

## Parts with no LDraw geometry

`42142` (double cross block) and `40147` (beam 1x2 with cross and hole) are
not in the library, so the checker cannot see them. The three existing
proxies -- centre shell `40995`, printed head `26881`, dog `93239` -- are in
the same position. Anything built on these is unverified.
