#!/usr/bin/env python3
"""
Extract and rename Google Photos Takeout photos for Acton Bounds monuments.

Usage:
    python3 process_takeout.py

Reads:  most recent takeout-*.zip in current directory, Google Sheet for site names
Writes: Monument Photos/, validation_report.txt, site_names_cache.txt

On each run the previous Monument Photos/ folder is archived to
"Monument Photos - YYYY-MM-DD/" before being recreated from scratch.
"""

import difflib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

EASTERN = ZoneInfo("America/New_York")
OUTPUT_DIR = Path("Monument Photos")
SITE_NAMES_CACHE = Path("site_names_cache.txt")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
# Sheet ID lives in a local, gitignored file (not this script) since this
# file is public on GitHub -- see SHEET_ID_FILE below.
SHEET_ID_FILE = "sheet_id.txt"
SHEET_TAB = "Monuments"
ALBUM_PREFIX = "Takeout/Google Photos/Acton Bounds/"

# Manual metadata for files that have no supplemental JSON.
# Format: filename -> (location_name, photo_note, "YYYY-MM-DD HH-MM")
MANUAL_METADATA = {
    "WBMarker  on Fort Pond Road.png": (
        "Acton/Littleton W B Marker on Fort Pond Road", "", "2026-03-14 10-02"
    ),
    "PXL_20251031_190147925.jpg": (
        "Acton/Boxborough Littlefield Road", "", "2025-10-31 15-01"
    ),
    "PXL_20251031_190140807.jpg": (
        "Acton/Boxborough Littlefield Road", "", "2025-10-31 15-01"
    ),
    "PXL_20250519_204403162.NIGHT.jpg": (
        "Acton/Littleton 2", "", "2025-05-19 16-44"
    ),
    "IMG_4091.JPG": (
        "Acton/Littleton 2", "", "2025-04-24 15-22"
    ),
}

# Known corrections: description text -> canonical sheet name
LOCATION_CORRECTIONS = {
    "Acton/Concord/Sudbury/Maynard": "Acton/Concord/Maynard/Sudbury",
    "Acton/Westford/Carlisle": "Acton/Carlisle/Westford",
    "WActon/Westford/Carlisle": "Acton/Carlisle/Westford",
}

# DocuShare mangles these characters when photos are uploaded there later:
# ':' truncates the filename to everything after it (losing the location/date
# prefix entirely), and straight/curly quotes get replaced with garbage
# ('_22' etc). Sanitize captions here so every filename this script produces
# is DocuShare-safe from the start.
COLON_REPLACEMENT = "-"
STRIP_CHARS = "'’‘‚\"“”„"


def sanitize_caption_text(text: str) -> str:
    sanitized = text.replace(":", COLON_REPLACEMENT)
    for ch in STRIP_CHARS:
        sanitized = sanitized.replace(ch, "")
    return sanitized


def get_credentials() -> Credentials:
    creds = None
    if Path(TOKEN_FILE).exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        Path(TOKEN_FILE).write_text(creds.to_json(), encoding="utf-8")
        print("Authentication successful. Token saved.")
    return creds


def load_sheet_id() -> str:
    path = Path(SHEET_ID_FILE)
    if not path.exists():
        raise SystemExit(
            f"{SHEET_ID_FILE} not found -- create it with the Google Sheet ID "
            f"on a single line (this file is gitignored, not committed)."
        )
    return path.read_text(encoding="utf-8").strip()


def load_site_names(creds: Credentials) -> list[str]:
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(load_sheet_id()).worksheet(SHEET_TAB)
    values = sheet.col_values(1)  # first column
    # Skip header row ("Name"), preserve sheet order
    return [v.strip() for v in values[1:] if v.strip()]


def check_site_names_changed(current: list[str], anomalies: list[str]) -> None:
    """Warn if names have been removed or changed since the last run."""
    if not SITE_NAMES_CACHE.exists():
        return
    previous = set(SITE_NAMES_CACHE.read_text(encoding="utf-8").splitlines())
    for name in sorted(previous - set(current)):
        anomalies.append(f"Site name removed from sheet since last run: '{name}'")


def save_site_names_cache(names: list[str]) -> None:
    SITE_NAMES_CACHE.write_text("\n".join(names) + "\n", encoding="utf-8")


def archive_output_dir() -> None:
    """Rename existing Monument Photos/ to a dated archive folder."""
    if not OUTPUT_DIR.exists():
        return
    date_str = datetime.now(tz=EASTERN).strftime("%Y-%m-%d")
    archive = Path(f"{OUTPUT_DIR} - {date_str}")
    # If an archive for today already exists, add a counter
    counter = 1
    candidate = archive
    while candidate.exists():
        counter += 1
        candidate = Path(f"{OUTPUT_DIR} - {date_str} - {counter}")
    shutil.move(str(OUTPUT_DIR), str(candidate))
    print(f"Archived previous photos to '{candidate}/'")


def format_timestamp(unix_ts: str) -> str:
    dt = datetime.fromtimestamp(int(unix_ts), tz=timezone.utc).astimezone(EASTERN)
    return dt.strftime("%Y-%m-%d %H-%M")


def close_matches(name: str, valid: set[str]) -> list[str]:
    return difflib.get_close_matches(name, valid, n=3, cutoff=0.6)


def collect_image_files(zf: zipfile.ZipFile) -> list[str]:
    all_entries = set(zf.namelist())
    return sorted(
        e for e in all_entries
        if e.startswith(ALBUM_PREFIX)
        and not e.endswith("/")
        and not e.endswith(".json")
        and Path(e).suffix.lower() in {".jpg", ".jpeg", ".png"}
    )


def main():
    creds = get_credentials()
    print("Loading site names from Google Sheet...")
    site_names_ordered = load_site_names(creds)
    site_names = set(site_names_ordered)
    print(f"Loaded {len(site_names)} site names.")

    zip_files = sorted(Path(".").glob("takeout-*.zip"))
    if not zip_files:
        print("No takeout-*.zip files found.")
        return
    zip_path = zip_files[-1]  # most recent by filename (timestamp is in the name)
    print(f"Using zip: {zip_path.name}")

    anomalies = []
    check_site_names_changed(site_names_ordered, anomalies)

    bad_locations = {}       # unrecognised name -> [filenames]
    output_names_used = {}   # output filename -> source filename (duplicate check)
    location_counts = {name: 0 for name in site_names_ordered}
    to_extract = []          # (zip_entry, output_path) pairs
    sanitized_captions = []  # (source filename, before, after) for changed captions

    with zipfile.ZipFile(zip_path) as zf:
        all_entries = set(zf.namelist())
        image_files = collect_image_files(zf)

        for entry in image_files:
            fname = Path(entry).name
            json_entry = entry + ".supplemental-met.json"

            if json_entry not in all_entries:
                if fname in MANUAL_METADATA:
                    location_name, photo_note, timestamp_str = MANUAL_METADATA[fname]
                else:
                    anomalies.append(f"No supplemental JSON: {fname}")
                    continue
            else:
                with zf.open(json_entry) as f:
                    meta = json.load(f)

                description = meta.get("description", "").strip()

                if not description:
                    anomalies.append(f"Empty description: {fname}")
                    continue

                if "," in description:
                    location_name, photo_note = description.split(",", 1)
                    location_name = location_name.strip()
                    photo_note = photo_note.strip()
                else:
                    location_name = description.strip()
                    photo_note = ""

                location_name = LOCATION_CORRECTIONS.get(location_name, location_name)

                if location_name not in site_names:
                    bad_locations.setdefault(location_name, []).append(fname)
                    continue

                photo_taken = meta.get("photoTakenTime", {}).get("timestamp", "")
                if not photo_taken:
                    anomalies.append(f"No photoTakenTime: {fname}")
                    continue

                timestamp_str = format_timestamp(photo_taken)

            location_counts[location_name] += 1
            safe_location = location_name.replace("/", "-")
            ext = Path(entry).suffix

            safe_note = sanitize_caption_text(photo_note)
            if safe_note != photo_note:
                sanitized_captions.append((fname, photo_note, safe_note))

            if safe_note:
                out_name = f"{safe_location}, {timestamp_str}, {safe_note}{ext}"
            else:
                out_name = f"{safe_location}, {timestamp_str}{ext}"

            base_name = out_name
            counter = 1
            while out_name in output_names_used:
                counter += 1
                stem = Path(base_name).stem
                out_name = f"{stem}, {counter}{ext}"

            if counter > 1:
                anomalies.append(
                    f"Duplicate timestamp — renamed to '{out_name}': {fname}"
                )
            output_names_used[out_name] = fname
            to_extract.append((entry, OUTPUT_DIR / out_name))

    # ── Report ────────────────────────────────────────────────────────────

    report_lines = []

    def emit(line=""):
        print(line)
        report_lines.append(line)

    emit("=" * 60)
    emit("VALIDATION REPORT")
    emit("=" * 60)

    if bad_locations:
        emit(f"\nLocation names not in sheet ({len(bad_locations)} unique):")
        for name, files in sorted(bad_locations.items()):
            suggestions = close_matches(name, site_names)
            emit(f"  '{name}'  ({len(files)} photo(s))")
            for fn in files:
                emit(f"    - {fn}")
            if suggestions:
                emit(f"    Close matches: {', '.join(repr(s) for s in suggestions)}")
    else:
        emit("\nAll location names match sheet entries.")

    missing = [loc for loc, n in location_counts.items() if n == 0]
    if missing:
        emit(f"\nSheet locations with no photos ({len(missing)}):")
        for loc in missing:
            emit(f"  {loc}")
    else:
        emit("\nAll sheet locations have at least one photo.")

    if anomalies:
        emit(f"\nOther anomalies ({len(anomalies)}):")
        for a in anomalies:
            emit(f"  {a}")

    if sanitized_captions:
        emit(f"\nCaptions sanitized for DocuShare-unsafe characters ({len(sanitized_captions)}):")
        for fname, before, after in sanitized_captions:
            emit(f"  {fname}")
            emit(f"    before: {before!r}")
            emit(f"    after:  {after!r}")
    else:
        emit("\nNo captions needed sanitizing (no ':', quote, or apostrophe characters found).")

    emit()
    emit("=" * 60)
    emit("PHOTOS PER LOCATION")
    emit("=" * 60)
    for loc in location_counts:
        emit(f"  {location_counts[loc]:>3}  {loc}")

    Path("validation_report.txt").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    save_site_names_cache(site_names_ordered)
    print("\nReport saved to validation_report.txt")

    # ── Extract ───────────────────────────────────────────────────────────

    archive_output_dir()
    OUTPUT_DIR.mkdir()

    print(f"\n{'-' * 60}")
    print(f"Extracting {len(to_extract)} photos to '{OUTPUT_DIR}/'...")
    print("-" * 60)

    with zipfile.ZipFile(zip_path) as zf:
        for entry, out_path in to_extract:
            with zf.open(entry) as src:
                out_path.write_bytes(src.read())
            print(f"  {Path(entry).name}  ->  {out_path.name}")

    print(f"\nDone. {len(to_extract)} photos written to '{OUTPUT_DIR}/'")


if __name__ == "__main__":
    main()
