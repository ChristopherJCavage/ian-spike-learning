# Measured geometry -- rainforest-chameleon

Every number here came out of `tools/ldrcheck.py`, not from looking at a
render. Re-derive with:

    python3 tools/ldrcheck.py measure 67351
    python3 tools/ldrcheck.py holes 67351 37308 47592

## Conventions

LDraw units, 20 LDU per Technic module. **+Y is down.** This model
declares:

    0 !LDRCHECK GROUND 20
    0 !LDRCHECK FRONT +Z

The hub sits at the origin: bottom y = 0, top y = -80, front z = +50,
sides x = ±70. Ground is the table at y = 20, so the hub's bottom
clears the floor by 20 LDU. Ball-plate feet (`14417`) are
`ground_contact: true` and splay onto that plane.

**Build-tester flip.** `model.ldr` places `67351` with matrix
`-1 0 0 0 1 0 0 0 -1` -- a 180 degree spin about Y, which negates local X
and Z and leaves Y untouched. Every number quoted below for the hub is
**local** (what `measure`/`holes` print, i.e. the part's own identity
frame); to get the world position actually used in this model, negate x
and z. Two consequences follow, both explained where they matter:

- The side holes and the two x = ±60 face-hole pairs are symmetric under
  that negation -- the *set* of hole positions maps onto itself, so legs,
  brow and tail keep the coordinates they always had. World z = +50 is
  still the head end, z = -50 still the tail end.
- The hub's own moulded features are not symmetric, so they actually
  move: the cable ports (local z = +49) land at world z = -49 -- the
  tail wall now, not the head wall -- and the lone top pin-hole pair
  (local z = -40) lands at world z = +40, over the shoulders instead of
  the tail. See "Where the cable ports are" and the deck note below.

## Sizes

| Part | LDraw | Size x,y,z | Notes |
|---|---|---|---|
| Small Hub | 67351 | 140, 80, 100 | origin at bottom-face centre; 2 ports |
| Colour Sensor | 37308 | 60, 58, 59 | lens at local z = -49 (native -Z) |
| 3x3 Colour Matrix | 47592 | 60, 58, 59 | LEDs at local z = -49 (native -Z) |
| 1x4 Technic brick | 3701 | 80, 28, 20 | holes along Z when identity |
| 1x2 Technic brick | 3700 | 40, 28, 20 | holes along Z when identity |
| 2x8 plate with holes | 3738 | 160, 12, 40 | tubes were missing; annotated |
| T-beam with 1x2 plate | 32530 | 40, 39, 20 | tubes were missing; annotated |
| Ball plate | 14417 | 40, 16, 38 | ball at local (0, 4, -20) |
| Socket plate | 14704 | 40, 16, 35 | socket at local (0, 4, -20) |
| 7M beam | 32524 | 18, 20, 138 | holes along Y when identity |
| 2M friction peg | 61332 | 40 along native X | 20 LDU into each part |
| Slide shoe 2x2 (cheek bump) | 2654 | 40, 12, 40 | four studs on top |
| 1x8 Technic brick | 3702 | 160, 28, 20 | holes along Z when identity; tail bar |
| 2x4 brick w/ cross hole | 39789 | 80, 28, 40 | tubes were missing; annotated |
| 2x4 plate, 3 holes | 3709 | 80, 12, 40 | tubes were missing; annotated |
| 2x2 roof tile 45 deg | 3039 | 40, 28, 40 | footprint z = -30..10, not centred |
| 1x1 cone | 59900 | 20, 28, 20 | one tube, dead centre |
| 2x2 round tile w/ hole | 15535 | 40, 8, 40 | corner tubes; annotated earlier |
| Flat tile 1x2 | 3069 | 40, 8, 20 | tubes were missing; annotated earlier |
| 1x1 round tile (eye) | 98138 | 20, 8, 20 | one tube (`pin_hole`), dead centre, underside y = 8 -- grips a peg tip the way a stud grips a tube |

Dropped in the build-tester pass: **Flex hose 10M** (`27328`, 200 along
native X) -- it was the tongue and it could not actually mount on the
sensor. No longer placed anywhere in this model.

## Where the mounting holes are

Hub `67351`, relative to its origin:

- **Sides** (x = ±70), axis X: y = -10, -30, -50 with z = ±20.
- **Front / back** (z = ±50), axis Z: x = ±60, y = -30.
- **Top** (y = -80), axis Y: x = ±60, z = -40.
- **Bottom** (y = 0), axis Y: x = ±60, z = ±40 and 0.

Colour sensor / matrix `37308` / `47592` (same housing):

- Rear pair at local (±20, 0, 10), axis Z -- used on the matrix (turned
  into world +Y when LEDs face -Y).
- Side pairs at local (±30, ±20, 0), axis X -- used on the sensor after
  a roll that keeps the lens on world +Y and maps those holes onto
  world ±Z, so they pin through the T-beams.

T-beam `32530`: pin holes at local (0, -2, 0) and (0, -22, 0), axis Z.
The chameleon uses the hole nearer the plate (world y = -58).

## Where the cable ports are, and the box in front of them

Both of them are on the **same face** -- but, after the build-tester
flip (see "Build-tester flip" above), it is the tail wall now, not the
head wall: local z = +49 lands at world z = -49. Socket mouths sit at
world (±40, -68, -49), opening along -Z (outward, away from the hub).
LDraw does draw them (`23807.dat`, turned 180° about Y so the 18 LDU
bore runs inward), but a drawn socket is not a reachable socket.

The reachable part is the air behind the hub, and it comes in two
pieces. Both formulas are unchanged from the part hardware itself --
only the sign and direction of z flipped with the hub.

**The plug.** `23816a` is 34 LDU across, 18 tall, box z = -20..14 in its
own frame, of which 14 goes into the bore. A seated plug therefore
stands 20 LDU proud, and each port now owns

    x = ±40 ± 17    y = -68 ± 9    z = -69 .. -49

**The wire.** It does not stop where the plug does. LDraw draws the tail
as a flat 6-wire ribbon (`s\23816s01`), 18.9 across and 4.2 thick,
leaving along the same axis. Give it one module of straight run before
it is allowed to bend and each port now owns

    x = ±40 ± 9.4   y = -68 ± 2.1   z = -89 .. -69

That is exactly where the tail lives, so the flip trades one clearance
problem for another -- the brow's cable lane (below) is gone, but the
tail shelf has to clear the same two boxes. It does, checked by
`ldrcheck` and worth restating here because two of the margins are
tight enough to matter on a re-read:

- **Tail bar** (`3702`, world z = -70..-50) and **tail plate** (`3738`,
  world z ≈ -90..-50) both sit inside the plug's z-range but clear it in
  Y -- the plug box rides higher on the wall than the shelf's top
  surface.
- **Round tiles** (`15535`, pressed onto the plate at x = ±40) clear the
  plug box by only **3 LDU** in Y: the plug's lowest reach (y = -59)
  stops just above the tiles' top surface (y = -56).
- **Tail base brick** (`39789`, x = -20..20) clears the plug box by only
  **3 LDU** in X: the brick's edge (x = 20) sits just inboard of the
  plug's inner edge (x = 23).
- The **wire** zone (z = -89..-69) falls across the base brick's length
  (z = -130..-50) but the brick is only 40 LDU wide (x = -20..20) against
  the wire's x = ±40 ± 9.4, so it clears the same way the plug does, by
  the same 3 LDU margin.

Nothing on the brow constrains this any more -- with the ports moved to
the tail wall, the front pins, brow bricks, plate, T-beams and horns
have no cable to route around. That is why step 9's horns no longer need
a "clear lane" comment the way an earlier draft did.

`ldrcheck` reads this from the `ports:` block on `67351` in
`connections.yml` and enforces it in **PORT ACCESS**, reporting the plug
zone and the cable zone separately, at whatever world position the
model's own rotation puts them -- it does not need to know about the
flip; it reads the placed part.

## Why the sensor is not hanging under the brow

Aimed down, the housing is 59 LDU tall along Y. The brow underside is at
y = -40 and the ground-clearance floor is y = 12. 59 does not fit in 52.
So the sensor sits **in front** of the brow, pinned through two T-beams
clutched on the brow's front studs. Lens world y ≈ -9, claimed clearance
20 LDU against GROUND 20 (actual gap is ~29). `CLEARANCE` only asserts a
minimum; "too high to read the pad" is still a human check.

The matrix hangs above the hub on a 7M deck pinned into the top holes.
Before the build-tester flip those were at world z = -40, over the tail;
the flip carries the hub's only top pin-hole pair from local z = -40 to
world z = +40, so the deck now sits at (±60, -80, 40), over the
shoulders, just behind the brow. LEDs still face world -Y.

## Why the tail uses no ball joint

The box ships five `14704` / `14417` pairs, but the fifth lives in the
spare tray rather than the main bin, so a build that spends five pairs
quietly assumes every table's spares are intact. All four pairs go to
the legs; the tail is plain clutch.

The tail grows backward from the tail shelf (`3738` top face at
y = -48, studs at x = ±10..±70 and z = -60, -80). Each segment steps two
studs further back and one layer higher, so it sweeps up as it tapers:

| Segment | Part | Origin | Occupies |
|---|---|---|---|
| base | 39789 Dark Green | (0, -72, -90) | z -130..-50, y -76..-48 |
| curl 1 | 3709 Flame Yellowish Orange | (-20, -80, -110) | x -60..20, y -84..-72 |
| curl 2 | 3709 Flame Yellowish Orange | (-60, -88, -110) | x -100..-20, y -92..-80 |
| curl 3 | 3709 Flame Yellowish Orange | (-100, -96, -110) | x -140..-60, y -100..-88 |
| point | 3039 Bright Reddish Violet | (-120, -120, -100) | x -140..-100, y -124..-96 |

The curl works because a 2x4 plate turned across the animal still lands
four anti-studs on the base brick. The brick's rear studs sit at
x = ±10, z = -100 and -120; the first plate at (-20, -80, -110) puts
anti-studs at x = -50, -30, -10, 10 crossed with z = -100, -120, so the
four inner ones bite and the two free columns swing out to -X. Each
next plate clutches those two free columns (four studs, not a hinge)
and steps up one plate. A one-plate curl stayed inside the hub
(x = -60) and vanished on every front-left instruction page; two
plates cleared the hub but not the splayed feet (x = -135). Three
plates reach x = -140, past the feet, so the animal has a tail in the
pictures. Offsetting a plate sideways *along* the tail instead would
have left a single column of two studs, which is a hinge, not a tail.

Each one lands on four anti-studs spread over two rows and two columns,
so none of them reads as a hinge. The tail reaches 70 LDU straight back
and then turns, against a 100 LDU body. An earlier draft ran 160 LDU
dead straight; at that length the tapering purple point read as a
second head from the side, which is the failure mode a render catches
and a parts list does not.

Before the build-tester flip, the rear was also the one place with
headroom: the matrix and 7M deck sat at z = -69..-11 / -49..-31, both
short of z = -70, so nothing in the tail came near either. The flip
carries both of those to the shoulders instead (z = +11..+69 for the
matrix, +31..+49 for the deck), so the tail's only remaining neighbour
back there is the two cable ports -- see "Where the cable ports are"
above for that clearance instead.

## Assertions

    0 !LDRCHECK FACES 37308.dat +Y
    0 !LDRCHECK CLEARANCE 37308.dat 20
    0 !LDRCHECK JOINS 37308.dat 67351.dat
    0 !LDRCHECK FACES 47592.dat -Y
    0 !LDRCHECK JOINS 47592.dat 67351.dat
    0 !LDRCHECK JOINS 98138.dat 61332.dat
