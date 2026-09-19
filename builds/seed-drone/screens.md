# Screens -- Seed Drone

One row per Figma frame. Chrome: `context/instruction-screens.md`.

figma file: TBD

The 34 build rows map one-for-one to `model.ldr`. Rows 35 and 36 are the
hands-on mission and Icon Blocks pages, so they have no LeoCAD PNG.

Previous pieces are faded by `tools/pages.py`; `highlight` stays off except
for the two white electronics, which otherwise disappear into the page.

Cameras follow the subassembly. The tail bay is built looking at the back
of the drone (`lon 0`), the grips and skids from the front quarter
(`lon 225`), and the face and rotor from straight ahead (`lon 180`).

The two eye pages drop to `lat 15`, nearly level with the table. The eyes
stick forward out of the sensor's front face, so a steep view foreshortens
them into two dots on top of a black box; from low down they read as a
face.

```
step | figma_frame | png | parts_added | camera | highlight | copy
1  | SeedDrone/01-hub           | renders/step-001.png | 1x yellow Small Hub | 55 225 | no  | "USB shape toward you; two round ports away."
2  | SeedDrone/02-skid-pins     | renders/step-002.png | 4x black peg | 10 225 | no  | "Four matching corner holes underneath -- skip the one-sided middle hole."
3  | SeedDrone/03-skid-plates   | renders/step-003.png | 2x green 2x8 plate | 15 225 | no  | "Two long green rails run nose-to-back under the Hub."
4  | SeedDrone/04-skid-shoes    | renders/step-004.png | 2x purple round shoe | 15 225 | no  | "Press one round shoe under the middle of each rail."
5  | SeedDrone/05-tail-pins     | renders/step-005.png | 2x black peg | 35 0 | no  | "Two rear pegs frame the round cable ports."
6  | SeedDrone/06-tail-spine    | renders/step-006.png | 1x blue 1x8 Technic brick | 35 0 | no  | "One long blue brick across the back: the spine the bay hangs from."
7  | SeedDrone/07-spine-pins    | renders/step-007.png | 2x black peg | 40 0 | no  | "Both end holes are full. Find the middle hole; fill the two beside it on one side."
8  | SeedDrone/08-tail-bracket  | renders/step-008.png | 1x green 3x5 right-angle beam | 40 0 | no  | "Green L on edge: long arm flat, short arm climbing, holes facing you."
9  | SeedDrone/09-bracket-pins  | renders/step-009.png | 2x black peg | 40 0 | no  | "Top and bottom hole of the climbing arm; skip the middle."
10 | SeedDrone/10-bay-motor     | renders/step-010.png | 1x Small Angular Motor | 40 0 | yes | "Stand the motor up. Turquoise output points straight back."
11 | SeedDrone/11-tray-axle     | renders/step-011.png | 1x red 6M axle | 40 0 | no  | "Push the long red axle straight back into the motor."
12 | SeedDrone/12-hinge         | renders/step-012.png | 1x yellow cross-hole brick | 40 0 | no  | "Slide the yellow brick onto the axle end, studs up. No turning needed."
13 | SeedDrone/13-tray-plate-1  | renders/step-013.png | 1x orange 2x4 plate | 45 0 | no  | "Turn the plate front-to-back and press it onto the hinge studs."
14 | SeedDrone/14-tray-walls    | renders/step-014.png | 2x purple 1x4 brick | 50 0 | no  | "A purple wall on each long edge. Two studs hang off -- that is for the next plate."
15 | SeedDrone/15-tray-square   | renders/step-015.png | 1x orange 2x4 plate | 45 0 | no  | "Second plate clicks onto the hanging studs and makes a square."
16 | SeedDrone/16-end-stop      | renders/step-016.png | 1x orange 1x2 brick | 50 0 | no  | "The orange brick fills the left end. Three sides now; right end open."
17 | SeedDrone/17-seed          | renders/step-017.png | 1x red ball | 50 0 | no  | "Press the seed down between the walls. It grips -- that is right."
18 | SeedDrone/18-grip-pins     | renders/step-018.png | 4x black peg | 30 225 | no  | "Middle row of each side wall: front and back holes, middle empty."
19 | SeedDrone/19-grips         | renders/step-019.png | 2x purple 1x4 Technic brick | 30 225 | no  | "One short bar per side. Pinch both and the drone lifts level."
20 | SeedDrone/20-nose-pins     | renders/step-020.png | 2x black peg | 25 180 | no  | "Two pegs into the short wall with the USB shape."
21 | SeedDrone/21-nose-bricks   | renders/step-021.png | 2x orange 1x2 brick | 35 180 | no  | "One orange brick on each nose peg. They can still swivel -- that is fine."
22 | SeedDrone/22-face          | renders/step-022.png | 1x green 2x8 plate | 35 180 | no  | "One green shelf across both bricks. This is the face."
23 | SeedDrone/23-brackets      | renders/step-023.png | 2x red T-beam | 35 180 | no  | "Two red T-beams inside the centre; leave both outer corners bare."
24 | SeedDrone/24-sensor-pins   | renders/step-024.png | 2x black peg | 25 180 | no  | "Push both pegs forward through the red holes."
25 | SeedDrone/25-sensor        | renders/step-025.png | 1x Colour Sensor | 25 180 | yes | "Press on the white sensor with its dark lens pointing down."
26 | SeedDrone/26-eye-pins      | renders/step-026.png | 2x black peg | 15 180 | no  | "Two pegs into the FRONT face of the sensor. The back holes are already used."
27 | SeedDrone/27-eyes          | renders/step-027.png | 2x white 1x1 round printed eye tile | 15 180 | no  | "One little eye pressed onto each peg tip. Blank in the picture, an eye on the real tile."
28 | SeedDrone/28-rotor-pins    | renders/step-028.png | 2x black peg | 65 180 | no  | "Stand two pegs in the top pair nearest the nose."
29 | SeedDrone/29-bearing       | renders/step-029.png | 1x blue 7M beam | 65 180 | no  | "Blue beam across the Hub; centre ROUND hole stays open."
30 | SeedDrone/30-spin-axle     | renders/step-030.png | 1x black 4M axle | 65 180 | no  | "Stand the black axle through the centre round hole. Round means it spins."
31 | SeedDrone/31-lock-hub      | renders/step-031.png | 1x dark-green cross-hole brick | 65 180 | no  | "Lock the brick onto the axle. A cross hole grips."
32 | SeedDrone/32-rotor-plate   | renders/step-032.png | 1x green 2x8 plate | 65 180 | no  | "Press the green plate on top. Seven holes in a row."
33 | SeedDrone/33-fasteners     | renders/step-033.png | 2x yellow 3M axle, 2x black friction peg | 70 180 | no  | "Yellow beside the middle -- it locks. Black at the far ends -- it grips."
34 | SeedDrone/34-blades        | renders/step-034.png | 2x purple 11M beam | 70 180 | no  | "One long blade onto each axle-and-peg pair; flick gently to spin the rotor."
35 | SeedDrone/35-mission       | TBD (no render -- try it) | (none) | - | no | "Sensor A, motor B. One grip per hand, skim low over the red drop zone."
36 | SeedDrone/36-code          | TBD (no render -- coding page) | (none) | - | no | "See red, tip the tray, play the drop sound, then return it level."
```
