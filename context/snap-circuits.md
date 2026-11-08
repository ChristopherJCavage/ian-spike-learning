# Snap Circuits

Ian also has Elenco Snap Circuits. The blocks are good; Elenco's manuals are
a page of pictures per project with almost no explanation, and there is no
order to learn in. This file is the plan for fixing the second part: our own
lessons, one idea each, in the same page style as the LEGO builds.

Not LEGO, not official curriculum, and not a copy of Elenco's manual. The
manuals are linked in `sources.md`; we write our own pages.

## The two boxes

Every block has its ID printed on it. That is how you tell which box a block
came from, and it is why every page prints the ID big (Elenco says colours
and styles vary). Inventories: `kits/scb20-beginner/parts.txt` and
`kits/sc100-jr/parts.txt`.

| Printed ID | Block | Beginner SCB-20 | Jr SC-100 |
|---|---|---|---|
| B3B | Battery holder, 3 AA = 4.5 V | 1 | - |
| B1 | Battery holder, 2 AA = 3 V | - | 1 |
| 3 | 3-snap wire | 4 | 3 (same part) |
| 1, 2, 4, 5 | Other snap wires | - | 3 / 5 / 1 / 1 |
| S1 | Slide switch | 1 | 1 (same part) |
| S2 | Press switch | 1 | 1 (same part) |
| L4 | White lamp (clear block, round lens) | 1 | - |
| L1 | 3 V lamp | - | 1 |
| D10 | Red/yellow LED, one colour each way | 1 | - |
| D8 | Colour LED | - | 1 |
| (egg) | white bulb cover; sits on the middle of a light block (D10 in the lessons) | 1 | - |
| M7 | Light motor (glows while it spins) | 1 | - |
| M1 | Motor | - | 1 |
| (fan) | Fan blade for the motor | 1 (inferred) | 1 |
| W1 | Horn | 1 | - |
| SP | Speaker | - | 1 |
| RP | Photoresistor (light sensor) | - | 1 |
| WC | Whistle chip | - | 1 |
| U1 U2 U3 | Music, alarm, space war modules | - | 1 each |
| (jumpers) | Red and black clip wires | - | 1 each |
| (grid) | Base grid | mini, 7.7 x 5.5 in | 11.0 x 7.7 in |

Neither inventory has been checked against a box yet:

- Beginner: Elenco says 14 parts and names 13. The 14th is almost certainly
  the fan blade. Chris to confirm.
- Jr: the 2021 manual's list adds up to 29, Elenco says 30. Older printings
  have a red LED (D1), a 100 ohm resistor (R1) and a 6-snap wire where the
  2021 list has the colour LED (D8). Fix `kits/sc100-jr/parts.txt` when the
  box lands, including which revision it is.

## Do the two boxes work together?

Yes. Same snap system, same grid pitch, and three parts are the same Elenco
part number in both boxes (3-snap wire, S1, S2): pool those.

**The battery rule.** B3B is 4.5 V and B1 is 3 V. Jr parts are rated for 3 V
(the Jr manual warns that more volts can burn out the lamp wire), so:

- Jr parts go on B1 only. `snap.py check` fails a layout that powers one from
  B3B (`OVERVOLT`).
- Beginner parts on B1 should simply run dimmer or slower. That is the
  expectation; it is not tested on a real box.

Storage: one bin per box, plus a "both" cup for the shared 3-snap wires and
the two switches (see `kits/storage.md`).

## One analogy for everything: the water park

Ian is 6, and electricity is invisible. Water is a picture he can trace with
a finger. The useful part of the picture is that the same water goes around
and comes back. It is not used up. A gap stops all of it, not just the water
at the gap.

The pump is the batteries. They do not hold the "water." The charge that
moves was already in the wires and the parts. What the AA cells supply is
the push: their chemicals shove that charge out of the + end, around the
loop, and back in at the − end. In grown-up words the push is voltage and
the moving charge is current. The comic says "push" and "water" to him, and
it says the real name out loud the first time each part appears.

Why it has to come back, which is the question a six-year-old asks about
Pip's one wire: the light does not eat the electricity. It uses some of the
push. If charge goes into the bulb and cannot leave, it crowds up, and that
crowd pushes back until it cancels the battery. The flow stops before the
bulb can glow. Case 1 says this in two talk pages, then keeps a second
picture: a bike chain. The pedals are the batteries, the chain is the
charge already in the wires, and a chain that does not return to the pedals
cannot keep turning.

Every lesson reuses this table. Case 1 has a Let's think page that says it
in the crew's voices, and each meet page prints `Really:` under the kid
name. The WHY? pages draw the picture from the real board (`water:` slides):
the water runs when the board works, and the picture shows where it stops
when it does not.

| Block | Really | In the picture | Kid name |
|---|---|---|---|
| Battery holder | the batteries | a pump | The Pump |
| Wire | a wire | a tube | Slide Tube |
| Slide switch | a switch | a gate you slide | The Gate |
| Press switch | a button | a gate you have to hold | The Button Gate |
| Lamp | a light bulb | a wheel the water squeezes past | The Glow Wheel |
| Motor (M1, Jr) | a motor | a wheel the water spins | The Spin Wheel |
| Light motor (M7) | a motor | a wheel that spins and glows | The Glow Spinner |
| Horn | a horn | a tiny drum the water shakes | The Splash Horn |
| LED (D10) | an LED | two flaps, red one way, yellow the other | The Two-Way Flap |
| LED (D8, Jr) | an LED | a flap that lets water through one way | The One-Way Flap |
| Photoresistor | a light sensor | a gate that opens wider in the light | The Sunny Gate |
| Fan | a fan | the blades on the wheel | The Fan |
| Short circuit | a wire straight across the battery | water skipping the wheel | The Shortcut |

## The comic: The Spark Detectives

Each lesson is a long comic in the spirit of Beast Academy: the characters
hit a problem, one of them makes the mistake Ian would make, the group works
out why, and Ian guesses, then tests, then hears the explanation. We copy the
**format and feel** only, never Beast Academy's characters, setting or pages.

- **Cast:** our own animal crew from the SPIKE decks, redrawn as a 2D comic:
  `context/story-cast-comic.png`, plus twelve reusable reaction poses in
  `context/comic/` (pointing, explaining, goggles, cheering, oops, magnifying
  glass, writing, asking, noticing, skating, puzzled, the crew cheering). Each
  has one job: **Coco** (capybara, tool belt) explains; **Pip** (frog) asks
  Ian's questions and makes the mistakes; **Tika** (toucan, notebook) keeps
  the case notes and runs the Number Lab; **Sully** (sloth, beanie) notices
  clues, and it is his skate show. Otto the otter is retired.
- **World:** not school, and not the jungle (that is the LEGO decks' world).
  The crew run a little detective agency in a town at night: their office,
  and the skate park. Every chapter is a case; every case ends "Case
  Closed" with a printable badge. The comic talks to Ian by name; he is the
  junior detective.
- **Modules so far:**
  1. `builds/snap-01-the-loop`, **The Night Skate Cases** (Beginner box), five
     cases on one loop: The Dark Skate Park (the loop), The Colour-Changing
     Light (D10 and its egg), The Silent Horn (S2 and W1; Pip's horn is in
     backwards), The Two Lights (D10 and the lamp in one circle), The Big Night (missions,
     no step pages).
  2. `builds/snap-02-flying-saucer`, **The UFO Case** (Jr box), two cases:
     the fan flies off the motor (Elenco's Flying Saucer, our pages), and
     Pip's backwards motor only blows.
- **Rules so far** (Tika's case notes): no circle, no light; some parts care
  which way round; the button gate only opens while you push; one gate, two
  paths, each light needs its own way back; guess first, then test it; fans
  push air, air pushes back; spin one way to fly, the other way to blow.
- **Number Lab:** the deck format still supports `numberlab` pages (the
  answer is worked out from the board), but Module 1 has none: Chris asked
  for them to come out (Nov 2026).
- **Art rules:** generate every panel with `context/story-cast-comic.png` as
  the reference. Describe Sully as "the brown sloth in the blue beanie": the
  name alone once got a blue horned monster from somebody else's film. No
  words in the art, and that includes graffiti, banners and signs. Panels
  live in `builds/<slug>/renders/comic-*.jpg` at 16:9; the preview crops them
  to the panel.

## What Elenco's own project list teaches

Elenco's SCB-20 manual has 21 projects. The ideas hiding in the titles (our reading, not Elenco's words):

- Projects 1-6: one block does one thing (motor, fan, lamp, red, yellow, horn).
- 7-8, 10, 19: two things in one loop.
- 11-12, 20: sharing the battery between parts (dimming).
- 13-14: two switches in a row versus side by side.
- 4-5, 17: flipping a part over changes what it does.
- 15-16, 18, 21: switches deciding what runs.

## Lesson arc

Module 1 (The Night Skate Cases) covers what used to be lessons 1-3 below:
the loop, the gate, and the one-way flap. Module 2 (The UFO Case) adds
thrust. What is left, as later modules:

| Idea | Try it | Boxes |
|---|---|---|
| Sharing the hill: two things in one loop each get less push | Lamp + motor in one loop | Beginner + a Jr 2-snap wire (the loop parity needs it) |
| Two gates: in a row both must be open; side by side either will do | Predict, then try each | Either (lay the OR board out and run `check` first) |
| The shortcut: why we never join the pump straight to itself | Picture only; batteries OUT | Either |
| The Sunny Gate (RP), cousin of the SPIKE colour sensor | Cover it, shine on it | Jr |
| Sound modules (U1-U3) and the speaker | Music, alarm, space war | Jr |
| Brain and battery: the SPIKE hub is a battery with a brain | Be the hub: press the gate when the program says "on" | Beginner + a LEGO build |

## How a chapter runs

Splash (Case N) -> comic problem and Pip's mistake -> a **talk page** (a row
of cartoon boxes where the crew argues the idea, one short bubble at a time)
-> meet the new blocks -> build with the comic (step pages for the first
loop, one swap page per later case) -> WATCH -> another talk page before the
guess -> GUESS!, then test -> WHY? (the water park) -> the talk page that
unpacks the surprise -> PUZZLE -> NUMBER LAB, with a talk page before the
harder maths -> CASE NOTES (the rule) -> CASE CLOSED badge -> cliffhanger.

Talk pages are the explanation, in the way a comic explains: Pip says the
wrong idea, someone asks a question, Coco gives a picture (water, a flap, a
clock, groups of things), and the last box says it in words a six-year-old
can repeat. They are not a second copy of the rule.

Every page has a grown-up strip under it (G hides it): **Do** (hands,
safety), **Watch for** (what tells you Ian is confused), **The real
reason** (one adult sentence, for his "why?"), and the **Answer** to any
question on the page, worked out by the checker. Bubbles pop in one per
click, so you can read them in voices; the preview remembers the page, and
the number keys jump to a case.

## How a lesson is built

`tools/snap.py` is the LeoCAD-and-ldrcheck of this kit. The source of truth
for a lesson is `circuit.snap`, a text layout; every page Ian copies is drawn
from it. `python3 tools/snap.py check builds/<slug>` proves:

- every block is from a box the build lists, in a quantity the boxes hold
  (`BOM`, `WRONG_KIT`), and `parts.txt` matches the layout
- blocks stay on the grid, never share a post at the same level, and every
  level-2 block's ends snap onto level-1 blocks that are already placed
  (`OFF_GRID`, `COLLISION`, `UNSUPPORTED`, `BUILD_ORDER`)
- no wire or closed switch joins + to - with nothing between (`SHORT`),
  checked with every switch closed as the worst case
- no part sits on a battery holder above its rating (`OVERVOLT`)
- every claim in an `expect` line holds: loop closed and lamp on, lamp off with
  the gate shut, LED red or yellow by which way round it sits, motor forward or
  backward, "dim" when loads share a loop (`EXPECT`)
- every chapter's board (`change`), puzzle board (`puzzle`) and mission
  answer (`mission ... => claims`) obeys the same rules, and each mission
  board really does what its card asks (`MISSION`); a fan launch is only
  drawn where the motor spins the `lift` way (`ASSIGN`)
- steps.md has a block for every step and scene, deck.md shows every step,
  change, scene and mission exactly once and in order, every slide has a
  grown-up line, and the renders are not stale (`STEPS_MD`, `DECK`, `DAD`,
  `RENDER`)
- every answer in the comic matches the board: GUESS! pages (`PREDICT`),
  puzzle boards (`PUZZLE`), and Number Lab facts such as the loop's post
  count, a post's name, the battery's volts, the colour after K flips, or
  how many settings a board has (`NUMBERLAB`)

`python3 tools/snap.py selftest` runs `tools/snap/fixtures/`: each `good-`
layout must pass clean and each `bad-` layout must trip exactly the one rule
it names, the same discipline as the LDraw fixtures.

### What the checker cannot see

- **Jr block sizes are still guesses.** The Beginner blocks are measured
  from photos of the real board (`measured: true` in
  `tools/snap/parts.json`): every 2-snap block is 1x3 with a snap at each
  end, a blue wire is 1x3 with three snaps, and the battery holder B3B is
  3x3 with its two snaps on one edge, so it rides the edge of the grid with
  the batteries hanging off. `check` fails a parts.json edit that changes
  any of those (`PARTS`). The Jr-only blocks (B1, M1, the big grid) are
  still `measured: false` and print an `UNMEASURED` warning.
- **Stacking.** Blocks only stack where end snaps meet, on one post, and
  leave it in different directions. `check` fails two blocks lying on top of
  each other (`OVERLAP`), a snap landing on a block's plastic (`BODY`), a
  block on top that would tilt more than one level (`TILT`), and a battery
  holder with nothing saying which side its case hangs (`HANG`). Every
  drawing is read back and compared with the layout (`DRAWN`), every post a
  page names must be a snap on that page's board (`POSTS`), and every photo
  of the real board is described in `circuit.snap` and compared too
  (`PHOTO`).
- **Which end is "forward".** The comics' answers lean on guesses about the
  + ends: D10 red with its + where current enters, W1 honking that way round,
  M7 spinning clockwise, and (`lift fwd`) M1's fan flying that way round.
  Each build's `preflight.md` has the five-minute test; if a guess is wrong,
  fix the data and `check` lists every page whose answer changed.
- **Parallel branches.** The electrical model handles them, and
  `good-parallel` is Case 4's real two-light board (photographed): the two
  joining wires snap on top of the stacks at 3E and 3C (level 3) and tilt
  one level onto the white light.
- **Not modelled yet:** the jumper wires, the whistle chip, the three sound
  modules, and what a photoresistor does with light. Using one fails
  `UNKNOWN_PART` (or is treated as a plain two-terminal part for RP and SP).
- **Brightness.** "dim" means "shares a loop with another load". It does not
  know a lamp from a motor.

## Safety

- Chris puts batteries in, spring pressed straight back, and checks the first
  ON. Batteries out while building anything that looks like the shortcut.
- A short circuit (a wire straight across the battery holder) can damage parts
  and flatten the batteries. The checker refuses to draw one.
- Moving parts: do not touch the motor or fan while it spins; a fan can fly
  off if the motor is driven fast. For the Flying Saucer (Module 2):
  goggles or sunglasses on everyone, lean back, never look straight down at
  the fan, aim it away from faces, a grown-up holds the board. Elenco's own
  warning says the same.
- Small parts, choking hazard under 3.

## Expansion path

- The Beginner set is **not upgradable**: Elenco's own summary says so.
- Real path: Snap Circuits Jr. SC-100 (the second box, arriving), then
  upgrade kits UC-30 (to SC-300), UC-40 (to SC-500), UC-60 (to SC-750). All
  upgrade from SC-100 or from each other; none upgrade from SCB-20. Parts also
  sell individually.
- Same snaps and grid pitch across the line, so the Beginner blocks mix into
  all of it. The battery rule above is the thing to watch.
