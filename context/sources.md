# Sources

Curated links. Use for ideas and part IDs. **Do not paste official Building
Instruction art or lesson PDFs into this repo.**

## Official LEGO Education

- Lessons library: <https://education.lego.com/en-us/lessons/>
  Filter SPIKE Essential or SPIKE Prime. Teacher pages, 5E, standards.
- SPIKE App (web): <https://spike.legoeducation.com/>
  Icon / Word / Python. Same app for both kits. This repo extracts the
  Word Block catalogue from its JS bundle into `tools/spike/blocks.json`.
- SPIKE App (iOS/Android/Chromebook/desktop): Getting Started, in-app BIs,
  Icon / Word / Python.
- Essential Small Hub `45609` tech sheet (2 ports A–B, no on-hub matrix):
  <https://assets.education.lego.com/v3/assets/blt293eea581807678a/blt8a69ecd244fee569/60fe864661f38746a5778f86/LE_SPIKE_Essential_Tech_fact_sheet_Small_Hub_45609_2HY21_Digital.pdf?locale=en-us>
- Prime Large Hub tech spec (6 ports, 5x5 matrix, speaker):
  <https://le-www-live-s.legocdn.com/sc/media/files/support/spike-prime/techspecs_techniclargehub-fba3b469ecb9eaafbde5f24d34ba090e.pdf>
- Essential product: <https://education.lego.com/en-us/products/lego-education-spike-essential-set/45345/>
- Prime product + BI index:
  <https://education.lego.com/en-us/product-resources/spike-prime/downloads/building-instructions/>

## Snap Circuits (Elenco) -- links only

Parts lists and numbers came from these. Do not paste their pages here.

- Beginner SCB-20 product page: <https://shop.elenco.com/consumers/snap-circuits-beginner.html>
- SCB-20 manual (parts list, 21 projects, short-circuit warning):
  <https://www.elenco.com/wp-content/uploads/2017/10/753097-2.pdf>
- Jr SC-100 product page: <https://shop.elenco.com/consumers/snap-circuits-jr-100-experiments.html>
- SC-100 manual, 2021 printing (parts list on page 2, base grid A-G x 1-10):
  <https://elenco.com/wp-content/uploads/2021/11/SC-100_Manual.pdf>
- SC-100 manual, older REV-H printing (red LED, 100 ohm resistor, 6-snap wire):
  <https://www.elenco.com/wp-content/uploads/2011/03/SC-100_REV-H_071712.pdf>
- Elenco product summary (SCB-20 "Upgradable? No"; SC-100 up to SC-750 and the
  UC-30/40/60 upgrade kits):
  <https://www.elenco.com/wp-content/uploads/2021/05/Snap-Circuits-Product-Summary_2020.pdf>

## Storage and sorting (see `kits/storage.md`)

- University of Idaho Extension, *Organizing the LEGO SPIKE Prime Robotics
  Kit*, BUL 1129 (Feb 2026). Tray systems for Prime alone and for Prime +
  Expansion, with parts cards:
  <https://verso.uidaho.edu/esploro/outputs/report/Organizing-the-LEGO-SPIKE-Prime-Robotics/996924745401851>
- Engineering With Bricks summary of the same bulletin:
  <https://engineeringwithbricks.com/posts/organizing-the-lego-spike-prime-kit>
- FLL Team 24277's storage plan (bin-per-part-feature scheme):
  <https://github.com/FLL-Team-24277/FLL-Lego-Storage>
- Brick Architect, storage for large collections (drawer cabinets vs trays):
  <https://brickarchitect.com/guide/bricks/large/>
- BrickNerd, opinionated guide to storage containers and cost:
  <https://bricknerd.com/home/an-opinionated-guide-to-lego-storage-containers-and-cost-5-25-23>
- LEGO Education Small Sorting Top Trays `45495` (the in-ecosystem fix):
  <https://education.lego.com/en-us/products/small-sorting-top-trays-by-lego-education/45495/>

Buy links, checked Sep 2026. Prices move; the model numbers do not.

- Plano StowAway 3700, 4-pack, single latch, $23.99 Amazon:
  <https://www.amazon.com/dp/B0FH7DNNX2>
- Plano 3700 **ProLatch** 4-pack, $34.99 Tackle Warehouse (better latch):
  <https://www.tacklewarehouse.com/Plano_3700_Stowaway_4-Pack/descpage-PSFP.html>
- Plano 3750 ProLatch single, $9.99 Tackle Warehouse:
  <https://www.tacklewarehouse.com/Plano_Pro_Latch_Utility_Box_3750_/descpage-PPLUB37502.html>
- Plano 3750 single on Amazon: <https://www.amazon.com/dp/B012NW3RKW>
- Plano 3701 shallow single, $12.99-17.17 Amazon (only if a tray needs 30+
  compartments): <https://www.amazon.com/dp/B00YH9J87G>
- Plano Guide Series 4-By Rack System, four boxes included, $55.99 direct /
  ~$48 elsewhere: <https://www.planooutdoors.com/products/guide-series-stowaway-rack-system-1598471>
  and <https://www.amazon.com/dp/B000E3FKTO>
- Milwaukee Packout Compact Organizer `48-22-8435`, $34.97 Home Depot. Amazon
  third-party sellers want $88 for the same box:
  <https://www.homedepot.com/p/Milwaukee-PACKOUT-5-Compartments-Small-Parts-Organizer-48-22-8435/303005752>

## FOSS 3D (this repo's pretty-page path)

- LDraw.org -- format + parts library: <https://www.ldraw.org/>
- LeoCAD (GPLv2, Mac): <https://www.leocad.org/>
  Source: <https://github.com/leozide/leocad>
  CLI: <https://www.leocad.org/docs/cli.html>
- LPub3D (open-source instruction booklets):
  <https://trevorsandy.github.io/lpub3d/>

**Not used:** BrickLink Studio (proprietary). LDCad (freeware, not FOSS).

## Community teaching (check BOM against our kits)

- Prime Lessons (Word Blocks + Python skill sequence; many robots are
  **45678-only**, no expansion): <https://primelessons.org/en/index.html>
  License: CC-BY-NC-SA. Still grep `kits/*/parts.txt` before copying a design.
- FIRST LEGO League / similar -- steal *mechanisms* (gears, pulleys, lifts),
  not competition robots aimed at older kids.
- Rebrickable SPIKE MOCs -- many assume Expansion `45681`, which we now
  own. Still grep `kits/*/parts.txt` first for quantities and colours.

## Catalog (IDs we already store)

- Brickset inventories were the source for `kits/*/parts.txt` (LEGO CS
  replacement-parts registry). Prefer our files over re-scraping.
  Inventory pages: <https://brickset.com/inventories/45345-1> and the
  same URL shape for `45678-1` and `45681-1`.
- **Design ID -> LDraw part number.** LEGO renumbers moulds; LDraw keeps
  the original number, and the LDraw library does not record LEGO design
  IDs at all. Two sources cross-reference them, and `tools/ldraw_aliases.json`
  was built from both:
  - BrickLink item pages show "Alternate Item No" --
    <https://www.bricklink.com/v2/catalog/catalogitem.page?P=6536>
  - Brickset design pages sometimes show "Designs with the same name" --
    <https://brickset.com/parts/design-40146>
  Rebrickable sits behind a bot check and is not fetchable from here.
  Run `python3 tools/ldrcheck.py kits` to see what is still unresolved.

## Deliberately out of scope

- **Pybricks** and other firmware-replacing Python stacks. They would
  break the SPIKE App workflow Ian's Saturday class depends on. Prime
  Python in this repo means the app's own SPIKE 3 API, documented in
  [`spike-blocks.md`](spike-blocks.md).

