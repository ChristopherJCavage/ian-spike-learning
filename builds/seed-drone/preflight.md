# Pre-flight -- Seed Drone

`ldrcheck` proves static geometry and clutch. It does not prove that a
loose ball rolls, that a motor turns the useful direction, or that a
colour sensor recognises construction paper. Run the machine checks, then
perform every table check before class.

## Machine (must be green)

```
python3 tools/ldrcheck.py check builds/seed-drone/model.ldr
python3 tools/ldrcheck.py steps builds/seed-drone/model.ldr
python3 tools/ldrcheck.py fixtures
python3 tools/pages.py check builds/seed-drone
python3 tools/blocks.py check builds/seed-drone
python3 tools/blocks.py fixtures
```

Expected:

- model: 58 parts, 34 steps, 0 problems, and an empty NO GEOMETRY list;
- build order: 0 problems;
- pages: 36 instruction blocks and rows, 34 step PNGs, 0 problems;
- Icon Blocks program: 0 problems;
- both fixture suites pass.

The model declares:

```
0 !LDRCHECK GROUND 32
0 !LDRCHECK FRONT +Z
0 !LDRCHECK FACES 37308.dat +Y
0 !LDRCHECK CLEARANCE 37308.dat 40
0 !LDRCHECK JOINS 37308.dat 67351.dat
0 !LDRCHECK JOINS 68488.dat 32526.dat
0 !LDRCHECK PIVOT 3706.dat +Z
0 !LDRCHECK PIVOT 3705.dat +Y
```

## Table checks

### 1. Load and tip the bay

With power off, press one red D16.5 ball down into the channel. The ball is
41.6 LDU across and the channel is 40, so it will not reach the floor: it
wedges between the tops of the two purple walls and is held there. Carry the
model level, then shake it gently. The seed must not shift or fall out.

That grip is the point of the tray, and it is also the one thing here that
CAD cannot settle. Turn the red motor axle slowly by hand until the open end
has rotated about a quarter-turn. The seed must let go and roll out. If it
stays wedged at 90 degrees, ease one purple wall out by a stud and accept a
looser well -- a seed that will not drop is worse than a seed that rattles.

Watch also that the tray clears the motor, green bracket, spine, and table
through the whole quarter-turn.

The bay now hangs off the back of the drone on a green right-angle beam.
Wiggle the tray sideways: the beam must not rock on its two spine pins. If
it does, one pin is in the beam's shared corner hole and the geometry is
wrong -- see `mechanism.md`.

### 2. Calibrate motor direction and travel

Plug the Colour Sensor into A and the Small Angular Motor into B. Run the
program once with an empty tray.

- If "clockwise" raises the open edge instead of lowering it, swap the two
  direction blocks in `program.spike` and re-render the program.
- If 0.25 rotations hits a hard stop, reduce both rotation values equally.
- If the ball does not clear the lip, increase both values slightly.
- If the ball stays wedged, see the hand test above before touching the code.
- The return move must leave the floor level enough to reload.

Do not stall the motor against the structure.

### 3. Test the red target

The target is the red band in `builds/rainforest-drop-zone`: two Bright Red
2x4 tiles butted side by side, wall to wall across the lane. Rest the two
slide shoes on the plate first; then lift only a few millimetres.
The sensor lens sits about 16.4 mm above the shoe plane, but `CLEARANCE` is
only a minimum-distance check -- it cannot tell whether the sensor is too
high to read.

Watch the Hub, not the tiles. You want a steady **red** over the patch and
nothing over the white plate beside it. If it is unreliable, recalibrate in
the SPIKE App. Do not lower the sensor below the skids.

**The seed is red too**, because Bright Red is the only ball colour in the
box. So a dropped seed lying on white plate is a valid target as far as the
sensor is concerned, and flying back over one will fire the program again.
Pick the seed up between passes. That is not a real limitation -- there are
only five balls, so someone is collecting them anyway -- but it will look
like a bug the first time it happens.

There is no orange near the target any more -- the four orange corner marks
of the earlier island were dropped because the sensor confused them with
red -- so the only false targets left are a dropped seed and a grass tuft
that has crept over the band. See the drop zone's own `preflight.md`.

### 4. Check the rotor

Hold the yellow Hub in both hands, keep fingers below the rotor plane,
and flick one purple blade gently. Both blades and the green hub
must turn together while the blue 7M bearing beam stays fixed.

The black vertical axle must stop on or just above the yellow Hub roof; it
must not be forced into the plastic. The rotor is passive and must remain
passive. This model does not fly.

Now the check this build exists to teach: **tug each blade straight up.**
Neither may lift off. The first version of this rotor mounted each blade on
two smooth yellow axles standing in the green plate's round holes, which
holds nothing at all -- the blades came off in the hand on the first flick,
while every CAD check passed. Each blade now has one yellow axle beside the
centre, locked in the dark-green brick's cross hole, and one black friction
peg at the far end of the plate, gripping a round hole. If a blade lifts,
the likely cause is a yellow axle that never reached the cross hole: push it
down until it stops.

The blades float about 12 LDU above the plate's studs and that is correct --
a Technic beam has no studs underneath, so nothing about it can clutch the
plate and the two fasteners are the only things holding it. A blade sitting
flat on the studs means it is not pushed down onto its fasteners.

Then load the tray and flick again. Geometry says the blades pass 30 LDU
(about 1.2 cm) over the ball, but confirm by eye that a full turn never
brushes the seed. That figure was 43 LDU before the blades came down to
where a 40-LDU peg could reach them, and it lost another 5 when the seed
stopped resting on the tray floor and rose up between the wall tops, so it
is worth an actual look.

### 5. Route both cables

Both ports sit under the tail spine, and the seed bay hangs behind them.
`PORT ACCESS` proves the plugs fit, not that the wires stay out of a
child's grip, the tipping tray, or the rotor. Route each cable out to one
side of the spine, keep both clear of the tray's swing, leave a small
service loop at each device, and test the full tray motion again.

### 6. Check the face

The two small round white tiles must be the **printed** ones, black iris
and pupil. LDraw cannot draw the print, so no render in this folder shows
the eyes -- match element 6284599 against `parts.txt`. There are four in
the box and the chameleon uses the other two, so there is no spare pair;
count them out before opening the bin.

Two things to confirm by hand, neither of which the checker can see. The
eye pegs must be in the sensor's **forward** holes, not the rear pair that
mounts it -- with the pegs backwards the eyes end up behind the red
brackets. And a peg-mounted eye can be pushed on crooked or pulled off,
unlike a tile on four studs: press each one down flat and tug it gently.
If an eye keeps falling off, that peg is a loose one -- swap it for another
of the 6 spare pegs rather than forcing it.

## Program realities

- Essential streams the program. Keep the tablet connected over Bluetooth
  throughout the handheld mission.
- The "effect sound until done" block supplies the hold-open interval and
  plays through the tablet, not the Hub.
- The colour event hat can fire again if the sensor leaves and re-enters the
  target. Reload only after moving the drone away from the red patch -- and
  away from any seed already on the ground, which is the same red.
- Start with the tray level before pressing Play.

## What the checker cannot see

- The Bright Red ball is `role: decorative` because it is loose payload.
  That correctly exempts it from clutch and support checks; it does not
  prove the tray retains or releases it.
- The checker sees only the rotor's displayed pose, not its swept volume.
- It has no centre-of-mass or grip-comfort model. Hold the completed drone
  over a soft surface and confirm it does not roll in the hand. The seed
  bay hangs a long way aft now, so check specifically that it does not
  nose up when a hand relaxes.
- The purple side bars protrude only 8 mm, and at the table they pop off
  when a child pulls on them. They are not a handhold: the pages tell
  kids to hold the yellow Hub. Watch a child pick the drone up, and add a
  two-hands rule if it rolls.
- All four yellow 3M axles and both purple 11M beams are used, with no
  spares. Confirm those exact quantities before class.

## Class safety and framing

Call it a **handheld model of a survey drone**, not a flying drone. Carry
it by the yellow Hub, never the purple side bars, skim it low, and use
only a gentle finger flick on the rotor. Keep faces, hair, and cables away from the blades.
Drop only the included LEGO ball onto the paper target.
