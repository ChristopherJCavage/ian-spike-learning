# The Night Skate Cases

The Spark Detectives, Module 1. Snap Circuits Beginner box (SCB-20), plus
one blue wire from the Jr box (SC-100) in Case 4 and Case 5: the two-light
board needs five blue wires and the Beginner box has four.
Five cases, one sitting each. The talk pages are comic pages (a full splash,
two wide panels, a banner over three boxes, and so on, not the same 2x2
every time). Pause there if he wants to answer before the next box. Ian builds along with the
comic: the board pictures come from `circuit.snap`, and every answer on a
GUESS, PUZZLE, NUMBER LAB and MISSION page is worked out by
`python3 tools/snap.py check builds/snap-01-the-loop`. If the board changes,
`check` says which answers changed.

Format: `parse_deck()` in `tools/snap.py`, and `builds/_snap-template/deck.md`.
The cast and their jobs: `context/snap-circuits.md`.

series: The Spark Detectives
module: The Night Skate Cases

## Chapter 1 -- The Dark Skate Park
badge: Light Finder

=== cover
art: renders/comic-chapter-1.jpg
dad: This is the chapter card. One click starts Case 1. Sit side by side.
    A click (or the space bar) shows the next page. G hides these notes.
    Number keys jump to a case.

=== splash
art: renders/comic-c1-splash.jpg
say: The Spark Detectives. Case 1.
dad: Sit side by side. A click (or the space bar) shows the next bubble, then
    the next page. G hides these notes. Number keys jump to a case.
reason: The whole case is one idea: electricity only flows in a full circle.

=== comic
panel: renders/comic-c1-office.jpg
caption: The Spark Detectives' office, after dark.
bubble: Tika @tr: A new case! The skate park went dark.
bubble: Sully @bl: No light, no skating. Can we fix it?
dad: Do the voices. The speaker's name is on top of each bubble.
watch: Ask what a detective does. Looks for clues, makes a guess, tests it.
    That is the method of every case.

=== comic
panel: renders/comic-c1-onewire.jpg
caption: Pip tries first.
bubble: Pip @tr: Easy! One wire from the battery to the light.
bubble: Sully @bl: Pip... it's still dark.
bubble: Pip @br: Huh?!
dad: Let Ian say what went wrong before you click on.
reason: One wire gives the electricity a way out of the battery but no way
    back in, so nothing flows at all.

=== talk
layout: splash
box: renders/talk/c1-04-splash.jpg
bubble: Pip: Why not one wire? Push electricity into the light. The light can use it!
bubble: Coco: The light does not eat electricity. It only uses the push.
bubble: Tika: If electricity goes in and can't leave, it crowds up in there.
bubble: Sully: The crowd pushes back as hard as the battery. Then the flow stops.
dad: Let him argue for one wire first. Then ask: if the electricity stays in
    the bulb, what stops more from coming in?
watch: "It should still glow a little" means he thinks the light uses
    electricity up slowly. It doesn't. The crowd pushes back at once, so the
    bulb stays dark.
reason: Charge is conserved. A tiny bit of charge moves onto the open end,
    the field from that imbalance cancels the battery, and the steady current
    is zero. The bulb consumes energy, not charge, so the filament never heats.

=== talk
layout: spread
box: renders/talk/c1-05-a.jpg
bubble: Pip: Why can't the light just eat all the electricity?
bubble: Coco: It has nowhere to keep it. A bulb is not a stomach.
box: renders/talk/c1-05-b.jpg
bubble: Tika: If it stayed inside, the bulb would fill up and block the door.
bubble: Sully: It can only pass through. It has to come out the other side.
dad: Let him say where the electricity would sit if the bulb ate it. There
    isn't a place. The next page is the way out: back to the battery.
reason: A lamp does not consume charge. There is no reservoir in the bulb.
    Charge can only pass through, and the return wire is that way out.

=== talk
layout: cinema
box: renders/talk/c1-06-1.jpg
bubble: Pip: So the electricity is still there, after the light?
box: renders/talk/c1-06-2.jpg
bubble: Coco: Yes. The light took some of the push. The electricity goes home.
box: renders/talk/c1-06-3.jpg
bubble: Tika: Like a bike chain. The back wheel does not eat the chain.
box: renders/talk/c1-06-4.jpg
bubble: Sully: The chain has to come back to the pedals, or nothing keeps turning.
dad: Pedals are the batteries, the push. The chain is the electricity already
    in the wires. The bulb is a tight spot the chain has to drag through.
    One loose end and the pedals can't keep it moving.
reason: The return wire lets the same charge circulate. The battery keeps
    supplying energy; it does not supply the charge the bulb "uses up."

=== talk
layout: hero
box: renders/talk/c1-07-1.jpg
bubble: Coco: We can't see electricity. So picture that push as water.
box: renders/talk/c1-07-2.jpg
bubble: Tika: The batteries are the pump. The wires are tubes.
box: renders/talk/c1-07-3.jpg
bubble: Pip: The light bulb is a wheel the water has to squeeze past.
box: renders/talk/c1-07-4.jpg
bubble: Sully: Same rule as the chain. The water has to come back.
dad: Stay on the chain until he can say it. Then this page is the switch to
    the picture. Point at the real battery holder, a wire, and the light as
    each box names it.
reason: Water is only a stand-in, introduced after the return path is already
    clear. The pump is still the batteries' push. The water is the charge,
    and it is not used up.

=== comic
panel: renders/comic-c1-chalkboard.jpg
caption: Coco draws the picture.
bubble: Coco @tl: Here is that water. The pump pushes it out...
bubble: Coco @tr: ...past the wheel, and BACK to the pump.
bubble: Tika @bl: Same as the chain. All the way around!
dad: Trace the circle on the drawing. Pump, tube, wheel, tube, pump. Say
    which real part each one is.
reason: This drawing is the picture from the previous page, not a new idea.
    Every later case reuses it.

=== talk
layout: spread
box: renders/talk/c1-09-a.jpg
bubble: Coco: Put a finger on the pump. Follow the tube.
bubble: Pip: Down, around the wheel, and back to the pump!
box: renders/talk/c1-09-b.jpg
bubble: Sully: I ended where I started. That's a circle.
bubble: Tika: If your finger falls off, it is not a circle yet.
dad: Trace the chalk circle together. His finger, then yours. Pump, tube,
    wheel, tube, pump.
reason: A circuit is a closed path. The finger-trace is the test he will use
    on every board in this module.

=== meet B3B
pose: coco-point
bubble: Coco: Really, these are the batteries. They do the pushing.
bubble: Coco: We call that push the Pump. A grown-up puts them in.
dad: Ian finds the battery holder in the Beginner bin. You put the batteries
    in at step 2.
reason: B3B holds 3 AA batteries: 4 1/2 volts.

=== meet wire3
pose: coco-point
bubble: Coco: Really, these are wires. The blue plastic is just the cover.
bubble: Coco: In the picture they are tubes. Electricity rides inside.
dad: The box has 4 blue 3-snap wires. This case uses 3.

=== meet S1
pose: coco-point
bubble: Coco: Really, this is a switch. Slide it to open or shut the path.
bubble: Coco: In the picture, a switch is a gate in the tube.
dad: Let him slide it back and forth before it goes on the board.

=== meet D10
pose: coco-point
bubble: Coco: Really, this is a light. A special kind, called an LED.
bubble: Coco: In the picture it's a wheel. Squeezing past is what makes it glow.
dad: Find the little + on one end of D10. It goes at the top tonight. It
    matters a lot in Case 2.

=== step 1
pose: sully-notice
bubble: Sully: Numbers go across. Letters go down. 1A is the corner.

=== step 2
pose: coco-point
bubble: Coco: The holder rides the top edge. Its snaps land on 1A and 3A.
bubble: Coco: The rest of it hangs off the board.
dad: Only one edge of the holder has snaps: + and -. Snap that edge onto
    row A, + on 1A. The batteries hang off the top of the grid.

=== step 3
pose: coco-point
bubble: Coco: The switch snaps on 1C and 1E. Slide it to OFF.

=== step 4
pose: pip-cheer
bubble: Pip: The Colour Wheel! Its + goes at the top, on 3C.

=== step 5
pose: coco-point
bubble: Coco: This blue tube runs from 1A down to 1C.

=== step 6
pose: coco-point
bubble: Coco: This blue tube runs from 1E across to 3E.

=== step 7
pose: tika-ask
bubble: Tika: Last tube, 3C up to 3A. Trace the circle with your finger.

=== step 8
pose: coco-point
bubble: Coco: Press the white ball onto the light. Now it's a big bulb.

=== comic
panel: renders/real-c1.jpg
caption: The real board.
bubble: Coco @tr: Yours should look like this. Batteries hang off the top.
bubble: Tika @bl: The white ball sits on the light, in the middle.
dad: Compare snaps, not the plastic. The holder snaps on 1A (+) and 3A; the
    rest hangs off. Switch: 1C to 1E. Blue tubes: 1A-1C, 1E-3E, 3C-3A. The
    light's + is the top snap, 3C. The egg stays on for the whole case.
reason: Every Beginner block is three posts long with a snap at each end.
    The battery holder is 3x3 with snaps on one edge only, so it rides the
    edge of the grid.

=== scene watch
pose: pip-cheer
bubble: Pip: IT LIGHTS!
bubble: Sully: Now I can see the ramp!

=== why
water: S1=on
pose: coco-explain
bubble: Coco: The pump pushes. The water goes all the way round.
bubble: Coco: Every time it passes the wheel, the wheel glows.
dad: Point at the dots moving along the tube: out of the pump and back in.
reason: Current flows from + round the loop to -. The lamp's thin wire gets
    hot enough to glow.

=== talk
layout: zigzag
box: renders/talk/c1-25-1.jpg
bubble: Pip: The water is moving. Why does the wheel GLOW?
box: renders/talk/c1-25-2.jpg
bubble: Coco: The wheel is a skinny hill. The water has to squeeze past.
box: renders/talk/c1-25-3.jpg
bubble: Tika: Squeezing through makes it hot. Hot enough to shine!
box: renders/talk/c1-25-4.jpg
bubble: Sully: Like a toaster wire. Tiny, so we can skate by it.
dad: Point at the moving dots, then at the wheel. Ask what the water is
    doing to the wheel (pushing through it).
reason: The filament heats because the current does work getting through it.
    Same current comes back to the battery; the energy came from the
    chemicals in the cells.

=== predict
pose: tika-ask
bubble: Tika: Detectives guess first. Then they test.
ask: Gate OFF. Light or dark?
test: S1=off
look: D10
choices: Light=on | Dark=off
answer: Dark
reveal: Coco: Dark! A shut Gate makes a gap.
dad: Ian picks out loud BEFORE you click, then slides S1 off to test.
watch: Guessing wrong is fine; Pip does it all the time. The test is the point.

=== why
water: S1=off
pose: coco-explain
bubble: Coco: The Gate blocks the tube. The water stops.
bubble: Coco: Not just at the Gate. EVERYWHERE.
dad: Ask where the water stops. Everywhere: a circle with a gap is not a circle.
reason: A switch opens a gap in the loop. No complete path, no current
    anywhere in it.

=== talk
layout: spread
box: renders/talk/c1-28-a.jpg
bubble: Pip: The water stops at the Gate. The rest can keep going!
bubble: Coco: Water in a full tube can't bunch up. All moves, or none.
box: renders/talk/c1-28-b.jpg
bubble: Tika: If it can't pass the Gate, it can't leave the pump.
bubble: Sully: The WHOLE circle stops. Not just one spot.
dad: This is the idea of the case. Let him argue Pip's side first. Then ask
    "can the pump push if the water has nowhere to go?"
watch: If he thinks the light stays on because it is "after" the gate, he
    is picturing water that piles up. Go back to "all moves, or none."
reason: Current is the same at every point in a single loop. Open the
    switch and the current is zero everywhere, not just at the switch.

=== predict
pose: pip-magnify
bubble: Pip: What if a tube comes off?
ask: Gate ON. Pull off the bottom tube. Light or dark?
test: S1=on, remove=6
look: D10
choices: Light=on | Dark=off
answer: Dark
reveal: Coco: Dark again. A missing tube is a gap too.
dad: Gate ON first. Ian pulls the tube from 1E to 3E, then presses it back
    after the reveal.

=== predict
pose: sully-puzzled
bubble: Sully: Maybe ONE tube doesn't matter?
ask: Which tube can you take out and keep the light on?
fact: keeps-on D10 @ S1=on
board: S1=on
answer: none
stars: 2
reveal: Tika: None of them! Every tube is part of the circle.
dad: Let him test all three tubes, one at a time. The light goes out every time.
reason: In one loop every piece carries all the current. Break any one and
    the whole loop stops.

=== talk
layout: stack
box: renders/talk/c1-31-1.jpg
bubble: Pip: Maybe the bottom tube is extra. Pull it off!
box: renders/talk/c1-31-2.jpg
bubble: Tika: Trace what's left. Pump, Gate, wheel... then a hole.
box: renders/talk/c1-31-3.jpg
bubble: Coco: A circle with a hole in it is just a curly line.
box: renders/talk/c1-31-4.jpg
bubble: Sully: Every tube is part of the circle. Any one, and it goes dark.
dad: He can pull each tube once more while saying "hole in the circle."
reason: Series means one path. There is no second path for the current to
    take, so any single break stops the loop.

=== puzzle
pose: tika-ask
bubble: Tika: Detective puzzle! Look for the gaps.
ask: Which boards light up?
boards: c1-a, c1-b, c1-c
look: D10
choices: Light=on | Dark=off
answer: c1-a=Dark, c1-b=Light, c1-c=Dark
stars: 1
dad: Point at each board. Ian says light or dark, then click to check.
watch: Board A is missing a tube; board C has the Gate off. Let him find the
    clues himself.

=== comic
panel: renders/comic-c1-lit.jpg
caption: That night.
bubble: Sully @tr: The light is on. Look at me go!
bubble: Pip @bl: Case closed!
dad: Ian switches the light on for Sully: slide S1 ON.

=== badge
rule: No circle, no light.
bubble: Coco: Case 1 closed. You are a Light Finder!
dad: Print this page for his badge (the browser's print dialog can print
    just the current page).

=== comic
panel: renders/comic-c1-cliff.jpg
caption: Next time...
bubble: Pip @tr: Sully's show needs COLOURS! Red! Yellow!
bubble: Tika @bl: Case 2 is coming...
dad: Leave the board built. Case 2 starts from it.

## Chapter 2 -- The Colour-Changing Light
badge: Colour Detective

=== splash
art: renders/comic-c2-splash.jpg
say: Case 2: The Colour-Changing Light.
dad: Start from the Case 1 board. If it was taken apart, rebuild it from the
    Case 1 step pages (press 1).
reason: New idea: some parts care which way round they go.

=== comic
panel: renders/comic-c2-clue.jpg
caption: The skate park, late at night.
bubble: Tika @tr: Someone saw a light that changes colour. Red, then yellow!
bubble: Pip @bl: Spooky! Let's find out how.
dad: Read it like a mystery.

=== talk
layout: hero
box: renders/talk/c2-01-1.jpg
bubble: Pip: Two lights! Someone swaps a red one for a yellow one.
box: renders/talk/c2-01-2.jpg
bubble: Sully: Or it's the SAME light, doing something sneaky.
box: renders/talk/c2-01-3.jpg
bubble: Tika: Our light only ever glowed yellow. How could it go red?
box: renders/talk/c2-01-4.jpg
bubble: Coco: Look closer. It has a tiny + on one end.
dad: Let him guess Pip's way and Sully's way before Coco. Both are fair
    guesses. Lift the egg and hunt for the + on the real D10: it is at the
    top, on 3C.
reason: D10 is two LEDs in anti-parallel, so direction decides the colour.

=== talk
layout: zigzag
box: renders/talk/c2-02-1.jpg
bubble: Coco: Picture a flap in a tube. Water opens it one way only.
box: renders/talk/c2-02-2.jpg
bubble: Pip: Push the other way and the flap slams shut!
box: renders/talk/c2-02-3.jpg
bubble: Tika: This block has TWO flaps, back to back.
box: renders/talk/c2-02-4.jpg
bubble: Sully: One flap shines red. The other shines yellow.
dad: Hold the real D10 and find the +. The flaps are the picture, not
    something he can see inside.
reason: Each LED is a one-way valve. They face opposite ways, so one
    direction lights red and the other lights yellow.

=== talk
layout: cinema
box: renders/talk/c2-03-1.jpg
bubble: Pip: Turn it around and I bet it breaks.
box: renders/talk/c2-03-2.jpg
bubble: Sully: Or it goes dark. Like a Gate that shut.
box: renders/talk/c2-03-3.jpg
bubble: Tika: Or the OTHER flap gets the water.
box: renders/talk/c2-03-4.jpg
bubble: Coco: Three guesses. Pick one. Then we turn it and see.
dad: He picks out loud here. The next page is the same guess, written down,
    and then the real flip. Don't flip it yet.
reason: Turning the LED reverses which of the two diodes is forward-biased.

=== predict
pose: tika-ask
bubble: Tika: Guess first! Then test.
ask: Turn the light around. What colour now?
test: S1=on, flip=4
look: D10
choices: Red=red | Yellow=yellow | Dark=off
answer: Red
reveal: Pip: RED! It changed!
dad: Ian picks out loud. The next page is the real turn.

=== change colours
pose: coco-point
bubble: Coco: Lift the egg and the tube ends. Turn the light around.
bubble: Coco: Now the + is at the bottom, on 3E.
dad: Gate OFF. Lift the egg, then the two tube ends on top of D10 (3C and
    3E). Turn D10 so its + snap is on 3E, press the tubes back down, put
    the egg back on. Gate ON.
watch: Where the + goes is the whole case. Check it matches the picture.

=== scene red
pose: pip-cheer
bubble: Pip: RED!
bubble: Sully: Same light. Same circle. A new colour!

=== comic
panel: renders/comic-c2-yellow.jpg
caption: A clue for the case notes.
bubble: Tika @tr: It cares which way round it goes!
bubble: Sully @bl: So THAT is the colour-changing light.
dad: Let him turn it back and forth a few times. Yellow, red, yellow.

=== why
water: base=colours, S1=on
pose: coco-explain
bubble: Coco: D10 has two little flaps inside. Each opens only one way.
bubble: Coco: Water one way opens the red flap. The other way, the yellow one.
dad: Show the wheel colour on the picture, then turn the real one again.
reason: Turned around, current enters the other end, so the red LED is the
    one that conducts.

=== talk
layout: stack
box: renders/talk/c2-04-1.jpg
bubble: Tika: Plus at the bottom. The water goes in the red flap.
box: renders/talk/c2-04-2.jpg
bubble: Pip: Turn it over. Now the plus is at the top!
box: renders/talk/c2-04-3.jpg
bubble: Coco: Same water. Same circle. It hits the yellow flap instead.
box: renders/talk/c2-04-4.jpg
bubble: Sully: The block didn't change. The WAY the water hits it did.
dad: Flip the real one once more while he says "red flap" and "yellow flap."
reason: Direction selects which LED conducts. The part is the same object
    either way; only the current's direction changed.

=== comic
panel: renders/comic-c2-lantern.jpg
bubble: Sully @tr: Colours at the skate park!
bubble: Tika @bl: Case 2 is nearly closed.
dad: Dim the room. Red, then turn it for yellow. Leave it on red for Case 3.

=== puzzle
pose: tika-ask
bubble: Tika: Find the + on each board.
ask: Red, yellow, or dark?
boards: c2-a, c2-b, c2-c
look: D10
choices: Red=red | Yellow=yellow | Dark=off
answer: c2-a=Yellow, c2-b=Red, c2-c=Dark
stars: 2
dad: Water comes in at the bottom (3E), and only when the Gate says ON.
    + at the bottom: red. + at the top: yellow. Board C says OFF, so it
    stays dark.
watch: The pictures are zoomed in on the Gate and D10 so the + and the
    word ON or OFF are big enough to see.

=== rule
rule: Some parts care which way round.
pose: tika-write
bubble: Tika: Rule 2!
dad: Ask which parts care so far (D10) and which don't (the Gate, the tubes).

=== badge
bubble: Coco: Case 2 closed. Colour Detective!
dad: Print the badge if he wants it.

=== comic
panel: renders/comic-c2-cliff.jpg
caption: Next time...
bubble: Sully @tr: How will the skaters know when to GO?
dad: Leave the board built.

## Chapter 3 -- The Silent Horn
badge: Sound Sleuth

=== splash
art: renders/comic-c3-splash.jpg
say: Case 3: The Silent Horn.
dad: Start from the Case 2 board. The horn is loud: short presses.
reason: Two ideas: a press switch is only on while you hold it, and a horn
    only works one way round.

=== comic
panel: renders/comic-c3-press.jpg
caption: The start line.
bubble: Pip @tr: I built a start horn! I press and press...
bubble: Sully @bl: ...and nothing. Not a peep.
dad: Ask Ian for ideas. What could be wrong?

=== talk
layout: hero
box: renders/talk/c3-01-1.jpg
bubble: Sully: Maybe the horn is just broken.
box: renders/talk/c3-01-2.jpg
bubble: Pip: I pressed it a hundred times. Still nothing!
box: renders/talk/c3-01-3.jpg
bubble: Tika: Detectives don't say broken yet. We hunt for clues.
box: renders/talk/c3-01-4.jpg
bubble: Coco: Two clues. The button, and which way the horn sits.
dad: Let him guess. Don't cross any guess out. Coco then names the two
    clues: the button, and which way the horn sits.
reason: Two independent causes: the momentary switch, and the horn's
    polarity. The case separates them on purpose.

=== meet S2
pose: coco-point
bubble: Coco: Really, this is a button. A switch you have to keep holding.
bubble: Coco: In the picture, a gate that springs shut when you let go.
dad: Let him press the real one. It springs back up.

=== meet W1
pose: coco-point
bubble: Coco: Really, this is a horn. A buzzer.
bubble: Coco: The water shakes a tiny drum inside. That shake is the honk.
dad: Find the + mark on W1 together.

=== talk
layout: zigzag
box: renders/talk/c3-02-1.jpg
bubble: Coco: The Slide Gate stays where you leave it.
box: renders/talk/c3-02-2.jpg
bubble: Pip: This button pops back up. It's a spring!
box: renders/talk/c3-02-3.jpg
bubble: Tika: The tube is open only while your finger holds it down.
box: renders/talk/c3-02-4.jpg
bubble: Sully: And the horn has a plus, like the colour light did.
dad: He presses S2 and lets go a few times, feeling it pop back up, before
    it goes on the board.
reason: S1 is a maintained switch. S2 is momentary. W1 is a polarized load.

=== change horn
pose: coco-point
bubble: Coco: The + goes on 3E. That is the bottom snap, on the blue tube.
dad: Gate OFF. Take the egg off. Swap S1 for S2 (1C to 1E), and D10 for W1
    with its + at 3E, like the picture. Row E, column 3. That is the way
    that honks.

=== scene silent
pose: pip-cheer
bubble: Pip: HONK! The + on 3E works!
bubble: Sully: Hold the button. Let go, and it stops.
watch: If it is silent, the + is on the other end. Turn W1 so the + snap
    is on 3E and try again.

=== comic
panel: renders/comic-c3-clue.jpg
caption: The detectives look closer.
bubble: Tika @tr: Clue! Look at the + mark.
bubble: Pip @bl: Rule 2! Some parts care which way round!
dad: Let Ian get there first: ask him to say rule 2.

=== talk
layout: cinema
box: renders/talk/c3-03-1.jpg
bubble: Pip: What if I turn the horn around?
box: renders/talk/c3-03-2.jpg
bubble: Tika: The colour light changed when we turned it. This might too.
box: renders/talk/c3-03-3.jpg
bubble: Sully: The plus would leave 3E and sit at the top.
box: renders/talk/c3-03-4.jpg
bubble: Coco: Guess first. Then we turn it and listen.
dad: He says honk or quiet out loud. The + is on 3E right now. Don't turn
    it until the next page.
reason: Same polarity lesson as D10, now with a one-way buzzer instead of
    two LEDs.

=== predict
pose: tika-ask
bubble: Tika: Guess first!
ask: Turn the horn around. Push. Honk or quiet?
test: base=horn, S2=pressed, flip=4
look: W1
choices: Honk=on | Quiet=off
answer: Quiet
reveal: Pip: Quiet! The plus left 3E, and the horn stopped.
dad: Lift the tube ends, turn W1 around, press back, then push S2.

=== change horn-fixed
pose: coco-point
bubble: Coco: Turn it back. The + sits on 3E again.
dad: + on 3E, the bottom snap, on the blue tube. That is the honking way.

=== scene honk
pose: pip-cheer
bubble: Pip: HONK! HONK!
bubble: Sully: Starter game! One honk is ready. Two honks is GO!
dad: Play it: Ian honks once (ready), twice (go), and a toy "skates".

=== comic
panel: renders/comic-c3-honk.jpg
bubble: Sully @tr: Two honks! GO!
dad: Ian is the starter now.

=== comic
panel: renders/real-c3.jpg
caption: The real board.
bubble: Coco @tr: Yours should look like this.
bubble: Tika @br: The + is on 3E, on the bottom tube.
dad: Compare snaps, not the plastic edges. Button: 1C to 1E. The bottom
    tube is on row E. The horn's + snap is 3E, its other snap 3C.

=== why
water: base=horn, S2=pressed, flip=4
pose: coco-explain
bubble: Coco: Backwards, the horn's flap stays shut. No water gets through.
bubble: Coco: No water anywhere, so no sound.
dad: Point at the shut flap on the picture.
reason: W1 only conducts one way, like a one-way valve.

=== talk
layout: stack
box: renders/talk/c3-04-1.jpg
bubble: Coco: Backwards, the flap stays shut. No water gets through the horn.
box: renders/talk/c3-04-2.jpg
bubble: Pip: The horn is quiet. The rest of the water can still move!
box: renders/talk/c3-04-3.jpg
bubble: Tika: No. The horn sits IN the circle, just like the wheel did.
box: renders/talk/c3-04-4.jpg
bubble: Sully: Shut flap. Hole in the circle. The water stops everywhere.
dad: Ask which Case 1 rule this is. A gap stops the whole loop.
reason: A reversed buzzer is an open circuit, same as a missing wire. One
    loop, one path.

=== predict
pose: tika-ask
bubble: Tika: Now let go of the button.
ask: Honk or quiet?
test: base=horn-fixed, S2=released
look: W1
choices: Honk=on | Quiet=off
answer: Quiet
reveal: Coco: The Button Gate only opens while you push. The Slide Gate stays put.
dad: Compare: S1 stays where you leave it; S2 springs back. Doorbells and game
    buttons are press switches.

=== talk
layout: strip
box: renders/talk/c3-05-1.jpg
bubble: Sully: I already pressed it. Why did the honk stop?
box: renders/talk/c3-05-2.jpg
bubble: Coco: The button is a spring. Let go, and it shuts the tube.
box: renders/talk/c3-05-3.jpg
bubble: Pip: The Slide Gate has no spring. It stays where I put it!
box: renders/talk/c3-05-4.jpg
bubble: Tika: Doorbells do this. Push, it rings. Let go, it stops.
dad: Press and let go a few more times. Then ask where else he has used a
    button like this: a doorbell, a game controller, a keyboard.
reason: A momentary switch is closed only while actuated. The slide switch
    latches.

=== puzzle
pose: tika-ask
bubble: Tika: Check the button and the + on each board.
ask: Honk or quiet?
boards: c3-a, c3-b, c3-c
look: W1
choices: Honk=on | Quiet=off
answer: c3-a=Quiet, c3-b=Quiet, c3-c=Honk
stars: 2
dad: A pushed button has an orange arrow. The + end shows which way the horn
    sits. Board B has the + at the top, so it stays quiet. The honking way
    is + on 3E.

=== rule
rule: The button gate only opens while you push.
pose: tika-write
bubble: Tika: Rule 3!
dad: Rule 2 solved the mystery; rule 3 is the new one.

=== badge
bubble: Coco: Case 3 closed. Sound Sleuth!
dad: Print the badge if he wants it.

=== comic
panel: renders/comic-c3-cliff.jpg
caption: After the race...
bubble: Sully @tr: The show needs TWO lights at once. Red AND white!
dad: Leave the board built.

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

## Chapter 5 -- The Big Night
badge: Junior Spark Detective

=== splash
art: renders/comic-c5-splash.jpg
say: Case 5: The Big Night.
dad: No step pages tonight. Put all the Beginner parts out, plus one blue
    wire from the Jr box; Ian picks.
reason: Every rule so far, used on his own, plus the detective method: guess,
    then test.

=== comic
panel: renders/comic-c5-missions.jpg
bubble: Coco @tr: Tonight YOU are the detective, Ian.
bubble: Tika @bl: Solve each mission card. Guess, build, test!
dad: Three missions tonight. Most have more than one right answer. The
    answer page shows one that works.

=== talk
layout: stack
box: renders/talk/c5-01-1.jpg
bubble: Coco: A mission says what the board should DO. Not which blocks.
box: renders/talk/c5-01-2.jpg
bubble: Pip: So I can build it my own way?
box: renders/talk/c5-01-3.jpg
bubble: Tika: If it does the job, it counts. Then we test it.
box: renders/talk/c5-01-4.jpg
bubble: Sully: Guess. Build. Switch it on. Were you right?
dad: Read the first mission, let him say which old rule it uses, then he
    builds. You are not the instruction page tonight.
reason: Transfer: he has to choose the part and the direction without a
    step list. Several builds can satisfy one claim.

=== mission yellow-gate
pose: tika-ask
bubble: Tika: Mission 1. You know this one!
card: Make a YELLOW light that the Slide Gate turns on and off.
stars: 1
dad: He builds it, tests it, then you click to see one answer.
watch: If it comes out red, the + is on the wrong end. Yellow wants the +
    at the top, on 3C.

=== comic
panel: renders/real-c5-yellow.jpg
caption: The real board.
bubble: Coco @tr: Yours should look like this.
bubble: Tika @br: Yellow ball. Slide gate on. + up top.
dad: The egg is the big ball. D10's + snap is the top one (3C). The bottom
    tube sits on row E.

=== mission red-button
pose: tika-ask
bubble: Tika: Mission 2. Two changes!
card: Make a RED light that only shines while you push the button.
stars: 2
dad: S2 goes in the Gate's spot, 1C to 1E. D10 turns the red way round, +
    on 3E.

=== comic
panel: renders/real-c5-red.jpg
caption: The real board.
bubble: Coco @tr: Press and hold. Red ball.
bubble: Tika @br: Button gate. + on the bottom tube.
dad: Compare snaps, not the plastic edges. The + snap is 3E, on the bottom
    tube. The light is red only while the button is down.

=== mission both-lights
pose: coco-goggles
bubble: Coco: Mission 3. Two lights. One slide gate.
card: Make the red light AND the white light shine with the Slide Gate.
stars: 3
dad: Same board as Case 4: D10 + on 3E, the white light on 5C-5E, a tube
    3E-5E and a tube 3C-5C on top. Five tubes, so one comes from the Jr box.

=== comic
panel: renders/real-c4-on.jpg
caption: The real board.
bubble: Coco @tr: Yours should look like this.
bubble: Tika @br: Two tubes out to the white light. Gate ON.
dad: Compare snaps. The two new tubes snap on top at 3E and 3C and reach
    the white light at 5E and 5C.

=== talk
layout: strip
box: renders/talk/c5-02-1.jpg
bubble: Tika: Mission 1. Yellow light. The slide gate.
box: renders/talk/c5-02-2.jpg
bubble: Coco: Mission 2. Red light, only while you push.
box: renders/talk/c5-02-3.jpg
bubble: Pip: Mission 3. The red light and the white light together.
box: renders/talk/c5-02-4.jpg
bubble: Sully: Three missions. Then the show.
dad: Three missions, then he puts the show on. You are not the instruction
    page.
reason: Each mission reuses a rule he already has. The third one is the
    split: one gate, two paths, two lights.

=== comic
panel: renders/comic-c5-show.jpg
caption: The Big Night Skate Show.
bubble: Sully @tr: Lights! Colours! Horn!
bubble: Pip @bl: Ian, you made the whole show work!
dad: Put on the show: D10 yellow, then red, then the horn, then the red and
    white lights together. Ian says which rule each one uses.

=== rule
rule: Guess first. Then test it.
pose: tika-write
bubble: Tika: Rule 5. The detective rule!
dad: Read all five rules together.

=== badge
bubble: Coco: All five cases closed. Junior Spark Detective!
bubble: Pip: Print it! Print it!
dad: The big badge. Worth printing.

=== comic
panel: renders/comic-c5-cliff.jpg
caption: Chapter 1 complete!
bubble: Pip @tr: Chapter 1 complete!
bubble: Tika @bl: Five cases. One loop. Two lights.
dad: Module 1 is done. The flying saucer is Module 2, when you want it.
