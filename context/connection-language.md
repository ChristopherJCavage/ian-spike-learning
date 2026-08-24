# Connection language

How we write `steps.md` so a human can build without CAD, and so step
numbers match `model.ldr` (`0 STEP`).

## Grid

- **System studs:** 8 mm pitch. Bricks are 9.6 mm tall; plates 3.2 mm (1/3 brick).
- **Technic holes:** 8 mm pitch along a beam. Number holes from **1 = an end**.
  Example: `15M beam, hole 1 = free end, hole 8 = middle`.
- **M** means modules of 8 mm on axles and beams (`7M axle`, `9M beam`).

## Fasteners (say which)

- **Pin** -- friction (black) vs bush/axle-pin. "Black pin through beam hole 3
  into motor housing."
- **Axle** -- cross section. "7M axle through Large Motor, then 24T gear, then
  bush."
- **Bush** -- stops an axle sliding. Half-bush vs full bush: say which.
- **Axle pin / pin with axle end** -- when a pin must also take a gear.

## Electronics

- Name the **part** (Small Angular Motor, Color Sensor, ...) then **port**.
  Essential: ports A, B. Prime: A--F.
- Cables: "route under the boom, clip with a wire clip, slack at the hub."
- After attaching a motor: **hand-turn** it before coding. Write a Check line.

## Step template

```
Step 12 -- hoist drum
  Sub: hoist
  Bin: Prime
  Add: 1x black 7M axle | kit 45678
  Do:  Slide axle through Large Motor (port C), then 24-tooth gear, then bush.
       Gear teeth mesh with 12-tooth on the boom (already on Step 10).
  Check: Drum spins when you turn the motor by hand. No scrape on the tower.
```

Rules:

- **Sub** -- named sub-assembly (`base`, `tower`, `boom`, `hoist`, `hook`).
  Same idea as official BI "build the legs, then attach."
- **Bin** -- Essential or Prime tray (home mixed builds).
- **Add** -- qty, color, kid name; kit number. Element ID lives in `parts.txt`.
- **Do** -- one action. Hole numbers and mesh/clutch described in words.
- **Check** -- what Ian should see/feel. Fail = patch this step, not Figma.

## What not to write

- Do not put element IDs on kid Figma screens.
- Do not skip the Check after gears, pulleys, or worm drives.
- Do not invent parts that fail `grep` on `kits/*/parts.txt`.
