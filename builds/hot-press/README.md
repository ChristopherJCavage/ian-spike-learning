# Build: hot-press

category: machine
venue: class
hub: essential
kits: 45345
skills: motor, slider-crank, axles, icon-blocks
coding: icon
age-fit: 6
figma: TBD
project: super-wood
role: main

Published at https://stem.galaxymoose.com/builds/hot-press
CC BY 4.0. Credit Chris Cavage, stem.galaxymoose.com.

The Hot Press is the press step from the club's wood poster. The motor
sits high on a red tower with big eyes and a red and a green light on
top. One peg in its hub pulls a blue beam, and the beam pushes a green
plate down two black axles. The red head under the plate comes down onto
two light orange plates, the old wood, and lifts again. One thinner
plate in front is the super wood. A frog and a bush watch. Nothing is
heated and nothing is soaked.

The crank is a peg in the motor's own hub, 20 LDU from its middle. The
press moves 16 mm and stops 1.6 mm over the wood, so the motor never
stalls on it. In the program, half a turn brings the press down, a sound
is the squeeze, and half a turn more lifts it.

Only parts from `kits/45345-essential/parts.txt` are in the model. The
Hub and the 3x3 matrix are used and are not bricks in `model.ldr`. See
`brief.md`, `mechanism.md`, `steps.md`, and `preflight.md`.

```
python3 tools/ldrcheck.py check builds/hot-press/model.ldr
python3 tools/ldrcheck.py steps builds/hot-press/model.ldr
python3 tools/pages.py check builds/hot-press
python3 tools/pages.py preview builds/hot-press
python3 tools/pages.py pdf builds/hot-press
python3 tools/blocks.py check builds/hot-press
python3 tools/blocks.py preview builds/hot-press
```
