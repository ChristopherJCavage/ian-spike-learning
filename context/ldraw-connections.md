# How LEGO Technic actually connects

`tools/ldrcheck.py` can tell you when two parts occupy the same space. That
is not the same as knowing whether they are **joined**. This file is the
prose that the checker encodes, so a later run (or a later person) can
read the reasoning and not only the numbers.

See `tools/connections.yml` for the per-part shafts and extra holes, and
`tools/ldraw_aliases.json` for kit design IDs that do not match LDraw names.

## Contact is not a connection

Two parts whose faces rest against each other are not built. A motor
sitting on a beam will look attached in a render and will pass a collision
check. The moment you pick the model up, it falls off. A connection is a
**joint**: a male shaft occupying a female hole, with real insertion depth.

## What a friction peg is for

A Technic friction pin (`61332`, 2M; `42924`/`6558`, 3M) joins **exactly
two parts**, hole to hole.

- Each end occupies one module (20 LDU) of hole.
- The 2M pin is 40 LDU long: 20 into A, 20 into B, faces flush.
- The 3M pin is 60 LDU long: 20 into A, 20 of shaft spanning a 20 LDU
  thickness or gap, 20 into B. That is how you pin through a beam into a
  second part on the far side.

A peg is not a beam. It is not a leg. It is not a standoff you leave
sticking out of a hole into the air. If one end is not inside a second
part's hole, it is not doing its job.

## Hinge versus rigid

One pin through two parts is a **hinge**. The parts can pivot around that
axis. Two pins through the same pair of parts, on **parallel axes that are
not the same line**, make a rigid joint. Two pins that share one axis
(collinear) are still a hinge -- they are just a longer hinge.

The checker reports hinges as warnings. They are legal (wheels, grabber
jaws, a dump bed) and also the usual way a "frame" accidentally folds.

## Ball and socket

A Technic ball joint (`14417` into `14704`) is a **pose**, not a hinge
and not a weld. LDraw already draws both halves as primitives
(`joint8ball.dat`, `joint8socket1.dat`); they were missing from the
checker's table the same way `axlehol5` was missing for gears.

When seated, the two primitive origins coincide. The ball is an 8 LDU
sphere, so matching is by origin gap (under 4 LDU), not by coaxial
overlap -- a splayed chameleon leg is still joined. One ball joint is
legal on its own, like `rotates: true` on a wheel.

See `tools/fixtures/good-ball-joint-leg.ldr`,
`tools/fixtures/bad-ball-joint-air.ldr`, and
`tools/fixtures/good-ball-against-brick.ldr`. The last one is the
chameleon-leg case: the seated ball sits 2 LDU from the hip brick. They
share the socket plate as a joint neighbour, so that graze is not
`CONTACT WITHOUT JOINT`.

The same missing-tube pattern shows up on plates the library only draws
as boxes: `3738` (2x8 with holes) and `32530` (T-beam with a 1x2 plate)
need hand-written `anti_stud` features. Fixtures:
`tools/fixtures/good-plate-on-brick.ldr` and
`tools/fixtures/good-tbeam-on-plate.ldr`.

It is broader than "plates the library draws as boxes", though. LDraw
*does* emit an underside tube for an ordinary brick or plate, as
`stud4a`, and the checker reads that as a female `pin_hole`. But a
`stud4a` tube sits **between** four studs, on the half-grid, so it never
lines up coaxially with a stud below it. That is why a plain 1x4 brick
resting on a plate produces no joint until somebody writes the
anti-studs out. The rule of thumb: if a part is going to sit on studs,
give it one `anti_stud` directly under each of its own top studs, with
the origin on its underside face -- `y = 8` for a plate, `y = 24` for a
brick or a slope. The chameleon's tail added `3709`, `39789`, `3039`,
`3040`, `59900` and `87079` that way; `tools/fixtures/good-tail-*.ldr`,
`good-crest-cone-on-plate.ldr` and `good-colour-tile-on-plate.ldr` prove
they clutch, and `bad-tail-plate-floating.ldr` proves the annotation
still fails when the part is one plate too high to reach.

Watch the footprint on slopes. A 2x2 roof tile (`3039`) spans
`z = -30..10`, not `-20..20`, so its two stud rows are at `z = 0` and
`z = -20`. Writing the tubes symmetrically about the origin puts them
where no stud is.

## Ports: the space a part needs that is not in its outline

A hub is not just a shape. Its cable sockets need air in front of them,
and nothing in the LDraw file says so. The Small Hub `67351` draws both
sockets faithfully -- `23807.dat` at `(±40, -68, 49)`, turned 180° about
Y so the 18 LDU bore runs inward -- and a head built onto the brow can
seal them shut without a single triangle overlapping, because the hub's
own solid stops at `z = 50` and the decoration starts there.

So the socket goes in `connections.yml` as a `ports:` entry:

```yaml
ports:
  - {name: "+x", origin: [40, -68, 49], axis: [0, 0, 1], up: [0, 1, 0]}
```

`origin` is the mouth, `axis` points the way the plug arrives, `up` is
the short side of the rectangular opening. Names are geometric: which
socket is lettered A and which is B is printed on the plastic and is not
in the part file, so the checker refuses to guess. The keep-out is not
invented:
the mating plug is `23816a`, 34 LDU across and 18 tall, with a bounding
box of `z = -20..14` of which 14 disappears into the bore. A seated plug
therefore stands 20 LDU proud, and **PORT ACCESS** flags any other
part's solid inside that box.

Then keep going, because the wire is the part that actually sweeps
things off the model. LDraw draws the plug's tail as a flat 6-wire
ribbon (`s\23816s01` inside `23816c01`): 18.9 LDU across, 4.2 thick,
leaving along the same axis. The checker gives it one module of straight
run past the plug -- a ribbon cannot turn a corner in zero distance --
and reports that as a separate `cable` zone.

The second zone is the one that catches real mistakes, because it
reaches *further out* than the plug while being much narrower. A part
can miss the plug by a single LDU and sit square in the wire. That looks
perfect in a render, seats the plug fine on the table, and then leans on
whatever the decoration is. `bad-hub-cable-swept.ldr` is exactly that
case; `bad-hub-port-blocked.ldr` is the blunter version where the plug
will not go in at all; `good-hub-ports-clear.ldr` is the same brow with
the cones two studs further out.

Two things fall out of the numbers. Studs are on a 20 LDU grid and the
plug is 34 wide, so a port centred between stud columns swallows the
columns either side -- you cannot decorate "next to" a port, only well
clear of it. And a socket does not own a box, it owns a **lane**: the
plug's width for the first module, the ribbon's width for as far as the
wire runs straight. Design around the lane and the rest of the model can
be as busy as you like.

## Axles and bushes

A cross axle is a male shaft that runs through axle holes and through the
round holes of a Technic beam. It needs something to stop it sliding out:
a bush, a wheel whose hub fills the end, or a second part whose hole is
the last stop. An axle through one hole and into empty space is a pin
with the other end missing.

Bushes (`4265c` / `32123b`) sit on an axle. They are retainers, not
two-ended fasteners. A bush in mid-air is as wrong as a peg in mid-air.

## Fitting is not holding: round hole versus cross hole

The single most expensive mistake in this repo so far. **A joint that exists
is not a joint that holds**, and the difference is invisible in a render.

| shaft | round `pin_hole` | cross `axle_hole` |
| --- | --- | --- |
| cross axle | spins **and slides out** -- holds nothing | locks: cannot turn, cannot pull out |
| friction peg | grips (ribbed) | n/a |
| smooth pin | spins, but stays: the moulded ridge snaps past the lip | n/a |

A cross axle is smooth along its whole length. Nothing on it catches a round
bore, so a round hole neither stops it turning nor stops it leaving. That is
a **feature** when you want a bearing -- the Seed Drone's rotor turns on
exactly that pairing, one axle in the round centre hole of a 7M beam -- and a
defect the moment it is the only thing holding a part on.

The Seed Drone's first rotor mounted each blade on two cross axles standing
in the round holes of a plate. Every check passed: no interpenetration, no
detached subassembly, twelve 20-LDU joints reported. The blades came off in a
child's hand on the first flick. The fix was to move each axle inboard to the
two holes that have a **cross** hole beneath them, in the dark-green 2x4
brick, and to fasten the outer end with a friction peg instead.

Note the asymmetry with smooth pins. Free to **rotate** and free to **slide
out** are different properties, and only the second loses parts. A LEGO pin,
friction or frictionless, has a ridge that snaps past the bore's lip, so a
frictionless pin spins in place and stays put. An axle has no ridge anywhere.

`ldrcheck` enforces this as **NOT RETAINED**: a connector fails if not one of
its joints appears in the `GRIPS` table. It is scored as a *transient* in
`ldrcheck steps`, because the normal order of assembly stands a shaft in its
bearing hole on one page and locks it on the next -- lingering into a second
page is the defect, and on the last page nothing is forgiven.

Before deciding which hole a fastener goes in, ask the part:

```
python3 tools/ldrcheck.py holes 39789.dat   # axle_hole (cross) x6 at x=-20, 0, +20
python3 tools/ldrcheck.py holes 3738.dat    # pin_hole (round) x7 at x=-60..60
```

Fixtures: `bad-axle-in-round-holes-only.ldr`,
`good-axle-locked-in-cross-hole.ldr`.

## Plates side by side clutch nothing

Two plates laid edge to edge are two loose parts. Studs point up and down,
not sideways, so nothing about the seam holds. Something above or below has
to span it: another plate bridging underneath, or -- cheaper -- a brick or
beam laid across the seam that the design needed anyway.

`ldrcheck` reports this as **CONTACT WITHOUT JOINT**, the pair touching with
no joint and no shared connector between them. It is a *hard* fail in
`ldrcheck steps`, not a one-page transient: a plate that only touches its
neighbour falls off in the child's hands. The seed drone hangs the two 1x4
walls off the first plate (two studs on, two off), then the second plate
clicks onto that overhang.

Which way the plates are turned decides whether an existing part can do the
tying. See `builds/seed-drone/mechanism.md`, "Tipping seed bay": the same two
plates make the same 4x4 square either way, but only one of the two tilings
puts the side walls across the seam.

If a shaft really is meant to run free and be held captive some other way,
say so: `0 !LDRCHECK FREERUN <part>`. Like every directive it is also an
assertion, so it fails if the part leaves the model or if something ends up
gripping it after all -- an excuse that has stopped excusing anything hides
the next real defect.

## Studs versus Technic holes

System bricks clutch stud-into-tube. Technic beams clutch pin-into-hole
and axle-into-hole. The Prime Hub's top is **smooth** -- it has pin holes,
not studs. You cannot press a brick onto it. You pin a Technic-to-stud
converter (a plate with holes, a pin-with-stud brick) into those holes,
then build on the studs.

A tile sitting on a smooth plastic face is decoration in the render, not
a build.

## What LDraw does and does not tell you

LDraw primitives (`peghole`, `beamhole`, `connhole`, `axlehole`, `stud`,
`joint8ball`, `joint8socket1`) mark female holes, studs, and the
ball-and-socket pair. They do **not** mark male pin or axle shafts. Every pin
and axle in this repo is annotated by hand in `connections.yml`. Some
parts (the dia.56 wheel's centre cross hole, the angular-motor output
disc) have holes that exist only as mesh, so those are annotated too.

Primitive axis signs are not trustworthy. The checker decides which way a
hole faces by probing which side of the mouth has plastic, not by reading
the sign off the primitive.

## Surface mounting: the pin centres on the face, the part centres off it

A part bolted flush against a flat face is not centred *on* that face --
it is centred **half its own thickness beyond it**. The pin (or hole) sits
at the mating face; the part's own centreline sits further out by half its
thickness.

    part centre = face position + sign * (part thickness / 2)

Get this wrong and the part straddles the wall: half its volume inside the
neighbour, half outside, looking flush in a render while `ldrcheck` sees
real solid-on-solid overlap. A 20 LDU thick rail meant to sit flush against
a face at x = 70 belongs at x = 80 (70 + 20/2), not x = 70. Centring it *on*
the face buries 10 LDU of the rail inside whatever is behind that face.

This is exactly the arithmetic in `tools/fixtures/bad-buried-in-shell.ldr`.

## Rigidity is a property of the subassembly, not the part

A part with two non-collinear pins into its neighbours is rigid *relative
to those neighbours*. That says nothing about whether the **group** they
form is rigid relative to the rest of the model. Two beams pinned tightly
to each other are just as free to swing as one beam would be if the only
thing anchoring the pair to everything else is a single pin, or several
pins that all lie on the same line.

Check rigidity by building rigid clusters first -- union parts that share
two or more non-collinear pins -- then look only at what crosses each
cluster's boundary. A cluster reaching the rest of the model through one
pin, or through pins whose axes are all collinear, is under-constrained
even though every individual part inside it looks fully pinned. This is
the sensor-gantry failure mode: two rails, rigidly cross-braced to each
other and to the sensor, reaching the Hub through exactly two pins that
share one line. The subassembly hinges even though no single part in it
has fewer than two engagements.

A cross axle is exempt from this by default -- a bare axle (`role:
connector`) is just a rotating shaft, not a structural claim, and a part
that is meant to spin on its axle (a wheel, a drill bit, a bush) says so
with `rotates: true` in `connections.yml`. Anything else reached only by
axle is treated the same as a single pin: a hinge, and here, a problem
rather than a warning, because a subassembly that rocks is worse than one
part that spins.

See `tools/fixtures/bad-collinear-subassembly.ldr` for the failing shape
and `tools/fixtures/good-wheel-rotates.ldr` for the legal one it must not
also catch.

## Kit names versus LDraw names

LEGO's design ID on the box is often not the LDraw file name. The Prime
Hub is kit `105474` and LDraw `45601.dat`. `tools/ldraw_aliases.json`
holds the 62 mismatches across the three kits: 52 point at a real `.dat`,
10 are declared to have no geometry at all. Decorative prints and molds
that LDraw simply does not have stay unmapped; the checker treats them as
empty geometry.

Run `ldrcheck kits` to see the whole mapping at once. It is the only way
to find out that a part is invisible to the checker *before* a build
leans on it. The trap is a design ID that happens to collide with an
unrelated LDraw part number -- always confirm against BrickLink's
"Alternate Item No", never against the number looking plausible.

## Colour

A part placed in an LDraw colour the kit does not ship is a documentation
bug that becomes a table bug: Ian will look in the wrong bin. The checker
compares the placed colour against `kits/*/parts.txt`. Colour 16 (main /
native electronics colour) is skipped.

## Ground plane and clearance

Touching the floor is not passing, for the same reason contact is not a
connection. Wheels are allowed to sit on the ground (`ground_contact: true`
in `connections.yml`). Everything else needs a positive gap: one plate,
8 LDU, so a beam frame that looks "just above the table" in a render and
actually occupies y = +70 is a defect.

The ground plane travels with the model, not with a flag you might forget:

    0 !LDRCHECK GROUND 70
    0 !LDRCHECK FRONT +Z

`--ground` on the CLI still overrides. An opt-in check is a check that does
not run.

## What `decorative` may and may not excuse

`role: decorative` means **no Technic joint is required**. It does not mean
the part is allowed to occupy the same cubic centimetres as its neighbour.

Before tagging a part decorative, run `ldrcheck holes` on it. If it emits
studs or tubes, it does not need the hatch -- annotate the missing underside
tubes (see `4079` in `connections.yml`) and let the matcher clutch them.

Check the primitive table before annotating, too. Gears looked solid for a
while purely because `axlehol5` and `axlehol6` -- the "open two opposite
sides" and "tooth" spellings of the same bore -- were missing from
`PRIMITIVES`. Six parts stopped being silent the moment they were added.
One line in the table beats six hand-written `features:` blocks.
The minifig body (`73200`, `76382`) genuinely has no primitives; those stay
decorative. A 1x1 brick standing in for a missing printed head is a proxy,
and stays decorative too.

Studs are 4 LDU tall. The pin-joint threshold of 8 LDU would make every
legal clutch invisible, so stud joints use a 2 LDU minimum. Stud-into-tube
is clutch, not a hinge: one stud holds an antenna.

## Support versus attachment

A jointless part with nothing next to it and nothing under it is floating.
Wall-mounted tiles (the truck's "eyes") rest against a face, not on the
floor -- contact in any direction counts as support. A round dish standing
on its rim above a deck, with no stud in its tube, is not supported in any
sense that will survive being picked up. Lay it flat on a stud.

## Orientation

LDraw has no concept of "forward." Minifig legs face **-Z** natively
(`facing: -Z` in `connections.yml`) and opt into the automatic FRONT
check with `faces_front: true`. Identity on a minifig therefore points
the driver at the rear of a +Z truck. 180 about Y
(`-1 0 0 0 1 0 0 0 -1`) is the matrix that faces them forward.

A colour sensor and the 3x3 light matrix also face **-Z** natively (the
lens / the LEDs). They do **not** set `faces_front` -- a chameleon aims
the sensor at the ground. `ldrcheck check` and `ldrcheck steps` both skip
the automatic FRONT test unless `faces_front` is set. Aim is a FACES
assertion, which may name any world axis, not only FRONT:

    0 !LDRCHECK FACES 37308.dat +Y
    0 !LDRCHECK FACES 47592.dat -Y

Figures are a pose, not a joint. Sitting them in the seat at the table
stays a human step.

## Numeric claims go in assertions

`0 //` comments are prose the checker never reads. A comment that says the
driver is "standing on the seat cushion" while their feet are on the deck
will stay wrong forever. Load-bearing numbers belong in assertions, which
fail closed -- including when they name a part that is no longer in the
model:

    0 !LDRCHECK CLEARANCE 64179.dat 40
    0 !LDRCHECK FACES 73200.dat +Z
    0 !LDRCHECK RESTS 35394.dat ON 3738.dat
    0 !LDRCHECK JOINS 64179.dat 45601.dat
    0 !LDRCHECK PIVOT 3705.dat +X

## Declaring a pivot, because an arm is not a defect

`RIGID CLUSTER HINGE` exists to catch a subassembly that can flop. But a
boom is a multi-part subassembly reaching the machine through exactly one
rotation axis, which is that rule's definition of a defect and also the
entire point of an excavator. The `rotates: true` exemption does not help:
it only forgives a *single* part on a shaft (a wheel, a driven disc), and
an arm is never one part.

`0 !LDRCHECK PIVOT <shaft> <axis>` says this shaft is meant to turn. The
boundary it carries stops being reported, and nothing else relaxes: the
joint must still exist, still engage a full module, and still not
interpenetrate. It names both a part and an axis so that declaring one
boom pivot does not quietly excuse every other copy of that axle in the
build -- though it is still per part file, so two 4M axles pivoting on the
same axis share one declaration. Being an assertion, it fails closed: a
pivot naming a part that has been rebuilt away, or turning about an axis
nothing turns about, is a FAIL rather than a silent free pass.

Comments keep the *why* ("a 9M beam cannot reach z = -80"). That rationale
can still rot, so re-reading it is a line on the pre-flight checklist, not
a promise the tooling makes.

Every defect found by eye should become three artifacts: a paragraph here,
a rule in `ldrcheck.py`, and a fixture in `tools/fixtures/`.

## Half-thick lugs: the quarter rack

`24121.dat` (kit 43038, the 11x11 quarter-circle rack) is a full module
thick everywhere except its two end lugs, which are half thick on one
face: local y 0..10 only. That is how four of them close a circle. Two
quarters meet in **one** plane, one turned half a turn about the
vertical, so their lugs land on opposite faces and stack into one
full-thickness lug that an axle locks. The first matrix anyone reaches
for, `0 0 1 -1 0 0 0 -1 0`, also lands a quarter in the lower right, but
it puts the lug on the same face as its partner and the two collide
(`bad-rack-lap-same-face.ldr`). `-1 0 0 0 0 1 0 1 0` is the partner of
`1 0 0 0 0 1 0 -1 0` (`good-rack-lap-joint.ldr`).

The lug bore is `axlehol4` scaled `0 10 0`, and the checker used to read
every one-sided axle hole as a whole module deep. The bore ran 10 LDU
out of the plastic into the beam behind, and a correct axle reported PIN
SLICE CONFLICT. A one-sided axle hole drawn half a module deep is now
read at that depth. Shallower ones are not: the Z20 bevel gear's bore is
drawn 7 deep, under `JOINT_MIN`, and it really does grip its axle.

The rack's teeth face **inward**, down to r = 173 from the arc centre,
not the 191 the bounding box suggests. Anything swinging inside the arc
has to clear 173.

## Proxies keep their real colour

`PROXY <stand-in> <design id>` keeps a stand-in out of PART vs KIT, and
now also lets COLOUR vs KIT accept the real part's colour. Leo's wig
(29066, Reddish Brown) has no LDraw file, so 18228 draws it in Reddish
Brown, a colour no kit ships 18228 in (`good-proxy-wig-colour.ldr`,
`bad-wig-colour-unproxied.ldr`). The stand-in's own kit colours still
count too, because one stand-in can cover several parts: the drill
truck's 3005 is both a yellow head and a nougat dog, and PROXY records
only one design id.

## A hand-written feature is a guess until something mates with it

`ldrcheck kits` proves the checker can see a part. It cannot prove it sees
it *correctly*: an `axle_hole` on the wrong axis and one on the right axis
are both "annotated." The only way to tell them apart is to place the part
against the thing it is supposed to grip and ask whether a joint appears.

Both round 2x2 tiles were annotated with a single female pocket at the
part's centre. Dropped onto a plate they reported **zero joints**, because
nothing ever sits at the centre of a 2x2 -- studs land at the four corners,
(±10, ±10). `2654` was worse than misplaced: it is a slide shoe with a
domed bottom and four studs on *top*, so the annotation had the wrong
gender on the wrong face. Neither error was visible by reading the YAML.
Both were obvious the moment a fixture tried to clutch them.

Hence the pairing in `tools/fixtures/`: `good-expansion-gears-on-axle`
mates gears and bushes onto an axle, and `bad-expansion-gear-off-axis`
holds the same gear in its native orientation on the same axle and expects
`CONTACT WITHOUT JOINT`. That message is the signature of a wrong axis:
the parts touch, and nothing engages.

## Joints the checker has no vocabulary for

Everything above is one shape of connection: a male shaft entering a female
bore. These are not, and today they are invisible -- not wrong, *absent*:

- **Stud into a plate's underside.** LDraw draws that underside as tubes
  sitting *between* studs, so a stud at a grid position is 14 LDU from the
  nearest bore and never matches. Two plain plates stacked report zero
  joints. Every stud connection that works today works because a hand-
  written `anti_stud` put a pocket where the stud actually lands.
- **Turntable top to bottom.** A ring seating in a groove, not a pin.
  `rotates: true` only excuses the halves from the hinge rule; it does not
  check they are mated, coaxial, or the right way up. A cab floating above
  its base passes.
- **Gear mesh** -- now declared, not inferred. Teeth engage only at a
  specific centre distance with parallel, coplanar axes. Undeclared, two
  meshed gears read as CONTACT WITHOUT JOINT and two gears 40 LDU apart
  read as fine. `0 !LDRCHECK MESH <gear> <partner> <distance>` says which
  pairs are meant to mesh: it fails if any gear is not `distance` from a
  partner's origin (a gear's or a curved rack's ring centre) in its
  plane, excuses their teeth touching, and allows them **zero** shared
  solid -- teeth interleave so shallowly (3.8 LDU for a Z28 in the
  43038 ring) that tip-on-tip overlaps less than OVERLAP_TOLERANCE.
  Pitch radius is 1.25 LDU per tooth, so centre distances come from tooth
  counts. Mid-build pages forgive a gear whose partner is not on yet.
  It does not know gear ratios or which gear drives; `tools/swing.py
  --roll` turns a carried gear for a swing. Fixtures:
  `good-gear-mesh-rack`, `bad-gear-mesh-undeclared`,
  `bad-gear-short-of-rack`, `bad-gear-tooth-on-tooth`.
- **Rack and pinion**, which adds a travel direction and end stops.
- **Belt and pulley.** The V-belts are marked `decorative`, which means
  "excused from needing a joint" -- a placeholder, not understanding.

Worth naming the risk plainly: a build that leans on any of these can pass
clean and still not work. The turntable is the one an excavator reaches
for first; gear mesh is covered only where a model says MESH.
