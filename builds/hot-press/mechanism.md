# Mechanism -- Hot Press

A slider-crank built from one SPIKE Essential box, with the drive on
top. No gears, no smooth pins. Ground is `y = 8`, the underside of the
white 16x16 plate. Up is -Y. The front is +Z, where the motor's face is.

## The parts of the machine

- **Frame.** A red 2x4 brick sits in the middle of the table, the bottom
  hot plate. A dark green round brick touches each end, and a black 8M
  axle stands up in each. The axles are the guides.
- **Press plate.** The green 2x8 plate with holes rides the two axles in
  its end holes, so it can only go up and down. A red 2x4 brick under it
  is the press head. A red 1x2 plate with two holes stands on its front
  edge, the hinge.
- **Tower.** Three red 2x2x3 bricks behind the press. On top, a purple
  1x4 Technic brick on the front row and an orange 1x4 on the back row,
  locked by a red 2x4 tile.
- **Motor.** Two pegs in the purple brick's end holes go into the two
  back holes level with the motor's hub. The motor's back is flat on the
  tower's front and its bottom hangs over the press. Its hub faces the
  front.
- **Crank.** One peg in a hole of the hub itself. The hub's four holes
  are 20 LDU from its middle, so that is the crank radius. No crank arm.
- **Rod.** The blue 7M beam, end holes 120 LDU apart. Top hole on the
  crank peg, bottom hole on a peg in the hinge's lower hole.

## The stroke

Crank radius 20 LDU, so the press moves 40 LDU (16 mm) top to bottom.

| | crank peg | hinge hole | plate top | head bottom | head over the wood's studs |
|---|---|---|---|---|---|
| top of the turn (the file) | -250 | -130 | -120 | -88 | 44 LDU (17.6 mm) |
| bottom of the turn | -210 | -90 | -80 | -48 | 4 LDU (1.6 mm) |

The wood's top is `y = -40` and its studs reach `-44`. The head stops
4 LDU above them. That is on purpose. A slider-crank cannot stop early:
if the head met the wood before the bottom of the turn, the motor would
stall against the bricks and the program would wait forever. Four LDU
reads as touching from a child's seat. It also keeps the head's
underside off the wood's studs, so the head never grabs the wood.

From the top of the turn, half a turn either way goes to the bottom.
The program does two clockwise half-turns, so the hub goes all the way
round once, the way a real press runs.

A short crank pushes harder. The motor's twist divided by the crank
radius is the push at the peg. A crank half as long pushes twice as
hard, and moves half as far. 16 mm is plenty for a press that only has
to look like it squeezes.

## The whole turn

The model was written out at every 15 degrees of the turn and each pose
went through `ldrcheck check`. Nothing collides in any pose. The closest
places:

- The motor's bottom and the top of the hinge, with the press open:
  42 LDU apart.
- The rod's top end and the eyes: at least 14 LDU apart.
- The rod rides at z = 20 to 40, in front of the press plate and the
  tower, and tips at most about 10 degrees (`asin(20/120)`).

The only flag in those poses is not real. The checker draws the motor's
hub as part of the still motor, so when the pose files turn the crank
peg, it lands in solid hub instead of in a hole that turned with it.

`0 !LDRCHECK` lines in `model.ldr`:

- `PIVOT 3707.dat +Y`: the press plate slides on the guide axles.
- `PIVOT 61332.dat +Z`: the rod turns on the crank peg and the hinge
  peg.
- `CLEARANCE 3738.dat 120`: the file is the open pose.
- `JOINS 14769.dat 61332.dat` and `JOINS 11127.dat 61332.dat`: the eyes
  and the crystals are on pegs, not floating. Both are marked decorative
  in `tools/connections.yml`, so this line is what checks them.

## The face

Two pegs in the motor's front holes, 60 LDU above the hub, carry the two
big eye tiles. The hub under them is the mouth. Two pegs in the motor's
top holes carry a red crystal and a green crystal, the same red and
green the matrix shows: hot, then done. A frog, a bush, and two grass
stems finish the garden. The bush is the tree nobody had to cut.

## What this is not

The wood does not get thinner. The single plate in front is the picture
of super wood. Red bricks, the red crystal, and the red matrix are the
picture of heat. Nothing is warmed and nothing is soaked.
