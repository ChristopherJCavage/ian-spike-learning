# The Night Skate Cases

The Spark Detectives, Module 1. Snap Circuits Beginner box (SCB-20) only.
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
    the picture. Point at the real battery holder, a wire, and the lamp as
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
reason: B3B holds 3 AA batteries: 4 1/2 volts. That number comes back in
    Case 2's Number Lab.

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

=== meet L4
pose: coco-point
bubble: Coco: Really, this is a light bulb.
bubble: Coco: In the picture it's a wheel. Squeezing past is what makes it glow.
dad: The lamp has no right or wrong way round. Remember that for Case 2.

=== step 1
pose: sully-notice
bubble: Sully: Numbers go across. Letters go down. 1A is the corner.

=== step 2
pose: coco-point
bubble: Coco: The holder hangs off the top. Its snaps land on 1A and 3A.

=== step 3
pose: coco-point
bubble: Coco: Switch snaps on 1C and 1D. Slide it to OFF.

=== step 4
pose: pip-cheer
bubble: Pip: The Glow Wheel! I can't wait to see it light!

=== step 5
pose: coco-point
bubble: Coco: This blue tube runs from 1A down to 1C.

=== step 6
pose: coco-point
bubble: Coco: This blue tube runs from 1D across to 3D.

=== step 7
pose: tika-ask
bubble: Tika: Last tube, 3C up to 3A. Trace the circle with your finger.

=== step 8
pose: coco-point
bubble: Coco: Press the white ball onto the yellow lamp. That is the bulb.

=== comic
panel: renders/comic-c1-real.jpg
caption: The real board.
bubble: Coco @tr: Yours should look like this. Batteries hang off the top.
bubble: Tika @bl: The white ball is the bulb. It snaps on the yellow lamp.
dad: Compare snaps, not the edges of the plastic. Switch snaps are 1C and
    1D. Blue tubes are 1A-1C, 1D-3D, and 3A-3C. The egg is on the lamp for
    this whole case. In Case 2, lift it off when you want to see the LED.
reason: The holder is taller than a grid row, so it has to overhang. S1 is
    a 2-snap part: one grid step, 1C to 1D. The green board is longer than
    those two snaps.

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
look: L4
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
look: L4
choices: Light=on | Dark=off
answer: Dark
reveal: Coco: Dark again. A missing tube is a gap too.
dad: Gate ON first. Ian pulls the tube from 1D to 3D, then presses it back
    after the reveal.

=== predict
pose: sully-puzzled
bubble: Sully: Maybe ONE tube doesn't matter?
ask: Which tube can you take out and keep the light on?
fact: keeps-on L4 @ S1=on
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
look: L4
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
box: pip-oops
bubble: Pip: Two lights! Someone swaps a red one for a yellow one.
box: sully-notice
bubble: Sully: Or it's the SAME light, doing something sneaky.
box: tika-ask
bubble: Tika: The old wheel glowed either way. What's different here?
box: coco-point
bubble: Coco: This one has a tiny +. The lamp never had that.
dad: Let him guess Pip's way and Sully's way before Coco. Both are fair
    guesses. The + is the clue to hunt on the real block.
reason: The lamp is non-polar. D10 is two LEDs in anti-parallel, so direction
    decides the colour.

=== meet D10
pose: pip-magnify
bubble: Pip: Really, this is an LED. A tiny light that cares which way.
bubble: Pip: It has a little + on one end. That's the clue!
dad: Help Ian find the + mark on the real D10.
reason: An LED only lets current through one way. D10 has two inside, back
    to back: one red, one yellow.

=== talk
layout: zigzag
box: coco-explain
bubble: Coco: Picture a flap in a tube. Water opens it one way only.
box: pip-magnify
bubble: Pip: Push the other way and the flap slams shut!
box: tika-write
bubble: Tika: This block has TWO flaps, back to back.
box: sully-notice
bubble: Sully: One flap shines red. The other shines yellow.
dad: Hold the real D10 and find the +. The flaps are the picture, not
    something he can see inside.
reason: Each LED is a one-way valve. They face opposite ways, so one
    direction lights red and the other lights yellow.

=== change colours
pose: coco-point
bubble: Coco: Lift the tube ends off the Glow Wheel. Swap in D10.
bubble: Coco: The + goes at the bottom, like the picture.
dad: Gate OFF. Lift the egg off the lamp so the LED is bare. Lift the ends of
    the two tubes on top of L4 (at 3C and 3D), swap L4 for D10 with its + at
    3D, press the tubes back down.
watch: Where the + goes is the whole case. Check it matches the picture.

=== scene red
pose: pip-cheer
bubble: Pip: RED!

=== talk
layout: cinema
box: pip-oops
bubble: Pip: Turn it around and I bet it breaks.
box: sully-puzzled
bubble: Sully: Or it goes dark. Like a Gate that shut.
box: tika-ask
bubble: Tika: Or the OTHER flap gets the water.
box: coco-explain
bubble: Coco: Three guesses. Pick one. Then we turn it and see.
dad: He picks out loud here. The next page is the same guess, written down,
    and then the real flip. Don't flip it yet.
reason: Turning the LED reverses which of the two diodes is forward-biased.

=== predict
pose: tika-ask
bubble: Tika: Guess first! Then test.
ask: Turn D10 around. What colour now?
test: base=colours, S1=on, flip=4
look: D10
choices: Red=red | Yellow=yellow | Dark=off
answer: Yellow
reveal: Pip: YELLOW! It changed!
dad: Gate OFF, lift the tube ends, turn D10 around, press back, Gate ON.

=== comic
panel: renders/comic-c2-yellow.jpg
caption: A clue for the case notes.
bubble: Tika @tr: It cares which way round it goes!
bubble: Sully @bl: So THAT is the colour-changing light.
dad: Let him flip it back and forth a few times. Red, yellow, red.

=== why
water: base=colours, S1=on, flip=4
pose: coco-explain
bubble: Coco: D10 has two little flaps inside. Each opens only one way.
bubble: Coco: Water one way opens the red flap. The other way, the yellow one.
dad: Show the wheel colour on the picture, then flip the real one again.
reason: Turned around, current enters the other end, so the yellow LED is the
    one that conducts.

=== talk
layout: stack
box: tika-write
bubble: Tika: Plus at the bottom. The water goes in the red flap.
box: pip-cheer
bubble: Pip: Turn it over. Now the plus is at the top!
box: coco-explain
bubble: Coco: Same water. Same circle. It hits the yellow flap instead.
box: sully-notice
bubble: Sully: The block didn't change. The WAY the water hits it did.
dad: Flip the real one once more while he says "red flap" and "yellow flap."
reason: Direction selects which LED conducts. The part is the same object
    either way; only the current's direction changed.

=== change lantern
pose: coco-point
bubble: Coco: Now the egg goes on top. Red side, please!
dad: Turn D10 back to red (+ at the bottom) and set the egg on it.

=== scene lantern
pose: pip-cheer
bubble: Pip: A party lantern! The show will love it.
dad: Dim the room for this one.

=== comic
panel: renders/comic-c2-lantern.jpg
bubble: Sully @tr: Colours at the skate park!
bubble: Tika @bl: Case 2 is nearly closed.
dad: Ian can try the egg on the yellow side too.

=== puzzle
pose: tika-ask
bubble: Tika: Find the + on each board.
ask: Red, yellow, or dark?
boards: c2-a, c2-b, c2-c
look: D10
choices: Red=red | Yellow=yellow | Dark=off
answer: c2-a=Yellow, c2-b=Red, c2-c=Dark
stars: 2
dad: + at the bottom (3D) means red. At the top means yellow. Board C has the
    Gate off.
watch: If he only looks at the block's colour, point to the little + circle.

=== numberlab
pose: tika-write
bubble: Tika: It starts red. Every flip changes the colour.
ask: Flip it 3 times. Red or yellow?
fact: flip-colour 3 of 4 @ base=colours, S1=on
answer: yellow
stars: 1
dad: He can flip the real one 3 times to check.

=== talk
layout: strip
box: pip-oops
bubble: Pip: Ten flips? I'll lose count and fall over.
box: tika-write
bubble: Tika: Start red. One flip makes yellow. Two flips, red again.
box: coco-explain
bubble: Coco: Odd flips land on yellow. Even flips come back to red.
box: sully-notice
bubble: Sully: Don't flip ten times. Ask: is ten odd, or even?
dad: Walk 1, 2, 3 on the real block if the pattern isn't sticking. Then he
    answers ten on the next page without flipping.
watch: If he wants to flip all ten, let him. Then show that even and odd
    would have saved the work.
reason: An even number of reversals returns to the start. Parity, not a
    long count.

=== numberlab
pose: tika-write
bubble: Tika: 10 flips is a lot. Find the pattern instead!
ask: Flip it 10 times. Red or yellow?
fact: flip-colour 10 of 4 @ base=colours, S1=on
answer: red
stars: 2
dad: Write 1, 2, 3, 4... with the colour under each. Red comes back on every
    even number.
reason: An even number of flips lands back where you started.

=== numberlab
pose: sully-puzzled
bubble: Sully: 25 flips would take me all day.
ask: Flip it 25 times. Red or yellow?
fact: flip-colour 25 of 4 @ base=colours, S1=on
answer: yellow
stars: 3
dad: 25 is odd. If he can say why that settles it, he has the idea.

=== talk
layout: wide
box: coco-explain
bubble: Coco: One battery pushes one and a half. Like one and a half steps.
box: pip-magnify
bubble: Pip: Two batteries. One and a half, plus one and a half.
box: tika-write
bubble: Tika: Two wholes make 2. Two halves make one more. That's 3.
box: sully-puzzled
bubble: Sully: OUR pump holds three batteries. That's another half to add!
dad: Use three half-dollars, or draw three "1 1/2"s. He adds them on the
    next page. Don't say four and a half yet.
reason: Cells in series add their voltages. 3 times 1.5 V is 4.5 V.

=== numberlab
pose: tika-write
bubble: Tika: Each battery pushes 1 1/2. The Pump holds 3.
ask: 1 1/2 + 1 1/2 + 1 1/2 = ?
fact: volts
answer: 4 1/2
stars: 2
dad: The wholes make 3; three halves make 1 1/2 more. Three half-dollars help.
reason: Volts measure how hard the pump pushes. Batteries in a row add up:
    3 x 1.5 V = 4.5 V.

=== rule
rule: Some parts care which way round.
pose: tika-write
bubble: Tika: Rule 2!
dad: Ask which parts care so far (D10) and which don't (the lamp, the Gate).

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
box: sully-puzzled
bubble: Sully: Maybe the horn is just broken.
box: pip-oops
bubble: Pip: I pressed it a hundred times. Still nothing!
box: tika-ask
bubble: Tika: Detectives don't say broken yet. We hunt for clues.
box: coco-point
bubble: Coco: Two clues. The button, and which way the horn sits.
dad: Collect his ideas first. Write none of them off. Then Coco narrows it
    to the two things this case is about.
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
bubble: Coco: In the picture, the water blows it. LOUD, when it works.
dad: Find the + mark on W1 together.

=== talk
layout: zigzag
box: coco-explain
bubble: Coco: The Slide Gate stays where you leave it.
box: pip-magnify
bubble: Pip: This button pops back up. It's a spring!
box: tika-write
bubble: Tika: The tube is open only while your finger holds it down.
box: sully-notice
bubble: Sully: And the horn has a plus, like the colour light did.
dad: He presses S2 and lets go a few times, feeling the spring, before it
    goes on the board.
reason: S1 is a maintained switch. S2 is momentary. W1 is a polarized load.

=== change horn
pose: pip-oops
bubble: Pip: Copy my board exactly. The + goes at the TOP!
dad: Swap S1 for S2, and D10 for W1 with its + at 3C, like the picture. That
    is Pip's mistake, on purpose.

=== scene silent
pose: sully-puzzled
bubble: Sully: Push... hold... nothing.
bubble: Pip: See? It's broken!
watch: If it honks, your horn's + is marked the other way from ours. Turn it
    so it is silent and carry on.

=== comic
panel: renders/comic-c3-clue.jpg
caption: The detectives look closer.
bubble: Tika @tr: Clue! Look at the + mark.
bubble: Pip @bl: Rule 2! Some parts care which way round!
dad: Let Ian get there first: ask him to say rule 2.

=== talk
layout: cinema
box: pip-oops
bubble: Pip: It's broken. I want a new horn. Can we go skate?
box: tika-ask
bubble: Tika: The colour light looked broken too. What was actually wrong?
box: sully-notice
bubble: Sully: The plus was the wrong way. We turned it around.
box: coco-point
bubble: Coco: Look at Pip's horn. Where did he put the plus?
dad: He should point at the + on the real horn and say "top" before the
    guess. The next page asks honk or quiet. Don't turn it yet.
reason: Same polarity lesson as D10, now with a one-way buzzer instead of
    two LEDs.

=== predict
pose: tika-ask
bubble: Tika: Guess first!
ask: Turn the horn around. Push. Honk or quiet?
test: base=horn, S2=pressed, flip=4
look: W1
choices: Honk=on | Quiet=off
answer: Honk
reveal: Pip: HONK! It wasn't broken. It was backwards!
dad: Lift the tube ends, turn W1 around, press back, then push S2.

=== change horn-fixed
pose: coco-point
bubble: Coco: + at the bottom now, like the picture.
dad: This page just shows the fixed board.

=== scene honk
pose: pip-cheer
bubble: Pip: HONK! HONK!
bubble: Sully: Starter game! One honk is ready. Two honks is GO!
dad: Play it: Ian honks once (ready), twice (go), and a toy "skates".

=== comic
panel: renders/comic-c3-honk.jpg
bubble: Sully @tr: Two honks! GO!
dad: Ian is the starter now.

=== why
water: base=horn, S2=pressed
pose: coco-explain
bubble: Coco: Backwards, the horn's flap stays shut. No water gets through.
bubble: Coco: No water anywhere, so no sound.
dad: Point at the shut flap on the picture.
reason: W1 only conducts one way, like a one-way valve.

=== talk
layout: stack
box: coco-explain
bubble: Coco: Backwards, the flap stays shut. No water gets through the horn.
box: pip-magnify
bubble: Pip: The horn is quiet. The rest of the water can still move!
box: tika-ask
bubble: Tika: No. The horn sits IN the circle, just like the wheel did.
box: sully-notice
bubble: Sully: Shut flap. Hole in the circle. The water stops everywhere.
dad: Ask him which Case 1 rule this is. (A gap stops the whole loop.)
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
box: sully-puzzled
bubble: Sully: I already pressed it. Why did the honk stop?
box: coco-explain
bubble: Coco: The button is a spring. Let go, and it shuts the tube.
box: pip-cheer
bubble: Pip: The Slide Gate has no spring. It stays where I put it!
box: tika-write
bubble: Tika: Doorbells do this. Push, it rings. Let go, it stops.
dad: Press and release a few more times. Then ask where else he has used a
    button like this (doorbell, game controller, keyboard).
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
dad: A pushed button has an orange arrow on it. Board B is Pip's backwards horn.

=== numberlab
pose: tika-write
bubble: Tika: Honk the answer! A grown-up says the sum.
ask: 6 + 7. Honk it!
fact: calc 6 + 7
answer: 13
stars: 1
dad: Say "6 plus 7". Ian honks 13 short honks while you both count.

=== numberlab
pose: tika-write
bubble: Tika: Three groups of 4 honks. Pause between groups.
ask: How many honks in 3 groups of 4?
fact: calc 3 x 4
answer: 12
stars: 2
dad: Honk-honk-honk-honk, pause, three times. Multiplication you can hear.
reason: Equal groups is what 3 x 4 means.

=== numberlab
pose: sully-notice
bubble: Sully: Count by 2s up to 20. One honk for each number.
ask: 2, 4, 6... up to 20. How many honks?
fact: calc 20 / 2
answer: 10
stars: 3
dad: He says the numbers and honks on each; you count the honks.

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
bubble: Sully @tr: Skating is HOT work. Phew!
dad: Leave the board built.

## Chapter 4 -- The Backwards Fan
badge: Wind Watcher

=== splash
art: renders/comic-c4-splash.jpg
say: Case 4: The Backwards Fan.
dad: Start from the Case 3 board. This case has a spinning fan: faces back,
    fingers off it while it spins.
reason: Motors care which way round too: turn one around and it spins the
    other way.

=== comic
panel: renders/comic-c4-hot.jpg
bubble: Sully @tr: I'm so hot. And my fan blows the wrong way!
bubble: Coco @bl: Let's build one and investigate.
dad: Read it, then on to the parts.

=== talk
layout: wide
box: sully-skate
bubble: Sully: The wind hits the wall. I want it on my face!
box: pip-oops
bubble: Pip: Easy. Turn the whole board around!
box: tika-ask
bubble: Tika: Then every tube falls off. Not a great plan.
box: coco-explain
bubble: Coco: Turn just the motor. Let's see what the spin does.
dad: Laugh at Pip's plan, then ask why the tubes would fall off. The real
    move (turning one block) comes after they meet the motor.
reason: Reversing the motor reverses the fan. Turning the whole board would
    also reverse the wind, but it isn't a circuit change.

=== meet M7
pose: coco-goggles
bubble: Coco: Really, this is a motor. It turns the push into spinning.
bubble: Coco: In the picture, a wheel. This one lights up too.
dad: Find the + mark on M7 together.

=== meet fan7
pose: coco-goggles
bubble: Coco: Really, this is a fan. The motor is what spins it.
bubble: Coco: Never touch it while it spins!
dad: The fan presses onto the motor's shaft. Faces back from it.

=== change spinner
pose: coco-point
bubble: Coco: Slide Gate back in. Glow Spinner in the wheel spot, + at the bottom.
bubble: Coco: Then press the fan on top.
dad: Swap S2 back to S1 (OFF). Swap W1 for M7 with its + at 3D. Press the
    fan on. Faces back.

=== scene spin
pose: pip-cheer
bubble: Pip: It spins AND glows!
bubble: Sully: Hold your hand above it. Which way is the wind going?
dad: Ian holds a flat hand a little above the fan, never touching. Up, or
    down? Remember the answer for after the next page.

=== talk
layout: hero
box: tika-write
bubble: Tika: Clock hands go this way. We call that clockwise.
box: pip-cheer
bubble: Pip: From 12, over to 3, down to 6, and back up to 9.
box: sully-notice
bubble: Sully: The other way is counterclockwise. 12, then 9, then 6.
box: coco-goggles
bubble: Coco: Watch our fan. Which of those two is it doing?
dad: Use a real clock if you have one. He names the way it spins NOW, before
    anyone turns the motor around.
watch: A spinning fan is hard to read. A sticker on one blade helps.
reason: "Clockwise" needs a reference. With the + at the bottom, this motor
    is defined as forward, which we are calling clockwise. Unmeasured on the
    real box: preflight checks it.

=== predict
pose: tika-ask
bubble: Tika: Clock hands go clockwise. Which way will it spin, turned around?
ask: Turn the Glow Spinner around. Which way does it spin?
test: base=spinner, S1=on, flip=4
look: M7
choices: Clockwise=fwd | Counterclockwise=rev | Still=off
answer: Counterclockwise
reveal: Pip: The other way! And the wind goes the other way too!
dad: Gate OFF. Take the fan off, lift the tube ends, turn M7 around, put it
    all back, Gate ON. Hand above again: the wind has flipped.
watch: A spinning fan is hard to read. Watch the arrow on the board picture,
    or put a small sticker on one blade.

=== comic
panel: renders/comic-c4-wind.jpg
bubble: Sully @tr: Ahhh. Wind on my face!
bubble: Tika @bl: The fan wasn't broken. It was backwards!
dad: Ask what Case 4 has in common with Case 3. (Both "broken" parts were
    just the wrong way round.)

=== why
water: base=spinner, S1=on, flip=4
pose: coco-explain
bubble: Coco: Now the water hits the wheel from the other side.
bubble: Coco: So the wheel spins the other way.
dad: Compare with the Case 1 picture: same loop, the wheel just turns the
    other way.
reason: Reverse the current through a motor and it turns the other way. The
    blade then pushes air the other way.

=== talk
layout: zigzag
box: coco-explain
bubble: Coco: Same water. Same circle. It hits the wheel from the other side.
box: pip-magnify
bubble: Pip: Push a wheel on the left, it spins one way. On the right, the other.
box: tika-write
bubble: Tika: The blades flip their push too. So the wind turns around.
box: sully-skate
bubble: Sully: The fan wasn't broken. The motor was backwards!
dad: Ask what Case 4 has in common with the horn and the colour light.
    (Turning the part around changed what it did.)
reason: Reverse the current through a DC motor and the torque reverses, so
    the fan's thrust reverses with it.

=== puzzle
pose: tika-ask
bubble: Tika: Look at the + and the Gate.
ask: Which way does each fan spin?
boards: c4-a, c4-b, c4-c
look: M7
choices: Clockwise=fwd | Counterclockwise=rev | Still=off
answer: c4-a=Counterclockwise, c4-b=Still, c4-c=Clockwise
stars: 2
dad: + at the bottom spins clockwise, + at the top counterclockwise. Gate
    off means still.

=== numberlab
pose: sully-notice
bubble: Sully: Clock hands go clockwise. From 12, over to 3, down to 6.
ask: Draw clockwise in the air. Now counterclockwise.
answer: Clockwise goes 12, 3, 6, 9. Counterclockwise goes 12, 9, 6, 3.
stars: 1
dad: Use a real clock if there is one nearby.

=== talk
layout: cinema
box: tika-ask
bubble: Tika: Count the blades on the real fan. Take your time.
box: pip-cheer
bubble: Pip: One, two, three!
box: sully-notice
bubble: Sully: One turn, three blades go past. Two turns, three more.
box: coco-explain
bubble: Coco: That's groups. Turns times blades. The next page is the big one.
dad: Count the real fan together. If it is not 3, stop and tell Chris: the
    blade count lives in tools/snap/parts.json, and the answers change.
reason: Each revolution brings every blade past once, so blades past equals
    turns times blades.

=== numberlab
pose: tika-write
bubble: Tika: The fan has 3 blades. Count them on the real fan!
ask: The fan turns 10 times. How many blades go past?
fact: blades 10 @ base=spinner
answer: 30
stars: 2
dad: Check the real fan has 3 blades. If not, tell Chris: the blade count is
    in tools/snap/parts.json and the answer will change.
reason: 10 turns of 3 blades: 3 x 10 = 30.

=== numberlab
pose: tika-write
bubble: Tika: Super-detective level!
ask: The fan turns 25 times. How many blades go past?
fact: blades 25 @ base=spinner
answer: 75
stars: 3
dad: 25 + 25 + 25, or 3 x 25. Three quarters make 75 cents.

=== rule
rule: Flip the motor, flip the spin.
pose: tika-write
bubble: Tika: Rule 4!
dad: Ask which other parts changed when he turned them around: D10's colour,
    and W1's sound.

=== badge
bubble: Coco: Case 4 closed. Wind Watcher!
dad: Print the badge if he wants it.

=== comic
panel: renders/comic-c4-cliff.jpg
caption: Tomorrow night...
bubble: Tika @tr: The Big Night Skate Show! Can we get it all ready?
dad: Case 5 has no step pages. Ian builds from mission cards.

## Chapter 5 -- The Big Night
badge: Junior Spark Detective

=== splash
art: renders/comic-c5-splash.jpg
say: Case 5: The Big Night.
dad: No step pages tonight. Put all the Beginner parts out; Ian picks.
reason: All four rules, used on his own, plus the detective method: guess,
    then test.

=== comic
panel: renders/comic-c5-missions.jpg
bubble: Coco @tr: Tonight YOU are the detective, Ian.
bubble: Tika @bl: Solve each mission card. Guess, build, test!
dad: Most missions have more than one right answer. The answer page shows
    one that works.

=== talk
layout: stack
box: coco-explain
bubble: Coco: A mission says what the board should DO. Not which blocks.
box: pip-cheer
bubble: Pip: So I can build it my own way?
box: tika-ask
bubble: Tika: If it does the job, it counts. Then we test it.
box: sully-notice
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
watch: If it comes out red, ask which rule helps (rule 2).

=== mission red-button
pose: tika-ask
bubble: Tika: Mission 2. Two swaps!
card: Make a RED light that only shines while you push the button.
stars: 2
dad: It needs S2 in the Gate's spot and D10 the red way round.

=== mission fan-back
pose: coco-goggles
bubble: Coco: Mission 3. Faces back from the fan!
card: Make the fan spin COUNTERCLOCKWISE.
stars: 1
dad: M7 with the fan on, turned so its + is at the top.

=== mission picture
pose: sully-notice
bubble: Sully: Mission 4. No words. Copy the picture!
card: Build this board exactly. Guess: push the button. What colour?
show: board
stars: 2
dad: Building from a picture is the real skill. Then he pushes S2.

=== talk
layout: strip
box: tika-write
bubble: Tika: Four rules in the notebook. Four clues on every board.
box: coco-point
bubble: Coco: Is the circle closed, or is there a hole?
box: pip-magnify
bubble: Pip: Is the button pushed? Is a plus the wrong way round?
box: sully-puzzled
bubble: Sully: One bad clue, and the board does nothing at all.
dad: For the first board, hunt the clues out loud together. Then let him
    do the rest before you click.
reason: Each failing board breaks exactly one of the rules he has. The
    puzzle is sorting which rule, not a new idea.

=== puzzle
pose: tika-ask
bubble: Tika: The big puzzle! Use all four rules.
ask: Will it work, or will nothing happen?
boards: c5-a, c5-b, c5-c, c5-d, c5-e, c5-f
choices: Works=on | Nothing=off
answer: c5-a=Works, c5-b=Nothing, c5-c=Nothing, c5-d=Nothing, c5-e=Works, c5-f=Works
stars: 3
dad: For each board, find the clue: a gap, a button not pushed, or a part the
    wrong way round.

=== talk
layout: wide
box: tika-ask
bubble: Tika: The Gate has two choices. On, or off.
box: pip-oops
bubble: Pip: And the colour light. This way, or turned. That's two more!
box: coco-explain
bubble: Coco: Two times two. Four different ways to set the same board.
box: sully-notice
bubble: Sully: But do all four LOOK different? We should check.
dad: Hold up fingers: two for the Gate, two for the flip. He says "four"
    before the next page. Don't explain the dark rows yet. That surprise
    is the page after the table.
reason: Independent binary choices multiply. Outcomes can collide, which is
    the following page.

=== numberlab
pose: tika-write
bubble: Tika: One board, lots of shows. Let's count them.
ask: D10 on the board. The Gate is on or off. D10 is this way or turned. How
    many ways to set it?
fact: settings S1, flip=4 @ base=colours
answer: 4
stars: 2
dad: Fill in the table together, trying each row on the real board.
reason: 2 choices times 2 choices is 4 ways. Counting by multiplying is where
    probability starts.

=== numberlab
pose: sully-puzzled
bubble: Sully: 4 ways... but do they all LOOK different?
ask: How many different things can you see?
fact: shows S1, flip=4 @ base=colours
answer: 3
stars: 3
dad: In the table, both Gate-off rows are dark. So: red, yellow, dark.
reason: Two settings give the same result. Counting outcomes is not the same
    as counting settings.

=== numberlab
pose: tika-write
bubble: Tika: One more choice: D10 or the Glow Spinner in that spot.
ask: Gate on or off, this way or turned, D10 or Spinner. How many ways?
fact: settings S1, flip=4, swap=4/M7 @ base=colours
answer: 8
stars: 3
dad: 2 x 2 x 2. He can list them all in the table.

=== comic
panel: renders/comic-c5-show.jpg
caption: The Big Night Skate Show.
bubble: Sully @tr: Lights! Colours! Horn! Wind!
bubble: Pip @bl: Ian, you made the whole show work!
dad: Put on the show: lamp, then D10 red and yellow, then the horn start, then
    the fan. Ian says which rule each part uses.

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
caption: Later that night...
bubble: Pip @tr: Look up there! A flying saucer?!
bubble: Tika @bl: A new case... for the Jr box.
dad: That is Module 2, builds/snap-02-flying-saucer, with the Snap Circuits
    Jr. box.
