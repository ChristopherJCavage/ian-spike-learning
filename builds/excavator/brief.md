# Brief -- Excavator ("Scoop")

Status: **filled**.

## Theme / story

A friendly yellow digger named Scoop. Ian rolls him along the floor by
hand to wherever the digging is, then presses the button on his back and
the arm goes to work: the boom drops, the bucket curls under and scoops,
and the boom lifts the load clear. Press again and the bucket tips the
load out. The hub face watches the arm -- eyes down while digging, happy
when the bucket dumps.

Honest naming note: with a fixed cab this is a **backhoe**, not a true
excavator. Ian gets to call it an excavator. The cab does not slew because
the checker cannot yet see a turntable joint at all -- see `preflight.md`
and `context/ldraw-connections.md`.

## Complexity

- Target step count (Figma pages): ~20 build steps + 1 code page.
- How much help Ian gets vs Chris: Chris builds the chassis and mounts the
  two motors and the sensor (the pin-heavy steps); Ian puts on the wheels,
  the bucket, the cab details, and presses everything home. Code together.
- Sub-assemblies: `base` (chassis beams + free-rolling axles), `wheels`,
  `cab` (hub + face), `boom` (large motor + lifting arm), `bucket`
  (medium motor + curling scoop), `trigger` (force sensor), `code`.

## Hardware

- Hub: **prime** (needs 3 ports and the Large Motor's torque)
- Motors: 1x Large Motor -> port A (boom lift -- highest torque, it holds
  the arm's weight against gravity); 1x Medium Angular Motor -> port B
  (bucket curl, carried on the boom)
- Sensors: Force Sensor -> port D (the dig button, mounted where Ian can
  press it without holding the arm)
- Wheels: four, **free-rolling, no drive motor**. Ian pushes it. He is
  here for the arm, not the driving.
- Done-when: press the force sensor and the arm digs one full scoop --
  boom down, bucket curls in, boom back up holding the load. Press again
  and the bucket tips out. Nothing moves until he presses.

## Constraints

- Only parts listed in `kits/*/parts.txt` (Essential 45345, Prime 45678,
  Expansion 45681). Every `parts.txt` line grepped against all three.
- One hub (Prime). The Expansion has none of its own.
- No turntable: the cab is fixed. Not a style choice -- a correctly
  assembled turntable currently fails `ldrcheck` with five problems,
  including a phantom interpenetration where the rings interleave.
- Kid screens: Word Blocks.
