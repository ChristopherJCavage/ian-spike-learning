# Build: mining-drill-truck

category: vehicle
venue: home
hub: prime
kits: 45345, 45678
skills: motors, distance-sensor, light-matrix, axles
coding: word
age-fit: 6
figma: TBD

"Digger" the Mining Drill Truck. 4 wheels, two Large Motors in a skid-steer
rear drive (each spins its own rear wheel directly off its output disc --
no shared rear axle), a Small Angular Motor spinning a front drill bit, a
Distance Sensor that wakes the drill up when something gets close, a
minifig driver, and a cute face (hood "eyes" + hub light-matrix expressions
+ a riding dog sidekick).

Needs the **Prime hub** — this build uses 4 ports (3 motors + 1 sensor) and
Essential only has 2. See `brief.md` for the full spec, `steps.md` for the
build, `code.md` for the program.

Click through the pages before Figma:

```
python3 tools/pages.py preview builds/mining-drill-truck
open builds/mining-drill-truck/preview.html
```

Word Blocks picture (shape-checked):

```
python3 tools/blocks.py preview builds/mining-drill-truck
open builds/mining-drill-truck/program.html
```
