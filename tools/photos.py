"""Kitchen-table photos for the site: export and check.

    python3 tools/photos.py export photos-inbox
    python3 tools/photos.py check

`export` reads `<inbox>/<slot>/<name>.<ext>` (HEIC, JPEG, or PNG), fixes the
rotation, drops all metadata, and writes 1600- and 800-pixel-wide WebP and
JPEG copies. A slot that names a build (`seed-drone`) writes to
`builds/<slot>/photos/`; any other slot (`rainforest-seed-mission`, `about`)
writes to `site/photos/<slot>/`.

`check` fails if any published photo carries EXIF, because phone photos
carry the GPS position of the house.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
WIDTHS = (1600, 800)
SOURCE_EXTS = {".heic", ".heif", ".jpg", ".jpeg", ".png"}
PUBLISHED_EXTS = {".jpg", ".jpeg", ".webp", ".png"}


def out_dir(slot: str) -> Path:
    if (ROOT / "builds" / slot / "README.md").exists():
        return ROOT / "builds" / slot / "photos"
    return ROOT / "site" / "photos" / slot


def open_source(path: Path, tmp: Path) -> Image.Image:
    if path.suffix.lower() in {".heic", ".heif"}:
        # Pillow cannot read HEIC; macOS sips can, and keeps the orientation tag.
        jpg = tmp / (path.stem + ".jpg")
        subprocess.run(
            ["sips", "-s", "format", "jpeg", str(path), "--out", str(jpg)],
            check=True, capture_output=True,
        )
        path = jpg
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    return img.convert("RGB")


def export(inbox: Path) -> int:
    sources = sorted(p for p in inbox.rglob("*") if p.suffix.lower() in SOURCE_EXTS)
    if not sources:
        print(f"no photos under {inbox}")
        return 1
    problems = 0
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        for src in sources:
            rel = src.relative_to(inbox)
            if len(rel.parts) != 2:
                print(f"skip {rel}: expected <slot>/<name>.<ext>")
                problems += 1
                continue
            slot, name = rel.parts[0], src.stem
            img = open_source(src, tmp)
            if img.width < max(WIDTHS):
                print(f"warn {rel}: only {img.width}px wide; want at least {max(WIDTHS)}")
            dest = out_dir(slot)
            dest.mkdir(parents=True, exist_ok=True)
            for w in WIDTHS:
                h = round(img.height * w / img.width)
                sized = img.resize((w, h), Image.LANCZOS) if img.width > w else img
                # A fresh image carries no info dict, so nothing from the
                # original (EXIF, GPS, ICC, XMP) can leak into the output.
                clean = Image.new("RGB", sized.size)
                clean.paste(sized)
                clean.save(dest / f"{name}-{w}.webp", "WEBP", quality=82, method=6)
                clean.save(dest / f"{name}-{w}.jpg", "JPEG", quality=85, optimize=True, progressive=True)
            print(f"ok   {rel} -> {dest.relative_to(ROOT)}/{name}-{{{','.join(map(str, WIDTHS))}}}.{{webp,jpg}}")
    return 1 if problems else 0


def published() -> list[Path]:
    roots = list((ROOT / "builds").glob("*/photos")) + [ROOT / "site" / "photos"]
    return sorted(p for r in roots if r.exists() for p in r.rglob("*") if p.suffix.lower() in PUBLISHED_EXTS)


def check() -> int:
    files = published()
    bad = []
    for p in files:
        with Image.open(p) as img:
            exif = img.getexif()
            if len(exif) or "exif" in img.info or "xmp" in img.info:
                bad.append(p)
    for p in bad:
        print(f"EXIF {p.relative_to(ROOT)}")
    print(f"{len(files)} photo(s), {len(bad)} with metadata")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("inbox", type=Path)
    sub.add_parser("check")
    args = ap.parse_args()
    if args.cmd == "export":
        if not shutil.which("sips"):
            print("note: sips not found; HEIC files will fail (JPEG and PNG still work)")
        return export(args.inbox)
    return check()


if __name__ == "__main__":
    sys.exit(main())
