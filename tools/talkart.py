"""Cut characters out of the cream pose sheets and sit them in a scene.

The paper behind a pose is the same cream as Tika's chest and the pages of
her notebook. Deleting every cream-colored pixel is what let the chalkboard
show through her. A dark outline is a wall: the flood that removes the paper
stops there, and anything sealed inside the ink is put back if it was eaten.

`imglint` refuses a cutout that still has a hole. Run it with:

    python3 tools/snap.py imglint builds/snap-01-the-loop
"""

from __future__ import annotations

from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
COMIC = ROOT / "context" / "comic"
ASSETS = Path.home() / ".cursor/projects/Users-cjcavage-Projects-ian-spike-learning/assets"
CREAM = (255, 236, 204)
# A hole this big is a missing piece of the character, not a speck of fringe.
HOLE_LIMIT = 80
# Ink. Anything darker than this blocks the paper flood.
WALL_LUM = 82
# Pose-sheet paper, as opposed to a white chest or a notebook page (those
# sit further from this cream). A pocket of it trapped between spokes, or
# between a leg and a skateboard, has to become transparent.
PAPER_DIST = 16


def _dist(p, cream=CREAM) -> int:
    return abs(p[0] - cream[0]) + abs(p[1] - cream[1]) + abs(p[2] - cream[2])


def _lum(p) -> float:
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]


def _sat(p) -> int:
    return max(p[0], p[1], p[2]) - min(p[0], p[1], p[2])


def _walls(src: Image.Image, dilate: int = 0) -> Image.Image:
    """Dark ink as 255. `dilate` closes hairline gaps in the outline."""
    w, h = src.size
    pix = src.load()
    wall = Image.new("L", (w, h), 0)
    wp = wall.load()
    for y in range(h):
        for x in range(w):
            if _lum(pix[x, y]) < WALL_LUM:
                wp[x, y] = 255
    if dilate:
        wall = wall.filter(ImageFilter.MaxFilter(dilate * 2 + 1))
    return wall


def _flood(src: Image.Image, wall: Image.Image, max_dist: int) -> bytearray:
    """Pixels of paper you can walk to from the edge without crossing ink."""
    w, h = src.size
    pix = src.load()
    wp = wall.load()
    bg = bytearray(w * h)
    q = deque()
    for x in range(w):
        q.append((x, 0))
        q.append((x, h - 1))
    for y in range(h):
        q.append((0, y))
        q.append((w - 1, y))
    while q:
        x, y = q.popleft()
        i = y * w + x
        if bg[i] or wp[x, y]:
            continue
        if max_dist < 10000 and _dist(pix[x, y]) > max_dist:
            continue
        bg[i] = 1
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not bg[ny * w + nx]:
                q.append((nx, ny))
    return bg


def _expand_shadow(src: Image.Image, bg: bytearray, wall: Image.Image) -> None:
    """The pose sheet's floor oval is cream too, just a little dirtier."""
    w, h = src.size
    pix = src.load()
    wp = wall.load()
    q = deque((i % w, i // w) for i, v in enumerate(bg) if v)
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            j = ny * w + nx
            if bg[j] or wp[nx, ny]:
                continue
            c = pix[nx, ny]
            if _dist(c) > 155 or _lum(c) < 165:
                continue
            bg[j] = 1
            q.append((nx, ny))


def cutout_image(im: Image.Image) -> Image.Image:
    """Lift a pose off its cream paper.

    Light feathers, a white chest and an open notebook stay, because they
    are inside the outline. Only paint that touches the edge of the sheet
    goes away.
    """
    src = im.convert("RGB")
    w, h = src.size
    pix = src.load()
    wall = _walls(src, 0)
    bg = _flood(src, wall, 52)
    _expand_shadow(src, bg, wall)
    # A gap in the ink can let the flood into the chest. Seal hairline gaps
    # and put back whatever is still enclosed.
    sealed = _flood(src, _walls(src, 2), 10000)
    out = Image.new("RGBA", (w, h))
    op = out.load()
    for y in range(h):
        row = y * w
        for x in range(w):
            r, g, b = pix[x, y]
            i = row + x
            keep = not bg[i]
            if bg[i] and not sealed[i] and _dist((r, g, b)) > 18:
                keep = True
            op[x, y] = (r, g, b, 255 if keep else 0)
    _open_see_through(out)
    return out


def _open_see_through(im: Image.Image) -> None:
    """Drop paper that the outline trapped, and an empty glass highlight.

    A wheel, a skateboard, or a gap between two characters closes a loop, so
    the paper inside never touches the edge of the sheet and the first flood
    leaves it opaque. That is the white sticker on the skate park. The same
    pass clears the blank part of a magnifying glass (the crescent that is
    not the eye). The chest, the notebook and the eye stay: they are not
    paper, and the eye touches the iris.
    """
    w, h = im.size
    pix = im.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            if a and _dist((r, g, b)) <= PAPER_DIST:
                pix[x, y] = (r, g, b, 0)

    rim = Image.new("L", (w, h), 0)
    rp = rim.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            if a and _sat((r, g, b)) < 38 and 100 <= _lum((r, g, b)) <= 175:
                rp[x, y] = 255
    rim = rim.filter(ImageFilter.MaxFilter(3))
    rp = rim.load()
    # The eye's white sits a few pixels from the red iris. The empty part of
    # the glass does not. Radius 8 reaches the eye and misses the highlight.
    near = Image.new("L", (w, h), 0)
    np = near.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            if a and r > 150 and r > g + 30 and r > b + 20:
                np[x, y] = 255
    near = near.filter(ImageFilter.MaxFilter(17))
    np = near.load()
    outside = bytearray(w * h)
    q = deque()
    for x in range(w):
        q.append((x, 0))
        q.append((x, h - 1))
    for y in range(h):
        q.append((0, y))
        q.append((w - 1, y))
    while q:
        x, y = q.popleft()
        i = y * w + x
        if outside[i] or rp[x, y]:
            continue
        outside[i] = 1
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not outside[ny * w + nx]:
                q.append((nx, ny))

    seen = bytearray(w * h)
    for y in range(h):
        for x in range(w):
            i = y * w + x
            if seen[i] or pix[x, y][3] == 0:
                continue
            r, g, b, _ = pix[x, y]
            if _lum((r, g, b)) < 200 or _sat((r, g, b)) > 48:
                continue
            blob = deque([(x, y)])
            seen[i] = 1
            cells = []
            while blob:
                cx, cy = blob.popleft()
                cells.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if not (0 <= nx < w and 0 <= ny < h):
                        continue
                    j = ny * w + nx
                    if seen[j] or pix[nx, ny][3] == 0:
                        continue
                    cr, cg, cb, _ = pix[nx, ny]
                    if _lum((cr, cg, cb)) < 200 or _sat((cr, cg, cb)) > 48:
                        continue
                    seen[j] = 1
                    blob.append((nx, ny))
            if len(cells) < 400:
                continue
            inside = sum(1 for cx, cy in cells if not outside[cy * w + cx])
            if inside < 0.8 * len(cells):
                continue
            if any(np[cx, cy] for cx, cy in cells):
                continue
            for cx, cy in cells:
                cr, cg, cb, _ = pix[cx, cy]
                pix[cx, cy] = (cr, cg, cb, 0)
    # The highlight leaves a pale jagged fringe against the rim. Eat light
    # pixels that now touch that hole, but not the eye (it sits on the iris).
    for _ in range(4):
        kill = []
        for y in range(h):
            for x in range(w):
                if outside[y * w + x] or rp[x, y] or np[x, y]:
                    continue
                r, g, b, a = pix[x, y]
                if not a or _lum((r, g, b)) < 170 or _sat((r, g, b)) > 60:
                    continue
                if any(0 <= nx < w and 0 <= ny < h and pix[nx, ny][3] == 0
                       for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))):
                    kill.append((x, y))
        if not kill:
            break
        for x, y in kill:
            r, g, b, _ = pix[x, y]
            pix[x, y] = (r, g, b, 0)


def _glass_is_empty(im: Image.Image) -> bytearray:
    """Pixels of a blank lens highlight. The eye, which sits on the iris, is not in here."""
    marked = im.convert("RGBA").copy()
    # Reuse the punch on a copy and see what changed. Cheap enough next to the
    # cutout, and it cannot drift from the pixels we actually clear.
    before = marked.split()[-1].tobytes()
    _open_see_through(marked)
    after = marked.split()[-1].load()
    w, h = marked.size
    empty = bytearray(w * h)
    prev = Image.frombytes("L", (w, h), before).load()
    for y in range(h):
        row = y * w
        for x in range(w):
            if prev[x, y] and after[x, y] == 0:
                empty[row + x] = 1
    return empty


def cutout(name: str) -> Image.Image:
    return cutout_image(Image.open(COMIC / f"{name}.jpg"))


def hole_pixels(im: Image.Image) -> int:
    """Transparent pixels sealed inside the character, not the page around it."""
    im = im.convert("RGBA")
    w, h = im.size
    alpha = im.split()[-1].load()
    seen = bytearray(w * h)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if alpha[x, y] == 0:
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if alpha[x, y] == 0:
                q.append((x, y))
    while q:
        x, y = q.popleft()
        if not (0 <= x < w and 0 <= y < h):
            continue
        i = y * w + x
        if seen[i] or alpha[x, y] != 0:
            continue
        seen[i] = 1
        q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    holes = 0
    for y in range(h):
        row = y * w
        for x in range(w):
            if alpha[x, y] == 0 and not seen[row + x]:
                holes += 1
    return holes


def erased_interior(src: Image.Image, cut: Image.Image) -> int:
    """Interior paint the cutout threw away, even if a gap joins it to the edge.

    The chest is the same cream as the paper. If the outline is intact, that
    cream is a hole. If the outline has a hairline gap, the hole is still
    inside the ink once the gap is closed, and it still counts.
    """
    src = src.convert("RGB")
    cut = cut.convert("RGBA")
    w, h = src.size
    if cut.size != (w, h):
        cut = cut.resize((w, h), Image.Resampling.NEAREST)
    reached = _flood(src, _walls(src, 2), 10000)
    # Blank glass and trapped paper are supposed to be transparent. A chest
    # is neither, so losing it still counts.
    allowed = _glass_is_empty(src)
    sp = src.load()
    alpha = cut.split()[-1].load()
    n = 0
    for y in range(h):
        row = y * w
        for x in range(w):
            if reached[row + x] or allowed[row + x]:
                continue
            if _lum(sp[x, y]) < WALL_LUM:
                continue
            if alpha[x, y] == 0 and _dist(sp[x, y]) > 18:
                n += 1
    return n


def trapped_paper(im: Image.Image) -> int:
    """Opaque pixels that are still the cream sheet. They read as white stickers."""
    im = im.convert("RGBA")
    w, h = im.size
    pix = im.load()
    n = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            if a > 20 and _dist((r, g, b)) <= PAPER_DIST:
                n += 1
    return n


def lint_cutout(name: str, im: Image.Image, src: Image.Image | None = None) -> str | None:
    w, h = im.size
    opaque = sum(1 for px in im.getdata() if px[3] > 20)
    if opaque < 0.08 * w * h:
        return f"{name}: cutout ate the character ({opaque} pixels left)"
    paper = trapped_paper(im)
    if paper > HOLE_LIMIT:
        return f"{name}: {paper} pixels of the pose-sheet paper are still opaque (a wheel or a gap will show white)"
    if src is not None:
        # The gap between a tail and a leg is transparent on purpose. What
        # fails is paint inside the ink (a white chest, a notebook page)
        # getting thrown away with the paper.
        erased = erased_interior(src, im)
        if erased > HOLE_LIMIT:
            return f"{name}: {erased} interior pixels were erased (a chest or a page will show the background)"
        return None
    holes = hole_pixels(im)
    if holes > HOLE_LIMIT:
        return f"{name}: {holes} transparent pixels inside the character (the background will show through)"
    return None


def lint_messages(bdir: Path) -> list[str]:
    """What's wrong with the saved cutouts. Empty means the scenes are clean."""
    folder = bdir / "renders" / "talk" / "cutouts"
    talk = bdir / "renders" / "talk"
    if not talk.exists() or not any(talk.glob("*.jpg")):
        return []
    if not folder.exists() or not any(folder.glob("*.png")):
        return ["talk scenes have no cutouts (run python3 tools/talkart.py)"]
    bad = []
    for f in sorted(folder.glob("*.png")):
        src_path = COMIC / f"{f.stem}.jpg"
        src = Image.open(src_path) if src_path.exists() else None
        msg = lint_cutout(f.stem, Image.open(f), src)
        if msg:
            bad.append(msg)
    return bad


def lint_saved(bdir: Path) -> int:
    folder = bdir / "renders" / "talk" / "cutouts"
    msgs = lint_messages(bdir)
    if not (bdir / "renders" / "talk").exists():
        return 0
    names = sorted(p.stem for p in folder.glob("*.png")) if folder.exists() else []
    bad_names = {m.split(":", 1)[0] for m in msgs}
    for name in names:
        if name not in bad_names:
            print(f"ok   {name}")
    for msg in msgs:
        print(f"FAIL IMGLINT     {msg}")
    if not msgs and names:
        print(f"{len(names)} cutouts, no holes")
    elif not names and not msgs:
        print("no talk scenes to lint")
    else:
        print(f"{len(msgs)} cutouts with holes")
    return 1 if msgs else 0


def _cover(bg: Image.Image, w: int, h: int, fx: float, fy: float) -> Image.Image:
    bw, bh = bg.size
    scale = max(w / bw, h / bh)
    nw, nh = int(bw * scale) + 1, int(bh * scale) + 1
    resized = bg.resize((nw, nh), Image.Resampling.LANCZOS)
    x = max(0, min(nw - w, int((nw - w) * fx)))
    y = max(0, min(nh - h, int((nh - h) * fy)))
    return resized.crop((x, y, x + w, y + h)).convert("RGBA")


def _trim(im: Image.Image) -> Image.Image:
    box = im.getchannel("A").getbbox()
    if not box:
        return im
    x0, y0, x1, y1 = box
    pad = 4
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def _plus(d: ImageDraw.ImageDraw, cx, cy, size, fill) -> None:
    t = max(6, size // 5)
    d.rectangle((cx - t // 2, cy - size // 2, cx + t // 2, cy + size // 2), fill=fill)
    d.rectangle((cx - size // 2, cy - t // 2, cx + size // 2, cy + t // 2), fill=fill)


def _arrow(d: ImageDraw.ImageDraw, x0, x1, y, color, thick) -> None:
    """A horizontal arrow. The head is at x1."""
    head = thick * 2
    if x1 >= x0:
        d.rectangle((x0, y - thick // 2, x1 - head // 2, y + thick // 2), fill=color)
        d.polygon([(x1, y), (x1 - head, y - head // 2), (x1 - head, y + head // 2)], fill=color)
    else:
        d.rectangle((x1 + head // 2, y - thick // 2, x0, y + thick // 2), fill=color)
        d.polygon([(x1, y), (x1 + head, y - head // 2), (x1 + head, y + head // 2)], fill=color)


def _board(d: ImageDraw.ImageDraw, box) -> None:
    d.rounded_rectangle(box, radius=28, fill=(18, 92, 62, 245), outline=(92, 58, 28, 255), width=10)


def paint_two_flaps(scene: Image.Image) -> Image.Image:
    """Two flaps in one tube: the left one red, the right one yellow."""
    w, h = scene.size
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    card = (int(w * 0.03), int(h * 0.05), int(w * 0.60), int(h * 0.72))
    _board(d, card)
    x0, y0, x1, y1 = (int(w * 0.07), int(h * 0.16), int(w * 0.56), int(h * 0.60))
    d.rounded_rectangle((x0, y0, x1, y1), radius=36, fill=(232, 242, 250, 255), outline=(20, 32, 48, 255), width=8)
    mid = (x0 + x1) // 2
    half = int((x1 - x0) * 0.22)
    flap = (mid - half, y0 + 22, mid + half, y1 - 22)
    # Back to back: flat edges meet, each flap opens the other way.
    d.pieslice(flap, 90, 270, fill=(226, 61, 61, 255), outline=(20, 20, 20, 255), width=6)
    d.pieslice(flap, 270, 90, fill=(255, 212, 59, 255), outline=(20, 20, 20, 255), width=6)
    d.line((mid, y0 + 22, mid, y1 - 22), fill=(20, 20, 20, 255), width=8)
    return Image.alpha_composite(scene, ov)


def paint_water_hit(scene: Image.Image) -> Image.Image:
    """One block. A pale arrow still points at the red end. The bold arrow
    has swung around and hits the yellow end."""
    w, h = scene.size
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    _board(d, (int(w * 0.02), int(h * 0.04), int(w * 0.70), int(h * 0.78)))
    bw, bh = int(h * 0.28), int(h * 0.62)
    bx, by = int(w * 0.30), int(h * 0.10)
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=18, fill=(255, 212, 59, 255), outline=(16, 22, 16, 255), width=6)
    midy = by + bh // 2
    d.rectangle((bx + 5, midy, bx + bw - 5, by + bh - 5), fill=(226, 61, 61, 255))
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=18, outline=(16, 22, 16, 255), width=6)
    cx = bx + bw // 2
    pr = int(bh * 0.16)
    py = by + int(bh * 0.78)
    d.ellipse((cx - pr, py - pr, cx + pr, py + pr), fill=(255, 255, 255, 255), outline=(214, 40, 40, 255), width=5)
    _plus(d, cx, py, int(pr * 1.3), (214, 40, 40, 255))
    pale = (170, 198, 214, 255)
    bold = (30, 144, 255, 255)
    _arrow(d, int(w * 0.08), bx - 8, by + int(bh * 0.75), pale, max(10, h // 28))
    _arrow(d, int(w * 0.64), bx + bw + 8, by + int(bh * 0.25), bold, max(16, h // 16))
    return Image.alpha_composite(scene, ov)


def _place(scene: Image.Image, guys: list, slots: list) -> Image.Image:
    w, h = scene.size
    for (name, im), (fx, scale) in zip(guys, slots):
        nh = max(1, int(h * scale))
        nw = max(1, int(im.width * nh / im.height))
        guy = im.resize((nw, nh), Image.Resampling.LANCZOS)
        x = int(w * fx - nw / 2)
        # Feet stay inside the frame. The old +2% shoved them off the bottom.
        y = h - nh - max(2, int(h * 0.015))
        shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).ellipse(
            (x + nw * 0.18, y + nh - int(h * 0.035), x + nw * 0.82, y + nh + int(h * 0.01)),
            fill=(0, 0, 0, 70),
        )
        scene = Image.alpha_composite(scene, shadow.filter(ImageFilter.GaussianBlur(6)))
        scene.paste(guy, (x, y), guy)
    return scene


def build(bdir: Path) -> int:
    assets = {
        k: Image.open(ASSETS / f"bg-{k}.jpg").convert("RGB")
        for k in ("office", "desk", "glow", "chalk", "skate", "bike")
    }
    out = bdir / "renders" / "talk"
    cuts = out / "cutouts"
    cuts.mkdir(parents=True, exist_ok=True)
    cache: dict[str, Image.Image] = {}
    problems = []
    written: set[str] = set()

    def guy(name):
        if name not in cache:
            src = Image.open(COMIC / f"{name}.jpg")
            im = cutout_image(src)
            msg = lint_cutout(name, im, src)
            if msg:
                problems.append(msg)
            im.save(cuts / f"{name}.png")
            cache[name] = _trim(im)
        return cache[name]

    def save(name, bg, poses, size, slots, crop, paint=None):
        scene = _cover(assets[bg], size[0], size[1], *crop)
        if paint:
            scene = paint(scene)
        scene = _place(scene, [(n, guy(n)) for n in poses], slots)
        scene.convert("RGB").save(out / name, quality=88)
        written.add(name)
        print(name)

    # Sizes match the talk-page frames (the slide is wide, so a "tall" panel
    # is still a big landscape, and a spread panel is a short wide shot).
    splash = (1680, 1000)
    spread = (1680, 620)
    banner = (1680, 700)
    side = (780, 900)
    hero_big = (1100, 980)
    hero_side = (860, 560)
    hero_foot = (1680, 380)
    zig_wide = (1280, 620)
    zig_sq = (760, 620)
    stack_l = (860, 980)
    stack_r = (1200, 980)
    stack_foot = (980, 420)

    one = [(0.50, 0.90)]
    two = [(0.28, 0.74), (0.72, 0.74)]
    # Shorter, and in from the corners, so splash bubbles have somewhere to sit.
    crowd = [(0.24, 0.64), (0.42, 0.70), (0.62, 0.64), (0.80, 0.68)]

    # One picture, four corners of the argument. Not a grid.
    save("c1-04-splash.jpg", "office", ["pip-oops", "coco-explain", "tika-ask", "sully-notice"], splash, crowd, (0.55, 0.62))
    save("c1-05-a.jpg", "office", ["pip-oops", "coco-explain"], spread, two, (0.35, 0.55))
    save("c1-05-b.jpg", "office", ["tika-ask", "sully-notice"], spread, two, (0.62, 0.58))
    # Banner is the bike. Pip asks; Sully is already on it.
    save("c1-06-1.jpg", "skate", ["pip-oops", "sully-bike"], banner, [(0.24, 0.90), (0.68, 0.96)], (0.42, 0.72))
    save("c1-06-2.jpg", "office", ["coco-explain"], side, one, (0.48, 0.5))
    save("c1-06-3.jpg", "chalk", ["tika-write"], side, one, (0.55, 0.42))
    save("c1-06-4.jpg", "skate", ["sully-bike"], side, one, (0.35, 0.78))
    save("c1-07-1.jpg", "chalk", ["coco-explain"], hero_big, [(0.46, 0.92)], (0.42, 0.48))
    save("c1-07-2.jpg", "chalk", ["tika-write"], hero_side, one, (0.62, 0.4))
    save("c1-07-3.jpg", "chalk", ["pip-magnify"], hero_side, one, (0.38, 0.45))
    save("c1-07-4.jpg", "chalk", ["sully-notice"], hero_foot, [(0.5, 0.98)], (0.5, 0.7))
    save("c1-09-a.jpg", "chalk", ["coco-point", "pip-cheer"], spread, two, (0.4, 0.5))
    save("c1-09-b.jpg", "chalk", ["sully-notice", "tika-write"], spread, two, (0.6, 0.45))
    save("c1-25-1.jpg", "glow", ["pip-magnify"], zig_wide, [(0.32, 0.94)], (0.3, 0.55))
    save("c1-25-2.jpg", "glow", ["coco-explain"], zig_sq, one, (0.7, 0.5))
    save("c1-25-3.jpg", "skate", ["tika-ask"], zig_sq, one, (0.45, 0.7))
    save("c1-25-4.jpg", "skate", ["sully-skate"], zig_wide, [(0.55, 0.94)], (0.55, 0.72))
    save("c1-28-a.jpg", "office", ["pip-oops", "coco-explain"], spread, two, (0.4, 0.55))
    save("c1-28-b.jpg", "office", ["tika-ask", "sully-notice"], spread, two, (0.58, 0.6))
    save("c1-31-1.jpg", "desk", ["pip-oops"], stack_l, one, (0.35, 0.48))
    save("c1-31-2.jpg", "desk", ["tika-ask"], stack_r, [(0.4, 0.94)], (0.45, 0.5))
    save("c1-31-3.jpg", "desk", ["coco-explain"], stack_foot, one, (0.3, 0.55))
    save("c1-31-4.jpg", "desk", ["sully-puzzled"], stack_foot, one, (0.7, 0.5))

    # Case 2. Each picture is the shape of its panel, and the character stands
    # in the room instead of filling it. The page was cropping these down to
    # a face, so the office, the board and the park disappeared.
    L, R = (0.30, 0.70), (0.72, 0.70)
    save("c2-01-1.jpg", "office", ["pip-oops"], (1400, 1040), [L], (0.62, 0.58))
    save("c2-01-2.jpg", "office", ["sully-notice"], (1000, 570), [L], (0.55, 0.5))
    save("c2-01-3.jpg", "desk", ["tika-ask"], (1000, 470), [L], (0.4, 0.45))
    save("c2-01-4.jpg", "chalk", ["coco-point"], (1900, 300), [(0.18, 0.92)], (0.55, 0.42))
    save("c2-02-1.jpg", "chalk", ["coco-explain"], (1500, 760), [L], (0.42, 0.45))
    save("c2-02-2.jpg", "chalk", ["pip-magnify"], (900, 780), [(0.42, 0.68)], (0.5, 0.4))
    save("c2-02-3.jpg", "office", ["tika-write"], (860, 680), [L], (0.58, 0.52))
    save("c2-02-4.jpg", "chalk", ["sully-notice"], (1500, 650), [(0.82, 0.86)], (0.72, 0.42), paint_two_flaps)
    save("c2-03-1.jpg", "skate", ["pip-oops"], (1680, 580), [(0.22, 0.86)], (0.4, 0.72))
    save("c2-03-2.jpg", "office", ["sully-puzzled"], (800, 600), [L], (0.55, 0.5))
    save("c2-03-3.jpg", "chalk", ["tika-ask"], (800, 600), [(0.4, 0.7)], (0.55, 0.4))
    save("c2-03-4.jpg", "desk", ["coco-explain"], (800, 600), [L], (0.35, 0.48))
    save("c2-04-1.jpg", "chalk", ["tika-write"], (900, 970), [(0.42, 0.68)], (0.48, 0.42))
    save("c2-04-2.jpg", "glow", ["pip-cheer"], (1400, 1020), [L], (0.62, 0.48))
    save("c2-04-3.jpg", "office", ["coco-explain"], (1000, 400), [(0.22, 0.9)], (0.55, 0.55))
    save("c2-04-4.jpg", "chalk", ["sully-notice"], (1450, 400), [(0.86, 0.92)], (0.62, 0.4), paint_water_hit)
    save("c2-05-1.jpg", "desk", ["pip-oops"], (700, 1600), [(0.5, 0.55)], (0.4, 0.35))
    save("c2-05-2.jpg", "chalk", ["tika-write"], (700, 1600), [(0.5, 0.52)], (0.5, 0.3))
    save("c2-05-3.jpg", "office", ["coco-explain"], (700, 1600), [(0.5, 0.55)], (0.55, 0.35))
    save("c2-05-4.jpg", "skate", ["sully-notice"], (700, 1600), [(0.5, 0.55)], (0.45, 0.55))
    save("c2-06-1.jpg", "glow", ["coco-explain"], (900, 1600), [(0.5, 0.55)], (0.55, 0.35))
    save("c2-06-2.jpg", "glow", ["pip-magnify"], (620, 1700), [(0.5, 0.5)], (0.4, 0.35))
    save("c2-06-3.jpg", "desk", ["tika-write"], (900, 1600), [(0.5, 0.52)], (0.4, 0.32))
    save("c2-06-4.jpg", "office", ["sully-puzzled"], (620, 1700), [(0.5, 0.55)], (0.6, 0.4))

    # Cases 3-5. Each chapter file lists the panels; the drawing lives next to it.
    import importlib.util
    for chapter in ("case3", "case4", "case5"):
        path = bdir / "chapters" / f"{chapter}_art.py"
        spec = importlib.util.spec_from_file_location(chapter, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.add(save)

    # Drop the old 2x2 panels so a stale filename can't sneak back onto a page.
    for old in out.glob("c1-*.jpg"):
        if old.name not in written:
            old.unlink()
            print(f"removed {old.name}")

    for msg in problems:
        print(f"FAIL IMGLINT     {msg}")
    if problems:
        print(f"{len(problems)} cutouts with holes; panels were still written so you can see them")
        return 1
    print(f"{len(cache)} cutouts, no holes")
    return 0


def _cream_disk(gap: bool = False) -> Image.Image:
    """A white disk inside a black ring, on the pose-sheet cream. The disk is
    the chest: same family of color as the paper, sealed in by ink."""
    im = Image.new("RGB", (180, 180), CREAM)
    d = ImageDraw.Draw(im)
    d.ellipse((30, 30, 150, 150), outline=(12, 14, 18), width=12)
    d.ellipse((54, 54, 126, 126), fill=(252, 248, 236))
    if gap:
        d.rectangle((89, 26, 91, 46), fill=CREAM)
    return im


def _eat_cream(im: Image.Image) -> Image.Image:
    """The bug: every near-cream pixel becomes a hole, chest included."""
    out = im.convert("RGBA")
    pix = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            if _dist((r, g, b)) < 48:
                pix[x, y] = (r, g, b, 0)
    return out


def selftest() -> int:
    bad = 0
    disk = _cream_disk()
    kept = cutout_image(disk)
    if lint_cutout("sealed", kept, disk):
        print("FAIL sealed chest was eaten:", lint_cutout("sealed", kept, disk))
        bad += 1
    else:
        print("ok   sealed chest stays")
    ruined = _eat_cream(disk)
    msg = lint_cutout("ruined", ruined, disk)
    if not msg:
        print("FAIL linter missed a transparent chest")
        bad += 1
    else:
        print("ok   linter catches a transparent chest")
    gappy = _cream_disk(gap=True)
    leaked = _eat_cream(gappy)
    if not lint_cutout("gap", leaked, gappy):
        print("FAIL linter missed a chest opened by a gap in the outline")
        bad += 1
    else:
        print("ok   linter catches a leak through the outline")
    fixed = cutout_image(gappy)
    msg = lint_cutout("gap-fixed", fixed, gappy)
    if msg:
        print("FAIL cutout still loses a chest when the outline has a gap:", msg)
        bad += 1
    else:
        print("ok   cutout keeps a chest even with a small gap")
    wheel = Image.new("RGB", (120, 120), CREAM)
    ImageDraw.Draw(wheel).ellipse((16, 16, 104, 104), outline=(8, 8, 10), width=8)
    opened = cutout_image(wheel)
    if trapped_paper(opened) > HOLE_LIMIT:
        print("FAIL paper still shows through a wheel:", trapped_paper(opened))
        bad += 1
    else:
        print("ok   paper inside a wheel is transparent")
    glass = Image.new("RGB", (160, 160), CREAM)
    g = ImageDraw.Draw(glass)
    g.ellipse((24, 24, 136, 136), outline=(148, 148, 150), width=12)
    g.chord((40, 36, 120, 90), 200, 340, fill=(255, 250, 238))
    g.ellipse((58, 78, 102, 122), fill=(210, 36, 36))
    seen = cutout_image(glass)
    sp, cp = glass.load(), seen.load()
    cap = sum(1 for y in range(40, 70) for x in range(50, 110) if cp[x, y][3] > 20 and _lum(sp[x, y]) > 200)
    eye = sum(1 for y in range(78, 122) for x in range(58, 102) if cp[x, y][3] > 20 and cp[x, y][0] > 180)
    if cap > 40 or eye < 200:
        print(f"FAIL glass highlight cap={cap} (want clear) eye={eye} (want kept)")
        bad += 1
    else:
        print("ok   empty glass is clear and the eye stays")
    print(f"imglint selftest: {bad} wrong")
    return 1 if bad else 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "builds" / "snap-01-the-loop"
    sys.exit(build(target))
