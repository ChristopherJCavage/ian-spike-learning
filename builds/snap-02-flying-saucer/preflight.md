# Pre-flight -- The UFO Case

Do this once when the Jr box is open, before Case 6. Goggles on for the
launch tests.

## Inventory the box (10 minutes)

1. Lay everything out and check it against `kits/sc100-jr/parts.txt`. The
   2021 manual's list adds up to 29 parts but Elenco says 30; older boxes
   have a red LED D1, a 100 ohm resistor R1 and a 6-snap wire instead of the
   colour LED D8. Note which printing you have and fix the file.
2. Count the big grid's posts: the comic assumes 10 across, 7 down (A-G).
3. B1 and M1: how many posts do they cover? The layout assumes three, with
   a snap at each end, like every Beginner block (S2 and the blue wires are
   measured on the Beginner box). Fix `tools/snap/parts.json` and set
   `measured: true` for what you check.

## Which way flies (the one guess this module depends on)

`circuit.snap` says `lift fwd`: the fan flies when M1's + is at 3E (the
bottom, current coming in at its + end). Build Case 6 steps 1-8, goggles on,
hold S2 until it is fast, let go.

- **It flies:** the guess is right. Done.
- **It stays on and blows air up at your hand:** the box is the other way.
  Change `lift fwd` to `lift rev` in `circuit.snap` and run
  `python3 tools/snap.py check builds/snap-02-flying-saucer`. It will list
  every page whose answer changed (the guess pages and the puzzle); swap the
  motor's + in `steps.md` step 4 and the change page's bubble, then `render`.
- **It neither flies nor blows hard:** new alkaline batteries, and press S2
  several quick times at full speed before letting go (Elenco's tip).

## Table check

- Case 6: it spins while S2 is held; it lifts off when S2 is let go.
- Case 7: with M1 turned (+ at 3C), it blows air up and never flies.
- Click through `preview.html` once yourself, with G on, before Ian sees it.
