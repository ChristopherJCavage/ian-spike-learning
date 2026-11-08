# Photos

Real photos of our own models, taken on our kitchen table. They're our
copyright, so the LEGO Group's Fair Play guidelines allow them, as long as
no LEGO box, official instruction booklet, or SPIKE™ App logo is in the
frame.

## Where They Go

| Slot | Photo | Treatment |
|---|---|---|
| Home hero | line art, not a photo (`site/assets/home/hero-line-art.svg`) | none |
| Project card, Seed Mission | `rainforest-seed-mission/hero` | Card |
| Project card, Chameleon | `rainforest-chameleon/hero` | Card |
| Project page hero | `rainforest-seed-mission/hero` | Hero |
| Build page heroes | `<build>/hero` | Hero, with the LeoCAD render as an "As Drawn" thumbnail |
| How It's Made | `seed-drone/iso` beside `renders/check-iso.png` | Inline pair |
| Project card, Half-pipe Swing | `halfpipe-swing/hero` | Card |
| Build pages, How It Works | `<build>/program` (SPIKE™ App screenshot) | Screenshot |
| About (optional) | `about/table` | Inline |

Step pictures in the PDFs and click-throughs stay LeoCAD renders. Photos
are for the top of the page, where someone decides whether to try it.

## The Fade Treatment

A kitchen table is bright and busy, and the site is near-black. Each
treatment makes the edges of the photo disappear into the page instead of
sitting in a hard box.

**Hero.** No border. The edges fade into the page background.

```css
.photo-hero img {
  mask-image: radial-gradient(ellipse 70% 65% at 50% 50%, #000 55%, transparent 100%);
  filter: brightness(.92) saturate(.92);
}
```

**Card.** The bottom of the photo fades into the card surface, and the
build name sits on the fade.

```css
.photo-card { position: relative; }
.photo-card::after {
  content: ""; position: absolute; inset: 60% 0 0 0;
  background: linear-gradient(to bottom, transparent, var(--color-surface));
}
.photo-card img { filter: brightness(.92) saturate(.92); }
```

**Inline.** Rounded corners, a 1px border, and the same slight dim.

```css
.photo-inline img {
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  filter: brightness(.92) saturate(.92);
}
```

**Screenshot.** The Inline frame with no filter, because the LEGO Group's
Fair Play terms ask for the app's pictures in unaltered form.

```css
.photo-screenshot img {
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
}
```

No other color grading. The bricks should look like bricks.

## Shot List

Rainforest Seed Mission

1. **The pair.** Ian's hands holding the Seed Drone low over the Drop Zone,
   seed loaded, ideally mid-drop. This is the project card and the project
   page hero. Take a burst. Saved as `rainforest-seed-mission/hero`.
2. **The drone alone**, at the same three-quarter angle as
   `builds/seed-drone/renders/check-iso.png`. This is both its build hero
   and the "As Built" half of the How It's Made pair. Take it once from
   slightly further back as `seed-drone/iso` if the hero is cropped tight.
3. **The Drop Zone alone**, from a little above, with the red band across
   the middle. Saved as `rainforest-drop-zone/hero`.

Chameleon Color-Match

4. **Three-quarter angle**, back lit up over a pad, matching its iso
   render. Saved as `rainforest-chameleon/hero`.
5. **The warning shot**: the back lit red over the red pad. A spare; it may
   go in How It Works.

Half-pipe Swing

6. **The button.** Ian's hands pressing the force sensor, reaching over
   the left lip, Leo on the board. Saved as `halfpipe-swing/hero`.

Program Screenshots

7. **One per build that has a program.** Open it in the SPIKE™ App on the
   iPad and take a screenshot. Crop it to just the blocks: no app logo,
   menus, or other screens, and no edits beyond the crop. Saved as
   `photos-inbox/<build>/program.png`. It goes under How It Works.

About (optional)

8. **Overhead of the table mid-build**, parts sorted, hands only. Saved as
   `about/table`.

## How to Shoot

- Landscape, at least 2400 pixels wide. The phone's normal camera is fine.
- Keep the model in the middle 60% of the frame. The fade eats the edges,
  so anything near the border disappears.
- Clear the table to a plain surface. Move the cereal.
- Window daylight, no flash. Flash makes the bricks shiny and flat.
- Shoot from about 30 degrees above the table, roughly where the renders
  look from.
- Hands only. No faces, no reflections of faces in the hub.
- No LEGO box, booklet, or App logo anywhere in the frame.

## Export

Drop the originals (HEIC or JPEG, or PNG for a screenshot) into
`photos-inbox/<slot>/<name>`, for example `photos-inbox/seed-drone/hero.heic`,
then run:

```
python3 tools/photos.py export photos-inbox
```

For each photo it fixes the rotation, strips every bit of EXIF (including
the GPS location of the house), and writes four files next to the build:

```
builds/<slug>/photos/<name>-1600.webp
builds/<slug>/photos/<name>-1600.jpg
builds/<slug>/photos/<name>-800.webp
builds/<slug>/photos/<name>-800.jpg
```

Project and about photos go to `site/photos/<slot>/`. `photos-inbox/` is
git-ignored so originals with location data never get committed.
`python3 tools/photos.py check` fails if any published photo still has
EXIF.
