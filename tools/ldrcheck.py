#!/usr/bin/env python3
"""Geometry checker for the LDraw models in this repo.

Renders are not proof. A PNG can look fine while two beams occupy the same
cubic centimetre, and a model can look attached while every part floats in
space. This reads the real LDraw part geometry and does the arithmetic.

Reports, per model:
  - the true axis-aligned bounding box of every placed part
  - pairs of parts that interpenetrate, with the overlap volume
  - joints (pin-in-hole, axle-in-hole, stud-in-tube) with engagement depth
  - fasteners that do not join two parts, contact without a joint, hinges
  - ground clearance (from `0 !LDRCHECK GROUND` in the model, or `--ground`)
  - facing (from `facing:` in connections.yml vs `0 !LDRCHECK FRONT`)
  - unsupported parts (jointless and nothing underneath)
  - `0 !LDRCHECK` assertions (CLEARANCE, FACES, RESTS, JOINS)

Parts are resolved out of the official LDraw complete.zip, read in place.
Download it once:

    mkdir -p .ldraw
    curl -o .ldraw/complete.zip \\
        https://library.ldraw.org/library/updates/complete.zip

Usage:
    tools/ldrcheck.py check builds/mining-drill-truck/model.ldr
    tools/ldrcheck.py check model.ldr --through-step 5
    tools/ldrcheck.py connections model.ldr
    tools/ldrcheck.py measure 45601 54675 68488
    tools/ldrcheck.py fixtures
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import zipfile
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LIBRARY = REPO / ".ldraw" / "complete.zip"
ALIASES_PATH = REPO / "tools" / "ldraw_aliases.json"
CONNECTIONS_PATH = REPO / "tools" / "connections.yml"
KITS_DIR = REPO / "kits"

# Voxel edge in LDraw units. Overlap is measured between eroded solids, so
# this also sets how much surface gets discarded: at 2 LDU a coincident skin
# is ignored while a genuine 4 LDU bite still registers.
VOXEL = 2.0

# Parts that merely touch share the voxel layer along the contact face, and a
# pin's surface is coincident with the wall of the hole it sits in. Both are
# legal. Comparing eroded solids -- cells with all six neighbours filled --
# throws that shared skin away, so what is left is real interpenetration.
OVERLAP_TOLERANCE = 200.0  # LDU^3, roughly a 6 LDU cube of solid-on-solid
# Minifig feet have no clutch primitive, so standing on a plate always
# bites a little. A body buried in a seat is an order of magnitude more.
DECORATIVE_OVERLAP_TOLERANCE = 500.0

# A joint counts once the shaft sits at least this far into a hole. Below
# that is noise (grazing a face). A full Technic module is 20 LDU.
JOINT_MIN = 8.0
# Studs are 4 LDU tall. Using JOINT_MIN for them would make every legal
# stud-into-tube clutch invisible, which is why cab furniture used to
# hide behind role: decorative.
STUD_JOINT_MIN = 2.0
MODULE = 20.0
RADIAL_TOL = 4.0
AXIS_DOT = 0.9
# One plate. Touching the ground is not clearance -- same lesson as
# "contact is not a connection", applied to the floor.
CLEARANCE_MIN = 8.0

# Pin-like joints that can rigidly fix two parts against each other when
# there are two or more, non-collinear. Cross axles rotate by design, so
# they never contribute to rigidity on their own -- see RIGID CLUSTER
# HINGE and part_rotates().
HINGE_KINDS = {"friction_pin", "smooth_pin"}

Matrix = tuple[float, ...]  # (a, b, c, d, e, f, g, h, i)
Vec = tuple[float, float, float]

AXIS_FROM_NAME: dict[str, Vec] = {
    "+X": (1.0, 0.0, 0.0),
    "-X": (-1.0, 0.0, 0.0),
    "+Y": (0.0, 1.0, 0.0),
    "-Y": (0.0, -1.0, 0.0),
    "+Z": (0.0, 0.0, 1.0),
    "-Z": (0.0, 0.0, -1.0),
    "X": (1.0, 0.0, 0.0),
    "Y": (0.0, 1.0, 0.0),
    "Z": (0.0, 0.0, 1.0),
}

IDENTITY: Matrix = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)


def mat_mul(m: Matrix, n: Matrix) -> Matrix:
    return (
        m[0] * n[0] + m[1] * n[3] + m[2] * n[6],
        m[0] * n[1] + m[1] * n[4] + m[2] * n[7],
        m[0] * n[2] + m[1] * n[5] + m[2] * n[8],
        m[3] * n[0] + m[4] * n[3] + m[5] * n[6],
        m[3] * n[1] + m[4] * n[4] + m[5] * n[7],
        m[3] * n[2] + m[4] * n[5] + m[5] * n[8],
        m[6] * n[0] + m[7] * n[3] + m[8] * n[6],
        m[6] * n[1] + m[7] * n[4] + m[8] * n[7],
        m[6] * n[2] + m[7] * n[5] + m[8] * n[8],
    )


def apply(m: Matrix, offset: Vec, p: Vec) -> Vec:
    x, y, z = p
    return (
        m[0] * x + m[1] * y + m[2] * z + offset[0],
        m[3] * x + m[4] * y + m[5] * z + offset[1],
        m[6] * x + m[7] * y + m[8] * z + offset[2],
    )


class Library:
    """The official parts library, read straight out of complete.zip."""

    def __init__(self, archive: Path):
        if not archive.exists():
            sys.exit(
                f"LDraw library not found at {archive}.\n"
                "Download it with:\n"
                "  mkdir -p .ldraw && curl -o .ldraw/complete.zip \\\n"
                "      https://library.ldraw.org/library/updates/complete.zip"
            )
        self.zip = zipfile.ZipFile(archive)
        self.index: dict[str, str] = {}
        for name in self.zip.namelist():
            if not name.lower().endswith(".dat"):
                continue
            # "ldraw/parts/s/3005s01.dat" is referenced as both "s\3005s01.dat"
            # and "3005s01.dat" depending on the file doing the referencing.
            trimmed = name[6:] if name.lower().startswith("ldraw/") else name
            self.index.setdefault(trimmed.lower(), name)
            self.index.setdefault(Path(name).name.lower(), name)
        self._triangles: dict[str, list[tuple[Vec, Vec, Vec]]] = {}
        self.missing: set[str] = set()

    def read(self, ref: str) -> list[str] | None:
        key = ref.replace("\\", "/").lower()
        for candidate in (key, f"parts/{key}", f"p/{key}", f"models/{key}"):
            name = self.index.get(candidate)
            if name:
                return self.zip.read(name).decode("utf-8", "replace").splitlines()
        return None

    def triangles(self, ref: str) -> list[tuple[Vec, Vec, Vec]]:
        """Every triangle in a part, in that part's own coordinates."""
        key = ref.replace("\\", "/").lower()
        cached = self._triangles.get(key)
        if cached is not None:
            return cached
        # Guard against a part that somehow references itself.
        self._triangles[key] = []
        lines = self.read(ref)
        if lines is None:
            self.missing.add(ref)
            return []
        tris = list(triangles_from_lines(lines, self))
        self._triangles[key] = tris
        return tris


def triangles_from_lines(lines: list[str], lib: Library):
    """Expand one file's lines into triangles, recursing into subfiles."""
    for line in lines:
        fields = line.split()
        if not fields:
            continue
        kind = fields[0]
        if kind == "1" and len(fields) >= 15:
            nums = [float(v) for v in fields[2:14]]
            offset = (nums[0], nums[1], nums[2])
            matrix: Matrix = tuple(nums[3:12])  # type: ignore[assignment]
            sub = " ".join(fields[14:])
            for tri in lib.triangles(sub):
                yield tuple(apply(matrix, offset, p) for p in tri)  # type: ignore[misc]
        elif kind == "3" and len(fields) >= 11:
            n = [float(v) for v in fields[2:11]]
            yield ((n[0], n[1], n[2]), (n[3], n[4], n[5]), (n[6], n[7], n[8]))
        elif kind == "4" and len(fields) >= 14:
            n = [float(v) for v in fields[2:14]]
            a = (n[0], n[1], n[2])
            b = (n[3], n[4], n[5])
            c = (n[6], n[7], n[8])
            d = (n[9], n[10], n[11])
            yield (a, b, c)
            yield (a, c, d)


@dataclass
class Placed:
    """One part line from the model, expanded into world space."""

    index: int
    step: int
    part: str
    color: int
    offset: Vec
    matrix: Matrix
    tris: list[tuple[Vec, Vec, Vec]]

    @property
    def label(self) -> str:
        x, y, z = self.offset
        return f"[{self.index:3}] step {self.step:2} {self.part:<12} at ({x:g}, {y:g}, {z:g})"

    def bounds(self) -> tuple[Vec, Vec]:
        lo = [math.inf] * 3
        hi = [-math.inf] * 3
        for tri in self.tris:
            for p in tri:
                for axis in range(3):
                    lo[axis] = min(lo[axis], p[axis])
                    hi[axis] = max(hi[axis], p[axis])
        return tuple(lo), tuple(hi)  # type: ignore[return-value]


def parse_axis_name(s: str) -> Vec | None:
    return AXIS_FROM_NAME.get(s.strip().upper())


def dat_name(name: str) -> str:
    name = name.strip()
    return name if name.lower().endswith(".dat") else f"{name}.dat"


@dataclass
class ModelDirectives:
    """World-model and assertions read from `0 !LDRCHECK` lines."""

    ground: float | None = None
    front: Vec | None = None
    assertions: list[tuple[str, tuple[str, ...]]] = field(default_factory=list)


def parse_directives(path: Path) -> ModelDirectives:
    """Read `0 !LDRCHECK ...` meta lines. Unknown verbs become assertions
    so a typo fails closed instead of being ignored."""
    out = ModelDirectives()
    for line in path.read_text().splitlines():
        fields = line.split()
        if len(fields) < 3 or fields[0] != "0":
            continue
        if fields[1].upper() != "!LDRCHECK":
            continue
        verb = fields[2].upper()
        args = tuple(fields[3:])
        if verb == "GROUND" and args:
            try:
                out.ground = float(args[0])
            except ValueError:
                out.assertions.append((verb, args))
        elif verb == "FRONT" and args:
            axis = parse_axis_name(args[0])
            if axis is None:
                out.assertions.append((verb, args))
            else:
                out.front = axis
        else:
            out.assertions.append((verb, args))
    return out


def load_model(path: Path, lib: Library, through_step: int | None) -> list[Placed]:
    placed: list[Placed] = []
    step = 1
    for line in path.read_text().splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] == "0":
            if len(fields) >= 2 and fields[1].upper() == "STEP":
                step += 1
            continue
        if fields[0] != "1" or len(fields) < 15:
            continue
        if through_step is not None and step > through_step:
            break
        nums = [float(v) for v in fields[2:14]]
        offset: Vec = (nums[0], nums[1], nums[2])
        matrix: Matrix = tuple(nums[3:12])  # type: ignore[assignment]
        part = " ".join(fields[14:])
        tris = [
            tuple(apply(matrix, offset, p) for p in tri)
            for tri in lib.triangles(part)
        ]
        placed.append(
            Placed(
                index=len(placed),
                step=step,
                part=part,
                color=int(fields[1]),
                offset=offset,
                matrix=matrix,
                tris=tris,  # type: ignore[arg-type]
            )
        )
    return placed


def solid_voxels(part: Placed) -> set[tuple[int, int, int]]:
    """Fill the part's interior on a grid shared by every part in the model.

    Casts a ray along +X through the centre of each (y, z) cell, collects where
    it crosses the part's surface, and fills between crossing pairs. LDraw
    parts are closed surfaces, so the crossings come in pairs.
    """
    crossings: dict[tuple[int, int], list[float]] = defaultdict(list)
    for (ax, ay, az), (bx, by, bz), (cx, cy, cz) in part.tris:
        y_lo, y_hi = min(ay, by, cy), max(ay, by, cy)
        z_lo, z_hi = min(az, bz, cz), max(az, bz, cz)
        for jy in range(int(math.floor(y_lo / VOXEL)), int(math.ceil(y_hi / VOXEL)) + 1):
            py = (jy + 0.5) * VOXEL
            for jz in range(int(math.floor(z_lo / VOXEL)), int(math.ceil(z_hi / VOXEL)) + 1):
                pz = (jz + 0.5) * VOXEL
                # Barycentric test in the YZ plane.
                d = (by - cy) * (az - cz) + (cz - bz) * (ay - cy)
                if abs(d) < 1e-12:
                    continue
                u = ((by - cy) * (pz - cz) + (cz - bz) * (py - cy)) / d
                v = ((cy - ay) * (pz - cz) + (az - cz) * (py - cy)) / d
                w = 1.0 - u - v
                if u < 0.0 or v < 0.0 or w < 0.0:
                    continue
                crossings[(jy, jz)].append(u * ax + v * bx + w * cx)

    filled: set[tuple[int, int, int]] = set()
    for (jy, jz), xs in crossings.items():
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            start, end = xs[k], xs[k + 1]
            for jx in range(
                int(math.floor(start / VOXEL)), int(math.ceil(end / VOXEL))
            ):
                filled.add((jx, jy, jz))
    return filled


def interior(cells: set[tuple[int, int, int]]) -> set[tuple[int, int, int]]:
    """Drop the outermost shell, so touching faces stop looking like overlap."""
    return {
        (x, y, z)
        for x, y, z in cells
        if (x + 1, y, z) in cells
        and (x - 1, y, z) in cells
        and (x, y + 1, z) in cells
        and (x, y - 1, z) in cells
        and (x, y, z + 1) in cells
        and (x, y, z - 1) in cells
    }


def neighbours(cells: set[tuple[int, int, int]]) -> set[tuple[int, int, int]]:
    grown = set(cells)
    for x, y, z in cells:
        grown.add((x + 1, y, z))
        grown.add((x - 1, y, z))
        grown.add((x, y + 1, z))
        grown.add((x, y - 1, z))
        grown.add((x, y, z + 1))
        grown.add((x, y, z - 1))
    return grown


def check(path: Path, through_step: int | None, ground: float | None) -> int:
    lib = Library(LIBRARY)
    parts = load_model(path, lib, through_step)
    if not parts:
        sys.exit(f"No part lines found in {path}")
    directives = parse_directives(path)
    if ground is None:
        ground = directives.ground

    print(f"{path}  --  {len(parts)} parts"
          + (f", through step {through_step}" if through_step else ""))
    if lib.missing:
        print("\nNOT IN LIBRARY (treated as empty, so they cannot be checked):")
        for ref in sorted(lib.missing):
            print(f"  {ref}")

    print("\nBOUNDING BOXES (LDraw units; +Y is down)")
    empty: list[Placed] = []
    for part in parts:
        if not part.tris:
            empty.append(part)
            continue
        lo, hi = part.bounds()
        print(
            f"  {part.label}"
            f"   x {lo[0]:7.1f}..{hi[0]:7.1f}"
            f"   y {lo[1]:7.1f}..{hi[1]:7.1f}"
            f"   z {lo[2]:7.1f}..{hi[2]:7.1f}"
        )

    solids = {p.index: solid_voxels(p) for p in parts if p.tris}
    cores = {i: interior(cells) for i, cells in solids.items()}
    voxel_volume = VOXEL ** 3
    problems = 0

    found = joints(parts, lib, solids)
    direct_pairs = {tuple(sorted((j.male_part, j.female_part))) for j in found}

    print("\nINTERPENETRATION")
    collisions = []
    for i, first in enumerate(parts):
        a_raw = solids.get(first.index)
        if not a_raw:
            continue
        for second in parts[i + 1:]:
            b_raw = solids.get(second.index)
            if not b_raw:
                continue
            raw_shared = a_raw & b_raw
            if not raw_shared:
                continue
            pair = tuple(sorted((first.index, second.index)))
            if pair in direct_pairs:
                # A pin sits inside its own hole; that shared volume is
                # the fit, not a collision.
                continue
            # A coincident skin belongs to neither part's core, so it
            # falls out here. Real interpenetration survives because it
            # is interior to at least one of the two solids, even if the
            # other one is a hollow shell whose own core erodes to nothing.
            core_union = cores.get(first.index, set()) | cores.get(second.index, set())
            shared = raw_shared & core_union
            if not shared:
                continue
            volume = len(shared) * voxel_volume
            decorative = (
                part_role(first.part) == "decorative"
                or part_role(second.part) == "decorative"
            )
            limit = DECORATIVE_OVERLAP_TOLERANCE if decorative else OVERLAP_TOLERANCE
            if volume > limit:
                collisions.append((volume, first, second))
    if collisions:
        problems += len(collisions)
        for volume, first, second in sorted(collisions, key=lambda c: -c[0]):
            print(f"  {volume:9.0f} LDU^3   {first.label}")
            print(f"                    overlaps {second.label}")
    else:
        print("  none")

    problems += connection_checks(parts, solids, found, directives.front)

    if ground is not None:
        print(f"\nGROUND CLEARANCE (plane y = {ground:g}, min {CLEARANCE_MIN:g} LDU)")
        sunk = []
        for part in parts:
            if not part.tris:
                continue
            _, hi = part.bounds()
            clearance = ground - hi[1]
            if part_ground_contact(part.part):
                if clearance < -0.5:
                    sunk.append((clearance, part, "below ground"))
            elif clearance < CLEARANCE_MIN:
                sunk.append((clearance, part, "scrapes" if clearance <= 0.5 else "low"))
        if sunk:
            problems += len(sunk)
            for clearance, part, why in sorted(sunk, key=lambda s: s[0]):
                print(f"  {clearance:6.1f} LDU ({why:12})  {part.label}")
        else:
            print("  none")

    problems += assertion_checks(parts, solids, found, ground, directives)

    if empty:
        print("\nNO GEOMETRY (proxies or missing parts, not checked)")
        for part in empty:
            print(f"  {part.label}")

    print(f"\n{problems} problem(s)")
    return 1 if problems else 0


def measure(refs: list[str]) -> int:
    lib = Library(LIBRARY)
    for ref in refs:
        name = ref if ref.lower().endswith(".dat") else f"{ref}.dat"
        tris = lib.triangles(name)
        print(f"\n=== {name} ===")
        if not tris:
            print("  not in library")
            continue
        lo = [math.inf] * 3
        hi = [-math.inf] * 3
        for tri in tris:
            for p in tri:
                for axis in range(3):
                    lo[axis] = min(lo[axis], p[axis])
                    hi[axis] = max(hi[axis], p[axis])
        for axis, letter in enumerate("xyz"):
            print(
                f"  {letter}: {lo[axis]:8.2f} .. {hi[axis]:8.2f}"
                f"   (size {hi[axis] - lo[axis]:7.2f}, centre {(lo[axis] + hi[axis]) / 2:7.2f})"
            )
        lines = lib.read(name) or []
        subs = [ln for ln in lines if ln.split()[:1] == ["1"]]
        if subs:
            print(f"  {len(subs)} direct subfile reference(s):")
            for ln in subs:
                fields = ln.split()
                x, y, z = fields[2:5]
                print(f"    {' '.join(fields[14:]):<20} at ({x}, {y}, {z})")
    return 0


# Female (and male-stud) primitives. Every one of these has its axis along
# Y in its own coordinates, so the transformed Y column of the matrix is
# the feature axis. Kind is the gendered name used by the joint matcher.
PRIMITIVES: dict[str, tuple[str, str]] = {
    "peghole.dat": ("female", "pin_hole"),
    "peghole5.dat": ("female", "pin_hole"),
    "beamhole.dat": ("female", "pin_hole"),
    "connhole.dat": ("female", "pin_hole"),
    "axlehole.dat": ("female", "axle_hole"),
    "axlehol2.dat": ("female", "axle_hole"),
    "axlehol8.dat": ("female", "axle_hole"),
    "axlehol9.dat": ("female", "axle_hole"),
    "stud.dat": ("male", "stud"),
    "stud2.dat": ("male", "stud"),
    "stud2a.dat": ("male", "stud"),
    "stud3.dat": ("male", "stud"),
    "stud3a.dat": ("male", "stud"),
    # Hollow studs / underside tubes: a Technic pin seats here, and so does
    # a regular stud. Treated as pin_hole so plate-with-holes works.
    "stud4.dat": ("female", "pin_hole"),
    "stud4a.dat": ("female", "pin_hole"),
}

# Male shaft type -> female hole kinds it may occupy.
COMPAT: dict[str, set[str]] = {
    "friction_pin": {"pin_hole"},
    "smooth_pin": {"pin_hole"},
    "cross_axle": {"axle_hole", "pin_hole"},
    "stud": {"pin_hole", "anti_stud"},
    "bar": {"pin_hole"},
}

# LDraw colour code -> LEGO Education colour name as used in kits/*/parts.txt.
LDRAW_COLOR = {
    0: "Black",
    1: "Bright Blue",
    2: "Dark Green",
    4: "Bright Red",
    10: "Bright Green",
    14: "Bright Yellow",
    15: "White",
    19: "Brick Yellow",
    25: "Bright Orange",
    26: "Bright Reddish Violet",
    36: "Bright Green",
    43: "Transparent Light Blue",
    47: "Transparent",
    71: "Medium Stone Grey",
    72: "Dark Stone Grey",
    85: "Medium Lilac",
    89: "Light Royal Blue",
    141: "Dark Green",
    192: "Reddish Brown",
    226: "Flame Yellowish Orange",
    268: "Medium Nougat",
    321: "Dark Azur",
    322: "Medium Azur",
    323: "Light Aqua",
    331: "Flame Yellowish Orange",
}

# Keep the old name so holes() and any leftover callers still work.
FEATURES = {k: f"{gender} {kind}" for k, (gender, kind) in PRIMITIVES.items()}


def v_add(a: Vec, b: Vec) -> Vec:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def v_sub(a: Vec, b: Vec) -> Vec:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def v_scale(a: Vec, s: float) -> Vec:
    return (a[0] * s, a[1] * s, a[2] * s)


def v_dot(a: Vec, b: Vec) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def v_cross(a: Vec, b: Vec) -> Vec:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def v_len(a: Vec) -> float:
    return math.sqrt(v_dot(a, a))


def v_norm(a: Vec) -> Vec:
    n = v_len(a)
    if n < 1e-9:
        return (0.0, 0.0, 0.0)
    return v_scale(a, 1.0 / n)


def rotate_vec(m: Matrix, v: Vec) -> Vec:
    x, y, z = v
    return (
        m[0] * x + m[1] * y + m[2] * z,
        m[3] * x + m[4] * y + m[5] * z,
        m[6] * x + m[7] * y + m[8] * z,
    )


def parse_scalar(s: str):
    s = s.strip()
    if s in ("null", "~"):
        return None
    if s in ("true", "false"):
        return s == "true"
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    try:
        return int(s) if "." not in s and "e" not in s.lower() else float(s)
    except ValueError:
        return s


def parse_flow(s: str):
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [parse_flow(x) if x.strip()[:1] in "[{" else parse_scalar(x)
                for x in _split_flow(inner)]
    if s.startswith("{") and s.endswith("}"):
        inner = s[1:-1].strip()
        out = {}
        if not inner:
            return out
        for item in _split_flow(inner):
            k, _, v = item.partition(":")
            out[k.strip()] = parse_flow(v) if v.strip()[:1] in "[{" else parse_scalar(v)
        return out
    return parse_scalar(s)


def _split_flow(s: str) -> list[str]:
    parts, buf, depth = [], "", 0
    for ch in s:
        if ch in "[{":
            depth += 1
            buf += ch
        elif ch in "]}":
            depth -= 1
            buf += ch
        elif ch == "," and depth == 0:
            parts.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf.strip())
    return parts


def load_yaml(path: Path) -> dict:
    """Tiny YAML subset: 2-space maps, dash lists, flow [] {}."""
    return _yaml_with_list_detection(path)


def _yaml_with_list_detection(path: Path) -> dict:
    root: dict = {}
    stack: list = [(root, -1)]  # (container, indent)

    def current():
        return stack[-1][0]

    lines = [(len(r) - len(r.lstrip()), r.strip())
             for r in path.read_text().splitlines()
             if r.strip() and not r.lstrip().startswith("#")]
    i = 0
    while i < len(lines):
        indent, stripped = lines[i]
        while len(stack) > 1 and indent <= stack[-1][1]:
            stack.pop()
        parent = current()
        if stripped.startswith("- "):
            i += 1
            continue
        key, _, rest = stripped.partition(":")
        key, rest = key.strip(), rest.strip()
        if rest:
            if isinstance(parent, dict):
                parent[key] = parse_flow(rest)
            i += 1
            continue
        # Decide list vs map from the next line.
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        if nxt and nxt[0] > indent and nxt[1].startswith("- "):
            lst: list = []
            if isinstance(parent, dict):
                parent[key] = lst
            stack.append((lst, indent))
            i += 1
            while i < len(lines) and lines[i][0] > indent and lines[i][1].startswith("- "):
                item_src = lines[i][1][2:]
                if item_src.startswith("{") or item_src.startswith("["):
                    lst.append(parse_flow(item_src))
                elif ":" in item_src:
                    lst.append(parse_flow("{" + item_src + "}"))
                else:
                    lst.append(parse_scalar(item_src))
                i += 1
            stack.pop()
            continue
        nested: dict = {}
        if isinstance(parent, dict):
            parent[key] = nested
        stack.append((nested, indent))
        i += 1
    return root


_ANNOT: dict | None = None
_ALIAS: dict | None = None
_KIT_COLORS: dict[str, set[str]] | None = None


def aliases() -> dict:
    global _ALIAS
    if _ALIAS is None:
        raw = json.loads(ALIASES_PATH.read_text())
        _ALIAS = {k: v for k, v in raw.items() if not k.startswith("_")}
    return _ALIAS


def annotations() -> dict:
    global _ANNOT
    if _ANNOT is None:
        data = load_yaml(CONNECTIONS_PATH) if CONNECTIONS_PATH.exists() else {}
        _ANNOT = {k.lower(): v for k, v in data.items()}
    return _ANNOT


def kit_colors() -> dict[str, set[str]]:
    """design_id (and aliased LDraw stem) -> set of kit colour names."""
    global _KIT_COLORS
    if _KIT_COLORS is not None:
        return _KIT_COLORS
    out: dict[str, set[str]] = defaultdict(set)
    for path in sorted(KITS_DIR.glob("*/parts.txt")):
        for line in path.read_text().splitlines():
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 6 or not parts[0].isdigit():
                continue
            color, design = parts[1], parts[4]
            out[design].add(color)
            mapped = aliases().get(design, {})
            ldraw = mapped.get("ldraw") if isinstance(mapped, dict) else None
            if ldraw:
                out[Path(ldraw).stem].add(color)
    _KIT_COLORS = dict(out)
    return _KIT_COLORS


def part_stem(part: str) -> str:
    return Path(part.replace("\\", "/")).stem.lower()


def _annot(part: str) -> dict:
    info = annotations().get(part.lower()) or annotations().get(part_stem(part) + ".dat") or {}
    return info if isinstance(info, dict) else {}


def part_role(part: str) -> str:
    return _annot(part).get("role", "structural")


def part_rotates(part: str) -> bool:
    """True if this part is annotated as an intended rotating member (a
    wheel, a driven disc) -- see RIGID CLUSTER HINGE."""
    return bool(_annot(part).get("rotates", False))


def part_ground_contact(part: str) -> bool:
    """True if this part is allowed to touch the ground plane (a wheel)."""
    return bool(_annot(part).get("ground_contact", False))


def part_facing_local(part: str) -> Vec | None:
    """The part's own 'front' axis, in its native coordinates, or None."""
    raw = _annot(part).get("facing")
    if raw is None:
        return None
    return parse_axis_name(str(raw))


@dataclass
class Feature:
    """One male shaft or female hole, in world coordinates."""

    part_index: int
    gender: str
    kind: str
    origin: Vec
    axis: Vec
    t0: float
    t1: float

    @property
    def span(self) -> float:
        return abs(self.t1 - self.t0)


@dataclass
class Joint:
    male_part: int
    female_part: int
    kind: str
    depth: float
    origin: Vec
    axis: Vec
    # Engaged interval along the male shaft's own axis parameter (same
    # frame male.t0/t1 are in), so two joints on the same connector can be
    # compared directly -- see PIN SLICE CONFLICT.
    t0: float
    t1: float


def axis_name(v: Vec) -> str:
    """Nearest named axis, so output reads as +X rather than (1, 0, 0)."""
    best = max(range(3), key=lambda i: abs(v[i]))
    if abs(v[best]) < 0.9:
        return f"({v[0]:.2f}, {v[1]:.2f}, {v[2]:.2f})"
    return f"{'+' if v[best] > 0 else '-'}{'XYZ'[best]}"


def collect_features(lib: Library, ref: str, matrix: Matrix, offset: Vec, out: list):
    lines = lib.read(ref)
    if lines is None:
        return
    for line in lines:
        fields = line.split()
        if not fields or fields[0] != "1" or len(fields) < 15:
            continue
        nums = [float(v) for v in fields[2:14]]
        sub_offset = apply(matrix, offset, (nums[0], nums[1], nums[2]))
        sub_matrix = mat_mul(matrix, tuple(nums[3:12]))  # type: ignore[arg-type]
        sub = " ".join(fields[14:])
        base = sub.replace("\\", "/").split("/")[-1].lower()
        prim = PRIMITIVES.get(base)
        if prim:
            gender, kind = prim
            axis = (sub_matrix[1], sub_matrix[4], sub_matrix[7])
            # stud.dat's Y column points +Y (into the brick). The stud itself
            # sticks out along -Y. Flip so clutch with an anti-stud above
            # the plate actually overlaps the 4 LDU shaft.
            if gender == "male" and kind == "stud":
                axis = (-axis[0], -axis[1], -axis[2])
            out.append((gender, kind, sub_offset, axis))
        else:
            collect_features(lib, sub, sub_matrix, sub_offset, out)


def _collapse_features(feats: list[Feature]) -> list[Feature]:
    """Two rims describe one hole -- keep one per coincident cluster."""
    kept: list[Feature] = []
    for feat in feats:
        dup = False
        for other in kept:
            if other.kind != feat.kind or other.gender != feat.gender:
                continue
            if v_len(v_sub(other.origin, feat.origin)) < 2.0:
                dup = True
                break
        if not dup:
            kept.append(feat)
    return kept


def probe_bore(
    origin: Vec, axis: Vec, cells: set[tuple[int, int, int]], depth: float
) -> tuple[float, float]:
    """Return (t0, t1) along axis for the hole's bore, using material.

    The hole itself is empty, so we sample a ring of radius 6 LDU around
    the axis -- the wall of the hole -- and see which side has plastic.
    Direction comes from material, not from the primitive's axis sign.
    """
    axis = v_norm(axis)
    if not cells:
        half = depth / 2.0
        return (-half, half)

    helper = (1.0, 0.0, 0.0) if abs(axis[0]) < 0.9 else (0.0, 1.0, 0.0)
    u = v_norm(v_cross(axis, helper))
    v = v_norm(v_cross(axis, u))
    ring = 6.0

    def occupied(p: Vec) -> bool:
        return (
            int(math.floor(p[0] / VOXEL)),
            int(math.floor(p[1] / VOXEL)),
            int(math.floor(p[2] / VOXEL)),
        ) in cells

    def wall(t: float) -> bool:
        centre = v_add(origin, v_scale(axis, t))
        for c, s in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = v_add(centre, v_add(v_scale(u, ring * c), v_scale(v, ring * s)))
            if occupied(p):
                return True
        return False

    # Sample out to roughly the declared depth, not a fixed 22 LDU --
    # a short bore (a half bush's 10 LDU hole) never has 2 wall hits
    # within a window sized for a full module and silently defaults to
    # a one-sided guess.
    k_max = max(6, int(depth / 2.0) + 1)
    plus = sum(1 for k in range(2, k_max + 1) if wall(k * 2.0))
    minus = sum(1 for k in range(2, k_max + 1) if wall(-k * 2.0))
    if plus >= 2 and minus >= 2:
        half = depth / 2.0
        return (-half, half)
    if minus > plus:
        return (-depth, 0.0)
    return (0.0, depth)


def world_features(part: Placed, lib: Library, cells: set) -> list[Feature]:
    raw: list = []
    collect_features(lib, part.part, part.matrix, part.offset, raw)
    feats: list[Feature] = []
    for gender, kind, origin, axis in raw:
        axis_n = v_norm(axis)
        if gender == "female":
            t0, t1 = probe_bore(origin, axis_n, cells, MODULE)
        else:
            t0, t1 = 0.0, 4.0  # stud height
        feats.append(Feature(part.index, gender, kind, origin, axis_n, t0, t1))

    info = annotations().get(part.part.lower()) or annotations().get(part_stem(part.part) + ".dat") or {}
    if isinstance(info, dict):
        for shaft in info.get("shafts") or []:
            local_o = tuple(float(x) for x in shaft["origin"])
            local_a = v_norm(tuple(float(x) for x in shaft["axis"]))  # type: ignore[arg-type]
            origin = apply(part.matrix, part.offset, local_o)  # type: ignore[arg-type]
            axis = v_norm(rotate_vec(part.matrix, local_a))
            feats.append(Feature(
                part.index, "male", shaft["type"], origin, axis,
                float(shaft["t0"]), float(shaft["t1"]),
            ))
        for extra in info.get("features") or []:
            local_o = tuple(float(x) for x in extra["origin"])
            local_a = v_norm(tuple(float(x) for x in extra["axis"]))  # type: ignore[arg-type]
            origin = apply(part.matrix, part.offset, local_o)  # type: ignore[arg-type]
            axis = v_norm(rotate_vec(part.matrix, local_a))
            gender = extra.get("gender", "female")
            depth = float(extra.get("depth", MODULE))
            if gender == "female":
                t0, t1 = probe_bore(origin, axis, cells, depth)
            else:
                t0, t1 = 0.0, depth
            feats.append(Feature(
                part.index, gender, extra["kind"], origin, axis, t0, t1,
            ))
    return _collapse_features(feats)


def overlap_1d(a0: float, a1: float, b0: float, b1: float) -> float:
    lo, hi = min(a0, a1), max(a0, a1)
    lo2, hi2 = min(b0, b1), max(b0, b1)
    return max(0.0, min(hi, hi2) - max(lo, lo2))


def overlap_1d_range(a0: float, a1: float, b0: float, b1: float) -> tuple[float, float]:
    """The actual overlapping interval, not just its length. Zero-width
    (or negative -- no overlap) collapses to a point at the near edge."""
    lo, hi = min(a0, a1), max(a0, a1)
    lo2, hi2 = min(b0, b1), max(b0, b1)
    start, end = max(lo, lo2), min(hi, hi2)
    if end < start:
        return (start, start)
    return (start, end)


def joints(parts: list[Placed], lib: Library, solids: dict) -> list[Joint]:
    """Pair every male shaft with coaxial female holes it occupies."""
    feats_by_part = {
        p.index: world_features(p, lib, solids.get(p.index, set()))
        for p in parts
    }
    males: list[Feature] = []
    females: list[Feature] = []
    for feats in feats_by_part.values():
        for f in feats:
            (males if f.gender == "male" else females).append(f)

    found: list[Joint] = []
    for male in males:
        allowed = COMPAT.get(male.kind, set())
        if not allowed:
            continue
        for female in females:
            if female.part_index == male.part_index:
                continue
            if female.kind not in allowed:
                continue
            if abs(v_dot(male.axis, female.axis)) < AXIS_DOT:
                continue
            offset = v_sub(female.origin, male.origin)
            radial = v_len(v_cross(offset, male.axis))
            if radial > RADIAL_TOL:
                continue
            # Project the female bore onto the male shaft parameter.
            t_origin = v_dot(offset, male.axis)
            sign = 1.0 if v_dot(male.axis, female.axis) >= 0 else -1.0
            f0 = t_origin + sign * female.t0
            f1 = t_origin + sign * female.t1
            depth = overlap_1d(male.t0, male.t1, f0, f1)
            min_depth = STUD_JOINT_MIN if male.kind == "stud" else JOINT_MIN
            if depth < min_depth:
                continue
            t0, t1 = overlap_1d_range(male.t0, male.t1, f0, f1)
            found.append(Joint(
                male_part=male.part_index,
                female_part=female.part_index,
                kind=male.kind,
                depth=depth,
                origin=female.origin,
                axis=male.axis,
                t0=t0,
                t1=t1,
            ))
    return found


def _partners(part_index: int, found: list[Joint]) -> dict[int, float]:
    """Other part index -> max engagement depth."""
    out: dict[int, float] = defaultdict(float)
    for j in found:
        if j.male_part == part_index:
            out[j.female_part] = max(out[j.female_part], j.depth)
        elif j.female_part == part_index:
            out[j.male_part] = max(out[j.male_part], j.depth)
    return out


def _components(n: int, found: list[Joint], skip: set[int]) -> list[list[int]]:
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for j in found:
        if j.male_part in skip or j.female_part in skip:
            continue
        union(j.male_part, j.female_part)
    groups: dict[int, list[int]] = defaultdict(list)
    for i in range(n):
        if i in skip:
            continue
        groups[find(i)].append(i)
    return list(groups.values())


def _collinear(pin_axes: list[tuple[Vec, Vec]]) -> bool:
    """True if every (origin, axis) pair lies on the same line -- a single
    hinge axis, no matter how many pins share it."""
    o0, a0 = pin_axes[0]
    a0 = v_norm(a0)
    for origin, axis in pin_axes[1:]:
        if abs(v_dot(a0, v_norm(axis))) < AXIS_DOT:
            return False
        if v_len(v_cross(v_sub(origin, o0), a0)) > RADIAL_TOL:
            return False
    return True


def _union_find(n: int, pairs: set[tuple[int, int]]) -> list[int]:
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for a, b in pairs:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    return [find(i) for i in range(n)]


def _structural_bonds(
    parts: list[Placed], found: list[Joint]
) -> dict[tuple[int, int], list[Joint]]:
    """Every point of contact between two non-connector parts: a direct
    joint (a stud seating in a socket), or -- the common case in this
    library -- a shared connector, a pin or axle whose two ends land in
    different parts. Keyed by the pair of non-connector part indices;
    the connector is how the bond was made, not a node in the graph, so
    two separate pins between the same two beams count as two samples of
    one bond rather than two one-joint bonds nobody can see are related."""
    by_connector: dict[int, list[Joint]] = defaultdict(list)
    bonds: dict[tuple[int, int], list[Joint]] = defaultdict(list)
    for j in found:
        if part_role(parts[j.male_part].part) == "connector":
            by_connector[j.male_part].append(j)
        else:
            bonds[tuple(sorted((j.male_part, j.female_part)))].append(j)
    for js in by_connector.values():
        far = sorted({j.female_part for j in js})
        for a in range(len(far)):
            for b in range(a + 1, len(far)):
                # Every joint from this connector shares its axis and sits
                # on its line, so any one of them samples the bond fairly.
                bonds[tuple(sorted((far[a], far[b])))].append(js[0])
    return bonds


def _rigid_pairs(bonds: dict[tuple[int, int], list[Joint]]) -> set[tuple[int, int]]:
    """Bonded part pairs with >=2 non-collinear samples -- a genuine rigid
    fix. One pin, or several sharing one axis, is a hinge, not a rigid
    connection, and must not merge the two parts into one cluster for
    RIGID CLUSTER HINGE."""
    rigid: set[tuple[int, int]] = set()
    for pair, samples in bonds.items():
        if len(samples) < 2:
            continue
        if not _collinear([(s.origin, s.axis) for s in samples]):
            rigid.add(pair)
    return rigid


def _boundary_verdict(
    samples: list[Joint], smaller_members: list[int], by_index: dict[int, Placed]
) -> tuple[str, list[Joint] | None]:
    """Classify a cluster boundary as "merge" (braced from more than one
    angle, so the two sides are really one rigid body), "hinge" (one pin,
    or several sharing an axis -- reportable), or "articulated" (the only
    thing crossing is a bare rotating shaft into a connector or a part
    annotated `rotates: true` -- intended movement, not a defect, and
    *not* a fusion either: a spinning wheel stays its own cluster so it
    can still be caught touching something it shouldn't)."""
    if any(s.kind == "stud" for s in samples):
        # Stud-into-tube clutch does not pivot. One stud holds an antenna
        # or a dish; treating it as a hinge would outlaw every legal
        # stud connection.
        return "merge", None
    pin_like = [s for s in samples if s.kind in HINGE_KINDS]
    axle_like = [s for s in samples if s.kind not in HINGE_KINDS]
    # A cross-axle (or similar) crossing into a lone connector part (a
    # bare axle) is just a rotating shaft, not a structural claim. Into a
    # lone non-connector part (a wheel), it needs `rotates: true` --
    # otherwise it looks like someone glued a beam on with an axle
    # instead of pinning it.
    exempted = False
    if axle_like and len(smaller_members) == 1:
        only = by_index[smaller_members[0]].part
        if part_role(only) == "connector" or part_rotates(only):
            axle_like = []
            exempted = True
    rigidity_joints = pin_like + axle_like
    if not rigidity_joints:
        return "articulated", None
    if len(rigidity_joints) > 1 and not _collinear(
        [(j.origin, j.axis) for j in rigidity_joints]
    ):
        return "merge", None
    return "hinge", rigidity_joints


def _rigid_clusters(
    parts: list[Placed], found: list[Joint], by_index: dict[int, Placed]
) -> tuple[list[int], list[tuple[int, list[int], list[Joint]]]]:
    """Union-find clusters, extended past single-pair rigidity: two
    clusters also merge when the *combined* joints crossing their
    boundary are non-collinear, even though no single part-pair between
    them carries two samples on its own -- a dense multi-pin junction is
    braced by several one-sample bonds that each touch a different part
    of the boundary. This is the same test as the per-pair one, just
    applied to the boundary as a whole, so it has to iterate: merging
    two clusters can complete a boundary a third cluster only half
    satisfied by itself.

    Returns the settled membership plus the boundaries that are still
    hinges once nothing more can merge -- those are the real ones."""
    bonds = _structural_bonds(parts, found)
    membership = _union_find(len(parts), _rigid_pairs(bonds))
    hinges: list[tuple[int, list[int], list[Joint]]] = []
    while True:
        cluster_members: dict[int, list[int]] = defaultdict(list)
        for i in range(len(parts)):
            cluster_members[membership[i]].append(i)
        pair_bonds: dict[tuple[int, int], list[Joint]] = defaultdict(list)
        for (p, q), samples in bonds.items():
            ra, rb = membership[p], membership[q]
            if ra != rb:
                pair_bonds[tuple(sorted((ra, rb)))].extend(samples)
        merges: list[tuple[int, int]] = []
        hinges = []
        for (ra, rb), samples in pair_bonds.items():
            size_a, size_b = len(cluster_members[ra]), len(cluster_members[rb])
            if size_a < 2 and size_b < 2:
                # Neither side is a multi-part rigid subassembly -- the
                # per-part hinge warning already covers this pair, and
                # its bonds were already tried directly by _rigid_pairs.
                continue
            smaller = ra if size_a <= size_b else rb
            verdict, joints_ = _boundary_verdict(samples, cluster_members[smaller], by_index)
            if verdict == "merge":
                merges.append((ra, rb))
            elif verdict == "hinge":
                hinges.append((smaller, cluster_members[smaller], joints_))
            # "articulated": intended movement -- leave the two clusters
            # separate and do not report a problem.
        if not merges:
            break
        parent = {r: r for r in cluster_members}

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for ra, rb in merges:
            fa, fb = find(ra), find(rb)
            if fa != fb:
                parent[fb] = fa
        membership = [find(membership[i]) for i in range(len(parts))]
    # A connector (pin, axle) is a mediator, not a rigid node, so the
    # union-find above never merges it with anything -- but it visibly
    # touches whatever it passes through. If every part it reaches ended
    # up in one settled cluster, count the connector as part of it too;
    # if its two ends are in different clusters, it is the hinge itself
    # and must stay out of both.
    for part in parts:
        if part_role(part.part) != "connector":
            continue
        far_roots = {membership[f] for f in _partners(part.index, found)}
        if len(far_roots) == 1:
            membership[part.index] = next(iter(far_roots))
    return membership, hinges


def _support_map(
    parts: list[Placed],
    solids: dict,
    found: list[Joint],
) -> dict[int, set[int]]:
    """part index -> set of part indexes that have solid immediately
    underneath it (+Y, since +Y is down). A joint also counts as support
    so RESTS can treat clutched parts as sitting on each other."""
    under: dict[int, set[int]] = defaultdict(set)
    by_cell: dict[tuple[int, int, int], list[int]] = defaultdict(list)
    for part in parts:
        cells = solids.get(part.index)
        if not cells:
            continue
        for cell in cells:
            by_cell[cell].append(part.index)
    for part in parts:
        cells = solids.get(part.index)
        if not cells:
            continue
        seen: set[int] = set()
        for x, y, z in cells:
            for other in by_cell.get((x, y, z), ()):
                if other != part.index:
                    seen.add(other)
            for other in by_cell.get((x, y + 1, z), ()):
                if other != part.index:
                    seen.add(other)
            for other in by_cell.get((x, y + 2, z), ()):
                if other != part.index:
                    seen.add(other)
        if seen:
            under[part.index] = seen
    for j in found:
        under[j.male_part].add(j.female_part)
        under[j.female_part].add(j.male_part)
    return under


def _contact_map(
    parts: list[Placed], solids: dict
) -> dict[int, set[int]]:
    """part index -> neighbours in any direction (one voxel). Wall-mounted
    tiles rest against a face, not on the ground, and still are not floating."""
    grown = {i: neighbours(cells) for i, cells in solids.items()}
    out: dict[int, set[int]] = defaultdict(set)
    listed = [p for p in parts if p.index in solids]
    for i, a in enumerate(listed):
        g = grown[a.index]
        for b in listed[i + 1:]:
            if g & solids[b.index]:
                out[a.index].add(b.index)
                out[b.index].add(a.index)
    return out


def _instances(parts: list[Placed], name: str) -> list[Placed]:
    key = dat_name(name).lower()
    return [p for p in parts if p.part.lower() == key]


def _joint_graph(n: int, found: list[Joint]) -> list[set[int]]:
    adj: list[set[int]] = [set() for _ in range(n)]
    for j in found:
        adj[j.male_part].add(j.female_part)
        adj[j.female_part].add(j.male_part)
    return adj


def _reachable(adj: list[set[int]], start: int) -> set[int]:
    seen = {start}
    stack = [start]
    while stack:
        i = stack.pop()
        for j in adj[i]:
            if j not in seen:
                seen.add(j)
                stack.append(j)
    return seen


def assertion_checks(
    parts: list[Placed],
    solids: dict,
    found: list[Joint],
    ground: float | None,
    directives: ModelDirectives,
) -> int:
    print("\nASSERTIONS (0 !LDRCHECK claims)")
    if not directives.assertions:
        print("  none")
        return 0
    problems = 0
    supported_by = _support_map(parts, solids, found)
    adj = _joint_graph(len(parts), found)
    front = directives.front
    for verb, args in directives.assertions:
        msg = _eval_assertion(
            verb, args, parts, ground, front, supported_by, adj
        )
        if msg is None:
            print(f"  ok    {verb} {' '.join(args)}")
        else:
            problems += 1
            print(f"  FAIL  {verb} {' '.join(args)}  -- {msg}")
    return problems


def _eval_assertion(
    verb: str,
    args: tuple[str, ...],
    parts: list[Placed],
    ground: float | None,
    front: Vec | None,
    supported_by: dict[int, set[int]],
    adj: list[set[int]],
) -> str | None:
    """None means pass; a string is the failure reason."""
    if verb == "CLEARANCE":
        if len(args) < 2:
            return "need a part and a minimum clearance"
        if ground is None:
            return "no GROUND declared"
        want = float(args[1])
        found_parts = _instances(parts, args[0])
        if not found_parts:
            return f"{dat_name(args[0])} is not in the model"
        for part in found_parts:
            _, hi = part.bounds()
            got = ground - hi[1]
            if got + 0.5 < want:
                return f"{part.label} has {got:g} LDU, claimed {want:g}"
        return None
    if verb == "FACES":
        if len(args) < 2:
            return "need a part and an axis"
        if front is None:
            return "no FRONT declared"
        want = parse_axis_name(args[1])
        if want is None:
            return f"unknown axis {args[1]}"
        if v_dot(want, front) < AXIS_DOT:
            return f"claimed {args[1]} is not the model's FRONT {axis_name(front)}"
        found_parts = _instances(parts, args[0])
        if not found_parts:
            return f"{dat_name(args[0])} is not in the model"
        for part in found_parts:
            local = part_facing_local(part.part)
            if local is None:
                return f"{part.part} has no facing: annotation"
            world = v_norm(rotate_vec(part.matrix, local))
            if v_dot(world, want) < AXIS_DOT:
                return f"{part.label} faces {axis_name(world)}"
        return None
    if verb == "RESTS":
        # RESTS a ON b
        names = [a for a in args if a.upper() != "ON"]
        if len(names) < 2:
            return "need RESTS a ON b"
        upper = _instances(parts, names[0])
        lower = _instances(parts, names[1])
        if not upper:
            return f"{dat_name(names[0])} is not in the model"
        if not lower:
            return f"{dat_name(names[1])} is not in the model"
        lower_ids = {p.index for p in lower}
        for part in upper:
            if supported_by.get(part.index, set()) & lower_ids:
                return None
        return f"{dat_name(names[0])} does not rest on {dat_name(names[1])}"
    if verb == "JOINS":
        if len(args) < 2:
            return "need two parts"
        left = _instances(parts, args[0])
        right = _instances(parts, args[1])
        if not left:
            return f"{dat_name(args[0])} is not in the model"
        if not right:
            return f"{dat_name(args[1])} is not in the model"
        right_ids = {p.index for p in right}
        for part in left:
            if _reachable(adj, part.index) & right_ids - {part.index}:
                return None
        return f"{dat_name(args[0])} is not joined to {dat_name(args[1])}"
    return f"unknown directive {verb}"


def connection_checks(
    parts: list[Placed],
    solids: dict,
    found: list[Joint],
    front: Vec | None = None,
) -> int:
    problems = 0
    by_index = {p.index: p for p in parts}

    print("\nJOINTS")
    if found:
        for j in sorted(found, key=lambda x: -x.depth):
            a, b = by_index[j.male_part], by_index[j.female_part]
            print(f"  {j.depth:5.1f} LDU  {j.kind:<14} {a.label}")
            print(f"                    into {b.label}")
    else:
        print("  none")

    print("\nNO JOINT (non-decorative part with no pin/axle/stud connection)")
    lonely = []
    for part in parts:
        if not part.tris:
            continue
        if part_role(part.part) == "decorative":
            continue
        if not _partners(part.index, found):
            lonely.append(part)
    if lonely:
        problems += len(lonely)
        for part in lonely:
            print(f"  {part.label}")
    else:
        print("  none")

    print("\nCONNECTOR DOES NOT JOIN TWO PARTS")
    bad_conn = []
    for part in parts:
        if part_role(part.part) != "connector":
            continue
        partners = _partners(part.index, found)
        if len(partners) < 2:
            bad_conn.append((part, partners))
    if bad_conn:
        problems += len(bad_conn)
        for part, partners in bad_conn:
            names = ", ".join(by_index[i].part for i in partners) or "nothing"
            print(f"  {part.label}  joins {names}")
    else:
        print("  none")

    print("\nSHALLOW ENGAGEMENT (connector end below one module)")
    shallow = []
    warns = []
    for part in parts:
        if part_role(part.part) != "connector":
            continue
        partners = _partners(part.index, found)
        for other, depth in partners.items():
            if depth < JOINT_MIN:
                continue
            if depth < MODULE - 0.5:
                warns.append((depth, part, by_index[other]))
    # Fail only ends that don't reach JOINT_MIN -- already covered by
    # "does not join two parts". Warn on 8..20.
    if warns:
        for depth, part, other in sorted(warns, key=lambda w: w[0]):
            print(f"  WARN {depth:5.1f} LDU  {part.label}")
            print(f"                    into {other.label}")
    else:
        print("  none")

    print("\nPIN SLICE CONFLICT (two parts claim the same section of a shaft)")
    by_male: dict[int, list[Joint]] = defaultdict(list)
    for j in found:
        by_male[j.male_part].append(j)
    slice_conflicts = []
    for idx, js in by_male.items():
        part = by_index[idx]
        if part_role(part.part) != "connector":
            continue
        for a in range(len(js)):
            for b in range(a + 1, len(js)):
                ja, jb = js[a], js[b]
                if ja.female_part == jb.female_part:
                    continue
                ov = overlap_1d(ja.t0, ja.t1, jb.t0, jb.t1)
                if ov > 1.0:
                    slice_conflicts.append(
                        (ov, part, by_index[ja.female_part], by_index[jb.female_part])
                    )
    if slice_conflicts:
        problems += len(slice_conflicts)
        for ov, part, fa, fb in sorted(slice_conflicts, key=lambda s: -s[0]):
            print(f"  {ov:5.1f} LDU  {part.label}")
            print(f"                    claimed by {fa.label}")
            print(f"                         and by {fb.label}")
    else:
        print("  none")

    print("\nCONTACT WITHOUT JOINT")
    grown = {i: neighbours(neighbours(cells)) for i, cells in solids.items()}
    # Direct joint pair set, plus "joined via one connector".
    direct = set()
    for j in found:
        direct.add(tuple(sorted((j.male_part, j.female_part))))
    via_connector: set[tuple[int, int]] = set()
    for part in parts:
        if part_role(part.part) != "connector":
            continue
        ids = list(_partners(part.index, found))
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                via_connector.add(tuple(sorted((ids[a], ids[b]))))
    # Two parts already welded into the same rigid cluster (by other
    # pins elsewhere, possibly several one-sample bonds that only brace
    # the joint together as a whole) are not a defect just because they
    # also happen to sit flush against each other -- that is normal for
    # a dense multi-pin junction. Only flag touches that cross a real
    # seam, i.e. a boundary RIGID CLUSTER HINGE below would also flag.
    membership, _ = _rigid_clusters(parts, found, by_index)
    contact_bad = []
    for i, first in enumerate(parts):
        if not first.tris or part_role(first.part) == "decorative":
            continue
        g = grown.get(first.index)
        if not g:
            continue
        for second in parts[i + 1:]:
            if not second.tris or part_role(second.part) == "decorative":
                continue
            cells = solids.get(second.index)
            if not cells or not (g & cells):
                continue
            pair = tuple(sorted((first.index, second.index)))
            if pair in direct or pair in via_connector:
                continue
            if membership[first.index] == membership[second.index]:
                continue
            # A pin that already joins two parts is doing its job. A third
            # part brushing it is crowding, not a missing joint.
            if (
                part_role(first.part) == "connector"
                and len(_partners(first.index, found)) >= 2
            ) or (
                part_role(second.part) == "connector"
                and len(_partners(second.index, found)) >= 2
            ):
                continue
            contact_bad.append((first, second))
    if contact_bad:
        problems += len(contact_bad)
        for first, second in contact_bad:
            print(f"  {first.label}")
            print(f"                    touches {second.label}")
    else:
        print("  none")

    print("\nUNDER-CONSTRAINED (hinge: one pin, or two collinear pins)")
    hinges = []
    for part in parts:
        if part_role(part.part) != "structural":
            continue
        if not part.tris:
            continue
        pin_axes: list[tuple[Vec, Vec]] = []
        has_other = False
        for j in found:
            other = j.female_part if j.male_part == part.index else (
                j.male_part if j.female_part == part.index else None
            )
            if other is None:
                continue
            if j.kind in HINGE_KINDS:
                pin_axes.append((j.origin, j.axis))
            else:
                has_other = True
        if has_other:
            continue
        if not pin_axes:
            continue
        if len(pin_axes) == 1 or _collinear(pin_axes):
            hinges.append(part)
    if hinges:
        for part in hinges:
            print(f"  WARN  {part.label}")
    else:
        print("  none")

    print("\nRIGID CLUSTER HINGE (subassembly reaches the rest of the model"
          " through a single joint, or joints on one axis)")
    _, cluster_hinges = _rigid_clusters(parts, found, by_index)
    if cluster_hinges:
        problems += len(cluster_hinges)
        for _smaller, members, rigidity_joints in cluster_hinges:
            labels = ", ".join(by_index[i].part for i in members[:6])
            extra = "" if len(members) <= 6 else f" +{len(members) - 6} more"
            print(f"  {len(members)} parts ({labels}{extra}) hang off:")
            for j in rigidity_joints:
                x, y, z = j.origin
                print(
                    f"      {j.kind:<14} at ({x:g}, {y:g}, {z:g})"
                    f"  axis {axis_name(j.axis)}"
                )
    else:
        print("  none")

    print("\nDETACHED SUBASSEMBLIES")
    skip = {p.index for p in parts
            if part_role(p.part) == "decorative" or not p.tris}
    comps = _components(len(parts), found, skip)
    comps = [c for c in comps if c]
    if len(comps) > 1:
        problems += len(comps) - 1
        for comp in comps:
            labels = ", ".join(by_index[i].part for i in comp[:8])
            extra = "" if len(comp) <= 8 else f" +{len(comp) - 8} more"
            print(f"  {len(comp)} parts: {labels}{extra}")
    else:
        print("  none")

    print("\nUNSUPPORTED (no joint, and no solid directly beneath)")
    supported_by = _support_map(parts, solids, found)
    touching = _contact_map(parts, solids)
    floating = []
    for part in parts:
        if not part.tris:
            continue
        if _partners(part.index, found):
            continue
        if supported_by.get(part.index):
            continue
        if touching.get(part.index):
            continue
        floating.append(part)
    if floating:
        problems += len(floating)
        for part in floating:
            print(f"  {part.label}")
    else:
        print("  none")

    print("\nFACING (annotated front vs the model's FRONT axis)")
    facing_bad = []
    if front is None:
        print("  (no 0 !LDRCHECK FRONT in the model; skipped)")
    else:
        for part in parts:
            local = part_facing_local(part.part)
            if local is None:
                continue
            world = v_norm(rotate_vec(part.matrix, local))
            if v_dot(world, front) < AXIS_DOT:
                facing_bad.append((part, world))
        if facing_bad:
            problems += len(facing_bad)
            for part, world in facing_bad:
                print(f"  {part.label}  faces {axis_name(world)}, need {axis_name(front)}")
        else:
            print("  none")

    print("\nCOLOUR vs KIT")
    colors = kit_colors()
    colour_bad = []
    for part in parts:
        if part.color == 16:
            continue
        name = LDRAW_COLOR.get(part.color)
        if not name:
            continue
        stem = part_stem(part.part)
        allowed = colors.get(stem, set())
        # Also try numeric stem as kit design id
        allowed |= colors.get(stem, set())
        if not allowed:
            continue
        if name not in allowed and "Multicombination" not in allowed:
            colour_bad.append((part, name, allowed))
    if colour_bad:
        problems += len(colour_bad)
        for part, name, allowed in colour_bad:
            print(f"  {part.label}  placed {name}; kit has {sorted(allowed)}")
    else:
        print("  none")

    return problems


def connections_report(path: Path, through_step: int | None) -> int:
    lib = Library(LIBRARY)
    parts = load_model(path, lib, through_step)
    solids = {p.index: solid_voxels(p) for p in parts if p.tris}
    found = joints(parts, lib, solids)
    by_index = {p.index: p for p in parts}
    print(f"{path}  --  {len(parts)} parts, {len(found)} joints")
    for part in parts:
        partners = _partners(part.index, found)
        role = part_role(part.part)
        print(f"  {part.label}  role={role}")
        if not partners:
            print("      (no joints)")
            continue
        for other, depth in sorted(partners.items(), key=lambda kv: -kv[1]):
            print(f"      {depth:5.1f} LDU -> {by_index[other].label}")
    return 0


def run_fixtures() -> int:
    folder = REPO / "tools" / "fixtures"
    if not folder.is_dir():
        print(f"no fixtures at {folder}")
        return 1
    failed = 0
    for ldr in sorted(folder.glob("*.ldr")):
        print(f"\n######## {ldr.name} ########")
        code = check(ldr, None, None)
        expect_bad = ldr.name.startswith("bad-")
        expect_good = ldr.name.startswith("good-")
        if expect_good and code != 0:
            print(f"FAIL {ldr.name}: expected clean, got problems")
            failed += 1
        elif expect_bad and code == 0:
            print(f"FAIL {ldr.name}: expected problems, got clean")
            failed += 1
        else:
            print(f"PASS {ldr.name}")
    print(f"\n{failed} fixture(s) failed")
    return 1 if failed else 0


def holes(refs: list[str]) -> int:
    lib = Library(LIBRARY)
    for ref in refs:
        name = ref if ref.lower().endswith(".dat") else f"{ref}.dat"
        found: list = []
        collect_features(lib, name, IDENTITY, (0.0, 0.0, 0.0), found)
        print(f"\n=== {name} ===")
        if not found:
            print("  no pin holes, axle holes or studs")
            continue
        grouped: dict[str, list] = defaultdict(list)
        for gender, kind, pos, axis in found:
            grouped[f"{gender} {kind}"].append((pos, axis))
        for kind in sorted(grouped):
            entries = grouped[kind]
            # Two rims describe one hole, so collapse anything coincident.
            unique: dict[tuple, str] = {}
            for pos, axis in entries:
                key = (round(pos[0], 1), round(pos[1], 1), round(pos[2], 1))
                unique[key] = axis_name(axis)
            print(f"  {kind} x{len(unique)}")
            for (x, y, z), ax in sorted(unique.items()):
                print(f"    ({x:7.1f}, {y:7.1f}, {z:7.1f})  axis {ax}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    check_cmd = sub.add_parser("check", help="check a model for collisions")
    check_cmd.add_argument("model", type=Path)
    check_cmd.add_argument(
        "--through-step",
        type=int,
        help="only check parts up to and including this step",
    )
    check_cmd.add_argument(
        "--ground",
        type=float,
        help="y of the ground plane (overrides 0 !LDRCHECK GROUND in the model)",
    )

    measure_cmd = sub.add_parser("measure", help="print the real size of parts")
    measure_cmd.add_argument("parts", nargs="+")

    holes_cmd = sub.add_parser(
        "holes", help="print every pin hole, axle hole and stud on a part"
    )
    holes_cmd.add_argument("parts", nargs="+")

    conn_cmd = sub.add_parser(
        "connections", help="list every joint in a model, with engagement depth"
    )
    conn_cmd.add_argument("model", type=Path)
    conn_cmd.add_argument("--through-step", type=int)

    sub.add_parser("fixtures", help="run tools/fixtures good-* / bad-* cases")

    args = parser.parse_args()
    if args.command == "check":
        return check(args.model, args.through_step, args.ground)
    if args.command == "holes":
        return holes(args.parts)
    if args.command == "connections":
        return connections_report(args.model, args.through_step)
    if args.command == "fixtures":
        return run_fixtures()
    return measure(args.parts)


if __name__ == "__main__":
    sys.exit(main())
