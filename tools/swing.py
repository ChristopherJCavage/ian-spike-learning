#!/usr/bin/env python3
"""Swing part of a model about a pivot and measure what it clears.

`ldrcheck` checks one pose: the model as written. A swinging arm has
every pose between its end stops, and the one written down is usually the
safest (hanging straight down). This rotates the steps that swing, writes
the rotated model, and reports the smallest gap from anything that moved
to anything that did not, at each angle asked for.

    python3 tools/swing.py builds/halfpipe-swing --steps 15-28 \\
        --roll 46372 -5 --angles -60 -30 0 30 60
    python3 tools/swing.py builds/halfpipe-swing --steps 15-28 \\
        --roll 46372 -5 --angles -60 60 --render

Gaps are measured on ldrcheck's 2 LDU voxel grid by growing the moved
parts one voxel at a time until they meet a stationary one, so they are
good to about 2 LDU. Parts named with --ignore are left out of the
stationary set: the part that carries the pivot, whose output disc turns
with the arm in real life but is one rigid file in LDraw.

`--roll PART RATIO` turns every swinging PART a further RATIO times the
swing angle about its own native Z, for a gear that rolls round a rack
while the arm carries it. A Z28 inside the 140-tooth ring turns -4x the
swing, i.e. -5x relative to the arm: `--roll 46372 -5`. Pairs the model
declares with `0 !LDRCHECK MESH` must then share no solid at all (teeth
clashing is the failure), and the gap is measured past them.

`--render` writes `renders/swing-<angle>.png` for each angle (the rotated
models go to a temp folder). The default `--camera back` is LeoCAD's
name for the +Z side, which is FRONT in this repo's models: LeoCAD's
"front" viewpoint looks from -Z, at the hub's legs.
"""

from __future__ import annotations

import argparse
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ldrcheck as L  # noqa: E402
import pages as P  # noqa: E402

AXES = {"x": 0, "y": 1, "z": 2}
MAX_LAYERS = 15


def _rotation(axis: str, degrees: float) -> list[list[float]]:
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    if axis == "x":
        return [[1, 0, 0], [0, c, -s], [0, s, c]]
    if axis == "y":
        return [[c, 0, s], [0, 1, 0], [-s, 0, c]]
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def _mul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _fmt(v: float) -> str:
    r = round(v, 4)
    return str(int(r)) if r == int(r) else f"{r:g}"


def rotate_model(
    text: str, steps: range, axis: str, degrees: float, pivot: list[float],
    rolls: dict[str, float] | None = None,
) -> str:
    """Rotate every part line on the given steps; leave the rest alone.
    Parts named in `rolls` also spin ratio * degrees about their local Z."""
    rot = _rotation(axis, degrees)
    rolls = rolls or {}
    step = 1
    out = []
    for line in text.splitlines():
        fields = line.split()
        if fields[:2] == ["0", "STEP"]:
            step += 1
        elif fields[:1] == ["1"] and len(fields) >= 15 and step in steps:
            nums = [float(v) for v in fields[2:14]]
            pos = [nums[i] - pivot[i] for i in range(3)]
            moved = [sum(rot[i][k] * pos[k] for k in range(3)) + pivot[i] for i in range(3)]
            m = [nums[3:6], nums[6:9], nums[9:12]]
            m2 = _mul(rot, m)
            ratio = rolls.get(L.part_stem(" ".join(fields[14:])))
            if ratio:
                m2 = _mul(m2, _rotation("z", ratio * degrees))
            vals = moved + [x for row in m2 for x in row]
            line = " ".join([fields[0], fields[1]] + [_fmt(v) for v in vals] + fields[14:])
        out.append(line)
    return "\n".join(out) + "\n"


def _gap(
    sources: list[L.Placed], still: list[L.Placed], solids: dict,
    by_index: dict[int, L.Placed],
) -> tuple[float | None, str]:
    """Grow `sources` a voxel at a time until they meet a `still` part."""
    if not sources or not still:
        return None, ""
    still_cells: dict[tuple[int, int, int], int] = {}
    for s in still:
        for c in solids[s.index]:
            still_cells[c] = s.index
    grown = set().union(*(solids[m.index] for m in sources))
    for layer in range(1, MAX_LAYERS + 1):
        grown = L.neighbours(grown)
        touched = {still_cells[c] for c in grown if c in still_cells}
        if touched:
            names = ", ".join(sorted({by_index[i].label.split(" at ")[0].split()[-1] for i in touched}))
            return layer * L.VOXEL, names
    return None, ""


def measure(path: Path, steps: range, ignore: set[str]) -> tuple[list[str], float | None, str]:
    """Collisions, then the smallest gap (LDU) from moved to stationary."""
    lib = L.Library(L.LIBRARY)
    parts = L.load_model(path, lib, None)
    solids = {p.index: L.solid_voxels(p) for p in parts if p.tris}
    meshed = L._meshed(parts, L.parse_directives(path).meshes)
    moved = [p for p in parts if p.step in steps and p.index in solids]
    still = [
        p for p in parts
        if p.step not in steps and p.index in solids
        and L.part_stem(p.part) not in ignore
    ]
    hits = []
    for m in moved:
        for s in still:
            shared = solids[m.index] & solids[s.index]
            if not shared:
                continue
            if tuple(sorted((m.index, s.index))) in meshed:
                # Meshed teeth touch; only solid-on-solid is a clash.
                shared &= L.interior(solids[m.index]) | L.interior(solids[s.index])
                if shared:
                    hits.append(f"{m.label} teeth clash with {s.label} ({len(shared) * L.VOXEL ** 3:.0f} LDU^3)")
                continue
            hits.append(f"{m.label} overlaps {s.label} ({len(shared) * L.VOXEL ** 3:.0f} LDU^3)")
    if hits:
        return hits, None, ""
    by_index = {p.index: p for p in parts}
    partners: dict[int, set[int]] = {}
    for a, b in meshed:
        partners.setdefault(a, set()).add(b)
        partners.setdefault(b, set()).add(a)
    best: tuple[float | None, str] = _gap(
        [m for m in moved if m.index not in partners], still, solids, by_index
    )
    for m in moved:
        if m.index not in partners:
            continue
        gap = _gap([m], [s for s in still if s.index not in partners[m.index]], solids, by_index)
        if gap[0] is not None and (best[0] is None or gap[0] < best[0]):
            best = gap
    if best[0] is None:
        return [], None, f"nothing within {MAX_LAYERS * L.VOXEL:g} LDU"
    return [], best[0], best[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("build", type=Path)
    ap.add_argument("--steps", required=True, help="steps that swing, e.g. 15-23")
    ap.add_argument("--axis", choices=sorted(AXES), default="z")
    ap.add_argument("--pivot", type=float, nargs=3, default=[0.0, 0.0, 0.0])
    ap.add_argument("--angles", type=float, nargs="+", default=[-60.0, 60.0])
    ap.add_argument("--ignore", nargs="*", default=["54675"],
                    help="part stems left out of the stationary set (default: the motor)")
    ap.add_argument("--roll", nargs=2, action="append", default=[], metavar=("PART", "RATIO"),
                    help="also spin PART ratio x the swing about its own Z (a gear rolling in a rack)")
    ap.add_argument("--render", action="store_true", help="also write renders/swing-<angle>.png")
    ap.add_argument("--camera", default="back",
                    help="LeoCAD viewpoint name or 'lat lon' for --render (default: back, i.e. the +Z side)")
    args = ap.parse_args()

    lo, _, hi = args.steps.partition("-")
    steps = range(int(lo), int(hi or lo) + 1)
    model = args.build / "model.ldr"
    text = model.read_text()
    ignore = {s.lower() for s in args.ignore}
    rolls = {L.part_stem(name): float(ratio) for name, ratio in args.roll}
    worst = None
    with tempfile.TemporaryDirectory() as tmp:
        for angle in args.angles:
            variant = Path(tmp) / f"swing-{angle:+g}.ldr"
            variant.write_text(rotate_model(text, steps, args.axis, angle, args.pivot, rolls))
            hits, gap, near = measure(variant, steps, ignore)
            if hits:
                print(f"{angle:+6g} deg  COLLISION")
                for h in hits:
                    print(f"           {h}")
                worst = -1.0
            elif gap is None:
                print(f"{angle:+6g} deg  clear ({near})")
            else:
                print(f"{angle:+6g} deg  min gap ~{gap:g} LDU  (nearest: {near})")
                worst = gap if worst is None else min(worst, gap)
            if args.render:
                png = (args.build / "renders" / f"swing-{angle:+g}.png").resolve()
                cmd = P._leocad_cmd(variant, png, 10_000, args.camera, highlight=False, fade=False)
                cmd[cmd.index("-f") + 1] = cmd[cmd.index("-t") + 1] = str(text.count("0 STEP"))
                before = png.stat().st_mtime if png.is_file() else 0
                subprocess.run(cmd, env=os.environ.copy(), capture_output=True, text=True)
                if png.is_file() and png.stat().st_mtime > before:
                    P.fit_hero(png)
                    print(f"           -> {png.relative_to(Path.cwd().resolve()) if png.is_relative_to(Path.cwd().resolve()) else png}")
                else:
                    print(f"           render FAILED for {png.name}")
                    worst = -1.0
    return 1 if worst is not None and worst < 0 else 0


if __name__ == "__main__":
    sys.exit(main())
