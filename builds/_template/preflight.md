# Pre-flight -- before you call a build done

`ldrcheck` is a linter, not a physics engine. LeoCAD snaps to a grid, not
to clutch. Run this after the checker is green and before you sit down
with Ian.

Copy this file with the rest of `_template/` into `builds/<slug>/`.

## Machine (must be green)

```
python3 tools/ldrcheck.py check builds/<slug>/model.ldr
python3 tools/ldrcheck.py fixtures
```

The model header should declare the world, not hope the CLI will:

    0 !LDRCHECK GROUND 70
    0 !LDRCHECK FRONT +Z

Numeric claims in comments should have a matching `0 !LDRCHECK` assertion
(CLEARANCE, FACES, RESTS, JOINS). If you delete a part, delete its
assertion -- a claim that names a missing part is a failure.

## Human (the checker will not see these)

- **Facing / pose.** Minifigs have no clutch primitives. The CAD may show
  them standing beside a seat. Sit them at the table, facing the FRONT
  the model declared.
- **Proxy parts.** A 1x1 brick standing in for a printed head or a dog is
  a placeholder. Swap the real mold in at the table.
- **Clearance intent.** The checker demands 8 LDU above the ground unless
  `ground_contact: true`. It cannot tell a decorative antenna from a wheel
  that should touch the floor -- that annotation is yours.
- **Rationale prose.** Comments that explain *why* (a 9M beam was too
  short) are not assertions. Re-read them against the coordinates after
  any geometry change.
- **The PNG.** Do not pretend clutch is proven until someone looks at a
  render or the LeoCAD GUI.

## Before exempting a part

```
python3 tools/ldrcheck.py holes <part>
```

If it emits studs or tubes, it does not need `role: decorative`. Annotate
the missing male shafts or underside tubes in `tools/connections.yml`
instead.
