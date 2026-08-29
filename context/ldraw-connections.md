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

## Axles and bushes

A cross axle is a male shaft that runs through axle holes and through the
round holes of a Technic beam. It needs something to stop it sliding out:
a bush, a wheel whose hub fills the end, or a second part whose hole is
the last stop. An axle through one hole and into empty space is a pin
with the other end missing.

Bushes (`4265c` / `32123b`) sit on an axle. They are retainers, not
two-ended fasteners. A bush in mid-air is as wrong as a peg in mid-air.

## Studs versus Technic holes

System bricks clutch stud-into-tube. Technic beams clutch pin-into-hole
and axle-into-hole. The Prime Hub's top is **smooth** -- it has pin holes,
not studs. You cannot press a brick onto it. You pin a Technic-to-stud
converter (a plate with holes, a pin-with-stud brick) into those holes,
then build on the studs.

A tile sitting on a smooth plastic face is decoration in the render, not
a build.

## What LDraw does and does not tell you

LDraw primitives (`peghole`, `beamhole`, `connhole`, `axlehole`, `stud`)
mark female holes and studs. They do **not** mark male shafts. Every pin
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
holds the 48 mismatches in these two kits. Decorative prints and molds
that LDraw simply does not have stay unmapped; the checker treats them as
empty geometry.

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
(`facing: -Z` in `connections.yml`). The model declares its own front with
`0 !LDRCHECK FRONT +Z`. Identity on a minifig therefore points the driver
at the rear of a +Z truck. 180 about Y (`-1 0 0 0 1 0 0 0 -1`) is the
matrix that faces them forward -- the same matrix the distance sensor
already used.

Figures are a pose, not a joint. The checker can demand they face FRONT and
that they do not occupy the seat's volume. Sitting them in the seat at the
table stays a human step.

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

Comments keep the *why* ("a 9M beam cannot reach z = -80"). That rationale
can still rot, so re-reading it is a line on the pre-flight checklist, not
a promise the tooling makes.

Every defect found by eye should become three artifacts: a paragraph here,
a rule in `ldrcheck.py`, and a fixture in `tools/fixtures/`.
