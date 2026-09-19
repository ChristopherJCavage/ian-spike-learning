# Story -- Chameleon Colour-Match

Five slides that come **before step 1**, the way the SPIKE App opens a
project. Chrome and the rules for this track: `context/instruction-screens.md`.

These are **printed on paper**, not clicked through, so they carry no
Back/Next chrome. `preview.html` still pages through them for review, and
its print stylesheet lays the whole deck out one page per sheet.

figma file: TBD

These are not build steps and they are numbered on their own track.
`screens.md` row N renders model step N, so nothing may be inserted ahead
of row 1 -- see the note at the top of `tools/pages.py`.

The cast is the real SPIKE Essential four, and the parts for all four are
in the box (`kits/45345-essential/parts.txt`, "Minifigure Parts"). Their
bios are LEGO Education's, linked from `context/sources.md`; we are using
the characters, not copying a lesson. Each one is on the slide that suits
who they actually are, because Ian will meet these same figures again in
every other Essential unit.

```
slide | figma_frame | art | who | copy | camera | overlay
1 | Chameleon/S1-trip    | renders/story-01.png | Sofie, Daniel, Maria, Leo | "Sofie, Daniel, Maria and Leo went to see a rainforest." | - | -
2 | Chameleon/S2-colour  | renders/story-02.png | Leo | "Leo started counting colours. He ran out of fingers." | - | -
3 | Chameleon/S3-spot    | renders/story-03.png | Leo | "Leo held still. Then a leaf blinked at him." | - | -
4 | Chameleon/S4-meet    | renders/story-04.png | Leo | "Leo learned its name. A chameleon changes colour to match where it sits." | - | -
5 | Chameleon/S5-build   | renders/story-05.png | Maria | "Build a chameleon that changes colour too." | 25 245 | renders/story-peek.png
```

Slides 1-4 are drawn and live in git at 1536x1024, which is one of the two
frame sizes in `context/instruction-screens.md`, so they drop into a
landscape tablet frame with no resampling.

Slide 5 has a `camera`, which means `pages.py render` draws it from
`model.ldr` like any step hero. It is the only slide that is not an
illustration, on purpose -- see below. It also has an `overlay`, the
chameleon from slide 4 cut into a sticker and tucked on the corner.

## Slide 1 -- the trip

**Read aloud:** "Sofie wanted to write a story about a real rainforest. So
all four of them went."

**Why Sofie leads:** she is the one who wants to be a journalist. She is
holding the notebook, and she is the one who writes down what Leo finds
two slides later.

**Art:** wide cartoon establishing shot. The four characters walking a
muddy path into the forest, seen from behind and slightly above, small
against enormous trees. A warm shaft of light through the canopy.
Friendly, storybook, no menace.

## Slide 2 -- the colour

**Read aloud:** "Everything was green. And then it was also red, and
orange, and blue, and yellow. Leo tried to count all of them -- and ran
out of fingers."

**Why Leo (build-tester note, was Daniel):** Ian's table read slide 2 as
Daniel's on the first pass, but it fits Leo better and sets up slide 3.
He is the quiet one who notices what everyone else walks past -- that is
the whole reason slide 3 already belonged to him. Here he is not just
looking at the colours, he is *counting* them, and that same close
attention is exactly what finds a lizard wearing the forest as a
disguise two pages later.

**Art:** the same forest, close up and loud. Leo -- blue top, dark green
legs, brown hair, same figure as slide 3 -- holds both hands up with all
ten fingers spread, caught mid-count and grinning at having run out.
Scarlet flowers, a blue morpho butterfly, yellow fruit, a tree frog, a
dozen different greens. This is the "oooo, aaaahhh" page -- it should be
the brightest thing in the deck, and it is.

## Slide 3 -- the chameleon

**Read aloud:** "The others walked right past it. Leo stayed still, and
that is why he saw it. A chameleon wears the colour of wherever it is
sitting. That is how it hides."

**Why Leo:** he is the quiet one, and he thinks frogs are the coolest.
Holding still being the *reason* he found it is the best thing this story
can teach a six-year-old right before a twenty-four step build.

**Art:** close on one mossy branch. A green chameleon -- curled tail,
turret eye, splayed grasping feet -- sitting on a leaf and almost exactly
the leaf's green. Its curled tail rests against a red bromeliad and has
gone red-orange to match, so the colour-changing is visible in one glance
rather than only in the narration. Leo crouched at the left, holding
still. Nobody else in frame.

## Slide 4 -- meet it

**Read aloud:** "It is called a chameleon. It can turn the colour of
whatever it is sitting on -- green on a leaf, blue by a blue flower. And
look what it does with its tongue."

**Why Leo (build-tester note, was Daniel):** slide 3 already belongs to
Leo, who found the chameleon by holding still -- so he is the one who
stays to watch it and is rewarded with the close look here, tongue and
all. Handing slide 4 to a character who was not even in slide 3 broke the
thread; keeping it Leo's means one kid's patience carries both pages.

**Art:** the chameleon front and centre, tongue shot out sideways in a big
cheeky curve to catch a fly. The body is caught mid-change and you can
read the whole idea in one glance: green head, yellow-orange middle,
turquoise tail where it touches a blue flower. Leo -- same blue top, dark
green legs, brown hair as slides 2 and 3 -- leans in on the left with
both hands on his cheeks, delighted.

The tongue is a drawing choice, not a build one. Ian's table found a
flex hose cannot actually mount on the sensor, so the real chameleon's
face is two black pegs and two white round eye tiles instead (steps
13-14), not a tongue. The art keeps the tongue anyway -- it is coral
pink-red, catching a tiny fly -- because this is the one page in the deck
where the drawing is allowed to be more chameleon than brick, the same
way it is allowed a tail that coils in one smooth sweep instead of a
stepped LEGO curl.

## Slide 5 -- build it

**Read aloud:** "Maria said: we could build one. Let's build one."

**Why Maria:** she is the inventive one who loves putting things together.
She hands the story over to the bricks.

**Art:** none drawn. `renders/story-05.png` is a LeoCAD shot of the
finished model at camera `25 245`. That angle keeps the whole animal
readable -- the two white eye tiles, all four feet, the tail curl, and
both the colour sensor and the light matrix -- while leaving the
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
of side 780 centred on (875, 480) in the 1536x1024 art, scale to 900x900,
mask to a circle inset 26px, and stroke that circle white at 26px.

**Build-tester re-cut:** slide 4 was regenerated with Leo in place of
Daniel (see above), which redraws the whole scene, so the crop was
re-checked against the new art rather than assumed. The chameleon landed
in the same part of the frame as before -- same crop, (875, 480) at side
780 -- because the new generation kept the same chameleon-on-the-right,
character-on-the-left layout. If a future regeneration shifts the
chameleon, re-derive the centre from that image rather than trusting
these numbers.
