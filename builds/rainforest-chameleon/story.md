# Story -- Chameleon Color-Match

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
the LEGO Education characters, on purpose. Each one is on the slide that
suits who they are, so Ian meets the same friends again in the next deck.

```
slide | figma_frame | art | who | copy | camera | overlay
1 | Chameleon/S1-trip    | renders/story-01.png | Tika, Pip, Coco, Sully | "Tika, Pip, Coco and Sully went to see a rainforest." | - | -
2 | Chameleon/S2-color   | renders/story-02.png | Sully | "Sully started counting colors. He ran out of claws." | - | -
3 | Chameleon/S3-spot    | renders/story-03.png | Sully | "Sully held still. Then a leaf blinked at him." | - | -
4 | Chameleon/S4-meet    | renders/story-04.png | Sully | "Sully learned its name. A chameleon changes color to match where it sits." | - | -
5 | Chameleon/S5-build   | renders/story-05.png | Coco | "Build a chameleon that changes color too." | 25 245 | renders/story-peek.png
```

Slides 1-4 are drawn with an AI image tool from one character sheet, so
the four look the same on every page. They were generated at 16:9 and
centre-cropped to 1536x1024, which is one of the two frame sizes in
`context/instruction-screens.md`, so they drop into a landscape tablet
frame with no resampling. Every figure is inside the crop.

Slide 5 has a `camera`, which means `pages.py render` draws it from
`model.ldr` like any step hero. It is the only slide that is not an
illustration, on purpose -- see below. It also has an `overlay`, the
chameleon from slide 4 cut into a sticker and tucked on the corner.

## Slide 1 -- the trip

**Read aloud:** "Tika wanted to write a story about a real rainforest. So
all four of them went."

**Why Tika leads:** she is the one who wants to write things down. She is
carrying the red notebook, and she is the one who writes down what Sully
finds two slides later.

**Art:** wide storybook establishing shot. The four walking a muddy path
into the forest, seen from behind, small against enormous buttress-rooted
trees. Tika in front with her notebook, Pip hopping beside her, Coco with
her tool belt, Sully in his blue beanie at the back. A warm shaft of light
through the canopy. Friendly, no menace.

## Slide 2 -- the color

**Read aloud:** "Everything was green. And then it was also red, and
orange, and blue, and yellow. Sully tried to count all of them -- and ran
out of claws."

**Why Sully:** he is the slow, quiet one who notices what everyone else
walks past. Here he is not just looking at the colors, he is *counting*
them, and that same close attention is what finds a lizard wearing the
forest as a disguise on the next page. A sloth has only three claws on
each hand, so running out is quick, and that is the joke.

**Art:** the same forest, close up and loud. Sully, arms up and claws
spread, grinning at having run out. Scarlet bromeliads, a blue morpho
butterfly, yellow fruit, orange lilies, pink orchids, a red-eyed tree frog
on a leaf. This is the "oooo, aaaahhh" page -- it should be the brightest
thing in the deck, and it is.

## Slide 3 -- the chameleon

**Read aloud:** "The others walked right past it. Sully stayed still, and
that is why he saw it. A chameleon wears the color of wherever it is
sitting. That is how it hides."

**Why Sully:** holding still is the one thing a sloth is best at, and it
being the *reason* he found the chameleon is the best thing this story can
teach a six-year-old right before a twenty-four step build.

**Art:** one mossy branch. A green chameleon -- curled tail, turret eye,
grasping feet -- on a leaf and almost exactly the leaf's green. Its curled
tail sits by a red bromeliad and has gone red-orange to match, so the
color-changing reads in one glance rather than only in the narration.
Sully rests on the branch at the left, very still and quietly amazed.
Nobody else in frame.

## Slide 4 -- meet it

**Read aloud:** "It is called a chameleon. It can turn the color of
whatever it is sitting on -- green on a leaf, blue by a blue flower. And
look what it does with its tongue."

**Why Sully:** slide 3 already belongs to him, so he is the one who stays
to watch and is rewarded with the close look here, tongue and all. One
friend's patience carries both pages.

**Art:** the chameleon front and centre, tongue shot out sideways in a big
cheeky curve to catch a fly. The body is caught mid-change: green head,
orange and turquoise patches down the back, a big blue flower beside it.
Sully leans in on the left with both paws on his cheeks, delighted.

The tongue is a drawing choice, not a build one. Ian's table found a
flex hose cannot actually mount on the sensor, so the real chameleon's
face is two black pegs and two white round eye tiles instead (steps
13-14), not a tongue. The art keeps the tongue anyway, because this is the
one page in the deck where the drawing is allowed to be more chameleon
than brick, the same way it is allowed a tail that coils in one smooth
sweep instead of a stepped LEGO curl.

## Slide 5 -- build it

**Read aloud:** "Coco said: we could build one. Let's build one."

**Why Coco:** she is the builder, the one with the tool belt. She hands
the story over to the bricks.

**Art:** none drawn. `renders/story-05.png` is a LeoCAD shot of the
finished model at camera `25 245`. That angle keeps the whole animal
readable -- the two white eye tiles, all four feet, the tail curl, and
both the color sensor and the light matrix -- while leaving the
bottom-right corner clear for the sticker. This is the one slide where
the kid sees exactly what they are about to make, so it must not be an
illustration, and it has to keep matching the model -- giving it a camera
in the table means `pages.py render` redraws it every time the bricks
move, so it cannot go stale the way a saved screenshot would.

`25 245` is low and side-on rather than the `55 225` used for the step
heroes. From up there the animal reads as a pile of bricks; from down here
you get head, then body, then tail, reading as an animal, which is the
whole job of this slide. After the hub flip the matrix sits over the
shoulders, so a one-plate curl hid behind the body on the old `30 235`
front-left shot. The curl now runs three plates out to -X, past the
feet, and this camera is a few degrees further around so that run is a
silhouette, not a pile of plates.

The LeoCAD PNG is transparent and drawn for a white page, so on the
slide's dark background it needs a white plate behind it or the black
pegs and grey feet disappear. `preview.html` does this automatically for
any slide with a camera; Figma has to do the same.

**Overlay:** `renders/story-peek.png` is the chameleon from slide 4, cut
into a round white-ringed sticker and parked on the bottom-right corner of
the model. The join between story and build is the weakest moment in the
deck -- the drawing stops and the bricks start -- and having the animal
lean in and look at its own LEGO self carries the kid across it. It sits
on the corner so it never covers the model, which is the thing being
copied.

The sticker is derived from the slide 4 art, not drawn separately, so the
two are the same animal. To redo it after changing slide 4: crop a square
of side 820 centred on (880, 570) in the 1536x1024 art, scale to 900x900,
mask to a circle inset 26px, and stroke that circle white at 26px. If a
future redraw moves the chameleon, re-derive the centre from that image
rather than trusting these numbers.
