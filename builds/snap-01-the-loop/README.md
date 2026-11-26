# Build: snap-01-the-loop -- The Night Skate Cases

category: circuit
venue: home
hub: none
kits: scb20, sc100
skills: closed loop, switch, press switch, polarity, two paths
coding: none
age-fit: 6
project: snap-electricity
role: main
figma: TBD

Published at https://stem.galaxymoose.com/builds/night-skate-cases
CC BY 4.0. Credit Chris Cavage, stem.galaxymoose.com.

The Spark Detectives, Module 1: a long comic in five cases, one sitting
each. Ian builds one loop in Case 1 (battery holder riding the top edge,
slide switch, the red/yellow light D10 with the egg on it, three blue
wires). Case 2 turns D10 around for red; Case 3 swaps in the press switch
and the horn; Case 4 adds the white light L4 on its own path next to the red
one, so one gate runs two lights. Case 5 has no step pages: Ian solves three
mission cards.

**This build needs both boxes:** the Snap Circuits Beginner (SCB-20) for
every block, plus one blue 3-snap wire from Snap Circuits Jr. (SC-100). The
Case 4 two-light board uses five blue wires and the Beginner box has four.

```bash
python3 tools/snap.py check builds/snap-01-the-loop
python3 tools/snap.py render builds/snap-01-the-loop
python3 tools/snap.py preview builds/snap-01-the-loop    # open preview.html
```

`preview.html` is the comic. Click or press space for the next bubble, G
hides the grown-up notes, number keys jump to a case. It remembers where
you stopped.

Status: checker green. Cases 1, 3, 4 and 5 are photo-checked on the real
board (`renders/real-*.jpg`, each described by a `photo` line in
`circuit.snap` that `check` compares with the layout). Block sizes, the
battery holder riding the edge, and which end of D10 and W1 is "forward"
come from those photos. Case 2's red board is the same board as the Case 5
red photo with the slide switch.
