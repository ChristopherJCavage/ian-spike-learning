# Brief -- Mining Drill Truck ("Digger")

Status: **filled**.

## Theme / story

A friendly little mining truck named Digger. It rolls forward, and when it
gets close to a "rock" (anything in front of it), its front drill spins up
to dig through. Cute on purpose: round eyes on the hood, a happy/determined
face on the hub screen, antennae, and a dog riding along.

## Complexity

- Target step count (Figma pages): 18 build steps + 1 code page (19).
- How much help Ian gets vs Chris: Chris pins beams and mounts motors/sensor
  (Steps 1-10); Ian snaps on shells, seat, minifig, eyes, antennae, dog
  (Steps 11-18); code together (Step 19).
- Sub-assemblies: `base` (chassis + wheels), `drive` (two rear motors, skid
  steer -- no shared rear axle), `drill` (front motor + bit), `sensor`
  (distance sensor), `cab` (shells, seat, window, driver), `face` (eyes,
  antennae, dog), `code`.

## Hardware

- Hub: **prime** (needs 4 ports; Essential only has 2)
- Motors: 2x Large Motor -> ports A/B (skid-steer rear drive, one wheel
  each -- the Large Motor's output disc cannot coaxially drive a shared
  rear axle in a truck this size); Small Angular Motor -> port C (drill bit)
- Sensors: Distance Sensor -> port D (front-facing, triggers the drill)
- Done-when: truck rolls forward continuously; when something is within
  about 4 in / 10 cm of the sensor, the drill spins and the hub shows a
  focused face; back away and the drill stops, smiley face comes back.

## Constraints

- Only `kits/45345-essential/parts.txt` and `kits/45678-prime/parts.txt` --
  every `parts.txt` line grepped against both before writing.
- No expansion 45681.
- One hub (Prime).
- Kid screens: Word Blocks (per house rules default; simple enough for a
  6-year-old with an adult reading the blocks aloud).
