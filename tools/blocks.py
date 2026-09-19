#!/usr/bin/env python3
"""Word-Block and Icon-Block programs: check, render, preview.

Same CLI shape as pages.py. The index in tools/spike/blocks.json is the
source of truth for shape, ports, extensions, and wording. Icon Blocks
are the `horizontal*` opcodes; `canvas: icon` in the header selects them.

    python3 tools/blocks.py check builds/mining-drill-truck
    python3 tools/blocks.py render builds/mining-drill-truck
    python3 tools/blocks.py preview builds/mining-drill-truck
    python3 tools/blocks.py fixtures
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX_PATH = REPO / "tools" / "spike" / "blocks.json"
FIXTURES = REPO / "tools" / "spike" / "fixtures"

BOOLEAN_SHAPES = {"boolean"}
REPORTER_SHAPES = {"reporter"}
HAT_SHAPES = {"hat"}
STATEMENT_SHAPES = {"stack", "c", "cap"}
C_SHAPES = {"c"}

MOVE_PREFIX = "flippermove_"
PAIR_SETTER = "flippermove_setMovementPair"

HEADER = re.compile(r"^(hub|extensions|canvas)\s*:?\s*(.*)$", re.I)
ARG = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=(.*)")

ICON_PAD_COLORS = {
    "red": "#E31B23",
    "blue": "#0A73DA",
    "yellow": "#F5C400",
    "green": "#00852B",
    "orange": "#F57C00",
    "white": "#F4F4F4",
    "black": "#222222",
    "pink": "#E91E8C",
    "violet": "#7B1FA2",
    "azure": "#00A3E0",
    "cyan": "#00A3E0",
    "purple": "#7B1FA2",
}


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------


def load_index() -> dict:
    if not INDEX_PATH.is_file():
        sys.exit(f"missing {INDEX_PATH} — run python3 tools/spike_extract.py")
    return json.loads(INDEX_PATH.read_text())


def block_info(index: dict, opcode: str) -> dict | None:
    hit = index.get("blocks", {}).get(opcode)
    if hit:
        return hit
    for block in index.get("icon_blocks") or []:
        if block.get("opcode") == opcode:
            return block
    return None


def _is_icon_opcode(opcode: str) -> bool:
    return opcode.startswith("horizontal")


def ports_for_hub(index: dict, hub: str) -> set[str]:
    spec = index.get("hubs", {}).get(hub, {})
    return set(spec.get("ports", []))


# ---------------------------------------------------------------------------
# program.spike parser
# ---------------------------------------------------------------------------


@dataclass
class Node:
    opcode: str
    args: dict[str, str] = field(default_factory=dict)
    condition: Node | None = None
    then: list[Node] = field(default_factory=list)
    orelse: list[Node] = field(default_factory=list)
    line: int = 0

    @property
    def body(self) -> list[Node]:
        return self.then


@dataclass
class Program:
    hub: str
    extensions: list[str]
    stacks: list[Node]
    path: Path | None = None
    canvas: str = "word"

    @property
    def is_icon(self) -> bool:
        if self.canvas == "icon":
            return True
        return any(_is_icon_opcode(n.opcode) for s in self.stacks for n in walk(s))


def _split_opcode_args(rest: str) -> tuple[str, dict[str, str]]:
    rest = rest.strip()
    if not rest:
        return "", {}
    parts = rest.split()
    opcode = parts[0]
    args: dict[str, str] = {}
    for tok in parts[1:]:
        m = ARG.match(tok)
        if not m:
            sys.exit(f"bad argument token {tok!r} (want NAME=value)")
        args[m.group(1)] = m.group(2)
    return opcode, args


def parse_program(path: Path) -> Program:
    if not path.is_file():
        sys.exit(f"missing {path}")
    lines = path.read_text().splitlines()
    hub = "prime"
    extensions: list[str] = []
    canvas = "word"
    raw: list[tuple[int, int, str]] = []  # indent, lineno, text
    body_started = False
    for n, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        hm = HEADER.match(line.strip())
        if hm and not body_started:
            key = hm.group(1).lower()
            val = hm.group(2).strip()
            if key == "hub":
                hub = val.lower().replace(":", "").strip()
            elif key == "extensions":
                extensions = [x.strip() for x in val.replace(",", " ").split() if x.strip()]
            elif key == "canvas":
                canvas = val.lower().replace(":", "").strip()
                if canvas in {"iconblocks", "icon_blocks", "doodle", "horizontal"}:
                    canvas = "icon"
                elif canvas in {"wordblocks", "word_blocks"}:
                    canvas = "word"
            continue
        body_started = True
        indent = len(line) - len(line.lstrip(" "))
        raw.append((indent, n, line.strip()))

    def parse_block_list(i: int, parent_indent: int) -> tuple[list[Node], int]:
        nodes: list[Node] = []
        while i < len(raw):
            indent, lineno, text = raw[i]
            if indent < parent_indent:
                break
            if indent > parent_indent and nodes:
                # unexpected extra indent without a C-block opener
                break
            if indent != parent_indent:
                break
            if text.startswith("@") and not text.startswith("@condition "):
                break
            node, i = parse_one(i, indent)
            nodes.append(node)
        return nodes, i

    def parse_one(i: int, indent: int) -> tuple[Node, int]:
        _, lineno, text = raw[i]
        i += 1
        if text.startswith("@condition "):
            text = text[len("@condition ") :]
        opcode, args = _split_opcode_args(text)
        node = Node(opcode=opcode, args=args, line=lineno)
        if i >= len(raw):
            return node, i
        next_indent = raw[i][0]
        if next_indent <= indent:
            return node, i
        # children
        while i < len(raw) and raw[i][0] > indent:
            child_indent, child_line, child_text = raw[i]
            if child_text == "@condition" or child_text.startswith("@condition "):
                if child_text == "@condition":
                    i += 1
                    if i >= len(raw) or raw[i][0] <= indent:
                        break
                    cond, i = parse_one(i, raw[i][0])
                    node.condition = cond
                else:
                    cond, i = parse_one(i, child_indent)
                    node.condition = cond
                continue
            if child_text == "@then":
                i += 1
                then_nodes, i = parse_block_list(i, child_indent + 2) if i < len(raw) else ([], i)
                # children of @then are indented further; accept same extra indent
                if not then_nodes and i < len(raw) and raw[i][0] > child_indent:
                    then_nodes, i = parse_block_list(i, raw[i][0])
                node.then = then_nodes
                continue
            if child_text == "@else":
                i += 1
                else_nodes: list[Node] = []
                if i < len(raw) and raw[i][0] > child_indent:
                    else_nodes, i = parse_block_list(i, raw[i][0])
                node.orelse = else_nodes
                continue
            if child_text == "@body":
                i += 1
                body, i = parse_block_list(i, child_indent + 2) if i < len(raw) else ([], i)
                if not body and i < len(raw) and raw[i][0] > child_indent:
                    body, i = parse_block_list(i, raw[i][0])
                node.then = body
                continue
            child, i = parse_one(i, child_indent)
            node.then.append(child)
        return node, i

    stacks: list[Node] = []
    i = 0
    if raw:
        base = raw[0][0]
        while i < len(raw):
            node, i = parse_one(i, base)
            stacks.append(node)
    if canvas == "word" and any(_is_icon_opcode(s.opcode) for s in stacks):
        canvas = "icon"
    return Program(
        hub=hub, extensions=extensions, stacks=stacks, path=path, canvas=canvas
    )


# ---------------------------------------------------------------------------
# Check
# ---------------------------------------------------------------------------


@dataclass
class Problem:
    code: str
    line: int
    message: str

    def __str__(self) -> str:
        loc = f"line {self.line}" if self.line else "program"
        return f"{self.code}: {loc}: {self.message}"


def walk(node: Node):
    yield node
    if node.condition:
        yield from walk(node.condition)
    for ch in node.then:
        yield from walk(ch)
    for ch in node.orelse:
        yield from walk(ch)


def _port_values(node: Node) -> list[str]:
    ports = []
    for key in ("PORT", "PAIR", "LEFT", "RIGHT"):
        if key in node.args:
            ports.append(node.args[key])
    return ports


def _letters(token: str) -> list[str]:
    return [c for c in token.upper() if c in "ABCDEF"]


def check_program(prog: Program, index: dict) -> list[Problem]:
    problems: list[Problem] = []
    hub = prog.hub
    if hub not in index.get("hubs", {}):
        problems.append(Problem("HUB", 0, f"unknown hub {hub!r} (prime or essential)"))
        hub = "prime"
    allowed_ports = ports_for_hub(index, hub)
    listed_ext = set(prog.extensions)

    def fail(code: str, node: Node, msg: str) -> None:
        problems.append(Problem(code, node.line, msg))

    def check_node(node: Node, *, in_condition: bool, after_hat: bool, pair_on: bool) -> bool:
        info = block_info(index, node.opcode)
        if info is None:
            fail("UNKNOWN", node, f"opcode {node.opcode} is not in the index")
            return pair_on
        shape = info.get("shape")
        if node.opcode == PAIR_SETTER:
            pair_on = True
        if (
            node.opcode.startswith(MOVE_PREFIX)
            and node.opcode != PAIR_SETTER
            and not pair_on
        ):
            fail(
                "MOVEMENT_PAIR",
                node,
                f"{node.opcode} acts on the pair from {PAIR_SETTER}, which has not run yet",
            )
        ext = info.get("extension")
        if ext and ext not in listed_ext:
            fail(
                "EXTENSION",
                node,
                f"{node.opcode} is behind the {ext} extension, which this program did not add",
            )
        hubs = info.get("hubs") or ["prime", "essential"]
        if hub not in hubs:
            fail("HUB_BLOCK", node, f"{node.opcode} is not available on the {hub} hub")
        if shape in BOOLEAN_SHAPES and not in_condition:
            fail(
                "BOOLEAN_AS_STATEMENT",
                node,
                f"{node.opcode} is a hexagon — it reports true/false and does not run as a line. "
                "Drop it inside wait-until or if.",
            )
        if shape in REPORTER_SHAPES and not in_condition:
            fail(
                "REPORTER_AS_STATEMENT",
                node,
                f"{node.opcode} is an oval — it reports a value. Drop it into a slot.",
            )
        if shape in HAT_SHAPES and after_hat:
            fail("HAT_NESTED", node, f"{node.opcode} is a hat and cannot snap under another block")
        if shape in STATEMENT_SHAPES and not after_hat and not in_condition:
            fail(
                "STATEMENT_WITHOUT_HAT",
                node,
                f"{node.opcode} needs a hat (when program starts, when distance, …) above it",
            )
        for token in _port_values(node):
            for letter in _letters(token):
                if letter not in allowed_ports:
                    fail(
                        "PORT",
                        node,
                        f"port {letter} is not on the {hub} hub "
                        f"(ports {', '.join(sorted(allowed_ports))})",
                    )
        if node.condition:
            check_node(node.condition, in_condition=True, after_hat=True, pair_on=pair_on)
        child_after = after_hat or shape in HAT_SHAPES
        child_pair = pair_on
        for ch in node.then:
            child_pair = check_node(ch, in_condition=False, after_hat=child_after, pair_on=child_pair)
        for ch in node.orelse:
            check_node(ch, in_condition=False, after_hat=child_after, pair_on=pair_on)
        return pair_on

    for stack in prog.stacks:
        info = block_info(index, stack.opcode)
        if info and info.get("shape") not in HAT_SHAPES:
            fail(
                "STACK_ROOT",
                stack,
                f"stack starts with {stack.opcode}, which is not a hat",
            )
        check_node(stack, in_condition=False, after_hat=False, pair_on=False)
    return problems


# ---------------------------------------------------------------------------
# SVG render
# ---------------------------------------------------------------------------

NOTCH_X = 16
NOTCH_W = 12
NOTCH_H = 4
ROW_H = 40
PAD_X = 10
CHAR_W = 7.4


def _cat_colors(index: dict, category: str) -> dict[str, str]:
    for c in index.get("categories", []):
        if c["id"] == category:
            return c["colors"]
    return {"primary": "#4C97FF", "secondary": "#3373CC", "tertiary": "#2b5aa8"}


def _format_message(info: dict, args: dict[str, str], menus: dict) -> str:
    msg = info.get("message") or info.get("short") or info.get("label") or info["opcode"]
    merged = {}
    for a in info.get("arguments") or []:
        if "default" in a and a["default"] is not None:
            merged[a["name"]] = str(a["default"])
    merged.update(args)
    if "IMAGE" in merged and "MATRIX" not in merged:
        merged["MATRIX"] = merged["IMAGE"]
    if "PAIR" in merged and re.fullmatch(r"[A-Fa-f]+", merged["PAIR"]):
        merged["PAIR"] = "+".join(merged["PAIR"].upper())
    for name, val in merged.items():
        pretty = val
        for menu in (info.get("arguments") or []):
            if menu.get("name") == name and menu.get("menu") in menus:
                pretty = menus[menu["menu"]].get(val, val)
                break
        msg = msg.replace(f"[{name}]", str(pretty))
        msg = msg.replace(f"({name})", str(pretty))
        msg = msg.replace(f"<{name}>", str(pretty))
    msg = re.sub(r"\[([A-Z_]+)\]", r"\1", msg)
    return msg


def _condition_split(label: str) -> tuple[str, str]:
    """Text either side of a boolean slot: "if <CONDITION> then / else" -> ("if", "then").

    The hexagon is a separate shape, so the words have to be drawn around
    it. Printing the raw label instead leaves a literal "<CONDITION>" on
    the block and buries it under the hexagon.
    """
    head, sep, tail = label.partition("<CONDITION>")
    if not sep:
        return label.split("/")[0].strip(), ""
    return head.strip(), tail.split("/")[0].strip()


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _stack_path(w: float, h: float, hat: bool, cap: bool) -> str:
    """Scratch-like puzzle outline. y=0 is the top of the body (below hat bump)."""
    nx, nw, nh = NOTCH_X, NOTCH_W, NOTCH_H
    r = 8
    if hat:
        # bump then body with bottom notch (unless cap)
        top = (
            f"M {r} {-18} "
            f"C {w*0.15} {-28}, {w*0.35} {-28}, {w*0.45} {-18} "
            f"L {w-r} {-18} Q {w} {-18} {w} {-18+r} "
        )
        start_y = -18
    else:
        top = (
            f"M 0 {r} Q 0 0 {r} 0 L {nx} 0 "
            f"L {nx} {nh} L {nx+nw} {nh} L {nx+nw} 0 "
            f"L {w-r} 0 Q {w} 0 {w} {r} "
        )
        start_y = 0
    if cap:
        bot = f"L {w} {h-r} Q {w} {h} {w-r} {h} L {r} {h} Q 0 {h} 0 {h-r} Z"
    else:
        bot = (
            f"L {w} {h-r} Q {w} {h} {w-r} {h} "
            f"L {nx+nw} {h} L {nx+nw} {h+nh} L {nx} {h+nh} L {nx} {h} "
            f"L {r} {h} Q 0 {h} 0 {h-r} Z"
        )
    if hat:
        return (
            f"M {r} {-18} "
            f"C {min(80, w*0.25)} {-32}, {min(140, w*0.5)} {-32}, {min(160, w*0.55)} {-18} "
            f"L {w-r} {-18} Q {w} {-18} {w} {-10} "
            + bot.replace("Z", f"L 0 {-10+r} Q 0 {-18} {r} {-18} Z")
        )
    return top + bot


def _hexagon_path(w: float, h: float) -> str:
    tip = 12
    return f"M {tip} 0 L {w-tip} 0 L {w} {h/2} L {w-tip} {h} L {tip} {h} L 0 {h/2} Z"


def _pill_path(w: float, h: float) -> str:
    r = h / 2
    return (
        f"M {r} 0 L {w-r} 0 Q {w} 0 {w} {r} "
        f"L {w} {h-r} Q {w} {h} {w-r} {h} L {r} {h} Q 0 {h} 0 {h-r} "
        f"L 0 {r} Q 0 0 {r} 0 Z"
    )


@dataclass
class Drawn:
    svg: str
    width: float
    height: float


def draw_node(node: Node, index: dict, x: float, y: float) -> Drawn:
    info = block_info(index, node.opcode) or {
        "opcode": node.opcode,
        "shape": "stack",
        "category": "extension",
        "message": node.opcode,
        "arguments": [],
    }
    shape = info.get("shape", "stack")
    colors = _cat_colors(index, info.get("category", "extension"))
    menus = index.get("menus", {})
    label = _format_message(info, node.args, menus)
    head, tail = _condition_split(label)
    text_w = max(80, PAD_X * 2 + len(label) * CHAR_W)
    inner = []
    inner_h = 0.0
    inner_w = 0.0
    cond_drawn: Drawn | None = None
    if node.condition:
        cond_drawn = draw_node(node.condition, index, 0, 0)
        inner.append(("cond", cond_drawn))
        text_w = max(
            text_w,
            PAD_X * 2 + (len(head) + len(tail)) * CHAR_W + cond_drawn.width + 24,
        )
    if shape in C_SHAPES or node.then or node.orelse:
        for ch in node.then:
            d = draw_node(ch, index, 0, 0)
            inner.append(("then", d))
            inner_h += d.height - NOTCH_H
            inner_w = max(inner_w, d.width)
        else_h = 0.0
        for ch in node.orelse:
            d = draw_node(ch, index, 0, 0)
            inner.append(("else", d))
            else_h += d.height - NOTCH_H
            inner_w = max(inner_w, d.width)
        text_w = max(text_w, inner_w + 24)
        header_h = ROW_H
        mouth = max(24, inner_h + 8)
        else_bar = ROW_H if node.orelse else 0
        else_mouth = max(24, else_h + 8) if node.orelse else 0
        w = text_w + 8
        hat_off = 18 if shape in HAT_SHAPES else 0
        path = _c_path(w, header_h, mouth, else_bar, else_mouth, hat=shape in HAT_SHAPES)
        # "if <> then / else" is one message; the else half is drawn on its
        # own bar further down, so only the first half goes in the header.
        head_x = x + PAD_X + 4
        parts = [
            f'<path d="{path}" fill="{colors["primary"]}" stroke="{colors["tertiary"]}" '
            f'stroke-width="1" transform="translate({x},{y+hat_off})"/>',
            f'<text x="{head_x}" y="{y+hat_off+24}" font-family="Arial, Helvetica, sans-serif" '
            f'font-size="13" font-weight="bold" fill="#fff">{_esc(head)}</text>',
        ]
        ix = x + 16
        cursor = y + hat_off + header_h - NOTCH_H
        for kind, d in inner:
            if kind == "cond":
                cx = head_x + len(head) * CHAR_W + 8
                parts.append(_shift_svg(d.svg, cx, y + hat_off + 4))
                if tail:
                    parts.append(
                        f'<text x="{cx+d.width+8}" y="{y+hat_off+24}" '
                        f'font-family="Arial, Helvetica, sans-serif" font-size="13" '
                        f'font-weight="bold" fill="#fff">{_esc(tail)}</text>'
                    )
            elif kind == "then":
                parts.append(_shift_svg(d.svg, ix, cursor))
                cursor += d.height - NOTCH_H
        if node.orelse:
            else_y = y + hat_off + header_h + mouth
            parts.append(
                f'<text x="{x+PAD_X+4}" y="{else_y+24}" font-family="Arial, Helvetica, sans-serif" '
                f'font-size="13" font-weight="bold" fill="#fff">else</text>'
            )
            cursor = else_y + ROW_H - NOTCH_H
            for kind, d in inner:
                if kind == "else":
                    parts.append(_shift_svg(d.svg, ix, cursor))
                    cursor += d.height - NOTCH_H
        total_h = header_h + mouth + else_bar + else_mouth + 16 + hat_off
        return Drawn("\n".join(parts), w + 4, total_h)

    hat_off = 18 if shape in HAT_SHAPES else 0
    w = text_w + (24 if shape in BOOLEAN_SHAPES else 8)
    w = round(w, 1)
    h = 32 if shape in BOOLEAN_SHAPES | REPORTER_SHAPES else ROW_H
    fill = colors["primary"]
    stroke = colors["tertiary"]
    # "wait until <>" is a plain stack block that still carries a hexagon.
    # Drawing only the label would delete the test from the picture.
    text = head if cond_drawn is not None else label
    if shape in BOOLEAN_SHAPES:
        path = _hexagon_path(w, h)
        ty = y + h * 0.68
        tx = x + 14
    elif shape in REPORTER_SHAPES:
        path = _pill_path(w, h)
        ty = y + h * 0.68
        tx = x + 12
    else:
        path = _stack_path(w, h, hat=shape in HAT_SHAPES, cap=shape == "cap")
        ty = y + hat_off + 24
        tx = x + PAD_X
    svg = (
        f'<path d="{path}" fill="{fill}" stroke="{stroke}" stroke-width="1" '
        f'transform="translate({x},{y+hat_off})"/>\n'
        f'<text x="{tx}" y="{ty}" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="13" font-weight="bold" fill="#fff">{_esc(text)}</text>'
    )
    if cond_drawn is not None:
        cx = tx + len(head) * CHAR_W + 8
        svg += "\n" + _shift_svg(cond_drawn.svg, cx, y + hat_off + 4)
        if tail:
            svg += (
                f'\n<text x="{cx+cond_drawn.width+8}" y="{ty}" '
                f'font-family="Arial, Helvetica, sans-serif" font-size="13" '
                f'font-weight="bold" fill="#fff">{_esc(tail)}</text>'
            )
    return Drawn(svg, w + 2, h + hat_off + (NOTCH_H if shape not in BOOLEAN_SHAPES | REPORTER_SHAPES | {"cap"} else 0))


def _c_path(w: float, header: float, mouth: float, else_bar: float, else_mouth: float, hat: bool) -> str:
    nx, nw, nh = NOTCH_X, NOTCH_W, NOTCH_H
    rail = 12
    inner = 16
    y = 0
    parts = [f"M 0 8 Q 0 0 8 0"]
    if hat:
        parts = [
            f"M 8 -18 C 40 -32, 90 -32, 130 -18 L {w-8} -18 Q {w} -18 {w} -10"
        ]
        y = -18
    else:
        parts.append(f"L {nx} 0 L {nx} {nh} L {nx+nw} {nh} L {nx+nw} 0")
        parts.append(f"L {w-8} 0 Q {w} 0 {w} 8")
    # down right of header
    parts.append(f"L {w} {header}")
    # into mouth
    parts.append(f"L {inner+nw} {header} L {inner+nw} {header+nh} L {inner} {header+nh} L {inner} {header}")
    parts.append(f"L {rail} {header} L {rail} {header+mouth}")
    yb = header + mouth
    if else_bar:
        parts.append(f"L {inner} {yb} L {inner} {yb+nh} L {inner+nw} {yb+nh} L {inner+nw} {yb}")
        parts.append(f"L {w-8} {yb} Q {w} {yb} {w} {yb+8} L {w} {yb+else_bar}")
        yb2 = yb + else_bar
        parts.append(f"L {inner+nw} {yb2} L {inner+nw} {yb2+nh} L {inner} {yb2+nh} L {inner} {yb2}")
        parts.append(f"L {rail} {yb2} L {rail} {yb2+else_mouth}")
        yb = yb2 + else_mouth
    # footer with bottom notch
    parts.append(f"L {inner} {yb} L {inner} {yb+nh} L {inner+nw} {yb+nh} L {inner+nw} {yb}")
    parts.append(f"L {w-8} {yb} Q {w} {yb} {w} {yb+8} L {w} {yb+16-8} Q {w} {yb+16} {w-8} {yb+16}")
    parts.append(f"L {nx+nw} {yb+16} L {nx+nw} {yb+16+nh} L {nx} {yb+16+nh} L {nx} {yb+16}")
    parts.append(f"L 8 {yb+16} Q 0 {yb+16} 0 {yb+8} L 0 8 Z")
    return " ".join(parts)


def _shift_svg(svg: str, dx: float, dy: float) -> str:
    if dx == 0 and dy == 0:
        return svg
    return f'<g transform="translate({dx},{dy})">\n{svg}\n</g>'


# ---------------------------------------------------------------------------
# Icon Blocks (horizontal pictorial tiles, not Scratch notches)
# ---------------------------------------------------------------------------

ICON_TILE = 120
ICON_GAP = 26
ICON_ROW = 44
ICON_LEFT = 108
ICON_TOP = 20
ICON_RADIUS = 22


def _node_color_name(node: Node) -> str:
    for key in ("COLOR", "MATRIX", "VALUE", "IMAGE"):
        if key in node.args:
            return node.args[key].lower()
    return ""


def _color_hex(name: str) -> str:
    if not name:
        return "#C8C8C8"
    return ICON_PAD_COLORS.get(name.lower(), "#888888")


def _chip_stroke(fill: str) -> str:
    return "#333333" if fill.lower() in {"#f5c400", "#f4f4f4", "#ffffff"} else "#ffffff"


def _flatten_icon(node: Node) -> list[Node]:
    tiles = [node]
    for ch in node.then:
        tiles.extend(_flatten_icon(ch))
    for ch in node.orelse:
        tiles.extend(_flatten_icon(ch))
    return tiles


@dataclass
class IconCell:
    x: float
    y: float
    opcode: str
    fill: str
    stroke: str
    accent: str
    port: str
    kind: str
    label: str


@dataclass
class IconPlan:
    cells: list[IconCell]
    connectors: list[tuple[float, float]]
    captions: list[tuple[float, float, str, str]]
    width: float
    height: float


def _icon_kind(opcode: str) -> str:
    if opcode == "horizontalevents_whenColor":
        return "whenColor"
    if opcode == "horizontaldisplay_ledMatrix":
        return "ledMatrix"
    if opcode == "horizontalevents_whenProgramStarts":
        return "whenStart"
    return "generic"


def _plan_icon(prog: Program, index: dict) -> IconPlan:
    cells: list[IconCell] = []
    connectors: list[tuple[float, float]] = []
    captions: list[tuple[float, float, str, str]] = []
    y = ICON_TOP
    max_x = ICON_LEFT
    for stack in prog.stacks:
        color_name = _node_color_name(stack)
        caption = color_name or "stack"
        ink = _color_hex(color_name) if color_name else "#444444"
        if caption == "yellow":
            ink = "#C9A000"
        captions.append((12, y + ICON_TILE / 2, caption, ink))
        x = ICON_LEFT
        tiles = _flatten_icon(stack)
        for i, node in enumerate(tiles):
            info = block_info(index, node.opcode) or {}
            colors = _cat_colors(index, info.get("category", "event"))
            kind = _icon_kind(node.opcode)
            accent_name = _node_color_name(node) or color_name
            default_port = "A" if kind in {"whenColor", "whenStart"} else "B"
            port = node.args.get("PORT", default_port)
            label = info.get("label") or node.opcode.split("_", 1)[-1]
            cells.append(
                IconCell(
                    x=x,
                    y=y,
                    opcode=node.opcode,
                    fill=colors["primary"],
                    stroke=colors["tertiary"],
                    accent=_color_hex(accent_name),
                    port=port,
                    kind=kind,
                    label=label,
                )
            )
            if i:
                connectors.append((x - ICON_GAP / 2, y + ICON_TILE / 2))
            x += ICON_TILE + ICON_GAP
        max_x = max(max_x, x)
        y += ICON_TILE + ICON_ROW
    height = (y - ICON_ROW + 24) if prog.stacks else 48
    return IconPlan(cells, connectors, captions, max_x + 16, height)


def _svg_icon_cell(cell: IconCell) -> str:
    t, r = ICON_TILE, ICON_RADIUS
    x, y = cell.x, cell.y
    parts = [
        f'<rect x="{x}" y="{y}" width="{t}" height="{t}" rx="{r}" '
        f'fill="{cell.fill}" stroke="{cell.stroke}" stroke-width="2"/>'
    ]
    if cell.kind == "whenColor":
        sx, sy = x + 26, y + 16
        parts.append(
            f'<rect x="{sx}" y="{sy}" width="44" height="58" rx="7" '
            f'fill="#fff" stroke="#333" stroke-width="2"/>'
        )
        parts.append(f'<circle cx="{sx + 22}" cy="{sy + 22}" r="13" fill="#1a1a1a"/>')
        parts.append(f'<circle cx="{sx + 22}" cy="{sy + 22}" r="6" fill="#7ec8e3"/>')
        parts.append(
            f'<circle cx="{x + 90}" cy="{y + 94}" r="18" fill="{cell.accent}" '
            f'stroke="{_chip_stroke(cell.accent)}" stroke-width="3"/>'
        )
    elif cell.kind == "ledMatrix":
        origin_x, origin_y = x + 23, y + 28
        cell_n, gap = 22, 6
        for row in range(3):
            for col in range(3):
                px = origin_x + col * (cell_n + gap)
                py = origin_y + row * (cell_n + gap)
                parts.append(
                    f'<rect x="{px}" y="{py}" width="{cell_n}" height="{cell_n}" '
                    f'rx="5" fill="{cell.accent}" stroke="{_chip_stroke(cell.accent)}" '
                    f'stroke-width="1"/>'
                )
    elif cell.kind == "whenStart":
        cx, cy = x + t / 2, y + t / 2
        parts.append(
            f'<polygon points="{cx - 16},{cy - 22} {cx - 16},{cy + 22} {cx + 24},{cy}" '
            f'fill="#fff"/>'
        )
    else:
        words = cell.label.replace("_", " ")
        if len(words) > 18:
            words = words[:17] + "…"
        parts.append(
            f'<text x="{x + t / 2}" y="{y + t / 2 + 5}" text-anchor="middle" '
            f'font-family="Arial, Helvetica, sans-serif" font-size="12" '
            f'font-weight="bold" fill="#fff">{_esc(words)}</text>'
        )
    if cell.port:
        parts.append(f'<circle cx="{x + t - 18}" cy="{y + 18}" r="13" fill="#fff"/>')
        parts.append(
            f'<text x="{x + t - 18}" y="{y + 23}" text-anchor="middle" '
            f'font-family="Arial, Helvetica, sans-serif" font-size="13" '
            f'font-weight="bold" fill="#222">{_esc(cell.port)}</text>'
        )
    return "\n".join(parts)


def draw_icon_program(prog: Program, index: dict) -> tuple[str, float, float]:
    plan = _plan_icon(prog, index)
    parts = []
    for cap_x, cap_y, text, fill in plan.captions:
        parts.append(
            f'<rect x="{cap_x}" y="{cap_y - 8}" width="14" height="14" rx="3" fill="{fill}"/>'
        )
        parts.append(
            f'<text x="{cap_x + 20}" y="{cap_y + 5}" '
            f'font-family="Arial, Helvetica, sans-serif" font-size="16" '
            f'font-weight="bold" fill="#333">{_esc(text)}</text>'
        )
    for cx, cy in plan.connectors:
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="8" fill="#e6e6e6" stroke="#bbb" stroke-width="2"/>'
        )
    for cell in plan.cells:
        parts.append(_svg_icon_cell(cell))
    w, h = plan.width, plan.height
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(w)}" height="{int(h)}" '
        f'viewBox="0 0 {int(w)} {int(h)}">\n'
        f'<rect width="100%" height="100%" fill="#f5f5f5"/>\n'
        + "\n".join(parts)
        + "\n</svg>"
    )
    return svg, w, h


def _paint_icon_png(prog: Program, index: dict, png_path: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont

    plan = _plan_icon(prog, index)
    scale = 2
    img = Image.new("RGB", (int(plan.width) * scale, int(plan.height) * scale), "#f5f5f5")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 28)
        small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
        small = font
    for cap_x, cap_y, text, fill in plan.captions:
        x, y = cap_x * scale, cap_y * scale
        draw.rounded_rectangle([x, y - 16, x + 28, y + 12], radius=6, fill=fill)
        draw.text((x + 40, y - 16), text, fill="#333333", font=font)
    for cx, cy in plan.connectors:
        r = 16
        draw.ellipse(
            [(cx * scale - r), (cy * scale - r), (cx * scale + r), (cy * scale + r)],
            fill="#e6e6e6",
            outline="#bbbbbb",
            width=3,
        )
    t = ICON_TILE * scale
    for cell in plan.cells:
        x, y = cell.x * scale, cell.y * scale
        draw.rounded_rectangle(
            [x, y, x + t, y + t], radius=ICON_RADIUS * scale, fill=cell.fill, outline=cell.stroke, width=3
        )
        if cell.kind == "whenColor":
            sx, sy = x + 52, y + 32
            draw.rounded_rectangle([sx, sy, sx + 88, sy + 116], radius=14, fill="#ffffff", outline="#333333", width=3)
            draw.ellipse([sx + 18, sy + 18, sx + 70, sy + 70], fill="#1a1a1a")
            draw.ellipse([sx + 32, sy + 32, sx + 56, sy + 56], fill="#7ec8e3")
            cr = 36
            cx, cy = x + 180, y + 188
            draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=cell.accent, outline=_chip_stroke(cell.accent), width=4)
        elif cell.kind == "ledMatrix":
            origin_x, origin_y = x + 46, y + 56
            n, gap = 44, 12
            for row in range(3):
                for col in range(3):
                    px = origin_x + col * (n + gap)
                    py = origin_y + row * (n + gap)
                    draw.rounded_rectangle(
                        [px, py, px + n, py + n], radius=10, fill=cell.accent, outline=_chip_stroke(cell.accent), width=2
                    )
        elif cell.kind == "whenStart":
            cx, cy = x + t / 2, y + t / 2
            draw.polygon([(cx - 32, cy - 44), (cx - 32, cy + 44), (cx + 48, cy)], fill="#ffffff")
        else:
            draw.text((x + 24, y + t / 2 - 12), cell.label[:16], fill="white", font=small)
        if cell.port:
            pr = 26
            px, py = x + t - 36, y + 36
            draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill="#ffffff")
            draw.text((px - 8, py - 12), cell.port, fill="#222222", font=small)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(png_path, "PNG")


def draw_program(prog: Program, index: dict) -> tuple[str, float, float]:
    if prog.is_icon:
        return draw_icon_program(prog, index)
    y = 16
    x = 16
    parts = []
    max_w = 400.0
    for stack in prog.stacks:
        d = draw_node(stack, index, 0, 0)
        parts.append(_shift_svg(d.svg, x, y))
        y += d.height + 24
        max_w = max(max_w, d.width + 32)
    height = y + 16
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(max_w)}" height="{int(height)}" '
        f'viewBox="0 0 {int(max_w)} {int(height)}">\n'
        f'<rect width="100%" height="100%" fill="#f5f5f5"/>\n'
        + "\n".join(parts)
        + "\n</svg>"
    )
    return svg, max_w, height


def _try_png(svg_path: Path, png_path: Path, prog: Program | None, index: dict | None) -> bool:
    if prog is not None and index is not None:
        try:
            _paint_png(prog, index, png_path)
            return png_path.is_file() and png_path.stat().st_size > 100
        except Exception as exc:
            print(f"PIL PNG failed ({exc}); trying rsvg-convert", file=sys.stderr)
    import shutil
    import subprocess

    if shutil.which("rsvg-convert"):
        r = subprocess.run(
            ["rsvg-convert", "-o", str(png_path), str(svg_path)],
            capture_output=True,
        )
        return r.returncode == 0 and png_path.is_file()
    return False


def _layout_boxes(node: Node, index: dict, x: int, y: int) -> tuple[list[tuple], int, int]:
    """Return (boxes, width, height) for a PIL pass. box = (x,y,w,h,fill,label,kind)."""
    info = block_info(index, node.opcode) or {
        "opcode": node.opcode,
        "shape": "stack",
        "category": "extension",
        "message": node.opcode,
        "arguments": [],
    }
    shape = info.get("shape", "stack")
    colors = _cat_colors(index, info.get("category", "extension"))
    label = _format_message(info, node.args, index.get("menus", {}))
    head, tail = _condition_split(label)
    fill = colors["primary"]
    kind = "hex" if shape in BOOLEAN_SHAPES else "pill" if shape in REPORTER_SHAPES else "hat" if shape in HAT_SHAPES else "c" if (shape in C_SHAPES or node.then or node.orelse) else "stack"
    text_w = max(90, int(PAD_X * 2 + len(label) * CHAR_W))
    header = 36 if kind == "hat" else 32 if kind in {"hex", "pill"} else ROW_H
    head_w = int(len(head) * CHAR_W)
    boxes: list[tuple] = []
    if kind == "c":
        inner_y = y + header
        inner_h = 8
        inner_w = text_w
        cond_boxes: list[tuple] = []
        if node.condition:
            cb, cw, ch = _layout_boxes(node.condition, index, x + PAD_X + head_w + 12, y + 4)
            cond_boxes = cb
            if tail:
                cond_boxes.append(
                    (x + PAD_X + head_w + cw + 20, y + 8, 40, 20, fill, tail, "label")
                )
            text_w = max(text_w, PAD_X * 2 + head_w + cw + int(len(tail) * CHAR_W) + 28)
        then_boxes: list[tuple] = []
        for ch in node.then:
            b, w, h = _layout_boxes(ch, index, x + 16, inner_y + inner_h)
            then_boxes.extend(b)
            inner_h += h - 2
            inner_w = max(inner_w, w + 16)
        else_h = 0
        else_boxes: list[tuple] = []
        else_header = 0
        if node.orelse:
            else_header = ROW_H
            ey = inner_y + inner_h + else_header
            eh = 8
            for ch in node.orelse:
                b, w, h = _layout_boxes(ch, index, x + 16, ey + eh)
                else_boxes.extend(b)
                eh += h - 2
                inner_w = max(inner_w, w + 16)
            else_h = eh
        total_h = header + inner_h + else_header + else_h + 16
        total_w = max(text_w, inner_w) + 8
        # A C-block is a header bar, a left rail, and a footer -- not a
        # filled slab with the body drawn on top of it.
        boxes.append((x, y, total_w, header, fill, head, "c-head"))
        boxes.append((x, y + header, 14, inner_h + else_header + else_h, fill, "", "rail"))
        boxes.append((x, y + total_h - 16, total_w, 16, fill, "", "rail"))
        boxes.extend(cond_boxes)
        boxes.extend(then_boxes)
        if node.orelse:
            boxes.append((x, inner_y + inner_h, total_w, else_header, fill, "else", "c-head"))
            boxes.extend(else_boxes)
        return boxes, total_w, total_h
    w = text_w + (20 if kind == "hex" else 8)
    h = header + (8 if kind == "hat" else 0)
    if node.condition:
        cb, cw, ch = _layout_boxes(node.condition, index, x + PAD_X + head_w + 12, y + 4)
        w = max(w, PAD_X * 2 + head_w + cw + 20)
        boxes.append((x, y, w, h, fill, head, kind))
        boxes.extend(cb)
    else:
        boxes.append((x, y, w, h, fill, label, kind))
    extra = 0
    max_w = w
    cy = y + h - 2
    for ch in node.then:
        b, cw, chh = _layout_boxes(ch, index, x + 12, cy)
        boxes.extend(b)
        cy += chh - 2
        extra += chh - 2
        max_w = max(max_w, cw + 12)
    return boxes, max_w, h + extra


def _paint_png(prog: Program, index: dict, png_path: Path) -> None:
    if prog.is_icon:
        _paint_icon_png(prog, index, png_path)
        return
    from PIL import Image, ImageDraw, ImageFont

    all_boxes: list[tuple] = []
    y = 16
    max_w = 400
    max_h = 16
    for stack in prog.stacks:
        boxes, w, h = _layout_boxes(stack, index, 16, y)
        all_boxes.extend(boxes)
        y += h + 20
        max_w = max(max_w, w + 32)
        max_h = y
    scale = 2
    img = Image.new("RGB", (int(max_w) * scale, int(max_h + 16) * scale), "#f5f5f5")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
        small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
        small = font
    for x, y, w, h, fill, label, kind in all_boxes:
        x, y, w, h = x * scale, y * scale, w * scale, h * scale
        if kind == "label":
            draw.text((x + 4, y + 2), label, fill="white", font=small)
            continue
        if kind == "rail":
            draw.rectangle([x, y, x + w, y + h], fill=fill)
            continue
        r = 16 if kind in {"pill", "hat"} else 12
        if kind == "hex":
            tip = 20
            pts = [
                (x + tip, y),
                (x + w - tip, y),
                (x + w, y + h / 2),
                (x + w - tip, y + h),
                (x + tip, y + h),
                (x, y + h / 2),
            ]
            draw.polygon(pts, fill=fill)
        else:
            draw.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill)
        if label:
            draw.text((x + 14, y + (10 if kind == "hat" else 8)), label, fill="white", font=font)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(png_path, "PNG")


# ---------------------------------------------------------------------------
# Preview HTML
# ---------------------------------------------------------------------------


def write_preview(
    out: Path, title: str, svg: str, problems: list[Problem], *, canvas: str = "word"
) -> None:
    status = (
        '<p class="ok">0 problems</p>'
        if not problems
        else "<ul class='bad'>" + "".join(f"<li>{html_lib.escape(str(p))}</li>" for p in problems) + "</ul>"
    )
    if canvas == "icon":
        blurb = (
            "Icon Blocks picture — pictorial tiles, not Word Blocks. "
            "Each yellow hat is its own stack; snapping two hats into one row "
            "waits for the first colour, then the second. Figma imports the SVG."
        )
    else:
        blurb = "Word Blocks picture from <code>tools/spike/blocks.json</code>. Figma imports the SVG."
    out.write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{html_lib.escape(title)}</title>
<style>
  body {{ font-family: system-ui, sans-serif; background: #f5f5f5; margin: 0; }}
  header {{ background: #fff; padding: 16px 24px; border-bottom: 1px solid #ddd; }}
  main {{ padding: 24px; }}
  .ok {{ color: #0a7; }}
  .bad {{ color: #c00; }}
  .stage {{ background: #fff; display: inline-block; padding: 8px; border-radius: 8px; }}
</style>
</head>
<body>
<header>
  <h1>{html_lib.escape(title)}</h1>
  {status}
  <p>{blurb}</p>
</header>
<main><div class="stage">{svg}</div></main>
</body>
</html>
"""
    )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def program_path_for(build: Path) -> Path:
    p = build / "program.spike"
    if p.is_file():
        return p
    sys.exit(f"missing {p}")


def cmd_check(target: Path, index: dict) -> int:
    prog = parse_program(program_path_for(target) if target.is_dir() else target)
    problems = check_program(prog, index)
    for p in problems:
        print(p)
    print(f"{len(problems)} problem(s)")
    return 1 if problems else 0


def cmd_render(target: Path, index: dict) -> int:
    build = target if target.is_dir() else target.parent
    prog = parse_program(program_path_for(target) if target.is_dir() else target)
    svg, _, _ = draw_program(prog, index)
    out_dir = build / "renders"
    out_dir.mkdir(exist_ok=True)
    svg_path = out_dir / "program.svg"
    svg_path.write_text(svg)
    print(f"wrote {svg_path}")
    png_path = out_dir / "program.png"
    if _try_png(svg_path, png_path, prog, index):
        print(f"wrote {png_path}")
    else:
        print("PNG skipped; SVG is the picture Figma should import")
    return 0


def cmd_preview(target: Path, index: dict) -> int:
    build = target if target.is_dir() else target.parent
    prog = parse_program(program_path_for(target) if target.is_dir() else target)
    problems = check_program(prog, index)
    svg, _, _ = draw_program(prog, index)
    out = build / "program.html"
    title = build.name if target.is_dir() else target.stem
    write_preview(out, title, svg, problems, canvas=prog.canvas if prog.is_icon else "word")
    print(f"wrote {out}")
    return 0


EXPECT = re.compile(r"^#\s*expect:\s*(.+)$", re.M)


def cmd_fixtures(index: dict) -> int:
    if not FIXTURES.is_dir():
        sys.exit(f"missing {FIXTURES}")
    failed = 0
    for path in sorted(FIXTURES.glob("*.spike")):
        text = path.read_text()
        prog = parse_program(path)
        problems = check_program(prog, index)
        codes = {p.code for p in problems}
        expect_fail = path.name.startswith("bad-")
        m = EXPECT.search(text)
        wanted = {c.strip() for c in m.group(1).replace(",", " ").split()} if m else set()
        if expect_fail:
            if not problems:
                print(f"FAIL {path.name}: expected problems, got 0")
                failed += 1
            elif not wanted:
                # A negative control that fails for an unnamed reason proves
                # nothing: it might be failing on a typo.
                print(f"FAIL {path.name}: needs a '# expect: CODE' line")
                failed += 1
            elif not wanted <= codes:
                print(
                    f"FAIL {path.name}: expected {', '.join(sorted(wanted))}; "
                    f"got {', '.join(sorted(codes)) or 'nothing'}"
                )
                for p in problems:
                    print(f"  {p}")
                failed += 1
            else:
                print(f"PASS {path.name}: {', '.join(sorted(wanted))}")
        else:
            if problems:
                print(f"FAIL {path.name}: expected clean, got:")
                for p in problems:
                    print(f"  {p}")
                failed += 1
            else:
                # A good fixture also has to be drawable.
                try:
                    draw_program(prog, index)
                except Exception as exc:  # noqa: BLE001 - report, do not crash the suite
                    print(f"FAIL {path.name}: renders clean but draw failed: {exc}")
                    failed += 1
                    continue
                print(f"PASS {path.name}")
    print(f"{failed} fixture(s) failed" if failed else "all fixtures passed")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_ in (
        ("check", "validate a program.spike against the index"),
        ("preview", "write program.html with colourful blocks"),
        ("render", "write renders/program.svg plus a PNG (Pillow, else rsvg-convert)"),
    ):
        p = sub.add_parser(name, help=help_)
        p.add_argument("target", type=Path)
    sub.add_parser(
        "fixtures",
        help="run tools/spike/fixtures: good-* must be clean and drawable, "
        "bad-* must raise the code named in their '# expect:' line",
    )
    args = parser.parse_args()
    index = load_index()
    if args.command == "fixtures":
        return cmd_fixtures(index)
    target = args.target
    if not target.is_absolute():
        target = (Path.cwd() / target).resolve()
    if args.command == "check":
        return cmd_check(target, index)
    if args.command == "preview":
        return cmd_preview(target, index)
    return cmd_render(target, index)


if __name__ == "__main__":
    sys.exit(main())
