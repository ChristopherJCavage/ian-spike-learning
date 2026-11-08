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
  - port access (room for a cable plug, from `ports:` in connections.yml)
  - `0 !LDRCHECK` assertions (CLEARANCE, FACES, RESTS, JOINS, GRIP, PROXY,
    MESH)
  - every intermediate step (`steps`): transients must clear by the next page

Parts are resolved out of the official LDraw complete.zip, read in place.
Download it once:

    mkdir -p .ldraw
    curl -o .ldraw/complete.zip \\
        https://library.ldraw.org/library/updates/complete.zip

Usage:
    tools/ldrcheck.py check builds/mining-drill-truck/model.ldr
    tools/ldrcheck.py check model.ldr --through-step 5
    tools/ldrcheck.py steps model.ldr
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
# LEGO kit folders start with the set number; non-LEGO kits (Snap Circuits:
# scb20-..., sc100-...) have their own inventory format, checked by tools/snap.py.
LEGO_KIT_GLOB = "[0-9]*/parts.txt"

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
# joint8ball.dat is an 8 LDU sphere. Origins coincide when the ball is
# seated; JOINT_MIN of 8 LDU would hide every real one, same reason
# studs needed their own floor. Match by origin gap, not coaxial overlap
# -- a splayed chameleon leg is still joined.
BALL_RADIUS = 8.0
BALL_JOINT_MIN = 2.0
BALL_JOINT_MAX_GAP = 4.0
MODULE = 20.0
RADIAL_TOL = 4.0
AXIS_DOT = 0.9

# A hub port is useless if you cannot get the cable into it. The Powered Up
# plug is LDraw 23816a: 34 LDU across the face, 18 LDU tall, and its box runs
# z = -20..14 with the 14 inside the socket's 18 LDU bore. So a seated plug
# stands 20 LDU proud of the socket, and that block of air has to be empty.
# These are the part's own measurements, not a guess at "about a brick".
PLUG_HALF_WIDTH = 17.0
PLUG_HALF_HEIGHT = 9.0
PLUG_STANDOFF = 20.0
# The wire does not stop where the plug does. LDraw models the tail as a flat
# 6-wire ribbon (s\23816s01 inside 23816c01): 18.9 LDU across, 4.2 thick,
# leaving the plug along its axis. Those two numbers are measured. The length
# is the one judgement here -- a ribbon cannot turn a corner in zero distance,
# so it is given one module of straight run before it is allowed to bend.
CABLE_HALF_WIDTH = 9.43
CABLE_HALF_THICK = 2.08
CABLE_RUN = MODULE
# One voxel of plastic clipping a corner of that box is grid noise; two is a
# part that is really in the way.
PORT_TOLERANCE = 2 * VOXEL**3
# One plate. Touching the ground is not clearance -- same lesson as
# "contact is not a connection", applied to the floor.
CLEARANCE_MIN = 8.0
# One action per page. Six identical pins is one action; a rail, a pin,
# a beam and a sensor on the same page is four. `ldrcheck steps` flags
# a page at or above PAGE_TYPES_MAX distinct part files, or above
# PAGE_PARTS_MAX pieces (even of one type).
PAGE_TYPES_MAX = 3
PAGE_PARTS_MAX = 8

# Pin-like joints that can rigidly fix two parts against each other when
# there are two or more, non-collinear. Cross axles rotate by design, so
# they never contribute to rigidity on their own -- see RIGID CLUSTER
# HINGE and part_rotates(). A ball-and-socket is a 3-DOF pose joint, not
# a hinge and not a rigid weld; it is legal on its own.
HINGE_KINDS = {"friction_pin", "smooth_pin"}
POSE_KINDS = {"ball"}

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
    # Shafts the model declares as intended pivots: (part name, axis). A
    # boom is *supposed* to swing on one axis, and without this every
    # powered arm reads as RIGID CLUSTER HINGE.
    pivots: list[tuple[str, Vec]] = field(default_factory=list)
    # Pairs the model declares as an intended grip: (part name, part name).
    # A minifig hand is a C-clip that closes *around* what it holds, so in
    # LDraw the two solids genuinely share volume -- about 800 LDU^3 for a
    # camera in a hand, well over even DECORATIVE_OVERLAP_TOLERANCE. That
    # is the fit, not a collision, exactly like a pin inside its own hole.
    grips: list[tuple[str, str]] = field(default_factory=list)
    # Connectors the model declares as deliberately free-running: nothing
    # grips them and that is the design. A bearing axle held captive by a
    # part above it is the honest case. See NOT RETAINED.
    freeruns: list[str] = field(default_factory=list)
    # Gear pairs the model declares as meshed: (gear, partner, centre
    # distance). Teeth that engage touch with no pin between them, which
    # every other rule reads as a part resting against a part.
    meshes: list[tuple[str, str, float]] = field(default_factory=list)
    # Parts standing in for a kit part LDraw has no geometry for: the dog,
    # the printed heads before they were aliased. Keyed by the stand-in's
    # part name, valued by the kit design id it represents.
    proxies: dict[str, str] = field(default_factory=dict)
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
        elif verb == "PIVOT" and len(args) >= 2:
            axis = parse_axis_name(args[1])
            if axis is None:
                out.assertions.append((verb, args))
            else:
                out.pivots.append((dat_name(args[0]), axis))
                # Also an assertion, so a pivot naming a part that is no
                # longer in the model fails instead of quietly excusing
                # nothing.
                out.assertions.append((verb, args))
        elif verb == "PROXY" and len(args) >= 2:
            out.proxies[dat_name(args[0])] = args[1]
            # Also an assertion, so a proxy standing in for something that
            # is not in any kit -- or that LDraw now has geometry for --
            # gets said out loud instead of excusing itself.
            out.assertions.append((verb, args))
        elif verb == "FREERUN" and args:
            out.freeruns.append(dat_name(args[0]))
            # Also an assertion, so a FREERUN naming a part that has left the
            # model, or one that something now grips, fails instead of
            # quietly excusing nothing.
            out.assertions.append((verb, args))
        elif verb == "GRIP" and len(args) >= 2:
            out.grips.append((dat_name(args[0]), dat_name(args[1])))
            # Also an assertion, so a GRIP left behind after the held item
            # moves fails instead of quietly excusing a real collision.
            out.assertions.append((verb, args))
        elif verb == "MESH" and len(args) >= 3:
            try:
                out.meshes.append((dat_name(args[0]), dat_name(args[1]), float(args[2])))
            except ValueError:
                pass
            # Also an assertion: every gear must sit at that centre distance
            # from a partner, so a MESH whose gear has wandered fails.
            out.assertions.append((verb, args))
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
    gripped = {tuple(sorted(g)) for g in directives.grips}
    meshed = _meshed(parts, directives.meshes)
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
            if tuple(sorted((first.part, second.part))) in gripped:
                # Declared grip: a hand closed around a held item.
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
            if pair in meshed:
                limit = MESH_OVERLAP_TOLERANCE
            if volume > limit:
                collisions.append((volume, first, second))
    if collisions:
        problems += len(collisions)
        for volume, first, second in sorted(collisions, key=lambda c: -c[0]):
            print(f"  {volume:9.0f} LDU^3   {first.label}")
            print(f"                    overlaps {second.label}")
    else:
        print("  none")

    problems += connection_checks(
        parts, solids, found, directives.front, directives.pivots,
        directives.proxies, directives.freeruns, directives.meshes,
    )

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

    problems += assertion_checks(
        parts, solids, found, ground, directives,
        partial=through_step is not None,
    )

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
    "peghole2.dat": ("female", "pin_hole"),
    "peghole3.dat": ("female", "pin_hole"),
    "peghole4.dat": ("female", "pin_hole"),
    "peghole5.dat": ("female", "pin_hole"),
    "peghole6.dat": ("female", "pin_hole"),
    "beamhole.dat": ("female", "pin_hole"),
    "connhole.dat": ("female", "pin_hole"),
    # Every axlehol* variant is the same bore drawn with different edges
    # showing. Gears in particular use the "Tooth" and "Open Two Opposite
    # Sides" spellings, which is why a bevel gear used to read as solid.
    # axlehol0 is a build hint with no surface, so it stays out.
    "axlehole.dat": ("female", "axle_hole"),
    "axlehol2.dat": ("female", "axle_hole"),
    "axlehol3.dat": ("female", "axle_hole"),
    "axlehol4.dat": ("female", "axle_hole"),
    "axlehol5.dat": ("female", "axle_hole"),
    "axlehol6.dat": ("female", "axle_hole"),
    "axlehol7.dat": ("female", "axle_hole"),
    "axlehol8.dat": ("female", "axle_hole"),
    "axlehol9.dat": ("female", "axle_hole"),
    # The "Semi-Reduced" family is the same bore with a slightly slimmer
    # wall, and it is spelled axl3ho*, not axlehol*. Every brick with
    # vertical axle holes uses it -- 39789, the 2x4 with three of them,
    # is built entirely from these. Leaving them out made such a brick
    # read as solid plastic, so an axle through it registered no joint
    # and the brick itself reported NO JOINT. Same class of miss as the
    # bevel gear above. There is no axl3ho0 hint variant to exclude.
    "axl3hole.dat": ("female", "axle_hole"),
    "axl3hol2.dat": ("female", "axle_hole"),
    "axl3hol3.dat": ("female", "axle_hole"),
    "axl3hol6.dat": ("female", "axle_hole"),
    "axl3hol8.dat": ("female", "axle_hole"),
    "axl3hol9.dat": ("female", "axle_hole"),
    "axl3ho10.dat": ("female", "axle_hole"),
    "stud.dat": ("male", "stud"),
    "stud2.dat": ("male", "stud"),
    "stud2a.dat": ("male", "stud"),
    "stud3.dat": ("male", "stud"),
    "stud3a.dat": ("male", "stud"),
    # Round and octagonal parts do not use stud.dat. They use one of the
    # laterally-truncated studs, which were all missing here, so a 2x2
    # round brick emitted no top studs at all -- stack two and the upper
    # one reported NO JOINT and CONTACT WITHOUT JOINT while the lower one
    # looked fine. Same class of miss as the axl3ho* family below.
    "stud6.dat": ("male", "stud"),
    "stud6a.dat": ("male", "stud"),
    "stud10.dat": ("male", "stud"),
    "stud15.dat": ("male", "stud"),
    "stud17.dat": ("male", "stud"),
    "stud17a.dat": ("male", "stud"),
    # Plain studs drawn without the base ring or without the logo.
    "studa.dat": ("male", "stud"),
    "stud26.dat": ("male", "stud"),
    # Hollow studs / underside tubes: a Technic pin seats here, and so does
    # a regular stud. Treated as pin_hole so plate-with-holes works.
    "stud4.dat": ("female", "pin_hole"),
    "stud4a.dat": ("female", "pin_hole"),
    # The rest of that family -- stud4h/4o/4s, stud2s, stud16/16a, stud23 --
    # is deliberately left out. They are partial shapes ("without Outer
    # Cylinder", "Sliced", "Split") that parts use as inner detail, not as
    # a whole socket, and they are not placed at the socket mouth: the 1x1
    # round tile 98138 carries a stud4o at y=4, four LDU short of its real
    # underside at y=8. Adding them gave that tile a second, shallower hole
    # on top of its hand annotation below, which then double-claimed a
    # section of pin and reported PIN SLICE CONFLICT on a good build. Where
    # one of these parts matters, annotate it in connections.yml instead.
    # Technic ball-and-socket. Origins coincide when seated; the ball
    # primitive's Y column is not the stem, so matching is by origin,
    # not by coaxial overlap. See joints() and POSE_KINDS.
    "joint8ball.dat": ("male", "ball"),
    "joint8socket1.dat": ("female", "ball_socket"),
}

# Male shaft type -> female hole kinds it may occupy.
# Which (male, female) pairings actually HOLD, as opposed to merely fitting.
# COMPAT says a joint exists; this says whether the joint resists being pulled
# apart. The distinction is invisible in CAD and decides whether a model stays
# together in a child's hands.
#
# A cross axle is smooth along its length. In a cross-shaped axle_hole its
# splines lock, so it cannot rotate and its friction against the walls holds
# it in. In a round pin_hole it has nothing to bite: it spins and slides
# freely. That free fit is a feature when you want a bearing -- the drone's
# rotor spins on exactly that pairing -- and a defect when it is the only
# thing holding a part on. The drone's rotor blades were mounted on four
# smooth axles in round beam and plate holes, passed every check, and fell
# off the physical model.
#
# A friction_pin is the opposite: ribbed, so a round pin_hole grips it. That
# is what a "peg with friction" is for, and why the same 61332 peg appears 24
# times in that build.
# Note that smooth_pin counts as gripping and cross_axle in a round hole does
# not, even though both turn freely. Free to ROTATE and free to SLIDE OUT are
# different properties, and only the second one loses parts. A LEGO pin --
# friction or frictionless -- has a moulded ridge that snaps past the lip of
# the bore, so a "pin without friction" spins in place but stays put; that is
# what tools/fixtures/good-expansion-pins.ldr is asserting. A cross axle has
# no ridge anywhere along its length, so a round hole neither stops it turning
# nor stops it leaving.
GRIPS: set[tuple[str, str]] = {
    ("friction_pin", "pin_hole"),
    ("smooth_pin", "pin_hole"),
    ("cross_axle", "axle_hole"),
    ("stud", "anti_stud"),
    ("stud", "pin_hole"),
    ("ball", "ball_socket"),
}

COMPAT: dict[str, set[str]] = {
    "friction_pin": {"pin_hole"},
    "smooth_pin": {"pin_hole"},
    "cross_axle": {"axle_hole", "pin_hole"},
    "stud": {"pin_hole", "anti_stud"},
    "bar": {"pin_hole"},
    "ball": {"ball_socket"},
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
    # 36 used to sit here as a second "Bright Green". LDraw 36 is Trans_Red
    # (#C91A09): a part written 36 came out transparent red in LeoCAD while
    # this table called it green and said nothing. Real Bright Green is 10,
    # already above. Third phantom found in this table -- see 268 and 141
    # below, and 331 before them.
    35: "Transparent Bright Green",
    36: "Transparent Red",
    43: "Transparent Light Blue",
    47: "Transparent",
    71: "Medium Stone Grey",
    72: "Dark Stone Grey",
    85: "Medium Lilac",
    89: "Light Royal Blue",
    # LEGO's "Flame Yellowish Orange" is LDraw 191 Bright_Light_Orange.
    # 226 (Bright_Light_Yellow) and 331 (not a code at all) were both
    # mapped here once; 331 rendered grey in LeoCAD while still passing
    # this table, which is exactly the kind of silent pass to not have.
    191: "Flame Yellowish Orange",
    # Reddish_Brown is 70. 192 was another code LDConfig does not define.
    70: "Reddish Brown",
    # 268 used to sit here as "Medium Nougat" and is not an LDraw code at
    # all -- same silent-pass as 331 above. LDConfig.ldr in .ldraw/
    # complete.zip has Medium_Nougat at 84, so anything written as 268
    # rendered plain grey in LeoCAD while this table waved it through.
    84: "Medium Nougat",
    # LDraw's real Dark_Green is 288 (#00451A). Code 2 above is LDraw
    # "Green" (#00852B) -- noticeably lighter -- and 141 was another
    # phantom. Prefer 288 for Dark Green parts; 2 is kept only because
    # the drone and chameleon rotor hubs already ship with it.
    288: "Dark Green",
    321: "Dark Azur",
    322: "Medium Azur",
    323: "Light Aqua",
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
    for path in sorted(KITS_DIR.glob(LEGO_KIT_GLOB)):
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


def kit_colours_for(
    part: "Placed", colors: dict[str, set[str]], proxies: dict[str, str]
) -> set[str]:
    """Kit colours a placed part may legally be.

    A proxy is drawn in the colour of the part it stands in for, so that
    part's kit colours count too: a brown wig proxied by 18228 is right in
    Reddish Brown even though no kit ships 18228 in that colour. Its own
    colours still count, because one stand-in file can cover several real
    parts (the drill truck's 3005 is a yellow head and a nougat dog) and
    PROXY records only one of them. A stand-in that is in no kit stays
    unchecked, as before."""
    allowed = set(colors.get(part_stem(part.part), set()))
    if allowed and part.part in proxies:
        allowed |= colors.get(proxies[part.part], set())
    return allowed


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


def part_ports(part: str) -> list[dict]:
    """Cable sockets declared in connections.yml, in part-local coordinates.

    Each entry is {name, origin, axis, up}: `axis` points out of the socket
    the way the plug arrives, `up` is the short side of the rectangular
    opening. LDraw does model the socket (23807) inside the hub, but it does
    not model the air a plug needs in front of it, which is the part that
    actually gets built over.
    """
    raw = _annot(part).get("ports")
    return [p for p in raw if isinstance(p, dict)] if isinstance(raw, list) else []


def part_faces_front(part: str) -> bool:
    """True if this part must look along the model's FRONT.

    A colour sensor has a native facing (the lens) but the chameleon aims
    it at the ground, not at FRONT. Minifigs opt in with faces_front.
    """
    return bool(_annot(part).get("faces_front", False))


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
    # The female feature's kind, not the male's. Needed because the same
    # connector grips or free-runs depending on what it went into: a cross
    # axle locks in an axle_hole and slides straight through a pin_hole.
    # See GRIPS and NOT RETAINED.
    female_kind: str
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
        if kind in ("ball", "ball_socket"):
            # The sphere sits at the primitive origin. probe_bore looking
            # for a pin-hole wall would invent a fake shaft.
            t0, t1 = -BALL_RADIUS, BALL_RADIUS
        elif gender == "female":
            t0, t1 = probe_bore(origin, axis_n, cells, MODULE)
            # axlehol* primitives are one LDU tall and scaled to the bore,
            # so a one-sided hole drawn at 0 10 0 is 10 deep, not a module.
            # The ends of the 24121 quarter rack are half-thick lap tabs
            # like this; reading them as 20 deep pushed the bore out of
            # the plastic and into whatever sat behind it. Two-sided holes
            # are left alone: two 10-deep halves at one origin is how a
            # through bore is usually drawn. So are bores under half a
            # module: the Z20 bevel gear's is drawn 7 deep, which is below
            # JOINT_MIN, and clipping it would unseat a gear that really
            # does grip its axle (good-expansion-gears-on-axle).
            scale = v_len(axis)
            if kind == "axle_hole" and MODULE / 2 - 0.5 <= scale < MODULE - 0.5:
                if t0 == 0.0 and t1 > 0.0:
                    t1 = scale
                elif t1 == 0.0 and t0 < 0.0:
                    t0 = -scale
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
            if male.kind == "ball":
                # Seated iff the two primitive origins coincide. A splayed
                # leg is still joined -- do not demand coaxial axes.
                dist = v_len(v_sub(female.origin, male.origin))
                if dist > BALL_JOINT_MAX_GAP:
                    continue
                depth = BALL_RADIUS - dist
                if depth < BALL_JOINT_MIN:
                    continue
                found.append(Joint(
                    male_part=male.part_index,
                    female_part=female.part_index,
                    kind=male.kind,
                    female_kind=female.kind,
                    depth=depth,
                    origin=female.origin,
                    axis=male.axis,
                    t0=male.t0,
                    t1=male.t1,
                ))
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
                female_kind=female.kind,
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


def _joint_neighbors(found: list[Joint]) -> dict[int, set[int]]:
    """Undirected joint graph: each part -> the parts it actually joins."""
    nbrs: dict[int, set[int]] = defaultdict(set)
    for j in found:
        nbrs[j.male_part].add(j.female_part)
        nbrs[j.female_part].add(j.male_part)
    return nbrs


MESH_DISTANCE_TOLERANCE = 1.0  # LDU; teeth overlap only ~4 LDU radially
# Meshed teeth interleave so shallowly that tip-on-tip shares at most ~220
# LDU^3 -- inside OVERLAP_TOLERANCE -- while a correctly phased mesh shares
# none. So a declared mesh gets no allowance at all.
MESH_OVERLAP_TOLERANCE = 0.0


def _mesh_pairs(
    parts: list[Placed], gear: str, partner: str, distance: float
) -> tuple[set[tuple[int, int]], list[Placed]]:
    """Gear/partner pairs that really engage, and the gears that engage nothing.

    A gear's axis is its native Z (true of every gear in connections.yml).
    Engaged means the partner's origin -- the centre of a gear or of a
    curved rack's ring -- lies `distance` from the gear's axis, and the two
    overlap along that axis, so the teeth share a plane. The tooth phase is
    left to the interpenetration pass: teeth tip-on-tip overlap and fail.
    """
    pairs: set[tuple[int, int]] = set()
    loose: list[Placed] = []
    partners = _instances(parts, partner)
    for g in _instances(parts, gear):
        axis = v_norm(rotate_vec(g.matrix, (0.0, 0.0, 1.0)))
        g_lo, g_hi = g.bounds()
        engaged = False
        for p in partners:
            if p.index == g.index:
                continue
            d = tuple(p.offset[k] - g.offset[k] for k in range(3))
            along = v_dot(d, axis)
            radial = math.sqrt(max(0.0, v_dot(d, d) - along * along))
            if abs(radial - distance) > MESH_DISTANCE_TOLERANCE:
                continue
            p_lo, p_hi = p.bounds()
            if not all(g_lo[k] < p_hi[k] and p_lo[k] < g_hi[k] for k in range(3)):
                continue
            pairs.add(tuple(sorted((g.index, p.index))))
            engaged = True
        if not engaged:
            loose.append(g)
    return pairs, loose


def _meshed(
    parts: list[Placed], meshes: list[tuple[str, str, float]] | None
) -> set[tuple[int, int]]:
    out: set[tuple[int, int]] = set()
    for gear, partner, distance in meshes or []:
        out |= _mesh_pairs(parts, gear, partner, distance)[0]
    return out


def _contact_excused(
    first: Placed,
    second: Placed,
    pair: tuple[int, int],
    direct: set[tuple[int, int]],
    via_connector: set[tuple[int, int]],
    membership: dict[int, int],
    nbrs: dict[int, set[int]],
    found: list[Joint],
    meshed: set[tuple[int, int]] | None = None,
) -> bool:
    """True if a voxel graze is not a missing joint.

    A ball seated in a socket plate that is clutched to a brick sits 2 LDU
    from that brick -- the sphere is 8 LDU, the brick is 20 thick, and the
    socket is at the plate's end. They share a joint neighbour (the socket
    plate), so the graze is the joint's geometry, not a stray touch.
    """
    if pair in direct or pair in via_connector:
        return True
    if meshed and pair in meshed:
        return True
    if membership[first.index] == membership[second.index]:
        return True
    if nbrs[first.index] & nbrs[second.index]:
        return True
    if (
        part_role(first.part) == "connector"
        and len(_partners(first.index, found)) >= 2
    ) or (
        part_role(second.part) == "connector"
        and len(_partners(second.index, found)) >= 2
    ):
        return True
    if part_ground_contact(first.part) and part_ground_contact(second.part):
        # Two parts that both sit on the table, touching each other: two
        # baseplates laid edge to edge. Neither one holds the other up, the
        # table does, so the seam is not a missing joint. Bridging it is
        # still worth doing and the diorama does, but a bare seam is a real
        # buildable state rather than a defect.
        return True
    return False


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


def _carries_declared_pivot(
    j: Joint, by_index: dict[int, Placed], pivots: list[tuple[str, Vec]]
) -> bool:
    """True if this joint is carried by a shaft the model declared a pivot,
    turning on the declared axis. Both halves matter: naming the part alone
    would excuse every other copy of that axle in the build."""
    carrier = by_index[j.male_part].part.lower()
    for name, axis in pivots:
        if carrier != name.lower():
            continue
        if abs(v_dot(v_norm(axis), v_norm(j.axis))) >= AXIS_DOT:
            return True
    return False


def _boundary_verdict(
    samples: list[Joint],
    smaller_members: list[int],
    by_index: dict[int, Placed],
    pivots: list[tuple[str, Vec]] | None = None,
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
    if samples and all(s.kind in POSE_KINDS for s in samples):
        # A ball-and-socket is a deliberate 3-DOF pose. Legal on its own,
        # like rotates: true on a wheel -- not a hinge, not a weld.
        return "articulated", None
    pin_like = [s for s in samples if s.kind in HINGE_KINDS]
    axle_like = [
        s for s in samples
        if s.kind not in HINGE_KINDS and s.kind not in POSE_KINDS
    ]
    # A whole subassembly turning on a declared pivot is the point of a
    # boom, an arm, or a steering knuckle. The `rotates` exemption below
    # only covers a SINGLE part hanging off a shaft, which a boom never
    # is, so without this every powered arm reads as a defect.
    if pivots:
        pin_like = [
            s for s in pin_like if not _carries_declared_pivot(s, by_index, pivots)
        ]
        axle_like = [
            s for s in axle_like if not _carries_declared_pivot(s, by_index, pivots)
        ]
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
    parts: list[Placed],
    found: list[Joint],
    by_index: dict[int, Placed],
    pivots: list[tuple[str, Vec]] | None = None,
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
            smaller_members = cluster_members[smaller]
            if len(smaller_members) == 1 and part_role(
                by_index[smaller_members[0]].part
            ) != "structural":
                # A lone decorative leaf on a single pin (a googly eye
                # capping a peg tip) is the exact shape of joint
                # UNDER-CONSTRAINED already lets through for a lone part,
                # regardless of what is on the other end of that pin. It
                # only reaches this branch instead of the size<2-and-
                # size<2 skip above because the *far* side happens to
                # already be a big rigid cluster -- but the size of the
                # far side does not make the eye any more likely to spin
                # or fall off, so judge it the same way either way.
                continue
            verdict, joints_ = _boundary_verdict(
                samples, smaller_members, by_index, pivots
            )
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


def _assertion_subjects(verb: str, args: tuple[str, ...]) -> list[str]:
    """Part names an assertion is *about*. Missing any of these under
    `--through-step` means the claim does not apply yet, not that it failed."""
    if verb == "CLEARANCE" and args:
        return [args[0]]
    if verb == "FACES" and args:
        return [args[0]]
    if verb == "RESTS":
        return [a for a in args if a.upper() != "ON"][:2]
    if verb == "JOINS":
        return list(args[:2])
    if verb == "GRIP":
        return list(args[:2])
    if verb == "PROXY" and args:
        return [args[0]]
    if verb == "PIVOT" and args:
        return [args[0]]
    if verb == "FREERUN" and args:
        return [args[0]]
    if verb == "MESH":
        return list(args[:2])
    return []


def assertion_checks(
    parts: list[Placed],
    solids: dict,
    found: list[Joint],
    ground: float | None,
    directives: ModelDirectives,
    partial: bool = False,
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
        if partial and any(
            not _instances(parts, name)
            for name in _assertion_subjects(verb, args)
        ):
            print(f"  skip  {verb} {' '.join(args)}  -- not placed yet")
            continue
        msg = _eval_assertion(
            verb, args, parts, ground, front, supported_by, adj, found,
            partial=partial,
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
    found: list[Joint] | None = None,
    partial: bool = False,
) -> str | None:
    """None means pass; a string is the failure reason. `partial` is a
    page of `steps` before the last."""
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
        want = parse_axis_name(args[1])
        if want is None:
            return f"unknown axis {args[1]}"
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
    if verb == "PROXY":
        if len(args) < 2:
            return "need a stand-in part and the kit design id it represents"
        if not _instances(parts, args[0]):
            return f"{dat_name(args[0])} is not in the model"
        design = args[1]
        if not kit_colors().get(design):
            return f"{design} is in no kit, so there is nothing to stand in for"
        mapped = aliases().get(design)
        ldraw = mapped.get("ldraw") if isinstance(mapped, dict) else mapped
        if ldraw:
            return (
                f"{design} now maps to {ldraw}; use the real part instead "
                "of a proxy"
            )
        return None
    if verb == "GRIP":
        if len(args) < 2:
            return "need two parts"
        left = _instances(parts, args[0])
        right = _instances(parts, args[1])
        if not left:
            return f"{dat_name(args[0])} is not in the model"
        if not right:
            return f"{dat_name(args[1])} is not in the model"
        # Bounding boxes, not voxels: this only has to catch a GRIP that
        # has stopped excusing anything, e.g. the held item was moved and
        # now floats. Real overlap is measured by the interpenetration
        # pass, which this directive tells to look away.
        for a in left:
            a_lo, a_hi = a.bounds()
            for b in right:
                b_lo, b_hi = b.bounds()
                if all(a_lo[k] < b_hi[k] and b_lo[k] < a_hi[k] for k in range(3)):
                    return None
        return (
            f"{dat_name(args[0])} and {dat_name(args[1])} do not touch, "
            "so the GRIP excuses nothing"
        )
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
    if verb == "PIVOT":
        if len(args) < 2:
            return "need a shaft part and an axis"
        axis = parse_axis_name(args[1])
        if axis is None:
            return f"{args[1]} is not an axis"
        shafts = _instances(parts, args[0])
        if not shafts:
            return f"{dat_name(args[0])} is not in the model"
        # A pivot that turns nothing is a stale claim: it silences the
        # hinge rule while the arm it described has been rebuilt around
        # some other shaft.
        ids = {p.index for p in shafts}
        for j in found or []:
            if j.male_part not in ids:
                continue
            if abs(v_dot(v_norm(axis), v_norm(j.axis))) >= AXIS_DOT:
                return None
        return (
            f"{dat_name(args[0])} carries no joint turning about "
            f"{axis_name(axis)}"
        )
    if verb == "FREERUN":
        # An excuse that has stopped excusing anything is worse than no
        # excuse, because it hides the next real one. Fail if the part has
        # left the model, or if something now grips every instance of it.
        name = dat_name(args[0])
        shafts = _instances(parts, name)
        if not shafts:
            return f"no {name} in the model"
        gripped = set()
        for j in found or []:
            if (j.kind, j.female_kind) in GRIPS:
                gripped.add(j.male_part)
        loose = [p for p in shafts if p.index not in gripped]
        if not loose:
            return f"every {name} is gripped -- FREERUN excuses nothing"
        return None
    if verb == "MESH":
        if len(args) < 3:
            return "need a gear, its partner, and the centre distance"
        try:
            distance = float(args[2])
        except ValueError:
            return f"{args[2]} is not a distance"
        if not _instances(parts, args[0]):
            return f"{dat_name(args[0])} is not in the model"
        if not _instances(parts, args[1]):
            return f"{dat_name(args[1])} is not in the model"
        _, loose = _mesh_pairs(parts, dat_name(args[0]), dat_name(args[1]), distance)
        if partial:
            # Mid-build, a gear whose rail is not on yet is waiting, not
            # wrong. One sharing a partner's plane at the wrong distance is.
            partners = _instances(parts, args[1])
            loose = [
                g for g in loose
                if any(
                    all(g.bounds()[0][k] < p.bounds()[1][k]
                        and p.bounds()[0][k] < g.bounds()[1][k] for k in range(3))
                    for p in partners
                )
            ]
        if loose:
            return (
                f"{loose[0].label} is not {distance:g} LDU from any "
                f"{dat_name(args[1])} in its plane"
            )
        return None
    return f"unknown directive {verb}"


def _prefix(parts: list[Placed], found: list[Joint], solids: dict, cores: dict, through: int):
    """Parts placed by `through`, plus joints/solids that only involve them.

    Part indexes are assigned in file order, which is step order, so a
    through-step cut is a prefix of the full list and `len(prefix)` is a
    valid union-find universe.
    """
    sub = [p for p in parts if p.step <= through]
    ids = {p.index for p in sub}
    sub_found = [
        j for j in found if j.male_part in ids and j.female_part in ids
    ]
    sub_solids = {i: cells for i, cells in solids.items() if i in ids}
    sub_cores = {i: cells for i, cells in cores.items() if i in ids}
    return sub, sub_found, sub_solids, sub_cores


def _grace_keys(
    parts: list[Placed],
    solids: dict,
    found: list[Joint],
    ground: float | None,
    freeruns: list[str] | None = None,
    pivots: list[tuple[str, Vec]] | None = None,
) -> dict[str, set[int]]:
    """Transient states that a later page is allowed to resolve.

    A key that is still present on the *next* page is a real defect --
    the next page did not pick it up. Keys are part indexes.
    """
    lonely = set()
    for part in parts:
        if not part.tris:
            continue
        if part_role(part.part) == "decorative":
            continue
        if not _partners(part.index, found):
            lonely.add(part.index)
    loose = set()
    for part in parts:
        if part_role(part.part) != "connector":
            continue
        if len(_partners(part.index, found)) < 2:
            loose.add(part.index)
    supported_by = _support_map(parts, solids, found)
    touching = _contact_map(parts, solids)
    floating = set()
    for part in parts:
        if not part.tris:
            continue
        if _partners(part.index, found):
            continue
        if supported_by.get(part.index):
            continue
        if touching.get(part.index):
            continue
        floating.add(part.index)
    clearance: set[int] = set()
    if ground is not None:
        for part in parts:
            if not part.tris:
                continue
            _, hi = part.bounds()
            gap = ground - hi[1]
            if part_ground_contact(part.part):
                if gap < -0.5:
                    clearance.add(part.index)
            elif gap < CLEARANCE_MIN:
                clearance.add(part.index)
    skip = {
        p.index for p in parts
        if part_role(p.part) == "decorative" or not p.tris
    }
    comps = [c for c in _components(len(parts), found, skip) if c]
    # A singleton is a part that landed and joined nothing. Two motors
    # that each already have a wheel are parallel subassemblies, not
    # leftovers -- official instructions do that constantly.
    detached = {c[0] for c in comps if len(c) == 1}
    # Retention is a transient, not a hard defect, because the usual order of
    # assembly puts a shaft in on one page and locks it on the next: the
    # drone's drive axle stands in its round bearing hole for one page before
    # the cross-hole brick goes on, and the truck's does the same. Lingering
    # into a second page is the real defect, and on the last page nothing is
    # forgiven.
    by_index = {p.index: p for p in parts}
    unretained = {
        part.index
        for part, _ in _unretained(parts, found, by_index, freeruns or [])
    }
    # A subassembly reaching the model through a single joint is transient for
    # the same reason as the two above: putting a part on one pin and tying it
    # down with the next part is ordinary assembly order. The drone's two nose
    # bricks each sit on one peg for exactly one page before the face plate
    # spans them. Still fatal on the last page, and `check` is unchanged.
    _, hinges = _rigid_clusters(parts, found, by_index, pivots or [])
    hinge_cluster = {i for _s, members, _j in hinges for i in members}
    return {
        "no_joint": lonely,
        "loose_connector": loose,
        "unsupported": floating,
        "clearance": clearance,
        "detached_singleton": detached,
        "not_retained": unretained,
        "hinge_cluster": hinge_cluster,
    }


def _interpenetrations(
    parts: list[Placed],
    solids: dict,
    cores: dict,
    found: list[Joint],
    grips: list[tuple[str, str]] | None = None,
    meshes: list[tuple[str, str, float]] | None = None,
) -> list[tuple[float, Placed, Placed]]:
    direct = {tuple(sorted((j.male_part, j.female_part))) for j in found}
    gripped = {tuple(sorted(g)) for g in (grips or [])}
    meshed = _meshed(parts, meshes)
    voxel_volume = VOXEL ** 3
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
            if pair in direct:
                continue
            if tuple(sorted((first.part, second.part))) in gripped:
                continue
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
            if pair in meshed:
                limit = MESH_OVERLAP_TOLERANCE
            if volume > limit:
                collisions.append((volume, first, second))
    return collisions


def _unretained(
    parts: list[Placed],
    found: list[Joint],
    by_index: dict[int, Placed],
    freeruns: list[str],
) -> list[tuple[Placed, list[Placed]]]:
    """Connectors whose every joint is a free-running fit.

    A connector that fits is not the same as a connector that holds. If not
    one of a shaft's joints appears in GRIPS, then nothing on the model
    resists pulling it straight back out, and whatever it was carrying comes
    off the moment the model is handled. This is the check that the drone's
    first rotor -- four smooth cross axles in round beam and plate holes --
    would have failed, instead of passing everything and falling apart on
    the table.
    """
    by_male: dict[int, list[Joint]] = defaultdict(list)
    for j in found:
        by_male[j.male_part].append(j)
    out = []
    for idx, js in sorted(by_male.items()):
        part = by_index[idx]
        if part_role(part.part) != "connector":
            continue
        if part.part in freeruns:
            continue
        if any((j.kind, j.female_kind) in GRIPS for j in js):
            continue
        holes = sorted({by_index[j.female_part].index for j in js})
        out.append((part, [by_index[i] for i in holes]))
    return out


def _bare_contacts(
    parts: list[Placed],
    solids: dict,
    found: list[Joint],
    by_index: dict[int, Placed],
    pivots: list[tuple[str, Vec]] | None = None,
    meshes: list[tuple[str, str, float]] | None = None,
) -> list[tuple[Placed, Placed]]:
    """Pairs that touch with nothing joining them, after the usual excuses.

    Two parts can abut for honest reasons -- same rigid cluster, joined
    through a shared connector, adjacent in the joint graph -- and
    `_contact_excused` knows those. What is left is a pair resting against
    each other and held by nothing, which is how a plate ends up looking
    attached in a render while falling off on the table.
    """
    grown = {i: neighbours(neighbours(cells)) for i, cells in solids.items()}
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
    membership, _hinges = _rigid_clusters(parts, found, by_index, pivots or [])
    nbrs = _joint_neighbors(found)
    meshed = _meshed(parts, meshes)
    out = []
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
            if _contact_excused(
                first, second, pair, direct, via_connector, membership, nbrs, found,
                meshed,
            ):
                continue
            out.append((first, second))
    return out


def _hard_messages(
    parts: list[Placed],
    solids: dict,
    cores: dict,
    found: list[Joint],
    ground: float | None,
    directives: ModelDirectives,
    partial_assertions: bool,
) -> list[str]:
    """Defects that are never allowed to linger -- wrong even as a WIP."""
    msgs: list[str] = []
    by_index = {p.index: p for p in parts}

    for volume, first, second in _interpenetrations(
        parts, solids, cores, found, directives.grips, directives.meshes
    ):
        msgs.append(
            f"INTERPENETRATION {volume:.0f} LDU^3  {first.label} overlaps {second.label}"
        )

    by_male: dict[int, list[Joint]] = defaultdict(list)
    for j in found:
        by_male[j.male_part].append(j)
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
                    fa, fb = by_index[ja.female_part], by_index[jb.female_part]
                    msgs.append(
                        f"PIN SLICE {ov:.1f} LDU  {part.label} claimed by "
                        f"{fa.part} and {fb.part}"
                    )

    # A part that only *touches* another part is not attached. Two plates
    # side by side clutch nothing -- the second one falls off. Hang the
    # spanning brick off the first plate first, then the next plate has
    # studs to click onto. Not a one-page grace: kids cannot hold a loose
    # plate while they pick up the next parts.
    for first, second in _bare_contacts(
        parts, solids, found, by_index, directives.pivots, directives.meshes
    ):
        msgs.append(
            f"CONTACT WITHOUT JOINT  {first.label} touches {second.label}"
        )

    front = directives.front
    if front is not None:
        for part in parts:
            if not part_faces_front(part.part):
                continue
            local = part_facing_local(part.part)
            if local is None:
                continue
            world = v_norm(rotate_vec(part.matrix, local))
            if v_dot(world, front) < AXIS_DOT:
                msgs.append(
                    f"FACING  {part.label} faces {axis_name(world)}, "
                    f"need {axis_name(front)}"
                )

    colors = kit_colors()
    for part in parts:
        if part.color == 16:
            continue
        name = LDRAW_COLOR.get(part.color)
        if not name:
            continue
        allowed = kit_colours_for(part, colors, directives.proxies)
        if not allowed:
            continue
        if name not in allowed and "Multicombination" not in allowed:
            msgs.append(
                f"COLOUR  {part.label} placed {name}; kit has {sorted(allowed)}"
            )

    supported_by = _support_map(parts, solids, found)
    adj = _joint_graph(len(parts), found)
    for verb, args in directives.assertions:
        if partial_assertions and any(
            not _instances(parts, n) for n in _assertion_subjects(verb, args)
        ):
            continue
        msg = _eval_assertion(
            verb, args, parts, ground, front, supported_by, adj, found,
            partial=partial_assertions,
        )
        if msg is not None:
            msgs.append(f"ASSERTION  {verb} {' '.join(args)} -- {msg}")
    return msgs


def _page_added(parts: list[Placed], step: int) -> list[Placed]:
    return [p for p in parts if p.step == step]


def steps_check(path: Path, ground: float | None = None) -> int:
    """Every intermediate state must be buildable. Voxelize once, then
    slice. A transient (loose pin, unsupported brick, singleton sitting
    by itself) is allowed on the page it appears; it must be gone by
    the next page. The last page has no grace window."""
    lib = Library(LIBRARY)
    parts = load_model(path, lib, None)
    if not parts:
        sys.exit(f"No part lines found in {path}")
    directives = parse_directives(path)
    if ground is None:
        ground = directives.ground
    solids = {p.index: solid_voxels(p) for p in parts if p.tris}
    cores = {i: interior(cells) for i, cells in solids.items()}
    found_all = joints(parts, lib, solids)
    max_step = max(p.step for p in parts)

    print(f"{path}  --  {len(parts)} parts, {max_step} steps")
    problems = 0

    # Page budget is for instruction models (2+ steps). Single-step
    # fixtures are geometry cases, not pages.
    if max_step > 1:
        print("\nPAGE BUDGET (one action: "
              f"<{PAGE_TYPES_MAX} types and <={PAGE_PARTS_MAX} parts)")
        for s in range(1, max_step + 1):
            added = _page_added(parts, s)
            counted = [
                p for p in added if part_role(p.part) != "decorative"
            ]
            types = {p.part.lower() for p in counted}
            fat = (
                len(types) >= PAGE_TYPES_MAX
                or len(counted) > PAGE_PARTS_MAX
            )
            mark = "FAIL" if fat else "ok  "
            print(
                f"  {mark}  step {s:2}  {len(counted):2} parts  "
                f"{len(types)} types  "
                + (", ".join(sorted(types)) if types else "(decorative only)")
            )
            if fat:
                problems += 1

    print("\nBUILD ORDER (transient must clear by the next page)")
    prev_grace: dict[str, set[int]] = {}
    by_index = {p.index: p for p in parts}
    for s in range(1, max_step + 1):
        sub, sub_found, sub_solids, sub_cores = _prefix(
            parts, found_all, solids, cores, s
        )
        last = s == max_step
        hard = _hard_messages(
            sub, sub_solids, sub_cores, sub_found, ground, directives,
            partial_assertions=not last,
        )
        grace = _grace_keys(
            sub, sub_solids, sub_found, ground, directives.freeruns,
            directives.pivots,
        )
        lingered: list[str] = []
        if last:
            # Finished model: same bar as `check`. Anything still
            # transient is a defect.
            for kind, keys in grace.items():
                for idx in sorted(keys):
                    lingered.append(f"{kind}  {by_index[idx].label}")
        else:
            for kind, keys in grace.items():
                for idx in sorted(keys & prev_grace.get(kind, set())):
                    lingered.append(f"{kind}  {by_index[idx].label}")
        n_trans = sum(len(v) for v in grace.values())
        fail = bool(hard or lingered)
        if fail:
            problems += len(hard) + len(lingered)
        status = "FAIL" if fail else "ok  "
        extra = f", {n_trans} transient" if n_trans and not last else ""
        print(f"  {status}  step {s:2}  {len(sub):3} parts{extra}")
        for msg in hard:
            print(f"         {msg}")
        for msg in lingered:
            print(f"         lingered {msg}")
        prev_grace = grace

    print(f"\n{problems} problem(s)")
    return 1 if problems else 0


def connection_checks(
    parts: list[Placed],
    solids: dict,
    found: list[Joint],
    front: Vec | None = None,
    pivots: list[tuple[str, Vec]] | None = None,
    proxies: dict[str, str] | None = None,
    freeruns: list[str] | None = None,
    meshes: list[tuple[str, str, float]] | None = None,
) -> int:
    problems = 0
    by_index = {p.index: p for p in parts}
    proxies = proxies or {}
    freeruns = freeruns or []

    print("\nJOINTS")
    if found:
        for j in sorted(found, key=lambda x: -x.depth):
            a, b = by_index[j.male_part], by_index[j.female_part]
            print(f"  {j.depth:5.1f} LDU  {j.kind:<14} {a.label}")
            print(f"                    into {b.label}")
    else:
        print("  none")

    print("\nNO JOINT (non-decorative part with no pin/axle/stud/ball connection)")
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

    print("\nNOT RETAINED (connector nothing grips -- fits, but will pull out)")
    unretained = _unretained(parts, found, by_index, freeruns)
    if unretained:
        problems += len(unretained)
        for part, holes in unretained:
            print(f"  {part.label}")
            for hole in holes:
                print(f"                    free-runs in {hole.label}")
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
    membership, _ = _rigid_clusters(parts, found, by_index, pivots)
    nbrs = _joint_neighbors(found)
    meshed = _meshed(parts, meshes)
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
            if _contact_excused(
                first, second, pair, direct, via_connector, membership, nbrs, found,
                meshed,
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
            elif j.kind in POSE_KINDS:
                # A ball joint is a legal pose, not "some other rigid fix"
                # and not a pin hinge. Skip the hinge warning.
                has_other = True
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
    _, cluster_hinges = _rigid_clusters(parts, found, by_index, pivots)
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
            if not part_faces_front(part.part):
                continue
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

    print("\nPORT ACCESS (room for the plug, then for the wire behind it)")
    blocked = port_blockers(parts, solids)
    if blocked:
        problems += len(blocked)
        for owner, name, offender, volume, zone in blocked:
            print(f"  {volume:6.0f} LDU^3  {zone:5} of port {name} on {owner.part} at "
                  f"({owner.offset[0]:g}, {owner.offset[1]:g}, {owner.offset[2]:g})")
            print(f"                    blocked by {offender.label}")
    elif any(part_ports(p.part) for p in parts):
        print("  none")
    else:
        print("  (no part in this model declares a port; skipped)")

    colors = kit_colors()

    # Before asking whether the colour is right, ask whether the part is in
    # the box at all. The colour check below skips any part it cannot find
    # in a kit, which meant a part from no kit passed in silence: a plain
    # 2x4 brick 3001, which Essential does not contain, drew no comment.
    # kit_colors() keys on both the kit design id and the aliased LDraw
    # stem, so a model written the documented way -- LDraw names, not design
    # ids -- resolves here.
    print("\nPART vs KIT (design id in no kit's parts.txt)")
    absent = [
        p
        for p in parts
        if not colors.get(part_stem(p.part)) and p.part not in proxies
    ]
    if absent:
        problems += len(absent)
        seen = set()
        for part in absent:
            if part.part in seen:
                continue
            seen.add(part.part)
            print(f"  {part.label}  is in no kit; add an alias or pick another part")
    else:
        print("  none")

    print("\nCOLOUR vs KIT")
    colour_bad = []
    for part in parts:
        if part.color == 16:
            continue
        name = LDRAW_COLOR.get(part.color)
        if not name:
            continue
        allowed = kit_colours_for(part, colors, proxies)
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


def port_blockers(
    parts: list[Placed], solids: dict[int, set[tuple[int, int, int]]]
) -> list[tuple[Placed, str, Placed, float, str]]:
    """Parts standing in the space a cable needs.

    Two zones per port, both extruded along the socket axis from its mouth:

      plug   0 .. PLUG_STANDOFF, the full 34 x 18 shell of a seated plug
      cable  PLUG_STANDOFF .. +CABLE_RUN, the narrower ribbon behind it

    A part clear of the first and fouling the second is the case that looks
    fine in a render and shoves the wire sideways on the table. The socket's
    own part is skipped: its front face is the wall both zones start from.
    """
    found: list[tuple[Placed, str, Placed, float, str]] = []
    cell = VOXEL**3
    zones = (
        ("plug", 0.0, PLUG_STANDOFF, PLUG_HALF_WIDTH, PLUG_HALF_HEIGHT),
        ("cable", PLUG_STANDOFF, PLUG_STANDOFF + CABLE_RUN,
         CABLE_HALF_WIDTH, CABLE_HALF_THICK),
    )
    for owner in parts:
        for spec in part_ports(owner.part):
            axis = v_norm(rotate_vec(owner.matrix, tuple(spec["axis"])))
            up = v_norm(rotate_vec(owner.matrix, tuple(spec.get("up", (0, 1, 0)))))
            across = v_norm(v_cross(axis, up))
            mouth = apply(owner.matrix, owner.offset, tuple(spec["origin"]))
            name = str(spec.get("name", "?"))
            for other in parts:
                if other.index == owner.index:
                    continue
                cells = solids.get(other.index)
                if not cells:
                    continue
                hits = {zone[0]: 0 for zone in zones}
                for jx, jy, jz in cells:
                    point = ((jx + 0.5) * VOXEL, (jy + 0.5) * VOXEL, (jz + 0.5) * VOXEL)
                    d = v_sub(point, mouth)
                    out = v_dot(d, axis)
                    side = abs(v_dot(d, across))
                    lift = abs(v_dot(d, up))
                    for zone, near, far, half_w, half_h in zones:
                        if near < out < far and side < half_w and lift < half_h:
                            hits[zone] += 1
                for zone, *_ in zones:
                    volume = hits[zone] * cell
                    if volume > PORT_TOLERANCE:
                        found.append((owner, name, other, volume, zone))
    return sorted(found, key=lambda f: -f[3])


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
        # Multi-step `*-steps-*` fixtures exercise the grace window, which
        # `check` on the finished model cannot see.
        if "-steps-" in ldr.name:
            code = steps_check(ldr)
        else:
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


def kit_design_ids() -> dict[str, dict]:
    """design_id -> {name, kits} across every kits/*/parts.txt."""
    out: dict[str, dict] = {}
    for path in sorted(KITS_DIR.glob(LEGO_KIT_GLOB)):
        kit = path.parent.name
        for line in path.read_text().splitlines():
            if line.startswith("#") or line.count("|") != 5:
                continue
            fields = [f.strip() for f in line.split("|")]
            if not fields[0].isdigit():
                continue
            _qty, _color, name, _cat, design, _elem = fields
            entry = out.setdefault(design, {"name": name, "kits": set()})
            entry["kits"].add(kit)
    return out


def resolve_design(design: str, lib: Library) -> tuple[str | None, str]:
    """Map a kit design ID to an LDraw file. Returns (ldraw_name, why)."""
    mapped = aliases().get(design)
    if isinstance(mapped, dict):
        ldraw = mapped.get("ldraw")
        if ldraw is None:
            return None, "alias: no LDraw geometry"
        if lib.read(ldraw) is None:
            return None, f"alias points at {ldraw}, missing from library"
        return ldraw, "alias"
    direct = f"{design}.dat"
    if lib.read(direct) is not None:
        return direct, "direct"
    return None, "no .dat at that number and no alias"


def kits_audit(strict: bool = False) -> int:
    """Sort every kit part into what the checker can and cannot see.

    Four outcomes, and only two of them are work:
      library   -- LDraw emits holes/studs; nothing to write
      annotated -- connections.yml already fills the gap
      silent    -- geometry exists but emits nothing; needs annotation
      unmapped  -- no LDraw file at all; needs an alias or a proxy
    """
    lib = Library(LIBRARY)
    designs = kit_design_ids()
    buckets: dict[str, list] = defaultdict(list)

    for design in sorted(designs, key=lambda d: (len(d), d)):
        info = designs[design]
        kits = ",".join(sorted(k.split("-")[0] for k in info["kits"]))
        ldraw, why = resolve_design(design, lib)
        if ldraw is None:
            bucket = "proxy" if "no LDraw geometry" in why else "unmapped"
            buckets[bucket].append((design, info["name"], kits, why))
            continue
        annot = _annot(ldraw)
        feats: list = []
        collect_features(lib, ldraw, IDENTITY, (0.0, 0.0, 0.0), feats)
        kinds = sorted({f"{g} {k}" for g, k, _p, _a in feats})
        detail = ", ".join(kinds) if kinds else "no primitives"
        if annot:
            role = annot.get("role", "structural")
            extra = []
            if annot.get("shafts"):
                extra.append(f"{len(annot['shafts'])} shaft(s)")
            if annot.get("features"):
                extra.append(f"{len(annot['features'])} feature(s)")
            note = f"{role}" + (f" + {', '.join(extra)}" if extra else "")
            buckets["annotated"].append((design, info["name"], kits, f"{ldraw}: {note}"))
        elif feats:
            buckets["library"].append((design, info["name"], kits, f"{ldraw}: {detail}"))
        else:
            buckets["silent"].append((design, info["name"], kits, f"{ldraw}: {detail}"))

    titles = {
        "library": "LDRAW SEES IT (holes/studs emitted; nothing to write)",
        "annotated": "ANNOTATED in connections.yml",
        "silent": "SILENT -- geometry exists but emits no clutch (needs annotation)",
        "unmapped": "UNMAPPED -- no LDraw file; needs an alias entry",
        "proxy": "NO GEOMETRY -- declared proxy-only (printed heads, cables, dog)",
    }
    for key in ("silent", "unmapped", "annotated", "library", "proxy"):
        rows = buckets[key]
        print(f"\n{titles[key]}  [{len(rows)}]")
        if not rows:
            print("  (none)")
        for design, name, kits, detail in rows:
            print(f"  {design:<8} {name[:38]:<38} {kits:<18} {detail}")

    total = sum(len(v) for v in buckets.values())
    print(
        f"\n{total} design IDs across {len(list(KITS_DIR.glob(LEGO_KIT_GLOB)))} kits: "
        f"{len(buckets['library'])} free, {len(buckets['annotated'])} annotated, "
        f"{len(buckets['silent'])} silent, {len(buckets['unmapped'])} unmapped, "
        f"{len(buckets['proxy'])} proxy."
    )
    if strict and (buckets["silent"] or buckets["unmapped"]):
        print("\nstrict: silent or unmapped parts remain")
        return 1
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

    steps_cmd = sub.add_parser(
        "steps",
        help="check every intermediate step; transients must clear next page",
    )
    steps_cmd.add_argument("model", type=Path)
    steps_cmd.add_argument(
        "--ground",
        type=float,
        help="y of the ground plane (overrides 0 !LDRCHECK GROUND in the model)",
    )

    sub.add_parser("fixtures", help="run tools/fixtures good-* / bad-* cases")

    kits_cmd = sub.add_parser(
        "kits",
        help="audit every kit part: what LDraw sees, what needs annotating",
    )
    kits_cmd.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 if any part is silent or unmapped",
    )

    args = parser.parse_args()
    if args.command == "check":
        return check(args.model, args.through_step, args.ground)
    if args.command == "holes":
        return holes(args.parts)
    if args.command == "connections":
        return connections_report(args.model, args.through_step)
    if args.command == "steps":
        return steps_check(args.model, args.ground)
    if args.command == "fixtures":
        return run_fixtures()
    if args.command == "kits":
        return kits_audit(args.strict)
    return measure(args.parts)


if __name__ == "__main__":
    sys.exit(main())
