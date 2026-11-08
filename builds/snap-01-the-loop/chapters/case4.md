## Chapter 4 -- The Two Lights
badge: Both Lights

=== splash
art: renders/comic-c4-splash.jpg
say: Case 4: The Two Lights.
dad: Start from the Case 3 board. Get the white light (L4) from the
    Beginner box and ONE blue wire from the Jr box (SC-100). Tonight takes
    five blue wires; the Beginner box has four.
reason: One gate, then the current splits into two paths, one light on
    each. Open the gate and both go dark.

=== comic
panel: renders/comic-c4-hot.jpg
bubble: Sully @tr: The show needs a red light AND a white light!
bubble: Coco @bl: Both at once. One gate.
dad: Read it, then look at the real parts.

=== talk
layout: wide
box: renders/talk/c4-01-1.jpg
bubble: Sully: White for the ramp. Red for the start line.
box: renders/talk/c4-01-2.jpg
bubble: Pip: Easy. Stack the white light right on top of the red one!
box: renders/talk/c4-01-3.jpg
bubble: Tika: It won't sit. Blocks only join at the snaps on their ends.
box: renders/talk/c4-01-4.jpg
bubble: Coco: So the white light goes next door. Two tubes join them.
dad: Let him try Pip's idea with the real blocks: lay L4 on D10. It rocks
    and won't snap. Two blocks can share one end snap, then they have to
    go different ways.
reason: Blocks only connect at snaps. They can share a post and leave it in
    different directions, but they never lie on top of each other along
    their length.

=== change c4-red
pose: coco-point
bubble: Coco: Slide Gate back in. The colour light goes back, + on 3E.
bubble: Coco: Egg on top. That's the red light.
dad: Gate OFF. Swap S2 back to S1. Swap the horn for D10 with its + on 3E,
    the bottom snap. Press the tubes back down and put the egg on.

=== meet L4
pose: pip-magnify
bubble: Pip: Really, this is a light too. A white one!
bubble: Pip: No + on this one. It works either way round.
dad: L4 is the clear block with the round lens in the middle. Let him hunt
    for a + mark. There isn't one.

=== change c4-lamp
pose: coco-point
bubble: Coco: The white light stands on 5C and 5E. Next door, not on top.
dad: L4 snaps straight onto the grid, 5C to 5E. It does not touch the
    circle yet.

=== predict
pose: tika-ask
bubble: Tika: Guess first!
ask: Gate ON. Does the white light shine yet?
test: base=c4-lamp, S1=on
look: L4
choices: Lit=on | Dark=off
answer: Dark
reveal: Pip: Dark! Nothing joins it to the circle.
dad: Gate ON to test: red on, white dark. Then Gate OFF again.

=== change c4-tube1
pose: coco-point
bubble: Coco: A blue tube from 3E to 5E. At 3E it snaps on top.
dad: At 3E the new tube snaps on top of the tube already there. At 5E it
    snaps onto the white light. It tips a little. That's fine.
watch: Press both ends until they click.

=== predict
pose: sully-puzzled
bubble: Sully: Now it's joined. It HAS to shine!
ask: Gate ON. One tube. Does the white light shine?
test: base=c4-tube1, S1=on
look: L4
choices: Lit=on | Dark=off
answer: Dark
reveal: Coco: Still dark! The water gets in, but it has no way back.
dad: Test it, then Gate OFF. Ask where the water would go after the
    white light.
reason: One end joined is a dead end. The white light needs its own way
    back to the battery, just like Case 1.

=== change c4-tube2
pose: coco-point
bubble: Coco: Last tube, 3C to 5C. This one comes from the Jr box!
dad: All four Beginner tubes are on the board now. Take one from the Jr box.
    At 3C it snaps on top of the tube already there; at 5C it snaps onto
    the white light.

=== comic
panel: renders/real-c4-off.jpg
caption: The real board, Gate OFF.
bubble: Coco @tr: Yours should look like this.
bubble: Tika @br: White light on 5C to 5E. One tube on top, one on the bottom.
dad: Compare snaps, not the plastic. New tubes: 3E-5E along the bottom and
    3C-5C across, each snapped on top at 3E or 3C. The white light stands on
    5C and 5E. The holder still rides the top edge.

=== predict
pose: tika-ask
bubble: Tika: Big guess!
ask: Gate ON. Does the white light shine now?
test: base=c4-tube2, S1=on
look: L4
choices: Lit=on | Dark=off
answer: Lit
reveal: Pip: YES! And the red one too!
dad: Ian slides the Gate ON.

=== scene c4-both
pose: pip-cheer
bubble: Pip: Red AND white!
bubble: Sully: One gate did both!
dad: Slide the Gate OFF and ON a few times. Both lights go together.

=== comic
panel: renders/real-c4-on.jpg
caption: The real board, Gate ON.
bubble: Coco @tr: Both lights at once!
bubble: Sully @bl: The start line AND the ramp!
dad: Dim the room. Gate ON: red ball and white light. Gate OFF: both dark.

=== why
water: base=c4-tube2, S1=on
pose: coco-explain
bubble: Coco: Through the gate, then the water splits.
bubble: Coco: One stream for the red light. One for the white light.
dad: Point at the gate first, then follow each stream back to the pump.
reason: After the switch the circuit forks into two paths. Each light is its
    own path back to the battery.

=== talk
layout: hero
box: renders/talk/c4-02-1.jpg
bubble: Tika: Gate off. The water stops before either light.
box: renders/talk/c4-02-2.jpg
bubble: Pip: Gate on. Now the water can split.
box: renders/talk/c4-02-3.jpg
bubble: Sully: Pull the top tube off. Only the white light goes out!
box: renders/talk/c4-02-4.jpg
bubble: Coco: Two paths. One gate in front of both.
dad: The next page tests Sully's idea for real.
reason: The lights are in parallel. Breaking one path leaves the other.
    The switch is in front of both, so it stops both.

=== predict
pose: pip-magnify
bubble: Pip: Let's test Sully's idea.
ask: Gate ON. Pull off the top tube, 3C to 5C. Is the red light still on?
test: base=c4-tube2, S1=on, remove=11
look: D10
choices: Red=red | Yellow=yellow | Dark=off
answer: Red
reveal: Tika: Still red! Only the white light lost its way back.
dad: Pull the 3C-5C tube, look, then press it back on.
reason: Each light is its own loop. Breaking the white light's loop leaves
    the red light's loop whole.

=== predict
pose: tika-ask
bubble: Tika: Now turn the colour light around.
ask: Turn D10 around, + on 3C. Gate ON. What colour now?
test: base=c4-tube2, S1=on, flip=4
look: D10
choices: Red=red | Yellow=yellow | Dark=off
answer: Yellow
reveal: Coco: Yellow AND white! Rule 2 still works.
dad: Optional: lift the egg and the three tube ends at 3C and 3E, turn D10,
    press them back. Yellow and white. Turn it back to red after.

=== comic
panel: renders/comic-c4-wind.jpg
bubble: Sully @tr: Both lights! The show can start!
bubble: Tika @bl: The water split, and the gate still runs both.
dad: Ask what can stop both lights. The gate, or the tube before the split.

=== talk
layout: zigzag
box: renders/talk/c4-03-1.jpg
bubble: Coco: The gate is before the split.
box: renders/talk/c4-03-2.jpg
bubble: Pip: After the gate, the water splits.
box: renders/talk/c4-03-3.jpg
bubble: Tika: Two circles. One through each light.
box: renders/talk/c4-03-4.jpg
bubble: Sully: Shut the gate. Both lights quit.
dad: Have him say it back: one gate, two circles, two lights.
reason: The switch is in series with both lights. The two lights are in
    parallel.

=== puzzle
pose: tika-ask
bubble: Tika: Is the white light lit?
ask: Is the white light lit?
boards: c4-a, c4-b, c4-c
look: L4
choices: Lit=on | Dark=off
answer: c4-a=Lit, c4-b=Dark, c4-c=Dark
stars: 2
dad: A is Gate on. B is Gate off, so nothing lights. C is Gate on, but the
    top tube to the white light is gone: only the red light shines.

=== rule
rule: One gate, two paths. Each light needs its own way back.
pose: tika-write
bubble: Tika: Rule 4!
dad: The water splits after the gate, so the gate runs both. Each light
    still needs a full circle of its own.

=== badge
bubble: Coco: Case 4 closed. Both Lights!
dad: Print the badge if he wants it.

=== comic
panel: renders/comic-c4-cliff.jpg
caption: Tomorrow night...
bubble: Tika @tr: The Big Night. You build from the cards.
dad: Case 5 has no step pages. Ian builds from mission cards. Keep the Jr
    box tube handy: mission 3 needs it.
