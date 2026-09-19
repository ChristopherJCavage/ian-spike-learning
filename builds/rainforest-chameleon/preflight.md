# Pre-flight -- Chameleon Colour-Match

`ldrcheck` is a linter, not a physics engine. LeoCAD snaps to a grid, not
to clutch. Run this after the checker is green and before you sit down
with Ian.

## Machine (must be green)

```
python3 tools/ldrcheck.py check builds/rainforest-chameleon/model.ldr
python3 tools/ldrcheck.py steps builds/rainforest-chameleon/model.ldr
python3 tools/ldrcheck.py fixtures
python3 tools/pages.py check builds/rainforest-chameleon
python3 tools/blocks.py check builds/rainforest-chameleon
```

The model header declares the world:

    0 !LDRCHECK GROUND 20
    0 !LDRCHECK FRONT +Z
    0 !LDRCHECK FACES 37308.dat +Y
    0 !LDRCHECK CLEARANCE 37308.dat 20
    0 !LDRCHECK JOINS 37308.dat 67351.dat
    0 !LDRCHECK FACES 47592.dat -Y
    0 !LDRCHECK JOINS 47592.dat 67351.dat
    0 !LDRCHECK JOINS 98138.dat 61332.dat

## Human (the checker will not see these)

- **Sensor read range.** `CLEARANCE` asserts a *minimum* gap (20 LDU
  above y = 20). It cannot tell "mounted too high to read." The lens sits
  about 29 LDU above the table; the pad has to come up into that ~1 cm
  window. If the animal cannot see the tile at the table, lower the pad
  stack or add a plate under the tile -- do not lower the sensor into
  the ground plane.
- **Colour pads.** 2x4 tiles on plate bases, one each of blue, red,
  yellow, dark green, azure, from the same Essential bin. They are not
  in `model.ldr`. Chris brings them.
- **No tongue any more.** An earlier draft parked a flex hose (`27328`)
  in front of the sensor as a decorative tongue. Ian's build-test found
  it does not actually mount there -- nothing to clutch onto -- so it
  is gone from `model.ldr` and the BOM. The sensor's face now carries
  two pegs and two white round tiles instead (steps 13-14). The story
  slides keep a drawn tongue on the illustrated chameleon; that is art,
  not a part list -- see `story.md`.
- **Eye tiles are a friction fit, not a true clutch.** `98138` grips
  the last few LDU of a `61332` peg the way a stud grips a tube --
  annotated in `connections.yml`, and `ldrcheck` flags it `WARN
  SHALLOW ENGAGEMENT` on purpose rather than a hard problem. Press them
  on straight; a light twist afterward is normal and does not mean it
  is loose.
- **Ball-joint pose.** The four feet are splayed 25° so sibling plates
  do not graze. Ian can re-pose them. All four pairs are legs -- the
  tail is plain clutch, so a table missing its spare tray still builds.
- **Tail overhang.** The orange plate turns across the animal and hangs
  two studs clear of the brick under it. Four studs of clutch is plenty
  for a part that carries nothing, but the tip is the first thing a
  six-year-old will grab to pick the animal up. Lift it by the hub. The
  tail was cut from eight studs and then bent after a left-side render:
  straight and long, it tapered to a purple point that read as a second
  head.
- **Hub top.** Kids will ask why nothing sits on most of the yellow lid.
  It has exactly two pin holes, both at (±60, -80, +40) -- over the
  shoulders now, just behind the brow, since the build-tester flip
  carried them here from the tail end -- and the matrix deck stands in
  both. A 2x8 plate with holes does peg onto them cleanly, but a 2M peg
  cannot serve the plate and the deck at once: 20 LDU goes into the hub,
  the plate's bore takes 16 of the remaining 20, and the deck needs a
  full 20. It is the plate or the matrix.
- **Brow horns.** Four 1x1 cones on one stud each. They pop off if
  brushed; that is fine, they are decoration. Keep two spares handy.
  They must go on the **outermost** stud column, x = ±70 -- one column
  in used to land in the plug/wire zone when the ports were on this
  wall (two drafts of this model got that wrong in two different ways).
  Since the build-tester flip moved both ports to the tail wall, the
  brow has no cable to dodge any more; x = ±70 is now just where they
  look right, not a clearance requirement.
- **Plug the cables in last, not the horns.** Both ports are now on the
  **tail** wall, framed by the rear pins (step 19), so neither cable
  crosses the brow at all. Port A (sensor) has the long run now -- the
  whole body, tail to snout -- and port B (matrix) the shorter one, to
  the shoulders. That is the reverse of the first draft, where the
  ports were at the head and the matrix cable was the long one.
- **Cables.** Port A = colour sensor, port B = matrix, both plugged in
  at the tail wall. Route slack under the belly so a pad can still
  slide through, and keep port A's long run off to one flank rather
  than draped across the light matrix on the way there. `ldrcheck`
  proves a plug fits; it says nothing about where the wire goes after
  that.
- **The PNG.** Do not pretend clutch is proven until someone looks at a
  render or the LeoCAD GUI.

## Before exempting a part

```
python3 tools/ldrcheck.py holes <part>
```

If it emits studs or tubes, it does not need `role: decorative`. Annotate
the missing male shafts or underside tubes in `tools/connections.yml`
instead. This build taught the checker `3738` and `32530` underside
tubes that way (`good-plate-on-brick.ldr`, `good-tbeam-on-plate.ldr`),
and then `3709`, `39789`, `3039`, `3040`, `59900` and `87079` for the
new tail and the colour patches (`good-tail-*.ldr`,
`good-crest-cone-on-plate.ldr`, `good-colour-tile-on-plate.ldr`, with
`bad-tail-plate-floating.ldr` proving the annotation still fails when
the part is out of reach). The build-tester pass added one more:
`98138`'s underside tube, so the eye tile can seat on a peg tip the way
a stud grips a tube (`good-eye-tile-on-pin.ldr`). It stays
`role: decorative` -- the mining-drill-truck glues two of these flat
against a beam with nothing plugged in -- so the tube is a `pin_hole`,
not the usual `anti_stud`, which is what lets it mate with a
`friction_pin` without forcing every use of the part into a joint.

## Two traps this build closed

`0 !LDRCHECK` and the kit audit both used to accept LDraw colour 331 as
"Flame Yellowish Orange". 331 is not an LDraw colour code at all -- the
parts rendered plain grey in LeoCAD while the colour-vs-kit check
reported no problem. The real code is 191 (`Bright_Light_Orange`). If a
part renders grey and you did not ask for grey, check the colour code
against `ldraw/LDConfig.ldr` in `complete.zip` before anything else.

The second one shipped in the first build of this very model: four crest
cones standing directly in front of the two cable ports. Nothing
interpenetrated -- the hub's solid stops at z = 50 and the cones started
there -- so every geometric check passed and the render looked tidy. The
model was simply impossible to plug in. `ldrcheck` now has a **PORT
ACCESS** check driven by the real plug part's measurements, with
`good-hub-ports-clear.ldr` and `bad-hub-port-blocked.ldr` holding it in
place. The general lesson: an electronics brick has requirements that
are not in its outline, and "no collision" is not the same as "usable".

The first fix for it was wrong too, and in a more interesting way. The
horns moved to x = ±50, which cleared the plug by one LDU and then sat
directly in the flat ribbon leaving it -- the plug seats, and the wire
pushes a cone held by a single stud straight off the model. So the check
now models the wire as well as the plug, as a separate narrower zone
reaching a module further out, and `bad-hub-cable-swept.ldr` pins it.
When you add a rule for a connector, ask what comes out of it as well as
what goes into it.

Both paragraphs above describe the ports on the **head** wall, where
they lived for the model's first two drafts. The build-tester pass
moved the ports to the **tail** wall (see "Plug the cables in last, not
the horns" above) and PORT ACCESS re-verified clean there instead --
the check itself did not need to change, only where the model asks it
to look. The horns are still at x = ±70 on the brow, just with nothing
left there to clear.
