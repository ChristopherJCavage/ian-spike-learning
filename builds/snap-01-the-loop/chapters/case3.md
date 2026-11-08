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
