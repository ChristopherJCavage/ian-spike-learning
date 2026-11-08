#!/usr/bin/env python3
"""Snap Circuits: check a layout, draw the panels, flip through the comic.

`ldrcheck` proves a LEGO model can be built. This does the same job for
Elenco Snap Circuits (SCB-20 Beginner, SC-100 Jr.): a build is a plain-text
layout, `circuit.snap`, and every board Ian copies block-for-block is drawn
FROM that layout, never freehand. The lesson is a comic, `deck.md`, and
every answer in it (light or dark? how many posts? red or yellow?) is worked
out from the same layout, so the answer key cannot drift from the board.

    python3 tools/snap.py check builds/snap-01-the-loop      # a build folder
    python3 tools/snap.py check some/layout.snap              # one layout
    python3 tools/snap.py render builds/snap-01-the-loop      # SVG panels
    python3 tools/snap.py preview builds/snap-01-the-loop     # preview.html
    python3 tools/snap.py bom builds/snap-01-the-loop --write # parts.txt
    python3 tools/snap.py selftest                            # fixtures

`circuit.snap` (one directive per line, `#` starts a comment):

    kits scb20[, sc100]
    grid 7x5 grid-mini             # columns x rows, and which grid block
    lift fwd                       # the spin that makes a motor's fan fly off
    step 1: grid
    step 2: B3B at 1A dir=right side=up level=1
    change colours: flip=4         # a later chapter's board
    puzzle gap: S1=on, remove=6    # a board for a puzzle page
    mission red: flip=4 => S1=on: D10 red; S1=off: D10 off
    scene watch: S1=on             # a page drawn with the switches set
    expect S1=on: D10 yellow       # claims the checker must prove
    photo c1: renders/real-c1.jpg  # a photo of the real board, and what is in it
      board: S1=on
      parts: B3B 1A+ 3A, wire3 1A 1C, S1 1C 1E, D10 3C+ 3E, egg on D10
      shows: D10 yellow

A post is the column number, then the row letter (1A is top-left: column 1,
row A). Numbers run across the top, 1 to 7. Letters run down the side, A to
E. `at A1` is accepted too, and means the same post. A block covers
`span` posts from its `at` post along `dir`: every 2-snap block is 1x3,
with its snaps on the two end posts. B3B is 3x3: its snaps are the two
corners of one edge, and `side=` says where the rest of the case lies. It
usually rides the edge of the board, snaps on row A and the case hanging
off the top. Electricity flows between blocks that share a post.

Stacking: two blocks may share ONE post, where both have a snap, and they
leave it in different directions (N, S, E or W). The one placed later sits a
level higher. Blocks never lie on top of each other along their length
(OVERLAP) and a snap never lands on plastic (BODY). A block's `level` is the
height of its higher end; its two ends may differ by one level (a tilt the
real snaps take), never more (TILT).

Assignments (in change, puzzle, mission, scene, expect, and deck tests):
`S1=on|off`, `S2=pressed|released`, `remove=N` (take step N's block away),
`hide=N` (as remove, drawn as a ?), `swap=N/KEY` (another block of the same
size), `flip=N` (turn step N's block around; flip it twice and it is back),
`add=N/KEY` (an accessory, the egg or a fan, on step N's block),
`part=N/KEY@POST/DIR/LEVEL` (a new block, step N, added on its own posts),
`launch=N` (draw step N's fan flying off: the switch must be released, and
held down the motor must spin the `lift` way), and `base=NAME` (first, to
start from a change, puzzle or mission defined above).

A mission is an answer board plus what it must do, `=> <claims>`, each claim
`<assignments>: <ID> <tokens>` and separated by `;`.

A photo is a picture of the real board (renders/real-*.jpg). `parts:` lists
every block in it by its end snaps, + marked; `board:` is the layout state
it should equal; `shows:` is what is lit in it. check fails if the layout
drifts from the photo, and if the deck shows the photo while the board on
the page before is a different one.

tools/snap/parts.json holds every block's size and behaviour; parts that
were checked against the real box are marked measured:true.

`deck.md` is the comic: chapters, and slides in order. Its format is in the
docstring of parse_deck() and in builds/_snap-template/deck.md.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import itertools
import json
import math
import os
import re
import sys
import textwrap
from dataclasses import dataclass, field, replace
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTS_JSON = ROOT / "tools" / "snap" / "parts.json"
FIXTURES = ROOT / "tools" / "snap" / "fixtures"
COMIC_DIR = ROOT / "context" / "comic"
DIRS = {"right": (0, 1), "left": (0, -1), "down": (1, 0), "up": (-1, 0)}
OPP = {"right": "left", "left": "right", "up": "down", "down": "up"}
SWITCH_WORDS = {"on": True, "pressed": True, "off": False, "released": False}
TOKENS = {"on", "off", "dim", "red", "yellow", "fwd", "rev", "fly", "blow"}

_DB: dict | None = None


def db() -> dict:
    global _DB
    if _DB is None:
        _DB = json.loads(PARTS_JSON.read_text())
    return _DB


def part_def(key: str) -> dict | None:
    return db()["parts"].get(key)


def host_keys(d: dict) -> set:
    """Parts an accessory is allowed to sit on. `on` may be one key or a list."""
    on = d.get("on")
    if not on:
        return set()
    return {on} if isinstance(on, str) else set(on)


def talk_art(bdir: Path, art: str) -> Path:
    """A pose name, or a picture path inside the build (renders/talk/...)."""
    if "/" in art or art.endswith(".jpg"):
        return bdir / art
    return COMIC_DIR / f"{art}.jpg"


def post_name(r: int, c: int) -> str:
    """Column number, then row letter. Top-left of the Beginner grid is 1A."""
    return f"{c + 1}{chr(65 + r)}"


def parse_post(text: str):
    """`1A` (column, row) or the older `A1`. Both name the same post."""
    m = re.match(r"^(\d+)([A-Z])$", text)
    if m:
        return ord(m.group(2)) - 65, int(m.group(1)) - 1
    m = re.match(r"^([A-Z])(\d+)$", text)
    if m:
        return ord(m.group(1)) - 65, int(m.group(2)) - 1
    return None


# ---------------------------------------------------------------- parsing


@dataclass
class Assign:
    sw: dict = field(default_factory=dict)  # switch key -> closed?
    remove: set = field(default_factory=set)
    hide: set = field(default_factory=set)
    swap: dict = field(default_factory=dict)  # step -> key
    flip: set = field(default_factory=set)
    add: dict = field(default_factory=dict)  # step -> accessory key
    launch: int = 0
    base: str = ""
    parts: tuple = ()  # extra blocks this board adds, as Placed

    def copy(self) -> "Assign":
        return Assign(dict(self.sw), set(self.remove), set(self.hide), dict(self.swap),
                      set(self.flip), dict(self.add), self.launch, self.base, tuple(self.parts))

    def label(self) -> str:
        bits = [f"base={self.base}"] if self.base else []
        bits += [f"{k}={'on' if v else 'off'}" for k, v in sorted(self.sw.items())]
        bits += [f"remove={n}" for n in sorted(self.remove)]
        bits += [f"hide={n}" for n in sorted(self.hide)]
        bits += [f"swap={n}/{k}" for n, k in sorted(self.swap.items())]
        bits += [f"flip={n}" for n in sorted(self.flip)]
        bits += [f"add={n}/{k}" for n, k in sorted(self.add.items())]
        bits += [f"part={p.step}/{p.key}@{post_name(p.r, p.c)}/{p.dir}/{p.level}" for p in self.parts]
        bits += [f"launch={self.launch}"] if self.launch else []
        return ", ".join(bits) or "-"


@dataclass
class Placed:
    step: int
    key: str
    line: int
    r: int = 0
    c: int = 0
    dir: str = "right"
    level: int = 1
    host: int = 0  # accessories: the step whose block they ride on
    side: str = ""  # a block with depth (B3B): where its case lies

    def defn(self) -> dict:
        return part_def(self.key) or {}

    def cells(self) -> list:
        """The snap row: `span` posts from `at` along `dir`."""
        d = self.defn()
        if d.get("kind") in ("grid", "accessory") or "span" not in d:
            return []
        dr, dc = DIRS[self.dir]
        return [(self.r + dr * i, self.c + dc * i) for i in range(d["span"])]

    def body_cells(self) -> list:
        """Posts under the rest of a deep block's case, beyond its snap row."""
        depth = self.defn().get("depth", 1)
        if depth <= 1 or self.side not in DIRS:
            return []
        sr, sc = DIRS[self.side]
        return [(r + sr * k, c + sc * k) for k in range(1, depth) for r, c in self.cells()]

    def footprint(self) -> list:
        return self.cells() + self.body_cells()

    def snaps(self) -> list:
        cells = self.cells()
        return [cells[i] for i in self.defn().get("snaps", [])]

    def ends(self) -> list:
        sn = self.snaps()
        return [sn[0], sn[-1]] if len(sn) > 1 else sn

    def plus_post(self):
        """The post under the + mark: a source's + snap, a polar load's first snap."""
        d = self.defn()
        if d.get("kind") == "source" and self.cells():
            return self.cells()[d["plus"]]
        if d.get("polarity") in ("colour", "spin", "silent") and self.snaps():
            return self.snaps()[0]
        return None


@dataclass
class Expect:
    line: int
    assign: Assign
    key: str
    tokens: set


@dataclass
class Variant:
    kind: str  # change | puzzle | mission
    name: str
    assign: Assign
    line: int
    claims: list = field(default_factory=list)  # Expect, missions only


@dataclass
class PhotoItem:
    """One block in a photo: its two end snaps, the + one marked, or the block an accessory rides on."""
    key: str
    posts: frozenset = frozenset()
    plus: tuple | None = None
    host: str = ""

    def text(self) -> str:
        if self.host:
            return f"{self.key} on {self.host}"
        names = sorted(self.posts, key=lambda rc: (rc[1], rc[0]))
        return f"{self.key} " + " ".join(post_name(*rc) + ("+" if rc == self.plus else "") for rc in names)


@dataclass
class Photo:
    name: str
    file: str
    line: int
    assign: Assign | None = None
    items: list = field(default_factory=list)  # PhotoItem
    shows: list = field(default_factory=list)  # Expect


@dataclass
class Circuit:
    path: Path
    kits: list = field(default_factory=list)
    cols: int = 0
    rows: int = 0
    grid_key: str = ""
    lift: str = ""
    placed: list = field(default_factory=list)
    scenes: list = field(default_factory=list)  # (name, Assign, line)
    expects: list = field(default_factory=list)
    variants: dict = field(default_factory=dict)  # name -> Variant, file order
    photos: list = field(default_factory=list)  # Photo
    problems: list = field(default_factory=list)  # (code, message)

    def fail(self, code: str, msg: str, line: int = 0) -> None:
        where = f"{self.path.name}:{line}: " if line else ""
        self.problems.append((code, where + msg))

    def changes(self) -> list:
        return [v for v in self.variants.values() if v.kind == "change"]


def parse_assign(text: str, circ: Circuit, line: int, start: Assign | None = None) -> Assign:
    a = start.copy() if start else Assign()
    text = text.strip()
    if text in ("", "-"):
        return a
    for i, tok in enumerate(t.strip() for t in text.split(",")):
        if "=" not in tok:
            circ.fail("SYNTAX", f"bad assignment '{tok}'", line)
            continue
        k, v = (s.strip() for s in tok.split("=", 1))
        try:
            if k == "base":
                var = circ.variants.get(v)
                if i != 0:
                    circ.fail("SYNTAX", f"base={v} must come first", line)
                elif not var:
                    circ.fail("SYNTAX", f"base={v}: no change, puzzle or mission named '{v}' above this line", line)
                else:
                    a = var.assign.copy()
                    a.base = v
            elif k in ("remove", "hide"):
                getattr(a, k).add(int(v))
            elif k == "swap":
                n, key = v.split("/")
                a.swap[int(n)] = key
            elif k == "flip":
                a.flip ^= {int(v)}
            elif k == "add":
                n, key = v.split("/")
                a.add[int(n)] = key
            elif k == "launch":
                a.launch = int(v)
            elif k == "part":
                # 9/L4@3E/up/3 — a block this board adds, on its own posts
                step_s, rest = v.split("/", 1)
                key, at = rest.split("@", 1)
                post, direction, level = at.split("/")
                rc = parse_post(post)
                if rc is None or direction not in DIRS:
                    circ.fail("SYNTAX", f"bad part '{v}' (use step/KEY@post/dir/level)", line)
                else:
                    a.parts = a.parts + (Placed(int(step_s), key, line, rc[0], rc[1], direction, int(level)),)
            else:
                d = part_def(k)
                if not d or d.get("kind") != "switch":
                    circ.fail("SYNTAX", f"'{k}' is not a switch", line)
                elif v not in SWITCH_WORDS:
                    circ.fail("SYNTAX", f"switch state '{v}' (use on/off/pressed/released)", line)
                else:
                    a.sw[k] = SWITCH_WORDS[v]
        except ValueError:
            circ.fail("SYNTAX", f"bad assignment '{tok}'", line)
    return a


STEP_RE = re.compile(r"^step\s+(\d+):\s*(\S+?)(?:\s+at\s+(\S+))?((?:\s+\w+=\S+)*)$")
CLAIM_RE = re.compile(r"^(.*?):\s+(\S+)\s+(.+)$")


def parse_photo_items(text: str, ph: Photo, circ: Circuit, line: int) -> None:
    for bit in (b.strip() for b in text.split(",") if b.strip()):
        words = bit.split()
        if len(words) == 3 and words[1] == "on":
            ph.items.append(PhotoItem(words[0], host=words[2]))
            continue
        posts, plus = [], None
        for w in words[1:]:
            rc = parse_post(w.rstrip("+"))
            if rc is None:
                circ.fail("SYNTAX", f"photo {ph.name}: '{w}' is not a post (in '{bit}')", line)
                break
            posts.append(rc)
            if w.endswith("+"):
                plus = rc
        else:
            if len(posts) != 2:
                circ.fail("PHOTO", f"photo {ph.name}: '{bit}' needs the block's two end snaps", line)
            ph.items.append(PhotoItem(words[0], frozenset(posts), plus))


def parse_photo_line(raw: str, ph: Photo, circ: Circuit, n: int) -> None:
    m = re.match(r"^(board|parts|shows):\s*(.*)$", raw)
    if not m:
        circ.fail("SYNTAX", f"photo {ph.name}: use board:, parts: or shows: (got '{raw}')", n)
        return
    key, val = m.groups()
    if key == "board":
        ph.assign = parse_assign(val, circ, n)
    elif key == "parts":
        parse_photo_items(val, ph, circ, n)
    else:
        for bit in (b.strip() for b in val.split(",") if b.strip()):
            words = bit.split()
            if len(words) < 2 or set(words[1:]) - TOKENS:
                circ.fail("SYNTAX", f"photo {ph.name}: shows '{bit}' (use '<ID> <tokens>', tokens from {' '.join(sorted(TOKENS))})", n)
                continue
            ph.shows.append(Expect(n, Assign(), words[0], set(words[1:])))


def parse_circuit(path: Path) -> Circuit:
    circ = Circuit(path)
    photo: Photo | None = None
    for n, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if raw[:1] in (" ", "\t"):
            if photo is None:
                circ.fail("SYNTAX", f"indented line with no photo above it: {line}", n)
            else:
                parse_photo_line(line, photo, circ, n)
            continue
        photo = None
        if m := re.match(r"^photo\s+([a-z0-9-]+):\s*(\S+)$", line):
            photo = Photo(m.group(1), m.group(2), n)
            if any(p.name == photo.name for p in circ.photos):
                circ.fail("SYNTAX", f"photo {photo.name}: that name is already used", n)
            circ.photos.append(photo)
        elif m := re.match(r"^kits\s+(.+)$", line):
            circ.kits = [k.strip() for k in m.group(1).split(",") if k.strip()]
        elif m := re.match(r"^grid\s+(\d+)x(\d+)\s+(\S+)$", line):
            circ.cols, circ.rows, circ.grid_key = int(m.group(1)), int(m.group(2)), m.group(3)
        elif m := re.match(r"^lift\s+(\S+)$", line):
            if m.group(1) not in ("fwd", "rev"):
                circ.fail("SYNTAX", f"lift {m.group(1)} (use fwd or rev)", n)
            else:
                circ.lift = m.group(1)
        elif m := STEP_RE.match(line):
            step, key = int(m.group(1)), m.group(2)
            p = Placed(step, circ.grid_key if key == "grid" else key, n)
            if m.group(3):
                got = parse_post(m.group(3))
                if not got:
                    circ.fail("SYNTAX", f"post '{m.group(3)}' (use 1A: column number, then row letter)", n)
                else:
                    p.r, p.c = got
            for opt in m.group(4).split():
                k, v = opt.split("=", 1)
                if k in ("dir", "side") and v not in DIRS:
                    circ.fail("SYNTAX", f"{k}={v} (use right/left/up/down)", n)
                elif k == "dir":
                    p.dir = v
                elif k == "side":
                    p.side = v
                elif k == "level" and v.isdigit():
                    p.level = int(v)
                else:
                    circ.fail("SYNTAX", f"step {step}: '{opt}' (use dir=, side= or level=)", n)
            if key != "grid" and not m.group(3):
                circ.fail("SYNTAX", f"step {step}: '{key}' needs 'at <post>'", n)
            circ.placed.append(p)
        elif m := re.match(r"^(change|puzzle|mission)\s+([a-z0-9-]+):\s*(.*)$", line):
            kind, name, rest = m.groups()
            claims = ""
            if kind == "mission":
                if "=>" not in rest:
                    circ.fail("SYNTAX", f"mission {name} needs '=> <what it must do>'", n)
                else:
                    rest, claims = rest.split("=>", 1)
            elif "=>" in rest:
                circ.fail("SYNTAX", f"only a mission has '=>' claims", n)
            if name in circ.variants:
                circ.fail("SYNTAX", f"{kind} {name}: that name is already used", n)
                continue
            var = Variant(kind, name, parse_assign(rest, circ, n), n)
            for c in (x.strip() for x in claims.split(";") if x.strip()):
                cm = CLAIM_RE.match(c)
                if not cm:
                    circ.fail("SYNTAX", f"mission {name}: bad claim '{c}' (use '<assignments>: <ID> <tokens>')", n)
                    continue
                ca = parse_assign(cm.group(1), circ, n, start=var.assign)
                var.claims.append(Expect(n, ca, cm.group(2), set(cm.group(3).split())))
            circ.variants[name] = var
        elif m := re.match(r"^scene\s+([a-z0-9-]+):\s*(.*)$", line):
            circ.scenes.append((m.group(1), parse_assign(m.group(2), circ, n), n))
        elif m := re.match(r"^expect\s+(.*?):\s+(\S+)\s+(.+)$", line):
            circ.expects.append(
                Expect(n, parse_assign(m.group(1), circ, n), m.group(2), set(m.group(3).split()))
            )
        else:
            circ.fail("SYNTAX", f"cannot read: {line}", n)
    resolve_hosts(circ)
    return circ


def resolve_hosts(circ: Circuit) -> None:
    """An accessory sits on the block whose first post it names."""
    for p in circ.placed:
        d = part_def(p.key) or {}
        if d.get("kind") != "accessory":
            continue
        cands = [h for h in circ.placed if h is not p and h.cells() and h.cells()[0] == (p.r, p.c)]
        host = next((h for h in cands if h.key in host_keys(d)), cands[0] if cands else None)
        p.host = host.step if host else 0


def read_inventory(kit: str) -> dict:
    info = db()["kits"].get(kit)
    if not info:
        return {}
    f = ROOT / info["dir"] / "parts.txt"
    out: dict = {}
    if not f.exists():
        return out
    for raw in f.read_text().splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        cols = [c.strip() for c in raw.split("|")]
        out[cols[1]] = out.get(cols[1], 0) + int(cols[0])
    return out


# --------------------------------------------------------------- analysis


@dataclass
class Edge:
    u: tuple
    v: tuple
    part: Placed
    kind: str  # wire | switch | load


@dataclass
class Graph:
    edges: list
    plus: tuple | None
    minus: tuple | None
    sources: int
    open_switches: list  # (u, v, Placed)


def turned(p: Placed) -> Placed:
    cells = p.cells()
    if not cells:
        return p
    r, c = cells[-1]
    return replace(p, r=r, c=c, dir=OPP[p.dir])


def effective_parts(circ: Circuit, a: Assign) -> list:
    out = []
    for p in circ.placed:
        if p.step in a.remove or p.step in a.hide:
            continue
        q = p
        if p.step in a.swap:
            deep = (part_def(a.swap[p.step]) or {}).get("depth", 1) > 1
            q = replace(p, key=a.swap[p.step], side=p.side if deep else "")
        if p.step in a.flip:
            q = turned(q)
        out.append(q)
    by_step = {q.step: q for q in out}
    res = []
    for q in out:
        d = q.defn()
        if d.get("kind") == "accessory":
            h = by_step.get(q.host)
            if not h or h.key not in host_keys(d):
                continue  # the block it rode on was swapped out or removed
        res.append(q)
    for n, key in sorted(a.add.items()):
        h, d = by_step.get(n), part_def(key) or {}
        if h and h.key in host_keys(d):
            res.append(Placed(1000 + n, key, 0, host=n))
    for p in a.parts:
        if p.step in a.remove or p.step in a.hide:
            continue
        res.append(p)
    return res


def build_graph(parts: list, a: Assign) -> Graph:
    edges, openers, plus, minus, sources = [], [], None, None, 0
    for p in parts:
        d = p.defn()
        kind = d.get("kind")
        if kind in (None, "grid", "accessory"):
            continue
        cells, sn = p.cells(), p.snaps()
        if kind == "source":
            sources += 1
            plus, minus = cells[d["plus"]], cells[d["minus"]]
        elif kind == "wire":
            edges += [Edge(sn[i], sn[i + 1], p, "wire") for i in range(len(sn) - 1)]
        elif kind == "switch":
            if a.sw.get(p.key, False):
                edges.append(Edge(sn[0], sn[-1], p, "switch"))
            else:
                openers.append((sn[0], sn[-1], p))
        elif kind == "load":
            edges.append(Edge(sn[0], sn[-1], p, "load"))
    return Graph(edges, plus, minus, sources, openers)


def adjacency(g: Graph) -> dict:
    adj: dict = {}
    for e in g.edges:
        adj.setdefault(e.u, []).append((e.v, e))
        adj.setdefault(e.v, []).append((e.u, e))
    return adj


def find_paths(g: Graph, limit: int = 400) -> list:
    """Simple paths from + to -; each is a list of (edge, from, to)."""
    if g.plus is None or g.minus is None:
        return []
    adj, paths = adjacency(g), []

    def dfs(node, seen, trail):
        if len(paths) >= limit:
            return
        if node == g.minus:
            paths.append(list(trail))
            return
        for nxt, e in adj.get(node, []):
            if nxt in seen:
                continue
            seen.add(nxt)
            trail.append((e, node, nxt))
            dfs(nxt, seen, trail)
            trail.pop()
            seen.discard(nxt)

    dfs(g.plus, {g.plus}, [])
    return paths


def is_short(g: Graph) -> bool:
    if g.plus is None or g.minus is None:
        return False
    adj, seen, todo = adjacency(g), {g.plus}, [g.plus]
    while todo:
        node = todo.pop()
        for nxt, e in adj.get(node, []):
            if e.kind != "load" and nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    return g.minus in seen


def path_is_live(path: list) -> bool:
    for e, frm, _ in path:
        if e.kind == "load" and e.part.defn().get("polarity") == "silent" and frm != e.u:
            return False
    return True


def dead_end_walk(g: Graph) -> list:
    """Longest walk from + that current could make before it hits a gap."""
    if g.plus is None:
        return []
    adj, best = adjacency(g), [g.plus]

    def dfs(node, seen, trail):
        nonlocal best
        if len(trail) > len(best):
            best = list(trail)
        for nxt, e in adj.get(node, []):
            if nxt in seen:
                continue
            if e.kind == "load" and e.part.defn().get("polarity") == "silent" and node != e.u:
                continue
            seen.add(nxt)
            trail.append(nxt)
            dfs(nxt, seen, trail)
            trail.pop()
            seen.discard(nxt)

    dfs(g.plus, {g.plus}, [g.plus])
    return best


@dataclass
class Result:
    short: bool
    live: list  # live paths
    tokens: dict  # step -> set of words
    parts: list
    graph: Graph
    dead: list  # posts of the longest dead-end walk (only if no live path)


def evaluate(circ: Circuit, a: Assign) -> Result:
    parts = effective_parts(circ, a)
    g = build_graph(parts, a)
    live = [p for p in find_paths(g) if path_is_live(p)]
    tokens = {p.step: {"off"} for p in parts if p.defn().get("kind") == "load"}
    fans = {p.host for p in parts if p.defn().get("kind") == "accessory" and p.defn().get("blades")}
    for path in live:
        loads = [(e, frm) for e, frm, _ in path if e.kind == "load"]
        for e, frm in loads:
            d, fwd = e.part.defn(), frm == e.u
            t = {"on"}
            if len(loads) >= 2:
                t.add("dim")
            if d.get("polarity") == "colour":
                t.add(d["colour_forward"] if fwd else d["colour_reverse"])
            if d.get("polarity") == "spin":
                way = "fwd" if fwd else "rev"
                t.add(way)
                if circ.lift and e.part.step in fans:
                    t.add("fly" if way == circ.lift else "blow")
            cur = tokens[e.part.step]
            cur.discard("off")
            cur |= t
    dead = [] if live else dead_end_walk(g)
    return Result(is_short(g), live, tokens, parts, g, dead)


def closed_all(circ: Circuit, a: Assign) -> Assign:
    b = a.copy()
    b.sw = {p.key: True for p in effective_parts(circ, a) if p.defn().get("kind") == "switch"}
    return b


# ----------------------------------------------------------------- checks


def named_assigns(circ: Circuit) -> list:
    """(label, Assign, line) for every board state the layout talks about."""
    out = [(f"scene {n}", a, ln) for n, a, ln in circ.scenes]
    out += [(f"expect line {e.line}", e.assign, e.line) for e in circ.expects]
    for v in circ.variants.values():
        out.append((f"{v.kind} {v.name}", v.assign, v.line))
        out += [(f"mission {v.name} claim", c.assign, v.line) for c in v.claims]
    out += [(f"photo {ph.name}", ph.assign, ph.line) for ph in circ.photos if ph.assign]
    return out


def scenarios(circ: Circuit) -> list:
    """Every board state the layout talks about, plus each one's worst
    case: every switch held closed."""
    out = [("all switches closed", closed_all(circ, Assign()))]
    for label, a, _ in named_assigns(circ):
        out.append((label, a))
        worst = closed_all(circ, a)
        if worst.sw != a.sw:
            out.append((f"{label} with every switch closed", worst))
    return out


def need_counts(circ: Circuit) -> dict:
    """The most of each block the lesson ever has on the board at once."""
    need: dict = {}
    for a in [Assign()] + [a for _, a, _ in named_assigns(circ)]:
        here: dict = {}
        for p in effective_parts(circ, a):
            here[p.key] = here.get(p.key, 0) + 1
        for k, q in here.items():
            need[k] = max(need.get(k, 0), q)
    return need


def part_fact_problems(key: str, d: dict) -> list:
    """What every real block of this kind is, checked against parts.json.
    These are the facts Chris's photos settled; a typo here would quietly
    redraw every board wrong, so check refuses it."""
    out = []
    kind, span, snaps = d.get("kind"), d.get("span"), d.get("snaps")
    where = f"parts.json {key}"
    if kind == "wire":
        n = int(d.get("printed", "0")) if str(d.get("printed", "")).isdigit() else None
        if n and (span != n or snaps != list(range(n))):
            out.append(("PARTS", f"{where}: a {n}-snap wire spans {n} posts with a snap on every one (span {n}, snaps {list(range(n))})"))
    elif kind in ("switch", "load"):
        if span != 3 or snaps != [0, 2]:
            out.append(("PARTS", f"{where}: span {span}, snaps {snaps}. Every 2-snap block is 1x3: span 3, snaps [0, 2] at the two end posts, nothing in the middle"))
    elif kind == "source":
        if snaps != [0, span - 1 if span else 0]:
            out.append(("PARTS", f"{where}: a battery holder's two snaps are the two ends of its snap edge"))
        if key == "B3B" and (span != 3 or d.get("depth") != 3 or not d.get("hangs")):
            out.append(("PARTS", f"{where}: B3B is a 3x3 module (span 3, depth 3) that can hang off the edge (hangs: true); "
                                 f"got span {span}, depth {d.get('depth', 1)}"))
    elif kind == "grid" and key == "grid-mini" and (d.get("cols"), d.get("rows")) != (7, 5):
        out.append(("PARTS", f"{where}: the Beginner grid is 7 posts across (1-7) by 5 down (A-E)"))
    return out


def stacks(parts: list) -> dict:
    """post -> the blocks with a snap there, bottom first."""
    at: dict = {}
    for p in parts:
        for s in p.snaps():
            at.setdefault(s, []).append(p)
    for s in at:
        at[s].sort(key=lambda q: (q.level, q.step))
    return at


def end_heights(p: Placed, at: dict) -> list:
    """How high each end of `p` sits: 1 on the grid, +1 for every block under it there."""
    return [1 + sum(1 for q in at.get(e, []) if q.level < p.level) for e in p.ends()]


def placement_problems(circ: Circuit, parts: list, strict: bool = True) -> list:
    """(code, message, line) for where the blocks of one board sit.

    `strict` boards are real builds; a board with a block pulled out for a
    puzzle is not, so it skips the height checks (the rest would drop down)."""
    out = []
    body = [p for p in parts if p.defn().get("kind") not in (None, "grid", "accessory")]
    on = lambda rc: 0 <= rc[0] < circ.rows and 0 <= rc[1] < circ.cols
    who = lambda p: f"step {p.step} {p.key}"

    def add(code, p, msg):
        out.append((code, msg, p.line))

    for p in body:
        d = p.defn()
        if p.level < 1:
            add("LEVEL", p, f"{who(p)}: level must be 1 or more")
        off = [c for c in p.cells() if not on(c)]
        if off:
            what = "its snap row" if d.get("depth", 1) > 1 else "it"
            add("OFF_GRID", p, f"{who(p)}: {what} reaches {post_name(*off[0])}, off the {circ.cols}x{circ.rows} grid")
        if d.get("depth", 1) > 1:
            if p.side not in DIRS or p.side in (p.dir, OPP[p.dir]):
                add("HANG", p, f"{who(p)} is {d['span']}x{d['depth']}: its snaps are one edge, and side= says where the rest "
                               f"of the case lies, across that edge (side=up hangs it off the top of row A)")
            elif not d.get("hangs") and any(not on(c) for c in p.body_cells()):
                add("OFF_GRID", p, f"{who(p)}: its case reaches off the grid, and this block cannot hang")
        elif p.side:
            add("HANG", p, f"{who(p)}: side= is only for a block with a case beyond its snaps (B3B)")
    for i, p in enumerate(body):
        fp = set(p.footprint())
        for q in body[i + 1:]:
            shared = fp & set(q.footprint())
            names = ", ".join(post_name(*c) for c in sorted(shared, key=lambda rc: (rc[1], rc[0])))
            if len(shared) >= 2:
                add("OVERLAP", q, f"{who(p)} and {who(q)} lie on top of each other ({names}). Blocks only stack where "
                                  f"their end snaps meet, one post, and leave it in different directions")
            elif shared:
                cell = next(iter(shared))
                if cell not in p.snaps() or cell not in q.snaps():
                    plastic = p if cell not in p.snaps() else q
                    add("BODY", q, f"{who(p)} and {who(q)} meet at {names}, but that is {who(plastic)}'s plastic, "
                                   f"not a snap. Snaps only stack on snaps")
    at = stacks(body)
    for s, stack in at.items():
        for a, b in zip(stack, stack[1:]):
            if a.level == b.level:
                add("COLLISION", b, f"{who(a)} and {who(b)} are both on {post_name(*s)} at level {a.level}; one must sit a level higher")
            elif a.step > b.step:
                add("BUILD_ORDER", b, f"{who(b)} goes on top of {who(a)} at {post_name(*s)}, which is placed later")
    if strict:
        for p in body:
            hs = end_heights(p, at)
            if not hs:
                continue
            top, low = max(hs), min(hs)
            if p.level > top:
                add("UNSUPPORTED", p, f"{who(p)} says level {p.level}, but nothing holds it up there: its ends sit at level "
                                      f"{' and '.join(str(h) for h in hs)} ({' and '.join(post_name(*e) for e in p.ends())})")
            elif top - low > 1:
                hi, lo = p.ends()[hs.index(top)], p.ends()[hs.index(low)]
                add("TILT", p, f"{who(p)} tips over: level {top} at {post_name(*hi)} but level {low} at {post_name(*lo)}. "
                               f"One level is as far as a block bends")
    return out


def board_items(parts: list) -> list:
    """The blocks on a board the way a photo lists them."""
    by_step = {p.step: p for p in parts}
    out = []
    for p in parts:
        d = p.defn()
        if d.get("kind") in (None, "grid"):
            continue
        if d.get("kind") == "accessory":
            host = by_step.get(p.host)
            out.append(PhotoItem(p.key, host=host.key if host else "?"))
        else:
            out.append(PhotoItem(p.key, frozenset(p.ends()), p.plus_post()))
    return out


def item_diff(want: list, got: list) -> tuple:
    """(in want only, in got only) as text, comparing blocks, ends and + marks."""
    sig = lambda it: (it.key, it.posts, it.plus, it.host)
    w, g = [sig(i) for i in want], [sig(i) for i in got]
    only_w = [i.text() for i in want if w.count(sig(i)) > g.count(sig(i))]
    only_g = [i.text() for i in got if g.count(sig(i)) > w.count(sig(i))]
    return sorted(set(only_w)), sorted(set(only_g))


def photo_problems(circ: Circuit, ph: Photo) -> list:
    out = []
    if ph.assign is None:
        return [("PHOTO", f"photo {ph.name}: needs a board: line (the layout state the photo shows)")]
    if not ph.items:
        return [("PHOTO", f"photo {ph.name}: needs a parts: line (every block in the photo)")]
    for it in ph.items:
        d = part_def(it.key)
        if not d:
            out.append(("PHOTO", f"photo {ph.name}: no such block '{it.key}'"))
        elif not it.host and it.plus is None and (d.get("polarity") in ("colour", "spin", "silent") or d.get("kind") == "source"):
            out.append(("PHOTO", f"photo {ph.name}: {it.text()} -- mark which end has the + (like 3E+)"))
        elif not it.host and it.plus is not None and not (d.get("polarity") in ("colour", "spin", "silent") or d.get("kind") == "source"):
            out.append(("PHOTO", f"photo {ph.name}: {it.key} has no + end; drop the + from {it.text()}"))
    if out:
        return out
    parts = effective_parts(circ, ph.assign)
    only_photo, only_board = item_diff(ph.items, board_items(parts))
    if only_photo or only_board:
        bits = []
        if only_photo:
            bits.append("the photo has " + "; ".join(only_photo))
        if only_board:
            bits.append("the layout has " + "; ".join(only_board))
        out.append(("PHOTO", f"photo {ph.name} ({ph.file}) does not match the board {ph.assign.label()}: " + ", but ".join(bits)))
    for e in ph.shows:
        msg = claim_problem(circ, replace(e, assign=ph.assign))
        if msg:
            out.append(("PHOTO", f"photo {ph.name} shows {e.key} {' '.join(sorted(e.tokens))}, but {msg}"))
    return out


def validate_assign(circ: Circuit, label: str, a: Assign) -> list:
    out = []
    nums = {p.step for p in circ.placed} | {p.step for p in a.parts}
    named = a.remove | a.hide | set(a.swap) | a.flip | set(a.add) | ({a.launch} if a.launch else set())
    for n in sorted(named):
        if n not in nums:
            out.append(("ASSIGN", f"{label}: no step {n}"))
    for n, key in a.swap.items():
        old = next((p for p in circ.placed if p.step == n), None)
        d = part_def(key)
        if old and (not d or d.get("span") != old.defn().get("span") or d.get("kind") in ("grid", "accessory")):
            out.append(("ASSIGN", f"{label}: cannot swap step {n} ({old.key}) for '{key}': unknown or a different size"))
        elif d and d["kit"] != "both" and d["kit"] not in circ.kits:
            out.append(("WRONG_KIT", f"{label}: {key} is from the {d['kit']} box, which this build does not list"))
    eff = {p.step: p for p in effective_parts(circ, a)}
    for n in a.flip:
        if n in eff and not eff[n].cells():
            out.append(("ASSIGN", f"{label}: step {n} ({eff[n].key}) has no ends to turn around"))
    for n, key in a.add.items():
        d = part_def(key)
        if not d or d.get("kind") != "accessory":
            out.append(("ASSIGN", f"{label}: '{key}' is not an accessory"))
        elif n in eff and eff[n].key not in host_keys(d):
            out.append(("ASSIGN", f"{label}: {key} rides on {' or '.join(sorted(host_keys(d)))}, but step {n} is {eff[n].key} there"))
        elif d["kit"] != "both" and d["kit"] not in circ.kits:
            out.append(("WRONG_KIT", f"{label}: {key} is from the {d['kit']} box, which this build does not list"))
    seen_steps = {p.step for p in circ.placed}
    for p in a.parts:
        if p.step in seen_steps:
            out.append(("ASSIGN", f"{label}: part step {p.step} is already used"))
        seen_steps.add(p.step)
        d = part_def(p.key)
        if not d or d.get("kind") in ("grid", "accessory", None):
            out.append(("ASSIGN", f"{label}: part {p.key} has to be a real block, not a cover"))
            continue
        if d["kit"] != "both" and d["kit"] not in circ.kits:
            out.append(("WRONG_KIT", f"{label}: {p.key} is from the {d['kit']} box, which this build does not list"))
        if d.get("depth", 1) > 1:
            out.append(("HANG", f"{label}: part= cannot place {p.key}; give it its own step with side="))
    if a.parts or a.swap or a.flip:
        base = {(c, m) for c, m, _ in placement_problems(circ, circ.placed)}
        strict = not (a.remove or a.hide)
        for code, msg, _ in placement_problems(circ, effective_parts(circ, a), strict):
            if (code, msg) not in base:
                out.append((code, f"{label}: {msg}"))
    if a.launch and a.launch in nums:
        fan = [q for q in effective_parts(circ, a) if q.defn().get("blades") and q.host == a.launch]
        if not circ.lift:
            out.append(("ASSIGN", f"{label}: launch= needs a `lift fwd|rev` line"))
        elif not fan:
            out.append(("ASSIGN", f"{label}: launch={a.launch}, but step {a.launch} has no fan on it"))
        else:
            if evaluate(circ, a).tokens.get(a.launch, {"off"}) != {"off"}:
                out.append(("ASSIGN", f"{label}: the motor is still running; the fan only flies off once the switch is let go"))
            if "fly" not in evaluate(circ, closed_all(circ, a)).tokens.get(a.launch, set()):
                out.append(("ASSIGN", f"{label}: held down, this motor spins the blowing way, so the fan would stay on"))
    return out


def claim_problem(circ: Circuit, e: Expect) -> str | None:
    ev = evaluate(circ, e.assign)
    hits = [p for p in ev.parts if p.key == e.key and p.defn().get("kind") == "load"]
    if not hits:
        return f"with {e.assign.label()}: no load '{e.key}' in the circuit"
    for p in hits:
        got = ev.tokens[p.step]
        ok = got == {"off"} if "off" in e.tokens else e.tokens <= got
        if not ok:
            why = ""
            if got == {"off"}:
                why = " (battery is shorted)" if ev.short else " (no complete loop from + to - through it)"
            return f"with {e.assign.label()}: {e.key} should be {' '.join(sorted(e.tokens))} but is {' '.join(sorted(got))}{why}"
    return None


def check_circuit(circ: Circuit) -> tuple:
    """Returns (problems, warnings) as lists of (code, text)."""
    warns: list = []

    def fail(code, msg, line=0):
        circ.fail(code, msg, line)

    if not circ.kits:
        fail("KITS", "no `kits` line")
    for k in circ.kits:
        if k not in db()["kits"]:
            fail("KITS", f"unknown kit '{k}'")
    if not circ.cols or not circ.rows:
        fail("GRID", "no `grid CxR key` line")
    gd = part_def(circ.grid_key)
    if circ.grid_key and (not gd or gd.get("kind") != "grid"):
        fail("GRID", f"'{circ.grid_key}' is not a grid block")
    elif gd and (circ.cols > gd["cols"] or circ.rows > gd["rows"]):
        fail("GRID", f"grid {circ.cols}x{circ.rows} is bigger than a {circ.grid_key} ({gd['cols']}x{gd['rows']})")

    steps = [p.step for p in circ.placed]
    if sorted(steps) != list(range(1, len(steps) + 1)) or steps != sorted(steps):
        fail("STEPS", f"steps must run 1..{len(steps)} in order, got {steps}")
    grids = [p for p in circ.placed if p.defn().get("kind") == "grid"]
    if len(grids) != 1 or (grids and grids[0].step != 1):
        fail("GRID", "exactly one `step 1: grid` is required, and it comes first")

    body = []
    for p in circ.placed:
        d = part_def(p.key)
        if not d:
            fail("UNKNOWN_PART", f"step {p.step}: no such block '{p.key}' (see tools/snap/parts.json)", p.line)
            continue
        if d["kit"] != "both" and d["kit"] not in circ.kits:
            fail("WRONG_KIT", f"step {p.step}: {p.key} is from the {d['kit']} box, which this build does not list", p.line)
        if d["kit"] == "both" and not any(k in ("scb20", "sc100") for k in circ.kits):
            fail("WRONG_KIT", f"step {p.step}: {p.key} needs a Snap Circuits kit", p.line)
        if d["kind"] not in ("grid", "accessory"):
            body.append(p)
    for key in sorted(need_counts(circ)):
        d = part_def(key)
        if d and "measured" in d and not d["measured"]:
            warns.append(("UNMEASURED", f"{key} geometry is not measured against a real box"))

    # what every real block is; the photos settled these
    for key, d in sorted(db()["parts"].items()):
        for code, msg in part_fact_problems(key, d):
            fail(code, msg)

    # placement: bounds, the battery's overhang, overlaps, stacks, heights
    for code, msg, line in placement_problems(circ, body):
        fail(code, msg, line)
    for p in circ.placed:
        d = p.defn()
        if d.get("kind") == "accessory":
            host = next((h for h in body if h.step == p.host), None)
            if not host or host.key not in host_keys(d):
                fail("ACCESSORY", f"step {p.step}: {p.key} goes on {' or '.join(sorted(host_keys(d)))}; put `at` on that block's first post", p.line)
            elif host.step > p.step:
                fail("BUILD_ORDER", f"step {p.step}: {p.key} goes on {host.key}, which is placed later", p.line)

    # every named board state only names real steps and fitting blocks
    for label, a, ln in named_assigns(circ):
        for code, msg in validate_assign(circ, label, a):
            fail(code, msg, ln)

    # power
    sources = [p for p in body if p.defn().get("kind") == "source"]
    if len(sources) != 1:
        fail("SOURCE", f"need exactly one battery holder, found {len(sources)}")
    volts = sources[0].defn().get("volts", 0) if sources else 0

    # bill of materials: quantity never exceeds what the listed kits hold
    have: dict = {}
    for k in circ.kits:
        for key, q in read_inventory(k).items():
            have[key] = have.get(key, 0) + q
    for key, q in sorted(need_counts(circ).items()):
        if key in have and q > have[key]:
            fail("BOM", f"uses {q}x {key} but the listed kits hold {have[key]}")
        elif key not in have and part_def(key) and part_def(key)["kit"] in (*circ.kits, "both"):
            fail("BOM", f"uses {key}, which is not in the listed kits' parts.txt")

    # electrical: shorts, voltage, and every claim
    if sources:
        flagged = set()
        for label, a in scenarios(circ):
            ev = evaluate(circ, a)
            if ev.short and "SHORT" not in flagged:
                flagged.add("SHORT")
                fail("SHORT", f"{label}: wires and closed switches join battery + to battery - with nothing in between")
            if not ev.short:
                for step, toks in ev.tokens.items():
                    p = next((q for q in ev.parts if q.step == step), None)
                    mv = p.defn().get("max_volts", 99) if p else 99
                    if toks != {"off"} and mv < volts and (p.key, "V") not in flagged:
                        flagged.add((p.key, "V"))
                        fail("OVERVOLT", f"{label}: {p.key} (step {step}) is rated {mv} V but sits on a {volts} V battery holder")
        for e in circ.expects:
            msg = claim_problem(circ, e)
            if msg:
                fail("EXPECT", msg, e.line)
        for v in circ.variants.values():
            if v.kind != "mission":
                continue
            if not v.claims:
                fail("MISSION", f"mission {v.name} says nothing it must do", v.line)
            for c in v.claims:
                msg = claim_problem(circ, c)
                if msg:
                    fail("MISSION", f"mission {v.name}: {msg}", v.line)

    # photos of the real board: the layout must be what the camera saw
    for ph in circ.photos:
        for code, msg in photo_problems(circ, ph):
            fail(code, msg, ph.line)

    out, seen = [], set()
    for pr in circ.problems:
        if pr not in seen:
            seen.add(pr)
            out.append(pr)
    return out, warns


# ------------------------------------------------------------ number facts


class FactError(Exception):
    pass


def frac_text(x: Fraction) -> str:
    whole, rest = divmod(x.numerator, x.denominator)
    if rest == 0:
        return str(whole)
    return f"{whole} {rest}/{x.denominator}" if whole else f"{rest}/{x.denominator}"


NUM_RE = re.compile(r"(\d+)\s+(\d+)/(\d+)|(\d+)/(\d+)|(\d+)")


def read_number(text: str) -> Fraction | None:
    m = NUM_RE.search(text)
    if not m:
        return None
    if m.group(1):
        return int(m.group(1)) + Fraction(int(m.group(2)), int(m.group(3)))
    if m.group(4):
        return Fraction(int(m.group(4)), int(m.group(5)))
    return Fraction(int(m.group(6)))


def calc(expr: str) -> Fraction:
    """+, -, x (or *), / and brackets over whole numbers, fractions and
    mixed numbers like 4 1/2. Small on purpose."""
    toks = re.findall(r"\d+\s+\d+/\d+|\d+/\d+|\d+|[-+x*×/()]", expr)
    if "".join(toks).replace(" ", "") != re.sub(r"\s+", "", expr):
        raise FactError(f"calc can only read numbers and + - x / ( ): '{expr}'")
    pos = 0

    def peek():
        return toks[pos] if pos < len(toks) else None

    def take():
        nonlocal pos
        pos += 1
        return toks[pos - 1]

    def atom():
        t = take() if peek() else None
        if t == "(":
            v = sum_()
            if take() != ")":
                raise FactError(f"calc: missing ) in '{expr}'")
            return v
        if t and t[0].isdigit():
            return read_number(t)
        raise FactError(f"calc: cannot read '{expr}'")

    def prod():
        v = atom()
        while peek() in ("x", "*", "×", "/"):
            op = take()
            v = v / atom() if op == "/" else v * atom()
        return v

    def sum_():
        v = prod()
        while peek() in ("+", "-"):
            v = v + prod() if take() == "+" else v - prod()
        return v

    v = sum_()
    if peek() is not None:
        raise FactError(f"calc: cannot read '{expr}'")
    return v


def kid_result(p: Placed, toks: set) -> str:
    eff = p.defn().get("effect")
    if toks == {"off"}:
        return {"light": "dark", "sound": "quiet", "spin": "still"}.get(eff, "off")
    if eff == "light":
        return next((t for t in ("red", "yellow") if t in toks), "light")
    if eff == "sound":
        return "honk"
    if eff == "spin":
        way = "clockwise" if "fwd" in toks else "counterclockwise"
        return way + (" and flies" if "fly" in toks else "")
    return "on"


def board_result(circ: Circuit, a: Assign) -> str:
    ev = evaluate(circ, a)
    words = [kid_result(p, ev.tokens[p.step]) for p in ev.parts if p.step in ev.tokens]
    return " + ".join(words) or "nothing"


def assign_from(circ: Circuit, text: str) -> tuple:
    k = len(circ.problems)
    a = parse_assign(text, circ, 0)
    errs = [m for _, m in circ.problems[k:]]
    del circ.problems[k:]
    errs += [m for _, m in validate_assign(circ, f"'{text}'", a)]
    return a, errs


def loop_cells(circ: Circuit, ev: Result) -> list:
    """The posts the water passes, in order: out of + and round to -, then
    back through the battery holder."""
    if not ev.live:
        return []
    g = ev.graph
    cells = [g.plus] + [to for _, _, to in ev.live[0]]
    src = next(p for p in ev.parts if p.defn().get("kind") == "source")
    inside = src.cells()
    if inside and inside[0] == g.minus:
        inside = inside[::-1]
    for c in reversed(inside):
        if c not in cells:
            cells.append(c)
    return cells


def toggles_from(circ: Circuit, text: str, base: Assign) -> list:
    """(table header, kind, what) for each choice a settings table varies."""
    out = []
    by = {p.step: p for p in circ.placed}
    for t in (x.strip() for x in text.split(",") if x.strip()):
        if m := re.match(r"^flip=(\d+)$", t):
            n = int(m.group(1))
            key = base.swap.get(n, by[n].key if n in by else "?")
            out.append((f"{key} turned?", "flip", n))
        elif m := re.match(r"^swap=(\d+)/(\S+)$", t):
            n, new = int(m.group(1)), m.group(2)
            old = base.swap.get(n, by[n].key if n in by else "?")
            out.append((f"{old} or {new}?", "swap", (n, new)))
        elif part_def(t) and part_def(t).get("kind") == "switch":
            out.append((f"{part_def(t).get('kid', t)} ({t})", "switch", t))
        else:
            raise FactError(f"'{t}' is not a switch, flip=N or swap=N/KEY")
    return out


def settings_rows(circ: Circuit, toggles: list, base: Assign) -> list:
    rows = []
    for bits in itertools.product((False, True), repeat=len(toggles)):
        a = base.copy()
        cells = []
        for (label, kind, what), on in zip(toggles, bits):
            if kind == "switch":
                a.sw[what] = on
                cells.append("on" if on else "off")
            elif kind == "flip":
                if on:
                    a.flip ^= {what}
                cells.append("yes" if on else "no")
            else:
                n, new = what
                old = base.swap.get(n) or next((p.key for p in circ.placed if p.step == n), "?")
                if on:
                    a.swap[n] = new
                cells.append(new if on else old)
        rows.append(cells + [board_result(circ, a)])
    return rows


def compute_fact(circ: Circuit, spec: str) -> dict:
    """{'answer': str, 'show': str, 'rows': [...], 'head': [...]}; raises FactError."""
    head, _, tail = spec.partition("@")
    words = head.split()
    if not words:
        raise FactError("empty fact")
    kind, args = words[0], words[1:]
    a, errs = assign_from(circ, tail.strip()) if tail.strip() else (Assign(), [])
    if errs:
        raise FactError(errs[0])
    if kind == "calc":
        expr = " ".join(args)
        v = calc(expr)
        return {"answer": frac_text(v), "show": f"{expr} = {frac_text(v)}"}
    if kind == "grid-posts":
        gd = part_def(circ.grid_key) or {}
        n = gd.get("cols", 0) * gd.get("rows", 0)
        return {"answer": str(n), "show": f"{gd.get('cols')} across x {gd.get('rows')} down = {n} posts"}
    if kind == "volts":
        src = next((p for p in effective_parts(circ, a) if p.defn().get("kind") == "source"), None)
        if not src or not src.defn().get("cells"):
            raise FactError("no battery holder with a `cells` count in parts.json")
        cells = src.defn()["cells"]
        v = Fraction(3, 2) * cells
        return {"answer": frac_text(v), "show": " + ".join(["1 1/2"] * cells) + f" = {frac_text(v)} volts"}
    if kind == "loop-posts":
        ev = evaluate(circ, a)
        cells = loop_cells(circ, ev)
        if not cells:
            raise FactError(f"loop-posts: with {a.label()} there is no loop")
        return {"answer": str(len(cells)), "show": "The water goes past " + ", ".join(post_name(*c) for c in cells) + f": {len(cells)} posts."}
    if kind == "post-of":
        if not args or not args[0].isdigit():
            raise FactError("post-of needs a step number")
        p = next((q for q in effective_parts(circ, a) if q.step == int(args[0])), None)
        if not p or not p.cells():
            raise FactError(f"post-of: no block at step {args[0]}")
        names = [post_name(*c) for c in p.cells()]
        return {"answer": " and ".join(names), "show": f"{p.defn().get('kid', p.key)} ({p.key}) sits on " + " and ".join(names) + "."}
    if kind == "flip-colour":
        if len(args) != 3 or args[1] != "of" or not args[0].isdigit() or not args[2].isdigit():
            raise FactError("use: flip-colour K of N @ <assignments>")
        k, n = int(args[0]), int(args[2])
        b = a.copy()
        if k % 2:
            b.flip ^= {n}
        toks = evaluate(circ, b).tokens.get(n)
        col = next((t for t in ("red", "yellow") if toks and t in toks), None)
        if not col:
            raise FactError(f"flip-colour: step {n} does not light a colour there")
        return {"answer": col, "show": f"{k} flips is {'odd' if k % 2 else 'even'}, so it ends {col}."}
    if kind in ("settings", "shows"):
        toggles = toggles_from(circ, " ".join(args), a)
        rows = settings_rows(circ, toggles, a)
        head = [t[0] for t in toggles] + ["what happens"]
        if kind == "settings":
            n = len(rows)
            return {"answer": str(n), "show": " x ".join(["2"] * len(toggles)) + f" = {n} ways to set it", "rows": rows, "head": head}
        n = len({r[-1] for r in rows})
        return {"answer": str(n), "show": f"{len(rows)} ways to set it, but only {n} different shows", "rows": rows, "head": head}
    if kind == "keeps-on":
        if not args:
            raise FactError("keeps-on needs a block ID")
        ev = evaluate(circ, a)
        if not ev.live:
            raise FactError("keeps-on: that board does not work to begin with")
        wires = sorted({e.part.step for e, _, _ in ev.live[0] if e.kind == "wire"})
        keep = []
        for st in wires:
            b = a.copy()
            b.remove.add(st)
            evb = evaluate(circ, b)
            if any(p.key == args[0] and evb.tokens.get(p.step, {"off"}) != {"off"} for p in evb.parts):
                keep.append(st)
        ans = "none" if not keep else ", ".join(f"step {s}" for s in keep)
        return {"answer": ans, "show": f"Take out any one of the {len(wires)} tubes and the {args[0]} goes off." if not keep else ans}
    if kind == "blades":
        if not args or not args[0].isdigit():
            raise FactError("use: blades K @ <assignments>")
        fan = next((q for q in effective_parts(circ, a) if q.defn().get("blades")), None)
        if not fan:
            raise FactError("blades: no fan on that board")
        b, k = fan.defn()["blades"], int(args[0])
        return {"answer": str(b * k), "show": f"{b} blades x {k} turns = {b * k}"}
    raise FactError(f"unknown fact '{kind}'")


def same_answer(computed: str, written: str) -> bool:
    norm = lambda s: re.sub(r"\s+", " ", s.strip().lower().rstrip(".!"))
    if re.fullmatch(r"([A-Z]\d+)( and [A-Z]\d+)*", computed):
        return set(re.findall(r"[A-Z]\d+", written.upper())) == set(re.findall(r"[A-Z]\d+", computed))
    c = read_number(computed)
    if c is not None and NUM_RE.fullmatch(computed.strip()):
        w = read_number(written)
        return w == c
    return norm(computed) == norm(written)


# ------------------------------------------------------------------ deck


CAST = {"Coco": "#7b4fb5", "Pip": "#3a8d2f", "Tika": "#d9730d", "Sully": "#2f6db3"}
# Comic-page shapes for talk slides. `strip` is the old four-across row.
TALK_LAYOUTS = ("strip", "hero", "zigzag", "quad", "cinema", "stack", "wide", "splash", "spread")
POSITIONS = ("tl", "tc", "tr", "bl", "bc", "br")
COMMON_FIELDS = {"say", "dad", "watch", "reason", "pose", "bubble", "reveal", "title"}
KIND_FIELDS = {
    "cover": {"art"},
    "splash": {"art"},
    "comic": {"panel", "caption"},
    "talk": {"box", "caption", "layout"},
    "meet": set(),
    "step": set(),
    "change": set(),
    "scene": set(),
    "predict": {"test", "look", "choices", "answer", "ask", "fact", "stars", "board"},
    "why": {"water", "board"},
    "puzzle": {"boards", "look", "choices", "answer", "ask", "stars"},
    "mission": {"card", "stars", "show"},
    "numberlab": {"fact", "answer", "ask", "stars", "board", "show"},
    "rule": {"rule"},
    "badge": {"rule"},
}


@dataclass
class Bubble:
    who: str
    pos: str
    text: str


@dataclass
class Panel:
    art: str
    line: int
    bubbles: list = field(default_factory=list)
    captions: list = field(default_factory=list)


@dataclass
class Slide:
    kind: str
    arg: str
    line: int
    chapter: int
    idx: int
    f: dict = field(default_factory=dict)
    bubbles: list = field(default_factory=list)
    reveal: list = field(default_factory=list)
    panels: list = field(default_factory=list)
    calc: dict = field(default_factory=dict)  # filled in by check_deck


@dataclass
class Chapter:
    n: int
    title: str
    line: int
    badge: str = ""


@dataclass
class Deck:
    path: Path
    title: str = ""
    meta: dict = field(default_factory=dict)
    chapters: list = field(default_factory=list)
    slides: list = field(default_factory=list)
    problems: list = field(default_factory=list)

    def fail(self, code: str, msg: str, line: int = 0) -> None:
        self.problems.append((code, f"deck.md:{line}: {msg}" if line else msg))


CHAPTER_RE = re.compile(r"^## Chapter (\d+) -- (.+?)\s*$")
SLIDE_RE = re.compile(r"^=== ([a-z]+)(?:\s+(\S+))?\s*$")
FIELD_LINE = re.compile(r"^([a-z][a-z-]*):\s?(.*)$")
BUBBLE_RE = re.compile(r"^(\w+)(?:\s*@(\w+))?:\s*(.+)$")


def parse_bubble(deck: Deck, text: str, line: int) -> Bubble | None:
    m = BUBBLE_RE.match(text)
    if not m:
        deck.fail("DECK", f"bubble needs 'Who: words' or 'Who @tl: words', got '{text}'", line)
        return None
    who, pos, words = m.groups()
    if who not in CAST:
        deck.fail("DECK", f"'{who}' is not in the cast ({', '.join(CAST)})", line)
    if pos and pos not in POSITIONS:
        deck.fail("DECK", f"bubble position @{pos} (use {', '.join(POSITIONS)})", line)
    return Bubble(who, pos or "", words.strip())


def parse_deck(path: Path) -> Deck:
    """The comic, one slide at a time.

        # Title                          first line
        (any prose up to the first chapter is notes for humans)
        ## Chapter 1 -- The Dark Skate Park
        badge: Light Finder
        === cover                        a full-page chapter card, before case 1
        art: renders/comic-chapter-1.jpg
        === splash                       a slide: === <kind> [arg]
        art: renders/comic-c1-splash.jpg
        say: Read-aloud line.
        dad: What the grown-up does.
        === comic
        panel: renders/comic-c1-01.jpg   a panel; bubbles below ride on it
        caption: Narration box.
        bubble: Sully @tl: It's too dark to skate!
        === talk                         2 to 4 cartoon boxes, one idea, argued out
        box: pip-oops                    a pose in context/comic/, no .jpg
        bubble: Pip: One wire should do it!
        box: coco-explain
        bubble: Coco: The water has to come back.
        === step 3                       pose + bubbles beside the board
        pose: coco-point
        bubble: Coco: Find the Gate.
        === predict                      guess, then test; the checker
        test: S1=off                     works out the answer and fails
        look: L4                         the deck if `answer` disagrees
        choices: Light=on | Dark=off
        answer: Dark
        reveal: Coco: Dark! A shut gate is a gap.

    A line that starts with a space continues the line above. Lines that
    start with `>` are notes to the author and are skipped.
    """
    deck = Deck(path)
    ch: Chapter | None = None
    sl: Slide | None = None
    last = None
    for n, raw in enumerate(path.read_text().splitlines(), 1):
        if not raw.strip():
            last = None
            continue
        if not deck.chapters and not deck.title and raw.startswith("# "):
            deck.title = raw[2:].strip()
            continue
        if m := CHAPTER_RE.match(raw):
            ch = Chapter(int(m.group(1)), m.group(2), n)
            deck.chapters.append(ch)
            sl, last = None, None
            continue
        if ch is None:
            if m := FIELD_LINE.match(raw):
                if m.group(1) in ("series", "module"):
                    deck.meta[m.group(1)] = m.group(2).strip()
            continue
        if raw.startswith(">"):
            continue
        if m := SLIDE_RE.match(raw):
            kind, arg = m.group(1), m.group(2) or ""
            if kind not in KIND_FIELDS:
                deck.fail("DECK", f"unknown slide kind '{kind}' (use {', '.join(KIND_FIELDS)})", n)
            sl = Slide(kind, arg, n, ch.n, len(deck.slides) + 1)
            deck.slides.append(sl)
            last = None
            continue
        if raw[:1] in (" ", "\t"):
            if last:
                last(raw.strip())
            else:
                deck.fail("DECK", "indented line with nothing above it to continue", n)
            continue
        m = FIELD_LINE.match(raw)
        if not m:
            deck.fail("DECK", f"cannot read: {raw.strip()}", n)
            continue
        key, val = m.group(1), m.group(2).strip()
        if sl is None:
            if key == "badge":
                ch.badge = val
                last = lambda t, c=ch: setattr(c, "badge", c.badge + " " + t)
            else:
                deck.fail("DECK", f"'{key}:' before the chapter's first slide (only badge: goes there)", n)
            continue
        if key not in COMMON_FIELDS | KIND_FIELDS.get(sl.kind, set()):
            deck.fail("DECK", f"'{key}:' does not belong on a {sl.kind} slide", n)
            last = None
            continue
        if key in ("panel", "box"):
            sl.panels.append(Panel(val, n))
            last = None
        elif key == "caption":
            if not sl.panels:
                deck.fail("DECK", "caption: comes after a panel:", n)
                continue
            sl.panels[-1].captions.append(val)
            last = lambda t, p=sl.panels[-1]: p.captions.__setitem__(-1, p.captions[-1] + " " + t)
        elif key in ("bubble", "reveal"):
            b = parse_bubble(deck, val, n)
            if not b:
                continue
            if key == "reveal":
                sl.reveal.append(b)
            elif sl.kind == "comic":
                if not sl.panels:
                    deck.fail("DECK", "a comic bubble comes after a panel:", n)
                    continue
                sl.panels[-1].bubbles.append(b)
            elif sl.kind == "talk":
                if not sl.panels:
                    deck.fail("DECK", "a talk bubble comes after a box:", n)
                    continue
                sl.panels[-1].bubbles.append(b)
            else:
                sl.bubbles.append(b)
            last = lambda t, b=b: setattr(b, "text", b.text + " " + t)
        else:
            if key in sl.f:
                deck.fail("DECK", f"'{key}:' twice on one slide", n)
            sl.f[key] = val
            last = lambda t, s=sl, k=key: s.f.__setitem__(k, s.f[k] + " " + t)
    return deck


def parse_choices(text: str) -> list:
    out = []
    for part in text.split("|"):
        if "=" not in part:
            raise FactError(f"choice '{part.strip()}' needs Label=tokens")
        lab, toks = part.split("=", 1)
        ts = set(toks.split())
        if not ts or ts - TOKENS:
            raise FactError(f"choice '{part.strip()}': tokens must be from {' '.join(sorted(TOKENS))}")
        out.append((lab.strip(), ts))
    return out


def classify(toks: set, choices: list) -> list:
    hits = []
    for lab, want in choices:
        if "off" in want:
            if toks == {"off"}:
                hits.append(lab)
        elif toks != {"off"} and want <= toks:
            hits.append(lab)
    return hits


def look_tokens(circ: Circuit, a: Assign, key: str) -> tuple:
    ev = evaluate(circ, a)
    loads = [p for p in ev.parts if p.defn().get("kind") == "load" and (not key or p.key == key)]
    if len(loads) != 1:
        raise FactError(f"look: found {len(loads)} '{key or 'load'}' blocks on that board, need exactly 1")
    return ev.tokens[loads[0].step], ev


def steps_copy(steps: dict, s: Slide) -> dict:
    if s.kind == "step" and s.arg.isdigit():
        return steps.get(("step", int(s.arg)), {})
    if s.kind == "scene":
        return steps.get(("scene", s.arg), {})
    return {}


def art_path(bdir: Path, rel: str) -> Path:
    return bdir / rel


def check_deck(bdir: Path, circ: Circuit, deck: Deck, steps: dict, fixture: bool = False) -> tuple:
    P: list = list(deck.problems)
    W: list = []

    def fail(code, msg, line=0):
        P.append((code, f"deck.md:{line}: {msg}" if line else msg))

    for i, ch in enumerate(deck.chapters, 1):
        if ch.n != i:
            fail("DECK", f"chapters must be numbered 1..N, found Chapter {ch.n} in place {i}", ch.line)
        if not ch.badge:
            fail("DECK", f"Chapter {ch.n} has no badge: line", ch.line)
        if not any(s.chapter == ch.n for s in deck.slides):
            fail("DECK", f"Chapter {ch.n} has no slides", ch.line)
    if not deck.chapters:
        fail("DECK", "deck.md has no '## Chapter 1 -- Title' heading")

    # coverage: the build is in the comic exactly once, in order
    def cover(kind, want, label):
        got = [s.arg for s in deck.slides if s.kind == kind]
        if got == want:
            return
        missing = [w for w in want if w not in got]
        extra = [g for g in got if g not in want]
        dupes = sorted({g for g in got if got.count(g) > 1})
        bits = []
        if missing:
            bits.append(f"no slide for {label} {', '.join(missing)}")
        if extra:
            bits.append(f"{label} {', '.join(extra)} not in circuit.snap")
        if dupes:
            bits.append(f"{label} {', '.join(dupes)} more than once")
        if not bits:
            bits.append(f"{label}s out of order: deck has {', '.join(got)}, circuit.snap has {', '.join(want)}")
        fail("DECK", "; ".join(bits))

    cover("step", [str(p.step) for p in circ.placed], "step")
    cover("change", [v.name for v in circ.changes()], "change")
    cover("scene", [n for n, _, _ in circ.scenes], "scene")
    missions = [v.name for v in circ.variants.values() if v.kind == "mission"]
    got_m = [s.arg for s in deck.slides if s.kind == "mission"]
    for m in missions:
        if m not in got_m:
            fail("DECK", f"no slide for mission {m}")
    puzzles_used: set = set()
    need = need_counts(circ)

    for s in deck.slides:
        where = s.line
        f = s.f
        sc = steps_copy(steps, s)
        if not (f.get("dad") or sc.get("Do")):
            fail("DAD", f"{s.kind} slide has no dad: line (what the grown-up does)", where)
        if "pose" in f and not (COMIC_DIR / f"{f['pose']}.jpg").exists():
            fail("DECK", f"pose '{f['pose']}' is not in context/comic/", where)
        for b in s.bubbles + s.reveal + [b for p in s.panels for b in p.bubbles]:
            if len(b.text.split()) > 22:
                W.append(("WORDY", f"deck.md:{where}: {b.who}'s bubble is {len(b.text.split())} words; a six-year-old listens to about 15"))
        if len(f.get("say", "").split()) > 26:
            W.append(("WORDY", f"deck.md:{where}: say: is {len(f['say'].split())} words"))
        if "stars" in f and f["stars"] not in ("1", "2", "3"):
            fail("DECK", f"stars: {f['stars']} (use 1, 2 or 3)", where)
        if s.kind in ("puzzle", "numberlab", "mission") and "stars" not in f:
            fail("DECK", f"{s.kind} slide needs stars: 1, 2 or 3", where)

        def need_art(rel):
            if not fixture and not art_path(bdir, rel).exists():
                fail("DECK", f"{rel} does not exist", where)

        if s.kind in ("splash", "cover"):
            if "art" not in f:
                fail("DECK", f"{s.kind} needs art:", where)
            else:
                need_art(f["art"])
        elif s.kind == "comic":
            if not 1 <= len(s.panels) <= 2:
                fail("DECK", f"a comic slide has 1 or 2 panels, this one has {len(s.panels)}", where)
            for p in s.panels:
                need_art(p.art)
        elif s.kind == "talk":
            lay = f.get("layout", "strip")
            if lay not in TALK_LAYOUTS:
                fail("DECK", f"layout: {lay} (use {', '.join(TALK_LAYOUTS)})", where)
            nboxes = len(s.panels)
            if lay == "splash" and nboxes != 1:
                fail("DECK", "a splash talk is one picture with every bubble on it", where)
            elif lay == "spread" and nboxes != 2:
                fail("DECK", "a spread talk is two wide pictures", where)
            elif lay not in ("splash", "spread") and not 2 <= nboxes <= 4:
                fail("DECK", f"a talk page has 2, 3 or 4 boxes, this one has {nboxes}", where)
            bubble_cap = 4 if lay == "splash" else 2
            for p in s.panels:
                art = talk_art(bdir, p.art)
                if not art.exists():
                    fail("DECK", f"box '{p.art}' is not in context/comic/ or the build", where)
                if not p.bubbles:
                    fail("DECK", f"box {p.art} needs a bubble", where)
                elif len(p.bubbles) > bubble_cap:
                    fail("DECK", f"box {p.art} has {len(p.bubbles)} bubbles; keep it to {bubble_cap}", where)
        elif s.kind == "meet":
            if not part_def(s.arg):
                fail("DECK", f"meet {s.arg}: no such block", where)
            elif s.arg not in need:
                fail("DECK", f"meet {s.arg}: this lesson never uses it", where)
        elif s.kind == "step" and not s.arg.isdigit():
            fail("DECK", f"step slide needs a step number, got '{s.arg}'", where)
        elif s.kind in ("change", "mission"):
            v = circ.variants.get(s.arg)
            if not v or v.kind != s.kind:
                fail("DECK", f"{s.kind} {s.arg}: circuit.snap has no {s.kind} named that", where)
            elif s.kind == "mission":
                if "card" not in f:
                    fail("DECK", "mission slide needs card: (what Ian must make)", where)
                s.calc = {"variant": v}
        elif s.kind == "rule" and not f.get("rule"):
            fail("DECK", "rule slide needs rule:", where)
        elif s.kind == "why" and not ("water" in f or "board" in f):
            fail("DECK", "why slide needs water: or board: (the picture that explains it)", where)

        # questions whose answers the checker works out
        try:
            if s.kind == "predict" or (s.kind == "numberlab" and "fact" in f):
                if "answer" not in f:
                    fail("PREDICT" if s.kind == "predict" else "NUMBERLAB", f"{s.kind} needs answer:", where)
                elif "fact" in f:
                    got = compute_fact(circ, f["fact"])
                    s.calc = got
                    if not same_answer(got["answer"], f["answer"]):
                        fail("PREDICT" if s.kind == "predict" else "NUMBERLAB",
                             f"answer says '{f['answer']}' but the board says '{got['answer']}' ({got['show']})", where)
                else:
                    for k in ("test", "choices"):
                        if k not in f:
                            raise FactError(f"predict needs {k}: (or fact:)")
                    a, errs = assign_from(circ, f["test"])
                    if errs:
                        raise FactError(errs[0])
                    toks, ev = look_tokens(circ, a, f.get("look", ""))
                    if ev.short:
                        fail("SHORT", f"test {a.label()} shorts the battery", where)
                    hits = classify(toks, parse_choices(f["choices"]))
                    if len(hits) != 1:
                        raise FactError(f"the board says {' '.join(sorted(toks))}, which matches {len(hits)} choices; it must match exactly one")
                    s.calc = {"answer": hits[0], "assign": a, "show": board_result(circ, a)}
                    if hits[0].lower() != f["answer"].strip().lower():
                        fail("PREDICT", f"answer says '{f['answer']}' but the board says '{hits[0]}' ({board_result(circ, a)})", where)
            elif s.kind == "numberlab" and "answer" not in f:
                fail("NUMBERLAB", "numberlab needs answer: (written out when there is no fact:)", where)
            if s.kind == "puzzle":
                for k in ("boards", "choices", "answer"):
                    if k not in f:
                        raise FactError(f"puzzle needs {k}:")
                choices = parse_choices(f["choices"])
                written = {}
                for bit in f["answer"].split(","):
                    if "=" not in bit:
                        raise FactError(f"puzzle answer '{bit.strip()}' needs board=Choice")
                    k, v = bit.split("=", 1)
                    written[k.strip()] = v.strip()
                names = [b.strip() for b in f["boards"].split(",") if b.strip()]
                answers = {}
                for nm in names:
                    v = circ.variants.get(nm)
                    if not v or v.kind != "puzzle":
                        fail("DECK", f"puzzle board '{nm}': circuit.snap has no puzzle named that", where)
                        continue
                    puzzles_used.add(nm)
                    toks, _ = look_tokens(circ, v.assign, f.get("look", ""))
                    hits = classify(toks, choices)
                    if len(hits) != 1:
                        raise FactError(f"board {nm} says {' '.join(sorted(toks))}, which matches {len(hits)} choices")
                    answers[nm] = hits[0]
                    if nm not in written:
                        fail("PUZZLE", f"answer: has nothing for board {nm}", where)
                    elif written[nm].lower() != hits[0].lower():
                        fail("PUZZLE", f"board {nm}: answer says '{written[nm]}' but the board says '{hits[0]}' ({board_result(circ, v.assign)})", where)
                s.calc = {"answers": answers}
            for k in ("board", "water"):
                if k in f:
                    a, errs = assign_from(circ, f[k])
                    if errs:
                        raise FactError(errs[0])
                    s.calc[k] = a
        except FactError as e:
            code = {"predict": "PREDICT", "numberlab": "NUMBERLAB", "puzzle": "PUZZLE"}.get(s.kind, "DECK")
            fail(code, str(e), where)

    for v in circ.variants.values():
        if v.kind == "puzzle" and v.name not in puzzles_used:
            fail("DECK", f"puzzle {v.name} is never shown")

    # A real photo goes right after the board it shows, so "yours should
    # look like this" is true of the page before it.
    by_file = {ph.file: ph for ph in circ.photos}
    shown: set = set()
    last = None  # (slide, Assign)
    for s in deck.slides:
        arts = [p.art for p in s.panels] + ([s.f["art"]] if "art" in s.f else [])
        for art in arts:
            if not Path(art).name.startswith("real-"):
                continue
            ph = by_file.get(art)
            if not ph:
                fail("PHOTO", f"{art} is a photo of the real board, but circuit.snap has no `photo` line for it", s.line)
                continue
            shown.add(ph.name)
            if ph.assign is None or not ph.items:
                continue
            if last is None:
                fail("PHOTO", f"photo {ph.name} comes before any board page; put it after the board it shows", s.line)
                continue
            got = board_items(effective_parts(circ, last[1]))
            only_photo, only_page = item_diff(ph.items, got)
            if only_photo or only_page:
                bits = (["the photo has " + "; ".join(only_photo)] if only_photo else []) + \
                       (["the page has " + "; ".join(only_page)] if only_page else [])
                fail("PHOTO", f"photo {ph.name} follows the {last[0].kind} {last[0].arg} page (deck.md:{last[0].line}), "
                              f"which shows a different board: " + ", but ".join(bits), s.line)
        b = slide_board(circ, s)
        if b is not None:
            last = (s, b)
    for ph in circ.photos:
        if ph.name not in shown:
            fail("PHOTO", f"photo {ph.name} ({ph.file}) is never shown in the deck")
        if not re.match(r"^renders/real-[a-z0-9-]+\.jpg$", ph.file):
            fail("PHOTO", f"photo {ph.name}: name the file renders/real-<name>.jpg (got {ph.file})")
        elif not fixture and not (bdir / ph.file).exists():
            fail("PHOTO", f"photo {ph.name}: {ph.file} does not exist")
    for code, msg, line in post_problems(circ, deck, steps):
        fail(code, msg, line)
    return P, W


POST_TOKEN = re.compile(r"(?<!\w)[1-9][A-H](?!\w)")
OLD_POST = re.compile(r"(?<!\w)[A-H][1-9]\d?(?!\w)")


def old_posts(text: str) -> set:
    """Posts written letter-first (D3). Part names like B1 or D10 are not posts."""
    return {t for t in OLD_POST.findall(text) if t not in db()["parts"]}


def board_posts(circ: Circuit, a: Assign) -> set:
    """Every post a block on this board has a metal snap on."""
    out = set()
    for p in effective_parts(circ, a):
        out |= {post_name(r, c) for r, c in p.snaps()}
    return out


def post_problems(circ: Circuit, deck: Deck, steps: dict) -> list:
    """A post a page names has to be a snap on the board that page is about
    (or the one just before it). Step text that still says 1B after the
    holder moved to 1A is the mistake this catches."""
    out = []
    grid = {post_name(r, c) for r in range(circ.rows) for c in range(circ.cols)}

    def texts(s: Slide) -> list:
        t = [b.text for b in s.bubbles + s.reveal] + [b.text for p in s.panels for b in p.bubbles]
        return t + [s.f.get(k, "") for k in ("dad", "watch", "ask", "card", "say")]

    def posts_at(n: int) -> set:
        return board_posts(circ, Assign(remove={p.step for p in circ.placed if p.step > n}))

    for (kind, arg), f in steps.items():
        if kind == "step":
            ok = grid if arg == min(p.step for p in circ.placed) else posts_at(arg)
        else:
            a = next((a for n, a, _ in circ.scenes if n == arg), None)
            ok = board_posts(circ, a) if a else grid
        for k, v in f.items():
            for t in sorted(old_posts(str(v))):
                out.append(("POSTS", f"steps.md {kind} {arg} {k}: '{t}' is the old way round; posts are number then letter "
                                      f"({t[1:]}{t[0]})", 0))
            for t in sorted(set(POST_TOKEN.findall(str(v))) - ok):
                out.append(("POSTS", f"steps.md {kind} {arg} {k}: names {t}, which is not a snap on that board "
                                      f"(snaps: {' '.join(sorted(ok - grid if ok != grid else set())) or 'any grid post'})", 0))
    # a board page that calls a light by its picture name means a light on that board
    kid: dict = {}
    for key, d in db()["parts"].items():
        if isinstance(d, dict) and d.get("kind") == "load" and d.get("kid"):
            kid.setdefault(d["kid"].lower(), set()).add(key)

    def keys_on(a):
        return {p.key for p in effective_parts(circ, a)} if a is not None else set()

    last = posts_at(min((p.step for p in circ.placed), default=0))
    last_keys: set = set()
    first = min((p.step for p in circ.placed), default=0)
    for s in deck.slides:
        b = slide_board(circ, s)
        if s.kind == "step" and s.arg.isdigit() and int(s.arg) == first:
            ok = grid
        else:
            ok = last | (board_posts(circ, b) if b is not None else set())
            if s.kind == "mission" and s.arg in circ.variants:
                for c in circ.variants[s.arg].claims:
                    ok |= board_posts(circ, c.assign)
        for t in sorted({t for x in texts(s) for t in POST_TOKEN.findall(x)} - ok):
            out.append(("POSTS", f"{s.kind} {s.arg}: names {t}, which is not a snap on that board", s.line))
        for t in sorted({t for x in texts(s) for t in old_posts(x)}):
            out.append(("POSTS", f"{s.kind} {s.arg}: '{t}' is the old way round; posts are number then letter ({t[1:]}{t[0]})", s.line))
        if b is not None:
            on = keys_on(b) | last_keys
            words = " ".join(texts(s)).lower()
            for name, keys in sorted(kid.items()):
                if name in words and not keys & on:
                    out.append(("NAMES", f"{s.kind} {s.arg}: says '{name}' ({'/'.join(sorted(keys))}), "
                                         f"which is not on that board", s.line))
            last = board_posts(circ, b)
            last_keys = keys_on(b)
    return out


def slide_board(circ: Circuit, s: Slide) -> Assign | None:
    """The board a page puts in front of Ian, or None for a page without one."""
    if s.kind == "step" and s.arg.isdigit():
        n = int(s.arg)
        return Assign(remove={p.step for p in circ.placed if p.step > n})
    if s.kind in ("change", "mission"):
        v = circ.variants.get(s.arg)
        if v:
            return v.claims[0].assign if (s.kind == "mission" and v.claims) else v.assign
    if s.kind == "scene":
        return next((a for n, a, _ in circ.scenes if n == s.arg), None)
    if s.kind in ("why", "predict"):
        for k in ("water", "board", "assign"):
            if isinstance(s.calc.get(k), Assign):
                return s.calc[k]
    return None


# ------------------------------------------------------------- build files


def read_tags(readme: Path) -> dict:
    tags: dict = {}
    if not readme.exists():
        return tags
    for line in readme.read_text().splitlines()[1:]:
        if not line.strip():
            if tags:
                break
            continue
        if m := re.match(r"^(\w[\w-]*):\s*(.*)$", line):
            tags[m.group(1)] = m.group(2).strip()
    return tags


FIELD_RE = re.compile(r"^  (Bin|Add|Say|Ask|Do|Check):\s*(.*)$")
HEAD_RE = re.compile(r"^(?:Step (\d+)|Scene ([a-z0-9-]+)) -- (.+)$")


def parse_steps(path: Path) -> dict:
    """{('step', n) | ('scene', name): {'title':..., 'Say':..., ...}}"""
    out: dict = {}
    if not path.exists():
        return out
    cur = None
    last = None
    for raw in path.read_text().splitlines():
        if m := HEAD_RE.match(raw):
            key = ("step", int(m.group(1))) if m.group(1) else ("scene", m.group(2))
            cur = out.setdefault(key, {"title": m.group(3).strip()})
            last = None
        elif cur is not None and (m := FIELD_RE.match(raw)):
            last = m.group(1)
            cur[last] = m.group(2).strip()
        elif cur is not None and last and raw.startswith("      ") and raw.strip():
            cur[last] += " " + raw.strip()
        elif not raw.strip():
            last = None
    return out


def build_hash(bdir: Path) -> str:
    h = hashlib.sha1()
    for name in ("circuit.snap", "steps.md", "deck.md"):
        f = bdir / name
        h.update(f.read_bytes() if f.exists() else b"")
    h.update(PARTS_JSON.read_bytes())
    h.update(Path(__file__).read_bytes())
    return h.hexdigest()[:12]


def bom_rows(circ: Circuit) -> list:
    out = []
    for key, q in need_counts(circ).items():
        d = part_def(key) or {}
        out.append((q, key, d.get("printed", "?"), d.get("name", "?"), d.get("kit", "?")))
    return out


def bom_text(circ: Circuit) -> str:
    lines = [
        "# QTY | KEY | PRINTED | NAME | KIT",
        "# Written by `python3 tools/snap.py bom <build> --write`: every block the lesson",
        "# ever has on the board at once, across all its chapters. `snap.py check` fails if this drifts.",
    ]
    lines += [" | ".join(str(x) for x in row) for row in bom_rows(circ)]
    return "\n".join(lines) + "\n"


DRAWN_RE = re.compile(r'data-step="(\d+)" data-key="([^"]+)" data-want="([^"]*)" data-drawn="([^"]*)"')


def drawn_problems(svg: str) -> list:
    """Read each block back off a drawing and compare it with the layout."""
    out = []
    for step, key, want, got in DRAWN_RE.findall(svg):
        if want != got:
            out.append(f"step {step} {key} should be drawn as '{want}' but the picture shows '{got}'")
    return out


def check_build(bdir: Path) -> tuple:
    circ = parse_circuit(bdir / "circuit.snap")
    problems, warns = check_circuit(circ)

    def fail(code, msg):
        problems.append((code, msg))

    tags = read_tags(bdir / "README.md")
    if not tags:
        fail("README", "README.md has no tag header")
    elif {k.strip() for k in tags.get("kits", "").split(",")} != set(circ.kits):
        fail("README", f"README kits '{tags.get('kits')}' differ from circuit.snap kits '{', '.join(circ.kits)}'")

    steps_md = bdir / "steps.md"
    steps = parse_steps(steps_md)
    if not steps_md.exists():
        fail("STEPS_MD", "steps.md is missing")
    else:
        want = {("step", p.step) for p in circ.placed} | {("scene", n) for n, _, _ in circ.scenes}
        for k in sorted(want - set(steps), key=str):
            fail("STEPS_MD", f"steps.md has no block for {k[0]} {k[1]}")
        for k in sorted(set(steps) - want, key=str):
            fail("STEPS_MD", f"steps.md has {k[0]} {k[1]} but circuit.snap does not")
        for k, f in steps.items():
            if "Say" not in f:
                fail("STEPS_MD", f"{k[0]} {k[1]}: no Say: line (the sentence printed on the page)")
            if k[0] == "step" and ("Do" not in f or "Check" not in f):
                fail("STEPS_MD", f"step {k[1]}: needs Do: and Check:")

    # a lesson that runs one box out of a block needs both boxes, and says so
    need = need_counts(circ)
    if len(circ.kits) > 1:
        alone = [k for k in circ.kits
                 if all(read_inventory(k).get(key, 0) >= q for key, q in need.items()
                        if (part_def(key) or {}).get("kit") in (k, "both"))
                 and all((part_def(key) or {}).get("kit") in (k, "both") for key in need if part_def(key))]
        readme = (bdir / "README.md").read_text() if (bdir / "README.md").exists() else ""
        if alone:
            fail("KITS", f"the {BOX_NAME.get(alone[0], alone[0])} alone covers this lesson; list only that kit")
        elif not re.search(r"needs both", readme, re.I):
            short = ", ".join(f"{q}x {key}" for key, q in sorted(need.items())
                              if (part_def(key) or {}).get("kit") == "both" and q > read_inventory(circ.kits[0]).get(key, 0))
            fail("KITS", f"README.md must say this build needs both boxes ({short or 'parts from each box'})")

    # every photo of the real board is listed in circuit.snap
    listed = {ph.file for ph in circ.photos}
    rd = bdir / "renders"
    for f_ in sorted(rd.glob("real-*")) if rd.exists() else []:
        if f"renders/{f_.name}" not in listed:
            fail("PHOTO", f"renders/{f_.name} is a photo of the real board with no `photo` line in circuit.snap (say what is in it)")

    if (bdir / "story.md").exists():
        fail("DECK", "story.md is replaced by deck.md; move its slides into the comic and delete it")
    deck = None
    if not (bdir / "deck.md").exists():
        fail("DECK", "deck.md is missing")
    else:
        deck = parse_deck(bdir / "deck.md")
        dp, dw = check_deck(bdir, circ, deck, steps)
        problems += dp
        warns += dw
        used = {s.f.get("art") for s in deck.slides} | {p.art for s in deck.slides for p in s.panels}
        rd = bdir / "renders"
        for f in sorted(rd.iterdir()) if rd.exists() else []:
            if f.suffix in (".jpg", ".png") and f"renders/{f.name}" not in used:
                fail("DECK", f"renders/{f.name} is not used by any slide (delete it or use it)")

    parts_txt = bdir / "parts.txt"
    if not parts_txt.exists():
        fail("BOM_FILE", "parts.txt is missing (python3 tools/snap.py bom <build> --write)")
    elif parts_txt.read_text() != bom_text(circ):
        fail("BOM_FILE", "parts.txt does not match circuit.snap (python3 tools/snap.py bom <build> --write)")

    if deck is not None and not [p for p in problems if p[0] in ("SYNTAX",)]:
        h = build_hash(bdir)
        planned = {rel for rel, _ in planned_renders(bdir, circ, deck)}
        for rel in sorted(planned):
            f = bdir / rel
            if not f.exists():
                fail("RENDER", f"{rel} is missing (run render)")
            elif f"snap-sha: {h}" not in f.read_text()[:400]:
                fail("RENDER", f"{rel} is stale (run render)")
        rd = bdir / "renders"
        for f in sorted(rd.glob("*.svg")) if rd.exists() else []:
            if f"renders/{f.name}" not in planned:
                fail("RENDER", f"renders/{f.name} is not drawn by render any more (run render to clear it)")
        for f in sorted(rd.glob("*.svg")) if rd.exists() else []:
            for msg in drawn_problems(f.read_text()):
                fail("DRAWN", f"renders/{f.name}: {msg}")

    import talkart
    for msg in talkart.lint_messages(bdir):
        fail("IMGLINT", msg)
    return problems, warns


def imglint(bdir: Path) -> int:
    """Refuse character cutouts that have a hole the background can show through."""
    import talkart
    return talkart.lint_saved(bdir)


def report(label: str, problems: list, warns: list) -> int:
    for code, msg in problems:
        print(f"FAIL {code:<12} {msg}")
    for code, msg in warns:
        print(f"warn {code:<12} {msg}")
    print(f"{label}: {len(problems)} problems" + (f", {len(warns)} warnings" if warns else ""))
    return 1 if problems else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("check", "render", "preview", "bom", "imglint"):
        s = sub.add_parser(name)
        s.add_argument("target", type=Path)
        if name == "bom":
            s.add_argument("--write", action="store_true")
    sub.add_parser("selftest")
    args = ap.parse_args()

    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "imglint":
        target = args.target if args.target.is_absolute() else Path.cwd() / args.target
        return imglint(target)
    target = args.target if args.target.is_absolute() else Path.cwd() / args.target
    if args.cmd == "check":
        if target.is_dir():
            return report(target.name, *check_build(target))
        return report(target.name, *check_circuit(parse_circuit(target)))
    circ = parse_circuit(target / "circuit.snap")
    if args.cmd == "bom":
        if args.write:
            (target / "parts.txt").write_text(bom_text(circ))
            print(f"wrote {target / 'parts.txt'}")
        else:
            print(bom_text(circ), end="")
        return 0
    problems, _ = check_circuit(circ)
    if problems:
        print("refusing to draw a layout that fails check:")
        return report(target.name, problems, [])
    if not (target / "deck.md").exists():
        print("no deck.md: nothing to draw the comic from")
        return 1
    deck = parse_deck(target / "deck.md")
    steps = parse_steps(target / "steps.md")
    dp, _ = check_deck(target, circ, deck, steps)
    if args.cmd == "render":
        return render_build(target, circ, deck)
    if dp:
        print(f"note: deck has {len(dp)} problems (run check); previewing anyway")
    return preview_build(target, circ, deck, steps)


def fixture_want(f: Path) -> str | None:
    for raw in f.read_text().splitlines()[:4]:
        if m := re.match(r"^#\s*bad:\s*(\w+)", raw):
            return m.group(1)
    return None


def selftest() -> int:
    bad = 0
    items = sorted(p for p in FIXTURES.iterdir() if p.suffix == ".snap" or (p.is_dir() and (p / "deck.md").exists()))
    for f in items:
        if f.is_dir():
            circ = parse_circuit(f / "circuit.snap")
            problems, _ = check_circuit(circ)
            dp, _ = check_deck(f, circ, parse_deck(f / "deck.md"), parse_steps(f / "steps.md"), fixture=True)
            problems = problems + dp
            want = fixture_want(f / "deck.md") or fixture_want(f / "circuit.snap")
        else:
            problems, _ = check_circuit(parse_circuit(f))
            want = fixture_want(f)
        codes = {c for c, _ in problems}
        if f.name.startswith("good-"):
            ok = not problems
        else:
            # exactly the declared problem: a fixture that trips five rules
            # proves none of them
            ok = want is not None and codes == {want}
        detail = "" if ok else f"  want {want or 'no problems'}, got {sorted(codes) or 'none'}"
        if not ok and problems:
            detail += "\n      " + "\n      ".join(m for _, m in problems[:4])
        print(("ok   " if ok else "FAIL ") + f.name + detail)
        bad += 0 if ok else 1
        if f.name.startswith("good-") and f.suffix == ".snap":
            # every good board, read back off its own drawing, is the layout
            drawn = drawn_problems(board_panel(parse_circuit(f), Assign(), "selftest"))
            if drawn:
                print(f"FAIL {f.name} drawing: {drawn[0]}")
                bad += 1
    print(f"{len(items)} fixtures, {bad} wrong")

    # the part facts the photos settled: a typo in parts.json must fail check
    for key, change, why in (("L4", {"span": 2, "snaps": [0, 1]}, "a 1x2 lamp"),
                             ("S1", {"snaps": [0, 1, 2]}, "a switch with a middle snap"),
                             ("B3B", {"depth": 2}, "a 3x2 battery holder"),
                             ("B3B", {"hangs": False}, "a battery holder that cannot ride the edge"),
                             ("wire3", {"span": 2, "snaps": [0, 1]}, "a 3-snap wire two posts long"),
                             ("grid-mini", {"rows": 4}, "a 7x4 grid")):
        d = dict(part_def(key))
        d.update(change)
        ok = any(c == "PARTS" for c, _ in part_fact_problems(key, d)) and not part_fact_problems(key, part_def(key))
        print(("ok   " if ok else "FAIL ") + f"parts.json refuses {why}")
        bad += 0 if ok else 1
    # a drawing that shrinks a block is caught
    svg = board_panel(parse_circuit(FIXTURES / "good-series-loop.snap"), Assign(), "selftest")
    shrunk = svg.replace('data-drawn="1A 3A span=3 depth=3"', 'data-drawn="1A 3A span=3 depth=2"', 1)
    ok = shrunk != svg and bool(drawn_problems(shrunk))
    print(("ok   " if ok else "FAIL ") + "a 3x2 battery drawing is caught (DRAWN)")
    bad += 0 if ok else 1
    import talkart
    bad += talkart.selftest()
    return 1 if bad else 0


# ------------------------------------------------------------------ render

FONT = "'Avenir Next','Trebuchet MS','Helvetica Neue',Arial,sans-serif"
PW, PH = 1200, 800
INK = "#1d2433"
ARROWS = {"right": "\u2192", "left": "\u2190", "down": "\u2193", "up": "\u2191"}
BOX_NAME = {"scb20": "Beginner box", "sc100": "Jr box", "both": "Either box"}
LIT = {"red": "#ff4d4d", "yellow": "#ffd43b"}


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def panel_open(sha: str, bg: str = "#ffffff") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW}" height="{PH}" viewBox="0 0 {PW} {PH}" '
        f'font-family="{FONT}">\n<!-- snap-sha: {sha} -->\n<rect width="{PW}" height="{PH}" fill="{bg}"/>\n'
    )


def text(x, y, lines, size, fill=INK, weight="normal", anchor="start", lh=1.22) -> str:
    if isinstance(lines, str):
        lines = [lines]
    out = f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">'
    for i, ln in enumerate(lines):
        dy = 0 if i == 0 else size * lh
        out += f'<tspan x="{x:.1f}" dy="{dy:.1f}">{esc(ln)}</tspan>'
    return out + "</text>\n"


def wrap(s: str, width: int) -> list:
    return textwrap.wrap(s, width) or [""]


@dataclass
class View:
    ox: float
    oy: float
    p: float
    r0: int
    r1: int
    c0: int
    c1: int
    nums: str = "bottom"  # which edge the column numbers go on
    lets: str = "left"  # which edge the row letters go on
    margin: tuple = (1.9, 1.15, 1.15, 1.15)  # top, right, bottom, left, in posts, for crops

    def xy(self, cell) -> tuple:
        r, c = cell
        return (self.ox + (c - self.c0) * self.p, self.oy + (r - self.r0) * self.p)

    def post_at(self, x, y) -> tuple:
        return (round((y - self.oy) / self.p) + self.r0, round((x - self.ox) / self.p) + self.c0)


def used_box(circ: Circuit) -> tuple:
    cells = [c for pl in circ.placed for c in pl.cells()]
    if not cells:
        return 0, circ.rows - 1, 0, circ.cols - 1
    rs, cs = [c[0] for c in cells], [c[1] for c in cells]
    return (max(0, min(rs) - 1), min(circ.rows - 1, max(rs) + 1),
            max(0, min(cs) - 1), min(circ.cols - 1, max(cs) + 1))


def zoom_view(cells, x0, y0, x1, y1) -> View:
    """Frame just these posts, large. Puzzle cards are small; a full 1-7
    grid makes the + mark a few pixels tall."""
    rs = [r for r, _ in cells]
    cs = [c for _, c in cells]
    r0, r1, c0, c1 = min(rs), max(rs), min(cs), max(cs)
    nr, nc = max(1, r1 - r0), max(1, c1 - c0)
    top, side, bot = 1.9, 1.05, 1.45
    p = min((x1 - x0) / (nc + side + 0.65), (y1 - y0) / (nr + top + bot), 280)
    ox = x0 + side * p + ((x1 - x0) - (nc + side + 0.65) * p) / 2
    oy = y0 + top * p + ((y1 - y0) - (nr + top + bot) * p) / 2
    return View(ox, oy, p, r0, r1, c0, c1)


def clue_cells(circ: Circuit, a: Assign) -> list:
    cells = []
    for pl in effective_parts(circ, a):
        d = pl.defn()
        if d.get("kind") == "switch" or d.get("polarity") == "colour":
            cells.extend(pl.cells())
    return cells


PLATE = 0.55  # the clear grid's edge, in posts beyond the outer posts
CASE = 0.45  # a block's plastic beyond its end snaps, in posts
LABEL = 0.6  # room for the row letters and column numbers outside the plate


def hang_extent(circ: Circuit) -> tuple:
    """How far (posts) any block on any board in this lesson reaches past
    each edge of the grid: (top, right, bottom, left). The battery case
    usually hangs two rows off the top."""
    top = right = bottom = left = 0
    boards = [Assign()] + [a for _, a, _ in named_assigns(circ)]
    seen = set()
    for a in boards:
        for p in effective_parts(circ, a):
            k = (p.key, p.r, p.c, p.dir, p.side)
            if k in seen:
                continue
            seen.add(k)
            for r, c in p.footprint():
                top, bottom = max(top, -r), max(bottom, r - (circ.rows - 1))
                left, right = max(left, -c), max(right, c - (circ.cols - 1))
    return top, right, bottom, left


def fit_view(circ: Circuit, x0, y0, x1, y1) -> View:
    """The whole base grid, not a crop around the parts, plus room for a
    battery case that hangs off an edge. Beginner is 1-7 by A-E."""
    r0, c0 = 0, 0
    r1, c1 = max(0, circ.rows - 1), max(0, circ.cols - 1)
    nr, nc = r1 - r0, c1 - c0
    ht, hr, hb, hl = hang_extent(circ)
    nums = "top" if hb and not ht else "bottom"
    lets = "right" if hl and not hr else "left"
    edge = lambda h: max(PLATE, h + CASE) if h else PLATE
    mt = edge(ht) + (LABEL if nums == "top" else 0)
    mb = edge(hb) + (LABEL if nums == "bottom" else 0)
    ml = edge(hl) + (LABEL if lets == "left" else 0)
    mr = edge(hr) + (LABEL if lets == "right" else 0)
    mt, mr, mb, ml = (m + 0.1 for m in (mt, mr, mb, ml))
    p = min((x1 - x0) / (nc + ml + mr), (y1 - y0) / (nr + mt + mb), 140)
    ox = x0 + ml * p + ((x1 - x0) - (nc + ml + mr) * p) / 2
    oy = y0 + mt * p + ((y1 - y0) - (nr + mt + mb) * p) / 2
    return View(ox, oy, p, r0, r1, c0, c1, nums, lets, (mt, mr, mb, ml))


def board_base(v: View) -> str:
    p = v.p
    nr, nc = v.r1 - v.r0, v.c1 - v.c0
    x, y = v.ox - PLATE * p, v.oy - PLATE * p
    s = (f'<rect x="{x:.1f}" y="{y:.1f}" width="{(nc + 2 * PLATE) * p:.1f}" height="{(nr + 2 * PLATE) * p:.1f}" '
         f'rx="{0.3 * p:.1f}" fill="#eef3f8" stroke="#aebccd" stroke-width="3" data-grid="{nc + 1}x{nr + 1}"/>\n')
    for r in range(v.r0, v.r1 + 1):
        for c in range(v.c0, v.c1 + 1):
            cx, cy = v.xy((r, c))
            s += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.085 * p:.1f}" fill="#c7d2df"/>\n'
    off = (PLATE + LABEL / 2) * p
    lx = v.ox - off if v.lets == "left" else v.ox + nc * p + off
    for r in range(v.r0, v.r1 + 1):
        s += text(lx, v.xy((r, v.c0))[1] + 0.09 * p, chr(65 + r), 0.26 * p, "#7d8aa0", "bold", "middle")
    ny = v.oy - off + 0.09 * p if v.nums == "top" else v.oy + nr * p + off + 0.09 * p
    for c in range(v.c0, v.c1 + 1):
        s += text(v.xy((v.r0, c))[0], ny, str(c + 1), 0.26 * p, "#7d8aa0", "bold", "middle")
    return s


def drawn_attrs(pl: Placed, v: View, snap_xy: list, box: tuple) -> str:
    """What the picture really shows, read back off the drawing: which posts
    the snap circles sit on, and how many posts long and deep the plastic is.
    check compares these with the layout (DRAWN), so a drawing bug that
    shrinks a 1x3 block to 1x2 or a 3x3 battery to 3x2 fails the build."""
    posts = [v.post_at(x, y) for x, y in snap_xy]
    x, y, w, h = box
    along = w if pl.dir in ("left", "right") else h
    across = h if pl.dir in ("left", "right") else w
    span = round((along - 2 * CASE * v.p) / v.p) + 1
    depth = round((across - 2 * CASE * v.p) / v.p) + 1 if pl.defn().get("depth", 1) > 1 else 1
    want = " ".join(post_name(*c) for c in pl.snaps())
    got = " ".join(post_name(*c) for c in posts)
    d = pl.defn()
    return (f' data-step="{pl.step}" data-key="{esc(pl.key)}" data-want="{want} span={d.get("span")} depth={d.get("depth", 1)}"'
            f' data-drawn="{got} span={span} depth={depth}"')


def part_box(pl: Placed, v: View) -> tuple:
    """(x, y, w, h) of a block's plastic: a deep block's whole case."""
    if pl.defn().get("depth", 1) > 1 and pl.body_cells():
        fp = [v.xy(c) for c in pl.footprint()]
        e = CASE * v.p
        x, y = min(q[0] for q in fp) - e, min(q[1] for q in fp) - e
        return (x, y, max(q[0] for q in fp) + e - x, max(q[1] for q in fp) + e - y)
    return geom(pl, v)[0]


def geom(pl: Placed, v: View):
    cells = pl.cells()
    a, b = v.xy(cells[0]), v.xy(cells[-1])
    L = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
    u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L) if L else (1.0, 0.0)
    horiz = abs(u[0]) >= 0.5
    kind = pl.defn().get("kind")
    hw = (0.24 if kind == "wire" else 0.36) * v.p
    e = CASE * v.p
    x0, x1, y0, y1 = min(a[0], b[0]), max(a[0], b[0]), min(a[1], b[1]), max(a[1], b[1])
    if horiz:
        rect = (x0 - e, y0 - hw, x1 - x0 + 2 * e, 2 * hw)
    else:
        rect = (x0 - hw, y0 - e, 2 * hw, y1 - y0 + 2 * e)
    return rect, u, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), a


def spin_group(cx, cy, r, colour, rev, on, extra="") -> str:
    blades = "".join(
        f'<ellipse cx="{cx:.1f}" cy="{cy - r * 0.55:.1f}" rx="{r * 0.28:.1f}" ry="{r * 0.55:.1f}" fill="{colour}" opacity="0.9" transform="rotate({a} {cx:.1f} {cy:.1f})"/>'
        for a in (0, 120, 240)
    )
    anim = ""
    if on:
        to = -360 if rev else 360
        anim = f'<animateTransform attributeName="transform" type="rotate" from="0 {cx:.1f} {cy:.1f}" to="{to} {cx:.1f} {cy:.1f}" dur="0.7s" repeatCount="indefinite"/>'
    return f'<g>{blades}<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.16:.1f}" fill="#fff" stroke="#555"/>{anim}</g>\n{extra}'


def glow(cx, cy, r, colour, anim=True) -> str:
    pulse = '<animate attributeName="opacity" values="0.3;0.6;0.3" dur="1.4s" repeatCount="indefinite"/>' if anim else ""
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{colour}" opacity="0.45">{pulse}</circle>\n'


def draw_glyph(pl: Placed, v: View, cx, cy, toks: set, a: Assign, anim: bool) -> str:
    d, p = pl.defn(), v.p * 0.8
    kind, eff = d.get("kind"), d.get("effect")
    on = "on" in toks
    if kind == "switch":
        closed = a.sw.get(pl.key, False)
        if d.get("momentary"):
            # a button: pressed is pushed in, with the push arrow on it
            s = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.24 * p:.1f}" fill="{"#0b3d20" if closed else "#ffffff"}" stroke="#0b3d20" stroke-width="4"/>\n'
            if closed:
                s += f'<path d="M {cx:.1f} {cy - 0.62 * p:.1f} L {cx:.1f} {cy - 0.3 * p:.1f} M {cx - 0.12 * p:.1f} {cy - 0.42 * p:.1f} L {cx:.1f} {cy - 0.28 * p:.1f} L {cx + 0.12 * p:.1f} {cy - 0.42 * p:.1f}" stroke="#ff7a1a" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>\n'
            return s
        # Slide switch: the body carries ON/OFF. A lever here covered the name.
        return ""
    if eff == "light":
        if d.get("polarity") == "colour":
            # Unlit, the two coloured halves of the body are the picture.
            # A grey bulb in the middle covered the seam.
            if not next((t for t in toks if t in LIT), None):
                return ""
            col = LIT[next(t for t in toks if t in LIT)]
        elif d.get("glow") == "white":
            # L4: a clear block with a round lens in the middle. Lit, it is a
            # white light, so the rays carry the "on" on a white page.
            s = glow(cx, cy, 0.8 * p, "#ffe58a", anim) if on else ""
            if on:
                for k in range(8):
                    ang = k * math.pi / 4
                    s += (f'<line x1="{cx + 0.3 * p * math.cos(ang):.1f}" y1="{cy + 0.3 * p * math.sin(ang):.1f}" '
                          f'x2="{cx + 0.52 * p * math.cos(ang):.1f}" y2="{cy + 0.52 * p * math.sin(ang):.1f}" '
                          f'stroke="#f5a700" stroke-width="{max(3, 0.05 * p):.1f}" stroke-linecap="round"/>\n')
            lens = "#ffffff" if on else "#cfd9e2"
            return s + f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.2 * p:.1f}" fill="{lens}" stroke="#7f95a8" stroke-width="3"/>\n'
        else:
            col = "#ffd43b" if on else "#f4efdc"
        s = glow(cx, cy, 0.8 * p, col, anim) if on else ""
        # glass dome and a small bulb, the way the real lamp reads
        s += f'<path d="M {cx - 0.16 * p:.1f} {cy + 0.12 * p:.1f} Q {cx:.1f} {cy - 0.34 * p:.1f} {cx + 0.16 * p:.1f} {cy + 0.12 * p:.1f} Z" fill="{col}" fill-opacity="0.85" stroke="#6b5a2e" stroke-width="3"/>\n'
        return s + f'<circle cx="{cx:.1f}" cy="{cy + 0.02 * p:.1f}" r="{0.07 * p:.1f}" fill="#fff8dc" stroke="#555" stroke-width="2"/>\n'
    if eff == "spin":
        extra = glow(cx, cy, 0.7 * p, "#ffe066", anim) if (on and d.get("glows")) else ""
        return extra + spin_group(cx, cy, 0.27 * p, "#d9c2f5", "rev" in toks, on and anim)
    if eff == "sound":
        s = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.15 * p:.1f}" fill="{INK}"/>\n'
        for i, k in enumerate((0.26, 0.38)):
            an = f'<animate attributeName="opacity" values="1;0.2;1" dur="{0.9 + i * 0.3}s" repeatCount="indefinite"/>' if (on and anim) else ""
            op = "1" if on else "0.25"
            s += f'<path d="M {cx + k * p:.1f} {cy - 0.14 * p:.1f} Q {cx + (k + 0.1) * p:.1f} {cy:.1f} {cx + k * p:.1f} {cy + 0.14 * p:.1f}" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round" opacity="{op}">{an}</path>\n'
        return s
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.17 * p:.1f}" fill="#fff" stroke="#555" stroke-width="3"/>\n'


def _colour_halves(x, y, w, h, first, cx, cy):
    """(red box, yellow box). Red is the end with the + mark."""
    if w >= h:
        mid = x + w / 2
        left, right = (x, y, w / 2, h), (mid, y, w / 2, h)
        return (left, right) if first[0] <= cx else (right, left)
    mid = y + h / 2
    top, bot = (x, y, w, h / 2), (x, mid, w, h / 2)
    return (top, bot) if first[1] <= cy else (bot, top)


def draw_part(pl: Placed, v: View, opacity: float, toks: set, a: Assign, anim: bool, badge: bool = True) -> str:
    d, p = pl.defn(), v.p
    (x, y, w, h), u, (cx, cy), first = geom(pl, v)
    kind = d["kind"]
    s = ""
    sn = pl.snaps()
    snap_xy = [v.xy(c) for c in sn]
    box = (x, y, w, h)
    if kind == "source":
        # A 3x3 holder: the snaps are two corners of one edge, and the case
        # (with the batteries) lies to its `side`, usually hanging off the grid.
        fp = [v.xy(c) for c in pl.footprint()]
        e = CASE * p
        bx, by = min(q[0] for q in fp) - e, min(q[1] for q in fp) - e
        bw, bh = max(q[0] for q in fp) + e - bx, max(q[1] for q in fp) + e - by
        box = (bx, by, bw, bh)
        s += f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="{0.14 * p:.1f}" fill="#e7f4fb" fill-opacity="0.96" stroke="#6f93ab" stroke-width="4"/>\n'
        horiz = pl.dir in ("left", "right")
        far = [v.xy(c) for c in pl.body_cells()]
        if far:
            # the batteries lie along the snap edge, in the part of the case away from it
            fx0, fy0 = min(q[0] for q in far) - e, min(q[1] for q in far) - e
            fx1, fy1 = max(q[0] for q in far) + e, max(q[1] for q in far) + e
            ncells = int(d.get("cells") or 2)
            for i in range(ncells):
                t = (i + 0.5) / ncells
                if horiz:
                    my = fy0 + (fy1 - fy0) * t
                    rx0, rx1 = fx0 + 0.22 * p, fx1 - 0.22 * p
                    s += f'<rect x="{rx0:.1f}" y="{my - 0.2 * p:.1f}" width="{rx1 - rx0:.1f}" height="{0.4 * p:.1f}" rx="{0.12 * p:.1f}" fill="#3a3a3a"/>\n'
                    cap = rx0 if i % 2 == 0 else rx1 - 0.5 * p
                    s += f'<rect x="{cap:.1f}" y="{my - 0.2 * p:.1f}" width="{0.5 * p:.1f}" height="{0.4 * p:.1f}" rx="{0.1 * p:.1f}" fill="#c4a574"/>\n'
                else:
                    mx = fx0 + (fx1 - fx0) * t
                    ry0, ry1 = fy0 + 0.22 * p, fy1 - 0.22 * p
                    s += f'<rect x="{mx - 0.2 * p:.1f}" y="{ry0:.1f}" width="{0.4 * p:.1f}" height="{ry1 - ry0:.1f}" rx="{0.12 * p:.1f}" fill="#3a3a3a"/>\n'
                    cap = ry0 if i % 2 == 0 else ry1 - 0.5 * p
                    s += f'<rect x="{mx - 0.2 * p:.1f}" y="{cap:.1f}" width="{0.4 * p:.1f}" height="{0.5 * p:.1f}" rx="{0.1 * p:.1f}" fill="#c4a574"/>\n'
        else:
            ncells = int(d.get("cells") or 2)
            for i in range(ncells):
                t = (i + 0.5) / ncells
                bx2, by2 = x + w * t, y + h * t
                if horiz:
                    s += f'<rect x="{bx2 - 0.32 * p:.1f}" y="{cy - 0.14 * p:.1f}" width="{0.64 * p:.1f}" height="{0.28 * p:.1f}" rx="{0.08 * p:.1f}" fill="#3a3a3a"/>\n'
                else:
                    s += f'<rect x="{cx - 0.14 * p:.1f}" y="{by2 - 0.32 * p:.1f}" width="{0.28 * p:.1f}" height="{0.64 * p:.1f}" rx="{0.08 * p:.1f}" fill="#3a3a3a"/>\n'
        # The battery sign is printed along the snap edge. Nothing can lie on
        # that edge between the snaps (it is plastic), so + and - drawn just
        # inside each snap are never covered by a wire.
        mx, my = (snap_xy[0][0] + snap_xy[-1][0]) / 2, (snap_xy[0][1] + snap_xy[-1][1]) / 2
        s += text(mx, my + 0.1 * p, f"{d.get('volts', '')}V", 0.24 * p, "#c0392b", "bold", "middle")
        dr, dc = DIRS[pl.dir]
        for cell in sn:
            sx, sy = v.xy(cell)
            plus = cell == pl.cells()[d["plus"]]
            inward = 1 if cell == pl.cells()[0] else -1
            s += f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{0.16 * p:.1f}" fill="#d8dde3" stroke="#5c6770" stroke-width="3"/>\n'
            s += text(sx + dc * inward * 0.5 * p, sy + dr * inward * 0.5 * p + 0.12 * p, "+" if plus else "\u2212",
                      0.4 * p, "#c0392b" if plus else "#22405f", "bold", "middle")
    else:
        if pl.level > 1:
            s += f'<rect x="{x + 5:.1f}" y="{y + 7:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{0.2 * p:.1f}" fill="#000" opacity="0.16"/>\n'
        fill = d["colour"]
        label = "#fff" if not is_pale(fill) else INK
        shut = kind == "switch" and not d.get("momentary") and not a.sw.get(pl.key, False)
        split = False
        if kind == "switch" and not d.get("momentary"):
            # ON is a solid green block. OFF is a pale block with an orange
            # break through the middle, so a thumbnail still shows the gate.
            fill = "#fff7ed" if shut else "#0f7a32"
            label = "#9a3412" if shut else "#ffffff"
        elif d.get("polarity") == "colour":
            # Lit: the whole block is that colour (the answer). Dark: grey,
            # the light is off. Not yet solved: red half at the + end, yellow
            # half at the other, so the two boards can be told apart.
            lit = next((t for t in toks if t in LIT), None)
            if lit == "red":
                fill = "#e23d3d"
            elif lit == "yellow":
                fill, label = "#ffd43b", "#3a2a00"
            elif "off" in toks:
                fill, label = "#4b5568", "#fff"
            else:
                split = True
                fill, label = "#fffdf8", "#1d2433"
        s += f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{0.2 * p:.1f}" fill="{fill}" stroke="#102216" stroke-width="3"/>\n'
        if split:
            red, yel = _colour_halves(x, y, w, h, first, cx, cy)
            s += f'<rect x="{yel[0]:.1f}" y="{yel[1]:.1f}" width="{yel[2]:.1f}" height="{yel[3]:.1f}" fill="#ffd43b"/>\n'
            s += f'<rect x="{red[0]:.1f}" y="{red[1]:.1f}" width="{red[2]:.1f}" height="{red[3]:.1f}" fill="#e23d3d"/>\n'
            s += f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{0.2 * p:.1f}" fill="none" stroke="#102216" stroke-width="4"/>\n'
        if shut:
            # a gap through the middle: the gate is shut, so the path is broken
            band = 0.32 * p
            if abs(u[0]) >= 0.5:
                s += f'<rect x="{cx - band / 2:.1f}" y="{y - 2:.1f}" width="{band:.1f}" height="{h + 4:.1f}" fill="#f97316"/>\n'
            else:
                s += f'<rect x="{x - 2:.1f}" y="{cy - band / 2:.1f}" width="{w + 4:.1f}" height="{band:.1f}" fill="#f97316"/>\n'
        if kind == "wire":
            # the white stripe down a real blue 3-snap wire
            if abs(u[0]) >= 0.5:
                s += f'<rect x="{x + 0.08 * p:.1f}" y="{cy - 0.05 * p:.1f}" width="{w - 0.16 * p:.1f}" height="{0.1 * p:.1f}" rx="{0.04 * p:.1f}" fill="#f7fbff"/>\n'
            else:
                s += f'<rect x="{cx - 0.05 * p:.1f}" y="{y + 0.08 * p:.1f}" width="{0.1 * p:.1f}" height="{h - 0.16 * p:.1f}" rx="{0.04 * p:.1f}" fill="#f7fbff"/>\n'
        ends = {sn[0], sn[-1]} if kind == "wire" else set(sn)
        for cell in sn:
            sx, sy = v.xy(cell)
            r = 0.12 * p if cell in ends else 0.07 * p
            s += f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{r:.1f}" fill="#e6e6e6" stroke="#6b6b6b" stroke-width="2.5"/>\n'
        if kind == "wire":
            lx, ly = first[0] + u[0] * 0.5 * p, first[1] + u[1] * 0.5 * p
            s += text(lx, ly + 0.09 * p, d["printed"], 0.27 * p, "#1d4e89", "bold", "middle")
        else:
            # glyph above, printed ID below: both fit between the two snaps
            # whichever way the block lies
            s += draw_glyph(pl, v, cx, cy - 0.13 * p, toks, a, anim)
            if kind == "switch" and not d.get("momentary"):
                # The state word is a pill beside the block. A word in the
                # middle sits under the wire and cannot be read.
                s += text(cx, cy + 0.42 * p, d["printed"], 0.16 * p, label, "bold", "middle")
            else:
                if split:
                    s += f'<rect x="{cx - 0.24 * p:.1f}" y="{cy + 0.14 * p:.1f}" width="{0.48 * p:.1f}" height="{0.30 * p:.1f}" rx="{0.08 * p:.1f}" fill="#fff" stroke="#102216" stroke-width="2"/>\n'
                s += text(cx, cy + 0.33 * p, d["printed"], 0.21 * p, label, "bold", "middle")
    if badge:
        if abs(u[0]) >= 0.5:
            bx, by = x + 0.14 * p, y
        else:
            bx, by = x, y + 0.14 * p
        s += f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{0.14 * p:.1f}" fill="#fff" stroke="{INK}" stroke-width="2.5"/>\n'
        s += text(bx, by + 0.06 * p, str(pl.level), 0.18 * p, INK, "bold", "middle")
    return f'<g opacity="{opacity}"{drawn_attrs(pl, v, snap_xy, box)}>\n' + s + "</g>\n"


def is_pale(colour: str) -> bool:
    c = colour.lstrip("#")
    if len(c) != 6:
        return False
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    return 0.299 * r + 0.587 * g + 0.114 * b > 170


def wind(gx, gy, p, up: bool, anim: bool) -> str:
    """Little chevrons beside a fan: up = it blows wind at your hand."""
    s = ""
    for i, dx in enumerate((-0.7, 0.7)):
        x = gx + dx * p
        sign = -1 if up else 1
        pts = f"{x - 0.12 * p:.1f},{gy:.1f} {x:.1f},{gy + sign * 0.14 * p:.1f} {x + 0.12 * p:.1f},{gy:.1f}"
        an = (f'<animateTransform attributeName="transform" type="translate" values="0 0; 0 {sign * 0.3 * p:.1f}" dur="0.9s" begin="{i * 0.3}s" repeatCount="indefinite"/>'
              f'<animate attributeName="opacity" values="1;0" dur="0.9s" begin="{i * 0.3}s" repeatCount="indefinite"/>') if anim else ""
        s += f'<polyline points="{pts}" fill="none" stroke="#1e90ff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">{an}</polyline>\n'
    return s


def draw_accessory(pl: Placed, host: Placed, v: View, toks: set, anim: bool) -> str:
    (_, _, _, _), u, (cx, cy), _ = geom(host, v)
    p = v.p
    if not pl.defn().get("blades"):
        tint = next((LIT[t] for t in toks if t in LIT), "")
        # The white ball is the bulb you see. When the light is on, it glows
        # that colour; dark, it stays the white egg. It sits over the middle
        # of the light, between the two end snaps, so it never hides the +.
        fill, op = (tint, 0.92) if tint else ("#fffaf4", 0.72)
        r = 0.8 * p
        return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" fill-opacity="{op}" stroke="#d9d0c4" stroke-width="4"'
                f' data-egg-on="{host.step}"/>\n')
    gx, gy = cx - u[0] * 0.3 * p, cy - u[1] * 0.3 * p
    s = spin_group(gx, gy, 0.42 * p, "#f2994a", "rev" in toks, "on" in toks and anim)
    if "blow" in toks or "fly" in toks:
        s += wind(gx, gy - 0.1 * p, p, "blow" in toks, anim)
    return s


def draw_launch(pl: Placed, host: Placed, v: View, anim: bool) -> str:
    (_, _, _, _), u, (cx, cy), _ = geom(host, v)
    gx, gy, p = cx - u[0] * 0.3 * v.p, cy - u[1] * 0.3 * v.p, v.p
    if not anim:
        return spin_group(gx, gy, 0.42 * p, "#f2994a", False, False)
    up = -2.6 * p
    trail = f'<path d="M {gx:.1f} {gy:.1f} L {gx:.1f} {gy + up:.1f}" stroke="#f2994a" stroke-width="5" stroke-dasharray="6 14" opacity="0.6"/>\n'
    fly = (f'<g><animateTransform attributeName="transform" type="translate" values="0 0; 0 {up:.1f}; 0 {up:.1f}" keyTimes="0;0.7;1" dur="2.2s" repeatCount="indefinite"/>'
           f'<animate attributeName="opacity" values="1;1;0" keyTimes="0;0.6;1" dur="2.2s" repeatCount="indefinite"/>'
           + spin_group(gx, gy, 0.42 * p, "#f2994a", False, True) + "</g>\n")
    return trail + fly


def draw_turn(pl: Placed, v: View) -> str:
    """A round arrow around a block: turn it the other way round."""
    (_, _, _, _), _, (cx, cy), _ = geom(pl, v)
    r = 0.95 * v.p
    a0, a1 = math.radians(-150), math.radians(150)
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    s = f'<path d="M {x0:.1f} {y0:.1f} A {r:.1f} {r:.1f} 0 1 1 {x1:.1f} {y1:.1f}" fill="none" stroke="#ff7a1a" stroke-width="9" stroke-linecap="round"/>\n'
    hx, hy = x1, y1
    s += f'<path d="M {hx - 22:.1f} {hy - 4:.1f} L {hx:.1f} {hy:.1f} L {hx - 4:.1f} {hy + 22:.1f}" fill="none" stroke="#ff7a1a" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>\n'
    return s


def chain_points(ev: Result) -> list:
    pts = []
    for path in ev.live:
        nodes = [ev.graph.plus] + [to for _, _, to in path]
        pts.append(nodes)
    if not pts and len(ev.dead) > 1:
        pts.append(ev.dead)
    return pts


def draw_flow(ev: Result, v: View, anim: bool, colour="#1e90ff") -> str:
    s = ""
    gap = max(26, 0.36 * v.p)
    for nodes in chain_points(ev):
        pts = " ".join(f"{v.xy(n)[0]:.1f},{v.xy(n)[1]:.1f}" for n in nodes)
        s += f'<polyline points="{pts}" fill="none" stroke="#bfe3ff" stroke-opacity="0.65" stroke-width="{0.2 * v.p:.1f}" stroke-linecap="round" stroke-linejoin="round"/>\n'
        move = f'<animate attributeName="stroke-dashoffset" from="0" to="{-(gap + 0.1):.1f}" dur="0.9s" repeatCount="indefinite"/>' if anim else ""
        s += f'<polyline points="{pts}" fill="none" stroke="{colour}" stroke-width="{0.15 * v.p:.1f}" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="0.1 {gap:.1f}">{move}</polyline>\n'
    return s


def draw_markers(circ: Circuit, ev: Result, a: Assign, v: View) -> str:
    s = ""
    if ev.live or not ev.dead:
        return s
    last = ev.dead[-1]
    spots = []
    for (u, w, pl) in ev.graph.open_switches:
        if last in (u, w):
            (_, _, c, _) = geom(pl, v)
            spots.append((c, "Gate shut"))
    for pl in circ.placed:
        if pl.step in a.remove and last in pl.snaps():
            (r, _, c, _) = geom(pl, v)
            s += f'<rect x="{r[0]:.1f}" y="{r[1]:.1f}" width="{r[2]:.1f}" height="{r[3]:.1f}" rx="{0.2 * v.p:.1f}" fill="none" stroke="#c0392b" stroke-width="4" stroke-dasharray="10 8"/>\n'
            spots.append((c, "Missing!"))
    for pl in ev.parts:
        d = pl.defn()
        if d.get("polarity") == "silent" and pl.cells() and last in pl.snaps():
            (_, _, c, _) = geom(pl, v)
            spots.append((c, "Wrong way!"))
    for (cx, cy), label in spots[:1]:
        p = v.p
        tw = len(label) * 0.15 * p + 0.3 * p
        s += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.26 * p:.1f}" fill="#d62828" stroke="#fff" stroke-width="4"/>\n'
        s += text(cx, cy + 0.12 * p, "\u00d7", 0.42 * p, "#fff", "bold", "middle")
        s += f'<rect x="{cx - tw / 2:.1f}" y="{cy + 0.36 * p:.1f}" width="{tw:.1f}" height="{0.36 * p:.1f}" rx="{0.18 * p:.1f}" fill="#fff" stroke="#c0392b" stroke-width="3"/>\n'
        s += text(cx, cy + 0.62 * p, label, 0.24 * p, "#c0392b", "bold", "middle")
    return s


def draw_hidden(circ: Circuit, a: Assign, v: View) -> str:
    s = ""
    for pl in circ.placed:
        if pl.step in a.hide:
            (r, _, (cx, cy), _) = geom(pl, v)
            s += f'<rect x="{r[0]:.1f}" y="{r[1]:.1f}" width="{r[2]:.1f}" height="{r[3]:.1f}" rx="{0.2 * v.p:.1f}" fill="#fff6e0" stroke="#e08a00" stroke-width="5" stroke-dasharray="12 9"/>\n'
            s += text(cx, cy + 0.2 * v.p, "?", 0.62 * v.p, "#e08a00", "bold", "middle")
    return s


def draw_plus(pl: Placed, v: View) -> str:
    """The + mark, drawn last so a wire snap cannot hide it.

    It sits on the + snap. Drawn last, so a tube on that snap cannot hide
    it, and it cannot float off the part onto the wrong end.
    """
    d = pl.defn()
    if d.get("polarity") not in ("colour", "spin", "silent") or not pl.snaps():
        return ""
    p = v.p
    (_, _, _, _), _, _, first = geom(pl, v)
    big = d.get("polarity") == "colour"
    px, py = first
    rad = 0.30 * p if big else 0.20 * p
    s = f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rad:.1f}" fill="#fff" stroke="#d62828" stroke-width="{max(3, 0.06 * p):.1f}"/>\n'
    s += text(px, py + (0.10 * p if big else 0.06 * p), "+", 0.40 * p if big else 0.26 * p, "#d62828", "bold", "middle")
    return s


def draw_gate_label(pl: Placed, v: View, a: Assign) -> str:
    """ON or OFF beside a slide switch. The wire runs down the middle of the
    block, so a word drawn there disappears."""
    d = pl.defn()
    if d.get("kind") != "switch" or d.get("momentary"):
        return ""
    shut = not a.sw.get(pl.key, False)
    p = v.p
    (x, y, w, h), u, (cx, cy), _ = geom(pl, v)
    word = "OFF" if shut else "ON"
    fill = "#f97316" if shut else "#0f7a32"
    tw, th = (0.95 * p, 0.40 * p)
    if abs(u[0]) >= 0.5:
        px, py = cx - tw / 2, y + h + 0.08 * p
    else:
        px, py = x + w + 0.06 * p, cy - th / 2
    s = f'<rect x="{px:.1f}" y="{py:.1f}" width="{tw:.1f}" height="{th:.1f}" rx="{th / 2:.1f}" fill="{fill}" stroke="#102216" stroke-width="3"/>\n'
    s += text(px + tw / 2, py + th * 0.72, word, 0.26 * p, "#fff", "bold", "middle")
    return s


def draw_board(circ: Circuit, v: View, a: Assign, ev: Result | None, *, upto=None, new=(), ghost=False,
               anim=True, flow=True, turn=()) -> str:
    parts = effective_parts(circ, a)
    toks = ev.tokens if ev else {}
    s = board_base(v)
    body = [pl for pl in parts if pl.cells() and (upto is None or pl.step <= upto)]
    for pl in sorted(body, key=lambda q: (q.level, q.step)):
        op = 0.3 if (ghost and pl.step not in new) else 1
        s += draw_part(pl, v, op, toks.get(pl.step, set()), a, anim)
    hosts = {pl.step: pl for pl in body}
    for pl in parts:
        if pl.defn().get("kind") == "accessory" and pl.host in hosts and (upto is None or pl.step <= upto):
            host = hosts[pl.host]
            if a.launch == host.step and ev is not None:
                s += draw_launch(pl, host, v, anim)
            else:
                s += draw_accessory(pl, host, v, toks.get(host.step, set()), anim)
    for pl in body:
        if pl.step in new:
            r = part_box(pl, v)
            pulse = '<animate attributeName="stroke-opacity" values="1;0.35;1" dur="1.1s" repeatCount="indefinite"/>' if anim else ""
            s += f'<rect x="{r[0] - 7:.1f}" y="{r[1] - 7:.1f}" width="{r[2] + 14:.1f}" height="{r[3] + 14:.1f}" rx="{0.26 * v.p:.1f}" fill="none" stroke="#ff7a1a" stroke-width="8">{pulse}</rect>\n'
        if pl.step in turn:
            s += draw_turn(pl, v)
    if ev and flow:
        s += draw_flow(ev, v, anim)
        if not a.launch:  # a launch page is about the fan, not the open switch
            s += draw_markers(circ, ev, a, v)
    s += draw_hidden(circ, a, v)
    for pl in body:
        s += draw_plus(pl, v)
        s += draw_gate_label(pl, v, a)
    return s


def board_panel(circ: Circuit, a: Assign, sha: str, *, effects=True, upto=None, new=(), ghost=False, turn=(),
                left=24, tight=False, zoom=False) -> str:
    """`left` leaves room for the find card on build pages; `tight` crops to
    the board for the small puzzle and mission panels. `zoom` frames the
    gate and the colour block, which is the whole clue on those cards."""
    cells = clue_cells(circ, a) if zoom else []
    v = zoom_view(cells, 20, 20, PW - 20, PH - 20) if cells else fit_view(circ, left, 24, PW - 24, PH - 24)
    ev = evaluate(circ, a) if effects else None
    body = draw_board(circ, v, a, ev, upto=upto, new=new, ghost=ghost, flow=effects, turn=turn)
    if not tight and not cells:
        return panel_open(sha) + body + "</svg>\n"
    p = v.p
    if cells:
        x, y = v.ox - 1.05 * p, v.oy - 1.75 * p
        w, h = (v.c1 - v.c0) * p + 1.7 * p, (v.r1 - v.r0) * p + 3.2 * p
    else:
        mt, mr, mb, ml = v.margin
        x, y = v.ox - ml * p, v.oy - mt * p
        w, h = (v.c1 - v.c0 + ml + mr) * p, (v.r1 - v.r0 + mt + mb) * p
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" viewBox="{x:.1f} {y:.1f} {w:.1f} {h:.1f}" '
            f'font-family="{FONT}">\n<!-- snap-sha: {sha} -->\n<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#ffffff"/>\n'
            + body + "</svg>\n")


def part_panel(key: str, sha: str) -> str:
    d = part_def(key) or {}
    s = panel_open(sha)
    kind = d.get("kind")
    if kind == "grid":
        cols, rows = d["cols"], d["rows"]
        m = 2 * (PLATE + LABEL)
        p = min((PW - 160) / (cols - 1 + m), (PH - 160) / (rows - 1 + m))
        v = View((PW - (cols - 1) * p) / 2, (PH - (rows - 1) * p) / 2, p, 0, rows - 1, 0, cols - 1)
        return s + board_base(v) + "</svg>\n"
    if kind == "accessory":
        cx, cy = PW / 2, PH / 2
        if d.get("blades"):
            s += spin_group(cx, cy, 300, d.get("colour", "#f2994a"), False, False)
        else:
            s += f'<ellipse cx="{cx}" cy="{cy}" rx="200" ry="250" fill="#ffffff" fill-opacity="0.85" stroke="#999" stroke-width="8"/>\n'
        return s + "</svg>\n"
    span, depth = d.get("span", 3), d.get("depth", 1)
    # a deep block (B3B) is shown the way it sits on the board: snaps along
    # the bottom edge, the batteries above them
    pl = Placed(1, key, 0, depth - 1, 0, "right", 1, side="up" if depth > 1 else "")
    p = min(300, (PW - 260) / (span - 1 + 2 * CASE + 0.4), (PH - 200) / (depth - 1 + 2 * CASE + 0.4))
    v = View((PW - (span - 1) * p) / 2, (PH - (depth - 1) * p) / 2, p, 0, depth - 1, 0, span - 1)
    s += draw_part(pl, v, 1, set(), Assign(), False, badge=False)
    return s + "</svg>\n"


def water_panel(circ: Circuit, a: Assign, sha: str) -> str:
    """The water-park picture of a board: the pump, the slide tubes, the gate
    and the wheels. Water runs when the board works; when it does not, the
    picture shows where it stops and why."""
    shape = a.copy()
    shape.remove, shape.hide, shape.launch = set(), set(), 0
    shape = closed_all(circ, shape)
    sg = build_graph(effective_parts(circ, shape), shape)
    paths = find_paths(sg)
    s = panel_open(sha, "#dff3ff")
    if not paths:
        return s + "</svg>\n"
    paths = paths[:4]
    loops = [[sg.plus] + [to for _, _, to in pth] + [sg.plus] for pth in paths]
    xs = [c for lp in loops for _, c in lp]
    ys = [r for lp in loops for r, _ in lp]
    x0, y0, x1, y1 = 240, 150, PW - 240, PH - 190
    sc = min((x1 - x0) / max(1, max(xs) - min(xs)), (y1 - y0) / max(1, max(ys) - min(ys)), 200)
    ox = x0 + ((x1 - x0) - (max(xs) - min(xs)) * sc) / 2
    oy = y0 + ((y1 - y0) - (max(ys) - min(ys)) * sc) / 2

    def P(cell):
        return (ox + (cell[1] - min(xs)) * sc, oy + (cell[0] - min(ys)) * sc)

    ev = evaluate(circ, a)
    live_sigs = {tuple(e.part.step for e, _, _ in pth) for pth in ev.live}

    def blocker_of(pth):
        for e, frm, _ in pth:
            st = e.part.step
            if st in a.remove or st in a.hide:
                return ("gap", e.part)
            if e.kind == "switch" and not a.sw.get(e.part.key, False):
                return ("gate", e.part)
            if e.kind == "load" and e.part.defn().get("polarity") == "silent" and frm != e.u:
                return ("flap", e.part)
        return None

    flowing = [tuple(e.part.step for e, _, _ in pth) in live_sigs for pth in paths]
    blockers = []
    for pth, ok in zip(paths, flowing):
        b = None if ok else blocker_of(pth)
        if b and all(b[1].step != o[1].step for o in blockers):
            blockers.append(b)

    s += '<ellipse cx="250" cy="90" rx="140" ry="40" fill="#fff" opacity="0.9"/><ellipse cx="960" cy="70" rx="170" ry="46" fill="#fff" opacity="0.9"/>\n'
    s += f'<rect x="0" y="{PH - 90}" width="{PW}" height="90" fill="#bfe9b0"/>\n'
    pts_all = [" ".join(f"{P(n)[0]:.1f},{P(n)[1]:.1f}" for n in lp) for lp in loops]
    for pts in pts_all:
        s += f'<polyline points="{pts}" fill="none" stroke="#1f7fc4" stroke-width="74" stroke-linecap="round" stroke-linejoin="round"/>\n'
    for pts in pts_all:
        s += f'<polyline points="{pts}" fill="none" stroke="#9fdcff" stroke-width="56" stroke-linecap="round" stroke-linejoin="round"/>\n'
    for pts, ok in zip(pts_all, flowing):
        if ok:
            s += (f'<polyline points="{pts}" fill="none" stroke="#fff" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="0.1 42">'
                  '<animate attributeName="stroke-dashoffset" from="0" to="-42.1" dur="1.0s" repeatCount="indefinite"/></polyline>\n')
        else:
            s += f'<polyline points="{pts}" fill="none" stroke="#ffffff" stroke-opacity="0.5" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="0.1 42"/>\n'
    R = 54
    mid = P(((min(ys) + max(ys)) / 2, (min(xs) + max(xs)) / 2))

    def vertical(pl):
        sn = pl.snaps() or pl.cells()
        return abs(sn[0][0] - sn[-1][0]) > abs(sn[0][1] - sn[-1][1])

    def centre(pl):
        sn = pl.snaps() or pl.cells()
        a1, b1 = P(sn[0]), P(sn[-1])
        return (a1[0] + b1[0]) / 2, (a1[1] + b1[1]) / 2

    # labels go where they hit nothing: no other label, no wheel, no tube
    tubes = [(min(P(u)[0], P(w)[0]) - 37, min(P(u)[1], P(w)[1]) - 37, max(P(u)[0], P(w)[0]) + 37, max(P(u)[1], P(w)[1]) + 37)
             for lp in loops for u, w in zip(lp, lp[1:])]
    wheels = [centre(e.part) for pth in paths for e, _, _ in pth if e.kind != "wire"]
    wheels.append(centre(next(p for p in effective_parts(circ, shape) if p.defn().get("kind") == "source")))
    taken: list = []

    def hits(b, boxes):
        return sum(1 for o in boxes if b[0] < o[2] and o[0] < b[2] and b[1] < o[3] and o[1] < b[3])

    def label(cx, cy, d, vert):
        dx, dy = cx - mid[0], cy - mid[1]
        w = 0.56 * 30 * max(len(d["kid"]), 1)
        side = [(cx + R + 22, cy, "start"), (cx - R - 22, cy, "end")]
        ends = [(cx, cy + R + 42, "middle"), (cx, cy - R - 40, "middle")]
        if vert:
            near = [(cx, cy + sc + 66, "middle"), (cx, cy - sc - 72, "middle")]
            spots = (side if dx > 0 else side[::-1]) + near + ends
        else:
            spots = (ends if dy > 0 else ends[::-1]) + side

        def box(sp):
            lx, ly, anc = sp
            x0_ = lx if anc == "start" else lx - w if anc == "end" else lx - w / 2
            return (x0_, ly - 28, x0_ + w, ly + 32)

        def cost(sp):
            b = box(sp)
            off = b[0] < 6 or b[2] > PW - 6 or b[1] < 6 or b[3] > PH - 80
            circles = [(x - R, y - R, x + R, y + R) for x, y in wheels]
            return 100 * off + 50 * hits(b, taken) + 20 * hits(b, circles) + hits(b, tubes)

        lx, ly, anchor = min(spots, key=cost)
        taken.append(box((lx, ly, anchor)))
        return text(lx, ly - 2, d["kid"], 30, INK, "bold", anchor) + text(lx, ly + 26, f"({d['printed']})", 22, "#566179", "normal", anchor)

    pump = next(p for p in effective_parts(circ, shape) if p.defn().get("kind") == "source")
    px, py = centre(pump)
    s += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{R}" fill="#ff9f43" stroke="#c96a10" stroke-width="6"/>\n'
    s += f'<path d="M {px:.1f} {py + 26:.1f} L {px:.1f} {py - 24:.1f} M {px - 20:.1f} {py - 4:.1f} L {px:.1f} {py - 26:.1f} L {px + 20:.1f} {py - 4:.1f}" stroke="#fff" stroke-width="11" fill="none" stroke-linecap="round" stroke-linejoin="round"/>\n'
    s += label(px, py, pump.defn(), vertical(pump))
    actual = {p.step: p for p in ev.parts}
    gaps = {b[1].step for b in blockers if b[0] == "gap"}
    flaps = {b[1].step for b in blockers if b[0] == "flap"}
    done = set()
    for pth in paths:
        for e, frm, _ in pth:
            pl = e.part
            if pl.step in done:
                continue
            done.add(pl.step)
            if pl.step in gaps:
                cs = [P(c) for c in pl.cells()]
                gp = " ".join(f"{x:.1f},{y:.1f}" for x, y in cs)
                s += f'<polyline points="{gp}" fill="none" stroke="#dff3ff" stroke-width="80" stroke-linecap="butt"/>\n'
                continue
            if e.kind == "wire":
                continue
            cx, cy = centre(pl)
            d = (actual.get(pl.step) or pl).defn()
            toks = ev.tokens.get(pl.step, {"off"})
            if e.kind == "switch":
                shut = not a.sw.get(pl.key, False)
                s += f'<rect x="{cx - 58:.1f}" y="{cy - 50:.1f}" width="20" height="100" rx="6" fill="#2e9e5b"/><rect x="{cx + 38:.1f}" y="{cy - 50:.1f}" width="20" height="100" rx="6" fill="#2e9e5b"/>\n'
                if shut:
                    s += f'<rect x="{cx - 44:.1f}" y="{cy - 12:.1f}" width="88" height="24" rx="8" fill="#1d6b3f" transform="rotate({90 if not vertical(pl) else 0} {cx:.1f} {cy:.1f})"/>\n'
                else:
                    s += f'<line x1="{cx - 46:.1f}" y1="{cy - 40:.1f}" x2="{cx + 40:.1f}" y2="{cy - 76:.1f}" stroke="#1d6b3f" stroke-width="14" stroke-linecap="round"/>\n'
                s += label(cx, cy + 6, d, vertical(pl))
                continue
            eff = d.get("effect")
            on = toks != {"off"}
            white = d.get("glow") == "white"
            col = next((LIT[t] for t in toks if t in LIT), ("#ffffff" if white else "#ffd43b") if on else ("#dfe6ec" if white else "#f4efdc"))
            if eff == "light" and on:
                s += glow(cx, cy, R * 1.6, "#ffe58a" if white else col)
            if eff == "spin" and on and d.get("glows"):
                s += glow(cx, cy, R * 1.5, "#ffe066")
            fill = col if eff == "light" else ("#d9c2f5" if eff == "spin" else "#bde8f7")
            s += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R}" fill="{fill}" stroke="#7a5b00" stroke-width="6"/>\n'
            spokes = "".join(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx + R * 0.86 * math.cos(k * 1.0472):.1f}" y2="{cy + R * 0.86 * math.sin(k * 1.0472):.1f}" stroke="#7a5b00" stroke-width="7" stroke-linecap="round"/>' for k in range(6))
            if on:
                to = -360 if "rev" in toks else 360
                spokes += f'<animateTransform attributeName="transform" type="rotate" from="0 {cx:.1f} {cy:.1f}" to="{to} {cx:.1f} {cy:.1f}" dur="2.4s" repeatCount="indefinite"/>'
            s += f"<g>{spokes}</g>\n"
            if eff == "sound" and on:
                for i, k in enumerate((1.25, 1.6)):
                    s += (f'<path d="M {cx + R * k:.1f} {cy - R * 0.6:.1f} Q {cx + R * (k + 0.35):.1f} {cy:.1f} {cx + R * k:.1f} {cy + R * 0.6:.1f}" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round">'
                          f'<animate attributeName="opacity" values="1;0.2;1" dur="{0.8 + i * 0.3}s" repeatCount="indefinite"/></path>\n')
            if pl.step in flaps:
                s += f'<rect x="{cx - 8:.1f}" y="{cy - R - 18:.1f}" width="16" height="{2 * R + 36}" rx="6" fill="#c0392b" transform="rotate({0 if vertical(pl) else 90} {cx:.1f} {cy:.1f})"/>\n'
            s += label(cx, cy, d, vertical(pl))
    words = {"gap": "Missing tube!", "gate": "Gate shut!", "flap": "Flap shut: wrong way!"}
    for kind_, pl in blockers:
        bx, by = centre(pl)
        s += f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="30" fill="#d62828" stroke="#fff" stroke-width="5"/>\n'
        s += text(bx, by + 14, "\u00d7", 46, "#fff", "bold", "middle")
    if blockers and not ev.live:
        s += text(PW / 2, PH - 34, words[blockers[0][0]] + "  The water stops, so nothing works.", 32, "#c0392b", "bold", "middle")
    elif blockers:
        s += text(PW / 2, PH - 34, words[blockers[0][0]] + "  That way is blocked. The other way still flows!", 32, "#c0392b", "bold", "middle")
    elif sum(flowing) > 1:
        s += text(PW / 2, PH - 34, "The water splits, goes through both wheels, and comes back!", 32, "#1d6b3f", "bold", "middle")
    elif ev.live:
        s += text(PW / 2, PH - 34, "All the way round: the water flows!", 32, "#1d6b3f", "bold", "middle")
    return s + "</svg>\n"


def change_diff(circ: Circuit, prev: Assign, cur: Assign) -> list:
    """What Ian does to go from the last chapter's board to this one:
    (verb, step, old key, new key) with verb swap | turn | add | take."""
    out = []
    for p in circ.placed:
        if p.defn().get("kind") in ("grid", "accessory"):
            continue
        ok, nk = prev.swap.get(p.step, p.key), cur.swap.get(p.step, p.key)
        if ok != nk:
            out.append(("swap", p.step, ok, nk))
        elif (p.step in prev.flip) != (p.step in cur.flip):
            out.append(("turn", p.step, nk, nk))
    for n in sorted(set(prev.add) | set(cur.add)):
        if prev.add.get(n) != cur.add.get(n):
            if cur.add.get(n):
                out.append(("add", n, prev.add.get(n), cur.add[n]))
            elif prev.swap.get(n) == cur.swap.get(n):
                out.append(("take", n, prev.add[n], None))
    # an accessory from the build (the egg) comes off when its block is
    # swapped for one it cannot sit on, and goes back on when it returns
    kept = lambda a: {p.step: p for p in effective_parts(circ, a) if p.defn().get("kind") == "accessory" and p.step < 1000}
    was, now = kept(prev), kept(cur)
    for n in sorted(set(was) | set(now)):
        if n in now and n not in was:
            out.append(("add", now[n].host, None, now[n].key))
        elif n in was and n not in now:
            out.append(("take", was[n].host, was[n].key, None))
    prev_parts = {p.step: p for p in prev.parts}
    cur_parts = {p.step: p for p in cur.parts}
    for n in sorted(set(prev_parts) | set(cur_parts)):
        if n not in prev_parts and n in cur_parts:
            out.append(("add", n, None, cur_parts[n].key))
        elif n in prev_parts and n not in cur_parts:
            out.append(("take", n, prev_parts[n].key, None))
    return out


def change_prevs(circ: Circuit, deck: Deck) -> dict:
    """change name -> the board Ian has in front of him when he reaches it:
    the last page before it that showed a board. After a guess page that
    turned the horn round, "turn it back" is a turn, not nothing."""
    out, last = {}, Assign()
    for s in deck.slides:
        if s.kind == "change" and s.arg in circ.variants:
            out[s.arg] = last
        b = slide_board(circ, s)
        if b is not None:
            last = b
    for v, prev in change_states(circ):
        out.setdefault(v.name, prev)
    return out


def change_states(circ: Circuit) -> list:
    """(Variant, previous Assign) for each change, in file order."""
    out, prev = [], Assign()
    for v in circ.changes():
        out.append((v, prev))
        prev = v.assign
    return out


def colour_puzzle_names(circ: Circuit, deck: Deck) -> set:
    """Boards on a puzzle page where every card is the colour block, and
    none of them is missing a part. Those cards zoom in on the gate and the
    +. A missing wire is a different clue, so that page keeps the whole grid."""
    names = set()
    for s in deck.slides:
        if s.kind != "puzzle":
            continue
        boards = [b.strip() for b in s.f.get("boards", "").split(",") if b.strip()]
        variants = [circ.variants.get(nm) for nm in boards]
        if not boards or any(v is None for v in variants):
            continue
        # A part that is missing on every card is not the clue. The egg is
        # off for the whole colour case; the cards differ by the + and the gate.
        same_gap = len({frozenset(v.assign.remove) for v in variants}) == 1
        same_gap = same_gap and len({frozenset(v.assign.hide) for v in variants}) == 1
        if not same_gap:
            continue
        if all(any(pl.defn().get("polarity") == "colour" for pl in effective_parts(circ, v.assign)) for v in variants):
            names.update(boards)
    return names


def planned_renders(bdir: Path, circ: Circuit, deck: Deck) -> list:
    """(relative path, function that draws it) for every SVG `render` writes."""
    sha = build_hash(bdir)
    zoom = colour_puzzle_names(circ, deck)
    out = []
    card = 470  # build and swap pages: the find card sits on the left
    for pl in circ.placed:
        out.append((f"renders/step-{pl.step:03d}.svg",
                    lambda pl=pl: board_panel(circ, Assign(), sha, effects=False, upto=pl.step, new={pl.step}, ghost=True, left=card)))
    prevs = change_prevs(circ, deck)
    for v in circ.changes():
        diff = change_diff(circ, prevs[v.name], v.assign)
        new = {st for _, st, _, _ in diff}
        turn = {st for verb, st, _, _ in diff if verb == "turn"}
        shown = v.assign.copy()
        shown.sw = {}
        out.append((f"renders/change-{v.name}.svg",
                    lambda shown=shown, new=new, turn=turn: board_panel(circ, shown, sha, effects=False, new=new, ghost=True, turn=turn, left=card)))
    for v in circ.variants.values():
        if v.kind == "puzzle":
            z = v.name in zoom
            out.append((f"renders/puzzle-{v.name}.svg", lambda v=v, z=z: board_panel(circ, v.assign, sha, effects=False, tight=True, zoom=z)))
            out.append((f"renders/puzzle-{v.name}-key.svg", lambda v=v, z=z: board_panel(circ, v.assign, sha, tight=True, zoom=z)))
        elif v.kind == "mission":
            out.append((f"renders/mission-{v.name}.svg", lambda v=v: board_panel(circ, v.assign, sha, effects=False, tight=True)))
            first = v.claims[0].assign if v.claims else v.assign
            out.append((f"renders/mission-{v.name}-key.svg", lambda a=first: board_panel(circ, a, sha, tight=True)))
    for name, a, _ in circ.scenes:
        out.append((f"renders/scene-{name}.svg", lambda a=a: board_panel(circ, a, sha)))
    seen = set()
    for s in deck.slides:
        if s.kind == "meet" and part_def(s.arg) and s.arg not in seen:
            seen.add(s.arg)
            out.append((f"renders/part-{s.arg}.svg", lambda k=s.arg: part_panel(k, sha)))
        if s.kind == "predict" and isinstance(s.calc.get("assign"), Assign):
            a = s.calc["assign"]
            out.append((f"renders/slide-{s.idx:03d}-q.svg", lambda a=a: board_panel(circ, a, sha, effects=False)))
            out.append((f"renders/slide-{s.idx:03d}-a.svg", lambda a=a: board_panel(circ, a, sha)))
        if isinstance(s.calc.get("board"), Assign):
            # Number Lab boards are maps to count on: no flow, no markers
            lab = s.kind == "numberlab"
            out.append((f"renders/slide-{s.idx:03d}-board.svg",
                        lambda a=s.calc["board"], t=lab: board_panel(circ, a, sha, tight=t, effects=not t)))
        if isinstance(s.calc.get("water"), Assign):
            out.append((f"renders/slide-{s.idx:03d}-water.svg", lambda a=s.calc["water"]: water_panel(circ, a, sha)))
    return out


def render_build(bdir: Path, circ: Circuit, deck: Deck) -> int:
    out = bdir / "renders"
    out.mkdir(exist_ok=True)
    planned = planned_renders(bdir, circ, deck)
    keep = set()
    for rel, draw in planned:
        (bdir / rel).write_text(draw())
        keep.add(rel)
    gone = 0
    for f in out.glob("*.svg"):
        if f"renders/{f.name}" not in keep:
            f.unlink()
            gone += 1
    print(f"wrote {len(planned)} panels to {out}" + (f", cleared {gone} old ones" if gone else ""))
    return 0


# ------------------------------------------------------------------ preview


SCENE_TAG = {"watch": ("WATCH", "#1e90ff"), "try": ("TRY IT", "#2e9e5b"), "think": ("THINK", "#8e44ad")}
KIND_TAG = {
    "meet": ("MEET", "#2f6db3"), "change": ("SWAP", "#ff7a1a"), "predict": ("GUESS!", "#8e44ad"),
    "why": ("WHY?", "#1e90ff"), "puzzle": ("PUZZLE", "#e07b00"), "mission": ("MISSION", "#d62828"),
    "numberlab": ("NUMBER LAB", "#2e9e5b"), "rule": ("CASE NOTES", "#6b4f2a"), "badge": ("CASE CLOSED", "#d62828"),
}


def switch_words(a: Assign) -> list:
    out = []
    for k, v in sorted(a.sw.items()):
        mom = (part_def(k) or {}).get("momentary")
        out.append(f"{k} {('pressed' if v else 'let go') if mom else ('on' if v else 'off')}")
    return out


def assign_words(circ: Circuit, a: Assign) -> str:
    """A board state in grown-up words, for the answer line."""
    by = {p.step: p for p in circ.placed}
    bits = [f"{key} where {by[n].key} was" for n, key in sorted(a.swap.items()) if n in by]
    bits += [f"{a.swap.get(n, by[n].key)} turned around" for n in sorted(a.flip) if n in by]
    bits += [f"{key} on top" for _, key in sorted(a.add.items())]
    bits += [f"{p.key} added at {post_name(p.r, p.c)}" for p in a.parts]
    bits += [f"step {n} ({by[n].key}) taken out" for n in sorted(a.remove) if n in by]
    bits += switch_words(a)
    return ", ".join(bits) or "the board as built"


def box_label(circ: Circuit, key: str, nth: int = 0) -> str:
    """Which box to take the block from. `nth` is which copy of it this is on
    the board; once the first box has run out, the next one comes from the
    second box (Case 4's fifth blue wire is from the Jr box)."""
    kit = (part_def(key) or {}).get("kit", "")
    if kit == "both":
        if len(circ.kits) == 1:
            kit = circ.kits[0]
        elif nth:
            kit = circ.kits[0] if nth <= read_inventory(circ.kits[0]).get(key, 0) else circ.kits[1]
        else:
            kit = "both"
    return BOX_NAME.get(kit, "")


def chip_html(key: str) -> str:
    d = part_def(key) or {}
    pid = d.get("printed", "-")
    bg = d.get("colour", "#888")
    fg = INK if is_pale(bg) else "#fff"
    return f'<span class="pid" style="background:{bg};color:{fg}">{esc(pid if pid != "-" else d.get("kid", key))}</span>'


def bubble_html(b: Bubble, beat: int, extra: str = "") -> str:
    pos = f" at-{b.pos}" if b.pos else ""
    return (f'<div class="bub beat{pos} {extra}" data-b="{beat}" style="--who:{CAST.get(b.who, "#333")}">'
            f'<span class="who">{esc(b.who)}</span>{esc(b.text)}</div>')


def stars_html(f: dict) -> str:
    n = int(f["stars"]) if f.get("stars", "").isdigit() else 0
    return f'<span class="stars">{"&#9733;" * n}{"&#9734;" * (3 - n)}</span>' if n else ""


def slide_html(bdir: Path, circ: Circuit, deck: Deck, s: Slide, steps: dict, ctx: dict) -> str:
    f = s.f
    sc = steps_copy(steps, s)
    ch = next(c for c in deck.chapters if c.n == s.chapter)
    beats = itertools.count(1)
    pre = [(b, next(beats)) for b in s.bubbles]
    has_reveal = s.kind in ("predict", "puzzle", "numberlab", "mission")
    rv = next(beats) if has_reveal else 0
    post = [(b, next(beats)) for b in s.reveal]
    reveal_dot = f'<i class="beat reveal" data-b="{rv}"></i>' if has_reveal else ""

    def img(rel, cls=""):
        return f'<img class="{cls}" src="{esc(rel)}" alt="">'

    def pose_col():
        bubs = "".join(bubble_html(b, k) for b, k in pre) + "".join(bubble_html(b, k, "post") for b, k in post)
        pose = f.get("pose")
        pimg = f'<div class="panel pose">{img(os.path.relpath(COMIC_DIR / (pose + ".jpg"), bdir))}</div>' if pose else ""
        return f'<div class="col"><div class="bubs">{bubs}</div>{pimg}</div>'

    tag, colour = KIND_TAG.get(s.kind, ("", "#1d2433"))
    box = ""
    say = f.get("say") or sc.get("Say", "")
    main = ""
    answer = ""
    if s.kind == "cover":
        series = deck.meta.get("series", "")
        module = f.get("title") or deck.meta.get("module") or ch.title
        main = (img(f.get("art", ""), "fill")
                + f'<div class="cover-title"><small>{esc(series)}</small>'
                + f'<b>Chapter {ch.n}</b><span>{esc(module)}</span></div>')
    elif s.kind == "splash":
        tag, colour = f"CASE {ch.n}", "#d62828"
        title = f.get("title") or ch.title
        series = deck.meta.get("series", "")
        body = (f'<div class="panel splash">{img(f.get("art", ""), "fill")}</div>'
                f'<div class="splash-title"><small>{esc(series)}</small>{esc(title)}</div>')
        main = body + "".join(bubble_html(b, k) for b, k in pre)
    elif s.kind == "comic":
        n = len(s.panels)
        cells = []
        k = 1
        for i, p in enumerate(s.panels):
            caps = "".join(f'<div class="cap">{esc(c)}</div>' for c in p.captions)
            bubs = ""
            for j, b in enumerate(p.bubbles):
                if not b.pos:
                    b = replace(b, pos=("tr", "bl", "br", "tl")[j % 4] if p.captions else ("tl", "tr", "bl", "br")[j % 4])
                bubs += bubble_html(b, k)
                k += 1
            cells.append(f'<div class="panel cp{n}{"ab"[i]}">{img(p.art, "fill")}{caps}{bubs}</div>')
        main = "".join(cells)
        tag, colour = "", ""
    elif s.kind == "talk":
        cells = []
        k = 1
        lay = f.get("layout", "strip")
        for p in s.panels:
            caps = "".join(f'<div class="cap">{esc(c)}</div>' for c in p.captions)
            bubs = ""
            spots = ("bl", "tr", "tl", "br")
            for j, b in enumerate(p.bubbles):
                if lay == "splash" and not b.pos:
                    b = replace(b, pos=spots[j % 4])
                bubs += bubble_html(b, k)
                k += 1
            src = os.path.relpath(talk_art(bdir, p.art), bdir)
            who = p.bubbles[0].who if p.bubbles else ""
            cells.append(f'<div class="panel" style="--who:{CAST.get(who, "#333")}">{img(src, "fill")}{caps}<div class="boxbubs">{bubs}</div></div>')
        main = f'<div class="talk lay-{lay}" style="--cols:{len(s.panels) or 1}">{"".join(cells)}</div>'
        tag, colour = "LET'S THINK", "#7b4fb5"
    elif s.kind in ("step", "change", "scene", "why", "meet", "predict", "puzzle", "numberlab", "mission", "rule", "badge"):
        inner = ""
        if s.kind == "step":
            pl = next((p for p in circ.placed if str(p.step) == s.arg), None)
            nsteps = len(circ.placed)
            tag, colour = f"BUILD {s.arg}/{nsteps}", "#ff7a1a"
            if pl:
                d = pl.defn()
                box = box_label(circ, pl.key, sum(1 for q in circ.placed if q.key == pl.key and q.step <= pl.step))
                where = ""
                if pl.cells():
                    e0, e1 = pl.ends()
                    where = f'Snaps on <b>{post_name(*e0)}</b> and <b>{post_name(*e1)}</b> <span class="arrow">{ARROWS[pl.dir]}</span>'
                    pp = pl.plus_post()
                    if pp:
                        where += f'<br>The <b>+</b> goes on <b>{post_name(*pp)}</b>'
                    if any(not (0 <= r < circ.rows and 0 <= c < circ.cols) for r, c in pl.body_cells()):
                        where += "<br>The rest hangs off the edge"
                    where += f'<br>{"On top: level " + str(pl.level) if pl.level > 1 else "Level 1"}'
                inner = (img(f"renders/step-{pl.step:03d}.svg", "board")
                         + f'<div class="find">{chip_html(pl.key)}<div><b>{esc(d.get("kid", pl.key))}</b><br>{where}</div></div>')
        elif s.kind == "change":
            v = circ.variants.get(s.arg)
            rows = []
            if v:
                prev = change_prevs(circ, deck).get(v.name, Assign())
                now = {p.step: p for p in effective_parts(circ, v.assign)}

                def plus_at(st):
                    q = now.get(st)
                    pp = q.plus_post() if q and q.defn().get("kind") != "source" else None
                    return f' <span class="where">+ on <b>{post_name(*pp)}</b></span>' if pp else ""

                for verb, st, old, new in change_diff(circ, prev, v.assign):
                    if verb == "swap":
                        rows.append(f'<div><span class="verb out">OUT</span>{chip_html(old)} <span class="verb in">IN</span>{chip_html(new)}{plus_at(st)}</div>')
                        box = box_label(circ, new)
                    elif verb == "turn":
                        rows.append(f'<div><span class="verb in">TURN</span>{chip_html(new)} around{plus_at(st)}</div>')
                    elif verb == "add" and (part_def(new) or {}).get("kind") == "accessory":
                        host = now.get(st)
                        rows.append(f'<div><span class="verb in">ADD</span>{chip_html(new)} on {chip_html(host.key) if host else "top"}</div>')
                    elif verb == "add":
                        q = now.get(st)
                        where = ""
                        if q and q.cells():
                            e0, e1 = q.ends()
                            where = f' <span class="where"><b>{post_name(*e0)}</b> to <b>{post_name(*e1)}</b>, level {q.level}</span>'
                        rows.append(f'<div><span class="verb in">ADD</span>{chip_html(new)}{where}</div>')
                        box = box_label(circ, new, sum(1 for q in now.values() if q.key == new and q.step <= st))
                    else:
                        rows.append(f'<div><span class="verb out">TAKE OFF</span>{chip_html(old)}</div>')
                verbs = {verb for verb, *_ in change_diff(circ, prev, v.assign)}
                if verbs == {"add"}:
                    tag = "ADD"
                elif verbs == {"turn"}:
                    tag = "TURN"
            inner = img(f"renders/change-{s.arg}.svg", "board") + f'<div class="find swaps">{"".join(rows)}</div>'
        elif s.kind == "scene":
            tag, colour = SCENE_TAG.get(s.arg.split("-")[0], ("LOOK", "#1e90ff"))
            inner = img(f"renders/scene-{s.arg}.svg", "board")
        elif s.kind == "why":
            if "water" in s.calc:
                inner = img(f"renders/slide-{s.idx:03d}-water.svg", "board")
            elif "board" in s.calc:
                inner = img(f"renders/slide-{s.idx:03d}-board.svg", "board")
        elif s.kind == "meet":
            d = part_def(s.arg) or {}
            box = box_label(circ, s.arg)
            pid = d.get("printed", "-")
            find = (f'Find the block that says {chip_html(s.arg)}' if pid != "-" else f'Find {esc(d.get("looks_like", ""))}')
            real = f'<div class="real">Really: {esc(d["real"])}</div>' if d.get("real") else ""
            like = f'<div class="like">In the picture: {esc(d["analogy"])}</div>' if d.get("analogy") else ""
            inner = (img(f"renders/part-{s.arg}.svg", "part")
                     + f'<div class="meet"><div class="kid">{esc(d.get("kid", s.arg))}</div><div>{find}</div>'
                     + real + like + "</div>")
        elif s.kind == "predict":
            if "assign" in s.calc:
                inner = img(f"renders/slide-{s.idx:03d}-q.svg", "board q") + img(f"renders/slide-{s.idx:03d}-a.svg", "board a")
            elif "board" in s.calc:
                inner = img(f"renders/slide-{s.idx:03d}-board.svg", "board")
            right = s.calc.get("answer", "")
            show = s.calc.get("show", "")
            answer = right + (f" ({show})" if show and show.lower() != right.lower() else "")
            if "choices" in f:
                try:
                    labs = [lab for lab, _ in parse_choices(f["choices"])]
                except FactError:
                    labs = []
                chips = "".join(f'<span class="choice{" right" if lab == right else ""}">{esc(lab)}</span>' for lab in labs)
            else:
                chips = f'<span class="choice right after">{esc(right)}</span>'
            say = ""
            ctx["say_html"] = f'<span class="ask">{esc(f.get("ask", ""))}</span>{chips}'
        elif s.kind == "puzzle":
            names = [b.strip() for b in f.get("boards", "").split(",") if b.strip()]
            try:
                labs = [lab for lab, _ in parse_choices(f.get("choices", ""))]
            except FactError:
                labs = []
            cells = []
            for i, nm in enumerate(names):
                right = s.calc.get("answers", {}).get(nm, "")
                chips = "".join(f'<span class="choice{" right" if lab == right else ""}">{esc(lab)}</span>' for lab in labs)
                cells.append(f'<div class="mini"><div class="panel"><span class="letter">{chr(65 + i)}</span>'
                             + img(f"renders/puzzle-{nm}.svg", "board q") + img(f"renders/puzzle-{nm}-key.svg", "board a")
                             + f'</div><div class="chips">{chips}</div></div>')
            answer = ", ".join(f"{chr(65 + i)}: {s.calc.get('answers', {}).get(nm, '?')}" for i, nm in enumerate(names))
            cols = 3 if len(names) > 4 or len(names) == 3 else 2
            one_row = " one-row" if len(names) <= cols else ""
            main = pose_col() + f'<div class="grid{one_row}" style="--cols:{cols}">{"".join(cells)}</div>'
            say = ""
            ctx["say_html"] = f'<span class="ask">{esc(f.get("ask", ""))}</span>'
        elif s.kind == "numberlab":
            tag = "TIKA'S NUMBER LAB"
            calc_ = s.calc
            right = calc_.get("answer") or f.get("answer", "")
            answer = f"{right}. {calc_.get('show', '') or f.get('show', '')}"
            table = ""
            if calc_.get("rows"):
                th = "".join(f"<th>{esc(h)}</th>" for h in calc_["head"])
                trs = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r[:-1]) + f'<td class="after">{esc(r[-1])}</td></tr>' for r in calc_["rows"])
                table = f"<table><tr>{th}</tr>{trs}</table>"
            board = img(f"renders/slide-{s.idx:03d}-board.svg", "nb") if "board" in calc_ else ""
            work = calc_.get("show") or f.get("show", "")
            inner = (f'<div class="qtext">{esc(f.get("ask", ""))}</div>{board}{table}'
                     f'<div class="ans after"><b>{esc(right)}</b>{(" &mdash; " + esc(work)) if work else ""}</div>')
            main = pose_col() + f'<div class="panel main note">{inner}</div>'
        elif s.kind == "mission":
            v = s.calc.get("variant")
            q = img(f"renders/mission-{s.arg}.svg", "board q") if f.get("show", "") == "board" else ""
            a = img(f"renders/mission-{s.arg}-key.svg", "board a")
            inner = (f'<div class="card"><div class="cardtitle">Mission</div>{esc(f.get("card", ""))}</div>'
                     f'<div class="mboard">{q}{a}</div>')
            if v:
                proved = "; ".join(f"{', '.join(switch_words(c.assign)) or 'as built'}: {c.key} {' '.join(sorted(c.tokens))}" for c in v.claims)
                answer = f"One board that works: {assign_words(circ, v.assign)}. Checked: {proved}. Other answers can work too."
        elif s.kind == "rule":
            rules = ctx["rules"]
            items = "".join(f'<li class="{"new" if i == len(rules) - 1 else ""}">{esc(r)}</li>' for i, r in enumerate(rules))
            main = pose_col() + f'<div class="panel main note"><div class="qtext">Case notes</div><ol>{items}</ol></div>'
        elif s.kind == "badge":
            crew = os.path.relpath(COMIC_DIR / "crew-cheer.jpg", bdir)
            series = deck.meta.get("series", "")
            main = (f'<div class="panel crew">{img(crew, "fill")}</div>'
                    f'<div class="medal"><small>{esc(series)}</small><b>CASE {ch.n}</b><span>CLOSED</span><i>{esc(ch.badge)}</i></div>'
                    + "".join(bubble_html(b, k) for b, k in pre))
        if not main:
            main = pose_col() + f'<div class="panel main">{inner}</div>'
    title = f.get("title") or ch.title
    tag_html = f'<span class="tag" style="--tag:{colour}">{esc(tag)}</span>' if tag else ""
    box_html = f'<span class="box">{esc(box)}</span>' if box else ""
    head = "" if s.kind == "cover" else (
        f'<header class="top">{tag_html}<span class="chap">Case {ch.n} &middot; {esc(title)}</span>'
        f'{stars_html(f)}{box_html}</header>')
    say_html = ctx.pop("say_html", None)
    if say_html is None:
        say_html = esc(say)
    dad = []
    for lab, val in (("Do", f.get("dad") or sc.get("Do", "")), ("Check", sc.get("Check", "")), ("Ask Ian", sc.get("Ask", "")),
                     ("Watch for", f.get("watch", "")), ("The real reason", f.get("reason", "")), ("Answer", answer)):
        if val:
            dad.append(f"<div><b>{lab}</b>{esc(val)}</div>")
    return (f'<section class="slide k-{s.kind}" data-ch="{s.chapter}">'
            f'<div class="stage">{head}<div class="body">{main}{reveal_dot}</div><div class="say">{say_html}</div></div>'
            f'<aside class="dad">{"".join(dad)}</aside></section>')


CSS = """
:root { --sw: 1100px; --dadh: 0px; --ink: #1b1b1f; --paper: #fdeccd; }
* { box-sizing: border-box; }
body { margin: 0; background: #2b2f3a; color: var(--ink);
  font-family: 'Comic Neue', 'Chalkboard SE', 'Comic Sans MS', cursive; }
nav { height: 46px; display: flex; gap: 6px; align-items: center; justify-content: center;
  font: 600 14px system-ui, sans-serif; color: #dfe4ee; }
nav button { font: inherit; border: 0; border-radius: 999px; padding: 6px 14px; cursor: pointer;
  background: #444b5c; color: #fff; }
nav button.cur { background: #ff7a1a; }
nav .go { background: #ff7a1a; }
nav #where { min-width: 70px; text-align: center; }
.slide { display: none; width: var(--sw); margin: 0 auto; }
.slide.on { display: block; }
.stage { position: relative; width: var(--sw); height: calc(var(--sw) / 1.5); background: var(--paper);
  container-type: size; overflow: hidden; border-radius: 10px; cursor: pointer; }
.top { position: absolute; left: 2cqw; right: 2cqw; top: 1.2cqw; height: 5cqw; display: flex; align-items: center; gap: 1.2cqw; }
.tag { font-family: Bangers, Impact, sans-serif; font-size: 2.8cqw; letter-spacing: .12cqw; color: #fff;
  background: var(--tag); padding: .2cqw 1.4cqw; border: .3cqw solid var(--ink); border-radius: .9cqw; transform: rotate(-2deg); }
.chap { font-family: Bangers, Impact, sans-serif; font-size: 2.3cqw; letter-spacing: .08cqw; color: #7a6440; }
.stars { font-size: 2.6cqw; color: #f5a700; letter-spacing: .2cqw; }
.box { margin-left: auto; font: 600 1.5cqw system-ui, sans-serif; background: #566179; color: #fff; padding: .4cqw 1.2cqw; border-radius: 99px; }
.body { position: absolute; left: 2cqw; right: 2cqw; top: 7.4cqw; bottom: 9cqw; }
.say { position: absolute; left: 2cqw; right: 2cqw; bottom: 1cqw; height: 7.4cqw; display: flex; align-items: center;
  justify-content: center; gap: 1.4cqw; text-align: center; font-weight: 700; font-size: 2.6cqw; line-height: 1.15; }
.panel { position: absolute; border: .35cqw solid var(--ink); border-radius: .8cqw; background: #fff;
  box-shadow: .5cqw .5cqw 0 rgba(0,0,0,.18); }
.panel img.fill { width: 100%; height: 100%; object-fit: cover; border-radius: .45cqw; display: block; }
img.board, img.part { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain; }
img.a, .k-mission img.a0 { display: none; }
.revealed img.a { display: block; }
.revealed img.q { display: none; }
.col { position: absolute; left: 0; top: 0; bottom: 0; width: 25cqw; }
.col .pose { left: 0; bottom: 0; width: 25cqw; height: 25cqw; overflow: hidden; background: var(--paper); }
.col .pose img { width: 100%; height: 100%; object-fit: cover; }
.col .bubs { position: absolute; left: 0; right: 0; top: 0; bottom: 27cqw; display: flex; flex-direction: column;
  justify-content: flex-end; gap: 1cqw; }
.main { left: 27cqw; right: 0; top: 0; bottom: 0; overflow: hidden; }
.bub { position: relative; background: #fff; border: .3cqw solid var(--ink); border-radius: 2cqw; padding: .7cqw 1.2cqw .8cqw;
  font-size: 2cqw; font-weight: 700; line-height: 1.17; box-shadow: .3cqw .3cqw 0 rgba(0,0,0,.15); }
.bub .who { display: block; font-family: Bangers, Impact, sans-serif; font-weight: 400; font-size: 1.35cqw; letter-spacing: .08cqw; color: var(--who); }
.col .bub::after { content: ''; position: absolute; left: 4cqw; bottom: -1.5cqw; border-left: 1cqw solid transparent;
  border-right: .4cqw solid transparent; border-top: 1.5cqw solid var(--ink); }
.bub.post { border-color: #2e9e5b; background: #f0fff4; }
.beat { opacity: 0; scale: .6; transition: opacity .2s, scale .28s cubic-bezier(.3,1.7,.6,1); }
.beat.shown { opacity: 1; scale: 1; }
i.reveal { display: none; }
.cp1a { left: 4cqw; right: 4cqw; top: 3cqw; bottom: 1cqw; }
.k-comic img[src*="renders/real-"] { object-fit: contain; object-position: center center; background: #111; }
.cp2a { left: 0; width: 46.5cqw; top: 6cqw; height: 26.2cqw; }
.cp2b { right: 0; width: 46.5cqw; top: 17cqw; height: 26.2cqw; }
.panel .bub { position: absolute; max-width: 62%; }
.at-tl { top: -3.2cqw; left: 2%; } .at-tc { top: -3.2cqw; left: 25%; } .at-tr { top: -3.2cqw; right: 2%; }
.at-bl { bottom: -3.2cqw; left: 2%; } .at-bc { bottom: -3.2cqw; left: 25%; } .at-br { bottom: -3.2cqw; right: 2%; }
.panel .bub:not([class*=at-]) { top: -3.2cqw; left: 2%; }
.talk { position: absolute; inset: 0; display: grid; gap: 1.3cqw;
  grid-template-columns: repeat(var(--cols), minmax(0, 1fr)); }
.talk .panel { position: relative; overflow: hidden; border-width: .4cqw;
  border-top: .7cqw solid var(--who, var(--ink)); background: #1b2433; }
.talk .panel img.fill { object-fit: contain; object-position: center center; }
.talk .boxbubs { position: absolute; left: 3%; right: 3%; bottom: 3%; z-index: 1;
  display: flex; flex-direction: column; gap: .45cqw; }
.k-talk .body { bottom: 1.4cqw; }
.k-talk .say { display: none; }
.talk .panel .bub { position: relative; max-width: none; top: auto; left: auto; right: auto; bottom: auto;
  font-size: 1.7cqw; background: rgba(255,255,255,.96); }
.talk .cap { top: 3%; left: 4%; max-width: 90%; transform: none; z-index: 1; }
.talk.lay-hero { grid-template-columns: 1.45fr 1fr; grid-template-rows: 1.2fr 1fr .82fr;
  grid-template-areas: "a b" "a c" "d d"; }
.talk.lay-hero .panel:nth-child(1) { grid-area: a; }
.talk.lay-hero .panel:nth-child(2) { grid-area: b; }
.talk.lay-hero .panel:nth-child(3) { grid-area: c; }
.talk.lay-hero .panel:nth-child(4) { grid-area: d; }
.talk.lay-hero .panel:nth-child(1) .bub { font-size: 2.15cqw; }
.talk.lay-zigzag { grid-template-columns: 1.15fr .85fr 1.2fr; grid-template-rows: 1.15fr 1fr;
  grid-template-areas: "a a b" "c d d"; }
.talk.lay-zigzag .panel:nth-child(1) { grid-area: a; }
.talk.lay-zigzag .panel:nth-child(2) { grid-area: b; }
.talk.lay-zigzag .panel:nth-child(3) { grid-area: c; }
.talk.lay-zigzag .panel:nth-child(4) { grid-area: d; }
.talk.lay-zigzag .panel:nth-child(2),
.talk.lay-zigzag .panel:nth-child(3) { transform: rotate(-.7deg); }
.talk.lay-quad { grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr;
  grid-template-areas: "a b" "c d"; }
.talk.lay-quad .panel:nth-child(1) { grid-area: a; }
.talk.lay-quad .panel:nth-child(2) { grid-area: b; }
.talk.lay-quad .panel:nth-child(3) { grid-area: c; }
.talk.lay-quad .panel:nth-child(4) { grid-area: d; }
/* wide is a film strip: four panels in one row, the 1st and 3rd bigger.
   quad is the only 2x2. These used to be the same grid, which is why every
   talk page looked identical. */
.talk.lay-wide { grid-template-columns: 1.35fr .8fr 1.35fr .8fr; grid-template-rows: 1fr;
  grid-template-areas: "a b c d"; }
.talk.lay-wide .panel:nth-child(1) { grid-area: a; }
.talk.lay-wide .panel:nth-child(2) { grid-area: b; }
.talk.lay-wide .panel:nth-child(3) { grid-area: c; }
.talk.lay-wide .panel:nth-child(4) { grid-area: d; }
.talk.lay-strip { grid-template-rows: 1fr; }
.talk.lay-splash { display: block; }
.talk.lay-splash .panel { position: absolute; inset: 0; border-top-width: .4cqw; }
.talk.lay-splash .boxbubs { inset: 0; display: block; }
.talk.lay-splash .panel .bub { position: absolute; max-width: 34%; font-size: 1.85cqw; }
.talk.lay-splash .panel .bub.at-tl { top: 3%; left: 2%; right: auto; bottom: auto; }
.talk.lay-splash .panel .bub.at-tr { top: 3%; right: 2%; left: auto; bottom: auto; }
.talk.lay-splash .panel .bub.at-bl { bottom: 4%; left: 2%; top: auto; right: auto; }
.talk.lay-splash .panel .bub.at-br { bottom: 4%; right: 2%; top: auto; left: auto; }
.talk.lay-spread { grid-template-columns: 1fr; grid-template-rows: 1fr 1fr; }
.talk.lay-spread .boxbubs { flex-direction: row; align-items: flex-end; left: 2%; right: 2%; }
.talk.lay-spread .bub { flex: 1; font-size: 1.85cqw; }
.talk.lay-cinema { grid-template-columns: 1fr 1fr 1fr; grid-template-rows: 1.35fr .95fr;
  grid-template-areas: "a a a" "b c d"; }
.talk.lay-cinema .panel:nth-child(1) { grid-area: a; }
.talk.lay-cinema .panel:nth-child(2) { grid-area: b; }
.talk.lay-cinema .panel:nth-child(3) { grid-area: c; }
.talk.lay-cinema .panel:nth-child(4) { grid-area: d; }
.talk.lay-cinema .panel:nth-child(1) .bub { font-size: 2.2cqw; }
.talk.lay-stack { grid-template-columns: .85fr 1.25fr; grid-template-rows: 1fr 1fr .78fr;
  grid-template-areas: "a b" "a b" "c d"; }
.talk.lay-stack .panel:nth-child(1) { grid-area: a; }
.talk.lay-stack .panel:nth-child(2) { grid-area: b; }
.talk.lay-stack .panel:nth-child(3) { grid-area: c; }
.talk.lay-stack .panel:nth-child(4) { grid-area: d; }
.lay-hero .panel:nth-child(4) .bub,
.lay-zigzag .panel:nth-child(2) .bub,
.lay-zigzag .panel:nth-child(3) .bub,
.lay-cinema .panel:nth-child(n+2) .bub,
.lay-stack .panel:nth-child(n+3) .bub { font-size: 1.45cqw; }
.cap { position: absolute; top: -1.6cqw; left: -1.2cqw; max-width: 55%; background: #ffe680; border: .3cqw solid var(--ink);
  padding: .4cqw 1cqw; font-size: 1.7cqw; font-weight: 700; transform: rotate(-1.5deg); }
.panel.splash { left: 9cqw; right: 9cqw; top: 6cqw; bottom: 0; overflow: hidden; }
.splash-title { position: absolute; left: 1cqw; top: -1.6cqw; z-index: 2; background: #ffe14d; border: .45cqw solid var(--ink);
  padding: .5cqw 2cqw .7cqw; font-family: Bangers, Impact, sans-serif; font-size: 4.2cqw; letter-spacing: .15cqw;
  transform: rotate(-2deg); box-shadow: .6cqw .6cqw 0 rgba(0,0,0,.25); }
.splash-title small { display: inline; font-size: 1.8cqw; color: #b3261e; margin-right: 1.4cqw; vertical-align: middle; }
.k-splash .body > .bub { position: absolute; right: 4cqw; bottom: 3cqw; max-width: 40%; }
.k-cover .body { inset: 0; }
.k-cover .say { display: none; }
.k-cover img.fill { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;
  object-position: center bottom; border-radius: 0; }
.k-cover .body::after { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 62%;
  background: linear-gradient(to bottom, rgba(6, 14, 36, .72), rgba(6, 14, 36, 0)); pointer-events: none; }
.cover-title { position: absolute; z-index: 2; left: 3%; right: 3%; top: 4.5%; text-align: center;
  font-family: Bangers, Impact, sans-serif; font-weight: 400; color: #fff;
  text-shadow: .28cqw .28cqw 0 #1b1b1f; }
.cover-title small { display: block; font-size: 3.1cqw; letter-spacing: .32cqw; color: #ffe14d; }
.cover-title b { display: block; margin-top: .2cqw; font-size: 14cqw; font-weight: 400; line-height: .88;
  letter-spacing: .16cqw; -webkit-text-stroke: .38cqw #1b1b1f; paint-order: stroke fill; }
.cover-title span { display: block; margin-top: .8cqw; font-size: 4.6cqw; letter-spacing: .14cqw; color: #ffe14d;
  -webkit-text-stroke: .22cqw #1b1b1f; paint-order: stroke fill; }
.find { position: absolute; left: 1cqw; top: 1cqw; max-width: 36%; box-sizing: border-box; display: flex; gap: 1cqw;
  align-items: center; background: #fff8ec; border: .3cqw solid var(--ink); border-radius: 1cqw; padding: .8cqw 1.2cqw;
  font-size: 1.8cqw; line-height: 1.25; }
.find > .pid { flex: none; }
.find.swaps { flex-direction: column; align-items: flex-start; gap: .6cqw; }
.find .arrow { font-size: 2.6cqw; color: #ff7a1a; }
.find .where { margin-left: .6cqw; font-size: 1.8cqw; white-space: nowrap; }
.pid { display: inline-block; min-width: 4.4cqw; text-align: center; color: #fff; font: 800 2.2cqw system-ui, sans-serif;
  padding: .5cqw .9cqw; border-radius: .8cqw; border: .25cqw solid rgba(0,0,0,.35); vertical-align: middle; }
.verb { font-family: Bangers, Impact, sans-serif; font-size: 1.9cqw; letter-spacing: .08cqw; margin: 0 .6cqw; }
.verb.out { color: #c0392b; } .verb.in { color: #1d8a4a; }
.k-meet img.part { height: 62%; }
.meet { position: absolute; left: 0; right: 0; bottom: 1.5cqw; text-align: center; font-size: 2.2cqw; font-weight: 700; }
.meet .kid { font-family: Bangers, Impact, sans-serif; font-size: 4.6cqw; letter-spacing: .12cqw; font-weight: 400; }
.meet .real { font-size: 2.1cqw; margin-top: .5cqw; }
.meet .like { font-size: 1.7cqw; color: #566179; margin-top: .25cqw; }
.choice { display: inline-block; font-family: Bangers, Impact, sans-serif; font-size: 2.6cqw; letter-spacing: .1cqw; font-weight: 400;
  padding: .3cqw 1.8cqw; border: .3cqw solid var(--ink); border-radius: 99px; background: #fff; }
.revealed .choice.right { background: #2ecc71; color: #fff; scale: 1.08; }
.revealed .choice:not(.right) { opacity: .3; }
.choice.after, .after { visibility: hidden; }
.revealed .after { visibility: visible; }
.ask { font-size: 2.4cqw; }
.grid { position: absolute; left: 27cqw; right: 0; top: 0; bottom: 0; display: grid;
  grid-template-columns: repeat(var(--cols), 1fr); gap: 1.4cqw 1.6cqw; }
.mini { display: flex; flex-direction: column; gap: .6cqw; min-height: 0; }
.mini .panel { position: relative; flex: 1; min-height: 0; }
.grid.one-row { align-content: center; }
.grid.one-row .mini .panel { flex: none; aspect-ratio: .86; }
.k-puzzle .col { width: 18cqw; }
.k-puzzle .col .pose { width: 18cqw; height: 18cqw; }
.k-puzzle .col .bubs { bottom: 19cqw; }
.k-puzzle .grid { left: 19cqw; }
.k-puzzle .grid.one-row { align-content: stretch; grid-template-rows: 1fr; }
.k-puzzle .grid.one-row .mini { height: 100%; }
.k-puzzle .grid.one-row .mini .panel { flex: 1 1 auto; aspect-ratio: auto; min-height: 0; }
.mini .chips { display: flex; gap: .6cqw; justify-content: center; }
.mini .choice { font-size: 1.7cqw; padding: .15cqw 1cqw; }
.letter { position: absolute; left: -1cqw; top: -1cqw; z-index: 2; width: 3.6cqw; height: 3.6cqw; border-radius: 50%;
  background: #ff7a1a; color: #fff; border: .3cqw solid var(--ink); font: 400 2.2cqw Bangers, Impact, sans-serif;
  display: flex; align-items: center; justify-content: center; }
.note { background: repeating-linear-gradient(#fffef6 0 3.2cqw, #c9dcf5 3.2cqw calc(3.2cqw + 2px));
  padding: 2cqw 2.4cqw 2cqw 5cqw; overflow: hidden; }
.note::before { content: ''; position: absolute; left: 3.4cqw; top: 0; bottom: 0; width: 2px; background: #e57373; }
.note .qtext { font-size: 2.8cqw; font-weight: 700; margin-bottom: 1cqw; }
.note img.nb { display: block; max-width: 70%; max-height: 22cqw; margin: .6cqw 0; }
.note .ans { margin-top: 1cqw; font-size: 2.4cqw; background: #e9fbe9; border: .3cqw solid #2e9e5b; border-radius: 1cqw;
  padding: .8cqw 1.4cqw; display: inline-block; }
.note .ans b { font-size: 3.2cqw; color: #1d6b3f; }
.note table { border-collapse: collapse; font-size: 1.9cqw; margin: .6cqw 0; background: #fff; }
.note th, .note td { border: .2cqw solid var(--ink); padding: .35cqw 1cqw; text-align: center; }
.note th { background: #ffe680; }
.note ol { font-size: 2.8cqw; font-weight: 700; line-height: 1.6; margin: 0; padding-left: 3cqw; }
.note li.new { background: linear-gradient(transparent 55%, #ffe14d 55%); }
.card { position: absolute; left: 3%; right: 3%; top: 3%; padding: 1.4cqw 2cqw; background: #fff; border: .3cqw solid var(--ink);
  border-top: 1.4cqw solid #d62828; font-size: 2.8cqw; font-weight: 700; transform: rotate(-.6deg); z-index: 2; }
.cardtitle { font-family: Bangers, Impact, sans-serif; font-weight: 400; font-size: 2cqw; color: #d62828; letter-spacing: .1cqw; }
.mboard { position: absolute; left: 0; right: 0; bottom: 0; top: 30%; }
.panel.crew { left: 0; width: 56cqw; top: 2cqw; height: 31.5cqw; overflow: hidden; }
.medal { position: absolute; right: 3cqw; top: 1cqw; width: 34cqw; height: 34cqw; border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #fff3a6, #f5b700 70%); border: .7cqw solid var(--ink);
  display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;
  font-family: Bangers, Impact, sans-serif; box-shadow: 0 0 0 1.2cqw #d62828, .8cqw .8cqw 0 1.2cqw rgba(0,0,0,.2); }
.medal small { font-size: 1.8cqw; letter-spacing: .1cqw; } .medal b { font-size: 6cqw; font-weight: 400; }
.medal span { font-size: 4cqw; color: #d62828; } .medal i { font-style: normal; font-size: 2.6cqw; max-width: 80%; }
.k-badge .body > .bub { position: absolute; left: 3cqw; bottom: 1cqw; max-width: 52%; }
.k-badge .body > .bub + .bub { left: auto; right: 3cqw; max-width: 40%; }
.dad { display: none; width: var(--sw); margin: 6px auto 0; background: #151821; color: #e9edf5; border-radius: 10px;
  padding: 10px 14px; gap: 6px 18px; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  font: 14px/1.38 system-ui, sans-serif; max-height: var(--dadh); overflow: auto; }
.dad b { display: block; color: #ffcf6e; font-size: 11px; letter-spacing: .06em; text-transform: uppercase; }
body.dad-on .slide.on .dad { display: grid; }
@media print {
  :root { --sw: 10in; }
  @page { size: 11in 8.5in; margin: .25in .5in; }
  body { background: #fff; }
  nav { display: none; }
  .slide { display: block !important; page-break-after: always; }
  .beat { opacity: 1 !important; scale: 1 !important; }
  .dad { display: grid !important; max-height: none; background: #fff; color: #000; border: 1px solid #999; }
  .dad b { color: #555; }
}
"""

JS = """
const slides = [...document.querySelectorAll('.slide')];
const KEY = 'spark-deck:' + document.body.dataset.build;
let i = 0, beat = 0;
const beatsOf = s => [...s.querySelectorAll('.beat')].sort((a, b) => a.dataset.b - b.dataset.b);
function fit() {
  const navH = document.querySelector('nav').offsetHeight;
  const dadH = document.body.classList.contains('dad-on') ? Math.min(190, innerHeight * 0.22) : 0;
  document.documentElement.style.setProperty('--dadh', dadH + 'px');
  const sw = Math.min(innerWidth - 16, (innerHeight - navH - dadH - 22) * 1.5);
  document.documentElement.style.setProperty('--sw', Math.max(320, sw) + 'px');
}
function show(n, all) {
  i = Math.max(0, Math.min(slides.length - 1, n));
  slides.forEach((s, k) => s.classList.toggle('on', k === i));
  const s = slides[i], bs = beatsOf(s);
  beat = all ? bs.length : 0;
  bs.forEach((b, k) => b.classList.toggle('shown', k < beat));
  s.classList.toggle('revealed', !!all && !!s.querySelector('.reveal'));
  document.getElementById('where').textContent = (i + 1) + ' / ' + slides.length;
  document.querySelectorAll('nav [data-ch]').forEach(b => b.classList.toggle('cur', b.dataset.ch === s.dataset.ch));
  try { localStorage.setItem(KEY, i); } catch (e) {}
  history.replaceState(null, '', '#s=' + (i + 1));
}
function next() {
  const s = slides[i], bs = beatsOf(s);
  if (beat < bs.length) {
    const b = bs[beat++];
    b.classList.add('shown');
    if (b.classList.contains('reveal')) s.classList.add('revealed');
  } else if (i < slides.length - 1) show(i + 1, false);
}
function back() { show(i - 1, true); }
function chapter(c) { const k = slides.findIndex(s => s.dataset.ch === String(c)); if (k >= 0) show(k, false); }
document.getElementById('next').onclick = next;
document.getElementById('back').onclick = back;
document.getElementById('dad').onclick = () => { document.body.classList.toggle('dad-on'); fit(); };
document.querySelectorAll('nav [data-ch]').forEach(b => b.onclick = () => chapter(b.dataset.ch));
document.querySelectorAll('.stage').forEach(s => s.onclick = next);
addEventListener('keydown', e => {
  if (['ArrowRight', ' ', 'Enter', 'PageDown'].includes(e.key)) { e.preventDefault(); next(); }
  else if (['ArrowLeft', 'PageUp'].includes(e.key)) back();
  else if (e.key === 'g' || e.key === 'G') { document.body.classList.toggle('dad-on'); fit(); }
  else if (/^[1-9]$/.test(e.key)) chapter(e.key);
});
addEventListener('resize', fit);
fit();
const m = location.hash.match(/s=(\\d+)/);
let start = m ? +m[1] - 1 : 0;
if (!m) { try { start = +(localStorage.getItem(KEY) || 0); } catch (e) {} }
show(start, /all/.test(location.hash));
"""


def preview_build(bdir: Path, circ: Circuit, deck: Deck, steps: dict) -> int:
    ctx: dict = {"rules": []}
    sections = []
    for s in deck.slides:
        if s.f.get("rule"):
            ctx["rules"].append(s.f["rule"])
        sections.append(slide_html(bdir, circ, deck, s, steps, ctx))
    chapters = "".join(f'<button data-ch="{c.n}" title="{esc(c.title)}">Case {c.n}</button>' for c in deck.chapters)
    title = esc(deck.title or bdir.name)
    doc = (
        "<!doctype html>\n<meta charset=\"utf-8\">\n"
        f"<title>{title}</title>\n"
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link href="https://fonts.googleapis.com/css2?family=Bangers&family=Comic+Neue:wght@400;700&display=swap" rel="stylesheet">\n'
        f"<style>{CSS}</style>\n"
        f'<body class="dad-on" data-build="{esc(bdir.name)}">\n'
        f'<nav><button id="back">&#9664; Back</button>{chapters}<span id="where"></span>'
        f'<button id="dad" title="Grown-up notes (G)">Grown-up</button><button id="next" class="go">Next &#9654;</button></nav>\n'
        + "\n".join(sections)
        + f"\n<script>{JS}</script>\n</body>\n"
    )
    (bdir / "preview.html").write_text(doc)
    print(f"wrote {bdir / 'preview.html'} ({len(deck.slides)} pages in {len(deck.chapters)} chapters)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
