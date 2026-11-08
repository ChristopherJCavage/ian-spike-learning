# Screens -- Chameleon Colour-Match

One row per Figma frame. Chrome: `context/instruction-screens.md`.

figma file: TBD

Four story slides come **before** step 1 and live in `story.md` on their
own numbering. Do not merge them into this table: row N here is rendered
with LeoCAD `-f N`, so a page inserted ahead of row 1 would render the
wrong bricks.

`camera` is either two LeoCAD angles (`lat lon`) or a `--viewpoint` name.
`highlight` is whether LeoCAD should outline the parts added on that page.

Rewritten for the build-tester pass: the hub flipped 180 degrees about Y,
so the wall with the two round cable ports is now the **rear** wall over
the tail (steps 19-22), and the short wall with the little USB shape is
the **front** wall over the brow (steps 6-18). The hub stays Bright
Yellow -- a draft of this pass called it White off a table photo, but
LEGO's own catalogue has no white variant of this element, so that is
reverted; see `parts.txt`. Every other part -- legs, brow, tail -- kept
the world coordinates it always had, so most cameras below are unchanged
from the first cut. Only the deck/matrix subassembly actually moved in
space (tail -> shoulders), and the tongue is gone, replaced by two pegs
and two round eye tiles.

Steps 3-5 all sit at `70 180`. That is the one angle where both hips,
then all four cups, then all four feet are visible at once, and holding
the camera still across a sub-assembly means the child is comparing four
pictures of the same thing rather than re-finding the model each page.
Step 2 (hip pins) gets its own low, close-in angle (`10 235`) instead --
Ian could not tell the four pegs were on the *bottom* row of three from
the old overhead shot, so this one looks along the row from near table
height, where "bottom" is unambiguous.

The sensor aims **down** from the head at a pad (`FACES 37308.dat +Y`).
The matrix LEDs aim **up** (`FACES 47592.dat -Y`). Check views
`renders/check-left.png`, `renders/check-front.png`, `renders/check-top.png`,
and `renders/check-iso.png` confirm: four splayed ball-joint feet, the
lens visible from below, nine lights visible from above, both ports used
from the back wall, and a tail that steps up and tapers with no ball
joint in it.

`highlight` is `no` almost everywhere on purpose. The render ghosts every
part already built (`--fade-steps-color #60FFFFFF`), so the new piece is
the only saturated thing on the page and keeps its **real** colour --
which is also the colour the child has to find in the bin. Turning it on
recolours the new part bright yellow (`#FFFF00FF`) instead, which would
send a six-year-old looking for a yellow piece that does not exist -- so
it is reserved for the two pages where the new part is itself white and
would otherwise blend into the pale ghost or the white page: the sensor
(12) and the eye tiles (14). The hub (1) is Bright Yellow, which already
reads fine against a white page, so it does not need the exception.

```
step | figma_frame | png | parts_added | camera | highlight | copy
1  | Chameleon/01-hub          | renders/step-001.png | 1x Small Hub | 55 225 | no | "Stand the yellow hub on the table, the little USB shape facing you."
2  | Chameleon/02-hip-pins     | renders/step-002.png | 4x peg | 10 235 | no | "Four pegs go into the BOTTOM row only -- two per side."
3  | Chameleon/03-hips         | renders/step-003.png | 2x 1x4 Technic brick | 70 180 | no | "Press a purple 1x4 onto each pair, studs pointing down."
4  | Chameleon/04-sockets      | renders/step-004.png | 4x ball-cup plate | 70 180 | no | "Press a grey cup onto each end of each hip, cups facing out."
5  | Chameleon/05-feet         | renders/step-005.png | 4x ball-plate | 70 180 | no | "Pop a ball-plate into each cup and splay the feet."
6  | Chameleon/06-front-pins   | renders/step-006.png | 2x peg | 35 180 | no | "Push two pegs into the short wall with the little USB shape."
7  | Chameleon/07-brow-bricks  | renders/step-007.png | 2x 1x2 brick | 55 225 | no | "Two separate orange bricks on the pegs. They can still twist -- that is fine."
8  | Chameleon/08-brow-plate   | renders/step-008.png | 1x 2x8 plate | 55 225 | no | "The green plate presses across both bricks at once. Now nothing twists."
9  | Chameleon/09-cheeks       | renders/step-009.png | 2x round slide shoe | 5 180 | no | "Press a purple bump into each open tube under the middle of the plate. Cheeks, not eyes."
10 | Chameleon/10-horns        | renders/step-010.png | 4x 1x1 cone | 35 180 | no | "Two purple horns stand down each outside edge of the brow."
11 | Chameleon/11-tbeams       | renders/step-011.png | 2x T-beam | 35 180 | no | "Press two red T-beams onto the brow, holes facing you."
12 | Chameleon/12-snout-pins   | renders/step-012.png | 2x peg | 35 180 | no | "Push a peg into each T-beam so they point forward."
13 | Chameleon/13-sensor       | renders/step-013.png | 1x Colour Sensor | 35 180 | yes | "Press the sensor on, lens pointing down. No cable yet."
14 | Chameleon/14-eye-pins     | renders/step-014.png | 2x peg | 15 210 | no | "Two short pegs into the sensor's face, pointing straight at you."
15 | Chameleon/15-eyes         | renders/step-015.png | 2x round tile | 15 210 | yes | "Press a white eye onto the tip of each peg."
16 | Chameleon/16-top-pins     | renders/step-016.png | 2x peg | 70 180 | no | "Stand two pegs up on top of the hub, near the brow end."
17 | Chameleon/17-deck         | renders/step-017.png | 1x 7M beam | 70 180 | no | "Lower the blue beam onto those two pegs."
18 | Chameleon/18-matrix-pins  | renders/step-018.png | 2x peg | 70 180 | no | "Stand two more pegs up, closer together, in the middle of the beam."
19 | Chameleon/19-matrix       | renders/step-019.png | 1x 3x3 light matrix | 70 180 | no | "Press the lights on, facing up. No cable yet."
20 | Chameleon/20-rear-pins    | renders/step-020.png | 2x peg | 45 0 | no | "Push two pegs into the wall with the two round ports, one on each side."
21 | Chameleon/21-tail-bar     | renders/step-021.png | 1x 1x8 Technic brick | 55 45 | no | "One long blue brick across both pegs at once."
22 | Chameleon/22-tail-plate   | renders/step-022.png | 1x 2x8 plate, 2x round tile | 55 45 | no | "Press an orange circle onto each end of the green plate first, then press the plate onto the bar."
23 | Chameleon/23-tail-corners | renders/step-023.png | 2x flat tile | 55 45 | no | "Cap the plate's two far corners with the flat orange tiles."
24 | Chameleon/24-tail-base    | renders/step-024.png | 1x 2x4 brick w. cross hole | 55 45 | no | "Turn the dark green 2x4 brick the long way and press it onto the shelf."
25 | Chameleon/25-curl         | renders/step-025.png | 3x 2x4 plate, 1x 2x2 slope | 35 250 | no | "Three orange plates turn the tail sideways, each on the last four studs of the one before. Purple slope on the end."
26 | Chameleon/26-try          | TBD (no render -- try it) | (none) | - | no | "Plug both cables into the back wall. Pose the legs. Slide a coloured pad under its head."
27 | Chameleon/27-code         | TBD (no render -- coding page) | (none) | - | no | "Read the pad. Light the back to match -- red means warning!"
```
