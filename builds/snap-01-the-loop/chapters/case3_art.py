"""Case 3 talk pictures. Each save() is one panel of the horn case.

The paint shows the idea in that panel's bubble: a horn that works one way,
or a button that is on only while a finger holds it. No words in the picture.
The character is pasted after paint, so the drawing stays on the open side.
"""

from __future__ import annotations

import math

from PIL import Image, ImageDraw

INK = (20, 24, 32, 255)
RED = (214, 40, 40, 255)
RED_FILL = (226, 61, 61, 255)
YELLOW = (255, 212, 59, 255)
BLUE = (30, 144, 255, 255)
WHITE = (255, 255, 255, 255)
CYAN = (86, 204, 242, 255)
GREEN = (31, 138, 76, 255)
ORANGE = (255, 122, 26, 255)
SKIN = (255, 186, 120, 255)
NAIL = (255, 220, 186, 255)
CREAM = (236, 244, 250, 255)
BOARD = (18, 92, 62, 255)
WOOD = (92, 58, 28, 255)
DARK = (12, 40, 24, 255)


def _canvas(scene: Image.Image):
    w, h = scene.size
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return w, h, ov, ImageDraw.Draw(ov)


def _finish(scene: Image.Image, ov: Image.Image) -> Image.Image:
    return Image.alpha_composite(scene, ov)


def _box(w, h, x0, y0, x1, y1):
    return (int(w * x0), int(h * y0), int(w * x1), int(h * y1))


def _card(d, box):
    x0, y0, x1, y1 = box
    if x1 - x0 < 24 or y1 - y0 < 24:
        return
    rad = min(28, (x1 - x0) // 6, (y1 - y0) // 6)
    thick = max(6, min(x1 - x0, y1 - y0) // 36)
    d.rounded_rectangle((x0, y0, x1, y1), radius=rad, fill=BOARD, outline=WOOD, width=thick)


def _plus(d, cx, cy, size):
    t = max(6, size // 4)
    d.rectangle((cx - t // 2, cy - size // 2, cx + t // 2, cy + size // 2), fill=RED)
    d.rectangle((cx - size // 2, cy - t // 2, cx + size // 2, cy + t // 2), fill=RED)


def _badge(d, cx, cy, r):
    r = max(8, r)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WHITE, outline=RED, width=max(4, r // 5))
    _plus(d, cx, cy, int(r * 1.25))


def _arrow(d, x0, x1, y, color, thick):
    """Horizontal arrow. The head is at x1."""
    thick = max(6, thick)
    head = thick * 2
    if abs(x1 - x0) < head + 4:
        return
    if x1 > x0:
        d.rectangle((x0, y - thick // 2, x1 - head + 2, y + thick // 2), fill=color)
        d.polygon([(x1, y), (x1 - head, y - head // 2), (x1 - head, y + head // 2)], fill=color)
    else:
        d.rectangle((x1 + head - 2, y - thick // 2, x0, y + thick // 2), fill=color)
        d.polygon([(x1, y), (x1 + head, y - head // 2), (x1 + head, y + head // 2)], fill=color)


def _varrow(d, x, y0, y1, color, thick):
    """Vertical arrow. The head is at y1."""
    thick = max(6, thick)
    head = thick * 2
    if abs(y1 - y0) < head + 4:
        return
    if y1 > y0:
        d.rectangle((x - thick // 2, y0, x + thick // 2, y1 - head + 2), fill=color)
        d.polygon([(x, y1), (x - head // 2, y1 - head), (x + head // 2, y1 - head)], fill=color)
    else:
        d.rectangle((x - thick // 2, y1 + head - 2, x + thick // 2, y0), fill=color)
        d.polygon([(x, y1), (x - head // 2, y1 + head), (x + head // 2, y1 + head)], fill=color)


def _nosound(d, cx, cy, r):
    r = max(12, r)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=RED, width=max(5, r // 5))
    d.line((cx - int(r * 0.7), cy + int(r * 0.7), cx + int(r * 0.7), cy - int(r * 0.7)), fill=RED, width=max(5, r // 5))


def _sound(d, cx, cy, r, thick):
    for i in range(3):
        rr = r + thick + i * (thick + 4)
        d.arc((cx - rr, cy - rr, cx + rr, cy + rr), 300, 60, fill=YELLOW, width=thick)


def _horn(d, x, y, bw, bh, plus_at=None, loud=False, shut=False, quiet=False):
    """A round buzzer, not a tall blue rectangle. plus_at is 'top' or 'bottom'."""
    bw, bh = max(48, bw), max(48, bh)
    cx, cy = x + bw // 2, y + bh // 2
    r = max(16, min(bw, bh) // 2 - 6)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(232, 236, 240, 255), outline=INK, width=max(5, r // 8))
    d.ellipse((cx - int(r * 0.72), cy - int(r * 0.72), cx + int(r * 0.72), cy + int(r * 0.72)), fill=CYAN, outline=INK, width=max(4, r // 10))
    d.ellipse((cx - int(r * 0.28), cy - int(r * 0.28), cx + int(r * 0.28), cy + int(r * 0.28)), fill=INK)
    if shut:
        bar = max(8, r // 3)
        d.rectangle((cx - r, cy - bar // 2, cx + r, cy + bar // 2), fill=RED_FILL, outline=INK, width=3)
    elif loud:
        _sound(d, cx + int(r * 0.2), cy, max(8, r // 3), max(4, r // 8))
    elif quiet:
        _nosound(d, cx + int(r * 1.15), cy, max(14, int(r * 0.55)))
    if plus_at == "top":
        _badge(d, cx, cy - int(r * 0.55), max(12, int(r * 0.38)))
    elif plus_at == "bottom":
        _badge(d, cx, cy + int(r * 0.55), max(12, int(r * 0.38)))


def _colour_block(d, x, y, bw, bh, plus_at):
    """Red/yellow light. The red half is the end with the +."""
    rad = min(16, bw // 5)
    d.rounded_rectangle((x, y, x + bw, y + bh), radius=rad, fill=YELLOW, outline=INK, width=max(4, bw // 14))
    mid = y + bh // 2
    if plus_at == "top":
        d.rectangle((x + 5, y + 5, x + bw - 5, mid), fill=RED_FILL)
        py = y + int(bh * 0.22)
    else:
        d.rectangle((x + 5, mid, x + bw - 5, y + bh - 5), fill=RED_FILL)
        py = y + int(bh * 0.78)
    d.rounded_rectangle((x, y, x + bw, y + bh), radius=rad, outline=INK, width=max(4, bw // 14))
    _badge(d, x + bw // 2, py, max(10, int(min(bw, bh) * 0.16)))


def _finger(d, x, y, fw, fh):
    """A finger pointing down. (x, y) is the top-left."""
    fw, fh = max(18, fw), max(36, fh)
    d.rounded_rectangle((x, y, x + fw, y + fh), radius=fw // 2, fill=SKIN, outline=INK, width=max(4, fw // 8))
    d.ellipse(
        (x + int(fw * 0.22), y + int(fh * 0.62), x + int(fw * 0.78), y + int(fh * 0.90)),
        fill=NAIL,
        outline=INK,
        width=3,
    )


def _button(d, cx, cy, r, down):
    """A press button. cy is the top of the base. The red cap stays on that base.

    Returns the y of the top of the cap, so a finger or a spring can meet it.
    """
    r = max(18, r)
    stroke = max(4, r // 7)
    base_h = int(r * 0.78)
    d.rounded_rectangle(
        (cx - r, cy, cx + r, cy + base_h),
        radius=max(8, r // 3),
        fill=DARK,
        outline=INK,
        width=stroke,
    )
    cap_w = int(r * 0.80)
    cap_h = int(r * 0.42)
    # Share of the cap that sits down inside the base. Up still overlaps.
    inside = 0.70 if down else 0.42
    bottom = cy + int(2 * cap_h * inside)
    top = bottom - 2 * cap_h
    d.ellipse((cx - cap_w, top, cx + cap_w, bottom), fill=RED_FILL, outline=INK, width=stroke)
    return top


def _spring(d, cx, y0, y1, thick):
    """Round coils. A zigzag read as the word DOWN."""
    n = 5
    span = max(1, y1 - y0)
    rh = span / n
    rw = max(14, thick * 3)
    stroke = max(5, thick)
    for i in range(n):
        yy = y0 + i * rh
        d.arc((cx - rw, yy, cx + rw, yy + rh * 1.35), 200, 20, fill=ORANGE, width=stroke)


def _slide(d, x, y, sw, sh):
    """A slide switch with the lever parked at the right. It stays there."""
    d.rounded_rectangle((x, y, x + sw, y + sh), radius=sh // 3, fill=GREEN, outline=INK, width=max(4, sh // 10))
    d.rounded_rectangle(
        (x + int(sw * 0.12), y + int(sh * 0.30), x + int(sw * 0.88), y + int(sh * 0.70)),
        radius=sh // 5,
        fill=DARK,
    )
    kx = x + int(sw * 0.74)
    kr = max(10, int(sh * 0.32))
    d.rectangle((kx - kr // 4, y - int(sh * 0.45), kx + kr // 4, y + sh // 2), fill=YELLOW, outline=INK, width=4)
    d.ellipse((kx - kr, y + sh // 2 - kr, kx + kr, y + sh // 2 + kr), fill=YELLOW, outline=INK, width=4)


def _flap_shut(d, x, y0, y1, thick):
    d.rectangle((x - thick // 2, y0, x + thick // 2, y1), fill=RED_FILL, outline=INK, width=4)


def _flap_open(d, x, y0, y1):
    """A yellow flap swung up, so the tube is clear."""
    reach = max(16, (y1 - y0) // 2)
    d.polygon([(x, y1 - 6), (x - 6, y0), (x + reach, y0)], fill=YELLOW, outline=INK)


def _tube(d, box, thick):
    x0, y0, x1, y1 = box
    rad = min(24, (y1 - y0) // 2)
    d.rounded_rectangle(box, radius=rad, fill=CREAM, outline=INK, width=thick)


def _head(d, cx, cy, r, ang, color, size):
    """Arrowhead on a circle, pointing clockwise. ang is PIL degrees."""
    a = math.radians(ang)
    px = cx + r * math.cos(a)
    py = cy + r * math.sin(a)
    tx, ty = -math.sin(a), math.cos(a)
    nx, ny = math.cos(a), math.sin(a)
    d.polygon(
        [
            (px, py),
            (px - tx * size + nx * size * 0.55, py - ty * size + ny * size * 0.55),
            (px - tx * size - nx * size * 0.55, py - ty * size - ny * size * 0.55),
        ],
        fill=color,
    )


def _ring(d, cx, cy, r, start, end, color, width, heads):
    d.arc((cx - r, cy - r, cx + r, cy + r), start, end, fill=color, width=width)
    for ang in heads:
        _head(d, cx, cy, r, ang, color, width * 2.2)


def _glass(d, cx, cy, r):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=BLUE, width=max(6, r // 7))
    d.ellipse((cx - int(r * 0.72), cy - int(r * 0.72), cx + int(r * 0.72), cy + int(r * 0.72)), outline=WHITE, width=max(3, r // 12))
    d.line((cx + int(r * 0.7), cy + int(r * 0.7), cx + int(r * 1.7), cy + int(r * 1.7)), fill=INK, width=max(8, r // 5))


# --- panels ---------------------------------------------------------------
# Safe zones match the slots in add(): the drawing stays off the character,
# and on short panels it stays in the top ~60% (the bubble covers the rest).


def paint_quiet_horn(scene: Image.Image) -> Image.Image:
    """Maybe the horn is just broken: a horn with no sound."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.46, 0.06, 0.94, 0.58))
    _horn(d, int(w * 0.62), int(h * 0.12), int(w * 0.16), int(h * 0.40), plus_at=None, quiet=True)
    return _finish(scene, ov)


def paint_press_nothing(scene: Image.Image) -> Image.Image:
    """Pressed and pressed, still nothing: finger down on the button, horn silent."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.04, 0.06, 0.64, 0.60))
    r = int(h * 0.11)
    cx = int(w * 0.18)
    top = _button(d, cx, int(h * 0.36), r, down=True)
    fw, fh = int(w * 0.08), int(h * 0.24)
    _finger(d, cx - fw // 2, top - fh + 8, fw, fh)
    _horn(d, int(w * 0.38), int(h * 0.14), int(w * 0.16), int(h * 0.40), plus_at=None, quiet=True)
    return _finish(scene, ov)


def paint_hunt_clues(scene: Image.Image) -> Image.Image:
    """Hunt for clues: a glass beside the button, and a horn with a +."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.03, 0.05, 0.66, 0.62))
    _button(d, int(w * 0.16), int(h * 0.40), int(h * 0.11), down=False)
    _glass(d, int(w * 0.16), int(h * 0.28), int(h * 0.11))
    _horn(d, int(w * 0.36), int(h * 0.12), int(w * 0.18), int(h * 0.44), plus_at="bottom")
    return _finish(scene, ov)


def paint_two_clues(scene: Image.Image) -> Image.Image:
    """The button, and which way the horn sits: a + on one end."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.18, 0.06, 0.78, 0.64))
    _button(d, int(w * 0.32), int(h * 0.40), int(h * 0.16), down=False)
    _horn(d, int(w * 0.48), int(h * 0.10), int(h * 0.50), int(h * 0.50), plus_at="bottom")
    return _finish(scene, ov)


def paint_slide_stays(scene: Image.Image) -> Image.Image:
    """The Slide Gate stays where you leave it: lever parked, water still through."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.40, 0.06, 0.96, 0.64))
    _slide(d, int(w * 0.52), int(h * 0.14), int(w * 0.28), int(h * 0.16))
    y0, y1 = int(h * 0.40), int(h * 0.56)
    _tube(d, (int(w * 0.48), y0, int(w * 0.90), y1), max(6, h // 50))
    _flap_open(d, int(w * 0.62), y0 + 8, y1 - 8)
    _arrow(d, int(w * 0.52), int(w * 0.84), (y0 + y1) // 2, BLUE, max(10, h // 28))
    return _finish(scene, ov)


def paint_spring_up(scene: Image.Image) -> Image.Image:
    """The button pops back up: finger off, spring under the cap, arrow up."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.04, 0.05, 0.36, 0.82))
    cx = int(w * 0.16)
    top = _button(d, cx, int(h * 0.64), int(w * 0.07), down=False)
    _spring(d, cx, int(h * 0.28), top - 8, max(6, w // 48))
    fw, fh = int(w * 0.09), int(h * 0.12)
    _finger(d, cx - fw // 2, int(h * 0.06), fw, fh)
    _varrow(d, cx + int(w * 0.10), int(h * 0.30), int(h * 0.10), BLUE, max(10, w // 40))
    return _finish(scene, ov)


def paint_hold_open(scene: Image.Image) -> Image.Image:
    """Open only while a finger holds it: finger down, flap open, water through."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.50, 0.06, 0.97, 0.66))
    y0, y1 = int(h * 0.40), int(h * 0.58)
    _tube(d, (int(w * 0.54), y0, int(w * 0.94), y1), max(6, h // 40))
    _flap_open(d, int(w * 0.70), y0 + 6, y1 - 6)
    _arrow(d, int(w * 0.58), int(w * 0.90), (y0 + y1) // 2, BLUE, max(10, h // 26))
    fw, fh = int(w * 0.09), int(h * 0.30)
    _finger(d, int(w * 0.64), y0 - fh + 12, fw, fh)
    return _finish(scene, ov)


def paint_plus_like_light(scene: Image.Image) -> Image.Image:
    """The horn has a plus, like the colour light: both blocks marked on one end."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.03, 0.06, 0.64, 0.60))
    bh = int(h * 0.46)
    bw = int(h * 0.22)
    y = int(h * 0.10)
    _colour_block(d, int(w * 0.10), y, bw, bh, "bottom")
    _horn(d, int(w * 0.36), y, bw, bh, plus_at="bottom", loud=True)
    return _finish(scene, ov)


def paint_stays_quiet(scene: Image.Image) -> Image.Image:
    """This one stays quiet: the flap shuts the tube, and the horn makes no sound."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.28, 0.06, 0.94, 0.60))
    y0, y1 = int(h * 0.30), int(h * 0.50)
    flap_x = int(w * 0.62)
    _tube(d, (int(w * 0.34), y0, flap_x + 14, y1), max(6, h // 36))
    _flap_shut(d, flap_x, y0 + 6, y1 - 6, max(22, h // 14))
    _arrow(d, int(w * 0.38), flap_x - int(w * 0.04), (y0 + y1) // 2, BLUE, max(10, h // 24))
    _horn(d, flap_x + int(w * 0.03), int(h * 0.16), int(h * 0.34), int(h * 0.40), plus_at=None, quiet=True)
    return _finish(scene, ov)


def paint_colour_wrong(scene: Image.Image) -> Image.Image:
    """The colour light looked broken: the + is on the other end, water hits it."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.04, 0.06, 0.54, 0.78))
    x, y = int(w * 0.22), int(h * 0.12)
    bw, bh = int(w * 0.20), int(h * 0.58)
    _colour_block(d, x, y, bw, bh, "top")
    _arrow(d, int(w * 0.06), x - 8, y + int(bh * 0.78), BLUE, max(12, h // 28))
    return _finish(scene, ov)


def paint_we_turned_it(scene: Image.Image) -> Image.Image:
    """The plus was the wrong way: turn the block so the + moves to the bottom."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.03, 0.05, 0.54, 0.80))
    bw, bh = int(w * 0.16), int(h * 0.42)
    y = int(h * 0.28)
    _colour_block(d, int(w * 0.06), y, bw, bh, "top")
    _colour_block(d, int(w * 0.34), y, bw, bh, "bottom")
    arc_box = (int(w * 0.08), int(h * 0.06), int(w * 0.48), int(h * 0.42))
    d.arc(arc_box, 200, 340, fill=BLUE, width=max(8, h // 40))
    _head(d, (arc_box[0] + arc_box[2]) // 2, (arc_box[1] + arc_box[3]) // 2, (arc_box[2] - arc_box[0]) // 2, 330, BLUE, max(16, h // 22))
    return _finish(scene, ov)


def paint_plus_on_top(scene: Image.Image) -> Image.Image:
    """Where did Pip put the plus? On the top end of the horn."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.50, 0.05, 0.96, 0.78))
    _horn(d, int(w * 0.64), int(h * 0.10), int(w * 0.20), int(h * 0.62), plus_at="top", loud=False, shut=True)
    return _finish(scene, ov)


def paint_shut_flap(scene: Image.Image) -> Image.Image:
    """Backwards, the flap stays shut. No water gets through."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.04, 0.04, 0.92, 0.36))
    y0, y1 = int(h * 0.12), int(h * 0.28)
    _tube(d, (int(w * 0.08), y0, int(w * 0.62), y1), max(8, h // 60))
    flap_x = int(w * 0.40)
    _flap_shut(d, flap_x, y0 + 10, y1 - 10, max(14, h // 40))
    _arrow(d, int(w * 0.12), flap_x - int(w * 0.04), (y0 + y1) // 2, BLUE, max(12, h // 40))
    _horn(d, int(w * 0.66), int(h * 0.07), int(w * 0.16), int(h * 0.26), plus_at="top", loud=False, shut=True)
    return _finish(scene, ov)


def paint_water_still(scene: Image.Image) -> Image.Image:
    """Pip's guess: the horn is quiet and outside, but the circle of water still moves."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.56, 0.04, 0.97, 0.62))
    cx, cy, r = int(w * 0.68), int(h * 0.28), int(h * 0.15)
    thick = max(14, h // 36)
    _ring(d, cx, cy, r, 0, 359, BLUE, thick, (20, 110, 200, 290))
    hx = cx + r + int(h * 0.09)
    _horn(d, hx, cy - int(h * 0.10), int(w * 0.075), int(h * 0.22), plus_at="top", quiet=True)
    return _finish(scene, ov)


def paint_horn_in_circle(scene: Image.Image) -> Image.Image:
    """The horn sits in the circle. The loop has to go through it."""
    w, h, ov, d = _canvas(scene)
    # The card covers the chalkboard's own loop, so only this circle is the idea.
    _card(d, _box(w, h, 0.02, 0.00, 0.68, 1.00))
    cx, cy, r = int(w * 0.28), int(h * 0.30), int(h * 0.20)
    thick = max(12, h // 24)
    _ring(d, cx, cy, r, 36, 324, BLUE, thick, (110, 180, 250))
    bw, bh = int(h * 0.20), int(h * 0.38)
    _horn(d, cx + r - bw // 2, cy - bh // 2, bw, bh, plus_at="top")
    return _finish(scene, ov)


def paint_hole_in_circle(scene: Image.Image) -> Image.Image:
    """Shut flap. A hole in the circle. The water stops."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.02, 0.00, 0.72, 1.00))
    cx, cy, r = int(w * 0.32), int(h * 0.32), int(h * 0.20)
    thick = max(16, h // 16)
    # A wide gap at the top. No arrowheads, so the loop is not moving.
    d.arc((cx - r, cy - r, cx + r, cy + r), 330, 210, fill=BLUE, width=thick)
    fw, fh = thick * 2, int(r * 0.72)
    d.rounded_rectangle(
        (cx - fw // 2, cy - r - fh // 3, cx + fw // 2, cy - r + fh),
        radius=6,
        fill=RED_FILL,
        outline=INK,
        width=4,
    )
    return _finish(scene, ov)


def paint_honk_stopped(scene: Image.Image) -> Image.Image:
    """The honk stopped: finger off the button, horn silent."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.08, 0.04, 0.92, 0.48))
    r = int(w * 0.13)
    cx = int(w * 0.32)
    top = _button(d, cx, int(h * 0.24), r, down=False)
    fw, fh = int(w * 0.20), int(h * 0.08)
    _finger(d, cx - fw // 2, top - fh - int(h * 0.015), fw, fh)
    _horn(d, int(w * 0.55), int(h * 0.08), int(w * 0.28), int(h * 0.34), plus_at="bottom", quiet=True)
    return _finish(scene, ov)


def paint_let_go_shuts(scene: Image.Image) -> Image.Image:
    """Let go, and the spring shuts the tube."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.08, 0.03, 0.92, 0.50))
    cx = int(w * 0.32)
    _finger(d, cx - int(w * 0.10), int(h * 0.05), int(w * 0.20), int(h * 0.10))
    _spring(d, cx, int(h * 0.17), int(h * 0.28), max(6, w // 28))
    y0, y1 = int(h * 0.32), int(h * 0.44)
    _tube(d, (int(w * 0.12), y0, int(w * 0.88), y1), max(6, w // 40))
    _flap_shut(d, int(w * 0.55), y0 + 8, y1 - 8, max(12, w // 24))
    _arrow(d, int(w * 0.18), int(w * 0.46), (y0 + y1) // 2, BLUE, max(8, w // 36))
    return _finish(scene, ov)


def paint_no_spring(scene: Image.Image) -> Image.Image:
    """The Slide Gate has no spring. The lever stays, and the water keeps moving."""
    w, h, ov, d = _canvas(scene)
    _card(d, _box(w, h, 0.08, 0.04, 0.92, 0.50))
    _slide(d, int(w * 0.16), int(h * 0.08), int(w * 0.68), int(h * 0.10))
    # A spring with a bar through it: this gate does not have one.
    sx = int(w * 0.50)
    _spring(d, sx, int(h * 0.22), int(h * 0.32), max(5, w // 36))
    d.line((sx - int(w * 0.16), int(h * 0.22), sx + int(w * 0.16), int(h * 0.33)), fill=RED, width=max(6, w // 32))
    y0, y1 = int(h * 0.36), int(h * 0.46)
    _tube(d, (int(w * 0.12), y0, int(w * 0.88), y1), max(6, w // 40))
    _flap_open(d, int(w * 0.40), y0 + 6, y1 - 6)
    _arrow(d, int(w * 0.18), int(w * 0.80), (y0 + y1) // 2, BLUE, max(8, w // 36))
    return _finish(scene, ov)


def _bell(d, cx, cy, r, down):
    """A round doorbell on a plate. down sinks the red cap."""
    plate = int(r * 1.35)
    stroke = max(4, r // 8)
    d.rounded_rectangle(
        (cx - plate, cy - plate, cx + plate, cy + plate),
        radius=max(8, plate // 4),
        fill=(236, 228, 210, 255),
        outline=INK,
        width=stroke,
    )
    cap = int(r * (0.58 if down else 0.78))
    d.ellipse((cx - cap, cy - cap, cx + cap, cy + cap), fill=RED_FILL if not down else (176, 42, 36, 255), outline=INK, width=stroke)


def paint_doorbell(scene: Image.Image) -> Image.Image:
    """A doorbell on the door: push and it rings, let go and it stops."""
    w, h, ov, d = _canvas(scene)
    cx, r = int(w * 0.55), int(w * 0.09)
    # Finger on the button, sound beside it.
    cy = int(h * 0.11)
    fw, fh = int(w * 0.16), int(h * 0.07)
    _finger(d, cx - fw - int(r * 0.2), cy - fh // 2, fw, fh)
    _bell(d, cx, cy, r, down=True)
    _sound(d, cx + int(r * 2.3), cy, int(r * 0.45), max(5, w // 40))
    # Finger lifted, cap proud, no sound.
    cy2 = int(h * 0.30)
    _finger(d, cx - fw - int(r * 0.2), cy2 - fh - int(h * 0.02), fw, int(fh * 0.75))
    _bell(d, cx, cy2, r, down=False)
    _nosound(d, cx + int(r * 2.4), cy2, int(r * 0.7))
    return _finish(scene, ov)


def add(save):
    """One scenic panel per talk box. Layout sizes match the talk frames."""
    # Hero. Sully and Pip are wrong; Tika and Coco name the two clues.
    save("c3-01-1.jpg", "office", ["sully-puzzled"], (1400, 1040), [(0.24, 0.70)], (0.50, 0.48), paint_quiet_horn)
    save("c3-01-2.jpg", "glow", ["pip-oops"], (1000, 570), [(0.82, 0.72)], (0.50, 0.82), paint_press_nothing)
    save("c3-01-3.jpg", "desk", ["tika-ask"], (1000, 470), [(0.82, 0.72)], (0.45, 0.50), paint_hunt_clues)
    save("c3-01-4.jpg", "chalk", ["coco-point"], (1900, 300), [(0.10, 0.92)], (0.50, 0.20), paint_two_clues)

    # Zigzag. Slide gate stays. The button springs. The horn wears a +.
    save("c3-02-1.jpg", "chalk", ["coco-explain"], (1500, 760), [(0.20, 0.70)], (0.50, 0.25), paint_slide_stays)
    save("c3-02-2.jpg", "glow", ["pip-magnify"], (900, 780), [(0.67, 0.58)], (0.40, 0.50), paint_spring_up)
    save("c3-02-3.jpg", "chalk", ["tika-write"], (860, 680), [(0.26, 0.68)], (0.48, 0.40), paint_hold_open)
    save("c3-02-4.jpg", "chalk", ["sully-notice"], (1550, 660), [(0.82, 0.78)], (0.45, 0.20), paint_plus_like_light)

    # Cinema. Quiet horn, then the + that was the wrong way, then Pip's top end.
    save("c3-03-1.jpg", "desk", ["pip-oops"], (1680, 580), [(0.14, 0.78)], (0.48, 0.55), paint_stays_quiet)
    save("c3-03-2.jpg", "chalk", ["tika-ask"], (800, 600), [(0.76, 0.68)], (0.50, 0.45), paint_colour_wrong)
    save("c3-03-3.jpg", "chalk", ["sully-notice"], (800, 600), [(0.76, 0.62)], (0.50, 0.45), paint_we_turned_it)
    save("c3-03-4.jpg", "glow", ["coco-point"], (800, 600), [(0.26, 0.68)], (0.42, 0.55), paint_plus_on_top)

    # Stack. Shut flap, Pip's wrong circle, the horn in the loop, then the hole.
    save("c3-04-1.jpg", "chalk", ["coco-explain"], (900, 970), [(0.70, 0.62)], (0.42, 0.50), paint_shut_flap)
    save("c3-04-2.jpg", "chalk", ["pip-magnify"], (1400, 1020), [(0.30, 0.60)], (0.50, 0.35), paint_water_still)
    save("c3-04-3.jpg", "chalk", ["tika-ask"], (1000, 400), [(0.84, 0.88)], (0.50, 0.22), paint_horn_in_circle)
    save("c3-04-4.jpg", "chalk", ["sully-notice"], (1450, 400), [(0.86, 0.90)], (0.42, 0.18), paint_hole_in_circle)

    # Strip panels are narrow, so the character is shorter than 0.7 and the
    # idea sits in the top half, clear of the bubble and the figure.
    save("c3-05-1.jpg", "desk", ["sully-puzzled"], (700, 1600), [(0.55, 0.44)], (0.38, 0.50), paint_honk_stopped)
    save("c3-05-2.jpg", "chalk", ["coco-explain"], (700, 1600), [(0.42, 0.42)], (0.42, 0.50), paint_let_go_shuts)
    save("c3-05-3.jpg", "glow", ["pip-cheer"], (700, 1600), [(0.62, 0.34)], (0.48, 0.50), paint_no_spring)
    save("c3-05-4.jpg", "bike", ["tika-write"], (700, 1600), [(0.40, 0.40)], (0.68, 0.50), paint_doorbell)
