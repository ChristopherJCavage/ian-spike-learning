# Brief -- Half-pipe Swing

Status: **filled**.

## Theme / story

Ian is big into skateboarding. Leo stands on an orange board at the end of
a swinging arm, inside a real curved half-pipe built from four
quarter-circle gear racks. Under his board, two grey gears ride in the
racks' teeth and roll along them as he swings. Press the button and he
drops in, swings up to one lip, back across to the other, three times --
the lights on the front flash at every lip -- then rolls to a stop in the
middle, the lights go green, and the hub smiles and cheers.

Five story slides set it up before any bricks, with our animal crew at
a skate park: the trip, the ramp, Sully dropping in, everyone watching, then
"build one" over a LeoCAD shot of the finished model. See `story.md`.

## Complexity

- Target step count (Figma pages): 5 story slides, then 35 build steps +
  1 try-it page + 1 Word Blocks page (37 numbered pages, 42 frames).
- How much help Ian gets vs Chris: Chris does the pin-heavy frame (posts,
  motor, crossbeams, hub, rear legs), holds the back gear while the axle
  goes in, and does the three axles through the ramp; Ian builds the
  rider (T-beam, brick, board, Leo), slides on the bushes and the front
  gear, drops the four ramp pieces on, builds the light tower, and
  presses the button. Code together: Chris reads, Ian taps.
- Sub-assemblies: `base` (two baseplates, two green bricks), `frame`
  (posts, motor, two crossbeams), `hub` (hub on the motor's back, rear
  legs), `button` (force sensor on the back-left corner), `rider` (offset
  beam, arm, T-beam, brick, board, Leo), `gears` (axle, two gears, four
  half bushes), `ramp` (four quarter racks and three axles), `lights`
  (plate, two bricks, light matrix), `code`.

## Hardware

- Hub: **prime** (45678). Needs a motor, a button and a display; the
  Essential hub has two ports and no on-hub matrix. Prime adds the
  speaker and the 5x5.
- Motors: Large Motor (79818) on **port A**, axle toward the front, swings
  the arm. Its rotation sensor knows where Leo is, so "go to position"
  blocks put him on each lip.
- Sensors: Force Sensor (37312) on **port B**, button up, the "drop in"
  button.
- Lights: the Essential set's **3x3 Color Light Matrix** on **port C**,
  on a little tower in front of the ramp, facing Ian. Flashes orange at
  every lip, green on landing.
- Display: 5x5 shows an arrow toward each lip as Leo heads there, a smile
  when he lands. Hub sound on landing.
- Done-when: press the button and Leo swings lip to lip three times, the
  gears rolling along both rails the whole way and the front lights
  flashing at every lip, then stops level in the middle with green
  lights, a smile and a sound. Nothing but the gears ever touches the
  ramp.

## Constraints

- Parts from all three kits: `kits/45345-essential/parts.txt` (boards,
  Leo, baseplates, bricks, the light matrix), `kits/45678-prime/parts.txt`
  (hub, motor, force sensor, beams, pins, gears),
  `kits/45681-expansion/parts.txt` (the four 43038 quarter racks, half
  bushes). Home build, not the Saturday class, so mixing boxes is fine.
  Every step names its bin.
- One hub (Prime). Three ports used, A, B and C.
- **The ramp is the racks' teeth side, and the gears ride on it.** The
  racks are gear racks with the teeth on the inside of the curve, a
  140-tooth ring. The ramp is two curved rails, back and front, 100 LDU
  apart, and Leo rides in the gap between them. One axle under his board
  carries a Z28 gear in each rail, 140 LDU from the pivot -- exactly
  where a Z28 meshes with that ring -- so as the motor swings him the
  gears roll along the teeth (`tools/swing.py --roll`, see
  `geometry.md`). Everything else stays at least 24 LDU (1 cm) inside the
  teeth. Added after the first version, at Chris's request ("put gears
  on the skateboard that roll along"): the rider was rebuilt around them.
- **The force sensor sits at the back corner on Ian's left, not out
  front.** (Left and right in this build are as Ian sees it from the
  front, where Leo faces him -- so +X in `model.ldr` is his left.) The
  plan put it out front, but the front of the ramp has nothing to pin to:
  anything at the front sits inside the curve the rider sweeps. Behind
  the ramp, standing on the base brick, it is clear of everything and the
  button points straight up, so "drop in" is a push down onto something
  solid. Reach for it over the left-hand lip.
- **The lights stand off the front edge.** On the baseplate's last stud
  row, the light tower would sit flush against the front rail; an orange
  2x4 plate over the edge carries it one row further out.
- **Swing angle: plus/minus 60 degrees.** Leo stays well inside the curve,
  and the gears stay well inside the teeth (at 90 degrees they would run
  off the end of the ring). At 60 degrees the board points at the lip,
  which reads as "up the wall".
- Kid screens: **Word Blocks**. Icon motor tiles turn whole rotations
  (`tools/spike_extract.py` `ICON_LABELS`) and a swing needs plus/minus
  60 degrees, so this build is Word Blocks like the drill truck. Chris
  reads, Ian taps.
- Leo's brown wig (29066) has no LDraw file. 18228 stands in for it in the
  model (`0 !LDRCHECK PROXY 18228.dat 29066`); use the real brown wig at
  the table.
