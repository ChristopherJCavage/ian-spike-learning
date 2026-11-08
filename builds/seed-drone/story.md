# Story -- Seed Drone

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
the LEGO Education characters, on purpose. This deck tells the club's
rainforest lesson: drones can help a forest grow back by dropping seeds
where trees were cut down. The Rainforest Drop Zone's red band is the bare
patch, so the story and the two builds are the same picture.

```
slide | figma_frame | art | who | copy | camera | overlay
1 | SeedDrone/S1-patch   | renders/story-01.png | Tika, Pip, Coco, Sully | "Tika, Pip, Coco and Sully found a bare patch. A big tree used to grow there." | - | -
2 | SeedDrone/S2-seed    | renders/story-02.png | Tika | "Tika dropped a seed. That is how toucans plant new trees." | - | -
3 | SeedDrone/S3-count   | renders/story-03.png | Sully, Tika | "But the patch was big. Sully counted the spots and ran out of claws." | - | -
4 | SeedDrone/S4-drone   | renders/story-04.png | Pip, Coco, Sully, Tika | "Pip pointed up. A drone was dropping seeds from the sky!" | - | -
5 | SeedDrone/S5-build   | renders/story-05.png | Coco | "Build a seed drone. When it sees red, it drops a seed." | 20 215 | -
```

Slides 1-4 are drawn with an AI image tool from one character sheet,
`context/story-cast.jpg`, so the four look the same on every page. They
were generated at 16:9 and centre-cropped to 1536x1024, which is one of
the two frame sizes in `context/instruction-screens.md`, so they drop into
a landscape tablet frame with no resampling. Every figure is inside the
crop.

Slide 5 has a `camera`, which means `pages.py render` draws it from
`model.ldr` like any step hero. It is the only slide that is not an
illustration, on purpose -- see below.

## Slide 1 -- the bare patch

**Read aloud:** "Tika, Pip, Coco and Sully went back to the rainforest.
Right in the middle of all that green was a bare brown patch. A big tree
used to grow there, until someone cut it down."

**Why all four:** the opening slide is the same shape as the other decks
-- the four of them arriving somewhere, seen from behind -- so Ian knows
where he is in the story before a word is read.

**Art:** the four at the edge of a clearing, seen from behind, looking at
an old tree stump in the middle of a patch of bare brown earth. Lush
rainforest all around the patch, so the gap is the one thing that looks
wrong. Soft light, a little sad, never scary.

## Slide 2 -- the seed

**Read aloud:** "Tika knew what to do. Toucans eat fruit, fly off, and
drop the seeds somewhere new, and the seeds grow into trees. So Tika flew
over the patch and dropped a seed."

**Why Tika:** it is true. Toucans really are one of the ways a rainforest
plants itself, and a six-year-old can hold that idea in one picture. It
also sets up exactly what the drone does: fly over, drop a seed.

**Art:** Tika gliding low over the bare patch, a single seed falling from
her beak toward the earth. Her red notebook sits on the stump below, so
she is still easy to spot. The other three watch from the far side of the
patch.

## Slide 3 -- too big

**Read aloud:** "But the patch was big. Sully counted all the spots that
needed a seed. One, two, three... and he ran out of claws, again."

**Why Sully:** he is the one who counts, and running out of claws is his
joke from the chameleon deck, so Ian gets to laugh at it a second time.
The joke is also the problem: one toucan with one seed at a time is not
enough for a patch this big.

**Art:** a wider view of the big bare patch with one tiny sprout where
Tika's seed landed. Sully in the foreground holding out both paws, claws
spread, puzzled. Tika resting on a second stump, tired. Two stumps say
more than one tree came down, which is why the patch is so big.

## Slide 4 -- the drone

**Read aloud:** "Then Pip pointed up. A drone was flying over the forest,
dropping seeds where the trees used to be. People really do this, to help
a forest grow back faster."

**Why Pip:** he is the bouncy one who cheers, and this is the cheering
page. The drone in the drawing is a real-world one, a plain four-rotor
drone, not the model, so nobody tries to copy it. The model comes next.

**Art:** Pip in the middle, pointing at the sky. A small grey four-rotor
drone overhead with a seed box underneath, seed pods falling from it
toward the bare patch. Sully, Tika, and Coco grinning beside him.

## Slide 5 -- build it

**Read aloud:** "Coco said: let's build our own seed drone. The red band
on the Drop Zone is our bare patch. When the drone sees red, it drops a
seed. It doesn't fly. You carry it, low over the forest, like a pilot."

**Why Coco:** she is the builder, the one with the tool belt. She hands
the story over to the bricks, as she does in the other decks.

**Art:** none drawn. `renders/story-05.png` is a LeoCAD shot of the
finished model at camera `20 215`: low and from the front quarter, so the
rotor, the face, a side bar, the skids, and the red ball in the tray
behind all read as one drone instead of a pile of bricks. The step heroes
use the higher `55 225` to show where a piece goes; this one has to look
like a drone. Giving it a camera in the table means `pages.py render`
redraws it whenever the bricks move, so it cannot go stale.

The LeoCAD PNG is transparent and drawn for a white page, so on the
slide's dark background it needs a white plate behind it or the black
pegs disappear. `preview.html` does this automatically for any slide with
a camera; Figma has to do the same.
