"""
check_photo_names.py

Validate that photo filenames in a folder follow the Acton Bounds naming
convention (see the "Photos" section in the repo README):

    Location, YYYY-MM-DD HH-MM[, N][, Caption].ext

Reports (1) names that won't parse and (2) names that parse but whose location
matches no monument AND isn't already resolved in photo_manifest.csv. (2) is
manifest-aware on purpose: some photo filenames carry only a partial location
-- e.g. "Acton-Carlisle-Concord" for the monument "Acton/Carlisle/Concord Pope
Road Witness Marker" -- which build_manifest.py flags as UNMATCHED and a human
then corrects in the manifest. Those corrected rows are the source of truth, so
a name resolved there is NOT re-flagged. Reuses build_manifest.py's parser so
there is a single source of truth for the convention.

Usage:
    python3 check_photo_names.py [folder]

Default folder: ../Photos/Monument Photos/ (same as build_manifest.py). Exits 0
when everything is clean, 1 when any problems were found -- so it can gate a
build. This checks names only; it is not part of the normal build.
"""

import sys
from pathlib import Path

from build_manifest import (
    PHOTOS_DIR, XLSX_PATH, MANIFEST_PATH, parse_filename,
    load_monument_names, load_existing_manifest,
)

IMAGE_EXTS = (".jpg", ".jpeg", ".png")


def main():
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else PHOTOS_DIR
    if not folder.is_dir():
        sys.exit(f"Not a directory: {folder}")

    monument_names = load_monument_names(XLSX_PATH)
    lower = {n.lower(): n for n in monument_names}
    existing = load_existing_manifest(MANIFEST_PATH)  # filename -> row

    files = sorted(f.name for f in folder.iterdir()
                   if f.is_file() and f.suffix.lower() in IMAGE_EXTS)

    unparseable = []
    unmatched = []
    for name in files:
        parsed = parse_filename(name)
        if parsed is None:
            unparseable.append(name)
            continue
        mn = parsed["monument_name"]
        if mn in monument_names or mn.lower() in lower:
            continue  # filename location matches a monument directly
        # Partial/ambiguous location: fine only if the manifest already
        # resolves this file to a real monument (hand-corrected UNMATCHED).
        row = existing.get(name)
        if row and row.get("monument_name") in monument_names:
            continue
        unmatched.append((name, mn))

    print(f"Checked {len(files)} image file(s) in {folder}")

    if unparseable:
        print(f"\n{len(unparseable)} name(s) do NOT match the convention "
              f"'Location, YYYY-MM-DD HH-MM[, N][, Caption].ext':")
        for n in unparseable:
            print(f"   {n}")
    if unmatched:
        print(f"\n{len(unmatched)} name(s) parse but their location is not a "
              f"monument in the spreadsheet:")
        for n, mn in unmatched:
            print(f"   {n}   (location read as: {mn!r})")

    if not unparseable and not unmatched:
        print("All good -- every filename parses and matches a monument.")
        return 0
    print("\nFix the names above (or add the monument to the sheet) and re-run.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
