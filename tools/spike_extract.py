#!/usr/bin/env python3
"""Extract SPIKE App Word / Icon / Python block definitions.

The SPIKE web app at https://spike.legoeducation.com/ ships its block
catalogue in a hashed JS bundle. This script finds the current hash,
parses the definitions, and writes tools/spike/blocks.json.

    python3 tools/spike_extract.py
    python3 tools/spike_extract.py --from-dir /tmp/spikeprobe

Re-run when LEGO ships a new app. The JSON is the source of truth for
tools/blocks.py; do not hand-edit opcodes that came from the bundle.
Enrichment (shape-as-contract, hub gating, extensions, Python mapping)
is applied here as a documented overlay so it survives a re-extract.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "tools" / "spike" / "blocks.json"
APP = "https://spike.legoeducation.com/"

# ---------------------------------------------------------------------------
# Bundle fetch
# ---------------------------------------------------------------------------


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "ian-spike-learning/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def discover_scripts(html: str) -> list[str]:
    return re.findall(r'src="(/static/js/[^"]+\.js)"', html)


def load_sources(from_dir: Path | None) -> tuple[str, dict[str, str]]:
    """Return (index_js_name, {filename: text})."""
    files: dict[str, str] = {}
    if from_dir is not None:
        html_path = from_dir / "index.html"
        if not html_path.is_file():
            # probe dir of already-downloaded chunks
            for p in from_dir.glob("*.js"):
                files[p.name] = p.read_text(errors="replace")
            if not files:
                sys.exit(f"no JS in {from_dir}")
            index_name = next(
                (n for n in files if n.startswith("index.")),
                next(iter(files)),
            )
            return index_name, files
        html = html_path.read_text(errors="replace")
        scripts = discover_scripts(html)
        for src in scripts:
            name = src.rsplit("/", 1)[-1]
            local = from_dir / name
            if local.is_file():
                files[name] = local.read_text(errors="replace")
        index_name = next(n for n in files if n.startswith("index."))
        return index_name, files

    html = fetch(APP).decode("utf-8", errors="replace")
    scripts = discover_scripts(html)
    if not scripts:
        sys.exit("no /static/js scripts in SPIKE index.html — app layout changed")
    # Every block definition class lives in index.*.js. The sibling chunks
    # (a ~6 MB lazy chunk and scratch-vendor) were checked and contain zero
    # `this.opcode=` sites, so there is no reason to pull 11 MB for them.
    index_src = next((s for s in scripts if "/index." in s), None)
    if index_src is None:
        sys.exit(f"no index.*.js among {scripts} — app layout changed")
    name = index_src.rsplit("/", 1)[-1]
    files[name] = fetch(APP.rstrip("/") + index_src).decode("utf-8", errors="replace")
    return name, files


# ---------------------------------------------------------------------------
# JS helpers
# ---------------------------------------------------------------------------


def brace_match(text: str, start: int) -> str:
    """start points at '{'. Return the object including braces."""
    if start >= len(text) or text[start] != "{":
        raise ValueError("brace_match not on {")
    depth = 0
    i = start
    in_str = False
    esc = False
    quote = ""
    while i < len(text):
        c = text[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == quote:
                in_str = False
        else:
            if c in ('"', "'"):
                in_str = True
                quote = c
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
        i += 1
    raise ValueError("unbalanced {")


def decode_js_string(s: str) -> str:
    def hex_repl(m: re.Match[str]) -> str:
        return chr(int(m.group(1), 16))

    s = re.sub(r"\\x([0-9A-Fa-f]{2})", hex_repl, s)
    s = re.sub(r"\\u([0-9A-Fa-f]{4})", hex_repl, s)
    s = s.replace("\\n", "\n").replace("\\t", "\t").replace('\\"', '"').replace("\\\\", "\\")
    return s


def lookup_path(obj: object, path: str) -> object:
    if isinstance(obj, dict) and path in obj and isinstance(obj[path], str):
        return obj[path]
    cur: object = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


# ---------------------------------------------------------------------------
# Catalogue pieces from the bundle
# ---------------------------------------------------------------------------

CATEGORY_COLORS_RE = re.compile(
    r"(control|data|data_lists|light|event|extension|more|motor|movement|"
    r"music|myBlocks|operators|sensing|sounds|variables|weather|flipperTest)"
    r':\{primary:"(#[0-9A-Fa-f]{6})",secondary:"(#[0-9A-Fa-f]{6})",'
    r'tertiary:"(#[0-9A-Fa-f]{6})"\}'
)

# Short name on I.j.X -> full scratch opcode prefix.
PREFIX_BY_SHORT_HINT = {
    "whenButton": "flipperevents",
    "whenColor": "flipperevents",
    "whenCondition": "flipperevents",
    "whenDistance": "flipperevents",
    "whenGesture": "flipperevents",
    "whenOrientation": "flipperevents",
    "whenPressed": "flipperevents",
    "whenProgramStarts": "flipperevents",
    "whenTimer": "flipperevents",
}

ARG_FIELD_TYPES = {
    "ColorSensorSelector": {"kind": "port", "device": "color-sensor", "multi": False},
    "ForceSensorSelector": {"kind": "port", "device": "force-sensor", "multi": False},
    "DistanceSensorSelector": {"kind": "port", "device": "distance-sensor", "multi": False},
    "SingleMotorSelector": {"kind": "port", "device": "motor", "multi": False},
    "SinglePortSelector": {"kind": "port", "device": "any", "multi": False},
    "MultiplePortSelector": {"kind": "port", "device": "motor", "multi": True},
    "MovementPortSelector": {"kind": "port-pair", "device": "motor", "multi": True},
    "Direction": {"kind": "direction"},
    "Matrix3x3ColorImage": {"kind": "matrix3x3"},
    "Matrix5x5BrightnessImage": {"kind": "matrix5x5"},
    "MatrixPixelIndex": {"kind": "pixel-index"},
    "Piano": {"kind": "piano"},
}

# z.E2 argument helper names extracted from the bundle.
KNOWN_ARG_HELPERS = {
    "colorSensorArgument": {
        "default": "A",
        "field": "ColorSensorSelector",
    },
    "forceSensorArgument": {"default": "A", "field": "ForceSensorSelector"},
    "distanceSensorArgument": {"default": "A", "field": "DistanceSensorSelector"},
    "singleMotorArgument": {"default": "A", "field": "SingleMotorSelector"},
    "portArgument": {"default": "A", "field": "SinglePortSelector"},
    "portsArgument": {"default": "A", "field": "MultiplePortSelector"},
    "movementPairArgument": {"default": "AB", "field": "MovementPortSelector"},
    "distanceComparatorArgument": {
        "default": "closerThan",
        "menu": "distanceComparator",
        "options": ["closerThan", "fartherThan", "exactlyAt"],
    },
    "unitDistanceArgument": {
        "default": "percent",
        "menu": "unitDistance",
        "options": ["percent", "cm", "inches"],
        "note": "percent is % of the sensor's 200 cm range, not % of anything on screen. 20% = 40 cm.",
    },
    "directionArgument": {"default": "clockwise", "field": "Direction"},
    "motorDirectionArgument": {
        "default": "shortest",
        "menu": "motorDirection",
        "options": ["shortest", "clockwise", "counterclockwise"],
    },
    "motorStopMethodArgument": {
        "default": "brake",
        "menu": "motorSetStopMethod",
        "options": ["brake", "hold", "coast"],
    },
    "moveDirectionArgument": {
        "default": "forward",
        "menu": "moveDirection",
        "options": ["forward", "backward"],
    },
    "moveDistanceUnitArgument": {
        "default": "cm",
        "menu": "moveDistanceUnit",
        "options": ["cm", "inches"],
    },
    "unitMotorArgument": {
        "default": "rotations",
        "menu": "unitMotor",
        "options": ["rotations", "degrees", "seconds"],
    },
    "distanceArgument": {
        "default": "near",
        "menu": "nearOrFar",
        "options": ["near", "far", "changed"],
        "note": "near is the preset '< 20 cm'; far is '> 20 cm'. This is the block whose label contains a 20.",
    },
    "stopArgument": {
        "default": "all",
        "menu": "stopOption",
        "options": ["all", "this script", "other scripts"],
    },
}


def extract_colors(index_js: str) -> dict[str, dict[str, str]]:
    colors: dict[str, dict[str, str]] = {}
    for m in CATEGORY_COLORS_RE.finditer(index_js):
        colors[m.group(1)] = {
            "primary": m.group(2),
            "secondary": m.group(3),
            "tertiary": m.group(4),
        }
    return colors


def extract_i18n_key_map(index_js: str) -> dict[str, str]:
    """I.EventsWhenDistance=\"events.whenDistance\" """
    return dict(re.findall(r'I\.([A-Za-z0-9]+)="([A-Za-z0-9.]+)"', index_js))


def _parse_js_obj(blob: str) -> dict:
    quoted = re.sub(r'([,{]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:', r'\1"\2":', blob)
    quoted = decode_js_string(quoted)
    try:
        data = json.loads(quoted)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        data = {}
        for m in re.finditer(r'"([^"]+)":"([^"]*)"', blob):
            data[m.group(1)] = decode_js_string(m.group(2))
        return data


def extract_en_us(index_js: str) -> dict:
    """The bundle contains several `en-US` objects. We want the nested
    Word-Block catalogue (it starts with bargraphmonitor), not the flat
    music-drum table that appears first."""
    marker = '"en-US":{'
    best: dict = {}
    start = 0
    while True:
        i = index_js.find(marker, start)
        if i < 0:
            break
        blob = brace_match(index_js, i + len('"en-US":'))
        data = _parse_js_obj(blob)
        if "bargraphmonitor" in data or "sensors" in data or "events" in data:
            best = data
            break
        if len(json.dumps(data)) > len(json.dumps(best)):
            best = data
        start = i + len(marker)
    if not best:
        sys.exit("en-US Word-Block catalogue missing from bundle")
    return best


def extract_block_definitions(index_js: str) -> list[dict]:
    results: list[dict] = []
    for m in re.finditer(r"this\.opcode=I\.j\.(\w+)\}blockDefinition\(P\)\{return", index_js):
        short = m.group(1)
        # 'return' is followed by the object
        brace_at = index_js.find("{", m.end())
        try:
            body = brace_match(index_js, brace_at)
        except ValueError:
            continue
        bt = re.search(r"blockType:\w+\.(\w+)", body)
        shape_raw = bt.group(1) if bt else "COMMAND"
        terminal = "isTerminal:!0" in body or "isTerminal:true" in body
        branch = re.search(r"branchCount:(\d+)", body)
        text_key = re.search(r"text:P\.translate\((?:k\.d\.)?(\w+)\)", body)
        args = parse_arguments(body)
        results.append(
            {
                "short": short,
                "shape_raw": shape_raw,
                "is_terminal": terminal,
                "branch_count": int(branch.group(1)) if branch else 0,
                "text_key": text_key.group(1) if text_key else None,
                "arguments": args,
                "body": body,
            }
        )
    return results


def parse_arguments(body: str) -> list[dict]:
    am = re.search(r"arguments:\{", body)
    if not am:
        return []
    blob = brace_match(body, am.end() - 1)
    inner = blob[1:-1]
    args: list[dict] = []
    # Split on top-level commas between KEY:value
    pos = 0
    depth = 0
    in_str = False
    esc = False
    pieces: list[str] = []
    start = 0
    while pos < len(inner):
        c = inner[pos]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c in "{[(":
                depth += 1
            elif c in "}])":
                depth -= 1
            elif c == "," and depth == 0:
                pieces.append(inner[start:pos])
                start = pos + 1
        pos += 1
    if start < len(inner):
        pieces.append(inner[start:])
    for piece in pieces:
        piece = piece.strip()
        if not piece or ":" not in piece:
            continue
        name, rest = piece.split(":", 1)
        name = name.strip()
        rest = rest.strip()
        arg: dict = {"name": name}
        helper = re.search(r"z\.E2\.(\w+)", rest)
        if helper:
            hname = helper.group(1)
            arg["helper"] = hname
            if hname in KNOWN_ARG_HELPERS:
                arg.update({k: v for k, v in KNOWN_ARG_HELPERS[hname].items()})
        dv = re.search(r"defaultValue:(\d+|\"[^\"]+\")", rest)
        if dv:
            raw = dv.group(1)
            arg["default"] = int(raw) if raw.isdigit() else raw.strip('"')
        ty = re.search(r"type:(\w+)\.(\w+)", rest)
        if ty:
            arg["type"] = ty.group(2).lower()
        field = re.search(r"CustomFieldType\.(\w+)", rest)
        if field:
            arg["field"] = field.group(1)
            meta = ARG_FIELD_TYPES.get(field.group(1))
            if meta:
                arg["field_meta"] = meta
        args.append(arg)
    return args


FIELD_RE = re.compile(r"flipper[a-z]+_[A-Za-z0-9]+-[A-Za-z0-9-]+")
STANDALONE_RE = re.compile(r"flipper[a-z]+_[A-Za-z0-9]+(?![-A-Za-z0-9])")
KNOWN_SET_ANCHOR = '"flippermotor_motorTurnForDirection"'


def extract_opcode_strings(index_js: str) -> dict:
    """Classify every flipper-ish string in the bundle.

    Four unlike things in the bundle all look like opcodes:

    * live block opcodes (`flippersensors_isDistance`)
    * **field / shadow names**, which always carry a hyphen suffix
      (`flippermotor_multiple-port-selector`)
    * legacy opcodes kept only so old projects can be migrated
      (`flipperdisplay_ledImage`)
    * test blocks (`flippertest_assert`)

    Counting `flipper[a-z]+_[A-Za-z0-9]+` over the whole bundle mixes all
    four and, worse, truncates the field names at the hyphen -- which is
    how a nonexistent `flippermotor_multiple` opcode gets invented. The
    multi-select is real; that *name* is not.
    """
    fields = sorted(set(FIELD_RE.findall(index_js)))
    standalone = sorted(set(STANDALONE_RE.findall(index_js)))
    phantoms = sorted({f.split("-", 1)[0] for f in fields} - set(standalone))
    test = [o for o in standalone if o.startswith("flippertest_")]
    live = [o for o in standalone if not o.startswith("flippertest_")]
    return {
        "fields": fields,
        "standalone": live,
        "phantom_bases": phantoms,
        "test": test,
    }


def extract_known_opcodes(index_js: str) -> list[str]:
    """The app carries one flat list of every opcode it knows about."""
    i = index_js.find(KNOWN_SET_ANCHOR)
    if i < 0:
        return []
    start = index_js.rfind("[", 0, i)
    end = index_js.find("]", i)
    if start < 0 or end < 0:
        return []
    return re.findall(r'"([^"]+)"', index_js[start : end + 1])


def extract_legacy_opcodes(index_js: str) -> tuple[dict[str, str], list[str]]:
    """Opcodes the app rewrites when it loads an older project.

    `opcodeMapping={old:"new",...}` gives clean pairs; migration classes
    also name a single `srcOpcode` they convert away from.
    """
    mapping: dict[str, str] = {}
    for m in re.finditer(r"opcodeMapping=\{([^{}]{0,3000})\}", index_js):
        for old, new in re.findall(r'([A-Za-z0-9_]+):"([A-Za-z0-9_]+)"', m.group(1)):
            if "_" in old and "_" in new:
                mapping[old] = new
    src = sorted(set(re.findall(r'srcOpcode="([A-Za-z0-9_]+)"', index_js)))
    return mapping, src


# Opcode strings with no definition class in the current release, and why.
# Checked by hand once, against the migration classes in the bundle.
RETIRED_REASON = {
    "flipperevents_whenTilted": "renamed: the palette now says whenOrientation",
    "flippersensors_isTilted": "renamed: now isorientation",
    "flipperevents_whenGreaterThan": "split into whenTimer",
    "flipperevents_broadcast": "handled by the Scratch core event_broadcast block",
    "flipperevents_broadcastandwait": "handled by the Scratch core block",
    "flippermoremove_startDualPower": "replaced by startDualSpeed",
    "flippermoremotor_motorDidMovement": "removed from the palette",
    "flippermoremove_moveDidMovement": "removed from the palette",
    "flippermoremotor_motorSetStallDetection": "no definition class in this release",
    "flippersensors_whenColor": "the colour hat is flipperevents_whenColor",
    "flipperlight_centerButtonColor": "superseded by centerButtonLight",
}


def classify_uncovered(
    standalone: list[str],
    covered: set[str],
    legacy: set[str],
) -> list[dict]:
    out = []
    for op in standalone:
        if op in covered:
            continue
        prefix = op.split("_", 1)[0]
        short = op.split("_", 1)[-1]
        if short in {"menu", "custom"}:
            reason = "menu / field name, not a draggable block"
        elif prefix == "flipperdisplay":
            reason = "legacy display family — today's blocks are flipperlight_lightDisplay*"
        elif prefix == "flippermusic":
            reason = "music extension: opcode string only, no definition class in this release"
        elif op in RETIRED_REASON:
            reason = RETIRED_REASON[op]
        elif op in legacy:
            reason = "kept only so older projects can be migrated"
        else:
            reason = "no definition class in this release"
        out.append({"opcode": op, "reason": reason})
    return out


def extract_icon_opcodes(index_js: str) -> list[str]:
    ops = sorted(set(re.findall(r"horizontal[a-z]+_[a-zA-Z0-9]+", index_js)))
    return [o for o in ops if "_" in o and not o.endswith("_horizontal")]


MORE_MOVE_SHORTS = {
    "startDualSpeed",
    "startDualPower",
    "movementSetAcceleration",
    "movementSetStopMethod",
    "moveDistanceAtSpeed",
    "startSteerAtSpeed",
    "startSteerAtPower",
}


def prefix_from_text_key(text_key: str | None, short: str) -> str | None:
    if not text_key:
        return PREFIX_BY_SHORT_HINT.get(short)
    rules = (
        ("Moremotor", "flippermoremotor"),
        ("Moresensors", "flippermoresensors"),
        ("Events", "flipperevents"),
        ("Motor", "flippermotor"),
        ("Sensors", "flippersensors"),
        ("Sound", "flippersound"),
        ("Lights", "flipperlight"),
        ("Control", "flippercontrol"),
        ("Operator", "flipperoperator"),
        ("Move", None),
    )
    for start, pref in rules:
        if text_key.startswith(start):
            if pref:
                return pref
            return "flippermoremove" if short in MORE_MOVE_SHORTS else "flippermove"
    return PREFIX_BY_SHORT_HINT.get(short)


# Definition classes whose text key points at the wrong family.
SHORT_TO_OPCODE = {
    # "Lights" wording, but the opcode lives in the light family under its
    # own name -- the sensor's own light ring, not a display block.
    "ultrasonicLightUp": "flipperlight_ultrasonicLightUp",
}


def map_short_to_full(
    short: str,
    full_ops: list[str],
    key_map: dict[str, str],
    text_key: str | None,
    valid: set[str],
) -> str | None:
    """Resolve a definition class's short name to a real opcode.

    Never guesses: if no candidate is an opcode the bundle actually
    contains, returns None and the caller records it as unmapped. The
    previous version fell through to f"{prefix}_{canon}", which minted
    three opcodes that do not exist in the app.
    """
    if short in SHORT_TO_OPCODE:
        return SHORT_TO_OPCODE[short]
    # I.motorAbsolutePosition = "absolutePosition" (no dot) is an opcode alias.
    canon = key_map.get(short, short)
    if "." in str(canon):
        canon = short
    prefix = prefix_from_text_key(text_key, short)
    candidates = []
    if prefix:
        candidates.append(f"{prefix}_{canon}")
        if canon != short:
            candidates.append(f"{prefix}_{short}")
    lower = {o.lower(): o for o in valid}
    for c in candidates:
        if c in valid:
            return c
        if c.lower() in lower:
            return lower[c.lower()]
    matches = [o for o in full_ops if o.split("_", 1)[-1].lower() == canon.lower()]
    if prefix:
        prefixed = [o for o in matches if o.startswith(prefix + "_")]
        if prefixed:
            return prefixed[0]
    if len(matches) == 1:
        return matches[0]
    core = [o for o in matches if "more" not in o.split("_")[0]]
    if len(core) == 1:
        return core[0]
    return None


def shape_of(raw: str, short: str, full: str | None) -> str:
    raw_u = raw.upper()
    if raw_u == "HAT" or short.startswith("when"):
        return "hat"
    if raw_u == "BOOLEAN" or short.startswith("is") or short.startswith("buttonIs"):
        return "boolean"
    if raw_u == "REPORTER":
        return "reporter"
    if short in {"stop"} or (full or "").endswith("_stop"):
        return "cap"  # terminal stack
    return "stack"


def category_of(full: str) -> str:
    prefix = full.split("_", 1)[0]
    return {
        "flipperevents": "event",
        "flippermotor": "motor",
        "flippermoremotor": "more",
        "flippermove": "movement",
        "flippermoremove": "more",
        "flippersensors": "sensing",
        "flippermoresensors": "more",
        "flipperdisplay": "light",
        "flipperlight": "light",
        "flippersound": "sounds",
        "flippercontrol": "control",
        "flipperoperator": "operators",
        "flippermusic": "music",
        "weather": "weather",
        "control": "control",
        "operator": "operators",
        "data": "data",
        "horizontalevents": "event",
        "horizontalmotor": "motor",
        "horizontalmove": "movement",
        "horizontaldisplay": "light",
        "horizontalsound": "sounds",
        "horizontalcontrol": "control",
        "horizontalbargraphmonitor": "data",
        "horizontaldisplaymonitor": "light",
    }.get(prefix, "extension")


# ---------------------------------------------------------------------------
# Enrichment overlay — facts the bundle does not state as data
# ---------------------------------------------------------------------------

# Shape is the flow-control contract. A boolean never advances the program
# by itself; a hat never sits under another block.
SHAPE_CONTRACT = {
    "hat": "Starts its own stack. Nothing snaps above it. The rest of the stack runs when the event fires — it does not 'wait' inside another stack.",
    "stack": "A command. Snaps under a hat or another stack block and moves execution to the next block when it finishes. Blocks whose name starts with 'start' finish immediately and leave the motor/sound running.",
    "boolean": "A hexagon. Reports true/false. Does nothing on its own. Must be dropped inside wait-until, if, or repeat-until.",
    "reporter": "An oval. Reports a number or string. Must be dropped into a number/string slot. Does nothing on its own.",
    "c": "A C-shaped wrapper (forever / if / repeat). Holds a stack in its mouth.",
    "cap": "A stack that nothing can snap under (stop all).",
}

EXTENSION_BY_PREFIX = {
    "flippermoremotor": "more-motors",
    "flippermoremove": "more-movement",
    "flippermoresensors": "more-sensors",
    "flippermusic": "music",
    "weather": "weather",
}

# Hardware the block talks to. Motors/sensors mix across hubs; these do not.
PRIME_ONLY_SHORT = {
    # 5x5 hub matrix lives on the Prime hub. Essential has no built-in matrix.
    "lightDisplayImageOn",
    "lightDisplayImageOnForTime",
    "lightDisplayOff",
    "lightDisplayRotate",
    "lightDisplaySetBrightness",
    "lightDisplaySetOrientation",
    "lightDisplaySetPixel",
    "lightDisplayText",
    "centerButtonLight",
    # Prime hub speaker. Essential has none.
    "beep",
    "beepForTime",
    "playSound",
    "playSoundUntilDone",
    "stopSound",
}

# 3x3 colour matrix is an accessory on a port. Essential ships it; Prime does
# not, but the blocks appear whenever the accessory is plugged in.
ACCESSORY_3X3 = {
    "lightColorMatrixImageOn",
    "lightColorMatrixImageOnForTime",
    "lightColorMatrixOff",
    "lightColorMatrixRotate",
    "lightColorMatrixSetBrightness",
    "lightColorMatrixSetOrientation",
    "lightColorMatrixSetPixel",
}


PYTHON_MAP = {
    "flipperevents_whenProgramStarts": {
        "api": ["runloop"],
        "code": "async def main():\n    ...\nrunloop.run(main())",
    },
    "flippermotor_motorStartDirection": {
        "api": ["motor", "hub.port"],
        "code": "motor.run(port.A, velocity)  # velocity sign is direction",
    },
    "flippermotor_motorTurnForDirection": {
        "api": ["motor", "hub.port"],
        "code": "await motor.run_for_degrees(port.A, degrees, velocity)\n# or await motor.run_for_time(port.A, ms, velocity)",
    },
    "flippermotor_motorStop": {
        "api": ["motor", "hub.port"],
        "code": "motor.stop(port.A)",
    },
    "flippermotor_motorSetSpeed": {
        "api": ["motor"],
        "code": "# default velocity for later motor.run / run_for_* calls; Word Block only — Python passes velocity each call",
    },
    "flippermotor_motorGoDirectionToPosition": {
        "api": ["motor", "hub.port"],
        "code": "await motor.run_to_absolute_position(port.A, degrees, velocity)",
    },
    "flippermotor_absolutePosition": {
        "api": ["motor", "hub.port"],
        "code": "motor.absolute_position(port.A)",
    },
    "flippermotor_speed": {
        "api": ["motor", "hub.port"],
        "code": "motor.velocity(port.A)",
    },
    "flippermoremotor_motorStartPower": {
        "api": ["motor", "hub.port"],
        "code": "motor.run(port.A, duty)  # power, not speed",
    },
    "flippermoremotor_motorGoToRelativePosition": {
        "api": ["motor", "hub.port"],
        "code": "await motor.run_to_relative_position(port.A, degrees, velocity)",
    },
    "flippermove_setMovementPair": {
        "api": ["motor_pair", "hub.port"],
        "code": "motor_pair.pair(motor_pair.PAIR_1, port.A, port.B)",
    },
    "flippermove_startMove": {
        "api": ["motor_pair"],
        "code": "motor_pair.move(motor_pair.PAIR_1, 0, velocity=360)  # steering 0 = straight",
    },
    "flippermove_move": {
        "api": ["motor_pair"],
        "code": "await motor_pair.move_for_degrees(motor_pair.PAIR_1, degrees, steering, velocity=360)",
    },
    "flippermove_steer": {
        "api": ["motor_pair"],
        "code": "await motor_pair.move_for_degrees(motor_pair.PAIR_1, degrees, steering, velocity=360)",
    },
    "flippermove_startSteer": {
        "api": ["motor_pair"],
        "code": "motor_pair.move(motor_pair.PAIR_1, steering, velocity=360)",
    },
    "flippermove_stopMove": {
        "api": ["motor_pair"],
        "code": "motor_pair.stop(motor_pair.PAIR_1)",
    },
    "flippermoremove_startDualSpeed": {
        "api": ["motor_pair"],
        "code": "motor_pair.move_tank(motor_pair.PAIR_1, left_velocity, right_velocity)",
    },
    "flippersensors_isDistance": {
        "api": ["distance_sensor", "hub.port"],
        "code": "distance_sensor.distance(port.D) < 100  # mm; None if nothing seen",
    },
    "flippersensors_distance": {
        "api": ["distance_sensor", "hub.port"],
        "code": "distance_sensor.distance(port.D)  # millimetres, or None",
    },
    "flipperevents_whenDistance": {
        "api": ["distance_sensor", "runloop", "hub.port"],
        "code": "async def on_close():\n    ...\n# hats become tasks; or await runloop.until(lambda: distance_sensor.distance(port.D) < 100)",
    },
    "flippersensors_isColor": {
        "api": ["color_sensor", "color", "hub.port"],
        "code": "color_sensor.color(port.A) is color.RED",
    },
    "flippersensors_color": {
        "api": ["color_sensor", "hub.port"],
        "code": "color_sensor.color(port.A)",
    },
    "flippersensors_isPressed": {
        "api": ["force_sensor", "hub.port"],
        "code": "force_sensor.pressed(port.A)",
    },
    "flippersensors_force": {
        "api": ["force_sensor", "hub.port"],
        "code": "force_sensor.force(port.A)  # newtons",
    },
    "flipperlight_lightDisplayImageOn": {
        "api": ["hub.light_matrix"],
        "code": "light_matrix.show_image(light_matrix.IMAGE_HAPPY)  # Prime 5x5",
    },
    "flipperlight_lightDisplayText": {
        "api": ["hub.light_matrix"],
        "code": "light_matrix.write('Hi')",
    },
    "flipperlight_lightColorMatrixImageOn": {
        "api": ["color_matrix", "hub.port"],
        "code": "color_matrix.show(port.A, pixels)  # 3x3 accessory",
    },
    "flippersound_beep": {
        "api": ["hub.sound"],
        "code": "sound.beep(440, 1000, 100)  # Prime speaker",
    },
    "control_forever": {
        "api": ["runloop"],
        "code": "while True:\n    ...\n    await runloop.sleep_ms(0)",
    },
    "control_wait": {
        "api": ["runloop"],
        "code": "await runloop.sleep_ms(1000)",
    },
    "control_wait_until": {
        "api": ["runloop"],
        "code": "await runloop.until(lambda: ...)",
    },
    "control_if": {"api": [], "code": "if condition:\n    ..."},
    "control_if_else": {"api": [], "code": "if condition:\n    ...\nelse:\n    ..."},
}

SCRATCH_BLOCKS = [
    {
        "opcode": "control_forever",
        "short": "forever",
        "category": "control",
        "shape": "c",
        "message": "forever",
        "arguments": [],
        "hubs": ["prime", "essential"],
        "extension": None,
        "python": PYTHON_MAP["control_forever"],
    },
    {
        "opcode": "control_if",
        "short": "if",
        "category": "control",
        "shape": "c",
        "message": "if <CONDITION> then",
        "arguments": [{"name": "CONDITION", "type": "boolean"}],
        "hubs": ["prime", "essential"],
        "extension": None,
        "python": PYTHON_MAP["control_if"],
    },
    {
        "opcode": "control_if_else",
        "short": "if_else",
        "category": "control",
        "shape": "c",
        "message": "if <CONDITION> then / else",
        "arguments": [{"name": "CONDITION", "type": "boolean"}],
        "hubs": ["prime", "essential"],
        "extension": None,
        "python": PYTHON_MAP["control_if_else"],
    },
    {
        "opcode": "control_repeat",
        "short": "repeat",
        "category": "control",
        "shape": "c",
        "message": "repeat (TIMES)",
        "arguments": [{"name": "TIMES", "type": "number", "default": 10}],
        "hubs": ["prime", "essential"],
        "extension": None,
        "python": {"api": [], "code": "for _ in range(n):\n    ..."},
    },
    {
        "opcode": "control_repeat_until",
        "short": "repeat_until",
        "category": "control",
        "shape": "c",
        "message": "repeat until <CONDITION>",
        "arguments": [{"name": "CONDITION", "type": "boolean"}],
        "hubs": ["prime", "essential"],
        "extension": None,
        "python": {"api": ["runloop"], "code": "while not condition:\n    ..."},
    },
    {
        "opcode": "control_wait",
        "short": "wait",
        "category": "control",
        "shape": "stack",
        "message": "wait (DURATION) seconds",
        "arguments": [{"name": "DURATION", "type": "number", "default": 1}],
        "hubs": ["prime", "essential"],
        "extension": None,
        "python": PYTHON_MAP["control_wait"],
    },
    {
        "opcode": "control_wait_until",
        "short": "wait_until",
        "category": "control",
        "shape": "stack",
        "message": "wait until <CONDITION>",
        "arguments": [{"name": "CONDITION", "type": "boolean"}],
        "hubs": ["prime", "essential"],
        "extension": None,
        "python": PYTHON_MAP["control_wait_until"],
        "notes": [
            "This is the block that makes a boolean do something. "
            "Drop flippersensors_isDistance in the hexagon slot."
        ],
    },
    {
        "opcode": "control_stop",
        "short": "stop",
        "category": "control",
        "shape": "cap",
        "message": "stop [STOP_OPTION]",
        "arguments": [
            {
                "name": "STOP_OPTION",
                "menu": "stopOption",
                "options": ["all", "this script", "other scripts"],
                "default": "all",
            }
        ],
        "hubs": ["prime", "essential"],
        "extension": None,
    },
]


ICON_LABELS = {
    "horizontalevents_whenProgramStarts": "when program starts (yellow play)",
    "horizontalevents_whenCloserThan": "when distance is near (the 20 cm preset, as a hat)",
    "horizontalevents_whenColor": "when colour is ...",
    "horizontalevents_whenPressed": "when force sensor is pressed",
    "horizontalevents_whenTilted": "when hub is tilted",
    "horizontalevents_whenBroadcast": "when message received",
    "horizontalevents_broadcast": "broadcast message",
    "horizontalmotor_motorTurnClockwiseRotations": "motor clockwise for N turns",
    "horizontalmotor_motorTurnCounterClockwiseRotations": "motor counterclockwise for N turns",
    "horizontalmotor_motorSetSpeed": "set motor speed",
    "horizontalmotor_motorStop": "stop motor",
    "horizontalmove_moveForward": "move driving base forward",
    "horizontalmove_moveBackward": "move driving base backward",
    "horizontalmove_moveTurnClockwiseRotations": "turn driving base clockwise",
    "horizontalmove_moveTurnCounterClockwiseRotations": "turn driving base counterclockwise",
    "horizontalmove_moveSetSpeed": "set movement speed",
    "horizontalmove_moveStop": "stop moving",
    "horizontaldisplay_ledImage": "show 5x5 image (Prime)",
    "horizontaldisplay_ledMatrix": "show 3x3 colour matrix",
    "horizontaldisplay_ledRandom": "random 5x5 image",
    "horizontaldisplay_ledMatrixRandom": "random 3x3 image",
    "horizontalsound_playAnimalSoundUntilDone": "play animal sound",
    "horizontalsound_playEffectSoundUntilDone": "play effect sound",
    "horizontalsound_playMusicSoundUntilDone": "play music sound",
    "horizontalsound_playRecordedSound": "play recorded sound",
    "horizontalsound_recordSound": "record a sound",
    "horizontalcontrol_stopOtherStacks": "stop other stacks",
}


def icon_shape(opcode: str) -> str:
    if "_when" in opcode:
        return "hat"
    if opcode.endswith("stopOtherStacks"):
        return "cap"
    return "stack"


def hubs_for(short: str, full: str) -> list[str]:
    if short in PRIME_ONLY_SHORT:
        return ["prime"]
    return ["prime", "essential"]


def notes_for(short: str, full: str, args: list[dict]) -> list[str]:
    notes: list[str] = []
    if any(a.get("field") == "MultiplePortSelector" for a in args):
        notes.append(
            "PORT is a multi-select. The app pre-checks every connected motor. "
            "One line can spin the drill and a wheel. Un-tick the ports you "
            "did not mean, or use SingleMotorSelector blocks one port at a time."
        )
    if any(a.get("field") == "MovementPortSelector" for a in args) or short == "setMovementPair":
        notes.append(
            "This names the two motors every flippermove_* block will drive. "
            "The move blocks themselves have no port dropdown."
        )
    if full.startswith("flippermove_") and short != "setMovementPair":
        notes.append(
            "Acts on the pair from set movement motors, not on a port named here. "
            "Without that pair-set block earlier in the stack, the move does nothing useful."
        )
    if short == "isDistance":
        notes.append(
            "BOOLEAN. Does not move the program forward. Drop it inside "
            "'wait until' or 'if then'. Default unit is percent of 200 cm, "
            "default value 15 (≈ 30 cm), not 20 cm."
        )
    if short == "whenDistance":
        notes.append(
            "HAT. Starts its own stack when the condition becomes true. "
            "It does not sit inside forever. Default value is 8, default unit "
            "percent (≈ 16 cm). If you wanted 'when something is close', this "
            "is the right *family*, but wait-until + isDistance is the version "
            "that lives inside a driving loop."
        )
    if short in {"distance"}:
        notes.append("REPORTER oval. A number. Drop it into a compare slot. Unit dropdown: %, cm, inches.")
    if short in ACCESSORY_3X3:
        notes.append(
            "Drives the 3x3 Colour Light Matrix accessory on a port, not the "
            "Prime hub's 5x5. Consumes a port on whichever hub it is plugged into."
        )
    if short.startswith("lightDisplay"):
        notes.append("Drives the Prime hub's built-in 5x5 matrix. Essential has no 5x5.")
    if EXTENSION_BY_PREFIX.get(full.split("_", 1)[0]):
        notes.append(
            "Hidden until you add the matching extension from the bottom of the "
            "palette (the puzzle-piece tray)."
        )
    return notes


SHORT_MESSAGE_PATH = {
    "lightDisplayImageOn": "lights.led_image",
    "lightDisplayImageOnForTime": "lights.led_image_for",
    "lightDisplayOff": "lights.led_off",
    "lightDisplaySetPixel": "lights.led_on",
    "lightDisplayText": "lights.led_text",
    "lightDisplaySetBrightness": "lights.led_set_brightness",
    "lightDisplaySetOrientation": "lights.led_rotate_orientation",
    "lightDisplayRotate": "lights.display_matrix_rotate_direction",
    "lightColorMatrixImageOn": "lights.led_matrix",
    "lightColorMatrixImageOnForTime": "lights.led_matrix_for",
    "lightColorMatrixOff": "lights.led_matrix_off",
    "lightColorMatrixSetPixel": "lights.led_matrix_color",
    "lightColorMatrixSetBrightness": "lights.led_matrix_brightness",
    "lightColorMatrixSetOrientation": "lights.led_matrix_rotate_orientation",
    "lightColorMatrixRotate": "lights.led_matrix_rotate_direction",
    "centerButtonLight": "lights.center_button_light",
    "startMove": "move.startMoveCommand",
    "stopMove": "move.stopMoving",
    "movementSpeed": "move.setMovementSpeed",
    "motorStartDirection": "motor.motorStartClockwise",
    "motorTurnForDirection": "motor.motorTurnForClockwise",
    "motorGoDirectionToPosition": "motor.motorGoDirectionToPosition",
    "motorSetSpeed": "motor.motorSetSpeed",
    "motorStop": "motor.motorStop",
    "setMovementPair": "move.setMovementPair",
    "setDistance": "move.setMovementUnitToDistance",
    "steer": "move.steer",
    "startSteer": "move.startSteer",
    "startDualSpeed": "move.startDualSpeed",
}


def resolve_message(defns_text_key: str | None, key_map: dict[str, str], en_us: dict, short: str) -> str:
    if defns_text_key and defns_text_key in key_map:
        path = key_map[defns_text_key]
        val = lookup_path(en_us, path)
        if isinstance(val, str):
            return val
    if short in SHORT_MESSAGE_PATH:
        val = lookup_path(en_us, SHORT_MESSAGE_PATH[short])
        if isinstance(val, str):
            return val
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", short).lower()
    for root in ("events", "sensors", "motor", "move", "lights", "sound", "control", "operator", "moremotor", "moremove", "moresensors"):
        node = en_us.get(root) if isinstance(en_us, dict) else None
        if not isinstance(node, dict):
            continue
        for key in (short, snake):
            if key in node and isinstance(node[key], str):
                return node[key]
    return short


# ---------------------------------------------------------------------------
# Assemble
# ---------------------------------------------------------------------------


SHADOW_MESSAGE_RE = re.compile(r"^\[[A-Z_0-9]+\]$")


def build_index(index_name: str, index_js: str) -> dict:
    colors = extract_colors(index_js)
    key_map = extract_i18n_key_map(index_js)
    en_us = extract_en_us(index_js)
    definitions = extract_block_definitions(index_js)
    strings = extract_opcode_strings(index_js)
    known = extract_known_opcodes(index_js)
    legacy_mapping, legacy_src = extract_legacy_opcodes(index_js)
    full_ops = strings["standalone"]
    valid = set(full_ops) | set(known)
    icon_ops = extract_icon_opcodes(index_js)

    blocks: dict[str, dict] = {}
    unmapped: list[dict] = []
    shadows: list[dict] = []
    skipped_test = 0
    for order, d in enumerate(definitions):
        if d["short"].startswith("assert") or d["short"] in {"passTest"}:
            skipped_test += 1
            continue
        full = map_short_to_full(d["short"], full_ops, key_map, d["text_key"], valid)
        if not full:
            msg = resolve_message(d["text_key"], key_map, en_us, d["short"])
            unmapped.append(
                {
                    "short": d["short"],
                    "text_key": d["text_key"],
                    "shape_raw": d["shape_raw"],
                    "message": msg,
                    "why": "no opcode in the bundle matches this definition class"
                    + (
                        " — message is a bare argument slot, so this is a dropdown shadow"
                        if SHADOW_MESSAGE_RE.match(msg)
                        else ""
                    ),
                }
            )
            continue
        cat = category_of(full) if "_" in full else "extension"
        prefix = full.split("_", 1)[0]
        msg = resolve_message(d["text_key"], key_map, en_us, d["short"])
        if SHADOW_MESSAGE_RE.match(msg):
            # A whole "block" that is only an argument slot is a dropdown
            # shadow, not something you drag out of the palette.
            shadows.append({"opcode": full, "short": d["short"], "message": msg})
            continue
        entry = {
            "opcode": full,
            "short": d["short"],
            "category": cat,
            "bundle_order": order,
            "shape": shape_of(d["shape_raw"], d["short"], full),
            "shape_contract": "",
            "message": msg,
            "colors": colors.get(cat) or colors.get("extension") or {},
            "arguments": [{k: v for k, v in a.items()} for a in d["arguments"]],
            "is_terminal": d["is_terminal"],
            "hubs": hubs_for(d["short"], full),
            "extension": EXTENSION_BY_PREFIX.get(prefix),
            "python": PYTHON_MAP.get(full),
            "python_prime_only": True,
            "notes": notes_for(d["short"], full, d["arguments"]),
        }
        entry["shape_contract"] = SHAPE_CONTRACT[entry["shape"]]
        if d["short"] in {"startMove", "move"}:
            for a in entry["arguments"]:
                if a.get("name") == "DIRECTION":
                    a["default"] = "forward"
                    a["menu"] = "moveDirection"
                    a["options"] = ["forward", "backward"]
                    a.pop("field", None)
        if not entry["python"]:
            entry.pop("python")
        blocks[entry["opcode"]] = entry

    for i, scratch in enumerate(SCRATCH_BLOCKS):
        s = dict(scratch)
        s["shape_contract"] = SHAPE_CONTRACT[s["shape"]]
        s["is_terminal"] = s["shape"] == "cap"
        s["python_prime_only"] = True
        s["notes"] = s.get("notes") or []
        s["bundle_order"] = 1000 + i
        s["colors"] = colors.get(s["category"]) or {}
        s["scratch_core"] = True
        blocks[s["opcode"]] = s

    icon_blocks = []
    for op in icon_ops:
        icon_blocks.append(
            {
                "opcode": op,
                "category": category_of(op),
                "shape": icon_shape(op),
                "label": ICON_LABELS.get(op, op.split("_", 1)[-1]),
                "pictorial": True,
                "hubs": ["prime", "essential"],
                "notes": [
                    "Icon Blocks are a separate canvas (the app calls it 'doodle' / "
                    "'horizontal'). Tiles, not Scratch-shaped Word Blocks. Definitions "
                    "in the bundle are opcodes plus artwork, not English message templates."
                ],
            }
        )

    categories = []
    order = [
        ("event", "Events"),
        ("control", "Control"),
        ("motor", "Motors"),
        ("movement", "Movement"),
        ("light", "Lights"),
        ("sounds", "Sound"),
        ("sensing", "Sensors"),
        ("operators", "Operators"),
        ("data", "Variables"),
        ("more", "More (extensions)"),
        ("music", "Music"),
        ("weather", "Weather"),
    ]
    for palette_index, (key, label) in enumerate(order):
        categories.append(
            {
                "id": key,
                "label": label,
                "palette_index": palette_index,
                "colors": colors.get(key)
                or colors.get("extension")
                or {"primary": "#00B4AF", "secondary": "#008683", "tertiary": "#005654"},
            }
        )

    menus = {
        "distanceComparator": {
            "closerThan": lookup_path(en_us, "sensors.distanceComparator.closerThan") or "closer than",
            "fartherThan": lookup_path(en_us, "sensors.distanceComparator.fartherThan") or "farther than",
            "exactlyAt": lookup_path(en_us, "sensors.distanceComparator.exactlyAt") or "exactly at",
        },
        "nearOrFar": {
            "near": lookup_path(en_us, "sensors.distancevalues.near") or "near (< 20 cm)",
            "far": lookup_path(en_us, "sensors.distancevalues.far") or "far (> 20 cm)",
            "changed": lookup_path(en_us, "sensors.distancevalues.changed") or "changed",
        },
        "unitDistance": {"percent": "%", "cm": "cm", "inches": "inches"},
    }

    return {
        "source": {
            "app": APP,
            "bundle": index_name,
            "extracted": date.today().isoformat(),
            "note": "Derived index of an interface. Not LEGO artwork, not a dumped PDF.",
        },
        "canvases": ["iconBlocks", "wordBlocks", "python"],
        "python": {
            "hubs": ["prime"],
            "api": "SPIKE 3 MicroPython (hub, motor, motor_pair, distance_sensor, runloop)",
            "retired_api": "from spike import PrimeHub — zero occurrences in the shipped bundle. Tutorials that still teach it are stale.",
            "essential": "The Essential hub has no Python canvas.",
        },
        "hubs": {
            "essential": {
                "ports": ["A", "B"],
                "mode": "streaming",
                "matrix": "none-on-hub; 3x3 colour matrix is a port accessory",
                "speaker": False,
                "python": False,
            },
            "prime": {
                "ports": ["A", "B", "C", "D", "E", "F"],
                "mode": "download",
                "matrix": "built-in 5x5",
                "speaker": True,
                "python": True,
            },
        },
        "shape_contract": SHAPE_CONTRACT,
        "categories": categories,
        "menus": menus,
        "blocks": blocks,
        "icon_blocks": icon_blocks,
        "not_blocks": {
            "note": "Strings that look like opcodes but are not draggable Word Blocks. "
            "Counting them is how you get an inflated block count.",
            "field_names": strings["fields"],
            "phantom_bases": strings["phantom_bases"],
            "test_blocks": strings["test"],
            "dropdown_shadows": shadows,
            "no_definition_class": classify_uncovered(
                strings["standalone"],
                set(blocks),
                set(legacy_src)
                | set(legacy_mapping)
                | set(legacy_mapping.values()),
            ),
        },
        "legacy": {
            "note": "Opcodes the app only keeps so it can rewrite older projects. "
            "They are not in the current palette. flipperdisplay_* is the old "
            "name for today's flipperlight_lightDisplay* family.",
            "migrated_from": legacy_src,
            "opcode_mapping": legacy_mapping,
        },
        "unmapped_definitions": unmapped,
        "stats": {
            # Accounting that has to add up, so a re-extract cannot quietly
            # lose blocks: definition_classes_in_bundle
            #   = from_bundle + test_classes_skipped + unmapped_definitions
            "word_blocks": len(blocks),
            "from_bundle": len(blocks) - len(SCRATCH_BLOCKS),
            "scratch_core_added": len(SCRATCH_BLOCKS),
            "test_classes_skipped": skipped_test,
            "icon_blocks": len(icon_blocks),
            "definition_classes_in_bundle": len(definitions),
            "flipper_strings_in_bundle": len(strings["standalone"])
            + len(strings["test"])
            + len(strings["phantom_bases"]),
            "live_opcode_strings": len(strings["standalone"]),
            "field_names": len(strings["fields"]),
            "phantom_bases": len(strings["phantom_bases"]),
            "app_known_opcode_set": len(known),
            "unmapped_definitions": len(unmapped),
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--from-dir", type=Path, help="directory of already-downloaded JS chunks")
    ap.add_argument("-o", "--output", type=Path, default=OUT)
    args = ap.parse_args()
    index_name, files = load_sources(args.from_dir)
    index_js = files[index_name]
    print(f"parsing {index_name} ({len(index_js)} bytes)")
    index = build_index(index_name, index_js)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")
    print(
        f"wrote {args.output} — "
        f"{index['stats']['word_blocks']} word blocks, "
        f"{index['stats']['icon_blocks']} icon blocks"
    )


if __name__ == "__main__":
    main()
