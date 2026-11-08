# Brief -- Chameleon Colour-Match

Status: **filled**.

## Theme / story

A rainforest chameleon. Slide a coloured pad under its head and its
back changes to match -- camouflage. If the pad is bright red, the
back lights warning-red instead: some animals shout "don't eat me."

Five story slides set it up before any bricks, with our animal crew:
the trip, the color, Sully holding still long enough to see a chameleon,
Sully meeting it, then build one. See `story.md`. The point of slide 3 is
that camouflage is why he nearly missed it -- the kid should want the
model to hide before being told how it works. Slide 4 then names the
animal and shows its big round eye and its tongue. The eye carries into
the build -- steps 13-14 press two white round tiles onto the sensor's
face, matching the drawing. The tongue does not: Ian's build-test found
a flex hose cannot mount on the sensor, so the drawing keeps a tongue
the model never had, and the last piece the build actually adds is the
tail's purple point (step 24), not a tongue.

## Complexity

- Target step count (Figma pages): 5 story slides, then 24 build steps +
  1 try-it page + 1 Icon Blocks page (26 numbered pages, 31 frames).
- How much help Ian gets vs Chris: Chris pins the hub, hips, snout, eye
  pegs, and matrix deck (the pin-heavy steps); Ian snaps sockets,
  ball-plate feet, the brow/tail plates, the whole tail, the eye tiles,
  cheek bumps, horns and colour patches. Code together.
- Sub-assemblies: `body` (hub, then plug-in-and-try-it), `legs` (hips +
  ball-and-socket feet), `head` (front pins through brow, T-beams,
  snout pins and colour sensor), `face` (eye pegs + white round eye
  tiles), `shoulders` (top pins + 7M deck + 3x3 matrix -- moved here
  from the tail by the build-tester hub flip), `tail` (rear pins
  through the curl), `code`.

## Hardware

- Hub: **essential** (2 ports A/B, no on-hub matrix)
- Motors: none -- both ports are taken
- Sensors: Colour Sensor -> port A (in the head, aimed down at a pad)
- Lights: 3x3 Colour Light Matrix -> port B (LEDs aimed up, the "skin")
- Done-when: slide a blue / yellow / green pad under the head and the
  back matches; slide a bright-red pad and the back goes warning-red.

## Constraints

- Only `kits/45345-essential/parts.txt`. Essential-only on purpose:
  Saturday class, Essential hub, no Prime, no Expansion.
- **Four ball-and-socket pairs, not five.** The box ships five
  `14704`/`14417` pairs but the fifth sits in the spare tray, not the
  main bin. Anything a table might have lost is off limits, so all four
  pairs go to the legs and the tail is built from plain clutch.
- **Colour is part of the spec.** Real rainforest chameleons run
  blue-green-brown along the body. The Essential bin's nearest run is
  azure and blue at the shoulders (matrix and deck -- moved here from
  the tail by the build-tester hub flip), bright green across the brow
  and the tail shelf, then dark green, light orange and purple down the
  tail. Purple horns and cheek bumps on the head, white eyes on the
  face, orange patches on the tail. The animal should be worth staring
  at before it is ever switched on.
- One hub (the Small Hub). Both ports used.
- Kid screens: Icon Blocks.
- Colour pads (2x4 tiles on plate bases) are **classroom props**, not in
  `model.ldr`. Chris cuts them from the same Essential bin before class.
  `CLEARANCE` is a *minimum* gap -- "mounted too high to read" stays a
  human check at the table.
