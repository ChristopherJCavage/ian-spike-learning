# Build: rainforest-chameleon

category: creature
venue: class
hub: essential
kits: 45345
skills: colour-sensor, light-matrix, ball-joints, events
coding: icon
age-fit: 6
figma: TBD
project: rainforest-chameleon
role: main

Published at https://stem.galaxymoose.com/builds/rainforest-chameleon
CC BY 4.0. Credit Chris Cavage, stem.galaxymoose.com.

Chameleon Colour-Match. The club's first Essential-only rainforest
lesson: the animal reads a coloured pad under its head and lights the
3x3 matrix on its back to match -- with a bright-red branch for the
warning-colour idea. Two ports in, two ports used (colour sensor on A,
matrix on B). No motor. Ball-joint legs, white round eyes on pegs in
front of the sensor, purple cheek bumps and brow horns, a Dark Azur bar
under the tail shelf, and a tail that turns a corner, steps out past the
feet on three orange plates, and tapers to a purple point.

Build-tester pass: the hub (Bright Yellow -- a draft briefly called it
White off a table photo, reverted once LEGO's own catalogue confirmed
this element has no white variant) is flipped 180 degrees, so the two
cable ports are on the tail wall and the little USB shape is on the brow
wall -- more finger room for the plugs, at 5-7 years old. The deck and
light matrix moved with it, from over the tail to over the shoulders.
The tongue (a flex hose) turned out not to mount on the sensor, so the
face is now two pegs and two white round tiles instead. See
`geometry.md` for the exact before/after coordinates.

All four ball-and-socket pairs go to the legs. The fifth pair ships in
the spare tray rather than the main bin, so the tail is built from plain
clutch instead -- see `geometry.md`.

Class-safe: every part is from `kits/45345-essential/parts.txt`. See
`brief.md` for the spec, `steps.md` for the build, `code.md` for the
program.

Five story slides come ahead of step 1, the way the SPIKE App opens a
project: our animal crew hikes into a rainforest, Sully the sloth runs
out of claws counting colors, Sully holds still long enough to spot a
chameleon, Sully learns what it is and gets a tongue in the face, and
Coco the capybara says build one. `story.md` has the slides and why each character is on the one
they are on. They print, so they carry no Back/Next.

Click through the pages before Figma:

```
python3 tools/pages.py preview builds/rainforest-chameleon
open builds/rainforest-chameleon/preview.html
python3 tools/pages.py pdf builds/rainforest-chameleon
open builds/rainforest-chameleon/preview.pdf
```

Icon Blocks picture (shape-checked):

```
python3 tools/blocks.py preview builds/rainforest-chameleon
open builds/rainforest-chameleon/program.html
```
