#!/usr/bin/env python3
"""Instruction-page sync and preview for a build folder.

`ldrcheck` proves the model can be built. This proves the *pages* agree
with each other: every `0 STEP` has a `steps.md` block, a `screens.md`
row, and (for build pages) a PNG. It also writes the click-through
HTML Chris can open before anyone spends a Figma frame on a page list
that is still moving.

An optional `story.md` adds the narrative slides that run *ahead* of
step 1, the way the SPIKE App opens a project. They are a separate
track on purpose: `screens.md` row N renders model step N, so a page
inserted ahead of row 1 would silently render the wrong bricks.

    python3 tools/pages.py check builds/mining-drill-truck
    python3 tools/pages.py preview builds/mining-drill-truck
    python3 tools/pages.py pdf builds/mining-drill-truck
    python3 tools/pages.py render builds/mining-drill-truck
"""

from __future__ import annotations

import argparse
import html
import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEOCAD = Path("/Applications/LeoCAD.app/Contents/MacOS/LeoCAD")
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
VIEWPOINTS = {"front", "back", "left", "right", "top", "bottom", "home"}

# Render recipe. The job of a step page is to answer one question for a
# six-year-old: which piece is new and where does it go?
#
# FADE_COLOR ghosts everything already built, so the new part is the only
# saturated thing on the page and needs no false colour to stand out --
# it keeps its real colour, which is also the colour the child has to find
# in the bin. Lower alpha means more ghosted. HIGHLIGHT_COLOR only applies
# to steps that ask for it in `screens.md`, for a pale part that would
# otherwise disappear into the ghost.
RENDER_W, RENDER_H = 3000, 2250
FADE_COLOR = "#60FFFFFF"
HIGHLIGHT_COLOR = "#FFFF00FF"
LINE_WIDTH = "2"
AA_SAMPLES = "8"

# LeoCAD frames every step against the whole model's extent, so step 1 of
# the chameleon lands at 11% of the canvas and prints as a speck. Each
# render is trimmed to its own content and padded back out to one hero
# size, so the subject fills the page and every page is the same shape.
HERO_W, HERO_H = 2000, 1500
HERO_MARGIN = 0.05

STEP_HEAD = re.compile(r"^Step\s+(\d+)\s+--\s+(.*)$")
FIELD = re.compile(r"^\s+(Sub|Bin|Add|Do|Check|Note):\s*(.*)$")


@dataclass
class Step:
    number: int
    title: str
    sub: str = ""
    bin: str = ""
    add: list[str] = field(default_factory=list)
    do: str = ""
    check: str = ""
    note: str = ""


@dataclass
class Screen:
    number: int
    figma_frame: str
    png: str
    parts_added: str
    camera: str
    highlight: str
    copy: str

    @property
    def has_png(self) -> bool:
        return self.png.startswith("renders/") and self.png.endswith(".png")


@dataclass
class Slide:
    number: int
    figma_frame: str
    art: str
    who: str
    copy: str
    camera: str = ""
    overlay: str = ""

    @property
    def has_art(self) -> bool:
        return self.art.startswith("renders/") and self.art.endswith(".png")

    @property
    def has_overlay(self) -> bool:
        return self.overlay.startswith("renders/") and self.overlay.endswith(".png")

    @property
    def is_render(self) -> bool:
        """A slide with a camera is a LeoCAD shot of the finished model,
        refreshed by `pages.py render` like any step hero. Without one it
        is drawn art that lives in git."""
        return bool(self.camera.strip())


def parse_steps(path: Path) -> list[Step]:
    if not path.is_file():
        sys.exit(f"missing {path}")
    steps: list[Step] = []
    current: Step | None = None
    field_name: str | None = None
    buf: list[str] = []

    def flush_field() -> None:
        nonlocal field_name, buf
        if current is None or field_name is None:
            buf = []
            return
        text = " ".join(s.strip() for s in buf if s.strip())
        if field_name == "Add":
            current.add = [s.strip() for s in buf if s.strip()]
        elif field_name == "Sub":
            current.sub = text
        elif field_name == "Bin":
            current.bin = text
        elif field_name == "Do":
            current.do = text
        elif field_name == "Check":
            current.check = text
        elif field_name == "Note":
            current.note = text
        field_name = None
        buf = []

    for line in path.read_text().splitlines():
        head = STEP_HEAD.match(line)
        if head:
            flush_field()
            if current is not None:
                steps.append(current)
            current = Step(number=int(head.group(1)), title=head.group(2).strip())
            continue
        tagged = FIELD.match(line)
        if tagged and current is not None:
            flush_field()
            field_name = tagged.group(1)
            buf = [tagged.group(2)]
            continue
        if current is not None and field_name is not None and (
            line.startswith("      ") or line.startswith("\t")
        ):
            buf.append(line)
    flush_field()
    if current is not None:
        steps.append(current)
    return steps


def parse_screens(path: Path) -> list[Screen]:
    if not path.is_file():
        sys.exit(f"missing {path}")
    rows: list[Screen] = []
    in_fence = False
    for line in path.read_text().splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence or "|" not in line:
            continue
        if line.lower().lstrip().startswith("step"):
            continue
        cells = [c.strip() for c in line.split("|")]
        cells = [c for c in cells if c != ""]
        if len(cells) < 4 or not cells[0].isdigit():
            continue
        # Legacy: step | figma | png | parts | copy
        # Current: step | figma | png | parts | camera | highlight | copy
        if len(cells) >= 7:
            copy = cells[6]
            camera = cells[4]
            highlight = cells[5]
        else:
            copy = cells[4] if len(cells) > 4 else ""
            camera = "55 225"
            highlight = "yes"
        copy = copy.strip().strip('"')
        rows.append(
            Screen(
                number=int(cells[0]),
                figma_frame=cells[1],
                png=cells[2],
                parts_added=cells[3],
                camera=camera,
                highlight=highlight.lower(),
                copy=copy,
            )
        )
    return rows


def parse_story(path: Path) -> list[Slide]:
    """Narrative slides that play before step 1. Optional: a build with
    no `story.md` goes straight to bricks, which is how every build here
    worked before the chameleon."""
    if not path.is_file():
        return []
    rows: list[Slide] = []
    in_fence = False
    for line in path.read_text().splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence or "|" not in line:
            continue
        if line.lower().lstrip().startswith("slide"):
            continue
        cells = [c.strip() for c in line.split("|")]
        cells = [c for c in cells if c != ""]
        if len(cells) < 5 or not cells[0].isdigit():
            continue
        rows.append(
            Slide(
                number=int(cells[0]),
                figma_frame=cells[1],
                art=cells[2],
                who=cells[3],
                copy=cells[4].strip().strip('"'),
                camera=cells[5] if len(cells) > 5 and cells[5] != "-" else "",
                overlay=cells[6] if len(cells) > 6 and cells[6] != "-" else "",
            )
        )
    return rows


def count_ldr_steps(path: Path) -> tuple[int, int]:
    """Return (0 STEP count, max part-step). Part-step 1 is before the
    first `0 STEP`; each `0 STEP` increments. A trailing STEP after the
    last brick is the empty coding page and does not raise max part-step."""
    step = 1
    max_part = 0
    n_step_meta = 0
    for line in path.read_text().splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] == "0" and len(fields) >= 2 and fields[1].upper() == "STEP":
            step += 1
            n_step_meta += 1
            continue
        if fields[0] == "1":
            max_part = max(max_part, step)
    return n_step_meta, max_part


def _contiguous(nums: list[int], label: str, problems: list[str]) -> None:
    if not nums:
        problems.append(f"{label}: none found")
        return
    expect = list(range(1, nums[-1] + 1))
    if nums != expect:
        problems.append(f"{label}: expected {expect}, got {nums}")


def check_story(build: Path, problems: list[str]) -> list[Slide]:
    slides = parse_story(build / "story.md")
    on_disk = sorted((build / "renders").glob("story-*.png"))
    if not slides:
        if on_disk:
            problems.append(
                f"renders/ has story art but no story.md: "
                f"{[p.name for p in on_disk]}"
            )
        return slides
    _contiguous([s.number for s in slides], "story.md", problems)
    named: set[str] = set()
    for sl in slides:
        if not sl.has_art:
            problems.append(
                f"slide {sl.number}: art must be renders/*.png, got {sl.art}"
            )
            continue
        named.add(sl.art)
        if sl.is_render and not sl.art.startswith("renders/story-"):
            # `render` would overwrite whatever this points at, and the
            # check views are wanted at their own cameras.
            problems.append(
                f"slide {sl.number}: a slide with a camera is rendered, so "
                f"its art must be renders/story-NN.png, not {sl.art}"
            )
        if not (build / sl.art).is_file():
            problems.append(f"missing {sl.art}")
        if sl.overlay:
            if not sl.has_overlay:
                problems.append(
                    f"slide {sl.number}: overlay must be renders/*.png, "
                    f"got {sl.overlay}"
                )
            else:
                named.add(sl.overlay)
                if not (build / sl.overlay).is_file():
                    problems.append(f"missing {sl.overlay}")
    orphans = sorted({f"renders/{p.name}" for p in on_disk} - named)
    if orphans:
        problems.append(f"renders/ has unlisted story art: {orphans}")
    return slides


def check_build(build: Path) -> int:
    steps = parse_steps(build / "steps.md")
    screens = parse_screens(build / "screens.md")
    ldr = build / "model.ldr"
    if not ldr.is_file():
        sys.exit(f"missing {ldr}")
    n_meta, max_part = count_ldr_steps(ldr)
    renders = sorted((build / "renders").glob("step-*.png"))
    render_nums = []
    for png in renders:
        m = re.match(r"step-(\d+)\.png$", png.name)
        if m:
            render_nums.append(int(m.group(1)))

    problems: list[str] = []
    slides = check_story(build, problems)
    _contiguous([s.number for s in steps], "steps.md", problems)
    _contiguous([s.number for s in screens], "screens.md", problems)
    if len(steps) != len(screens):
        problems.append(
            f"steps.md has {len(steps)} blocks, screens.md has {len(screens)} rows"
        )
    else:
        for st, sc in zip(steps, screens):
            if st.number != sc.number:
                problems.append(
                    f"step {st.number} in steps.md vs screen {sc.number}"
                )

    png_screens = [s for s in screens if s.has_png]
    if max_part != len(png_screens):
        problems.append(
            f"model has parts through step {max_part}, "
            f"screens.md names {len(png_screens)} PNGs"
        )
    if n_meta != max_part:
        # Trailing 0 STEP after the last brick is required: it closes
        # the last build page. Coding-only trailing STEP would make
        # n_meta == max_part + 1; we accept that too.
        if n_meta != max_part + 1:
            problems.append(
                f"model has {n_meta} `0 STEP` lines and parts through step "
                f"{max_part} (want equal, or one extra empty coding STEP)"
            )

    named = []
    for sc in png_screens:
        m = re.search(r"step-(\d+)\.png$", sc.png)
        if not m:
            problems.append(f"screen {sc.number}: cannot parse PNG name {sc.png}")
            continue
        n = int(m.group(1))
        named.append(n)
        if n != sc.number:
            problems.append(
                f"screen {sc.number} points at {sc.png} (number mismatch)"
            )
        png_path = build / sc.png
        if not png_path.is_file():
            problems.append(f"missing {sc.png}")
    if sorted(named) != sorted(render_nums):
        extra = sorted(set(render_nums) - set(named))
        missing = sorted(set(named) - set(render_nums))
        if extra:
            problems.append(f"renders/ has unlisted step PNGs: {extra}")
        if missing:
            problems.append(f"screens.md names PNGs not on disk: {missing}")

    print(f"{build}")
    if slides:
        print(f"  story.md     {len(slides)} slides before step 1")
    print(f"  steps.md     {len(steps)} blocks")
    print(f"  screens.md   {len(screens)} rows")
    print(f"  model.ldr    {n_meta} STEP, parts through {max_part}")
    print(f"  renders/     {len(renders)} step PNGs")
    if problems:
        print(f"\n{len(problems)} problem(s)")
        for p in problems:
            print(f"  {p}")
        return 1
    print("\n0 problem(s)")
    return 0


def _esc(s: str) -> str:
    return html.escape(s, quote=True)


def write_preview(build: Path) -> Path:
    steps = parse_steps(build / "steps.md")
    screens = parse_screens(build / "screens.md")
    if len(steps) != len(screens):
        sys.exit("steps.md and screens.md length mismatch -- run pages.py check")
    pages = []
    for sl in parse_story(build / "story.md"):
        if sl.has_art:
            # LeoCAD PNGs are transparent and drawn for a white page; on the
            # slide's dark background the black pegs and grey feet vanish.
            plate = " plate" if sl.is_render else ""
            art = (
                f'<img class="art{plate}" src="{_esc(sl.art)}" '
                f'alt="{_esc(sl.copy)}">'
            )
        else:
            art = '<div class="art placeholder"><p>art pending</p></div>'
        if sl.has_overlay:
            art += (
                f'<img class="peek" src="{_esc(sl.overlay)}" alt="" '
                f'aria-hidden="true">'
            )
        # Story slides carry no Back/Next: these pages get printed on paper.
        pages.append(
            f"""
<section class="page slide" data-slide="{sl.number}" hidden>
  <div class="scene">
    <div class="stage">{art}</div>
    <p class="tell">{_esc(sl.copy)}</p>
  </div>
  <footer><p class="check">{_esc(sl.who)}</p></footer>
</section>"""
        )
    for st, sc in zip(steps, screens):
        add_html = "".join(f"<li>{_esc(a)}</li>" for a in st.add) or "<li>(none)</li>"
        img = ""
        if sc.has_png:
            img = (
                f'<img class="hero" src="{_esc(sc.png)}" '
                f'alt="Step {st.number}: {_esc(st.title)}">'
            )
        else:
            img = (
                f'<div class="hero placeholder">'
                f'<p>{_esc(st.do or sc.copy or "Coding page")}</p></div>'
            )
        pages.append(
            f"""
<section class="page" data-step="{st.number}" hidden>
  <header>
    <span class="badge">{st.number}</span>
    <h1>{_esc(st.title)}</h1>
    <span class="bin">{_esc(st.bin)}</span>
  </header>
  <div class="body">
    <aside>
      <h2>Add</h2>
      <ul>{add_html}</ul>
      <p class="copy">{_esc(sc.copy or st.do)}</p>
    </aside>
    {img}
  </div>
  <footer>
    <p class="check"><strong>Check:</strong> {_esc(st.check)}</p>
    <div class="nav">
      <button type="button" class="back">Back</button>
      <button type="button" class="next">Next</button>
    </div>
  </footer>
</section>"""
        )
    out = build / "preview.html"
    out.write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(build.name)} instructions</title>
<style>
  html, body {{ margin: 0; background: #fff; color: #111;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; }}
  /* `display` on .page beats the browser's own rule for the hidden
     attribute, so the flipbook needs this or every page shows at once. */
  .page[hidden] {{ display: none; }}
  .page {{ min-height: 100vh; display: flex; flex-direction: column;
    padding: 24px 32px 16px; box-sizing: border-box; }}
  header {{ display: flex; align-items: center; gap: 16px; }}
  .badge {{ background: #e31c3d; color: #fff; font-size: 28px; font-weight: 700;
    min-width: 56px; height: 56px; border-radius: 12px; display: flex;
    align-items: center; justify-content: center; }}
  h1 {{ font-size: 28px; margin: 0; flex: 1; }}
  .bin {{ font-size: 16px; color: #444; }}
  .body {{ flex: 1; display: grid; grid-template-columns: 280px 1fr;
    gap: 24px; align-items: center; min-height: 0; }}
  aside {{ background: #f4f4f4; border-radius: 12px; padding: 16px; }}
  aside h2 {{ margin: 0 0 8px; font-size: 14px; text-transform: uppercase;
    letter-spacing: .06em; color: #666; }}
  aside ul {{ margin: 0; padding-left: 18px; }}
  .copy {{ margin-top: 16px; font-size: 18px; line-height: 1.35; }}
  .hero {{ width: 100%; height: auto; background: #fff; }}
  .placeholder {{ min-height: 360px; display: flex; align-items: center;
    justify-content: center; background: #f4f4f4; border-radius: 12px;
    font-size: 22px; padding: 24px; text-align: center; }}
  footer {{ display: flex; align-items: center; justify-content: space-between;
    gap: 16px; margin-top: 12px; }}
  .check {{ flex: 1; font-size: 16px; color: #333; }}
  .slide {{ background: #06341f; color: #fff; cursor: pointer; }}
  .slide .scene {{ flex: 1; display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 20px; min-height: 0; }}
  .slide .stage {{ position: relative; display: inline-block; min-height: 0; }}
  .slide .art {{ display: block; max-width: 100%; max-height: 68vh;
    border-radius: 16px; }}
  .slide .plate {{ background: #fff; padding: 12px; box-sizing: border-box; }}
  /* The cartoon chameleon leans in on the build slide to look at its own
     LEGO self. It must not cover the model, so it sits on the corner. */
  .slide .peek {{ position: absolute; right: -6%; bottom: -8%; width: 30%;
    max-width: 280px; }}
  .slide .tell {{ margin: 0; max-width: 22ch; text-align: center;
    font-size: 40px; line-height: 1.2; font-weight: 700; }}
  .slide .check {{ color: #9fd9b6; font-size: 16px; }}
  .slide footer {{ justify-content: flex-start; }}
  @media print {{
    @page {{ size: landscape; margin: 10mm; }}
    html, body {{ background: #fff; }}
    /* On screen only one page is shown at a time; on paper print them all,
       one per sheet, and drop the buttons. */
    .page[hidden] {{ display: flex !important; }}
    .page {{ min-height: auto; height: 100vh; page-break-after: always;
      break-after: page; }}
    .page:last-child {{ page-break-after: auto; break-after: auto; }}
    .nav {{ display: none !important; }}
    .slide {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .slide .art {{ max-height: 60vh; }}
  }}
  .nav button {{ font-size: 22px; padding: 12px 28px; border: 0; border-radius: 10px;
    background: #111; color: #fff; cursor: pointer; }}
  .nav button:disabled {{ background: #bbb; cursor: default; }}
  @media (max-width: 900px) {{
    .body {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
{''.join(pages)}
<script>
const pages = [...document.querySelectorAll('.page')];
let i = 0;
function show(n) {{
  i = Math.max(0, Math.min(n, pages.length - 1));
  pages.forEach((p, k) => p.hidden = k !== i);
  // Story slides have no buttons -- they are printed, not clicked.
  const back = pages[i].querySelector('.back');
  const next = pages[i].querySelector('.next');
  if (back) back.disabled = i === 0;
  if (next) {{
    next.disabled = i === pages.length - 1;
    next.textContent = i === pages.length - 1 ? 'Done' : 'Next';
  }}
}}
document.body.addEventListener('click', e => {{
  if (e.target.classList.contains('next')) return show(i + 1);
  if (e.target.classList.contains('back')) return show(i - 1);
  // Buttonless pages still need a way forward on screen.
  if (pages[i].classList.contains('slide')) show(i + 1);
}});
document.addEventListener('keydown', e => {{
  if (e.key === 'ArrowRight' || e.key === ' ') {{ e.preventDefault(); show(i + 1); }}
  if (e.key === 'ArrowLeft') {{ e.preventDefault(); show(i - 1); }}
}});
show(0);
</script>
</body>
</html>
"""
    )
    print(f"wrote {out}")
    return out


STACKED_STYLE = """
  html, body { margin: 0; background: #fff; color: #111;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; }
  @page { size: letter landscape; margin: 0; }
  .page {
    display: flex; flex-direction: column; box-sizing: border-box;
    width: 11in; height: 8.5in; padding: 0.32in 0.42in 0.28in;
    page-break-after: always; break-after: page; page-break-inside: avoid;
    overflow: hidden;
  }
  .page:last-child { page-break-after: auto; break-after: auto; }
  .page[hidden] { display: flex; }
  header { display: flex; align-items: center; gap: 16px; }
  .badge { background: #e31c3d; color: #fff; font-size: 28px; font-weight: 700;
    min-width: 56px; height: 56px; border-radius: 12px; display: flex;
    align-items: center; justify-content: center; }
  h1 { font-size: 28px; margin: 0; flex: 1; }
  .bin { font-size: 16px; color: #444; }
  .body { flex: 1; display: grid; grid-template-columns: 280px 1fr;
    gap: 24px; align-items: center; min-height: 0; }
  aside { background: #f4f4f4; border-radius: 12px; padding: 16px; }
  aside h2 { margin: 0 0 8px; font-size: 14px; text-transform: uppercase;
    letter-spacing: .06em; color: #666; }
  aside ul { margin: 0; padding-left: 18px; }
  .copy { margin-top: 16px; font-size: 18px; line-height: 1.35; }
  .hero { width: 100%; height: auto; max-height: 6.2in; object-fit: contain;
    background: #fff; }
  .placeholder { min-height: 3.2in; display: flex; align-items: center;
    justify-content: center; background: #f4f4f4; border-radius: 12px;
    font-size: 22px; padding: 24px; text-align: center; }
  footer { display: flex; align-items: center; justify-content: space-between;
    gap: 16px; margin-top: 12px; }
  .check { flex: 1; font-size: 16px; color: #333; }
  .nav { display: none !important; }
  .slide { background: #06341f; color: #fff;
    -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .slide .scene { flex: 1; display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 16px; min-height: 0; }
  .slide .stage { position: relative; display: inline-block; min-height: 0; }
  .slide .art { display: block; max-width: 100%; max-height: 5.3in;
    border-radius: 16px; }
  .slide .plate { background: #fff; padding: 12px; box-sizing: border-box; }
  .slide .peek { position: absolute; right: -6%; bottom: -8%; width: 30%;
    max-width: 280px; }
  .slide .tell { margin: 0; max-width: 22ch; text-align: center;
    font-size: 36px; line-height: 1.2; font-weight: 700; }
  .slide .check { color: #9fd9b6; font-size: 16px; }
  .slide footer { justify-content: flex-start; }
"""


def _stacked_html(src: str) -> str:
    """Flipbook HTML -> one long booklet: every page visible, no Next/Back."""
    text = re.sub(
        r"<style>.*?</style>",
        "<style>\n" + STACKED_STYLE + "\n</style>",
        src,
        count=1,
        flags=re.S,
    )
    text = text.replace(" hidden>", ">")
    text = re.sub(
        r'<div class="nav">\s*'
        r'<button type="button" class="back">Back</button>\s*'
        r'<button type="button" class="next">Next</button>\s*'
        r"</div>",
        "",
        text,
    )
    text = re.sub(r"<script>.*?</script>", "", text, flags=re.S)
    return text


def _run_chrome_pdf(url: str, pdf_path: Path, timeout: float = 120) -> str:
    """Print URL to PDF. Chrome often hangs after writing (updater), so stop it."""
    pdf_path.unlink(missing_ok=True)
    log: list[str] = []
    with tempfile.TemporaryDirectory(prefix="spike-pdf-") as tmp:
        cmd = [
            str(CHROME),
            "--headless",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-background-networking",
            "--disable-component-update",
            "--disable-sync",
            "--disable-extensions",
            "--no-first-run",
            "--no-default-browser-check",
            "--no-pdf-header-footer",
            "--mute-audio",
            "--allow-file-access-from-files",
            f"--user-data-dir={tmp}",
            f"--print-to-pdf={pdf_path}",
            url,
        ]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
        )

        def _read() -> None:
            if not proc.stdout:
                return
            for line in proc.stdout:
                log.append(line)

        threading.Thread(target=_read, daemon=True).start()
        deadline = time.time() + timeout
        last_size = -1
        stable = 0
        try:
            while time.time() < deadline:
                if any("bytes written to file" in line for line in log):
                    time.sleep(0.4)
                    break
                if pdf_path.is_file():
                    size = pdf_path.stat().st_size
                    if size > 1000 and size == last_size:
                        stable += 1
                        if stable >= 4:
                            break
                    else:
                        stable = 0
                    last_size = size
                if proc.poll() is not None:
                    break
                time.sleep(0.5)
            else:
                raise TimeoutError(f"Chrome did not finish {pdf_path} in {timeout:.0f}s")
        finally:
            # macOS answers EPERM, not ESRCH, when the group's only members
            # left are zombies -- Chrome already exited. Both mean "gone".
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                pass
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
                proc.wait(timeout=3)
    return "".join(log)


# Cloudflare Pages refuses a file over 25 MiB. A step hero is a 2000x1500
# PNG, and thirty of those blow the limit. The PDF flattens each one onto
# white (that's the paper) and writes a JPEG. The click-through keeps the
# PNGs.
PDF_JPEG_LONG = 1400
PDF_JPEG_QUALITY = 75
_IMG_SRC = re.compile(r'(<img\b[^>]*\bsrc=")([^"]+)(")')


def _shrink_for_pdf(html_text: str, build: Path, dest: Path) -> str:
    """Rewrite image srcs to smaller files living next to the booklet HTML."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit(
            "Pillow is needed to shrink the PDF images.\n"
            "  python3 -m pip install -r requirements.txt"
        )
    cache: dict[tuple[str, bool], str] = {}

    def shrunk(src: str, flatten: bool) -> str:
        key = (src, flatten)
        if key in cache:
            return cache[key]
        path = (build / src).resolve()
        if not path.is_file():
            return src
        im = Image.open(path).convert("RGBA")
        if max(im.size) > PDF_JPEG_LONG:
            scale = PDF_JPEG_LONG / max(im.size)
            im = im.resize(
                (round(im.width * scale), round(im.height * scale)),
                Image.LANCZOS,
            )
        stem = Path(src).stem
        if flatten:
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1])
            out = dest / f"{stem}.jpg"
            bg.save(
                out, "JPEG", quality=PDF_JPEG_QUALITY, optimize=True, progressive=True
            )
        else:
            out = dest / f"{stem}.png"
            im.save(out, "PNG", optimize=True)
        cache[key] = out.name
        return out.name

    def repl(match: re.Match[str]) -> str:
        src = match.group(2)
        if not src.lower().endswith(".png"):
            return match.group(0)
        blob = match.group(1) + match.group(3)
        # Heroes and plated renders sit on white paper. Story art and the
        # peek overlay keep their transparency, just smaller.
        flatten = "hero" in blob or "plate" in blob
        return f"{match.group(1)}{shrunk(src, flatten)}{match.group(3)}"

    return _IMG_SRC.sub(repl, html_text)


def write_pdf(build: Path) -> Path:
    """One landscape PDF page per instruction page, no Next/Back chrome."""
    preview = build / "preview.html"
    if not preview.is_file():
        write_preview(build)
    pdf_path = (build / "preview.pdf").resolve()
    if not CHROME.is_file():
        sys.exit(f"need Google Chrome at {CHROME} to write {pdf_path}")
    with tempfile.TemporaryDirectory(prefix="spike-book-") as tmp:
        dest = Path(tmp)
        booklet = _shrink_for_pdf(_stacked_html(preview.read_text()), build, dest)
        stacked_path = dest / "booklet.html"
        stacked_path.write_text(booklet)
        log = _run_chrome_pdf(stacked_path.as_uri(), pdf_path, timeout=300)
    if not pdf_path.is_file() or pdf_path.stat().st_size < 1000:
        sys.stderr.write(log)
        sys.exit(f"Chrome failed to write {pdf_path}")
    mebibytes = pdf_path.stat().st_size / (1024 * 1024)
    print(f"wrote {pdf_path} ({mebibytes:.1f} MiB)")
    if mebibytes > 25:
        print(
            f"warning: {pdf_path.name} is over Cloudflare Pages' 25 MiB limit",
            file=sys.stderr,
        )
    return pdf_path


def _leocad_cmd(
    model: Path,
    png: Path,
    step: int,
    camera: str,
    highlight: bool,
    fade: bool = True,
) -> list[str]:
    cmd = [
        str(LEOCAD),
        str(model),
        "-i", str(png),
        "-w", str(RENDER_W),
        "-h", str(RENDER_H),
        "-f", str(step),
        "-t", str(step),
        "--line-width", LINE_WIDTH,
        "--aa-samples", AA_SAMPLES,
    ]
    # A step hero ghosts the history so the new piece stands out. A story
    # hero is the finished animal, so everything on it must be full colour.
    if fade:
        cmd.extend(["--fade-steps", "--fade-steps-color", FADE_COLOR])
    else:
        cmd.append("--no-fade-steps")
    if highlight:
        cmd.extend(["--highlight", "--highlight-color", HIGHLIGHT_COLOR])
    else:
        cmd.append("--no-highlight")
    cam = camera.strip()
    if cam in VIEWPOINTS:
        cmd.extend(["--viewpoint", cam])
    else:
        parts = cam.split()
        if len(parts) == 2:
            cmd.extend(["--camera-angles", parts[0], parts[1]])
        else:
            cmd.extend(["--camera-angles", "55", "225"])
    return cmd


def fit_hero(png: Path) -> None:
    """Trim the transparent margin and pad back out to one hero size.

    LeoCAD sizes every step's view to the finished model, so early steps
    render tiny and off-centre. The PNG is RGBA, so the drawn pixels are
    exactly the non-transparent ones and the trim is unambiguous."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit(
            "Pillow is needed to fit the renders to the page.\n"
            "  python3 -m pip install -r requirements.txt"
        )
    im = Image.open(png).convert("RGBA")
    box = im.getbbox()
    if box is None:
        return
    im = im.crop(box)
    margin = int(HERO_MARGIN * max(im.size))
    w, h = im.width + 2 * margin, im.height + 2 * margin
    # Grow the short side so the result is exactly the hero aspect.
    if w * HERO_H < h * HERO_W:
        w = round(h * HERO_W / HERO_H)
    else:
        h = round(w * HERO_H / HERO_W)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(im, ((w - im.width) // 2, (h - im.height) // 2))
    out.resize((HERO_W, HERO_H), Image.LANCZOS).save(png)


def render_build(build: Path) -> int:
    if not LEOCAD.is_file():
        sys.exit(f"LeoCAD not found at {LEOCAD}")
    screens = parse_screens(build / "screens.md")
    model = build / "model.ldr"
    (build / "renders").mkdir(exist_ok=True)
    failed = 0
    env = os.environ.copy()
    for sc in screens:
        if not sc.has_png:
            print(f"skip step {sc.number} (no PNG)")
            continue
        png = build / sc.png
        cmd = _leocad_cmd(
            model, png, sc.number, sc.camera, sc.highlight.startswith("y")
        )
        print(" ".join(cmd))
        before = png.stat().st_mtime if png.is_file() else 0
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        # LeoCAD on Mac prints pasteboard errors to stderr and often
        # exits non-zero even after writing a valid PNG. Trust the file,
        # not the exit code -- but the file must be *new*.
        if (
            png.is_file()
            and png.stat().st_size > 1000
            and png.stat().st_mtime > before
        ):
            fit_hero(png)
            print(f"ok  step {sc.number} -> {png.name}")
        else:
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            print(f"FAIL step {sc.number} (exit {result.returncode})")
            failed += 1
    # Story slides that name a camera are LeoCAD shots of the *finished*
    # model, so the "here is what you are making" page cannot drift.
    max_step = max((s.number for s in screens if s.has_png), default=1)
    for sl in parse_story(build / "story.md"):
        if not (sl.is_render and sl.has_art):
            continue
        png = build / sl.art
        cmd = _leocad_cmd(
            model, png, max_step, sl.camera, highlight=False, fade=False
        )
        print(" ".join(cmd))
        before = png.stat().st_mtime if png.is_file() else 0
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if (
            png.is_file()
            and png.stat().st_size > 1000
            and png.stat().st_mtime > before
        ):
            fit_hero(png)
            print(f"ok  slide {sl.number} -> {png.name}")
        else:
            print(result.stderr, file=sys.stderr)
            print(f"FAIL slide {sl.number} (exit {result.returncode})")
            failed += 1

    # Check views of the finished model, same default camera as before.
    checks = {
        "check-iso.png": ["--camera-angles", "55", "225"],
        "check-front.png": ["--viewpoint", "front"],
        "check-left.png": ["--viewpoint", "left"],
        "check-top.png": ["--viewpoint", "top"],
    }
    for name, cam in checks.items():
        png = build / "renders" / name
        cmd = [
            str(LEOCAD), str(model), "-i", str(png),
            "-w", str(RENDER_W), "-h", str(RENDER_H),
            "-f", str(max_step), "-t", str(max_step),
            "--line-width", LINE_WIDTH, "--aa-samples", AA_SAMPLES,
        ] + cam
        print(" ".join(cmd))
        before = png.stat().st_mtime if png.is_file() else 0
        result = subprocess.run(cmd, env=os.environ.copy(), capture_output=True, text=True)
        if (
            png.is_file()
            and png.stat().st_size > 1000
            and png.stat().st_mtime > before
        ):
            fit_hero(png)
            print(f"ok  {name}")
        else:
            print(result.stderr, file=sys.stderr)
            print(f"FAIL {name} (exit {result.returncode})")
            failed += 1
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_ in (
        ("check", "three-way sync of 0 STEP, steps.md, screens.md, renders"),
        ("preview", "write preview.html from steps.md + screens.md"),
        ("pdf", "write preview.pdf: one landscape sheet per page, no Next/Back"),
        ("render", "LeoCAD export of each screens.md row"),
    ):
        p = sub.add_parser(name, help=help_)
        p.add_argument("build", type=Path)
    args = parser.parse_args()
    build = args.build
    if not build.is_absolute():
        build = (Path.cwd() / build).resolve()
    if args.command == "check":
        return check_build(build)
    if args.command == "preview":
        write_preview(build)
        return 0
    if args.command == "pdf":
        write_pdf(build)
        return 0
    return render_build(build)


if __name__ == "__main__":
    sys.exit(main())
