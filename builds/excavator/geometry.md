# Geometry -- Excavator ("Scoop")

Measured, not guessed. Every number here came out of
`python3 tools/ldrcheck.py measure <part>` or `holes <part>`.

## World

- `+Y is DOWN`. Front is `+Z`. Ground plane `y = +80`.
- Wheel axles at `y = 10`, wheel radius 70, so tread meets `y = 80`.

## The parts this build stands on

| part | LDraw | size (x,y,z) | the number that mattered |
|---|---|---|---|
| Prime Hub | `45601` | 140 x 80 x 220 | bottom face is local `y=0`, top is `y=-80` |
| Large Motor | `54675` | 100 x 80 x 180 | output bore local `(0,-50,0)` along local Y |
| Medium Angular Motor | `54696p01` | 60 x 80 x 179 | same bore; body is 150 long on ONE side of it |
| Force Sensor | `37312` | 60 x 59 x 120 | button end at local `z=-70` |
| Wheel dia.56 | `39367` | radius 70, 35 thick | |
| 5M beam | `32316` | 18 x 20 x 98 | 5 holes at 20 pitch |
| 7x11 frame | `39794` | 140 x 20 x 220 | holes on all THREE axes -- see below |

## Hub hole map (the thing everything bolts to)

Local, with the Hub at the origin:

- side faces `x = +-70`: holes at `y = -50, -30, -10` on the `z = +-80`
  columns, plus `y = -10` on `z = +-40`. Axis X.
- front/back faces `z = +-110`: holes at `x = +-40`, `y = -50, -30, -10`.
  Axis Z.
- bottom `y = 0`: twelve holes, axis Y.
- top `y = -80`: four holes at `x = +-60`, `z = +-100`.

The front face spans only 40 LDU in y (-50 to -10). That single fact
decides the whole nose of this model: the Large Motor's own mounting
holes are **80 apart**, so it can never bolt straight to the Hub's face.
Hence the two upright 5M beams in step 7, which offer a hole column from
`y=-70` to `y=+10` -- the only 80-apart pair on the machine.

## Why the posts are beams stood on end

A beam lying along Z gives one hole row at one height. This chassis needs
three heights out of one part: `y=-50` and `y=-30` to catch the Hub's
side pins, and `y=10` for the wheel axle, which must clear the Hub's
`y=0` underside. Matrix `0 1 0 0 0 1 1 0 0` stands a 5M beam upright with
its holes still facing X, giving holes at `y = -70,-50,-30,-10,10`.

## Frames carry holes on three axes; beams do not

`39794` (and `64179`) are rings, not grids. Stood on edge with
`0 1 0 -1 0 0 0 0 1` a 7x11 frame gives:

- **X-facing** holes (from its native `+Y` rail holes) -- the boom pivot
- **Y-facing** holes along its top and bottom edges (from its native
  `+-X` side-wall holes) -- where the bucket motor hangs
- **Z-facing** holes at both ends

A plain beam only ever offers one axis, which is why the boom is a frame.

## Open problem: the arm's pose

The arm is currently modelled axis-aligned, boom horizontal. It checks
clean but reads as a rectangle on a stick rather than a digger arm.

Rotating the boom about its own pivot is mathematically safe -- the pivot
hole's axis is X and the rotation is about X, so hole alignment is exactly
preserved (new matrix `R*M`, new offset `P + R*(O - P)` about pivot
`P = (-40,-30,160)`). Both directions were worked out and both fail on a
220-long boom pivoting 100 LDU from its rear end:

- **nose down 20 deg**: the bucket motor, which hangs below the boom,
  drops to `y ~ 97` and goes through the ground plane at 80.
- **nose up 20 deg**: the boom's rear-lower corner swings back to
  `z = 106, y = -17`, straight into the Hub.

Both are the same fact: the boom is too long for where it pivots. The fix
is a shorter boom (the 5x7 frame `64179`, 140 long) or a pivot nearer its
end, not a smaller angle.
