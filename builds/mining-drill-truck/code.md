# Code -- Mining Drill Truck

SPIKE App, **Word Blocks** (per brief).

## Ports

| Port | Device | Role |
|---|---|---|
| A | Large Motor (left) | Drives the left rear wheel |
| B | Large Motor (right) | Drives the right rear wheel |
| C | Small Angular Motor | Spins the drill bit |
| D | Distance Sensor | Watches what's in front of the drill |

Skid steer: the truck has no shared rear axle, so both drive motors must run
together at the same speed and direction to go straight. Running them at
different speeds (or opposite directions) is how a future version could
turn -- out of scope for this build, but worth mentioning to Ian.

## Success

Digger rolls forward on its own. When something gets within about **4
inches (10 cm)** of its nose, the drill spins up and the hub's face flips
from a smiley to a focused/determined face. Back the object away and the
drill stops -- smiley face comes back.

## Program notes

```
On start:
  hub light matrix -> show "smiley" icon

Forever:
  motor A -> run forward at 40% power        (left rear wheel)
  motor B -> run forward at 40% power        (right rear wheel, same speed)
  if distance sensor (port D) < N inches:
    motor C -> run at high speed              (drill spins)
    hub light matrix -> show "focused" icon
  else:
    motor C -> stop
    hub light matrix -> show "smiley" icon
```

- **N** is a variable, not a hard-coded number -- start at **4 in / 10 cm**,
  then let Ian experiment: does the drill wait longer to start if N is
  bigger? Does it never stop if N is too big?
- Motors A and B never stop in this version -- Digger just keeps rolling
  forward the whole time. (A future version could add a bumper/stop
  condition, or split A and B's speeds to turn.)
- Word Blocks only for this brief; Icon Blocks would work too if Ian wants
  an even simpler pass with no typed numbers.
