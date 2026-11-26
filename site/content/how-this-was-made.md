# How It's Made

Layout: single column article, about 680px wide. One inline "As Drawn / As
Built" pair after the first section.

## Leveraging AI to Expedite Helping My Son Learn STEM

A LEGO® model and an Elenco® Snap Circuits® lesson do not come from the
same pipeline. Both get checked before Ian sees them.

### LEGO® Builds

Every LEGO® build starts as a text file. [LDraw](https://www.ldraw.org/) is a plain-text format for LEGO®
models that the fan community has kept alive since the nineties: one part
per line, each with a color and a position. Because it's text, it lives in
[git](https://git-scm.com/), a free tool that saves every version of a file
and shows what changed. I can see exactly which brick moved between versions, the same
way I'd review code at work. [LeoCAD](https://www.leocad.org/), a free and open-source LDraw editor,
draws every step picture on this site from those files. The photos at the
top of each build are the real thing, on our kitchen table.

Inline pair: `renders/check-iso.png` (As Drawn) beside
`photos/seed-drone/iso` (As Built), Photo frame / Inline, same angle.
Captions: "As Drawn, in LeoCAD" and "As Built, on our kitchen table".

#### The Part I Didn't Expect to Need

LeoCAD will happily let you set a plate down a millimeter above a brick,
and the picture looks perfect. I learned that reading the Seed Drone steps
back and finding one that told a six-year-old to set down a plate that
nothing would hold until two steps later. The picture was right. The build
was wrong.

So I had AI write [`ldrcheck`](https://github.com/ChristopherJCavage/ian-spike-learning/blob/main/tools/ldrcheck.py), a [Python](https://www.python.org/) script that reads the model and
asks the boring questions. Does this stud actually sit in that tube? Is
this axle in a hole that grips it, or one it just passes through? At the
end of every step, is every part attached to something? Is every part
really in the box, in that color? If it can't prove a part is held, the
build doesn't ship.

It keeps growing, too. Every new build turns up a mistake it didn't catch,
and each one becomes a new rule, with a small broken model the rule has to
catch, so the next build gets checked for it.

It can't see everything. It doesn't know whether a color sensor is mounted
too high to read a tile, or whether a small hand can hold the thing. Those
checks are done by hand, at the table.

#### One More Script

`pages.py` keeps the step numbers, the kid-facing words, and the pictures
in agreement, then writes the click-through page and the printable PDF
from the same source. The programs aren't generated. I build each one by
hand in the LEGO® SPIKE™ App on the iPad, and the picture on each build page is
a screenshot of it.

### Elenco® Snap Circuits®

These lessons are comics, not brick models. There is no LDraw file and no
LeoCAD picture. Each case is one circuit on a real board, told by Sully,
Tika, Pip, and Coco. I write the pages. `snap.py` checks the circuit: the
parts are in the boxes we own, the snaps close a loop, and a part made for
3 volts is not powered by the Beginner set's 4.5-volt battery holder. The
click-through is the comic. There is no PDF for these yet.

### About the AI

I use [Cursor](https://cursor.com) with [Anthropic](https://www.anthropic.com)'s Claude models and [xAI](https://x.ai/)'s Grok. They write most of the LDraw
and most of the Python, and an AI image tool draws the story pictures at
the start of some builds. I decide what to build, argue about what a
six-year-old can hold, and run the checks. I'd rather say that plainly
than have you wonder.

### Everything Is on GitHub

The repo is the source of truth. This site shows the builds we've finished
and tested at the table. If you find a mistake, open an issue there or
email me at [cjcavage@gmail.com](mailto:cjcavage@gmail.com).

[Open the GitHub Repo](https://github.com/ChristopherJCavage/ian-spike-learning)

Small print: Credits and licenses are on the [Legal](/legal) page. LDraw is
a trademark of the Estate of James Jessiman. LeoCAD, Cursor, and Anthropic
have nothing to do with this site, and neither do the LEGO Group or
Elenco.
