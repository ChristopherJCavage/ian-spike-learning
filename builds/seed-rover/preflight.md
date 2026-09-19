# Pre-flight -- Seed-Planting Rover

`ldrcheck` is a linter, not a physics engine. This build leans on it
harder than most, because almost every joint is a pin into a hub that has
no studs anywhere on it. Read the second section before you trust the
first.

**This build is not finished.** The last section says what is missing.

## Machine (currently green)

```
python3 tools/ldrcheck.py check builds/seed-rover/model.ldr
python3 tools/ldrcheck.py fixtures
```

`model.ldr` is 25 parts over 13 steps and reports **0 problems**. The
header declares its world and its one intentional pivot:

    0 !LDRCHECK GROUND 8
    0 !LDRCHECK FRONT +Z
    0 !LDRCHECK PIVOT 3707.dat +X

The ground plane is `y = +8` because the tyre's outer radius is 38 and
the drive axle sits at `y = -30`. If the drive axle ever moves, that
number moves with it.

## What the checker cannot see here

**The belt, entirely.** `85546` is a rigid ring in LDraw and carries
`role: decorative`, so it takes part in no check at all. Placing it
proves nothing. What matters is the number it has to span: the two
pulley centres are **95 LDU apart**, which is 38 mm. A relaxed D33 belt
is about 104 mm around, and this path needs roughly 131 mm, so the belt
runs at about 26% stretch. That is at the upper end of believable.
**Loop it on the table before building anything above it.** If it will
not reach, move the bearing brick one hole forward to `z = -80`, which
drops the span to 79 LDU, and move the gate axle and its pulley with it.

**Whether the rover stands up.** There is no centre-of-mass check in
`ldrcheck`, and this rover rides on exactly two wheels at `z = -20` with
a tail reaching back to `z = -140` and motors reaching forward to
`z = +70`. It will rock fore and aft, and the tail is heavy. It needs a
third contact point and does not yet have one.

**The paddle's swing.** The checker looks at one static pose. The paddle
sweeps a circle of radius 63 about `(y = -82, z = -100)`, and nothing in
the model verifies that circle is clear through a full turn. Two things
sit close enough to be worth eyeballing: the drive wheel, whose tyre
reaches `z = -58` against the paddle's `z = -80`, and the hub's rear
lower corner.

**Shallow engagement is expected, twice per side.** The pins from the
motor tops into the 2x8 plates grip 16 LDU, not 20. A 12-thick plate
cannot do better -- the bore is recorded 4 LDU above its own bottom face.
`ldrcheck` reports these as WARN and does not count them as problems,
which is correct: a plate really does hold a pin less firmly than a
brick. If the tail feels floppy in the hand, that is the reason, and the
fix is a brick rather than a plate, not a longer pin. The kit has no
longer pin.

**Colour.** Every part is placed in a colour the Essential kit actually
contains, checked by `COLOUR vs KIT`. That is a real constraint here
because several of these parts only exist in the box in one colour.

## What is missing

Mechanically:

- **The runway and its lip.** Nothing holds the seeds yet.
- **The seeds.** No nose cones are placed.
- **A third contact point**, per the stability note above.

The runway is blocked on a real conflict rather than on effort. The
paddle ended up outboard of the drive wheel, at `x = -205`, because it is
28 LDU thick and the two inboard gaps available to it are 30 and 23. A
runway has to sit in the paddle's plane to be swept, so it too would hang
outboard of the wheel, cantilevered off the back-left corner. That is
buildable and it is ugly.

Moving the paddle inboard means lifting the gate axle clear of the hub's
roof at `y = -80`, and that is where it binds: raising the axle far
enough to clear the hub also pushes it far enough back that the belt span
goes past 125 LDU, which no rubber belt in the kit will cover. **The
short belt and the tall hub are fighting each other, and the outboard
paddle is the honest consequence.** Resolving it properly means changing
the mechanism, not nudging coordinates.

As a lesson:

- **There is no program.** A tank-steering route with a seed count is the
  entire point of the build, and none of it is written or validated
  against `tools/spike/blocks.json`.
- **There are no build instructions.** The files in `renders/` are
  previews to look at, not the numbered pages a child builds from.
- `README.md`, `code.md`, `parts.txt`, `screens.md` and `steps.md` do not
  exist yet.

## Before exempting a part

```
python3 tools/ldrcheck.py holes <part>
```

If it emits studs or tubes, it does not need `role: decorative`. Annotate
the missing male shafts or underside tubes in `tools/connections.yml`
instead. Two parts earned real annotations during this build -- `4185b`
spins on its axle, and `2815` is a tyre and therefore touches the ground
-- and both are facts about the part, not conveniences for the model.
