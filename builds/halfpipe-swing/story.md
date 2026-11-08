# Story -- Half-pipe Swing

Five slides that come **before step 1**, the way the SPIKE App opens a
project. Chrome and the rules for this track: `context/instruction-screens.md`.

These are **printed on paper**, not clicked through, so they carry no
Back/Next chrome. `preview.html` still pages through them for review, and
its print stylesheet lays the whole deck out one page per sheet.

figma file: TBD

These are not build steps and they are numbered on their own track.
`screens.md` row N renders model step N, so nothing may be inserted ahead
of row 1 -- see the note at the top of `tools/pages.py`.

The cast is our own animal crew, drawn from the same character sheet as
the chameleon deck -- Sully the sloth in his blue beanie, Tika the toucan
with her red notebook, Pip the tree frog with his backpack, and Coco the
capybara with her tool belt -- because Ian has met them there already.
They are not minifigures and not the LEGO Education characters, on
purpose. Sully is the skater; the minifigure Ian builds on steps 22-23
rides the real model, and the orange board Sully carries in the art is
the same color as the orange board in the box.

```
slide | figma_frame | art | who | copy | camera | overlay
1 | Halfpipe/S1-park     | renders/story-01.png | Tika, Pip, Coco, Sully | "Tika, Pip, Coco and Sully went to the skate park." | - | -
2 | Halfpipe/S2-lip      | renders/story-02.png | Sully | "Sully stood at the top of the half-pipe. It was a long way down." | - | -
3 | Halfpipe/S3-drop     | renders/story-03.png | Sully | "He dropped in. Down, down, down -- and up the other side!" | - | -
4 | Halfpipe/S4-again    | renders/story-04.png | Sully, Coco, Pip, Tika | "Up one side, up the other. Three times. Everyone cheered." | - | -
5 | Halfpipe/S5-build    | renders/story-05.png | Coco | "Build a half-pipe. A motor makes your skater drop in." | 20 205 | -
```

Slides 1-4 are drawn with an AI image tool and live in git at 1536x1024,
which is one of the two frame sizes in `context/instruction-screens.md`,
so they drop into a landscape tablet frame with no resampling. They were
generated at 16:9 and centre-cropped to 3:2; every figure is inside the
crop. Slide 4 is cropped a little wider than the rest, with a thin strip
of sky added at the top, so Coco's paw and Sully's arm both stay in.

Slide 5 has a `camera`, which means `pages.py render` draws it from
`model.ldr` like any step hero. It is the only slide that is not an
illustration, on purpose -- see below.

## Slide 1 -- the park

**Read aloud:** "Tika, Pip, Coco and Sully went to the skate park. Sully
brought his skateboard. He is slow at everything except skating."

**Why all four:** the opening slide is the same shape as the chameleon's
-- the four of them walking into somewhere new, seen from behind -- so
Ian knows where he is in the story before a word is read.

**Art:** wide establishing shot. The four walking across a sunny skate
park toward a big concrete half-pipe, Sully in front carrying the orange
board under his arm. Ramps, a rail, painted walls, palm trees, golden
late-afternoon light.

## Slide 2 -- the lip

**Read aloud:** "Sully stood right at the top of the half-pipe. It was a
long way down."

**Why Sully:** Ian is the skater in this house, and a sloth who is slow
at everything except skating is the joke a six-year-old skater gets.
Standing on the lip before dropping in is the moment every skater knows
-- that is why the build starts with the skater waiting at the bottom for
the button.

**Art:** low angle from the bottom of the ramp, Sully on the lip on the
orange board, brave little grin, the curve falling away below him.

## Slide 3 -- drop in

**Read aloud:** "He dropped in. Down, down, down -- and up the other
side!"

**Art:** looking down the half-pipe, both walls visible, Sully arms-out
through the bottom with a swoosh line behind him. This is the picture of
what the model does: the motor is the swoosh.

## Slide 4 -- three times

**Read aloud:** "Up one side, then up the other. Three times! Everyone
cheered."

**Why "three times":** it is the number in the `repeat` block on the code
page. Ian will hear it here first and then type it there.

**Art:** Sully at the lip, arm up; Coco jumping, Pip clapping and Tika
writing it all down in her notebook on the deck at the left.

## Slide 5 -- build it

**Read aloud:** "Coco said: let's build a half-pipe -- and give it a
motor, so our skater can ride it all by himself."

**Why Coco:** she is the builder, the one with the tool belt, and she
hands the story over to the bricks, as she does in the chameleon deck.

**Art:** none drawn. `renders/story-05.png` is a LeoCAD shot of the
finished model at camera `20 205`: low and a little to the side, looking
into the U so the two black rails read as one curve with the minifigure
and its orange board in the middle, the front gear sitting in the teeth below
him, the light matrix in the foreground, the white motor behind him and
the yellow hub behind that. The step heroes use higher angles to show where a piece
goes; this one has to look like a half-pipe.

The LeoCAD PNG is transparent and drawn for a white page, so on the
slide's dark background it needs a white plate behind it or the black
rails disappear. `preview.html` does this automatically for any slide
with a camera; Figma has to do the same.
