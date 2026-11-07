# Build: snap-01-the-loop -- The Night Skate Cases

category: circuit
venue: home
hub: none
kits: scb20
skills: closed loop, switch, press switch, polarity, motor direction
coding: none
age-fit: 6
project: snap-electricity
role: main
figma: TBD

The Spark Detectives, Module 1: a long comic in five cases, one sitting
each. Ian builds one loop in Case 1 (battery holder, slide switch, lamp,
three blue wires), and every later case swaps one block into it: the
red/yellow LED and its egg, the press switch and the horn, the glowing motor
and its fan. Case 5 has no step pages: Ian solves mission cards on his own.
Every case has a Number Lab page or two, and the maths comes from the
board he built.

```bash
python3 tools/snap.py check builds/snap-01-the-loop
python3 tools/snap.py render builds/snap-01-the-loop
python3 tools/snap.py preview builds/snap-01-the-loop    # open preview.html
```

`preview.html` is the comic. Click or press space for the next bubble, G
hides the grown-up notes, number keys jump to a case. It remembers where
you stopped.

Status: checker green; **not table-tested**. Which end of D10, W1 and M7 is
"forward", and every block's size, are hypotheses until Chris runs
[`preflight.md`](preflight.md) on the real box.
