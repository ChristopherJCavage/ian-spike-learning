# Brief -- Seed-Planting Rover

Status: **filled** (design outline only -- no `model.ldr` yet, see
`mechanism.md` for why).

## Theme / story

A patch of rainforest has burned. The trees are gone, the ground is bare,
and nothing will come back on its own for a long time. So we send a
machine across it that plants as it drives.

The rover is a **seed drill**, which is a real farm machine and works in a
way worth showing a seven-year-old: nothing tells it when to plant. The
planting is geared to the wheel. Roll it further, it plants more. Push it
back and forth on the carpet with the power off and it still drops seeds,
because the ground itself is doing the counting.

That is the story beat to land in class. The kids will expect a button, a
sensor, or a "drop now" block. There is none. **The wheel is the clock.**

## Complexity

- Target step count (Figma pages): 4 story slides, then ~20 build steps +
  1 try-it page + 1 Icon Blocks page.
- How much help Ian gets vs Chris: Chris sets the gate axle height and
  fits the belt (the fussy step -- see the `h` knife edge in
  `mechanism.md`); kids build the chassis, tile the ramp, mount the
  wheels, and load the cones. Code together.
- Sub-assemblies: `chassis` (hub + two motors + skid), `wheels`,
  `belt` (two D24 pulleys + V-belt on the left side), `gate` (axle + arm
  + lip), `ramp` (tilted tiled deck), `code`.

## Hardware

- Hub: **essential** (2 ports A/B, no on-hub matrix, no speaker)
- Motors: 2x Small Angular Motor `68488` -- port A right wheel, port B
  left wheel. Tank steering.
- Sensors: **none, and none possible.** Both ports are motors.
- Done-when: set it on the floor, run the route, and it leaves a line of
  standing orange cones roughly a hand-span apart. Count the "move
  forward" tiles before pressing play and the count matches the seeds.

## Constraints

- Only `kits/45345-essential/parts.txt`. Essential-only on purpose:
  Saturday class, Essential hub, no Prime, no Expansion.
- **Both ports are motors**, so there is no light matrix, no colour
  sensor, and no sound. The falling seeds are the only output the model
  has. This is a feature -- it forces the lesson onto sequencing.
- **The kit has no gears.** Power moves only along an axle or through a
  V-belt between *parallel* axles four studs apart. Every mechanism choice
  in this build follows from that one fact. Four studs is the pulleys'
  number, not the belt's -- see `mechanism.md`.
- **The ramp must be tiled.** A 2x2 nose cone will not slide on bare
  studs. `FLAT TILE 1X8` `4162` (5 in the box) decks it.
- Seeds are 8x `NOSE CONE 2X2X2` in Bright Orange, which arrive under
  **two design IDs**, `14918` and `6834`, four each. Anyone grepping the
  parts file for one ID will conclude there are only four.
- One hub (the Small Hub). Kid screens: Icon Blocks.
- The "burned ground" is a **classroom prop**, not in the model -- a dark
  mat or sheet the rover crosses. Set it up before class.
