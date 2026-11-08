# Screens -- Half-pipe Swing

One row per Figma frame. Chrome: `context/instruction-screens.md`.

figma file: TBD

Five story slides come **before** step 1 and live in `story.md` on their
own numbering. Do not merge them into this table: row N here is rendered
with LeoCAD `-f N`, so a page inserted ahead of row 1 would render the
wrong bricks.

`camera` is either two LeoCAD angles (`lat lon`) or a `--viewpoint` name.
`highlight` is whether LeoCAD should outline the parts added on that page.
Longitude 180 looks at the FRONT (+Z, where Ian sits, Leo's face, the
motor's disc); 0 looks at the back, at the hub's legs and the button.

Cameras are held still across each sub-assembly so consecutive pages are
pictures of the same thing:

- **Frame, steps 1-7, from the front (`25 200`).** The pegs on step 4 go
  into the bottom two holes of each column of three on the motor's face;
  a low front angle is the only one where "bottom two" and "the disc"
  are both obvious.
- **Hub, steps 8-11, from behind (`35 20`).** Every peg on these pages
  points backward.
- **Button, steps 12-14, from behind, on the sensor's side (`40 330`).**
  The purple riser is on the front brick but its pegs and the sensor face
  the back, so this view sees the riser past the hub's leg. Because it is
  taken from behind, the sensor -- on Ian's **left** as he sits in front
  -- is on the right of the picture; `steps.md` says so on step 12.
- **Rider and gears, steps 15-28, close and low from the front
  (`15 190`).** Leo's face, the board and the T-beam all read from here,
  and so does the back gear: it is wider than the arm in front of it.
- **Ramp, steps 29-32, from the front and a little above (`30 205`).**
  High enough to see that the two rails are in front of and behind Leo,
  with a gear in each.
- **Lights, steps 33-35, from the front, low (`20 200`).** The light
  stand is the nearest thing to the camera.

`highlight` is `no` except the two white electronics. The render ghosts
every part already built, so a new part keeps its real colour, which is
the colour Ian has to find in the bin. Highlight recolours the new part
bright yellow, so it is reserved for the White Large Motor (3) and the
White Force Sensor (14), which would otherwise blend into the white
baseplates and the white page. The hub is Bright Yellow already.

```
step | figma_frame | png | parts_added | camera | highlight | copy
1  | Halfpipe/01-baseplates    | renders/step-001.png | 1x 16x16 plate, 1x 8x16 plate | 25 200 | no | "Two white plates, edges touching. The big one goes in front."
2  | Halfpipe/02-green-bricks  | renders/step-002.png | 2x 1x16 Technic brick | 25 200 | no | "One long green brick on each plate, holes facing you."
3  | Halfpipe/03-motor         | renders/step-003.png | 1x Large Motor | 25 200 | yes | "Hold the motor, round disc facing you, cable end down."
4  | Halfpipe/04-front-pegs    | renders/step-004.png | 6x peg | 25 200 | no | "Four pegs into the motor -- the bottom two holes each side. Two pegs into the green brick."
5  | Halfpipe/05-posts         | renders/step-005.png | 2x 9M beam | 25 200 | no | "A black beam on each side, then stand it all on the green brick's pegs."
6  | Halfpipe/06-cross-pegs    | renders/step-006.png | 4x peg | 25 200 | no | "Two pegs on each post: holes 6 and 8 from the top."
7  | Halfpipe/07-crossbeams    | renders/step-007.png | 2x 13M beam | 25 200 | no | "Two long blue beams, centred, one above the other."
8  | Halfpipe/08-hub-pegs      | renders/step-008.png | 4x peg | 35 20 | no | "Turn it around. Four pegs into the back of the motor."
9  | Halfpipe/09-hub           | renders/step-009.png | 1x Prime Hub | 35 20 | no | "The yellow hub lies flat, lights up, on those four pegs."
10 | Halfpipe/10-leg-pegs      | renders/step-010.png | 6x peg | 35 20 | no | "Four pegs in the far end of the hub, two in the back green brick. All point away."
11 | Halfpipe/11-legs          | renders/step-011.png | 2x 9M beam | 35 20 | no | "Two black legs, three pegs each. Push both on together."
12 | Halfpipe/12-riser         | renders/step-012.png | 1x 1x4 Technic brick | 40 330 | no | "A purple brick on the end of the front green brick -- your left end."
13 | Halfpipe/13-button-pegs   | renders/step-013.png | 2x peg | 40 330 | no | "Two pegs in the back of the purple brick."
14 | Halfpipe/14-sensor        | renders/step-014.png | 1x Force Sensor | 40 330 | yes | "The force sensor, button pointing at the ceiling."
15 | Halfpipe/15-disc-pegs     | renders/step-015.png | 2x 3M peg | 15 190 | no | "Line up the marks. Two long blue pegs in the disc: above the middle and below it."
16 | Halfpipe/16-offset        | renders/step-016.png | 1x 5M beam | 15 190 | no | "A purple beam hangs from the disc on holes 1 and 3."
17 | Halfpipe/17-arm-pegs      | renders/step-017.png | 2x 3M peg | 15 190 | no | "Two more long blue pegs in the purple beam's bottom two holes."
18 | Halfpipe/18-arm           | renders/step-018.png | 1x 7M beam | 15 190 | no | "The blue arm on those pegs, holes 2 and 3."
19 | Halfpipe/19-t-pegs        | renders/step-019.png | 2x peg | 15 190 | no | "Two pegs near the bottom of the arm. Leave the last hole empty."
20 | Halfpipe/20-t-beam        | renders/step-020.png | 1x T-beam | 15 190 | no | "An upside-down T on the end of the arm."
21 | Halfpipe/21-board-pegs    | renders/step-021.png | 2x peg | 15 190 | no | "A peg in each end of the T's crossbar. The middle stays empty."
22 | Halfpipe/22-board-brick   | renders/step-022.png | 1x 1x4 Technic brick | 15 190 | no | "A purple brick on both pegs, studs up."
23 | Halfpipe/23-board         | renders/step-023.png | 1x skateboard | 15 190 | no | "The orange board on top, long way across."
24 | Halfpipe/24-leo-body      | renders/step-024.png | 1x short legs, 1x torso | 15 190 | no | "Leo's green legs on the board, blue body on top. He faces you."
25 | Halfpipe/25-leo-head      | renders/step-025.png | 1x head, 1x wig | 15 190 | no | "Head, then hair. Leo is ready to drop in."
26 | Halfpipe/26-gear-axle     | renders/step-026.png | 1x Z28 gear, 1x 7M axle | 15 190 | no | "Hold a gear behind the arm. Push the yellow axle through from the front, under the board."
27 | Halfpipe/27-bushes        | renders/step-027.png | 3x half bush | 15 190 | no | "One yellow ring behind the gear, two in front of the purple brick."
28 | Halfpipe/28-front-gear    | renders/step-028.png | 1x Z28 gear, 1x half bush | 15 190 | no | "The second gear on the front, and one more ring to hold it."
29 | Halfpipe/29-rail-pegs     | renders/step-029.png | 2x 3M peg | 30 205 | no | "A long blue peg in each end of the UPPER blue beam."
30 | Halfpipe/30-back-rail     | renders/step-030.png | 2x curved rack, 1x 8M axle | 30 205 | no | "Leo over to the left, right curve on. Leo over to the right, left curve on. Black axle through the tabs."
31 | Halfpipe/31-lips          | renders/step-031.png | 2x 6M axle | 30 205 | no | "A red axle through each lip, sticking out toward you."
32 | Halfpipe/32-front-rail    | renders/step-032.png | 2x curved rack | 30 205 | no | "The same two curves on the front. A gear rides in each rail."
33 | Halfpipe/33-light-stand   | renders/step-033.png | 1x 2x4 plate, 2x 1x4 Technic brick | 20 200 | no | "An orange plate over the front edge, two purple bricks on its front row."
34 | Halfpipe/34-light-pegs    | renders/step-034.png | 2x peg | 20 200 | no | "Two pegs in the top purple brick."
35 | Halfpipe/35-light-matrix  | renders/step-035.png | 1x 3x3 Color Light Matrix | 20 200 | no | "The light matrix on the pegs, lights facing you."
36 | Halfpipe/36-try           | TBD (no render -- try it) | (none) | - | no | "Motor into A, button into B, lights into C. Push Leo up one side and down the other, slowly. Watch the gears roll."
37 | Halfpipe/37-code          | TBD (no render -- coding page) | (none) | - | no | "Press the button. Leo drops in, swings three times with a flash at every lip, and lands with green lights and a smile."
```
