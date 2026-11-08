# Pre-flight -- The Night Skate Cases

`snap.py check` proves the comic agrees with `circuit.snap`, and that every
photo of the real board (`renders/real-*.jpg`, described by a `photo` line in
`circuit.snap`) agrees with the layout. The block sizes below were read off
those photos; this list is what to look at again if you rebuild from scratch.

## What the photos settled (Nov 2026)

1. **Grid.** The mini grid is 7 across and 5 down (7 x 5 = 35), columns
   1-7, rows A-E.
2. **Every Beginner block is 1x3.** S1, S2, L4, D10 and W1 each cover three
   posts with a metal snap at each end; the middle is plastic. A blue wire
   covers three posts with a snap at every post. `parts.json` marks these
   `measured: true`, and `check` fails if one is edited to a 1x2.
3. **B3B is 3x3 and rides the edge.** Its two snaps (+ and -) are on one
   edge only. The board puts that edge on row A (+ on 1A, - on 3A) and the
   batteries hang off the top of the grid. `check` fails a holder with no
   `side=` or one whose case lies on other blocks.
4. **Stacking.** Blocks only stack where their end snaps meet, on one post,
   then leave it in different directions. Two blocks never lie on top of
   each other along their length (`OVERLAP`), a snap never lands on another
   block's plastic (`BODY`), and a block on top can tilt one level at most
   (`TILT`).
5. **The + ends.** D10 glows **red** with its + at the bottom (3E, where the
   current comes in) and yellow turned around. W1 **honks** with its + on
   3E. M7 is not used in this module.

## Parts to put out

- The Beginner box (SCB-20): everything except the fan.
- **One blue 3-snap wire from the Jr box (SC-100).** Case 4 and mission 3
  use five blue wires; the Beginner box has four.

## Table check (batteries in)

- Case 1: build steps 1-8 with the Gate OFF. Gate ON: the egg glows yellow.
  Gate OFF: dark. Pull the bottom tube (1E-3E): dark.
- Case 2: lift the egg and the tube ends, turn D10 so its + is on 3E: red.
- Case 3: W1 honks with the + on 3E while S2 is held, and stops when let go.
  Turned so the + is at the top (3C), it is silent.
- Case 4: S1 and D10 back (+ on 3E, egg on). L4 on 5C-5E. Tubes 3E-5E and
  3C-5C, each snapped on top at 3E or 3C. Gate ON: red and white. Gate OFF:
  both dark. Pull the 3C-5C tube: only the white light goes out.
- Click through `preview.html` once yourself, with G on, before Ian sees it.

If anything is wrong, patch `circuit.snap` first, then `steps.md`, then run
`render`. `check` fails a stale render and any answer that no longer matches
the board, so nothing can be forgotten.
