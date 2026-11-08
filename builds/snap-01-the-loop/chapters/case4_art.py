"""Case 4 talk panels. The drawing is the idea; the kid stands to one side.

The case is two lights side by side: the red light (D10 with the egg) and
the white light (L4), joined by two blue tubes, one along the top and one
along the bottom. Blocks never lie on top of each other; they only meet at
an end snap. Wide panels are a tall film strip, so the drawing sits above
the kid. Hero and zigzag panels keep the drawing where the bubble does not
cover it.
"""

import math

from PIL import Image, ImageDraw

INK = (20, 24, 32, 255)
PALE = (170, 198, 214, 255)
BOLD = (30, 144, 255, 255)
OTHER = (255, 122, 26, 255)
GOLD = (245, 167, 0, 255)
RED = (214, 40, 40, 255)
DARK_RED = (96, 40, 44, 255)
GREEN = (18, 92, 62, 255)
CHECK = (46, 158, 91, 255)
WOOD = (92, 58, 28, 255)
WHITE = (255, 255, 255, 255)
GREY = (78, 82, 92, 255)
CLEAR = (214, 230, 240, 255)
AMBER = (242, 182, 50, 255)
BLUE = (36, 104, 196, 255)
ORANGE = (232, 118, 42, 255)
SNAP = (226, 230, 234, 255)


def _overlay(scene):
    ov = Image.new("RGBA", scene.size, (0, 0, 0, 0))
    return ov, ImageDraw.Draw(ov)


def _board(d, box):
    d.rounded_rectangle(box, radius=28, fill=GREEN, outline=WOOD, width=10)


def _arrow(d, x0, y0, x1, y1, color, thick):
    """Flat arrow. The head sits on (x1, y1)."""
    ang = math.atan2(y1 - y0, x1 - x0)
    head = thick * 2.3
    sx = x1 - math.cos(ang) * head * 0.45
    sy = y1 - math.sin(ang) * head * 0.45
    px, py = math.sin(ang) * thick / 2, -math.cos(ang) * thick / 2
    d.polygon([(x0 + px, y0 + py), (sx + px, sy + py), (sx - px, sy - py), (x0 - px, y0 - py)], fill=color)
    left = (x1 - head * math.cos(ang - 0.42), y1 - head * math.sin(ang - 0.42))
    right = (x1 - head * math.cos(ang + 0.42), y1 - head * math.sin(ang + 0.42))
    d.polygon([(x1, y1), left, right], fill=color)


def _snap(d, cx, cy, r):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=SNAP, outline=INK, width=max(3, int(r / 4)))


def _white_light(d, cx, cy, r, on=True):
    """L4: a clear block's round lens. Lit, a white light with gold rays."""
    if on:
        for i in range(8):
            a = math.radians(i * 45 + 22)
            d.line([(cx + math.cos(a) * r * 1.25, cy + math.sin(a) * r * 1.25),
                    (cx + math.cos(a) * r * 1.85, cy + math.sin(a) * r * 1.85)],
                   fill=GOLD, width=max(6, int(r / 5)))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WHITE, outline=(120, 150, 175, 255), width=max(5, int(r / 7)))
        d.ellipse((cx - r * 0.5, cy - r * 0.55, cx - r * 0.1, cy - r * 0.15), fill=(255, 250, 225, 255))
    else:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GREY, outline=INK, width=max(5, int(r / 7)))


def _red_light(d, cx, cy, r, on=True):
    """D10 under the egg, the red way round."""
    if on:
        d.ellipse((cx - r * 1.35, cy - r * 1.35, cx + r * 1.35, cy + r * 1.35), fill=(255, 120, 110, 110))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=RED if on else DARK_RED, outline=INK, width=max(5, int(r / 7)))
    if on:
        d.ellipse((cx - r * 0.5, cy - r * 0.55, cx - r * 0.1, cy - r * 0.15), fill=(255, 170, 160, 255))


def _block(d, box, fill, snaps=True):
    """A 1x3 block standing up: snaps at the two ends, none in the middle."""
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=int((x1 - x0) * 0.3), fill=fill, outline=INK, width=6)
    if snaps:
        r = (x1 - x0) * 0.2
        cx = (x0 + x1) / 2
        _snap(d, cx, y0 + (x1 - x0) * 0.45, r)
        _snap(d, cx, y1 - (x1 - x0) * 0.45, r)


def _tube(d, x0, y, x1, thick):
    d.rounded_rectangle((x0, y - thick / 2, x1, y + thick / 2), radius=thick / 2, fill=BLUE, outline=INK, width=5)
    d.line([(x0 + thick * 0.5, y), (x1 - thick * 0.5, y)], fill=(235, 244, 255, 255), width=max(3, int(thick / 6)))


def _ladder(d, x0, y0, x1, y1, red_on=True, white_on=True, lift_top=False):
    """The Case 4 board in short: the red light on the left, the white light
    on the right, a tube along the top and one along the bottom."""
    bw = (x1 - x0) * 0.2
    lx, rx = x0 + bw * 0.5, x1 - bw * 0.5
    _block(d, (lx - bw / 2, y0, lx + bw / 2, y1), AMBER)
    _block(d, (rx - bw / 2, y0, rx + bw / 2, y1), CLEAR)
    top, bot = y0 + bw * 0.45, y1 - bw * 0.45
    thick = bw * 0.55
    _tube(d, lx, bot, rx, thick)
    if lift_top:
        # the top tube pulled off its snaps, lifted clear of the board
        lift = (y1 - y0) * 0.22
        _tube(d, lx + bw * 0.6, top - lift, rx + bw * 0.6, thick)
        _arrow(d, (lx + rx) / 2 + bw, top - lift * 0.15, (lx + rx) / 2 + bw, top - lift * 0.75, OTHER, max(8, int(thick * 0.45)))
    else:
        _tube(d, lx, top, rx, thick)
    mid = (y0 + y1) / 2
    _red_light(d, lx, mid, bw * 0.95, red_on)
    _white_light(d, rx, mid, bw * 0.55, white_on)


def _gate(d, box, open_=True):
    d.rounded_rectangle(box, radius=14, fill=(15, 122, 50, 255) if open_ else (255, 247, 237, 255), outline=INK, width=6)
    x0, y0, x1, y1 = box
    if not open_:
        mid = (y0 + y1) / 2
        d.rectangle((x0 + 8, mid - 8, x1 - 8, mid + 8), fill=OTHER)


def _cross(d, cx, cy, r, thick):
    d.line([(cx - r, cy - r), (cx + r, cy + r)], fill=RED, width=thick)
    d.line([(cx - r, cy + r), (cx + r, cy - r)], fill=RED, width=thick)


def _tick(d, cx, cy, r, thick):
    d.line([(cx - r, cy), (cx - r * 0.25, cy + r * 0.7), (cx + r, cy - r * 0.7)], fill=CHECK, width=thick, joint="curve")


def _round_arrow(d, cx, cy, rx, ry, start, sweep, color, thick):
    """An oval arrow. Clock degrees: 0 is 12, positive sweep is clockwise."""
    steps = max(16, int(abs(sweep) / 6))
    pts = []
    for i in range(steps + 1):
        a = math.radians(start + sweep * i / steps - 90)
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    d.line(pts, fill=color, width=thick)
    end, prev = pts[-1], pts[max(0, len(pts) - 4)]
    ang = math.atan2(end[1] - prev[1], end[0] - prev[0])
    head = thick * 2.4
    d.polygon([end,
               (end[0] - head * math.cos(ang - 0.45), end[1] - head * math.sin(ang - 0.45)),
               (end[0] - head * math.cos(ang + 0.45), end[1] - head * math.sin(ang + 0.45))], fill=color)


def paint_two_show(scene):
    """The show: a white light for the ramp and the red light for the start line."""
    w, h = scene.size
    ov, d = _overlay(scene)
    _board(d, (int(w * 0.08), int(h * 0.06), int(w * 0.92), int(h * 0.42)))
    _white_light(d, w * 0.32, h * 0.22, h * 0.08, True)
    _red_light(d, w * 0.68, h * 0.22, h * 0.09, True)
    return Image.alpha_composite(scene, ov)


def paint_stack_try(scene):
    """Pip's guess: lay the white light right on top of the red one. It won't sit."""
    w, h = scene.size
    ov, d = _overlay(scene)
    _board(d, (int(w * 0.06), int(h * 0.04), int(w * 0.94), int(h * 0.44)))
    bw = w * 0.22
    cx = w * 0.42
    _block(d, (cx - bw / 2, h * 0.08, cx + bw / 2, h * 0.40), AMBER)
    scene = Image.alpha_composite(scene, ov)
    tile = Image.new("RGBA", (int(bw * 1.1), int(h * 0.34)), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    _block(td, (4, 4, bw, h * 0.32), CLEAR)
    _white_light(td, bw / 2 + 2, h * 0.16, bw * 0.28, False)
    tile = tile.rotate(-24, expand=True, resample=Image.Resampling.BICUBIC)
    ov2 = Image.new("RGBA", scene.size, (0, 0, 0, 0))
    ov2.paste(tile, (int(cx - tile.width / 2 + w * 0.06), int(h * 0.05)), tile)
    scene = Image.alpha_composite(scene, ov2)
    ov, d = _overlay(scene)
    _cross(d, w * 0.80, h * 0.12, w * 0.07, max(10, int(w / 36)))
    return Image.alpha_composite(scene, ov)


def paint_end_snaps(scene):
    """Two blocks meet at one end snap and leave it in different directions."""
    w, h = scene.size
    ov, d = _overlay(scene)
    _board(d, (int(w * 0.06), int(h * 0.04), int(w * 0.94), int(h * 0.48)))
    bw = w * 0.16
    x, y0, y1 = w * 0.30, h * 0.08, h * 0.40
    _block(d, (x - bw / 2, y0, x + bw / 2, y1), AMBER)
    sy = y1 - bw * 0.45
    _tube(d, x, sy, w * 0.84, bw * 0.6)
    _snap(d, x, sy, bw * 0.24)
    _snap(d, w * 0.84 - bw * 0.1, sy, bw * 0.2)
    d.ellipse((x - bw * 0.55, sy - bw * 0.55, x + bw * 0.55, sy + bw * 0.55), outline=OTHER, width=max(6, int(w / 90)))
    _tick(d, w * 0.70, h * 0.17, w * 0.08, max(10, int(w / 36)))
    return Image.alpha_composite(scene, ov)


def paint_next_door(scene):
    """The white light next door, joined to the red one by a tube at each end."""
    w, h = scene.size
    ov, d = _overlay(scene)
    _board(d, (int(w * 0.06), int(h * 0.04), int(w * 0.94), int(h * 0.44)))
    _ladder(d, w * 0.14, h * 0.07, w * 0.86, h * 0.41)
    return Image.alpha_composite(scene, ov)


def paint_gate_off(scene):
    """Gate shut. Both lights dark."""
    w, h = scene.size
    ov, d = _overlay(scene)
    _gate(d, (w * 0.08, h * 0.08, w * 0.28, h * 0.42), open_=False)
    _red_light(d, w * 0.52, h * 0.22, h * 0.11, on=False)
    _white_light(d, w * 0.78, h * 0.22, h * 0.09, on=False)
    return Image.alpha_composite(scene, ov)


def paint_split(scene):
    """Gate open, then the water splits toward two lights."""
    w, h = scene.size
    ov, d = _overlay(scene)
    _gate(d, (w * 0.06, h * 0.10, w * 0.22, h * 0.42), open_=True)
    _arrow(d, w * 0.24, h * 0.26, w * 0.40, h * 0.26, BOLD, max(10, w // 40))
    _arrow(d, w * 0.40, h * 0.26, w * 0.58, h * 0.14, BOLD, max(8, w // 50))
    _arrow(d, w * 0.40, h * 0.26, w * 0.58, h * 0.38, BOLD, max(8, w // 50))
    _white_light(d, w * 0.72, h * 0.14, h * 0.07, True)
    _red_light(d, w * 0.72, h * 0.40, h * 0.09, True)
    return Image.alpha_composite(scene, ov)


def paint_pull_tube(scene):
    """Top tube pulled off: the white light goes dark, the red one stays on."""
    w, h = scene.size
    ov, d = _overlay(scene)
    _ladder(d, w * 0.10, h * 0.20, w * 0.56, h * 0.68, red_on=True, white_on=False, lift_top=True)
    return Image.alpha_composite(scene, ov)


def paint_one_gate(scene):
    """Short banner: one gate, two lights."""
    w, h = scene.size
    ov, d = _overlay(scene)
    _gate(d, (w * 0.04, h * 0.15, w * 0.18, h * 0.80), open_=True)
    _arrow(d, w * 0.20, h * 0.48, w * 0.30, h * 0.48, BOLD, max(10, int(h / 10)))
    _red_light(d, w * 0.42, h * 0.48, h * 0.26, True)
    _white_light(d, w * 0.64, h * 0.48, h * 0.2, True)
    return Image.alpha_composite(scene, ov)


def paint_gate_first(scene):
    """The gate, then both lights."""
    w, h = scene.size
    ov, d = _overlay(scene)
    _board(d, (int(w * 0.28), int(h * 0.04), int(w * 0.98), int(h * 0.62)))
    _gate(d, (w * 0.34, h * 0.16, w * 0.48, h * 0.46), open_=True)
    _arrow(d, w * 0.50, h * 0.30, w * 0.62, h * 0.30, BOLD, max(10, int(h / 28)))
    _white_light(d, w * 0.74, h * 0.20, h * 0.08, True)
    _red_light(d, w * 0.88, h * 0.40, h * 0.10, True)
    return Image.alpha_composite(scene, ov)


def paint_split_after(scene):
    """After the gate the arrows fork."""
    w, h = scene.size
    ov, d = _overlay(scene)
    _gate(d, (w * 0.42, h * 0.08, w * 0.58, h * 0.36), open_=True)
    _arrow(d, w * 0.58, h * 0.22, w * 0.70, h * 0.12, BOLD, max(8, int(h / 30)))
    _arrow(d, w * 0.58, h * 0.22, w * 0.70, h * 0.34, BOLD, max(8, int(h / 30)))
    _white_light(d, w * 0.84, h * 0.12, h * 0.06, True)
    _red_light(d, w * 0.84, h * 0.36, h * 0.08, True)
    return Image.alpha_composite(scene, ov)


def paint_two_circles(scene):
    """Two circles share the pump: a small one through the red light, a big
    one through the white light."""
    w, h = scene.size
    ov, d = _overlay(scene)
    _board(d, (int(w * 0.30), int(h * 0.04), int(w * 0.98), int(h * 0.64)))
    cy = h * 0.34
    d.rounded_rectangle((w * 0.33, cy - h * 0.10, w * 0.41, cy + h * 0.10), radius=10, fill=ORANGE, outline=INK, width=5)
    thick = max(8, int(h / 40))
    _round_arrow(d, w * 0.50, cy, w * 0.13, h * 0.20, 200, 300, BOLD, thick)
    _round_arrow(d, w * 0.66, cy, w * 0.29, h * 0.27, 210, 290, OTHER, thick)
    _red_light(d, w * 0.62, cy, h * 0.07, True)
    _white_light(d, w * 0.92, cy, h * 0.05, True)
    return Image.alpha_composite(scene, ov)


def paint_gate_shut(scene):
    """Shut gate, both lights out."""
    w, h = scene.size
    ov, d = _overlay(scene)
    _gate(d, (w * 0.08, h * 0.12, w * 0.24, h * 0.48), open_=False)
    _red_light(d, w * 0.46, h * 0.28, h * 0.12, on=False)
    _white_light(d, w * 0.70, h * 0.28, h * 0.10, on=False)
    return Image.alpha_composite(scene, ov)


def add(save):
    # Tall film strip. The kid stands under the drawing, a little off center,
    # small enough that the bench still shows above his head.
    save("c4-01-1.jpg", "glow", ["sully-notice"], (900, 1600), [(0.62, 0.56)], (0.32, 0.42), paint_two_show)
    save("c4-01-2.jpg", "glow", ["pip-oops"], (620, 1700), [(0.50, 0.50)], (0.70, 0.38), paint_stack_try)
    save("c4-01-3.jpg", "glow", ["tika-ask"], (900, 1600), [(0.36, 0.54)], (0.48, 0.50), paint_end_snaps)
    save("c4-01-4.jpg", "glow", ["coco-explain"], (620, 1700), [(0.50, 0.44)], (0.58, 0.36), paint_next_door)

    save("c4-02-1.jpg", "chalk", ["tika-write"], (1400, 1040), [(0.24, 0.70)], (0.46, 0.42), paint_gate_off)
    save("c4-02-2.jpg", "chalk", ["pip-cheer"], (1000, 570), [(0.22, 0.70)], (0.52, 0.40), paint_split)
    save("c4-02-3.jpg", "chalk", ["sully-notice"], (1000, 470), [(0.80, 0.70)], (0.40, 0.40), paint_pull_tube)
    save("c4-02-4.jpg", "chalk", ["coco-goggles"], (1900, 300), [(0.88, 0.90)], (0.50, 0.36), paint_one_gate)

    save("c4-03-1.jpg", "chalk", ["coco-explain"], (1500, 760), [(0.18, 0.70)], (0.42, 0.44), paint_gate_first)
    save("c4-03-2.jpg", "chalk", ["pip-magnify"], (900, 780), [(0.26, 0.56)], (0.55, 0.42), paint_split_after)
    save("c4-03-3.jpg", "chalk", ["tika-write"], (860, 680), [(0.24, 0.66)], (0.48, 0.46), paint_two_circles)
    save("c4-03-4.jpg", "chalk", ["sully-notice"], (1550, 660), [(0.84, 0.70)], (0.62, 0.40), paint_gate_shut)
