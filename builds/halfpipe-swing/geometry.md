# Measured geometry -- halfpipe-swing

Every number here comes out of `tools/ldrcheck.py` or `tools/swing.py`,
not from looking at a render. Re-derive with:

    python3 tools/ldrcheck.py measure <part>
    python3 tools/ldrcheck.py holes <part>
    python3 tools/swing.py builds/halfpipe-swing --steps 15-28 \
        --roll 46372 -5 --angles -60 -37 -30 -11 0 11 30 37 60

## Conventions

LDraw units, 20 LDU per Technic module. **+Y is down.** Declared in the
model header:

    0 !LDRCHECK GROUND 242
    0 !LDRCHECK FRONT +Z

The world origin is the **pivot**: the Large Motor's output axle, pointing
+Z (at Ian). Everything that swings turns about the Z axis through the
origin, so "how close does it get" is a question about radii, not
positions.

## Sizes

| Part | LDraw | Size x,y,z (as measured, local) | Notes |
|---|---|---|---|
| Large Motor | 54675 | 100 x 80 x 180 | Output disc on local -Y, turned to +Z; body hangs to y = 150 |
| Prime Hub | 45601 | 140 x 80 x 220 | Lies flat, 5x5 up at y = 50, z -250..-30 |
| Force Sensor | 37312 | 60 x 59 x 60 | On end, button up, top at y = 106 |
| 3x3 Color Light Matrix | 47592 | 60 x 58 x 59 | LEDs on local -Z; back holes at (+-20, 0, 10) |
| Quarter rack | 24121 | 218 x 20 x 218 | Outer radius 209 at the lips; teeth inward to r = 173 |
| Z28 double bevel gear | 46372 | 74 x 74 x 20 | Tips at r = 36.8; cross bore on its Z axis |
| Half bush | 32123b | 18 x 18 x 10 | z -5..5; bore runs from the -5 face |
| 5M / 7M / 9M / 13M beam | 32316 / 32524 / 64289 / 41239 | 18 wide | Ends 9 past the last hole |
| T-beam | 60484 | 58 x 20 | Crossbar holes x = -20, 0, 20 |
| 1x4 Technic brick | 3701 | 80 x 28 x 20 | Holes 10 below the top |
| 2x4 plate with holes | 3709 | 80 x 8 x 40 | Origin on the top face |
| Snowboard | 18746 | 32 x 13 x ~64 | Two top studs, three underside tubes; decorative |
| Short legs | 41879 | 38 x 35 | 24 hip to sole (long legs are 40) |

## Where the mounting holes are

- **Motor front face** (local y = -30 -> world z = 30): a column of three
  pin holes each side of the disc, at x = +-40, world y = 0, 80, 120. The
  model uses the bottom two of each column, front (posts) and back (hub).
- **Motor output disc**: axle hole on the axis, pin holes at r = 20 above
  and below; the 3M pins go 20 in, 40 out, so the offset beam sits at
  z 70..90. Two more 3M pins from its bottom holes (y = 40, 60) carry the
  arm one slab further forward, at z 110..130, leaving 90..110 -- the
  back rail's slab -- empty at the axis for the back gear.
- **Hub short ends**: pin holes at local y = -10/-30/-50; y = 80 and 120
  world are the top and bottom rows. Ports on both long sides at y = 62.
- **Quarter rack** (`holes 24121.dat`): axle holes at the two lips
  (-200, 0) and (0, 200), and at 45 degrees on the inner rim; eight pin
  holes along the arc. The one at local (-120, 0, 160) lands on the upper
  crossbeam's end hole (x = +-120, y = 160), which is why that crossbeam
  is at y = 160. The end tabs are half thick (local y 0..10), hence the
  lap joint: see `context/ldraw-connections.md`, "Half-thick lugs".
- **Gear axle line**: the arm's bottom hole, the T-beam crossbar's middle
  hole and the rider brick's middle hole all sit at (0, 140), on one
  line along Z. All three are round, so the 7M axle through them -- and
  the gears and bushes on it -- spins freely.

## Z layers, back to front

| z | What |
|---|---|
| -250..-30 | Hub, rear legs at -270..-250 |
| -30..30 | Motor body |
| 30..50 | Posts; motor's output disc face at 50 |
| 50..70 | Crossbeams |
| 70..90 | Offset beam (r <= 69); back half bush (80..90) |
| 90..110 | Back rail and back gear |
| 110..130 | Arm |
| 130..150 | T-beam |
| 150..170 | Rider brick; board and Leo above it span 144..184 |
| 170..190 | Two spacer half bushes |
| 190..210 | Front rail and front gear; front half bush 210..220 |
| 210..250 | Light plate (y 226..234), over the big plate's front edge |
| 230..250 | Light bricks |
| 250..309 | Light matrix, y 159..217 |

## The gears

The four racks' teeth are a ring of 4 x 35 = 140 teeth. LEGO gears are
module 2.5 LDU, so pitch radius = 1.25 x teeth: the ring's is 175 and a
Z28's is 35. A Z28 rolling inside the ring therefore has its axle at
175 - 35 = **140** from the centre -- seven modules, exactly on the
Technic grid, which is the arm's bottom hole. That is the claim
`0 !LDRCHECK MESH 46372.dat 24121.dat 140` makes.

**Phase.** The teeth interleave only 3.8 LDU deep (tips at 176.8 vs the
ring's at 173), so the gear's turn on its axle matters. Swept through one
tooth (12.86 degrees) in 0.25-degree steps against the racks: at the
identity rotation the gear shares no solid with them and touches both;
turning it 1.75 degrees or more either way makes the teeth bite (32 to
224 LDU^3). Both gears are at identity. A declared mesh gets zero
overlap allowance in `ldrcheck` for exactly this reason: tip-on-tip
is smaller than the 200 LDU^3 general tolerance.

**Rolling.** Carried round the ring by theta, a gear that rolls without
slipping turns -theta x (175 - 35) / 35 = -4 theta in the world, i.e.
-5 theta relative to the arm that carries it. Four turns of the gear per
turn of the swing; at +-60 degrees it has turned 240 degrees.
`swing.py --roll 46372 -5` swings the rider and turns the gears to
match, and treats any solid shared between a gear and its rack as a
clash. Checking the sign the same way:

| Roll ratio | -60 | -37 | -30 | -11 | 0 | 11 | 30 | 37 | 60 |
|---|---|---|---|---|---|---|---|---|---|
| -5 (rolls) | clear | clear | clear | clear | clear | clear | clear | clear | clear |
| +5 (wrong way) | clear | clear | clash | clash | clear | clash | clash | clear | clear |
| 0 (does not turn) | clash | clash | clash | clash | clear | clash | clash | clash | clash |

Only -5 is clear at every angle tested.

## Swing clearance

The rider assembly is steps 15-28 (disc pins, offset beam, arm, T-beam,
rider brick, board, Leo, gear axle, gears, bushes). `tools/swing.py`
rotates exactly those lines about the origin, turns the gears, and
re-runs the voxel collision test against everything else (the motor is
ignored -- the disc it turns is part of the same file). No collisions
at any angle. Nearest fixed part, gears' own racks excluded:

| Angle | Voxel gap | Nearest fixed part | What it is |
|---|---|---|---|
| -60 | ~28 | 24121 | Spacer bushes beside the front rail |
| -37, -30 | ~22 | 64289 | Disc's blue pins passing the posts |
| -11 | ~18 | 41239 | Back half bush over the upper crossbeam |
| 0 | ~16 | 41239 | Back half bush over the upper crossbeam |
| +11 | ~18 | 41239 | Back half bush over the upper crossbeam |
| +30, +37 | ~22 | 64289 | Disc's blue pins passing the posts |
| +60 | ~28 | 24121 | Spacer bushes beside the front rail |

`--render` draws the two extremes from the front (LeoCAD's `back`
viewpoint, which is the +Z side): `renders/swing-+60.png` and
`renders/swing--60.png`, with both gears turned and seated in the teeth.

The voxel gap counts layers grown face-to-face, so a gap across a corner
reads larger than the straight-line distance. The straight-line numbers:

- **Ramp.** Only the gears reach the teeth. Every other swinging part
  next to a rail -- the back bush, the spacer bushes, the front bush --
  is at r <= 149, so **24 LDU (1 cm)** inside the teeth at every angle.
  The farthest non-gear point, the rider brick's corners at r = 159,
  is between the rails (z 150..170), where there is no rack.
- **0 degrees.** The back bush's bottom is at y = 149 and z 80..90; the
  upper crossbeam's top edge is at y = 151 and z 50..70. 2 LDU apart in
  y, 10 apart in z -- the bush passes in front of the beam, never into
  it.
- **Disc pins.** The blue 3M pins sit at r = 20 and turn with the disc;
  at +-30 they pass about 14 LDU inside the posts' inner faces (x = +-31).

## Swing limits

The program stops at +-60 degrees. The rails cover 0 to 90 degrees each
side, so at +-60 Leo is still well inside the curve; the lips are at
+-90. At +-90 the gear's contact point is the very end of the ring, so
it would be running out of teeth; +-60 keeps it well inside them. It
also looks like a skater turning just below the lip, and keeps the three
swings short. The motor's cable is not in LDraw; it leaves the
bottom of the motor behind the arm's slab, and the try-it page (36) is
where a person checks it does not catch.

## Assertions

Load-bearing numbers live in `0 !LDRCHECK` lines in `model.ldr`. This
page keeps the *why*:

The ground plane, y = 242, is the underside of the baseplates; their top
surface is y = 234 and their studs reach 230.

- `CLEARANCE 24121.dat 30` -- the racks' lowest point is the bottom lug
  at about y = 210, 32 above the ground plane and 20 above the stud tops;
  they must not rest on the baseplate.
- `CLEARANCE 37312.dat 12` -- the sensor's foot is at y = 226, 16 above
  the ground plane and 4 above the stud tops, so pressing the button
  pushes the frame, not the baseplate.
- `CLEARANCE 47592.dat 20` -- the light matrix hangs past the plate's
  edge, over the table; its bottom is at y = 217, 25 above it.
- `FACES 47592.dat +Z` -- the lights face Ian.
- `MESH 46372.dat 24121.dat 140` -- both gears sit 140 from the ring's
  centre, in a rail's plane; see "The gears".
- `JOINS 24121.dat 3707.dat` -- the bottom axle is what makes each rail
  rigid (a single pin per half reported RIGID CLUSTER HINGE).
- `JOINS 47592.dat 3709.dat` -- the light matrix reaches the plate it
  stands on through its two pins and the two bricks.
- `RESTS 18746.dat ON 3701.dat` -- the board has no anti-stud geometry
  in LDraw, so its seat on the rider brick is asserted, not jointed.
- `PROXY 18228.dat 29066` -- Leo's real hair has no LDraw file.
- No `PIVOT` line: the offset beam is pinned to the disc, which is part
  of 54675.dat, so in LDraw the whole rider is rigid to the motor.
