# (Module title)

The Spark Detectives, Module N. The comic: `python3 tools/snap.py preview`
turns this file into `preview.html`. Rules for the comic (cast, world, art,
Number Lab): `context/snap-circuits.md`. A worked example of every slide kind:
`builds/snap-01-the-loop/deck.md`.

How this file works:

- `## Chapter N -- Title` starts a chapter (one sitting). Its first line is
  `badge: <what Ian becomes>` for the CASE CLOSED page.
- `=== <kind> [arg]` starts a slide. Kinds: splash, comic, talk, meet KEY,
  step N, change NAME, scene NAME, predict, why, puzzle, mission NAME,
  numberlab, rule, badge.
- A `talk` page is where the crew argues an idea out loud. Give it a
  `layout:` so the pages don't all look the same: `splash` (one picture,
  bubbles in the corners), `spread` (two wide pictures), `cinema` (a banner
  over three boxes), `hero`, `zigzag`, `stack`, `strip`, `wide`, `quad`.
  `quad` is the 2x2. Use it once in a while, not for every page. Each
  `box:` is a pose from `context/comic/` (no .jpg) or a picture path, then
  that character's `bubble:`. One new piece of the idea per box. Keep each
  bubble under about 15 words. A splash is one box with up to four bubbles.
  A spread is two boxes.
- `field: value` lines fill it. A line starting with spaces continues the
  field above. Lines starting with `>` are notes to yourself.
- Every slide needs `dad:` (what the grown-up does); step and scene slides
  can use steps.md's `Do:` instead. Optional: `watch:` (signs Ian is lost),
  `reason:` (one adult sentence of the real science), `say:` (the big
  read-aloud line), `pose:` (a file in context/comic/, without .jpg).
- `bubble: Who: words` (Who is Coco, Pip, Tika or Sully). On comic panels add
  a spot: `bubble: Pip @tr: words` (tl tc tr bl bc br). `reveal: Who: words`
  pops in after a question's answer is shown.
- Questions are answered by the checker, and `answer:` must agree:
  - `predict`: `test:` a board state, `look:` the block, `choices:
    Light=on | Dark=off`, `answer: Dark`. Or `fact:` instead of test/look/choices.
  - `puzzle`: `boards:` puzzle names from circuit.snap, `look:`, `choices:`,
    `answer: a=Light, b=Dark`, `stars:`.
  - `numberlab`: `fact:` (loop-posts, post-of N, grid-posts, volts, calc ...,
    flip-colour K of N, settings ..., shows ..., keeps-on KEY, blades K, each
    with `@ <assignments>` where it needs a board), `answer:`, `stars:`. With
    no `fact:`, the answer is written out and nobody checks it.
  - `mission NAME`: `card:` and `stars:`; circuit.snap proves the answer board.

series: The Spark Detectives
module: (Module title)

## Chapter 1 -- (Case title)
badge: (Badge name)

=== splash
art: renders/comic-c1-splash.jpg
say: The Spark Detectives. Case 1.
dad: Sit side by side. Click for the next bubble. G hides these notes.
reason: (The one idea of this case.)

=== step 1
pose: sully-notice
bubble: Sully: Numbers across, letters down. 1A is the corner.

=== rule
rule: (The rule, in Ian's words.)
pose: tika-write
bubble: Tika: Rule 1 goes in my case notes.
dad: Ian says the rule back in his own words.

=== badge
bubble: Coco: Case 1 closed!
dad: Print the badge if he wants it.
