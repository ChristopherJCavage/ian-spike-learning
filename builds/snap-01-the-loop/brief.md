# Brief -- The Night Skate Cases

## Theme / story

The Spark Detectives (Sully, Tika, Pip and Coco, drawn as a comic) run a
little detective agency in town. Sully's night skate show keeps hitting
mysteries: the park is dark, a light changes colour, the start horn is
silent, Sully's fan blows the wrong way. Each mystery is one case, solved
the way scientists work: a clue, a guess, a test, case closed. Ian is the
junior detective; the comic talks to him by name, and Case 5 hands him the
missions.

The water-park picture explains everything: battery = pump, wires = slide
tubes, switch = gate, lamp/LED/horn/motor = wheels the water pushes. It is
drawn from the real board, so it changes when the board does.

## Complexity

- Five chapters (cases), about 100 pages, one sitting each (15-20 minutes).
- Build once in Case 1 (7 steps); every later case is one or two block swaps.
- Chris puts the AA batteries in, watches the first ON, and reads the bubbles;
  Ian snaps, guesses, tests and answers.

## The ideas, one per case

1. No circle, no light. (A switch, or a missing tube, is a gap.)
2. Some parts care which way round. (D10: red one way, yellow the other.)
3. The button gate only opens while you push. (And Pip's "broken" horn was
   just backwards: rule 2 again.)
4. Flip the motor, flip the spin. (And the wind changes direction.)
5. Guess first. Then test it. (Missions with no step pages.)

## Number Lab (2nd-3rd grade maths, from the board)

Coordinates (post names), 7 x 5 = 35, the loop's perimeter (10 posts), why
every loop is even, odd/even flips, 1 1/2 + 1 1/2 + 1 1/2, honk-the-answer
addition and equal groups, clockwise, 3 x 10 and 3 x 25 blades, counting
cases (2 x 2 = 4 settings but only 3 shows; 2 x 2 x 2 = 8).

## Hardware

- Kit: Snap Circuits Beginner SCB-20 only. No batteries in the box: 3x AA.
- Parts over the five cases: `parts.txt` (written by `snap.py bom`).
- Done-when: Ian can say all five rules in his own words, and solve the
  Case 5 missions without step pages.

## Constraints

- Only parts in `kits/scb20-beginner/parts.txt`. `snap.py check` enforces it.
- Chris holds the AAs. No layout ever has a wire straight across the battery
  holder (`SHORT` fails the checker, in every chapter's board).
- Faces back from the fan in Case 4 and Case 5. Never touch it spinning.
