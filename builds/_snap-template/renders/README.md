Two kinds of file live here.

- Drawn by `python3 tools/snap.py render builds/<slug>` (do not edit; `check`
  fails stale ones and `render` clears ones it no longer draws):
  `step-NNN.svg`, `change-<name>.svg`, `scene-<name>.svg`,
  `puzzle-<name>[-key].svg`, `mission-<name>[-key].svg`, `part-<KEY>.svg`,
  and `slide-NNN-*.svg` for guess, Number Lab and WHY? pages.
- Comic panels, `comic-*.jpg`: generated pictures (16:9, no words in them)
  drawn from `context/story-cast-comic.png`. `check` fails one that no slide
  uses.
