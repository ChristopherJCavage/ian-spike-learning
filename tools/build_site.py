#!/usr/bin/env python3
"""Build the public STEM site into site/dist/.

Words come from site/content/. The look matches the Daily House brief.
The site is public: nothing here adds a login.
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "site" / "web"
DIST = ROOT / "site" / "dist"
ORIGIN = "https://stem.galaxymoose.com"

NAV = [
    ("projects", "/projects/", "Projects"),
    ("kits", "/kits/", "Kits"),
    ("how", "/how/", "How It's Made"),
    ("about", "/about/", "About"),
]

FOOTER = """
<footer class="footer">
  <p class="links">Galaxy Moose Software · Everything on this site is free · <a href="/legal/">CC BY 4.0</a> · <a href="/legal/">Legal</a> · <a href="https://github.com/ChristopherJCavage/ian-spike-learning">GitHub</a></p>
  <p class="fine">LEGO® is a trademark of the LEGO Group of companies which does not sponsor, authorize or endorse this site. SPIKE™, LEGO® Education, the Minifigure, and Technic® are trademarks of the LEGO Group. This site is unofficial.</p>
  <p class="fine">Elenco® and Snap Circuits® are registered trademarks of Elenco Electronics, LLC, which does not sponsor, authorize or endorse this site.</p>
</footer>
"""


def page(path: str, title: str, description: str, active: str, main: str, image: str) -> None:
    nav = []
    for key, href, label in NAV:
        current = ' aria-current="page"' if key == active else ""
        nav.append(f'<li><a href="{href}"{current}>{label}</a></li>')
    canonical = ORIGIN + path
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{description}">
  <meta name="robots" content="index, follow">
  <meta name="theme-color" content="#0e0f13">
  <link rel="canonical" href="{canonical}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{ORIGIN}{image}">
  <meta property="og:type" content="website">
  <meta name="twitter:card" content="summary_large_image">
  <title>{title}</title>
  <link rel="icon" href="/media/favicon.png" type="image/png">
  <link rel="apple-touch-icon" href="/media/apple-touch-icon.png">
  <link rel="stylesheet" href="/css/site.css">
</head>
<body>
  <div class="shell">
    <nav class="side" aria-label="Site">
      <a class="brand" href="/">
        <img class="brand-icon" src="/media/moose.png" alt="">
        <span class="brand-text">
          <span class="brand-mark">STEM Builds</span>
          <span class="brand-sub">Galaxy Moose</span>
        </span>
      </a>
      <ol class="nav-list">
        {''.join(nav)}
      </ol>
    </nav>
    <div class="main">
      <main>
        {main}
      </main>
      {FOOTER}
    </div>
  </div>
</body>
</html>
"""
    out = DIST / path.lstrip("/")
    if path.endswith("/"):
        out = out / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"page {path}")


def spike_badge() -> str:
    return """<span class="badge" aria-label="Essential needed. Prime not needed. Expansion not needed.">
      <span class="seg on">Essential</span>
      <span class="seg off">Prime</span>
      <span class="seg off">Expansion</span>
    </span>"""


def snap_badge() -> str:
    return """<span class="pills" aria-label="Beginner and Junior needed.">
      <span class="seg on">Beginner</span>
      <span class="seg on">Junior</span>
    </span>"""


def tag(kind: str) -> str:
    if kind == "club":
        return '<span class="pill green">Club-Ready</span>'
    return '<span class="pill blue">Home Build</span>'


def indicator(rows: list[tuple[str, bool]], hub: str | None) -> str:
    items = []
    for label, needed in rows:
        mark = '<span class="on">Needed</span>' if needed else '<span class="off">Not needed</span>'
        items.append(f"<li><span>{label}</span>{mark}</li>")
    if hub:
        items.append(f"<li><span>Hub</span><span>{hub}</span></li>")
    return '<ul class="indicator">' + "".join(items) + "</ul>"


SPIKE_ROWS = [
    ("Essential 45345", True),
    ("Prime 45678", False),
    ("Expansion 45681", False),
]
SNAP_ROWS = [
    ("Snap Circuits® Beginner SCB-20", True),
    ("Snap Circuits® Junior SC-100", True),
]


def copy_media() -> None:
    pairs = [
        ("site/assets/home/hero-crew.png", "media/hero-crew.png"),
        ("site/photos/rainforest-seed-mission/hero-1600.jpg", "media/seed-mission-hero.jpg"),
        ("site/photos/night-skate-cases/door-1600.jpg", "media/night-skate-door.jpg"),
        ("site/photos/night-skate-cases/hero-1600.jpg", "media/night-skate-hero.jpg"),
        ("builds/seed-drone/photos/hero-1600.jpg", "media/seed-drone-hero.jpg"),
        ("builds/seed-drone/photos/iso-1600.jpg", "media/seed-drone-iso.jpg"),
        ("builds/seed-drone/photos/program-1600.jpg", "media/seed-drone-program.jpg"),
        ("builds/seed-drone/renders/check-iso.png", "media/seed-drone-drawn.png"),
        ("builds/rainforest-drop-zone/photos/hero-1600.jpg", "media/drop-zone-hero.jpg"),
        ("builds/rainforest-drop-zone/renders/check-iso.png", "media/drop-zone-drawn.png"),
        ("builds/rainforest-chameleon/photos/hero-1600.jpg", "media/chameleon-hero.jpg"),
        ("builds/rainforest-chameleon/photos/program-1600.jpg", "media/chameleon-program.jpg"),
        ("builds/rainforest-chameleon/renders/check-iso.png", "media/chameleon-drawn.png"),
        ("builds/hot-press/photos/hero-1600.jpg", "media/hot-press-hero.jpg"),
        ("builds/hot-press/photos/program-1600.jpg", "media/hot-press-program.jpg"),
        ("builds/hot-press/renders/check-iso.png", "media/hot-press-drawn.png"),
    ]
    for src, dest in pairs:
        target = DIST / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / src, target)


def copy_lessons() -> None:
    lessons = [
        ("seed-drone", "builds/seed-drone", "preview.pdf", "seed-drone.pdf"),
        ("rainforest-drop-zone", "builds/rainforest-drop-zone", "preview_RainforestTile.pdf", "rainforest-drop-zone.pdf"),
        ("rainforest-chameleon", "builds/rainforest-chameleon", "preview.pdf", "rainforest-chameleon.pdf"),
        ("hot-press", "builds/hot-press", "preview.pdf", "hot-press.pdf"),
        ("night-skate-cases", "builds/snap-01-the-loop", None, None),
    ]
    for slug, folder, pdf_name, public_pdf in lessons:
        src = ROOT / folder
        steps = DIST / "builds" / slug / "steps"
        if steps.exists():
            shutil.rmtree(steps)
        shutil.copytree(src / "renders", steps / "renders")
        shutil.copy2(src / "preview.html", steps / "index.html")
        if pdf_name and public_pdf:
            shutil.copy2(src / pdf_name, DIST / "builds" / slug / public_pdf)
        print(f"lesson {slug}")


def home() -> None:
    main = f"""
<header class="hero">
  <div class="hero-rule">
    <h1>Welcome</h1>
  </div>
  <p class="lede">Hi, I'm Chris Cavage, and my son is Ian. He's in elementary school, and we do STEM projects together at home. I'm a software engineer by trade, and I wish I'd had kits like these when I was his age. Right now it's our three LEGO® SPIKE™ sets, the LEGO® Education Simple Machines set, and an Elenco® Snap Circuits® kit, where we snap together our own circuits.</p>
  <div class="actions">
    <a class="btn btn-primary" href="/projects/">See the Projects</a>
    <a class="btn btn-ghost" href="/how/">How It's Made</a>
  </div>
</header>
<section class="section prose">
  <h2>Why We Started Making Our Own</h2>
  <p>We've already worked through every LEGO® SPIKE™ Essential unit in the LEGO® SPIKE™ App. Ian's still a little young to explore the app on his own without a lesson to follow, so I make new lessons for him with <a href="https://www.leocad.org/">LeoCAD</a> (free, open-source building software), Anthropic's Claude models, xAI's Grok models, and a few custom Python scripts.</p>
  <p>We're also part of the LEGO® robotics club at the Contemporary Chinese School of Arizona (CCSA), and when the coach needs another lesson, I help out there too. This year's theme was rainforests, and the app didn't have enough lessons to fill the semester. That's where the Seed Drone, the Drop Zone, the Chameleon, and the Hot Press came from.</p>
  <p>The Elenco® Snap Circuits® manuals are the official experiments, and they didn't quite land for us. A page tells you to snap a part, and not what to look for. I wanted each page to do one job: a problem, a guess, a test, and then the reason.</p>
  <p>That's The Spark Detectives. Sully, Tika, Pip, and Coco run a little detective agency, and each case is one circuit, told as a comic. I took the shape of those pages from Beast Academy®, the math comic from Art of Problem Solving®. Ian loves those books. The way a lesson moves is theirs. The characters and the cases are ours.</p>
  <p>I made this site for other parents with young kids. Maybe you have a LEGO® SPIKE™ set or two, maybe an Elenco® Snap Circuits® kit, or maybe you're just looking for ideas to keep STEM going at home. Use any of it however you like.</p>
  <p>The LEGO Group stopped selling SPIKE™ on June 30, 2026, but the SPIKE™ App is supported through June 30, 2031. The Simple Machines set was retired years earlier, but it's all gears, levers, pulleys, and wheels, with no app or batteries, so it doesn't go out of date. You can still find both secondhand or from resellers, and they're still a great way to teach kids how machines work. <a href="/kits/">Kits</a></p>
</section>
<section class="section">
  <div class="doors">
    <article class="card">
      <div class="photo-card"><img src="/media/seed-mission-hero.jpg" alt="The Rainforest Seed Mission on our kitchen table."></div>
      <div class="card-copy">
        <h2>SPIKE™</h2>
        <p>Seed Mission, the Chameleon, and the Hot Press. All three come out of one Essential box.</p>
        {spike_badge()}
        <a class="btn btn-primary" href="/projects/#spike">See the SPIKE™ Builds</a>
      </div>
    </article>
    <article class="card">
      <div class="photo-card"><img src="/media/night-skate-door.jpg" alt="The Case 1 board, with Coco, Pip, and Tika on the empty side of the table."></div>
      <div class="card-copy">
        <h2>Snap Circuits®</h2>
        <p>The Spark Detectives, Chapter 1: The Night Skate Cases. Five cases, one sitting each.</p>
        {snap_badge()}
        <a class="btn btn-primary" href="/builds/night-skate-cases/">Start Chapter 1</a>
      </div>
    </article>
  </div>
</section>
"""
    page(
        "/",
        "STEM Builds",
        "Original STEM projects Chris and Ian build at home, with printable steps for SPIKE and Snap Circuits.",
        "",
        main,
        "/media/seed-mission-hero.jpg",
    )


def projects() -> None:
    main = f"""
<header class="hero">
  <div class="hero-rule">
    <p class="eyebrow">Projects</p>
    <h1>What We've Built So Far</h1>
  </div>
  <p class="lede">Some ideas are one build. Some are two that work together. The badge on each card shows which kit, and which boxes of it, you need.</p>
  <p class="lede">A kit family gets a section here when its first build is published, in the same order as <a href="/kits/">Kits</a>.</p>
</header>
<h2 class="family" id="spike">LEGO® SPIKE™</h2>
<div class="stack">
  <article class="card card-wide">
    <div class="photo-card"><img src="/media/seed-mission-hero.jpg" alt="The Rainforest Seed Mission on our kitchen table."></div>
    <div class="card-copy">
      <div class="title-row"><h3>Rainforest Seed Mission</h3><span class="count">2 builds</span></div>
      <p>Skim a survey drone over the rainforest. When its color sensor sees the red band where a tree was cut down, it drops a seed. Both builds come out of the same box.</p>
      {spike_badge()}
      <ul class="build-rows">
        <li><a href="/builds/seed-drone/">Seed Drone</a> — the drone. Color sensor, motor, Icon Blocks.</li>
        <li><a href="/builds/rainforest-drop-zone/">Rainforest Drop Zone</a> — the forest it flies over. No electronics, about ten minutes.</li>
      </ul>
      <a class="btn btn-primary" href="/projects/rainforest-seed-mission/">Open the Project</a>
    </div>
  </article>
  <div class="card-row">
    <article class="card">
      <div class="photo-card taken"><img src="/media/chameleon-card.jpg" alt="The Chameleon Color-Match on our kitchen table, light on and eyes down."></div>
      <div class="card-copy">
        <h3>Chameleon Color-Match</h3>
        <p>A chameleon that looks at a color and changes its back to match. Show it red and it flashes a warning instead of hiding.</p>
        {spike_badge()}
        <div class="actions">
          <a class="btn btn-primary" href="/builds/rainforest-chameleon/rainforest-chameleon.pdf">Print the PDF</a>
          <a class="btn btn-ghost" href="/builds/rainforest-chameleon/steps/">Click Through the Steps</a>
        </div>
      </div>
    </article>
    <article class="card">
      <div class="photo-card"><img src="/media/hot-press-hero.jpg" alt="The Hot Press model on our kitchen table."></div>
      <div class="card-copy">
        <h3>Hot Press</h3>
        <p>A motor with big eyes brings a red press head down onto two plates of old wood and lifts it again. The wood stays thick. Red bricks and a red light stand in for the heat.</p>
        {spike_badge()}
        <div class="actions">
          <a class="btn btn-primary" href="/builds/hot-press/hot-press.pdf">Print the PDF</a>
          <a class="btn btn-ghost" href="/builds/hot-press/steps/">Click Through the Steps</a>
        </div>
      </div>
    </article>
  </div>
</div>
<h2 class="family" id="snap">Elenco® Snap Circuits®</h2>
<article class="card" style="max-width: 560px">
  <div class="photo-card"><img src="/media/night-skate-hero.jpg" alt="The Night Skate Cases board."></div>
  <div class="card-copy">
    <h3>The Night Skate Cases</h3>
    <p>The Spark Detectives, Chapter 1. Five short cases about one loop of electricity, snapped on a real board. A grown-up puts the batteries in.</p>
    {snap_badge()}
    <a class="btn btn-primary" href="/builds/night-skate-cases/">Start Chapter 1</a>
  </div>
</article>
"""
    page("/projects/", "Projects · STEM Builds", "The builds we've finished and tested at the table.", "projects", main, "/media/seed-mission-hero.jpg")


def mission() -> None:
    main = f"""
<p class="crumbs"><a href="/projects/">Projects</a> &gt; Rainforest Seed Mission</p>
<header class="hero">
  <div class="split">
    <div class="build-copy">
      <div class="hero-rule" style="width:100%">
        <p class="eyebrow">Project</p>
        <h1>Rainforest Seed Mission</h1>
      </div>
      <div class="meta-row">{spike_badge()} {tag("club")}</div>
      <p class="lede">Someone cut down a tree in the rainforest. Your drone has to find the bare patch and plant a new seed. It's two builds that work together: the survey drone, and the strip of forest it flies over.</p>
      <p class="facts">2 builds · 75 parts · one SPIKE™ Essential box · about one session</p>
    </div>
    <div class="photo-hero"><img src="/media/seed-mission-hero.jpg" alt="The Rainforest Seed Mission on our kitchen table."></div>
  </div>
</header>
<section class="prose">
  <h2>How They Work Together</h2>
  <p>Both builds come out of one SPIKE™ Essential box, and you can make them in the same sitting. But the real point is that they work together. In the club, the lesson was how drones can help a rainforest grow back by dropping seeds into the bare patches where trees were cut down. The Drop Zone is a strip of forest with a red band where a tree used to be. The Seed Drone flies over it, and when its color sensor sees the red band, a motor tips its tray and the seed drops.</p>
  <h2>The Builds</h2>
</section>
<div class="card-row">
  <article class="card">
    <div class="photo-card"><img src="/media/seed-drone-hero.jpg" alt="The Seed Drone on our kitchen table."></div>
    <div class="card-copy">
      <h3>Seed Drone</h3>
      <p>The main build. A handheld drone with a color sensor underneath. When it sees red, a motor tips its tray and a seed rolls out.</p>
      <p class="facts">58 parts · 34 steps · Icon Blocks</p>
      <a class="btn btn-primary" href="/builds/seed-drone/">Open the Build</a>
    </div>
  </article>
  <article class="card">
    <div class="photo-card"><img src="/media/drop-zone-hero.jpg" alt="The Rainforest Drop Zone on our kitchen table."></div>
    <div class="card-copy">
      <h3>Rainforest Drop Zone</h3>
      <p>The companion build. A strip of forest with trees, a frog, a ranger, and a red band where the tree used to be. No electronics.</p>
      <p class="facts">17 parts · 9 steps · no program</p>
      <a class="btn btn-primary" href="/builds/rainforest-drop-zone/">Open the Build</a>
    </div>
  </article>
</div>
<section class="prose">
  <h2>Talking About It</h2>
  <p>Say up front that it's a model and won't take off. Real drones also map damaged forest from the air, so planting crews know where to go. A good question to ask afterward is why the rotor doesn't spin on its own. The hub only has two ports, so an engineer has to choose which parts get a motor and which just come along for the ride.</p>
  <h2>What You Need</h2>
  {indicator(SPIKE_ROWS, "Small Hub (Essential)")}
</section>
"""
    page("/projects/rainforest-seed-mission/", "Rainforest Seed Mission · STEM Builds", "Two builds from one SPIKE Essential box: a survey drone and the forest it flies over.", "projects", main, "/media/seed-mission-hero.jpg")


def build_page(
    slug: str,
    title: str,
    description: str,
    crumbs: str,
    badge: str,
    kind: str,
    lead: str,
    facts: str,
    actions: str,
    pdf_note: str,
    goes: str,
    hero: str,
    hero_alt: str,
    drawn: str | None,
    body: str,
    image: str,
) -> None:
    thumb = ""
    if drawn:
        thumb = f'<figure class="as-drawn"><img src="{drawn}" alt="As drawn in LeoCAD."><figcaption>As Drawn</figcaption></figure>'
    main = f"""
{crumbs}
<header class="hero">
  <div class="split">
    <div class="build-copy">
      <div class="hero-rule" style="width:100%">
        <h1>{title}</h1>
      </div>
      <div class="meta-row">{badge} {tag(kind)}</div>
      <p class="lede">{lead}</p>
      <p class="facts">{facts}</p>
      <div class="actions">{actions}</div>
      {pdf_note}
      {goes}
    </div>
    <div class="media">
      <div class="photo-hero"><img src="{hero}" alt="{hero_alt}"></div>
      {thumb}
    </div>
  </div>
</header>
<section class="prose">
  {body}
</section>
"""
    page(f"/builds/{slug}/", f"{title} · STEM Builds", description, "projects", main, image)


def builds() -> None:
    pdf = lambda slug, note: (
        f'<a class="btn btn-primary" href="/builds/{slug}/{slug}.pdf">Print the PDF</a>'
        f'<a class="btn btn-ghost" href="/builds/{slug}/steps/">Click Through the Steps</a>',
        f'<p class="pdf-note">{note}</p>',
    )
    seed_actions, seed_note = pdf("seed-drone", "41 pages · US Letter · print in color · 15 MB")
    drop_actions, drop_note = pdf("rainforest-drop-zone", "10 pages · US Letter · print in color · 9 MB")
    cham_actions, cham_note = pdf("rainforest-chameleon", "32 pages · US Letter · print in color · 16 MB")
    hot_actions, hot_note = pdf("hot-press", "27 pages · US Letter · print in color · 15 MB")
    mission_crumbs = '<p class="crumbs"><a href="/projects/">Projects</a> &gt; <a href="/projects/rainforest-seed-mission/">Rainforest Seed Mission</a> &gt; {name}</p>'
    one_crumbs = '<p class="crumbs"><a href="/projects/">Projects</a> &gt; {name}</p>'

    build_page(
        "seed-drone",
        "Seed Drone",
        "A handheld drone that hunts for the red band in the forest and drops a seed on it.",
        mission_crumbs.format(name="Seed Drone"),
        spike_badge(),
        "club",
        "A handheld drone that hunts for the red band in the forest and drops a seed on it.",
        "58 parts · 34 steps · Icon Blocks · about one session",
        seed_actions,
        seed_note,
        '<p class="goes"><span>Goes with</span> <a href="/builds/rainforest-drop-zone/">Rainforest Drop Zone →</a> <span>the patch of forest it flies over</span></p>',
        "/media/seed-drone-hero.jpg",
        "The Seed Drone on our kitchen table.",
        "/media/seed-drone-drawn.png",
        f"""
        <h2>How It Works</h2>
        <p>A color sensor points down from under the body. When it sees red, a small motor tips the little tray on the tail and a loose red ball, the seed, rolls out. The big two-blade rotor on top spins when you flick it but isn't powered. The Small Hub only has two ports, and the sensor and the tray motor use both.</p>
        <figure class="photo-screenshot"><img src="/media/seed-drone-program.jpg" alt="The Seed Drone program in the SPIKE App, cropped to the blocks."></figure>
        <p>The program is one stack. When the sensor on port A sees red, the motor on port B turns a quarter turn to tip the tray, the hub plays a sound while the seed rolls out, and the motor turns back so the tray is level for the next one.</p>
        <h2>What You Need</h2>
        {indicator(SPIKE_ROWS, "Small Hub (Essential)")}
        <ul>
          <li>One SPIKE™ Essential set: the Small Hub (charged), one small motor, and the color sensor.</li>
          <li>A tablet or laptop with the official SPIKE™ App. Essential runs the program from the tablet, so keep it connected while kids play.</li>
          <li>The Rainforest Drop Zone, or any red patch about four studs wide on a white surface.</li>
          <li>One of the red balls from the box as the seed. There are five.</li>
        </ul>
        <p class="small">Small print: Original model, not one of the official SPIKE™ lesson units.</p>
        """,
        "/media/seed-drone-hero.jpg",
    )
    build_page(
        "rainforest-drop-zone",
        "Rainforest Drop Zone",
        "The patch of forest the Seed Drone flies over, with a red band where a tree used to be.",
        mission_crumbs.format(name="Rainforest Drop Zone"),
        spike_badge(),
        "club",
        "The patch of forest the Seed Drone flies over, with a red band across the middle where a tree used to be. It's the short build, with no electronics, and it's done in about ten minutes.",
        "17 parts · 9 steps · no program · about ten minutes",
        drop_actions,
        drop_note,
        '<p class="goes"><span>Goes with</span> <a href="/builds/seed-drone/">Seed Drone →</a> <span>the drone that flies over it</span></p>',
        "/media/drop-zone-hero.jpg",
        "The Rainforest Drop Zone on our kitchen table.",
        "/media/drop-zone-drawn.png",
        f"""
        <h2>What's on It</h2>
        <p>A long white plate with a green wall down each side, a tree at each end, some grass, a frog, and a ranger holding the drone's controller. Two red tiles cross the lane between the walls, and that red band is what the drone's color sensor is looking for. Each step adds one kind of piece, so it's a good first build for the youngest kids in the room.</p>
        <h2>What You Need</h2>
        {indicator(SPIKE_ROWS, "none (no electronics)")}
        <ul>
          <li>The plates, tiles, trees, frog, and figure from one SPIKE™ Essential set, and nothing from the electronics. It shares no parts with the Seed Drone, so both can be built from the same box at once.</li>
          <li>The Seed Drone, to fly over it. On its own it's just a nice diorama.</li>
        </ul>
        <p class="small">Small print: Original model, not one of the official SPIKE™ lesson units.</p>
        """,
        "/media/drop-zone-hero.jpg",
    )
    build_page(
        "rainforest-chameleon",
        "Chameleon Color-Match",
        "A chameleon that looks at a color and changes its back to match.",
        one_crumbs.format(name="Chameleon Color-Match"),
        spike_badge(),
        "club",
        "A chameleon that looks at a color and changes its back to match. Show it red and it flashes a warning instead of hiding.",
        "54 parts · 26 steps · Icon Blocks · about one session",
        cham_actions,
        cham_note,
        "",
        "/media/chameleon-hero.jpg",
        "The Chameleon Color-Match model on our kitchen table.",
        "/media/chameleon-drawn.png",
        f"""
        <h2>How It Works</h2>
        <p>Its head, looking down, is the color sensor, and its back is the 3x3 light matrix. Between them they use both of the hub's ports, so there's no motor. Hold a colored pad under its head and its back lights the same color. That's a fair first explanation of camouflage. Hold a red pad under it and the back goes red anyway, because some animals shout "don't eat me" instead of hiding. It has ball-joint legs, round white eyes, and a tail that turns a corner.</p>
        <figure class="photo-screenshot"><img src="/media/chameleon-program.jpg" alt="The Chameleon program in the SPIKE App, cropped to the blocks."></figure>
        <p>The program is four short stacks, one for each pad color, because Icon Blocks don't have an if-else. Each stack waits for its color and sets the matrix to match. Nothing turns the light off when the pad slides away, so the last color stays lit. That's how Icon Blocks work, not a mistake.</p>
        <h2>What You Need</h2>
        {indicator(SPIKE_ROWS, "Small Hub (Essential)")}
        <ul>
          <li>One SPIKE™ Essential set: the Small Hub (charged), the color sensor, and the light matrix.</li>
          <li>A tablet or laptop with the official SPIKE™ App.</li>
          <li>Five color pads, made ahead from the same box: one 2x4 tile each in blue, red, yellow, dark green, and azure, each on a plate so it slides.</li>
        </ul>
        <p class="small">Small print: Original model, not one of the official SPIKE™ lesson units. It started as the club's first rainforest lesson.</p>
        """,
        "/media/chameleon-hero.jpg",
    )
    build_page(
        "hot-press",
        "Hot Press",
        "A motor brings a red press head down onto two plates of old wood and lifts it again.",
        one_crumbs.format(name="Hot Press"),
        spike_badge(),
        "club",
        "A motor with big eyes brings a red press head down onto two plates of old wood and lifts it again. The wood stays thick.",
        "36 parts · 20 steps · Icon Blocks · about one session",
        hot_actions,
        hot_note,
        "",
        "/media/hot-press-hero.jpg",
        "The Hot Press model on our kitchen table.",
        "/media/hot-press-drawn.png",
        f"""
        <h2>How It Works</h2>
        <p>The motor sits high on a red tower, pinned by two pegs through its back. One peg in the motor's own hub is the crank. It pulls a blue beam, and the beam pushes a green plate down two black axles. The red brick under the plate is the press head. It stops just over the wood, so the motor never jams on it.</p>
        <figure class="photo-screenshot"><img src="/media/hot-press-program.jpg" alt="The Hot Press program in the SPIKE App, cropped to the blocks."></figure>
        <p>The program is one stack. The 3x3 matrix turns red, the motor turns half a turn and the press comes down, the hub plays a sound, the motor turns half a turn more and the press goes back up, and the matrix turns green. The wood doesn't get thinner. The single thin plate in front of the press is the picture of wood after a real press. The red bricks, a red crystal, and the red matrix stand in for heat. Nothing is heated.</p>
        <h2>What You Need</h2>
        {indicator(SPIKE_ROWS, "Small Hub (Essential)")}
        <ul>
          <li>One SPIKE™ Essential set: the Small Hub (charged), one small motor, and the light matrix.</li>
          <li>A tablet or laptop with the official SPIKE™ App. Essential runs the program from the tablet, so keep it connected while kids play.</li>
        </ul>
        <p class="small">Small print: Original model, not one of the official SPIKE™ lesson units.</p>
        """,
        "/media/hot-press-hero.jpg",
    )
    build_page(
        "night-skate-cases",
        "The Night Skate Cases",
        "The Spark Detectives, Chapter 1. Five cases about one loop of electricity.",
        one_crumbs.format(name="The Night Skate Cases"),
        snap_badge(),
        "home",
        "The Spark Detectives, Chapter 1. The skate park goes dark, and Ian snaps a loop that brings the light back. Five cases, one sitting each.",
        "5 cases · 113 pages · no code · a grown-up puts the batteries in",
        '<a class="btn btn-primary" href="/builds/night-skate-cases/steps/">Click Through the Cases</a>',
        "",
        "",
        "/media/night-skate-hero.jpg",
        "The Night Skate Cases board.",
        None,
        f"""
        <h2>How It Works</h2>
        <p>One loop, built once in Case 1 and changed a little in each case after. The battery holder rides the top edge of the mini grid. A slide switch, a red-and-yellow light with the egg on it, and three blue wires close the circle. Nothing here is a SPIKE™ program, so there is no screenshot.</p>
        <p>Each case is one new idea:</p>
        <ol>
          <li>No circle, no light. A switch, or a missing wire, is a gap.</li>
          <li>Some parts care which way round they go. Turn the light and it changes color.</li>
          <li>The button only lets power through while you hold it. The horn was quiet because it was in backwards.</li>
          <li>One switch can run two lights, if each light has its own way back.</li>
          <li>Guess first, then test it. Three missions, and no step pages.</li>
        </ol>
        <h2>What You Need</h2>
        {indicator(SNAP_ROWS, None)}
        <ul>
          <li>One Elenco® Snap Circuits® Beginner set (SCB-20) and one Snap Circuits® Junior set (SC-100). Every block is from the Beginner box except one extra blue 3-snap wire, which Case 4 takes from the Junior box.</li>
          <li>Three AA batteries. A grown-up puts them in and takes them out.</li>
        </ul>
        <p class="small">Small print: Original lessons, not one of the official Snap Circuits® lessons.</p>
        """,
        "/media/night-skate-hero.jpg",
    )


def kits() -> None:
    main = """
<header class="hero">
  <div class="hero-rule">
    <p class="eyebrow">Kits</p>
    <h1>Which Kit You Need for Which Build</h1>
  </div>
  <p class="lede">We build with three kits: LEGO® Education SPIKE™, the LEGO® Education Simple Machines set, and Elenco® Snap Circuits®. Every build says up front which one it needs. The badge on its card shows the boxes, and the checklist under What You Need spells out the set numbers.</p>
</header>
<h2 class="family">LEGO® SPIKE™</h2>
<p class="family-intro">LEGO® SPIKE™ comes in three boxes: Essential, Prime, and the Prime Expansion. At the Contemporary Chinese School of Arizona (CCSA), the LEGO® robotics club sticks to SPIKE™ Essential. An hour on Saturday is about one box, and that's the one the club has. At home we mix and match. We have all three, and the pieces are sorted into tackle boxes.</p>
<div class="kit-grid">
  <article class="kit-card">
    <h3>SPIKE™ Essential</h3>
    <p class="setno">Set 45345</p>
    <p>The club's box, made for kids around six to ten. It has a Small Hub with two ports, two small motors, a color sensor, a 3x3 light matrix, four LEGO® minifigures, and a tray of bricks. Two ports means every model picks exactly two of motor, motor, sensor, or matrix.</p>
    <a href="https://education.lego.com/en-us/products/lego-education-spike-essential-set/45345/">Official Product Page →</a>
  </article>
  <article class="kit-card">
    <h3>SPIKE™ Prime</h3>
    <p class="setno">Set 45678</p>
    <p>The bigger sibling for older kids: a Large Hub with six ports, bigger motors, and distance and force sensors. We have one at home. None of the Club-Ready builds need it.</p>
    <a href="https://education.lego.com/en-us/products/lego-education-spike-prime-set/45678/">Official Product Page →</a>
  </article>
  <article class="kit-card">
    <h3>SPIKE™ Prime Expansion</h3>
    <p class="setno">Set 45681</p>
    <p>An add-on for Prime with a lot more LEGO® Technic® pieces, one more motor, and a second color sensor. It has no hub of its own, so it only works alongside a Prime set.</p>
    <a href="https://education.lego.com/en-us/products/lego-education-spike-prime-expansion-set/45681/">Official Product Page →</a>
  </article>
</div>
<section class="panel prose" id="spike" style="max-width:none">
  <h2>About the Retirement</h2>
  <p>LEGO® Education retired the SPIKE™ line, and company sales of Essential and Prime ended on June 30, 2026. Nothing about the kits stopped working. The SPIKE™ App gets bug fixes and support for new operating systems until June 30, 2031, and the official teacher resources stay online until then too. Resellers still have some stock, and there's a healthy secondhand market.</p>
  <p>After 2031 the app will still be downloadable but won't be updated, so a future iPad or Chromebook might not run it. If that day comes, there's an open-source firmware called <a href="https://pybricks.com/">Pybricks</a> that runs on SPIKE™ hubs and doesn't depend on the LEGO Group's timeline. I haven't tried it myself yet, so treat it as a lead and not a recommendation.</p>
  <p>Source for the dates: <a href="https://education.lego.com/en-us/spike-update-2026/">LEGO® Education, SPIKE™ portfolio retirement</a>.</p>
</section>
<h2 class="family">LEGO® Simple Machines</h2>
<article class="kit-card" style="max-width: 420px">
  <h3>Simple Machines</h3>
  <p class="setno">Set 9689</p>
  <p>The LEGO® Education Simple Machines set. It came out in 2011 and has 204 pieces: gears, levers, pulleys, and wheels, with no motor, no hub, and no app, so it doesn't go out of date the way a programmable kit can. The LEGO Group no longer sells it. It turns up secondhand. I don't have a retirement date from the LEGO Group, so this page doesn't guess one.</p>
</article>
<h2 class="family">Elenco® Snap Circuits®</h2>
<p class="family-intro">Elenco® Snap Circuits® comes in boxes that share one snap system, and we have two of them. The parts snap onto a plastic grid, so we snap together our own circuits with no solder and no code. It isn't a LEGO® product. The blocks from the two boxes can share a grid. The limit is the battery. Junior parts are made for 3 volts, from two AA batteries. The Beginner holder uses three AA batteries, which is 4.5 volts. The Junior manual warns that the extra voltage can burn out a part, including the lamp wire, so a Junior part stays off that holder.</p>
<div class="card-row">
  <article class="kit-card">
    <h3>Snap Circuits® Beginner</h3>
    <p class="setno">SCB-20</p>
    <p>The small box: 14 parts on a mini grid, run by three AA batteries. A lamp, a red-and-yellow LED, a motor that glows while it spins, a horn, two switches, and the wires to join them. It doesn't upgrade to the bigger sets, but its blocks snap into them.</p>
    <a href="https://shop.elenco.com/consumers/snap-circuits-beginner.html">Official Product Page →</a>
  </article>
  <article class="kit-card">
    <h3>Snap Circuits® Junior</h3>
    <p class="setno">SC-100</p>
    <p>The bigger box: about 30 parts on a full-size grid, run by two AA batteries, with 100 experiments in its manual. It adds a speaker, a light sensor, and sound modules, and it's where the upgrade kits to the larger Snap Circuits® sets start.</p>
    <a href="https://shop.elenco.com/consumers/snap-circuits-jr-100-experiments.html">Official Product Page →</a>
  </article>
</div>
"""
    page("/kits/", "Kits · STEM Builds", "Which kit you need for which build: SPIKE, Simple Machines, and Snap Circuits.", "kits", main, "/media/moose.png")


def how() -> None:
    main = """
<header class="hero">
  <div class="hero-rule">
    <p class="eyebrow">How It's Made</p>
    <h1>Leveraging AI to Expedite Helping My Son Learn STEM</h1>
  </div>
  <p class="lede">A LEGO® model and an Elenco® Snap Circuits® lesson do not come from the same pipeline. Both get checked before Ian sees them.</p>
</header>
<section class="prose">
  <h2>LEGO® Builds</h2>
  <p>Every LEGO® build starts as a text file. <a href="https://www.ldraw.org/">LDraw</a> is a plain-text format for LEGO® models that the fan community has kept alive since the nineties: one part per line, each with a color and a position. Because it's text, it lives in <a href="https://git-scm.com/">git</a>, a free tool that saves every version of a file and shows what changed. I can see exactly which brick moved between versions, the same way I'd review code at work. <a href="https://www.leocad.org/">LeoCAD</a>, a free and open-source LDraw editor, draws every step picture on this site from those files. The photos at the top of each build are the real thing, on our kitchen table.</p>
  <div class="pair">
    <figure class="photo-inline">
      <img src="/media/seed-drone-drawn.png" alt="The Seed Drone as drawn in LeoCAD.">
      <figcaption>As Drawn, in LeoCAD</figcaption>
    </figure>
    <figure class="photo-inline">
      <img src="/media/seed-drone-iso.jpg" alt="The Seed Drone as built on our kitchen table.">
      <figcaption>As Built, on our kitchen table</figcaption>
    </figure>
  </div>
  <h3>The Part I Didn't Expect to Need</h3>
  <p>LeoCAD will happily let you set a plate down a millimeter above a brick, and the picture looks perfect. I learned that reading the Seed Drone steps back and finding one that told a six-year-old to set down a plate that nothing would hold until two steps later. The picture was right. The build was wrong.</p>
  <p>So I had AI write <a href="https://github.com/ChristopherJCavage/ian-spike-learning/blob/main/tools/ldrcheck.py"><code>ldrcheck</code></a>, a <a href="https://www.python.org/">Python</a> script that reads the model and asks the boring questions. Does this stud actually sit in that tube? Is this axle in a hole that grips it, or one it just passes through? At the end of every step, is every part attached to something? Is every part really in the box, in that color? If it can't prove a part is held, the build doesn't ship.</p>
  <p>It keeps growing, too. Every new build turns up a mistake it didn't catch, and each one becomes a new rule, with a small broken model the rule has to catch, so the next build gets checked for it.</p>
  <p>It can't see everything. It doesn't know whether a color sensor is mounted too high to read a tile, or whether a small hand can hold the thing. Those checks are done by hand, at the table.</p>
  <h3>One More Script</h3>
  <p><code>pages.py</code> keeps the step numbers, the kid-facing words, and the pictures in agreement, then writes the click-through page and the printable PDF from the same source. The programs aren't generated. I build each one by hand in the LEGO® SPIKE™ App on the iPad, and the picture on each build page is a screenshot of it.</p>
  <h2>Elenco® Snap Circuits®</h2>
  <p>These lessons are comics, not brick models. There is no LDraw file and no LeoCAD picture. Each case is one circuit on a real board, told by Sully, Tika, Pip, and Coco. I write the pages. <code>snap.py</code> checks the circuit: the parts are in the boxes we own, the snaps close a loop, and a part made for 3 volts is not powered by the Beginner set's 4.5-volt battery holder. The click-through is the comic. There is no PDF for these yet.</p>
  <h2>About the AI</h2>
  <p>I use <a href="https://cursor.com">Cursor</a> with <a href="https://www.anthropic.com">Anthropic</a>'s Claude models and <a href="https://x.ai/">xAI</a>'s Grok. They write most of the LDraw and most of the Python, and an AI image tool draws the story pictures at the start of some builds. I decide what to build, argue about what a six-year-old can hold, and run the checks. I'd rather say that plainly than have you wonder.</p>
  <h2>Everything Is on GitHub</h2>
  <p>The repo is the source of truth. This site shows the builds we've finished and tested at the table. If you find a mistake, open an issue there or email me at <a href="mailto:cjcavage@gmail.com">cjcavage@gmail.com</a>.</p>
  <p><a class="btn btn-primary" href="https://github.com/ChristopherJCavage/ian-spike-learning">Open the GitHub Repo</a></p>
  <p class="small">Small print: Credits and licenses are on the <a href="/legal/">Legal</a> page. LDraw is a trademark of the Estate of James Jessiman. LeoCAD, Cursor, Anthropic, xAI, and the Python Software Foundation have nothing to do with this site, and neither do the LEGO Group or Elenco.</p>
</section>
"""
    page("/how/", "How It's Made · STEM Builds", "How the models, the checker, and the lessons get made.", "how", main, "/media/seed-drone-iso.jpg")


def about() -> None:
    main = """
<header class="hero">
  <div class="hero-rule">
    <p class="eyebrow">About</p>
    <h1>Chris Cavage</h1>
  </div>
</header>
<section class="prose">
  <p>Ian is six, and most of what we build starts at our kitchen table with the LEGO® SPIKE™ sets we already have. He builds every model before anyone else sees it. If he can't do a step, the step changes.</p>
  <p>Every Saturday morning we take him to the <a href="https://www.ccsarizona.org/">Contemporary Chinese School of Arizona</a> in Phoenix. My wife is originally from China, and Ian is there for Chinese class. After class, the school runs a LEGO® robotics club for kids ages four to eight.</p>
  <p>I got involved the way most parents do: I asked the coach if there was anything I could help with. The SPIKE™ App comes with good lessons, but a semester is long, and a room of six-year-olds needs more variety than that. So I keep in touch with the coach, and when the club needs more builds, we talk about what would make sense.</p>
  <p>By day I'm a Sr. Director of Engineering, leading the global Platform &amp; Firmware division at <a href="https://www.axon.com/">Axon Enterprise, Inc.</a>, at its headquarters in Scottsdale, Arizona. My team supports almost every physical camera and IoT product you can see on Axon's website. Before that I spent a decade at <a href="https://www.digital-control.com/">Digital Control</a> in Kent, Washington, building the locators that steer drills under roads and rivers, and before that I was at <a href="https://www.ensco.com/">ENSCO</a> outside D.C., working in the defense industry. That's over twenty years of software for hardware that has to keep working after it's been dropped, rained on, or buried. Most of my week now is people and budgets. A kitchen table covered in bricks, with a six-year-old asking why, is the part that still feels like engineering.</p>
  <p>Everything on this site is public because that just feels like the right thing to do. A lot of parents need ideas, and I'm generally biased toward a STEM-first education. LEGO® Education stopped selling SPIKE™ in 2026, and plenty of clubs like ours already have the boxes and not much budget for anything new. The details are on <a href="/kits/">Kits</a>. The short version is that these kits were always about teaching a kid that a machine does what you told it, not what you meant, and they're still good at it.</p>
  <p>Everything here is free. If a step is wrong or a part count doesn't match your box, tell me.</p>
  <p><a href="https://www.linkedin.com/in/christopher-cavage-20abb516/">LinkedIn</a> · <a href="https://github.com/ChristopherJCavage/ian-spike-learning">GitHub</a> · <a href="mailto:cjcavage@gmail.com">cjcavage@gmail.com</a></p>
  <p>Galaxy Moose Software is the name I put on side projects, but it will probably someday end up as an LLC when I decide to branch out and start my own product development company. 🙂</p>
</section>
"""
    page("/about/", "About · STEM Builds", "Chris Cavage, Ian, and why these builds are public.", "about", main, "/media/moose.png")


def legal() -> None:
    main = """
<header class="hero">
  <div class="hero-rule">
    <p class="eyebrow">Legal</p>
    <h1>This Site Is Unofficial</h1>
  </div>
</header>
<section class="prose">
  <p>LEGO® is a trademark of the LEGO Group of companies which does not sponsor, authorize or endorse this site. SPIKE™, LEGO® Education, the Minifigure, and Technic® are trademarks of the LEGO Group.</p>
  <p>Elenco® and Snap Circuits® are registered trademarks of Elenco Electronics, LLC, which does not sponsor, authorize or endorse this site.</p>
  <p>I've read the LEGO Group's <a href="https://www.lego.com/en-us/legal/notices-and-policies/fair-play">Fair Play guidelines</a> for fan sites and I'm trying to follow them. In practice that means:</p>
  <ul>
    <li>The LEGO logo does not appear anywhere on this site.</li>
    <li>I use the word LEGO® only as an adjective, in the running text, with the ® mark, and I don't put it in the site's address or make it look like a brand of my own.</li>
    <li>There are no official product photos, box art, or scans of official building instructions here. Every picture is a rendering of my own model made with free software, a photo of that model on our kitchen table, a story drawing made with an AI image tool, or a screenshot of one of my own programs in the SPIKE™ App, cropped to the blocks. The story drawings star our own animal characters, not minifigures. The SPIKE™ App and its blocks are the LEGO Group's copyright.</li>
    <li>Every model on this site is my own design. None of them is one of the official SPIKE™ lesson units, and nothing here is sold. The Snap Circuits® lessons are my own too. Elenco's manuals are linked, not copied.</li>
  </ul>
  <p>If you work for the LEGO Group or Elenco and think I've gotten something wrong, email <a href="mailto:cjcavage@gmail.com">cjcavage@gmail.com</a> and I'll fix it.</p>
  <h2>License for the Builds</h2>
  <p>The building instructions, the step pictures, the photos, the PDFs, the LDraw model files, and the words on this site are licensed under <a href="https://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International (CC BY 4.0)</a>.</p>
  <p>In plain language: you can print them, teach with them, hand them out, translate them, change them, and use them in a paid class or camp, as long as you say where they came from. Credit "Chris Cavage, stem.galaxymoose.com" and note if you changed anything. Full legal text is at the link above.</p>
  <p>What the license covers is my work. It does not cover the bricks, the Snap Circuits® parts, the LEGO®, SPIKE™, Elenco®, and Snap Circuits® trademarks, the SPIKE™ App, or the LDraw parts library, all of which belong to other people and have their own terms.</p>
  <h2>License for the Code</h2>
  <p>The tools that check and publish these builds (<code>ldrcheck.py</code>, <code>pages.py</code>, and the rest of the repo's <code>tools/</code> folder) are released under the <a href="https://github.com/ChristopherJCavage/ian-spike-learning/blob/main/LICENSE">MIT License</a>. Do what you like with them. Keep the copyright line.</p>
  <h2>Credits</h2>
  <p>None of these projects or companies is affiliated with this site.</p>
  <ul>
    <li><a href="https://www.leocad.org/">LeoCAD</a>, the editor and renderer for every step picture here. GNU General Public License, version 2.</li>
    <li>The <a href="https://www.ldraw.org/">LDraw parts library</a>, the part geometry those renders are built from. Creative Commons Attribution 2.0. LDraw.org states that rendered instruction images are not covered by the parts' copyright. LDraw is a trademark of the Estate of James Jessiman.</li>
    <li><a href="https://cursor.com">Cursor</a> and <a href="https://www.anthropic.com">Anthropic</a>'s Claude models, which I use to write the models and the Python. See <a href="/how/">How It's Made</a>.</li>
    <li>Python is a trademark of the Python Software Foundation. Naming the language does not need a symbol on every use.</li>
    <li>Grok is a trademark of xAI. Claude and Anthropic are trademarks of Anthropic, PBC. Anthropic's guidelines say to name Claude in plain text, without a trademark symbol.</li>
    <li>The typeface Poppins, under the <a href="https://openfontlicense.org/">SIL Open Font License</a>.</li>
    <li>Hosted on Cloudflare.</li>
  </ul>
  <h2>Privacy</h2>
  <p>This is a static site. There are no accounts, no comments, no forms, no advertising, and I don't run analytics or set cookies. Cloudflare, which serves the pages, keeps the ordinary server logs any host keeps. If you email me, I have your email. That's all. The photos have their location and camera data stripped before they're published, and nobody's face is in them.</p>
  <h2>Not Affiliated With the School</h2>
  <p>The Contemporary Chinese School of Arizona is mentioned because that's where the Club-Ready builds get used. This is my personal site, and nothing on it is an official statement from the school.</p>
</section>
"""
    page("/legal/", "Legal · STEM Builds", "Trademarks, the CC BY 4.0 license, and what this unofficial site does not claim.", "", main, "/media/moose.png")


def missing() -> None:
    page(
        "/404.html",
        "Page not found · STEM Builds",
        "That page is not on this site.",
        "",
        """
<header class="hero">
  <div class="hero-rule"><h1>That page isn't here</h1></div>
  <p class="lede">The link may be old. The builds that are published are on <a href="/projects/">Projects</a>.</p>
</header>
""",
        "/media/moose.png",
    )
    # Workers looks for /404.html at the asset root, not /404.html/index.html.
    src = DIST / "404.html" / "index.html"
    if src.exists():
        text = src.read_text(encoding="utf-8")
        shutil.rmtree(DIST / "404.html")
        (DIST / "404.html").write_text(text, encoding="utf-8")


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(WEB, DIST)
    copy_media()
    home()
    projects()
    mission()
    builds()
    kits()
    how()
    about()
    legal()
    missing()
    copy_lessons()
    (DIST / "_redirects").write_text("/sets /kits/ 301\n/sets/ /kits/ 301\n", encoding="utf-8")
    (DIST / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
    print(f"wrote {DIST}")


if __name__ == "__main__":
    main()
