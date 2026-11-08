# Story -- Hot Press

Five slides that come **before step 1**, the way the SPIKE App opens a
project. Chrome and the rules for this track: `context/instruction-screens.md`.

These are **printed on paper**, not clicked through, so they carry no
Back/Next chrome. `preview.html` still pages through them for review, and
its print stylesheet lays the whole deck out one page per sheet.

figma file: TBD

These are not build steps and they are numbered on their own track.
`screens.md` row N renders model step N, so nothing may be inserted ahead
of row 1 -- see the note at the top of `tools/pages.py`.

The cast is our own animal crew, the same four in every story deck (see
`context/instruction-screens.md`): Sully the sloth, Tika the toucan, Pip
the tree frog, and Coco the capybara. They are not minifigures and not
the LEGO Education characters, on purpose. This deck is the wood on the
club poster: a press makes an old plank strong enough to use again, so a
new tree does not have to be cut.

```
slide | figma_frame | art | who | copy | camera | overlay
1 | HotPress/S1-wood    | renders/story-01.png | Tika, Pip, Coco, Sully | "Tika, Pip, Coco and Sully found a pile of old wood." | - | -
2 | HotPress/S2-plank   | renders/story-02.png | Tika | "Tika tried one plank. It was not strong enough." | - | -
3 | HotPress/S3-press   | renders/story-03.png | Pip, Coco, Sully | "A press squeezed the wood. It came out thin and strong." | - | -
4 | HotPress/S4-tree    | renders/story-04.png | Coco, Tika, Pip, Sully | "Old wood could be used again. No new tree had to fall." | - | -
5 | HotPress/S5-build   | renders/story-05.png | Coco | "Build a press. It comes down on the wood." | 20 205 | -
```

Slides 1-4 are drawn with an AI image tool from one character sheet,
`context/story-cast.jpg`, so the four look the same on every page. They
were generated at 16:9 and centre-cropped to 1536x1024, which is one of
the two frame sizes in `context/instruction-screens.md`, so they drop into
a landscape tablet frame with no resampling. Every figure is inside the
crop.

Slide 5 has a `camera`, which means `pages.py render` draws it from
`model.ldr` like any step hero. It is the only slide that is not an
illustration, on purpose.

## Slide 1 -- old wood

**Read aloud:** "Tika, Pip, Coco and Sully found a pile of old wood. It
was left over from a tree that had already been cut."

**Why all four:** the opening slide is the same shape as the other decks,
the four of them arriving somewhere, seen from behind.

**Art:** the four at the edge of a clearing, seen from behind, looking at
a tidy pile of old planks and one wide stump. Lush rainforest all around.
Soft light, a little sad, never scary.

## Slide 2 -- not strong enough

**Read aloud:** "Tika tried to use one plank. It bent. It was not strong
enough."

**Why Tika:** she is the one who tries the idea and writes it down. One
thin plank bending in her wings is the whole problem.

**Art:** Tika in the clearing, holding a thin plank that is bending. Her
red notebook under one wing. The pile of wood behind her.

## Slide 3 -- the press

**Read aloud:** "Then they saw a press. It squeezed a thick piece of wood
until the wood was thin and strong."

**Why Pip:** he is the one who points. The press in the drawing is a
plain workshop press, not the model, so nobody tries to copy it.

**Art:** Pip pointing at a simple grey workshop press in the clearing.
A thick plank is in the press and a thin plank lies beside it. Coco
and Sully watch, pleased. No words on the machine.

## Slide 4 -- no new tree

**Read aloud:** "Coco said the old wood could be used again. Nobody had
to cut a new tree."

**Why all four:** this is the cheering page, and it is the reason the
press belongs with the rainforest builds.

**Art:** the four together, happy, with the thin strong plank and the
forest still thick and green behind them. No saw, no falling tree.

## Slide 5 -- build it

**Read aloud:** "Coco said: let's build a press. It comes down on the
wood. It does not really squash it. It shows the squeeze."

**Why Coco:** she is the builder, the one with the tool belt. She hands
the story over to the bricks.

**Art:** none drawn. `renders/story-05.png` is a LeoCAD shot of the
finished model at camera `20 205`: low and nearly head-on, so the
motor's eyes look out and the blue beam, the green plate, and the wood
read as one press. The
step heroes use the same angle. Giving it a camera in the table means
`pages.py render` redraws it whenever the bricks move.

The LeoCAD PNG is transparent and drawn for a white page, so on the
slide's dark background it needs a white plate behind it or the black
axles disappear. `preview.html` does this automatically for any slide
with a camera; Figma has to do the same.
