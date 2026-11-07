# Build: snap-02-flying-saucer -- The UFO Case

category: circuit
venue: home
hub: none
kits: sc100
skills: motor, press switch, polarity, thrust, measuring
coding: none
age-fit: 6
project: snap-electricity
role: main
figma: TBD

The Spark Detectives, Module 2: two cases with the Snap Circuits Jr. box.
Someone saw a UFO over the skate park. The detectives build Module 1's loop
again with the Jr pump and motor, hold the button until the fan is fast, let
go, and it flies. In the second case Pip's rebuilt launcher just blows wind:
the motor is in backwards, so the fan pushes air the other way. Number Lab
is a real flight log: measure five flights in inches, graph them, compare.

Do Module 1 first (`builds/snap-01-the-loop`).

```bash
python3 tools/snap.py check builds/snap-02-flying-saucer
python3 tools/snap.py render builds/snap-02-flying-saucer
python3 tools/snap.py preview builds/snap-02-flying-saucer    # open preview.html
```

Status: checker green; **not table-tested, and the Jr box is not yet
inventoried**. Which way M1 must spin for the fan to fly (`lift fwd` in
`circuit.snap`) is a guess until Chris runs [`preflight.md`](preflight.md).
