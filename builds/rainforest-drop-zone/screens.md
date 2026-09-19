# Screens -- Rainforest Drop Zone

One row per Figma frame. Chrome: `context/instruction-screens.md`.

figma file: TBD

The 9 build rows map one-for-one to `model.ldr`. Row 10 is the mission page,
which has no LeoCAD PNG because it is about flying the drone, not building
the island.

Nine pages is the whole point of this build. It is the short one, meant to be
finished inside a 60-minute class while another child builds the drone, so
there is no page here that adds only one small decoration.

Previous pieces are faded by `tools/pages.py`. `highlight` is off
throughout: nothing on this island is white-on-white the way the Hub and
sensor are on the drone, so the fade alone is enough contrast.

Cameras. Longitude stays at 30 for the whole build so the island never spins
under the builder -- the one thing worse than a bad angle is a changing one.
At 30 the lane runs diagonally across the frame, which is what shows both
walls at once; straight down the lane (`lon 0`) hides one wall behind the
other.

Step 2 is the steepest page at `lat 70`, nearly straight down. It is the only
page where the reader has to judge that two tiles butt into one solid square
with no white between them, and any tilt at all hides the seam. Step 3 stays
steep for the same reason -- it has to show the red reaching both walls, and
the bare white row left outside each one.

```
step | figma_frame | png | parts_added | camera | highlight | copy
1  | DropZone/01-island     | renders/step-001.png | 1x white 8x16 plate | 60 30 | no | "The long white plate, narrow across and long away from you."
2  | DropZone/02-drop-zone  | renders/step-002.png | 2x red 2x4 tile | 70 30 | no | "Two red tiles side by side in the middle. One solid square, no gaps."
3  | DropZone/03-walls      | renders/step-003.png | 2x green 1x16 Technic brick | 60 30 | no | "A green wall each side of the red, one white row outside each. Red touches both."
4  | DropZone/04-trees      | renders/step-004.png | 2x dark green 2x2 round brick, 2x dark green bush | 20 30 | no | "One brick and one bush at each end of the lane, both on the middle."
5  | DropZone/05-ranger     | renders/step-005.png | 1x orange legs, 1x green torso | 20 30 | no | "Stand her in the lane past the red, facing you."
6  | DropZone/06-head       | renders/step-006.png | 1x printed head, 1x wig | 20 30 | no | "Head onto the neck peg, then the hair."
7  | DropZone/07-controller | renders/step-007.png | 1x black camera | 20 30 | no | "Clip the black block into both hands, held up in front."
8  | DropZone/08-frog       | renders/step-008.png | 1x dark green frog | 30 30 | no | "The frog goes on the white behind the red, off to one side."
9  | DropZone/09-grass      | renders/step-009.png | 2x green grass stem | 25 30 | no | "One tuft on the bare row outside each wall. Neither in the lane."
10 | DropZone/10-mission    | TBD (no render -- fly it) | (none) | - | no | "Load a red ball, fly in over one tree and straight down the lane."
```
