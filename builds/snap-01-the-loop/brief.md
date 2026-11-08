# Brief -- The Night Skate Cases

## Theme / story

The Spark Detectives (Sully, Tika, Pip and Coco, drawn as a comic) run a
little detective agency in town. Sully's night skate show keeps hitting
mysteries: the park is dark, a light changes colour, the start horn is
silent, then the show needs a red light and a white light at once. Each
mystery is one case, solved the way scientists work: a clue, a guess, a
test, case closed. Ian is the junior detective; the comic talks to him by
name, and Case 5 hands him the missions.

The water-park picture explains everything: battery = pump, wires = slide
tubes, switch = gate, LED/lamp/horn = wheels the water pushes. It is drawn
from the real board, so it changes when the board does.

## Complexity

- Five chapters (cases), about 110 pages, one sitting each (15-20 minutes).
- Build once in Case 1 (8 steps); Cases 2 and 3 are one or two block changes;
  Case 4 adds one block and two wires, one change per page.
- Chris puts the AA batteries in, watches the first ON, and reads the bubbles;
  Ian snaps, guesses, tests and answers.

## The ideas, one per case

1. No circle, no light. (A switch, or a missing tube, is a gap.)
2. Some parts care which way round. (D10: + at the top yellow, + at the
   bottom red.)
3. The button gate only opens while you push. (And Pip's "broken" horn was
   just backwards: rule 2 again.)
4. One gate, two paths. Each light needs its own way back. (Blocks can't be
   stacked on top of each other, so the white light goes next door.)
5. Guess first. Then test it. (Missions with no step pages.)

## Hardware

- Kits: Snap Circuits Beginner SCB-20, plus one blue 3-snap wire from Snap
  Circuits Jr. SC-100 for Case 4 and mission 3 (five blue wires; the
  Beginner box has four). No batteries in the box: 3x AA.
- Parts over the five cases: `parts.txt` (written by `snap.py bom`).
- Done-when: Ian can say all five rules in his own words, and solve the
  Case 5 missions without step pages.

## Constraints

- Only parts in the two boxes' `kits/*/parts.txt`. `snap.py check` enforces
  it, and fails the README if it doesn't say the build needs both boxes.
- Chris holds the AAs. No layout ever has a wire straight across the battery
  holder (`SHORT` fails the checker, in every chapter's board).
- The battery holder rides the top edge of the grid; every other block is
  1x3 and only stacks at its end snaps. The checker fails anything else.
- The fan stays in the box for this module.
