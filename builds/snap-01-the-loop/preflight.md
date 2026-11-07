# Pre-flight -- The Night Skate Cases

`snap.py check` proves the comic agrees with `circuit.snap`. It cannot prove
`circuit.snap` agrees with the real blocks, because every size and every
"which end is +" in `tools/snap/parts.json` is still `measured: false`. Do
this once, before Case 1, with no batteries in.

## Measure on the real box (15 minutes)

1. **Grid.** Count the posts on the mini grid. The comic assumes 7 across and
   5 down (and asks Ian 7 x 5 = 35), rows lettered A-E. If it differs, fix
   `grid-mini` in `tools/snap/parts.json`; `check` will then tell you the
   Number Lab answer changed.
2. **How far each block reaches.** B3B covers 3 posts with snaps at the two
   ends; S1, S2, L4, D10, W1 and M7 cover 2; a blue wire covers 3. Compare
   with the board pictures for Case 1 steps 1-7. Fix `span`/`snaps` and set
   `measured: true` for each block you check.
3. **The + ends.** This is the one that matters most. The comic assumes:
   - B3B hangs off the top. + snap is 1A, the other snap is 3A.
   - D10 glows **red** when its + is at the bottom (3D), yellow turned around.
   - W1 **honks** with its + at the bottom (3D), silent turned around.
   - M7 spins **clockwise** with its + at the bottom (3D).
   Build each one in the Case 1 loop and look. If one is the other way, flip
   `colour_forward`/`colour_reverse` (D10), or tell the next person to swap
   the layout; `check` will list every page whose answer changed.
4. **The fan.** Count its blades: the Number Lab uses 3 (`blades` in
   `parts.json`). Is it the 14th part in the box?

## Table check (batteries in)

- Case 1: build steps 1-7 with the Gate OFF. Every wire end snug on a block's
  snap? Gate ON: lamp on. Gate OFF, lamp off. Pull the bottom tube: lamp off.
- Case 1: the egg is pressed on the yellow lamp. That is the bulb.
- Case 2: lift the egg off to see the LED. D10 + at the bottom: red. Turned:
  yellow. The egg can go back on the LED for the lantern.
- Case 3: Pip's horn (+ at the top) is silent; turned, it honks while S2 is
  held and stops when let go.
- Case 4: M7 spins and glows; turned around it spins the other way. Faces back.
- Click through `preview.html` once yourself, with G on, before Ian sees it.

If anything is wrong, patch `circuit.snap` first, then `steps.md`, then run
`render`. `check` fails a stale render and any answer that no longer matches
the board, so nothing can be forgotten.
