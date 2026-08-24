# How the SPIKE Essential and SPIKE Prime kits mix

Two kits, one App, one big bin of parts. This doc is the "why" and "how"
behind combining SPIKE Essential (45345) and SPIKE Prime (45678) for
Ian's builds, separate from the flat parts inventories in this folder.

## The setup

- **SPIKE Essential 45345** -- Ian's set for his Saturday ASU class.
  He's 6. 449 pieces on the box (473 in the detailed teardown). Smaller,
  simpler hub; built for K-5.
- **SPIKE Prime 45678** -- the "grow into it" set. 528 pieces on the box
  (557 in the detailed teardown). Bigger hub, more motors and sensors,
  built for upper-elementary/middle school.

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
  across both sets, so beams, connectors, bricks, and plates from either
  box combine freely. There's no "Essential-only" stud pattern.
- **Batteries and hubs do NOT mix.** The Essential hub takes its own
  battery pack; the Prime hub takes a different one. Don't assume you
  can swap power packs between hubs -- check the connector shape first.
- **Only one hub per build.** You pick either the Essential hub or the
  Prime hub as the "brain" for a given creation, then plug in whatever
  mix of motors/sensors from either box you want into that hub's ports
  (4 ports on Essential, 6 on Prime).

## What we're deliberately ignoring

- **Prime's official middle-school lesson plans.** We're not running the
  LEGO Education Prime curriculum -- it assumes an older kid and a
  classroom pace. We're using the *hardware* freely and building our own
  projects/lessons around Ian's age and interests.
- **Expansion Set 45681 (or any other add-on).** Nothing in these files
  assumes we own it. If we ever pick one up, it gets its own
  `kits/45681-expansion/parts.txt` file -- don't assume extra XL motors,
  bigger wheels, etc. are on hand until that file exists.

## Practical mixing guidance

- **For Ian's Saturday class:** default to the Essential hub. It's the
  hub his class actually uses, so muscle memory transfers. Borrow a
  Prime motor or sensor only when a specific build needs one Essential
  doesn't have (e.g., the distance sensor, force sensor, or a large
  motor for more torque).
- **For at-home free-build time:** either hub is fair game. If a build
  wants more ports or more torque, start with the Prime hub instead of
  daisy-chaining or forcing it onto the smaller one.
- **Storage:** it's fine to keep the two boxes' bins physically separate
  (each kit ships its own sorting tray) or to combine them into one big
  bin organized by part type -- this repo's parts lists work either way,
  since every line item already says which kit it came from.
- **Piece IDs matter more than kit boundaries.** If Ian loses a part,
  grep both `parts.txt` files by name (e.g. `grep -i "connector peg"
  kits/*/parts.txt`) -- LEGO's Pick-a-Brick / Customer Service replacement
  parts lookup uses the element IDs listed here, not "which box it came
  from."

## Not a parts database

These files are intentionally simple flat text, not a relational
database or spreadsheet. The goal is "can I `grep` for a part fast,"
not "can I query joins across sets." If this ever needs to become more
structured (e.g. a real sqlite/CSV inventory with build tracking), that's
a deliberate future decision, not something to back into by accident.
