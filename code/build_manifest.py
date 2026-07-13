"""
build_manifest.py

Scans ../Photos/Monument Photos/, parses filenames, matches to monument names
from ../Acton Bounds.xlsx, and writes/updates photo_manifest.csv.

Safe to re-run: existing rows are never overwritten. Only new photos are added.
Unmatched photos are included with monument_name = "UNMATCHED" so you can
review and handle them manually.

Run from the code/ directory:
    python3 build_manifest.py
"""

import csv
import re
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths anchored to this script's location, so it runs from any working
# directory (HERE = code/, ROOT = the Bounds project folder).
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PHOTOS_DIR = ROOT / "Photos" / "Monument Photos"
XLSX_PATH = ROOT / "Acton Bounds.xlsx"
MANIFEST_PATH = HERE / "photo_manifest.csv"

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

# Recognized values for the `section` column. `monument`/`appendix` are the
# original values; the `intro*` values were added Jul 5 2026 so claude.ai can
# mark photos for use in introductory sections instead of per-monument pages.
# `intro` (bare) means "belongs in an intro section, placement TBD".
VALID_SECTIONS = {
    "monument",
    "appendix",
    "intro",
    "intro-visits",
    "intro-legal",
    "intro-history",
    "intro-map",
    "intro-other-towns",
    "intro-policy",
    "intro-cover",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def photo_location_to_monument(photo_location: str) -> str:
    """Convert the location portion of a photo filename to XLSX monument name.

    Photo filenames use hyphens between town names and spaces before street
    names.  XLSX names use slashes throughout.

    Examples:
        'Acton-Boxborough-Stow'          -> 'Acton/Boxborough/Stow'
        'Acton-Boxborough Central Street' -> 'Acton/Boxborough Central Street'
        'Acton-Carlisle 1'               -> 'Acton/Carlisle 1'
    """
    # Replace hyphens that separate town names (i.e. hyphens between words
    # that start with an uppercase letter) with slashes.
    # Strategy: split on hyphens, then re-join runs of Title-case tokens with
    # '/' until we hit a token that looks like a street qualifier.
    parts = photo_location.split("-")
    town_parts = []
    remainder_parts = []
    in_towns = True
    for i, part in enumerate(parts):
        # A part is still a town name if it starts with an uppercase letter
        # and contains no spaces (town names are single words like
        # "Acton", "Boxborough", digits like "1" or "2" are handled below).
        if in_towns and re.match(r'^[A-Z]', part):
            town_parts.append(part)
        else:
            in_towns = False
            remainder_parts.append(part)

    town_str = "/".join(town_parts)
    if remainder_parts:
        return town_str + " " + "-".join(remainder_parts)
    return town_str


def parse_filename(filename: str):
    """Parse a photo filename into (location_raw, monument_name, datetime_str, caption).

    Filename format:
        <location>, <YYYY-MM-DD HH-MM>[, <caption>].<ext>

    Returns a dict with keys: location_raw, monument_name, datetime_str, caption.
    Returns None if the filename doesn't match the expected pattern.
    """
    stem = Path(filename).stem  # strip extension
    parts = stem.split(", ", maxsplit=2)
    if len(parts) < 2:
        return None

    location_raw = parts[0].strip()
    datetime_str = parts[1].strip()

    # Validate datetime loosely: expect YYYY-MM-DD HH-MM
    if not re.match(r'^\d{4}-\d{2}-\d{2} \d{2}-\d{2}$', datetime_str):
        return None

    # Caption: the third comma-separated part, if present.
    # Duplicate-numbering suffixes like ", 2" or ", 3" are NOT captions.
    caption = ""
    if len(parts) == 3:
        raw_caption = parts[2].strip()
        if not re.match(r'^\d+$', raw_caption):
            caption = raw_caption

    monument_name = photo_location_to_monument(location_raw)
    return {
        "location_raw": location_raw,
        "monument_name": monument_name,
        "datetime_str": datetime_str,
        "caption": caption,
    }


def load_existing_manifest(path: Path) -> dict:
    """Load existing manifest rows keyed by filename."""
    existing = {}
    if not path.exists():
        return existing
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing[row["filename"]] = row
    return existing


def load_monument_names(xlsx_path: Path) -> set:
    """Load the set of valid monument names from the XLSX."""
    df = pd.read_excel(xlsx_path, sheet_name="Monuments")
    return set(df["Name"].dropna().str.strip())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Loading monument names from {XLSX_PATH} ...")
    monument_names = load_monument_names(XLSX_PATH)
    print(f"  {len(monument_names)} monuments found.")

    print(f"Scanning {PHOTOS_DIR} ...")
    photo_files = sorted(
        [f.name for f in PHOTOS_DIR.iterdir()
         if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png")]
    )
    print(f"  {len(photo_files)} photos found.")

    existing = load_existing_manifest(MANIFEST_PATH)
    print(f"  {len(existing)} existing manifest rows loaded (will be preserved).")

    new_count = 0
    unmatched = []
    rows = []

    for filename in photo_files:
        if filename in existing:
            # Preserve all existing edits exactly as-is
            rows.append(existing[filename])
            continue

        parsed = parse_filename(filename)
        if parsed is None:
            print(f"  WARNING: Could not parse filename: {filename!r}")
            rows.append({
                "filename": filename,
                "monument_name": "PARSE_ERROR",
                "datetime": "",
                "caption": "",
                "include": "yes",
                "exclude_reason": "",
                "section": "monument",
            })
            new_count += 1
            continue

        # Match monument name
        matched_name = parsed["monument_name"]
        if matched_name not in monument_names:
            # Try a case-insensitive search as fallback
            lower_map = {n.lower(): n for n in monument_names}
            matched_name = lower_map.get(parsed["monument_name"].lower(), "UNMATCHED")
            if matched_name == "UNMATCHED":
                unmatched.append((filename, parsed["monument_name"]))

        rows.append({
            "filename": filename,
            "monument_name": matched_name,
            "datetime": parsed["datetime_str"],
            "caption": parsed["caption"],
            "include": "yes",
            "exclude_reason": "",
            "section": "monument",
        })
        new_count += 1

    # Sort rows: matched monuments first (by monument_name then datetime),
    # unmatched at the end.
    def sort_key(row):
        is_problem = row["monument_name"] in ("UNMATCHED", "PARSE_ERROR")
        return (is_problem, row["monument_name"], row["datetime"])

    rows.sort(key=sort_key)

    # Write manifest
    with open(MANIFEST_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nManifest written to {MANIFEST_PATH}")
    print(f"  {new_count} new rows added.")
    print(f"  {len(existing)} existing rows preserved.")

    if unmatched:
        print(f"\n  WARNING: {len(unmatched)} photos could not be matched to a monument:")
        for filename, attempted_name in unmatched:
            print(f"    {filename!r}  (tried: {attempted_name!r})")
        print("  These appear in the manifest with monument_name = 'UNMATCHED'.")
        print("  You can correct them manually in the CSV.")

    # Report monuments with no photos at all
    monuments_with_photos = {
        row["monument_name"]
        for row in rows
        if row["monument_name"] not in ("UNMATCHED", "PARSE_ERROR")
    }
    monuments_without_photos = sorted(monument_names - monuments_with_photos)
    if monuments_without_photos:
        print(f"\n  Monuments with no photos ({len(monuments_without_photos)}):")
        for name in monuments_without_photos:
            print(f"    {name}")
    else:
        print("\n  All monuments have at least one photo.")

    # Report photo counts by section value, and flag any unrecognized value.
    section_counts = {}
    unrecognized_sections = set()
    for row in rows:
        section = row.get("section", "")
        section_counts[section] = section_counts.get(section, 0) + 1
        if section and section not in VALID_SECTIONS:
            unrecognized_sections.add(section)

    print(f"\n  Photos by section ({len(rows)} total):")
    for section, count in sorted(section_counts.items()):
        print(f"    {section or '(blank)'}: {count}")
    if unrecognized_sections:
        print(f"\n  WARNING: unrecognized section value(s): {sorted(unrecognized_sections)}")


if __name__ == "__main__":
    main()
