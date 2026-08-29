# Measured geometry -- (slug)

Every number here should come out of `tools/ldrcheck.py`, not from looking
at a render. Re-derive with:

    python3 tools/ldrcheck.py measure <part>
    python3 tools/ldrcheck.py holes <part>

## Conventions

LDraw units, 20 LDU per Technic module. **+Y is down.** Declare the rest
in the model header so the checker actually reads them:

    0 !LDRCHECK GROUND <y of the floor>
    0 !LDRCHECK FRONT +Z   # or whichever way is forward

## Sizes

| Part | LDraw | Size x,y,z | Notes |
|---|---|---|---|
| | | | |

## Where the mounting holes are

(Fill from `ldrcheck holes`.)

## Assertions

Load-bearing numbers live in `0 !LDRCHECK` lines in `model.ldr`, not only
in this file. This page keeps the *why*.
