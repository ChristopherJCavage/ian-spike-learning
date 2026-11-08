"""Case 5 talk panels. The drawing is the idea; the kid stands to one side.

Stack panels are the mission: a card, two builds, a test, then guess-build-switch.
The strip is four clues. On the tall strip the drawing sits above the kid.
On a short stack panel the drawing stays in the top, clear of the speech bubble.
No words in the pictures.
"""

import math

from PIL import Image, ImageDraw

INK = (20, 24, 32, 255)
PALE = (170, 198, 214, 255)
BOLD = (30, 144, 255, 255)
CHALK = (86, 196, 255, 255)
OTHER = (255, 122, 26, 255)
YELLOW = (255, 212, 59, 255)
RED = (214, 40, 40, 255)
GREEN = (18, 92, 62, 255)
WOOD = (92, 58, 28, 255)
CREAM = (255, 246, 220, 255)
WHITE = (255, 255, 255, 255)
BLUE = (36, 104, 196, 255)
ORANGE = (232, 118, 42, 255)
DEAD = (132, 138, 146, 255)
NIGHT = (18, 28, 36, 255)


def _overlay(scene):
    ov = Image.new("RGBA", scene.size, (0, 0, 0, 0))
    return ov, ImageDraw.Draw(ov)


def _board(d, box):
    d.rounded_rectangle(box, radius=28, fill=GREEN, outline=WOOD, width=10)


def _plus(d, cx, cy, size, fill):
    t = max(6, int(size / 5))
    d.rectangle((cx - t / 2, cy - size / 2, cx + t / 2, cy + size / 2), fill=fill)
    d.rectangle((cx - size / 2, cy - t / 2, cx + size / 2, cy + t / 2), fill=fill)


def _arrow(d, x0, y0, x1, y1, color, thick):
    """Flat arrow. The head sits on (x1, y1)."""
    ang = math.atan2(y1 - y0, x1 - x0)
    head = thick * 2.3
    sx = x1 - math.cos(ang) * head * 0.45
    sy = y1 - math.sin(ang) * head * 0.45
    px, py = math.sin(ang) * thick / 2, -math.cos(ang) * thick / 2
    d.polygon(
        [(x0 + px, y0 + py), (sx + px, sy + py), (sx - px, sy - py), (x0 - px, y0 - py)],
        fill=color,
    )
    left = (x1 - head * math.cos(ang - 0.42), y1 - head * math.sin(ang - 0.42))
    right = (x1 - head * math.cos(ang + 0.42), y1 - head * math.sin(ang + 0.42))
    d.polygon([(x1, y1), left, right], fill=color)


def _arc(cx, cy, r, start, sweep):
    """Points on a clock arc. 0 is 12, positive sweep goes toward 3, 6, 9."""
    steps = max(16, int(abs(sweep) / 6))
    pts = []
    for i in range(steps + 1):
        clock = start + sweep * i / steps
        a = math.radians(clock - 90)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _round_arrow(d, cx, cy, r, start, sweep, color, thick):
    pts = _arc(cx, cy, r, start, sweep)
    d.line(pts, fill=color, width=thick)
    end, prev = pts[-1], pts[max(0, len(pts) - 4)]
    ang = math.atan2(end[1] - prev[1], end[0] - prev[0])
    head = thick * 2.4
    left = (end[0] - head * math.cos(ang - 0.45), end[1] - head * math.sin(ang - 0.45))
    right = (end[0] - head * math.cos(ang + 0.45), end[1] - head * math.sin(ang + 0.45))
    d.polygon([end, left, right], fill=color)


def _open_ring(d, cx, cy, r, start, sweep, color, thick):
    """A loop that does not close and has no arrow, so it looks stopped."""
    d.line(_arc(cx, cy, r, start, sweep), fill=color, width=thick)


def _lamp(d, cx, cy, r, on=True):
    """A bulb and a short base. Rays only when it is on."""
    if on:
        for i in range(8):
            a = math.radians(i * 45)
            d.line(
                [(cx + math.cos(a) * r * 1.2, cy + math.sin(a) * r * 1.2),
                 (cx + math.cos(a) * r * 1.75, cy + math.sin(a) * r * 1.75)],
                fill=YELLOW, width=max(6, int(r / 5)),
            )
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 244, 170, 255), outline=INK, width=max(5, int(r / 7)))
        d.ellipse((cx - r * 0.55, cy - r * 0.62, cx - r * 0.12, cy - r * 0.18), fill=WHITE)
    else:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=DEAD, outline=INK, width=max(5, int(r / 7)))
    base = YELLOW if on else (88, 92, 98, 255)
    d.rounded_rectangle(
        (cx - r * 0.42, cy + r * 0.78, cx + r * 0.42, cy + r * 1.35),
        radius=6, fill=base, outline=INK, width=4,
    )


def _cell(d, box):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=10, fill=ORANGE, outline=INK, width=5)
    d.rectangle((x0 + (x1 - x0) * 0.28, y0 + 6, x1 - (x1 - x0) * 0.22, y1 - 6), fill=(36, 36, 40, 255))


def _colour_block(d, box, plus_at="top"):
    """Red and yellow block. The plus sits on the end named by plus_at."""
    x0, y0, x1, y1 = box
    mid = (y0 + y1) / 2
    d.rounded_rectangle(box, radius=16, fill=YELLOW, outline=INK, width=6)
    if plus_at == "top":
        d.rectangle((x0 + 6, y0 + 6, x1 - 6, mid), fill=RED)
    else:
        d.rectangle((x0 + 6, mid, x1 - 6, y1 - 6), fill=RED)
    d.rounded_rectangle(box, radius=16, outline=INK, width=6)
    cx = (x0 + x1) / 2
    py = y0 + (y1 - y0) * (0.26 if plus_at == "top" else 0.74)
    pr = min(x1 - x0, y1 - y0) * 0.16
    d.ellipse((cx - pr, py - pr, cx + pr, py + pr), fill=WHITE, outline=RED, width=5)
    _plus(d, cx, py, pr * 1.45, RED)


def _switch(d, cx, cy, s, up=True):
    d.rounded_rectangle((cx - s, cy - s * 0.45, cx + s, cy + s * 0.62), radius=12, fill=(48, 150, 78, 255), outline=INK, width=5)
    d.ellipse((cx - s * 0.28, cy - s * 0.08, cx + s * 0.28, cy + s * 0.28), fill=(30, 90, 48, 255), outline=INK, width=4)
    tip = cy - s * 0.95 if up else cy + s * 0.95
    d.line([(cx, cy), (cx, tip)], fill=INK, width=max(6, int(s / 4)))
    kr = s * 0.28
    d.ellipse((cx - kr, tip - kr, cx + kr, tip + kr), fill=YELLOW, outline=INK, width=4)


def _glass(d, cx, cy, r):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(70, 78, 88, 255), width=max(8, int(r / 4)))
    d.arc((cx - r * 0.7, cy - r * 0.75, cx + r * 0.15, cy + r * 0.1), 200, 330, fill=WHITE, width=max(4, int(r / 8)))
    ang = math.radians(48)
    x0, y0 = cx + math.cos(ang) * r * 0.9, cy + math.sin(ang) * r * 0.9
    x1, y1 = cx + math.cos(ang) * r * 1.85, cy + math.sin(ang) * r * 1.85
    d.line([(x0, y0), (x1, y1)], fill=(50, 54, 60, 255), width=max(8, int(r / 3)))


def _card(d, box):
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0 + 14, y0 + 16, x1 + 14, y1 + 16), radius=22, fill=(0, 0, 0, 70))
    d.rounded_rectangle(box, radius=22, fill=CREAM, outline=INK, width=8)
    d.rectangle((x0 + 8, y0 + 8, x1 - 8, y0 + (y1 - y0) * 0.16), fill=YELLOW)
    ear = (x1 - x0) * 0.16
    d.polygon([(x1 - ear, y0), (x1, y0 + ear), (x1 - ear, y0 + ear)], fill=(232, 214, 170, 255))
    d.line([(x1 - ear, y0), (x1 - ear, y0 + ear), (x1, y0 + ear)], fill=INK, width=6)


def paint_mission_card(scene):
    """A case card that shows the job: a yellow light. Coco stands on the right."""
    w, h = scene.size
    ov, d = _overlay(scene)
    card = (w * 0.05, h * 0.07, w * 0.50, h * 0.64)
    _card(d, card)
    cx = (card[0] + card[2]) / 2
    cy = (card[1] + card[3]) / 2 + h * 0.04
    _lamp(d, cx, cy, min(w, h) * 0.11, on=True)
    return Image.alpha_composite(scene, ov)


def paint_two_ways(scene):
    """Two different boards. Both lamps are on. Pip stands on the left."""
    w, h = scene.size
    ov, d = _overlay(scene)
    top = (w * 0.46, h * 0.05, w * 0.96, h * 0.46)
    bot = (w * 0.46, h * 0.52, w * 0.96, h * 0.93)
    _board(d, top)
    _board(d, bot)
    wire = max(12, int(w / 70))
    # Across the top: cell, then lamp.
    _cell(d, (w * 0.52, h * 0.16, w * 0.68, h * 0.34))
    d.line([(w * 0.68, h * 0.25), (w * 0.76, h * 0.25)], fill=BLUE, width=wire)
    _lamp(d, w * 0.84, h * 0.22, h * 0.07, on=True)
    # Down the side: lamp above, cell below, wire on the right.
    _lamp(d, w * 0.62, h * 0.64, h * 0.065, on=True)
    _cell(d, (w * 0.54, h * 0.76, w * 0.72, h * 0.88))
    d.line([(w * 0.70, h * 0.70), (w * 0.86, h * 0.70), (w * 0.86, h * 0.82), (w * 0.72, h * 0.82)], fill=BLUE, width=wire)
    return Image.alpha_composite(scene, ov)


def paint_test_job(scene):
    """The lamp is already shining, and the switch is up. Short panel: up high, left."""
    w, h = scene.size
    ov, d = _overlay(scene)
    # Wide enough to cover the photo's own lamp. Tika stands on the right end.
    _board(d, (w * 0.03, h * 0.04, w * 0.97, h * 0.58))
    _switch(d, w * 0.20, h * 0.28, h * 0.15, up=True)
    _lamp(d, w * 0.48, h * 0.22, h * 0.11, on=True)
    return Image.alpha_composite(scene, ov)


def paint_guess_build(scene):
    """Guess, build, switch it on. Three pictures in the top, Sully on the right."""
    w, h = scene.size
    ov, d = _overlay(scene)
    boxes = []
    for i in range(3):
        box = (w * (0.03 + i * 0.23), h * 0.06, w * (0.22 + i * 0.23), h * 0.56)
        boxes.append(box)
        d.rounded_rectangle(box, radius=18, fill=CREAM, outline=INK, width=6)
    thick = max(10, int(h / 22))
    for i in range(2):
        y = h * 0.32
        _arrow(d, boxes[i][2] + w * 0.008, y, boxes[i + 1][0] - w * 0.008, y, BOLD, thick)
    # A glass: look first, then guess.
    b = boxes[0]
    _glass(d, (b[0] + b[2]) / 2 - w * 0.012, (b[1] + b[3]) / 2 - h * 0.02, h * 0.15)
    # Blocks on a board: the build. The lamp is not on yet.
    b = boxes[1]
    _board(d, (b[0] + w * 0.015, b[1] + h * 0.08, b[2] - w * 0.015, b[3] - h * 0.06))
    _cell(d, (b[0] + w * 0.03, b[1] + h * 0.18, b[0] + w * 0.09, b[3] - h * 0.16))
    d.line(
        [(b[0] + w * 0.09, (b[1] + b[3]) / 2), (b[2] - w * 0.07, (b[1] + b[3]) / 2)],
        fill=BLUE, width=max(8, int(h / 40)),
    )
    _lamp(d, b[2] - w * 0.045, b[1] + h * 0.22, h * 0.065, on=False)
    # Switch up, lamp on: the test.
    b = boxes[2]
    _switch(d, b[0] + w * 0.055, b[1] + h * 0.28, h * 0.12, up=True)
    _lamp(d, b[2] - w * 0.05, b[1] + h * 0.22, h * 0.08, on=True)
    return Image.alpha_composite(scene, ov)


def paint_gap_circle(scene):
    """A chalk loop that does not meet. The gap is at the top. Tika stands below."""
    w, h = scene.size
    ov, d = _overlay(scene)
    # The room's chalkboard already has a closed loop. Cover that whole band
    # so the only circle left is the one with a hole. Tika is pasted on top.
    d.rectangle((0, 0, w, int(h * 0.74)), fill=(18, 46, 36, 255))
    frame = (w * 0.04, h * 0.02, w * 0.96, h * 0.70)
    d.rounded_rectangle(frame, radius=18, fill=WOOD)
    d.rounded_rectangle(
        (frame[0] + 14, frame[1] + 14, frame[2] - 14, frame[3] - 14),
        radius=10, fill=(12, 42, 32, 255),
    )
    cx, cy = w * 0.50, h * 0.20
    r = min(w * 0.34, h * 0.15)
    _round_arrow(d, cx, cy, r, 36, 286, CHALK, max(18, int(w / 26)))
    return Image.alpha_composite(scene, ov)


def paint_push_button(scene):
    """One big press-button, with the push coming down onto it. Coco stands below."""
    w, h = scene.size
    ov, d = _overlay(scene)
    cx, cy = w * 0.50, h * 0.20
    base = min(w, h) * 0.22
    d.rounded_rectangle(
        (cx - base, cy - base * 0.85, cx + base, cy + base * 0.95),
        radius=28, fill=(232, 236, 240, 255), outline=INK, width=8,
    )
    for dx, dy in ((-0.55, -0.45), (0.55, -0.45), (-0.55, 0.55), (0.55, 0.55)):
        r = base * 0.12
        sx, sy = cx + base * dx, cy + base * dy
        d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=WHITE, outline=INK, width=4)
    br = base * 0.52
    d.ellipse((cx - br, cy - br * 0.15 - br, cx + br, cy - br * 0.15 + br), fill=RED, outline=INK, width=8)
    d.ellipse(
        (cx - br * 0.45, cy - br * 0.85, cx - br * 0.05, cy - br * 0.35),
        fill=(255, 150, 140, 255),
    )
    _arrow(d, cx, h * 0.035, cx, cy - br * 1.35, OTHER, max(16, int(w / 28)))
    return Image.alpha_composite(scene, ov)


def _white_light(d, cx, cy, r):
    for i in range(8):
        a = math.radians(i * 45 + 22)
        d.line([(cx + math.cos(a) * r * 1.25, cy + math.sin(a) * r * 1.25),
                (cx + math.cos(a) * r * 1.8, cy + math.sin(a) * r * 1.8)],
               fill=(245, 167, 0, 255), width=max(5, int(r / 5)))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WHITE, outline=(120, 150, 175, 255), width=max(5, int(r / 7)))


def paint_wrong_plus(scene):
    """Mission 3: the red light and the white light side by side, a blue tube
    across the top and one across the bottom. Never one on top of the other."""
    w, h = scene.size
    ov, d = _overlay(scene)
    bw = w * 0.18
    lx, rx = w * 0.26, w * 0.74
    y0, y1 = h * 0.06, h * 0.40
    d.rounded_rectangle((lx - bw / 2, y0, lx + bw / 2, y1), radius=int(bw * 0.3), fill=(242, 182, 50, 255), outline=INK, width=6)
    d.rounded_rectangle((rx - bw / 2, y0, rx + bw / 2, y1), radius=int(bw * 0.3), fill=(214, 230, 240, 255), outline=INK, width=6)
    for y in (y0 + bw * 0.45, y1 - bw * 0.45):
        d.rounded_rectangle((lx, y - bw * 0.28, rx, y + bw * 0.28), radius=int(bw * 0.28), fill=BLUE, outline=INK, width=5)
    r = bw * 0.8
    cy = (y0 + y1) / 2
    d.ellipse((lx - r, cy - r, lx + r, cy + r), fill=RED, outline=INK, width=5)
    _white_light(d, rx, cy, bw * 0.42)
    return Image.alpha_composite(scene, ov)


def paint_stopped_loop(scene):
    """Three finished missions: yellow, red, and red with white."""
    w, h = scene.size
    ov, d = _overlay(scene)
    r = h * 0.07
    cy = h * 0.22
    for i, col in enumerate((YELLOW, RED)):
        cx = w * (0.22 + i * 0.26)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col, outline=INK, width=5)
    cx = w * 0.80
    d.ellipse((cx - r * 0.9, cy - r * 1.9, cx + r * 0.9, cy - r * 0.1), fill=RED, outline=INK, width=5)
    _white_light(d, cx, cy + r * 1.0, r * 0.65)
    return Image.alpha_composite(scene, ov)


def add(save):
    # Mission stack. Office and desk. The kid is off to one side, about 0.7 tall.
    save("c5-01-1.jpg", "office", ["coco-explain"], (900, 970), [(0.78, 0.68)], (0.34, 0.48), paint=paint_mission_card)
    save("c5-01-2.jpg", "office", ["pip-cheer"], (1400, 1020), [(0.22, 0.66)], (0.58, 0.50), paint=paint_two_ways)
    save("c5-01-3.jpg", "desk", ["tika-ask"], (1000, 400), [(0.84, 0.72)], (0.40, 0.58), paint=paint_test_job)
    save("c5-01-4.jpg", "office", ["sully-notice"], (1450, 400), [(0.88, 0.72)], (0.46, 0.52), paint=paint_guess_build)

    # Four clues, tall and narrow. The drawing is in the top. The kid stands under it.
    save("c5-02-1.jpg", "chalk", ["tika-write"], (700, 1600), [(0.32, 0.58)], (0.50, 0.40), paint=paint_gap_circle)
    save("c5-02-2.jpg", "desk", ["coco-explain"], (700, 1600), [(0.36, 0.58)], (0.48, 0.42), paint=paint_push_button)
    save("c5-02-3.jpg", "desk", ["pip-magnify"], (700, 1600), [(0.40, 0.48)], (0.42, 0.45), paint=paint_wrong_plus)
    save("c5-02-4.jpg", "office", ["sully-puzzled"], (700, 1600), [(0.66, 0.58)], (0.55, 0.46), paint=paint_stopped_loop)
