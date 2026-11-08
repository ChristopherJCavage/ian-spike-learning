# Pre-flight -- Half-pipe Swing

`ldrcheck` is a linter, not a physics engine. LeoCAD snaps to a grid, not
to clutch. Run this after the checker is green and before you sit down
with Ian.

## Machine (must be green)

```
python3 tools/ldrcheck.py check builds/halfpipe-swing/model.ldr
python3 tools/ldrcheck.py steps builds/halfpipe-swing/model.ldr
python3 tools/ldrcheck.py fixtures
python3 tools/swing.py builds/halfpipe-swing --steps 15-28 --roll 46372 -5 --angles -60 -37 -30 -11 0 11 30 37 60
python3 tools/pages.py check builds/halfpipe-swing
python3 tools/blocks.py check builds/halfpipe-swing
```

The model header declares the world:

    0 !LDRCHECK GROUND 242
    0 !LDRCHECK FRONT +Z
    0 !LDRCHECK FACES 41879.dat +Z
    0 !LDRCHECK FACES 47592.dat +Z
    0 !LDRCHECK CLEARANCE 24121.dat 30
    0 !LDRCHECK CLEARANCE 37312.dat 12
    0 !LDRCHECK CLEARANCE 47592.dat 20
    0 !LDRCHECK JOINS 45601.dat 54675.dat
    0 !LDRCHECK JOINS 64289.dat 54675.dat
    0 !LDRCHECK JOINS 32316.dat 54675.dat
    0 !LDRCHECK JOINS 32524.dat 32316.dat
    0 !LDRCHECK JOINS 60484.dat 32524.dat
    0 !LDRCHECK JOINS 3701.dat 60484.dat
    0 !LDRCHECK JOINS 37312.dat 3701.dat
    0 !LDRCHECK JOINS 24121.dat 3707.dat
    0 !LDRCHECK JOINS 47592.dat 3709.dat
    0 !LDRCHECK RESTS 18746.dat ON 3701.dat
    0 !LDRCHECK PROXY 18228.dat 29066
    0 !LDRCHECK MESH 46372.dat 24121.dat 140

`ldrcheck` checks the model at one pose. `swing.py` is the only thing
that checks the rider at the angles the program actually drives it to,
with the gears turned the way they roll; re-run it after any change to
steps 15-32.

## Human (the checker will not see these)

- **Three boxes on the table.** Essential (baseplates, green and purple
  bricks, Leo, the board, the orange plate, the light matrix), Prime
  (hub, motor, sensor, beams, pegs, the two grey gears, the yellow and
  black axles), Expansion (the four curved racks, the red axles, the
  yellow half bushes). Every step names its bin. The light matrix is the
  one electronic part from the Essential box: it works on the Prime hub.
- **The motor's zero.** The program's "go to 0" means the motor's own
  zero mark, not "wherever Leo was when you pressed run". Before the
  first run, check the alignment marks on the disc and the motor body
  line up when the arm hangs straight down: the motor knows its angle
  from those marks, not from the arm. Step 15 lines them up before the
  blue pegs go in. If the arm went on a quarter-turn off (pegs in the
  side holes of the disc, then the disc turned), every swing will be
  lopsided; re-seat the arm rather than changing the angles in the
  program. The quick test is the end of the program: Leo must land
  hanging straight down.
- **Speed.** The program runs the swing at 50% speed. Faster looks more
  like skating, but the arm is a long lever with a minifigure on the end;
  at full speed Leo's hair is the first thing to fly off. Go up in steps
  of 10 if Ian wants more.
- **Cables.** Motor into **A**, force sensor into **B**, light matrix
  into **C** -- the letters are printed next to each port on the hub.
  Tuck the motor's cable down behind the posts, away from the front: the
  rider swings in front of the posts, and a loop of cable hanging
  forward is the one thing that can catch it. The light matrix's cable
  is the long one: run it along the baseplate, outside the end of a
  rail, round to the hub -- never across the front of the ramp or under
  the gears. Page 36 (try it by hand) is where you check.
- **The gears roll; the motor drives.** The motor turns the arm. The two
  gears are on a free axle and just roll along the rails' teeth as the
  arm carries them -- they do not drive anything, so a gear that jumps a
  tooth costs nothing but a click. If one clicks, check its half bushes:
  the front gear must be pressed back against the two spacers. If the
  swing feels stiff by hand on page 36, the rails are not square -- push
  the lip axles further through.
- **Hanging the racks around a gear (steps 30 and 32).** Each rail goes
  on in the same plane as a gear that is already there, so each quarter
  is hung with Leo swung over to the other side, out of its way. Turn
  him by hand slowly -- the motor turns stiffly -- and let the gear roll
  onto the teeth; do not force a quarter on over a gear.
- **Pressing the button.** The sensor is at the back on Ian's left (seen
  from the front, where Leo faces him), button up, behind the left lip.
  Reach over the left side of the ramp, not
  through it. A hard press flexes the green brick a little; that is
  fine, the sensor's foot is clear of the baseplate (`CLEARANCE`).
- **The lap joint at the bottom of each rail.** Each curved rack has thin
  end tabs; two of them overlap at the bottom into one full-thickness
  lug, which is why one of each pair is turned over (steps 30 and 32).
  If Ian puts both the same way round, the tabs will not overlap -- they
  will collide, and the black axle will not go through. That is the cue
  to flip the left-hand one (the second one hung).
- **The light stand overhangs on purpose.** The orange plate clutches
  only the big plate's last row of studs; its front row, the purple
  tower and the light matrix stand out over the table. On the last row
  itself the tower would sit flush against the front rail. Press the
  plate down firmly; nothing pushes on it once built.
- **Front rail alignment.** The front rail only hangs on the three axles
  (bottom and both lips). If it looks twisted, push the lip axles
  further through from the back.
- **Leo's board.** The board sits on the purple brick's four studs by its
  three underside tubes -- in LDraw it is asserted with `RESTS`, not
  proven as a clutch. Press it down firmly, all three tubes between the
  studs. If it pops off on the swing, slow the motor before anything
  else.
- **Hair.** `model.ldr` draws the wig as `18228` (PROXY) because the
  real one (`29066`, MINI WIG NO. 63) has no LDraw file. In the box it
  is the Reddish Brown hair piece in the minifigure bag.
- **Leo's face.** The BOM lists head 96004 (`MINI HEAD NO. '752'`), but
  any of the four printed heads fits. Let Ian choose.

## Why the build order is what it is

- **Motor before posts.** A post's foot ends 1 LDU above the baseplate's
  studs, so a post on its brick peg alone is a hinge resting on studs it
  does not clutch. Hanging the posts on the motor first, then lowering
  the whole thing onto the brick, means the posts are never loose.
- **The back brick is under the hub, not behind its legs.** That way the
  brick's pegs point the same way as the hub's, and each leg goes on in
  one push (step 11).
- **Racks and the black axle are one page.** Until the axle is in, the
  two halves of the back rail only rest against each other.
- **Gears before rails.** The gears go on while nothing is in the way
  (steps 26-28); the rails are then hung around them. The other way
  round, the back gear would have to be threaded in behind the arm
  through the back rail.

## Before exempting a part

```
python3 tools/ldrcheck.py holes <part>
```

If it emits studs or tubes, it does not need `role: decorative`. This
build taught the checker five things, each with fixtures:

- **Short legs face front.** `41879` is `role: decorative`, `facing: -Z`
  in `connections.yml` (`good-short-legs-face-front.ldr`,
  `bad-short-legs-backward.ldr`).
- **A proxy keeps its real part's colours.** `PROXY` now lets COLOUR vs
  KIT accept the real part's colours on the stand-in, but only if the
  stand-in is itself in a kit (`good-proxy-wig-colour.ldr`,
  `bad-wig-colour-unproxied.ldr`).
- **Half-thick lugs.** The quarter rack's end tabs are drawn as one-LDU
  axle-hole primitives scaled to 10 deep; the bore probe used to read
  them as 20. Now a scaled bore between half a module and a module is
  taken at its drawn depth (`good-rack-lap-joint.ldr`,
  `bad-rack-lap-same-face.ldr`). See `context/ldraw-connections.md`.
- **Gear mesh.** `0 !LDRCHECK MESH <gear> <partner> <centre distance>`
  asserts every gear sits that far from a partner, in its plane; excuses
  the teeth touching with no joint; and allows them zero shared solid,
  so a wrong tooth phase fails (`good-gear-mesh-rack.ldr`,
  `bad-gear-mesh-undeclared.ldr`, `bad-gear-short-of-rack.ldr`,
  `bad-gear-tooth-on-tooth.ldr`). `46372` is `rotates: true`.
- **Half bushes are 10 thick about their origin.** Their bore annotation
  started at the origin instead of the -5 face, so a bush next to a gear
  on one axle reported PIN SLICE CONFLICT.
