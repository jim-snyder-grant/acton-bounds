"""
add_cover_columns.py

Adds `orientation` and `cover_candidate` columns to photo_manifest.csv, for
use by the cover-collage Inkscape tooling.

- orientation: landscape / portrait / square (square treated as landscape
  for cover purposes), computed from each included photo's pixel dimensions.
  Blank for excluded rows.
- cover_candidate: defaults to "yes" for included rows, blank for excluded
  rows. Lets Jim exclude specific photos from the cover collage without
  touching the main `include` column.

Safe to re-run: existing non-blank values in either column are preserved
(Jim may have manually overridden them). Only blank values are filled in.

Run from the code/ directory:
    python3 add_cover_columns.py
"""

import csv
from pathlib import Path

from PIL import Image

PHOTOS_DIR = Path("../Photos/Monument Photos")
MANIFEST_PATH = Path("photo_manifest.csv")

MANIFEST_COLUMNS = [
    "filename",
    "monument_name",
    "datetime",
    "caption",
    "include",
    "exclude_reason",
    "section",
    "orientation",
    "cover_candidate",
    "docushare_url",
]


def classify_orientation(width: int, height: int) -> str:
    if width > height:
        return "landscape"
    if height > width:
        return "portrait"
    return "square"


def main():
    with open(MANIFEST_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total_included = 0
    portrait_count = 0
    landscape_count = 0
    square_count = 0
    preserved_count = 0
    filled_count = 0
    errors = []

    for row in rows:
        # Ensure both columns exist on every row dict (older rows may lack them).
        row.setdefault("orientation", "")
        row.setdefault("cover_candidate", "")

        included = row.get("include", "").strip().lower() == "yes"

        if not included:
            # Leave orientation blank; cover_candidate blank/no for excluded rows.
            if not row["cover_candidate"].strip():
                row["cover_candidate"] = ""
            continue

        total_included += 1

        # cover_candidate: default to "yes", preserve existing value.
        if row["cover_candidate"].strip():
            pass  # preserve Jim's existing override
        else:
            row["cover_candidate"] = "yes"

        # orientation: preserve existing value, else compute from the file.
        if row["orientation"].strip():
            preserved_count += 1
            orientation = row["orientation"].strip().lower()
        else:
            path = PHOTOS_DIR / row["filename"]
            try:
                with Image.open(path) as img:
                    width, height = img.size
                orientation = classify_orientation(width, height)
                row["orientation"] = orientation
                filled_count += 1
            except Exception as e:
                errors.append((row["filename"], str(e)))
                orientation = ""

        if orientation == "portrait":
            portrait_count += 1
        elif orientation == "landscape":
            landscape_count += 1
        elif orientation == "square":
            square_count += 1

    with open(MANIFEST_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Manifest updated: {MANIFEST_PATH}")
    print(f"\nTotal included photos: {total_included}")
    print(f"  Portrait:  {portrait_count}")
    print(f"  Landscape: {landscape_count}")
    print(f"  Square:    {square_count}")
    print(f"\nOrientation already set (preserved): {preserved_count}")
    print(f"Orientation newly filled in:          {filled_count}")

    if errors:
        print(f"\nCould not open {len(errors)} file(s) (orientation left blank):")
        for filename, err in errors:
            print(f"  {filename!r}: {err}")
    else:
        print("\nAll included photo files opened successfully.")


if __name__ == "__main__":
    main()
