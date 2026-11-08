# Brief -- Hot Press

Status: **filled**.

## Theme / story

The club poster shows a press that squeezes softened wood so an old plank
can be used again and a new tree does not have to be cut. This build is
that press. A red head comes down onto two light orange plates, the old
wood, and lifts again. One more plate in front, half as thick, is the
super wood that comes out. The bricks do not change. Nothing is heated
and nothing is soaked.

## Complexity

- 20 build pages, then a turn-it-by-hand page and an Icon Blocks page.
- Ian builds the table, the wood, the tower, the face, the lights, and
  the garden. Chris helps with the sliding plate, the motor pegs, and
  the blue beam.
- One action per page.

## Hardware

- Hub: **Essential Small Hub**, beside the press, not in the model.
- Motor: **one Small Angular Motor** on port B, pinned to the red tower
  by two pegs through its back. Its turning hub is the crank, so nobody
  holds it.
- Light: **3x3 matrix** on port A, stood in front of the press, lights
  toward the room. It is not a brick in the model.
- Done-when: start with the press open and tap play. The matrix turns
  red, the press comes down onto the wood, a sound plays, the press goes
  back up, and the matrix turns green.

## Constraints

- Essential-only. Every model part is in `kits/45345-essential/parts.txt`.
- No gears and no smooth pins. The two moving joints are friction pegs
  in beam holes.
- The crank is one peg in the motor's own hub, 20 LDU (8 mm) from the
  middle. The press moves 40 LDU (16 mm). At the bottom the red head
  stops 4 LDU (1.6 mm) over the wood's studs: close enough to read as a
  squeeze, never close enough to jam the motor.
- Kid screens use Icon Blocks.
