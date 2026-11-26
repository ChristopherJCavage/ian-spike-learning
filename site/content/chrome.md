# Shared chrome

## Header

Wordmark: **Galaxy Moose Software** (moose mark) with the small label
**STEM Builds**. No LEGO® word in the header.

Nav (in order): Projects · Kits · How It's Made · About

Each nav item is an accent-colored underline, the same treatment as a
text link, so it reads as a URL rather than a label.

"Projects" goes to `/projects`, the index of everything we've built, grouped
by kit family. "Kits" goes to `/kits`. `/sets` redirects there once the
static site exists. "How It's Made" goes to `/how`. Legal lives in the
footer only.

## Footer (every page)

Line 1: Galaxy Moose Software · Everything on this site is free ·
[CC BY 4.0](/legal) · [Legal](/legal) · [GitHub](https://github.com/ChristopherJCavage/ian-spike-learning)

Line 2 (verbatim, do not edit):

> LEGO® is a trademark of the LEGO Group of companies which does not
> sponsor, authorize or endorse this site. SPIKE™, LEGO® Education, the
> Minifigure, and Technic® are trademarks of the LEGO Group. This site is
> unofficial.

Line 3 (ours, same size and color as line 2):

> Elenco® and Snap Circuits® are registered trademarks of Elenco
> Electronics, LLC, which does not sponsor, authorize or endorse this site.

## Projects and Builds

A **project** is one idea. A **build** is one model with its own steps,
PDF, and program. Some projects are a single build. Some are two builds
that work together. Every published build belongs to exactly one project,
set by `project:` and `role:` in its README.

- Project of one (Chameleon, Hot Press, The Night Skate Cases): the card
  and the page are just the build. Half-pipe Swing is written the same
  way and stays off Home and Projects until it has been play-tested.
- Project of several (Rainforest Seed Mission): a project page, and each
  build page gets a Goes With chip.

The index is `/projects` (`site/content/projects.md`). Cards are grouped
under one section per kit family, in the same order as the Kits page. A
family gets a section when its first build is published. Every project page
and build page starts with a breadcrumb back to that index: `Projects >`,
then the project name when the build belongs to a project of several.
A project of one is `Projects > {Build}` and has no Goes With chip.

**Club-Ready** means `venue: class` and only kits the club owns: about one
session, written so a room of six-year-olds can finish it. Today that list
is just set 45345, one Essential box. **Home Build** means `venue: home`:
more than one box, or a kit the club doesn't have, and a grown-up does the
hard part of the frame. Both come from the README header block.

## Project Card

Four layouts. The first three have a photo (Photo frame / Card), the kit
badge on the photo, a Club-Ready or Home Build tag, the name, and one or
two sentences. Compact is the short one, for the home page strip.

- **Single:** links are Print the PDF · Click Through the Steps. Used for
  a project of one.
- **Pair:** a "2 builds" tag next to the name, then one row per build (name
  and role) and an Open the Project button. The kit badge is the union of
  the builds. A build that mixes kit families shows one badge per family.
- **Wide:** the pair, laid out with the photo on the left and the rows on
  the right, so it can sit full width above the single cards.
- **Compact:** photo, kit badge, tag, name, and one line. No link row. The
  whole card links to the build, or to the project page when the project
  has more than one build. Used in the Latest Projects strip on Home. The
  order of that strip is set by hand in `home.md`.

## Kit Badge

The emblem on every card and build hero. Each kit family has its own fixed
segments, in a fixed order, so a reader learns one shape per family. A
one-box kit is a single segment. A build that mixes families shows one
badge per family.

SPIKE™, always in this order:

```
[ Essential | Prime | Expansion ]
```

A needed segment is filled lime with dark text. An unneeded segment is an
outline with dim text. Words, not color alone, and no logo. The set numbers
do not appear on the badge. They stay in the full checklist under What You
Need.

Values come from the `kits:` tag. Each id maps to a family and a segment in
`the-kits.md`. A segment is Needed when its id is listed.

- Seed Mission, Chameleon, and Hot Press: Essential.
- A build that needs all three boxes lights Essential, Prime, and
  Expansion. Half-pipe Swing is that shape. It is not on the site yet.
- The Night Skate Cases (Snap Circuits®): Beginner and Jr. Every block is
  from the Beginner box, but Case 4 needs a fifth blue wire, and only the
  Jr. box has one.

## Kit Indicator

The full checklist. It stays under What You Need on build pages and project
pages. It does not sit on cards or heroes anymore; the kit badge does that
job. It lists the rows for the build's family, not always the three SPIKE™
rows. Filled lime check with the word "Needed"; muted dash with the word
"Not needed". Never color alone.

SPIKE™, always all three rows, plus a hub line. The hub line shows only for
SPIKE™ builds:

```
Essential 45345   [check]  Needed
Prime 45678       [dash]   Not needed
Expansion 45681   [dash]   Not needed
Hub: Small Hub (Essential)
```

A one-box kit is one row, for example Simple Machines 9689 once a build
uses it. Values come from the `kits:` and `hub:` tags in
`builds/<slug>/README.md`. `hub: none` prints "Hub: none (no electronics)"
on a SPIKE™ build, and prints nothing on a kit that has no hub.

## Photo Frame

Four treatments so a kitchen-table photo sits on the dark page. Specs and
CSS are in `photos.md`.

- **Hero:** no border; the edges fade into the page background.
- **Card:** the bottom fades into the card surface; the title sits on it.
- **Inline:** rounded corners and a 1px border, for pictures inside an
  article.
- **Screenshot:** Inline without the dim, for the SPIKE™ App program
  screenshots, which have to stay unaltered.

## Print Notes (under every PDF link)

Format: `{pages} pages · US Letter · print in color · {size} MB`

The step highlights and the kit badge depend on color. Never say the
PDF is grayscale-friendly.

## Shared Small Strings

- "Print the PDF"
- "Click Through the Steps"
- "Open the Project"
- "Small print: Original model, not one of the official {family} lessons."
  `{family}` is the kit's name, so a SPIKE™ build still reads "official
  SPIKE™ lessons."
