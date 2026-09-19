# How the SPIKE kits mix

Three kits, one App, one big bin of parts. This doc is the "why" and "how"
behind combining SPIKE Essential (45345), SPIKE Prime (45678), and the
Prime Expansion (45681) for Ian's builds, separate from the flat parts
inventories in this folder.

## The setup

- **SPIKE Essential 45345** -- Ian's set for his Saturday ASU class.
  He's 6. 449 pieces on the box (473 in the detailed teardown). Smaller,
  simpler hub; built for K-5.
- **SPIKE Prime 45678** -- the "grow into it" set. 528 pieces on the box
  (557 in the detailed teardown). Bigger hub, more motors and sensors,
  built for upper-elementary/middle school.
- **SPIKE Prime Expansion 45681** -- an add-on, not a standalone kit.
  604 pieces on the box (606 in the detailed teardown). **No hub, no
  battery, no USB cable.** It brings one more medium motor, one more
  colour sensor, and otherwise gears, turntables, big wheels, and beams.

Both run the **same SPIKE App** (iOS/Android/Chromebook/desktop). The app
detects whichever hub connects over Bluetooth or USB and shows the right
block palette automatically -- there's no separate install, no separate
account, no separate project format to worry about.

## What actually mixes

- **Motors and sensors are fully interchangeable.** A Prime distance
  sensor works on the Essential hub. An Essential small motor works on
  the Prime hub. Same 6-wire connector, same protocol, both directions.
  See `combined-electronics.txt` for the full inventory.
- **Studs and Technic pins are the same LEGO System/Technic standard**
  across all three sets, so beams, connectors, bricks, and plates from any
  box combine freely. There's no "Essential-only" stud pattern.
- **The Expansion is pure parts.** Everything in it plugs into what we
  already own. Its one motor and one colour sensor are duplicates of
  parts from the base kits, so they work on either hub like any other.
- **Batteries and hubs do NOT mix.** The Essential hub takes its own
  battery pack; the Prime hub takes a different one. Don't assume you
  can swap power packs between hubs -- check the connector shape first.
- **Only one hub per build.** You pick either the Essential hub or the
  Prime hub as the "brain" for a given creation, then plug in whatever
  mix of motors/sensors from either box you want into that hub's ports
  (2 ports on Essential, 6 on Prime).

## What the Expansion actually unlocks

Worth knowing before designing, because these are things the two base
kits genuinely could not do (full detail at the bottom of
`45681-expansion/parts.txt`):

- **Turntables** -- Z28 and Z60, top and bottom halves. The first real
  rotating platform we own: crane cabs, turrets, radar.
- **Big wheels** -- 4x 88mm with an integral tyre and a cross-axle hub,
  much larger than Prime's 56mm.
- **A proper gear train** -- bevel gears, conical wheels Z12/Z20/Z36,
  angled gear wheels, a 7M rack, and a curved quarter-circle rack.
- **Long axles** -- 32M and 12M, longer than anything in the base kits.
- **Pins in bulk** -- 80 black friction pegs and 36 blue 3M pegs. In
  practice this is now where the pins come from.

## What we're deliberately ignoring

- **Prime's official middle-school lesson plans.** We're not running the
  LEGO Education Prime curriculum -- it assumes an older kid and a
  classroom pace. We're using the *hardware* freely and building our own
  projects/lessons around Ian's age and interests.
- **Any further add-on.** Nothing in these files assumes we own anything
  beyond the three kits inventoried here. A new set gets its own
  `kits/<number>-<name>/parts.txt` before any build may reference it.

## Practical mixing guidance

- **For Ian's Saturday class:** default to the Essential hub. It's the
  hub his class actually uses, so muscle memory transfers. Borrow a
  Prime motor or sensor only when a specific build needs one Essential
  doesn't have (e.g., the distance sensor, force sensor, or a large
  motor for more torque).
- **For at-home free-build time:** either hub is fair game. If a build
  wants more ports or more torque, start with the Prime hub instead of
  daisy-chaining or forcing it onto the smaller one.
- **Storage:** merge Prime and Expansion into one part-type-sorted pool;
  keep Essential physically separate so the class kit stays Essential-only
  and portable. Full plan, with tray counts computed from these
  inventories, in [`storage.md`](storage.md). The parts lists work either
  way, since every line already says which kit it came from.
- **Piece IDs matter more than kit boundaries.** If Ian loses a part,
  grep all three `parts.txt` files by name (e.g. `grep -i "connector peg"
  kits/*/parts.txt`) -- LEGO's Pick-a-Brick / Customer Service replacement
  parts lookup uses the element IDs listed here, not "which box it came
  from." Part names are spelled identically across the three files when
  the design ID matches, so one grep really does span all three.

## Not a parts database

These files are intentionally simple flat text, not a relational
database or spreadsheet. The goal is "can I `grep` for a part fast,"
not "can I query joins across sets." If this ever needs to become more
structured (e.g. a real sqlite/CSV inventory with build tracking), that's
a deliberate future decision, not something to back into by accident.
