# Geometry -- Hot Press

Measured with `ldrcheck holes` and `measure` before any brick was placed.
LDU, +Y is down. World positions are in the open pose.

## Holes that carry the machine

- **Motor `68488`.** Hub axle hole at local (0, -50, 0). The four hub
  holes are 20 LDU around it and turn with the hub. Two back holes at
  local (+-20, 30, 0), level with the hub. Two front holes at local
  (+-20, -30, 60), 60 above the hub. Two top holes at local (+-20, 0, 70).
  Turned hub-forward at (0, -230, -30): the hub's middle is world
  (0, -230), its face at z = 20, the back face at z = -60.
- **Purple Technic brick `3701`.** Three holes at local x = -20, 0, 20,
  10 below its top, axis Z. On the tower at y = -240, the holes are at
  y = -230, level with the hub. Its front face is z = -60, the motor's
  back face.
- **Hinge `32530`.** Two holes, axis Z, at local y = -2 and -22, over a
  plate part from y = 0 to 8. On the press plate, the lower hole is
  10 LDU above the plate's top.
- **Rod `32524`.** 7M, end holes 120 apart.
- **Press plate `3738`.** Round holes at local x = -60 to +60, every 20.
  The guides use -60 and +60.
- **Socket `6143`.** One axle hole on Y. A cross axle grips it.

## Why the numbers close

Studs sit on odd multiples of 10 and the holes along a Technic brick sit
on even multiples, between the studs. The hub's middle, the purple
brick's middle hole, and the hinge's hole are all at x = 0. The motor's
back holes at x = +-20 land on the purple brick's end holes.

Up the middle:

- Table top 0. Bottom hot plate `-24 .. 0`. Wood `-40 .. -24`, studs to
  -44.
- Tower: three 72-tall bricks, top at -216. Purple brick `-240 .. -216`,
  holes at -230. That is the hub.
- Open: crank peg 20 above the hub, at -250. Rod 120 down, hinge hole
  at -130. Plate top 10 lower, at -120. Head brick under the 8-LDU
  plate, bottom at -88.
- Closed: everything 40 lower. Head bottom at -48, 4 above the studs.

The guide axles run from -7.5 to -167.5. The plate's top is at -120 when
open, so 47 LDU of axle stays above it.

## Measured and not used

- `32526` (3x5 angle beam) and `65249` (axle-pin bush) made a crank arm
  in an earlier draft. The hub's own holes are a shorter, stiffer crank.
- `95347` (lattice tower): one axle hole at the top. It does not guide
  a plate.
