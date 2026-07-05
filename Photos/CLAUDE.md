# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project purpose

Processing Google Photos Takeout photos of Acton, MA town boundary monuments (perambulation bounds). The script extracts photos from Takeout zips and renames them to a standard convention.

## Running the script

```bash
python3 process_takeout.py
```

Requires Python 3.9+ (uses `zoneinfo`). Install dependencies first:

```bash
pip install -r requirements.txt
```

The pyenv environment for this project is `photos`.

## What the script does

1. Authenticates with Google (OAuth, opens browser on first run — requires `credentials.json`)
2. Reads valid location names from the Google Sheet (Monuments tab, first column)
3. Scans all `takeout-*.zip` files in the current directory
4. For each image, looks up metadata in the `.supplemental-met.json` sidecar
5. Validates the location name against the sheet, applies corrections, builds output filename
6. Extracts renamed photos to `Monument Photos/`
7. Writes `validation_report.txt` and `site_names_cache.txt`

## Output filename convention

`{location name}, {YYYY-MM-DD HH-MM}[, {photo note}].{ext}`

- Location name comes from the Google Photos description field, with `/` replaced by `-`
- Timestamp from `photoTakenTime` in the supplemental JSON, converted to US/Eastern
- Photos with the same location + minute get `, 2`, `, 3` suffixes (consistent across all zips)
- Towns in location names are listed alphabetically (e.g. `Acton/Carlisle/Westford`)
- Photo notes (captions) are sanitized before being written into the filename
  — see "Caption sanitization for DocuShare" below

## Caption sanitization for DocuShare

Photos are eventually uploaded to Acton's DocuShare archive (manual step,
see `code/claude.md`), and DocuShare mangles certain characters in
filenames on upload: `:` **truncates the filename to everything after
it**, losing the location/date prefix entirely, and straight/curly
apostrophes and quotes get replaced with junk (`'` → `_`, `"` → `_22`).
This was discovered Jul 2 2026 after uploading a real batch of photos.

To prevent this, `sanitize_caption_text()` (near the top of
`process_takeout.py`) runs on every photo note before the output filename
is built: `:` → `-`, apostrophes/quotes stripped entirely. This means the
Google Photos description itself is left untouched (colons etc. are fine
there) — only the derived local filename is cleaned up, automatically, on
every run. `validation_report.txt` includes a "Captions sanitized for
DocuShare-unsafe characters" section showing before/after for every
caption this affected, so a caption edited to reintroduce one of these
characters is easy to spot on the next run.

Photos processed by `process_takeout.py` *before* this fix may still have
one of these characters in their local filename and/or in an already-
uploaded DocuShare document; those need a fresh Takeout run (to regenerate
the local filename) followed by a manual delete + re-upload on DocuShare.

## Key data

- Google Sheet (Monuments tab) — authoritative source of location names. Sheet ID intentionally not written here since this file is public on GitHub — ask Jim if you need it.
- `takeout-*.zip` — Google Photos Takeout archives (add new ones to this folder for future runs)
- `Monument Photos/` — output folder (gitignored); never deleted between runs, files overwritten if same name
- `validation_report.txt` — generated on each run (gitignored)
- `site_names_cache.txt` — saved sheet names from last run; used to detect if names are removed or renamed (gitignored)

## Takeout format notes

This takeout uses `.supplemental-met.json` sidecar files (not the classic `.json` format). Each image file has a corresponding `{filename}.supplemental-met.json`. Raw motion photo `.MP` files are ignored; only `.jpg`, `.JPG`, and `.png` files are processed.

## Adding corrections

**Wrong location name in a photo description** — add to `LOCATION_CORRECTIONS` at the top of the script:
```python
LOCATION_CORRECTIONS = {
    "Acton/Concord/Sudbury/Maynard": "Acton/Concord/Maynard/Sudbury",
    ...
}
```

**Photo with no supplemental JSON** — add to `MANUAL_METADATA` with `(location_name, photo_note, "YYYY-MM-DD HH-MM")`:
```python
MANUAL_METADATA = {
    "IMG_4091.JPG": ("Acton/Littleton 2", "", "2025-04-24 15-22"),
    ...
}
```

**Photos with no description are skipped** and listed in the anomaly report.

## Adding a new takeout zip

Drop the new `takeout-*.zip` file into this directory and re-run the script. All zips are processed together each time, so counts and duplicate numbering are always consistent across the full set.

## photo_manifest.csv section column (added Jul 5 2026)

`photo_manifest.csv` (built by `code/build_manifest.py`, not by anything
in this directory) has a `section` column marking where each photo is
used: `monument` (default, per-monument page), `appendix`, `intro-cover`,
or one of the intro-section values (`intro`, `intro-visits`,
`intro-legal`, `intro-history`, `intro-map`, `intro-other-towns`,
`intro-policy`) for photos claude.ai is using in the introductory
sections instead of a monument page. `include = yes` applies to all of
these — `include = no` is only for photos excluded from the report
entirely. See `code/claude.md`'s "Section column conventions" for the
full list; this note just exists so it's visible from this directory too.
