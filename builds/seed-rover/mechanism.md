# Mechanism -- Seed-Planting Rover

Measured, not guessed. Every number here came out of
`python3 tools/ldrcheck.py measure <part>` against the LDraw library, or
out of `kits/45345-essential/parts.txt`.

## The two facts the whole design hangs on

**1. The Essential kit has no gears.** Not one. Power moves along an axle,
or through a V-belt between two *parallel* axles. That single constraint
kills every design that needs to turn a corner: no bevel takeoff, no
vertical carousel, no worm feeder. Whatever meters the seeds has to spin
about a **transverse horizontal axis**, the same way the wheels do.

**2. The drive wheel rolls 9.55 cm per revolution.** Belt it 1:1 to a gate
axle and one gate revolution happens per 9.55 cm of ground travelled.

That number comes from the *second* wheel we tried, and the swap was
forced rather than chosen. The obvious drive wheel is the dia.43
(`65834`, 108 LDU across, 13.57 cm per turn), and the first draft used it.
But `ldrcheck holes` reports `65834` as carrying four pin holes on a
radius-20 circle and **no central bore at all**. A wheel with no bore
cannot have an axle pass through it, so it can never share a shaft with a
belt pulley -- and sharing a shaft is the whole mechanism. Nor can the
pulley be spaced outboard of it: that needs a pin longer than the 2M
`61332`, which is the only pin the kit has.

So the drive wheel became a **wedge-belt wheel `4185b` wearing tyre
`2815`**, which does have a native cross bore. Tyre outside diameter is
76 LDU = 3.04 cm, so `pi * 3.04` = **9.55 cm per revolution**. Rounder for
a kid to hold in their head, and it makes the rover's stride about a hand
span. The four dia.43 wheels stay in the box.

Put those together and the machine designs itself into a **seed drill**:
metering driven off the land wheel, so spacing follows *distance*, not
time. That is what a real drill is, and it is more robust than any trigger
we could have invented.

## Why there is no pusher (a design that was tried and failed)

The first pass had an arm on the gate axle shoving a train of standing
cones forward one cone-width per revolution, the lead one walking off the
back edge.

Drawing it to scale killed it. The train is consumed **from the front**,
so after each cycle every remaining cone sits 40 LDU further back --
including the rear-most one, which is where the arm pushes. The contact
point recedes 40 LDU per seed. A fixed arm gets two or three cycles and
then swings through empty air.

The fix is smaller and closer to the real machine: **tilt the ramp and let
gravity feed the train forward against a fixed lip.** Now the lead cone is
always in the same place, the arm only ever touches that one cone, and the
ramp reloads itself. The arm stopped being a conveyor and became a gate.

## Side view

```
              S I D E   V I E W   --  left side, front to the right

   rear                                                                front

      /\   /\   /\   /\   /\                          ______________________
     /__\ /__\ /__\ /__\ /__\                        |                      |
    ==========================                       |   SMALL HUB  67351   |
      tiled ramp, ~12 deg  ``--..__                  |  140w x 80h x 100L   |
                                   ``--..__          |______________________|
                                           ``--..    |        |        |
                              (O) gate axle, y=134   |        |        |
                               |  ||                [ MOTOR B ][ MOTOR A ]
                               |  || belt, 80 LDU             |
                          [#]  |  ||  (four studs)            |
                    lip ---^   v  ||        (O) drive axle, y=54
                       y=67                (      )              (o) slide shoe
                                            dia.43 wheel          2654, y=8
   =============================================================================
                     ^
                seed drops 67 LDU (27 mm), lands base-down

   overall length ~600 LDU (24 cm), width ~230 LDU (9 cm)
```

## Gate detail -- where the arithmetic lives

```
                    G A T E   D E T A I L   (zoomed ~2x)

                          (O)  gate axle, belted 1:1 to the left wheel
                         / |
                        /  |
              arm ---> /   |   arm = TECHNIC BRICK 1X4 (3701)
           1x4 brick  /    |   pivoted at its END hole
                     /     |   tip radius R = 70 LDU
                    /      |
                   v       |        h = 67 LDU  (axle above runway)
              ....................  <-- tip dips 3 LDU BELOW the runway
                                        sweep window = 2*sqrt(R^2 - h^2)
     /\    /\    /\   /\                            = 2*sqrt(4900-4489)
    /__\  /__\  /__\ /__\  <-- lead cone at the lip  = 40 LDU
   ______________________[#]                           = EXACTLY one cone
   runway, tiled, 2 wide  ^
        gravity feed -->  lip holds the train
```

The arm tip is below the runway only while `|x| <= sqrt(R^2 - h^2)`, so
the sweep window is `2 * sqrt(R^2 - h^2)`. With `R = 70`:

| `h` (LDU) | window | result |
|---|---|---|
| 59 (ramp one plate high) | 75 LDU | dumps two cones a turn |
| **67 (design point)** | **40 LDU** | **exactly one cone width** |
| 75 (ramp one plate low) | negative | arm never reaches, nothing plants |

One plate of ramp height, 8 LDU, is the difference between double-seeding
and not planting at all. **This is the fussy step and it belongs to the
adult.** Mount the gate axle in a beam with spare holes above and below so
the height can be trimmed at the table.

## Top view

```
                       T O P   V I E W   (front to the right)

        |<---------------- 8 cones, 16 studs -------------->|

    +===========================================+
    |                                           |         (O)===(  )   dia.43
    |   /\  /\  /\  /\  /\  /\  /\  /\          |          |    ^
    |   \/  \/  \/  \/  \/  \/  \/  \/          |==[belt]==+  MOTOR B
    |         runway, 2 studs wide              |  1:1        |
    |                                     [#]   |          [ HUB ]      (o) skid
    |                                           |             |
    +===========================================+          MOTOR A
                                                            |    v
                                                           (O)===(  )   dia.43

        belt runs on the LEFT side only: D24 pulley on the drive axle,
        D24 pulley on the gate axle, 80 LDU (four studs) apart
```

## Why the belt span is four studs, not two

The first draft got this wrong, and the mistake is worth keeping on the
page because it is an easy one to repeat.

Solve the belt equation on its own and you get a short span. `85546`
measures 86.31 LDU across its free loop, so the belt is about `pi * 33 mm`
= 104 mm long; round two D24 pulleys, `104 = pi * 24 + 2c` puts `c` near
40 LDU, about 2 studs. That number went straight into the design.

It is nonsense, because **a D24 pulley is 60 LDU across**. Two of them
with centres 40 apart are inside one another. `ldrcheck` on
`tools/fixtures/bad-belt-pulleys-too-close.ldr` reports exactly that.

The floor is 60 LDU, where the pulleys are tangent and still raise CONTACT
WITHOUT JOINT. Beam holes come on a 20 LDU pitch, so the first span that
is both clear and buildable is **80 LDU, four studs**, proved clean by
`tools/fixtures/good-belt-on-pulleys.ldr`.

The belt therefore runs stretched. That is normal for a LEGO rubber belt
and impossible to verify in LDraw, where the part is a rigid ring.
**Whether it physically reaches at four studs is a table check.**

## Why the ramp is 12 degrees and not 25

A `NOSE CONE 2X2X2` measures 40 wide by 48 tall. A block that shape topples
once the slope passes about 40 degrees, and it wants a margin. Twelve
degrees is steep enough to slide on tile and shallow enough that the cones
stay standing the whole way down.

It must be **tiled**. A cone will not slide on bare studs. `FLAT TILE 1X8`
`4162` decks it, and there are exactly 5 in the box for a 2x16 run.

## Parts, measured

| part | LDraw | size (LDU) | the number that mattered |
|---|---|---|---|
| Small Hub | `67351` | 140 x 80 x 100 | origin at its bottom face |
| Small Angular Motor | `68488` | 60 x 80 x 99 | a third the length of the Large Motor |
| Wheel dia.43 | `65834` | 108 dia, 35 wide | NO central bore -- ruled it out |
| Tyre for D24 | `2815` | 76 outside dia | 9.55 cm per revolution |
| Wedge-belt wheel D24 | `4185b` | 60 dia, 10 thick | 60 across is why the span is 4 studs |
| V-belt D33 | `85546` | 86.31 free loop | rigid ring, decorative, checker-invisible |
| Nose cone 2x2x2 | `14918` / `6834` | 40 x 40 x 48 | tips at ~40 deg |
| Slide shoe round 2x2 | `2654` | 40 x 40 x 12 | hangs 8 below its plate |
| Technic brick 1x4 | `3701` | 80 long | `R = 70` from the end hole |
| Plate 8x16 | `92438` | 320 x 160 | the ramp deck |

## The lesson the numbers hand us

The belt is 1:1, so **one wheel rotation = one seed = 9.55 cm**.

- **Icon Blocks (class).** Driving is counted in rotations, so the number
  of "move forward" tiles *is* the number of seeds. Kids can predict the
  field before pressing play.
- **Word Blocks (home).** `flippermove_setDistance` -- "set 1 motor
  rotation to 9.55 cm moved" -- calibrates the hub to these wheels, after
  which "move forward 29 cm" plants exactly three.

## What the checker can and cannot see

A first draft of this page got both of these wrong, in the direction that
would send a modelling run chasing problems that do not exist. Corrected:

- **The belt is invisible to the checker -- tested, not assumed.**
  `85546.dat` carries `role: decorative` in `tools/connections.yml`, and
  `tools/fixtures/good-belt-on-pulleys.ldr` shows what that buys: the belt
  is placed floating between two pulleys, geometrically impossible, and
  the model still checks **0 problems**. No NO JOINT, and it never appears
  in INTERPENETRATION. The gate axle is not an orphan cluster either,
  because it sits in a beam pinned to the chassis -- the belt carries
  power, not structure.

  So the belt can go straight into `model.ldr`, and LeoCAD will render it.
  It will render as a **rigid ring floating between the pulleys**, since
  the LDraw part is a fixed 86.31 circle that cannot wrap anything. That
  is a problem for the instruction art, not for the checker. The
  chameleon's flex hose precedent -- cut from the model, kept in the Figma
  drawing -- is there if the render looks worse than the omission.
- **The stud gap is plate-on-plate, not plate-on-brick.** The fixtures
  `good-plate-on-brick.ldr` and `good-colour-tile-on-plate.ldr` already
  pass. So land the ramp deck on **bricks** rather than stacked plates and
  the tiles register normally. This is a design constraint that costs
  nothing to honour, not a checker limitation to work around.

`pages.py` never calls `ldrcheck`; the two are independent. `pages.py
check` verifies the three-way sync of `0 STEP`, `steps.md`, `screens.md`
and the renders, then shells to LeoCAD. LeoCAD will render a model the
checker hates. "Clean before renders count" is a house rule, not a gate.

Human checks that stay human:

- Metering is tied to the left wheel, so a **pivot turn still plants**.
  Real drills have this problem too, which is why they lift out of gear at
  the headland. Keep spins away from the end of the route or the rover
  will pile seeds in one spot.
- **Essential streams** rather than downloads, so the tablet stays
  tethered for the whole run. A rover that drives a metre off and loses
  the connection stops mid-route.
- Icon Blocks tiles are recorded in `tools/spike/blocks.json` as artwork
  with no argument schema, so the numeric widget on "move forward" has to
  be confirmed at the tablet before the lesson plan promises a seed count.

## Notes for whoever models this

These are the **as-built** numbers from `model.ldr`, which passes
`ldrcheck` at 0 problems for everything through the drivetrain.

World: `0 !LDRCHECK GROUND 8`, `0 !LDRCHECK FRONT +Z`, and `+Y is DOWN`.
Hub `67351` sits at the origin with its own origin on its **bottom** face,
so it occupies `y = -80..0`, `x = -70..70`, `z = -50..50`.

| feature | above ground | LDraw y |
|---|---|---|
| ground plane | 0 | +8 |
| drive axle (tyre radius 38) | 38 | -30 |
| hub underside | 8 | 0 |
| hub top | 88 | -80 |
| tail plate top (stud face) | 76 | -68 |
| gate axle | 90 | -82 |

The gate axle sits at `z = -100`, the drive axle at `z = -20`, both in the
`x = -168` belt plane. That is a centre distance of 95 LDU. It is longer
than the 80 the fixture proved and the belt will be working hard; if it
will not reach on the table, the bearing brick moves one hole forward to
`z = -80` and the span drops to 79.

One placement is an admitted compromise. The paddle hangs **outboard of
the drive wheel**, at `x = -205`, because it does not fit anywhere else:
it is 28 LDU thick, and the two inboard gaps available to it -- between
the tail plate and the hub, and between the tail plate and the pulley --
are 30 and 23. It works and it checks clean, but it is exposed, and it
drops its seed in the left wheel's track rather than on the centreline.
Moving it inboard means getting the gate axle above the hub's roof at
`y = -80` so the axle can run across the model, which needs one more
plate of height under the bearing.

Two placements are forced rather than chosen, and it is worth knowing
which, because they are the ones you cannot slide around later.

- **Motors at `y = -30`.** A motor's back face offers mounting holes at
  `y-20`, `y` and `y+20`; the hub's side face offers `-50`, `-30`, `-10`.
  Those two patterns line up at exactly one value.
- **Motors at `x = -+100`.** That is what puts each back face flush on the
  hub's side at `x = -+70`.

Everything downstream -- axle height, ground plane, ride height, the whole
seed-drop budget -- falls out of those two.

## The tail is the hard part, and here is why

The chassis went in cleanly. The tail did not, and the reason is worth
recording, because it is a property of the *hub*, not of this design.

**The Small Hub has no studs.** `ldrcheck holes 67351` returns 23 pin
holes and nothing else. Nothing stacks on it. Every single thing you
attach to this rover is pinned, which is a much stiffer constraint than
the stud-and-plate building most of these models rely on.

Worse, of those 23 holes, the ones facing upward are **two**, at
`(-+60, -80, -40)`. They are 120 LDU apart, and the widest vertical-hole
part in the Essential kit spans 120 (`3738`, a 2x8 plate with holes) --
but a part that long also runs straight through the hub's own volume once
you drop it to hole height. So the hub's roof is, for practical purposes,
not a mounting surface.

The better anchor is the **motors**. Each one presents four upward pin
holes on a 40 x 40 rectangle -- on the left motor at `x = -120, -80` and
`z = -40, 0`, all at `y = -60`. Two motors give eight. A `3709` (2x4 plate
with 3 holes) turned to run fore-and-aft bridges one motor's pair exactly.

One thing to expect when you build on them: **a vertical pin into a plate
or brick from below cannot reach 20 LDU of grip.** The bore is recorded
starting 4 to 6 LDU above the part's own bottom face, so a 40 LDU pin
splits as 20 into the motor and roughly 14 into the part above, and
`ldrcheck` calls SHALLOW ENGAGEMENT. That is not a modelling error -- a
plate really does grip a pin less than a brick does. It needs either a
longer pin than the kit has, or a design that takes the load in shear
rather than relying on that one joint.

## Notes on matrices

This is the trap that cost two iterations on the excavator, and it fails
**silently** -- a mis-turned part simply joins nothing.

- A pin `61332` carries its shaft on its own **X**. Identity lays it
  across the model. To point it down world Z: `0 0 1 0 1 0 -1 0 0`.
- A cross axle `3705` / `3706` carries its length on its own **X**. To run
  it along world Z: `0 0 -1 0 1 0 1 0 0`.
- A motor `68488` carries its output bore on its own **Y**, so its own Y
  is the axis that has to become world X. `0 1 0 / -1 0 0 / 0 0 1` for the
  left flank, `0 -1 0 / 1 0 0 / 0 0 1` mirrored for the right.
- A pulley `4185b`, a wheel `65834` and the belt `85546` all carry their
  rotation axis on their own **Z**. To turn that onto world X, which is
  what a transverse axle needs: `0 0 1 0 1 0 -1 0 0`.
- A technic brick lying along its own X carries holes on its own Z.
  Standing it upright with `0 1 0 0 0 1 1 0 0` keeps the holes facing X
  while the length runs down Y.

Rules that are cheap to honour and expensive to discover:

- **Land the ramp deck on bricks, never plate-on-plate.** A stud into a
  plate underside registers no joint, because LDraw puts the tubes between
  the studs. Plate or tile onto a *brick* is fine and already has passing
  fixtures.
- **Pulley centres 80 LDU apart.** Not 40, not 60.
- **Two things cannot claim the same slice of one axle.** A pulley's bore
  is 20 LDU deep and starts 5 LDU behind the part's own centre, so a
  pulley at `x` owns the axle from `x-5` to `x+15`. The motor's bore owns
  its own 20. Crowd them and `ldrcheck` reports PIN SLICE CONFLICT, which
  is the checker noticing that in real plastic one of them would not go
  on. On this model the belt pulley sits at `-168` and the drive wheel at
  `-190` for exactly that reason.
- **Run `ldrcheck check` after every `0 STEP`.** A wrong matrix eight
  steps back is nearly free to fix and very expensive to find.
- The belt is decorative and checker-invisible. Placing it costs nothing
  and proves nothing.
