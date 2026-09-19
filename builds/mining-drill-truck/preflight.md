# Pre-flight -- mining drill truck

`ldrcheck` is a linter, not a physics engine. LeoCAD snaps to a grid, not
to clutch. Run this after the checker is green and before you sit down
with Ian.

## Machine (currently green)

```
python3 tools/ldrcheck.py check builds/mining-drill-truck/model.ldr
python3 tools/ldrcheck.py steps builds/mining-drill-truck/model.ldr
python3 tools/pages.py check builds/mining-drill-truck
```

All three print 0 problems as of the 45681 indexing pass.

## The drill bush -- CLOSED

This used to be an open discrepancy: `model.ldr` placed `4265c.dat`, the
**half** bush, while `parts.txt` sourced it from Essential element
`6271820`, which is design `42798` -- the **full** bush, `3713.dat`, twice
as long. The build could not supply the part it showed. The 1/2 bush is
design `42136` and lives in the Expansion box in Bright Yellow, which a
`45345, 45678` build may not draw on.

Two things had hidden it. `4265c.dat` is a redirect rather than a part
name, so it matched no kit design id and the colour check had nothing to
compare against; and there was no check at all for a part that appears in
no kit. `ldrcheck` now has one (`PART vs KIT`), and it failed on this line
the day it was added.

The old note said a 20 LDU bush could not fit the 5 LDU of shaft past the
last cone's face at z=375, so the choices were to change boxes or move the
cone stack. That was measured against the cone's **bounding box** rather
than its shape. `14918` tapers to a point at that end, and the bush's bore
is wider than the cone is there, so the full bush simply slides over the
tip. It now sits at z=380 spanning 370..390: no interpenetration, 10 LDU
of grip on the axle, cones untouched, and the drill capped in the same
place the half bush capped it.

**At the table:** the red bush in the Essential bin is the full-width one,
and that is now what the model shows. It should push on over the very point
of the drill and stop against the shoulder behind it.

## Human (the checker will not see these)

- **Minifig pose.** The driver stands beside the seat in CAD because
  minifigs have no clutch primitives. Sit him at the table, facing the
  declared FRONT (+Z).
- **Proxy parts.** `3005` stands in for the printed head `26881` and for
  the dog `93239`; neither mold exists in LDraw. Swap the real parts in.
- **Rationale prose.** The comments in `model.ldr` explaining the 48 LDU
  cone pitch and the doubled sensor rails are reasoning, not assertions.
  Re-read them against the coordinates after any geometry change.

## Before exempting a part

```
python3 tools/ldrcheck.py holes <part>
python3 tools/ldrcheck.py kits
```

If it emits studs or tubes, it does not need `role: decorative`. Annotate
the missing male shafts or underside tubes in `tools/connections.yml`.
