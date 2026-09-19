# LeoCAD PNGs

Instruction stills `step-001.png` … `step-024.png` (LeoCAD CLI, camera
and highlight per `screens.md`, previous steps faded). Step 25 (try it)
and step 26 (program) have no render -- no new bricks. Check views of
the finished chameleon:

- `check-left.png` -- side profile (head to the right), best view of the
  tail stepping up and tapering
- `check-front.png` -- looking at the sensor / eyes
- `check-top.png` -- plan view, nine matrix lights
- `check-iso.png` -- default instruction camera 55 225

`story-01.png` … `story-04.png` are the illustrated story slides and are
**not** from LeoCAD -- they are drawn scenery, 1536x1024, no words baked
in. See `../story.md`.

`story-peek.png` is cut from `story-04.png`: the chameleon's head and
tongue in a round white-ringed sticker, laid on the corner of slide 5.
`../story.md` has the crop numbers for redoing it.

`story-05.png` is the odd one out: it *is* LeoCAD, the finished model at
camera `25 245`, written by `pages.py render` from the `camera` column in
`story.md`. Low and side-on so the thing reads as an animal rather than a
pile of bricks, and regenerated with everything else so the "here is what
you are building" page cannot drift from the model.

The PNGs are RGBA with a transparent background. Step renders ghost the
history (`--fade-steps-color #60FFFFFF`) and leave the new part in its
real colour, then get trimmed to their content and padded to 2000x1500 so
the subject fills the page -- LeoCAD frames every step against the whole
model, which left early steps at about a tenth of the canvas. The recipe
and the reasoning are in `context/instruction-screens.md`.
