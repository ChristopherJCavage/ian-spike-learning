# Build: halfpipe-swing

category: machine
venue: home
hub: prime
kits: 45345, 45678, 45681
skills: motor-position, force-sensor, 5x5-display, color-matrix, gears, sound, loops
coding: word
age-fit: 6
figma: TBD
project: halfpipe-swing
role: main

Half-pipe Swing. Leo stands on an orange board at the end of a swinging
arm, inside a half-pipe made of four quarter-circle gear racks from the
Expansion box. Press the force sensor and the Large Motor swings him up
to each lip three times -- an arrow on the 5x5 shows which way he is
going, and the 3x3 light matrix on the front flashes orange at every lip
-- then sets him down in the middle with green lights, a smile and a
sound.

Under the board, two grey Z28 gears on one free axle ride in the racks'
teeth, one per rail, and roll along them as he swings. The motor axle is
the pivot and the ramp is centred on it, so the gears are meshed at
every angle (140 LDU out: the 140-tooth ring's pitch radius minus the
gear's) and everything else keeps at least 24 LDU (1 cm) from the teeth.
`tools/swing.py --roll 46372 -5` checks both at nine angles with the
gears turned the way they roll. The Prime hub lies flat on the motor's
back with its lights facing up, held at the far end by two legs. The
force sensor stands button-up at the back corner on Ian's left (left and
right as seen from the front, where Leo faces him).

Home build, three boxes: Essential (Leo, boards, baseplates, bricks, the
light matrix), Prime (hub, motor, sensor, beams, pins, gears), Expansion
(the four quarter racks, half bushes). See `brief.md` for the spec, `steps.md` for the build,
`code.md` for the program, `geometry.md` for the measured numbers.

Five story slides come ahead of step 1: our animal crew at a skate
park, Sully the sloth on the lip of a real half-pipe, Sully dropping in,
the others cheering, and "build one" over the finished model. `story.md` has the
slides.

Click through the pages before Figma:

```
python3 tools/pages.py preview builds/halfpipe-swing
open builds/halfpipe-swing/preview.html
python3 tools/pages.py pdf builds/halfpipe-swing
open builds/halfpipe-swing/preview.pdf
```

Word Blocks picture (shape-checked):

```
python3 tools/blocks.py preview builds/halfpipe-swing
open builds/halfpipe-swing/program.html
```
