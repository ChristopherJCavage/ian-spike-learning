# Build: seed-drone

category: machine
venue: class
hub: essential
kits: 45345
skills: colour-sensor, motor, events, axles, free-spin, right-angle beams
coding: icon
age-fit: 6
figma: TBD
project: rainforest-seed-mission
role: main

Published at https://stem.galaxymoose.com/builds/seed-drone
Project page: https://stem.galaxymoose.com/projects/rainforest-seed-mission
CC BY 4.0. Credit Chris Cavage, stem.galaxymoose.com.

The Seed Drone is a handheld rainforest-survey machine for the club's
careers-and-technology lesson. A child holds the yellow Hub in both hands
and skims the two landing shoes over the red band in
`builds/rainforest-drop-zone`. The downward Colour Sensor sees red, and one
Small Angular Motor tips a tray so a loose red D16.5 ball drops as a seed.

This is a model of a drone, not a flying aircraft. Its broad two-blade
rotor turns freely when a child flicks it. It is deliberately not powered:
the Essential Hub has two ports, and the sensor and seed-bay motor use both.
That constraint supports the lesson -- engineers choose which functions
need automation and which can stay passive.

The seed bay hangs off the tail on the centreline, carried by the kit's one
right-angle beam -- the only part that turns the rear spine's horizontal
row of holes into the vertical pair the motor needs. The nose carries a
face: the Colour Sensor housing is the head, and two black pegs pushed into
its forward face each hold one of the kit's small printed eye tiles, which
is the same trick `rainforest-chameleon` uses. Those eyes will not appear in
any render here, because LDraw has no way to draw a printed decoration.

Only parts from `kits/45345-essential/parts.txt` are used. The finished
model has 58 parts over 34 build steps, followed by a mission page and an
Icon Blocks page. See `brief.md` for the requirements, `mechanism.md` for
the geometry, `steps.md` for kid-facing instructions, and `preflight.md`
for the table checks that CAD cannot prove.

Five story slides come ahead of step 1, the way the SPIKE App opens a
project: our animal crew finds a bare patch where a tree was cut down,
Tika the toucan drops a seed, Sully the sloth runs out of claws counting
how many more it needs, Pip the tree frog spots a real drone dropping
seeds, and Coco the capybara says build one. `story.md` has the slides
and why each character is on the one they are on. They print, so they
carry no Back/Next.

The program is [`program.spike`](program.spike):

- Colour Sensor on port A
- seed-bay motor on port B
- red target -> tip one quarter-turn -> sound cue -> return level

Validate and preview everything:

```
python3 tools/ldrcheck.py check builds/seed-drone/model.ldr
python3 tools/ldrcheck.py steps builds/seed-drone/model.ldr
python3 tools/pages.py check builds/seed-drone
python3 tools/pages.py preview builds/seed-drone
python3 tools/pages.py pdf builds/seed-drone
python3 tools/blocks.py check builds/seed-drone
python3 tools/blocks.py preview builds/seed-drone
```

Open `preview.html` for the 41-page lesson (`preview.pdf` is the same
pages for printing) and `program.html` for the shape-checked Icon Blocks
picture.
