# Mechanism -- Seed Drone

Measured from LDraw and checked with `tools/ldrcheck.py`; not inferred from
the render.

## World and layout

- `+Y` is down.
- The USB-shaped wall is front, `+Z`.
- Both cable ports are rear, `-Z`.
- Ground is `y = +32`, set by the two round slide shoes.
- Right is `+X`, taken from forward `x` down: `(+Z) x (-Y) = +X`.

The Small Hub is at the origin, rotated 180 degrees about Y:

```
1 14 0 0 0 -1 0 0 0 1 0 0 0 -1 67351.dat
```

Everything else is arranged around it on the centreline. The sensor is
centred at the nose, the seed bay hangs off the tail, one short grip
sticks out of each side wall, and the rotor axis stands over the Hub.

## Why there is only one powered motion

The Essential Hub has two ports. A downward Colour Sensor uses A and the
payload motor uses B, leaving no port for a rotor motor. The broad rotor
therefore spins freely when flicked by hand.

This is not a missing feature. The lesson's technology is the feedback
loop -- **sense the restoration site, then release a payload**. A passive
rotor preserves that loop and gives the class a useful engineering
question: which motion actually needs automation?

## Getting the bay onto the tail centreline

The bay used to hang off the left wall. Putting it on the rear centreline
looks like a rotation, and is not, because of one measurement: the motor's
mounting face carries two holes **40 LDU apart**, and the Hub's two rear
holes are **120 LDU apart**. The motor cannot bolt to the rear wall.

The only rear anchor available is a 1x8 Technic brick spanning those two
rear holes -- and every hole in a Technic brick sits at the same height.
A horizontal row of holes cannot hold a part that needs a vertical pair.

Two dead ends, recorded so they are not retried:

- Rotating the proven left-wall bay rigidly about Y puts the motor's two
  mounting holes 40 LDU apart **in Y**, which the spine cannot supply.
- Adding a 90-degree roll to fix that tips the tray onto its side.

`32526.dat` (TECHNIC ANG. BEAM 3X5 90 DEG) resolves the conflict. It is
the one part in the Essential kit that converts a horizontal row of holes
into a vertical column. Mounted on edge:

```
1 10 80 -30 -80 0 0 -1 -1 0 0 0 1 0 32526.dat
```

the 5-hole arm lies flat along the spine and the 3-hole arm climbs. The
3-hole arm is the right arm for the column: its three holes span exactly
the 40 LDU the motor needs, top to bottom. Using the 5-hole arm as the
column instead lifts the tray above the Hub roof and leaves 39 LDU of bare
beam sticking into the air.

### The shared corner hole

A right-angle beam's **corner hole belongs to both arms at once**. Driving
a pin into it from each direction produces two pins occupying one hole:
INTERPENETRATION, and 22 cascading `steps` BUILD ORDER failures. The
spine pins therefore sit at `x = 20` and `x = 40`, clear of both the
corner and of the step-5 pins that pass through the spine's end holes into
the Hub at `x = ±60`.

## Tipping seed bay

The motor stands upright against the bracket with its output bore aimed
aft along `-Z`. A 6M axle drives a 1x2 brick with a cross hole; its two
studs lock the tray to the shaft. The floor is two 2x4 plates side by side,
both turned fore-and-aft: a 4x4 square from `x = -20..60` by
`z = -260..-180`.

Two plates side by side clutch nothing. The walls go on the first plate
first -- two studs clutch, two hang off -- and the second plate clicks onto
that overhang. The other order leaves a plate with nothing to attach to;
`ldrcheck steps` reports that as CONTACT WITHOUT JOINT and fails the page.
Each 1x4 then takes two studs from each plate. That is the whole reason the
plates are turned. Laid the other way -- four studs across, two deep,
stacked along `z` -- a 1x4 wall on
a `z` edge sits entirely on one plate and ties nothing, which is why the
first version of this tray needed a fourth plate underneath as a bridge.
The open end has to be an `x` edge, because the tray rotates about `Z` and
the ball therefore rolls in `x`; that fixes the walls onto the `z` edges and
so fixes the tiling too.

The two walls' inner faces are `z = -240` and `z = -200`: a channel 40 LDU
wide holding a ball 41.6 LDU across. The ball does not reach the floor. It
rides on the two wall top edges at `y = -92`, centre 5.7 LDU above them, and
is gripped there rather than resting anywhere. The 1x2 stop closes the
inboard end of that channel -- exactly 2 studs for exactly 2 studs -- and
`x = +60` stays open.

Gripping the ball rather than cradling it is deliberate. The first tray gave
it a 60-LDU well with 18.4 LDU of slack, and slack in a model a child walks
around with means a seed that leaves early. The cost is that the release is
no longer guaranteed by gravity alone, which is why `preflight.md` now makes
the quarter-turn drop an explicit hand test with an explicit fallback.

`0 !LDRCHECK PIVOT 3706.dat +Z` verifies that the axle really carries a
connected moving subassembly about the intended axis. It cannot prove the
ball rolls, the motor direction is correct, or 0.25 rotations is the best
travel. Those remain table checks.

## Downward survey sensor

The Colour Sensor is mounted at:

```
1 15 0 -58 120 0 1 0 0 0 -1 -1 0 0 37308.dat
```

Its lens faces local `-Z`. The matrix maps that to world `+Y`, so the lens
looks at the paper. The model asserts both the pose and the clearance:

```
0 !LDRCHECK FACES 37308.dat +Y
0 !LDRCHECK CLEARANCE 37308.dat 40
```

The lens reaches `y = -9`; the target plane is `y = +32`. The resulting
41-LDU gap is 16.4 mm, inside the approximate 1–2 cm range that must be
confirmed with the real sensor and target paper.

## The face

The sensor housing is the head, and it wears its eyes on two pegs pushed
into its forward face:

```
1  0 -20 -58 150 0 0 -1 0 1 0 1 0 0 61332.dat
1  0  20 -58 150 0 0 -1 0 1 0 1 0 0 61332.dat
1 15 -20 -58 170 1 0 0 0 0 1 0 -1 0 98138.dat
1 15  20 -58 170 1 0 0 0 0 1 0 -1 0 98138.dat
```

Those eight numbers are copied verbatim from `rainforest-chameleon`, and
they need no adjustment because the sensor is placed at exactly
`(0, -58, 120)` with exactly the matrix `0 1 0 0 0 -1 -1 0 0` in both
models. When two builds agree on a subassembly's frame, a feature hung off
it transfers as-is.

The sensor has holes on both of the faces that this orientation turns
fore-and-aft. The **rear** pair at `z = 90` already carries the pegs that
mount it to the red T-beams (step 23); the **forward** pair at `z = 150` is
free, which is what the eyes use. Step 25's Check line says the eye pegs
must not touch the brackets behind them, because getting the pair backwards
is the one plausible mistake here.

Kit part 13360 is `98138pr0008`: a 1x1 round tile with a black iris and
pupil printed on it. **LDraw carries no print**, so every render of this
build shows two blank white discs. The face is real; the drawing cannot
show it. Verify against the part number, not the picture.

A peg's shaft is close enough to a stud's diameter that the tile's
underside tube grips it the same way it grips a stud -- that is the whole
mechanism, and it is why the pupil can be a separate piece rather than a
print on the structural part.

`98138.dat` is annotated `role: decorative`, which exempts it from the
joint and support checks: an eye tile floating in mid-air would draw no
comment at all. `0 !LDRCHECK JOINS 98138.dat 61332.dat` in the header is
the only thing standing between a real grip and a coincidence.

### What used to be here

The first version of the face put the LARGE printed eye -- kit 44690,
`14769pr1116`, a 2x2 round tile with a blue iris -- flat on the two outer
corners of the nose face plate at `(+/-60, -56, 70)`. It read badly for a
reason the checker cannot see: lying flat on the deck the tiles faced
straight up, and 120 LDU apart they were nowhere near each other, so from
in front they were two instrument dials rather than a pair of eyes. Once
the sensor grew its own eyes there was no version where keeping both was
right, because that is four eyes.

Worth keeping from that attempt: `14769.dat` needed a `connections.yml`
entry before it would pass, and that entry is still in the file for the
next build that wants it. LDraw emits only the underside holder's bore, as
a lone centre `pin_hole` that joins nothing, because nothing ever sits at a
2x2's centre. Unannotated it produced 12 problems: NO JOINT x2,
INTERPENETRATION x2, and CONTACT WITHOUT JOINT x4. The fix declares the
four anti-studs it actually holds, copying the `15535.dat` precedent
directly above it in that file.

## Hand-flicked rotor

Two pins hold a 7M beam across the Hub's top holes. The beam's centre is a
round Technic hole, so a cross axle can rotate inside it. Above that
bearing, a 2x4 brick with vertical **cross** holes locks to the same axle.
A 2x8 plate spans that brick, and two fasteners per blade make the two 11M
beams turn as one rotor rather than swivel separately.

That pairing is the entire answer to "is there a piece that lets the
blades spin": a cross axle turns freely in a **round** hole and locks
solid in a **cross** hole. `32524.dat` emits `female pin_hole x8`, all
round. The 4M axle engages the centre one for 19.5 LDU and free-spins;
it engages `39789`'s cross hole for 20 LDU and cannot slip. No dedicated
bearing or bush part is involved, and none is available -- the axle's
lower tip already stops half an LDU above the Hub roof, so there is no
room below the beam for a retaining bush.

### The same rule, applied backwards, cost two rebuilds

The rotor spins because of round-versus-cross. The blades then **fell off**
for the same reason, twice over, and it is worth writing down how a fact
this build already depended on failed to transfer twenty LDU upward.

Version one mounted each blade on two vertical 3M cross axles at `x = ±20`
and `±40`, standing in the 2x8 plate's holes. `3738.dat` emits `female
pin_hole x7` -- all **round**. So did the beam. Twelve joints of 20 LDU
each, no interpenetration, nothing detached, `PIVOT` satisfied: clean. And
physically the blades lifted straight off, because a smooth axle in a round
bore is a bearing, which is precisely what the paragraph above says.

Version two kept the axles and added friction pegs, which grip, but left the
axles in round holes. Better, and still the axles held nothing.

Version three asked the part instead of assuming. `ldrcheck holes 39789.dat`
reports `female axle_hole x6` -- **cross** holes, vertical, at `x = -20, 0,
+20`. The centre one carries the drive axle; the other two were empty the
whole time. Each blade now takes one axle at `x = ±20`, through the plate's
round hole and 15 LDU into the brick's cross hole, plus one friction peg out
at `x = ±60` where the plate's round hole grips it. Two fasteners 40 LDU
apart, both holding for a different reason.

The lesson that generalised: **fitting and holding are different questions,
and the checker was only asking the first.** `ldrcheck` now has a `GRIPS`
table and a `NOT RETAINED` check, scored as a transient in `steps` because
assembly legitimately stands a shaft in its bearing on one page and locks it
on the next -- see `context/ldraw-connections.md`, "Fitting is not holding",
and the two fixtures named there.

Heights are forced rather than chosen, because `ldrcheck` models every pin
hole as a full 20-LDU bore even through an 8-LDU plate. A 40-LDU peg is
exactly two bores long, so the beam's bore must sit precisely back to back
with the plate's or `PIN SLICE CONFLICT` fires. That fixes the beam centre at
`y = -158` and both fasteners at `-148`. The blades therefore float 12 LDU
above the plate's studs, which is correct in its own right: a Technic beam
has no anti-studs, so it cannot clutch a plate and the fasteners are the only
thing holding it.

The black 4M rotor axle is centred at `y = -120`. It spans
`-159.5..-80.5`, leaving that tip clearance at `y = -80`. An earlier
placement centred it at `-110`; it rendered cleanly but drove 9.5 LDU into
the solid Hub, because connector shafts are excluded from voxel collision
checks. The corrected coordinate is deliberate.

`0 !LDRCHECK PIVOT 3705.dat +Y` validates the free-spin axis. The blades
sweep 458 LDU, about 18.3 cm tip to tip, at `y = -158`. The tallest thing
under that disc is the loaded seed ball at `y = -113`, so the blades pass
35 LDU clear of a loaded tray -- 43 before the beams came down to where a
40-LDU peg could reach them.

## Landing shoes and grips

Four pins attach two 2x8 plates under the Hub. A round slide shoe presses
into each plate and sets the ground plane. They protect the sensor lens
and let the model rest level while loading the ball.

The tail spine displaced the old rear handle, so the drone is now carried
from the sides. A 1x4 Technic brick sits on each side wall at
`(∓80, -40, 0)`, spanning `x 70..90, y -44..-16, z -40..40`.

A pair of side grips beats one rear handle here: it holds the model level
instead of cantilevered, and it keeps both hands below and outside the
rotor disc. But the measurements set an honest limit on what they are:

- They protrude **20 LDU (8 mm)** past the Hub wall at `x = 70`, because a
  brick pinned flat against a wall protrudes exactly its own thickness.
- The skid rails below reach to `x = 80`, so only the outer 10 LDU of each
  grip has free air beneath it, over a 28-LDU (11 mm) gap.

That is a thumb shelf and a fingertip hook, not a handle. The Hub body is
the real handhold; the grips locate the hands on it. `steps.md` and
`preflight.md` say so rather than promising a grip the geometry cannot
deliver.

They also cannot be made longer. The side wall offers holes only at
`z = ±20`, so any grip brick centres on `z = 0`; a 1x8 would then span
`z ±80` and collide with the spine, which reaches `x = ±80` at the same
height. 1x4 is the longest brick that fits.

`PORT ACCESS` is clean with the spine installed, but cable routing around
a child's hands is still a human check.

## Fixtures that earned the model

- `good-drone-rotor-free-spin.ldr`: round bearing + locked rotor hub.
- `good-drone-tipping-bay.ldr`: motor, axle, rigid tray, walls, and ball.
- `good-sensor-aims-down.ldr`: the exact lens-down rotation matrix.
- `good-seed-ball-payload.ldr`: loose payload is allowed without fake
  clutch geometry.
- `good-tail-bracket-upright-motor.ldr`: the 7-part spine-to-upright-motor
  chain, asserting `JOINS 68488.dat 32526.dat`.
- `good-eye-tile-on-pin.ldr`: the peg-and-pupil pattern this build's face
  uses, on the same sensor, asserting `JOINS 98138.dat 61332.dat`.
- `good-eye-tile-on-plate.ldr`: the large printed eye tile held by four
  studs -- the face this build started with and then dropped.

The finished model and all 31 intermediate steps report zero problems.

## What a "0 problems" result does not cover

The first eye tile was written into the model as `44690.dat`, its kit
design ID, instead of `14769.dat`. `ldrcheck` reported NO GEOMETRY and
carried on printing **0 problems** -- the eyes were neither rendered nor
checked. Models must name the LDraw part, and a clean run is only
trustworthy once the NO GEOMETRY list is empty. The same trap is live for
today's eyes: they are `98138.dat`, not kit `13360`.
