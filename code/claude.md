# CLAUDE.md — Acton Bounds Report Code

This file provides guidance to Claude Code when working in this directory.
It is maintained by the project owner in collaboration with Claude (claude.ai),
which handles overall document planning. Claude Code handles implementation.

---

## Source control

This file's directory (and `Photos/`) are tracked in a public GitHub repo:
https://github.com/jim-snyder-grant/acton-bounds — repo root is `Bounds/`
(the whole Insync-synced folder), but only code is tracked. `.gitignore`
is allowlist-style (deny everything by default, explicitly un-ignore only
specific files) because `Bounds/` has personal contact info (Contacts
sheet) and large reference material that must never be published.
Photos, the XLSX/manifest CSVs, generated PDFs, `.venv/`, and IDE cruft
are all excluded. The shared coordination `.md` files
(`acton_bounds_context.md`, `Acton Bounds TODO.md`, `Project Notes.md`,
`CHANGELOG.md`) are deliberately NOT in the repo yet — Jim wants to review
them for anything sensitive before they go public. claude.ai can read this
file directly at
raw.githubusercontent.com/jim-snyder-grant/acton-bounds/main/code/claude.md
without Jim relaying it by hand. Remember to `git add`/`commit`/`push`
after making changes to any tracked file — this doesn't happen
automatically the way Drive/Insync sync does.

**Before adding any new file to the allowlist, grep it for secrets first**
(Google Sheet/Doc/Drive IDs, API keys, hardcoded absolute paths with a
username/email in them, etc.) — this bit us once already (Jul 2 2026):
the Sheet ID and Drive folder ID were hardcoded in a few tracked files at
the very first commit, requiring a full repo delete + recreate to get a
clean history (fix-forward commits don't remove anything from git
history). The Google Sheet ID now lives in `Photos/sheet_id.txt`, a local
gitignored file `process_takeout.py` reads at runtime — follow that same
pattern (a local untracked file, not an environment variable, since the
scripts here are simple and this matches the existing `credentials.json`/
`token.json` precedent) for any other secret a script needs.

---

## Coordination with claude.ai — INBOX.md protocol

At the start of every Claude Code session, check the Bounds Google Drive
folder for any file named INBOX.md (or INBOX*.md).

If one or more exist:
1. Read each file carefully
2. Apply all described changes to the relevant local files (in place)
3. Delete the INBOX.md file(s) from Drive
4. Tell Jim what was applied

Jim reviews and approves the changes after the fact. If anything in the
inbox is ambiguous or seems wrong, apply your best interpretation and
flag it for Jim rather than leaving the inbox unprocessed.

**Insync duplicate-naming:** claude.ai can only create files, not edit or
delete them. If claude.ai creates a new file with the same name as an
existing Drive file (e.g. updating the same conceptual document, or simply
sending a second INBOX.md before Claude Code processed the first), Insync
renames the newer local copy by appending " (2)" (e.g. "INBOX (2).md").
If the "(2)" file is a stale duplicate of the same intended content,
resolve it by deleting the old file in Drive and renaming the "(2)"
version to the canonical name locally (Insync syncs the rename back). If
instead the "(2)" file has genuinely different content (e.g. a second,
distinct INBOX message sent before the first was processed), treat both
as separate messages to apply in creation order, then delete both.

The Bounds Drive folder ID is intentionally not written here since this
file is public on GitHub — ask Jim if you need it.

## CHANGELOG protocol

After any session in which you make substantive changes to shared files
(acton_bounds_context.md, TODO.md, Project Notes.md, CLAUDE.md, or any
other file a future Claude instance would need to read), append a brief
entry to CHANGELOG.md in the Bounds folder.

Format: YYYY-MM-DD [Claude Code] filename: one-line description
Newest entries go at the TOP of the log (below the header).

This allows claude.ai to quickly learn what changed since its last session
by reading just the top few lines of CHANGELOG.md, rather than re-reading
all shared files in full.

---

## Cover page — COMPLETE (do not modify)

The cover page (FrontPage.svg / FrontPage.pdf) is finished and lives in
the Bounds folder (not in code/). It was built with the SimpInkScr
Inkscape extension using `acton_cover.py` (in `code/`).

Claude Code does not need to touch the cover page. If it needs
regeneration, run `acton_cover.py` from within Inkscape's Simple Inkscape
Scripting extension dialog.

Key technical notes for reference:
- Photos are pre-downscaled via PIL (max 800px) before Inkscape sees them;
  embed=True is used. This keeps the exported PDF small (~5MB vs 145MB raw).
- Image placement uses a single SVG transform string passed to image():
    transform=f'translate({x0},{y0}) scale({scale_factor})'
  Do NOT use chained .scale() then .translate() — ordering goes wrong.
- Background rect must be drawn FIRST (painter's order).
- Text pt sizes render ~2x larger than expected; halve from normal print specs.

---

## Project Purpose

Generate a PDF report on the boundary markers (monuments) between Acton, MA
and its adjacent towns. The report has two parts:

1. **Introductory sections** — history, law, overview map, summary of visits.
   (Produced separately; not the responsibility of this code.)
2. **Monument pages** — one page per monument, generated from `../Acton Bounds.xlsx`
   and photos from `../Photos/Monument Photos/`. This is what the code here produces.

The two parts will be merged into a final PDF as a later step.

---

## Directory Layout

```
Bounds/                        # root of the project (Google Drive / Insync)
├── Acton Bounds.xlsx          # authoritative monument data (export of Google Sheet)
├── Photos/
│   └── Monument Photos/       # renamed photos from Google Takeout processing
│       └── *.jpg              # see filename convention below
├── code/                      # THIS directory — all code lives here
│   ├── CLAUDE.md              # this file
│   ├── bounds2pdf.py          # main report generator — produces output.pdf
│   ├── build_manifest.py      # builds/updates photo_manifest.csv
│   ├── photo_manifest.csv     # editable photo curation sheet (see below)
│   └── osm_screenshots/       # OSM map tiles, one per monument row index
│       └── osm_screenshot_*.jpg
```

---

## Running the Scripts

All scripts are run from the `code/` directory:

```bash
cd code/
python3 build_manifest.py     # step 1: build/update photo manifest
python3 bounds2pdf.py         # step 2: generate output.pdf
```

Dependencies: `pandas`, `reportlab`, `Pillow`, `playwright`. See existing imports in each file.
The pyenv environment for this project may be `photos` (check with the user).

---

## Data Source: Acton Bounds.xlsx

Sheet: `Monuments`

Key columns used by `bounds2pdf.py`:

| Column | Notes |
|---|---|
| `Name` | Monument identifier, e.g. `Acton/Boxborough/Stow` |
| `Type` | `Corner` or `Street Crossing` |
| `Status` | `Painted`, `Not Found`, `Documented`, `Found`, `Couldn't paint` |
| `Nearest Acton street name` | Always present |
| `Nearest other town street name` | Optional |
| `Nearby landmark` | Optional |
| `Notes on location` | Optional |
| `From 1904 description` | Optional — historical description |
| `Notes on Monument` | Optional |
| `Coordinate Source` | Text description of source |
| `Latitude` / `Longitude` | Decimal degrees WGS84; may be NaN if unknown |
| `OpenStreetMap link` | URL for map screenshot; may be NaN |
| `Tie-break number` | Used when multiple monuments share a name prefix |
| `Date of visit` | May be a float (Excel serial date) or string |

There are also town columns (`Boxborough`, `Littleton`, etc.) marked with `X`
for each town that shares that monument.

---

## Photo Filename Convention

Photos live in `../Photos/Monument Photos/` and follow this pattern:

```
{location name}, {YYYY-MM-DD HH-MM}[, {caption or duplicate number}].jpg
```

- **Location name** uses hyphens between town names and a space before street
  qualifiers: `Acton-Boxborough-Stow`, `Acton-Boxborough Central Street`
- **Datetime** is always `YYYY-MM-DD HH-MM` (note: `-` not `:` in time)
- **Third field** (after second comma) is either:
  - A plain integer (`2`, `3`, `4`) — duplicate-numbering suffix, NOT a caption
  - Descriptive text — this IS a caption

To convert a photo location name to an XLSX monument name:
replace `-` with `/` **only between town-name tokens** (capitalized single words).
Examples:
- `Acton-Boxborough-Stow` → `Acton/Boxborough/Stow`
- `Acton-Boxborough Central Street` → `Acton/Boxborough Central Street`
- `Acton-Carlisle 1` → `Acton/Carlisle 1`

---

## photo_manifest.csv

This CSV is the bridge between the photo files and `bounds2pdf.py`.
It is created and updated by `build_manifest.py` and **hand-edited by the user**
to curate which photos appear in the report and with what captions.

### Columns

| Column | Description |
|---|---|
| `filename` | Photo filename — **do not edit** (it's the key) |
| `monument_name` | Matched XLSX monument name — correct manually if `UNMATCHED` |
| `datetime` | Parsed from filename — used for sort order |
| `caption` | Editable — shown under photo in report; blank is fine |
| `include` | `yes` or `no` — whether to include in report |
| `exclude_reason` | Free text note explaining why `include=no` |
| `section` | `monument` (default) — reserved for future use (e.g. `appendix`) |
| `orientation` | `landscape`/`portrait`/`square`, computed by `add_cover_columns.py` for included photos — used by the cover-collage script |
| `cover_candidate` | `yes`/blank — defaults `yes` for included photos; lets Jim exclude a photo from the cover collage without touching `include` |
| `docushare_url` | Populated by `merge_docushare.py`; blank until that photo is uploaded and scraped |

### build_manifest.py behavior

- Scans `../Photos/Monument Photos/` for `.jpg`/`.jpeg`/`.png` files
- Parses each filename into monument_name, datetime, caption
- Matches monument_name against the XLSX Monuments sheet
- **Preserves all existing rows exactly** — only adds rows for new photos
- Sorts output: matched monuments alphabetically, then by datetime;
  `UNMATCHED` and `PARSE_ERROR` rows at the bottom
- Prints a summary including:
  - Count of new rows added
  - List of UNMATCHED photos (need manual correction)
  - List of monuments with NO photos (user may want to photograph these)

---

## bounds2pdf.py — Current State and Planned Changes

### What it currently does

For each row in the Monuments sheet, it creates one PDF page containing:
- Monument name + type (centered heading with underline)
- Status (bold label + grey-highlighted value)
- Coordinates (table with lat/long + source), or "Unknown Coordinates"
- Nearest Acton street name
- Nearest other town street name (if present)
- Nearby landmark (if present)
- Notes on location (if present)
- 1904 description (if present)
- Notes on Monument (if present)
- OSM map screenshot (captured live via Playwright, 300×300px)

### Current state

PDF library: **ReportLab** (switched from borb — borb had layout problems).

All major features are implemented and working:
- `networkidle` page navigation (replaced old fragile `asyncio.sleep` pattern)
- Date of visit (Excel serial dates → "Month D, YYYY"; "Not yet visited" if NaN)
- Witnesses line from Contacts sheet, with `(Town)` annotation for non-Acton attendees
- Defensive NaN handling throughout
- Photo integration: reads `photo_manifest.csv`; dynamic grid (2-across for
  landscape sets, 3-across for all-portrait sets, wider as needed); captions
  in small italic; spills to second page only if truly can't fit at min size
- Two-column layout: text left, OSM map right (150×150pt)

### Remaining work

#### OSM screenshot caching (nice to have)

Currently screenshots are re-captured on every run, which is slow (~4 seconds
per monument × 59 monuments ≈ 4 minutes). The files `osm_screenshot_N.jpg`
already exist from previous runs. Add a cache check:
- If `osm_screenshot_{row}.jpg` exists and the OSM link for that row hasn't
  changed, skip the browser capture and use the cached file.
- Add a `--force-screenshots` flag to bypass the cache.

#### DocuShare photo linking and clickable images

Full-resolution originals are hosted in DocuShare (Acton's permanent
archive, same place the finished report lives). See
`../CLAUDE.md note - DocuShare photo linking.md` for full spec; summary:

**Manifest schema:** `photo_manifest.csv` has a `docushare_url` column.
Empty values are fine — `bounds2pdf.py` handles blank gracefully (no link,
no error) so the PDF can be generated before all uploads are done.

**Implemented and verified Jun 30 2026** — scraper, merge, and link rendering
all built and tested against the live "Perambulation Images" collection
(12 photos uploaded so far). 10 working `doc.actonma.gov` photo links and
48 working `openstreetmap.org` map links confirmed present in the
generated PDF.

**Full batch uploaded and merged Jul 2 2026** — Jim uploaded all remaining
photos (177 documents in the collection, 173 unique filenames — 4 are
duplicate uploads, 2 document IDs each; harmless for linking,
`merge_docushare.py` just uses one, but worth cleaning up in DocuShare
eventually — see "Open items"). After the parsing fix below, **all 173
local photos have a `docushare_url`** — full coverage. No pagination issue
was hit — the collection listed all 177 documents on a single page, so the
">100 results" pagination warning in `scrape_docushare.py` is currently a false
alarm at this collection size (see "Open items" below).

**Bug found and fixed Jul 2 2026:** `merge_docushare.py`'s `MANIFEST_COLUMNS`
was stale from before the `orientation`/`cover_candidate` columns were
added — since it rewrites the whole manifest via
`csv.DictWriter(fieldnames=MANIFEST_COLUMNS)`, running it unmodified would
have silently dropped both columns. Fixed; verify `MANIFEST_COLUMNS` in
both `build_manifest.py` and `merge_docushare.py` stay in sync with the
manifest's actual columns whenever either changes.

**DocuShare's link URL text mangles filenames, but `dc:title` doesn't
(investigated Jul 2 2026):** the URL-encoded filename DocuShare puts in the
`<tr about="...">`/`<a href="...">` links looked mangled for some
documents — a literal `:` truncated that text down to everything after the
colon (e.g. "Context from Rte 27: Marker is up the embankment.jpg" showed
up there as just " Marker is up the embankment.jpg"), and apostrophes/
quotes were replaced with junk (`'` → `_`, `"` → `_22`). This looked like
real data loss at first, but isn't: every document row also has
`<strong property="dc:title">...</strong>` with the complete, correct
original filename, and the `Get/Document-{ID}/...` download URL resolves
purely by Document ID — **the trailing filename text in the URL is
cosmetic and never validated** (confirmed by successfully downloading a
document using a completely different, made-up filename in the URL). So
`scrape_docushare.py` now parses `dc:title` for the `filename` field (used
for manifest matching) and falls back to the URL-encoded path only if
`dc:title` is missing; `docushare_url` itself still comes from the `about`
path since that's a proven-working link regardless of how it displays. No
re-upload was needed for any of the affected photos.

One real upload-time issue Jim did hit: uploading files **one at a time**
with a colon in the filename failed outright (had to manually fix the
title afterward via DocuShare's edit UI). Uploading via drag-and-drop of
multiple files at once did not have this problem — Jim's practice going
forward. `Photos/process_takeout.py`'s caption sanitization (colons →
hyphens, apostrophes/quotes stripped — see `Photos/CLAUDE.md`) remains in
place as a belt-and-suspenders fix regardless of upload method.

**Workflow once photos are uploaded to DocuShare:**
1. Jim uploads a batch of photos to the DocuShare collection via the web UI (manual).
2. Run `python3 scrape_docushare.py` — fetches the collection page, parses
   `<tr about="...">` attributes to extract `Document-NNNNN` IDs and filenames,
   writes `docushare_urls.csv`. Detects and reports DocuShare's login/license-error
   pages instead of silently writing empty data (see guest session note below).
3. Run `python3 merge_docushare.py` — joins `docushare_urls.csv` into
   `photo_manifest.csv` on filename, populating the `docushare_url` column.
4. `bounds2pdf.py` picks up `docushare_url` from the manifest. Each photo
   *image itself* (not just the caption) is a clickable link to its DocuShare
   original, via a `LinkableImage` flowable that calls
   `canvas.linkURL(url, (0,0,w,h), relative=1)` after drawing — `relative=1`
   anchors the link rect to the image's own draw-time position so it's
   correct regardless of table/hAlign placement. Captions stay plain text
   (no link wrapping). A centered "Click any picture to see full size" note
   appears above the photo grid, but only on monument pages where at least
   one photo has a `docushare_url` — most pages don't show it yet since
   most photos aren't uploaded. No `docushare_url` = no link, omitted gracefully.
5. The OSM map image on each page uses the same `LinkableImage` approach,
   linking to the live interactive OpenStreetMap page at that monument's
   coordinates (the `OpenStreetMap link` column already in the XLSX, also
   used to drive screenshot capture) — no DocuShare upload needed for maps.

**DocuShare URL format:**
`https://doc.actonma.gov/dsweb/Get/Document-{ID}/{url-encoded-filename}`

IDs are stable across revisions (Jim can replace a photo later; URL stays valid).
IDs are NOT contiguous — never generate or guess them; always scrape from the listing.

**Guest session concurrency limit (discovered Jun 30 2026):** DocuShare's
anonymous access appears to allow only one concurrent guest session.
Re-running `scrape_docushare.py` shortly after a previous fetch can return
a "DocuShare License Error" or logged-out landing page instead of the real
listing. Wait a few minutes between runs if this happens.

**Open items** (photo linking itself is complete — all 173 local photos
have a `docushare_url` as of Jul 2 2026 — these are just cleanup):
- Pagination: `scrape_docushare.py` still warns whenever 100+ results are
  found, but as of Jul 2 2026 the collection (177 documents) rendered on a
  single page with nothing clipped — confirmed by diffing scraped filenames
  against `Photos/Monument Photos/` (see "Full batch uploaded" note above).
  The warning can likely be removed or downgraded, but leaving it as a
  no-op sanity check is harmless; hasn't been revisited yet.
- 4 filenames had duplicate DocuShare uploads (2 document IDs each) — Jim
  reports deleting the extras Jul 2 2026, but this hasn't been verified via
  a fresh scrape yet (no HTML re-saved after the deletion). Verify next
  time `scrape_docushare.py` runs against fresh data — the duplicate
  document IDs to check are no longer present:
  `Acton-Boxborough Littlefield Road, 2025-10-31 15-01.jpg` (Document-98988,
  98994), `Acton-Boxborough Littlefield Road, 2025-11-06 13-53, 2.jpg`
  (Document-98989, 98990), `Acton-Boxborough Summer Street, 2025-09-16
  09-49.jpg` (Document-98996, 98997), `Acton-Littleton W B Marker on Fort
  Pond Road, 2026-03-14 10-02.png` (Document-98963, 99112).

---

## Workflow for Adding New Photos

1. Take new photos; let them sync to Google Photos
2. Create a new Google Takeout export (Photos only)
3. Drop the new `takeout-*.zip` into `../Photos/`
4. Run `python3 ../Photos/process_takeout.py` from the Photos directory
   (it re-processes all zips together for consistent naming)
5. Run `python3 build_manifest.py` from `code/` — new photos are added to
   the manifest; existing edits are preserved
6. Edit `photo_manifest.csv` to set captions, exclude unwanted photos, etc.
7. Upload batch to DocuShare (manual), then run scrape + merge scripts to
   populate `docushare_url` column (see above)
8. Run `python3 bounds2pdf.py` to regenerate the report

---

## Reverse geocoding (planned — see TODO.md Field work)

Once monument coordinates are finalized, generate a CSV (name, lat, lon)
for Jim to run through Geoapify's free reverse-geocoding web tool
(geoapify.com/tools/reverse-geocoding-online, no account needed, accepts
CSV/Excel, returns addresses + distance-to-nearest-address) to get a
"Nearest address" column for monuments lacking one. The distance column is
the signal for discarding bad matches (woodland corners far from any
address).

**If a scripted (non-manual) geocoding step is ever needed** — e.g. a
re-run after coordinate updates — claude.ai's research recommends
**geocode.maps.co** (OpenStreetMap-based, simple API, free with account)
over CSV2GEO, GeoPlugin, or the Google Maps API. Geoapify itself also has
an API if preferred for consistency with the manual step. Don't build a
scripted version until Jim actually asks for one — the manual web UI step
is the current plan.

---

## Key Design Decisions (agreed with project owner)

- **One page per monument** is the goal; spill to two pages only when photos
  genuinely won't fit at minimum readable size
- **Photos in datetime order**, two-across or more as needed
- **Captions** come from the manifest, not the filename (so they're editable
  without touching the archive)
- **OSM maps** are captured via Playwright (Chromium); the existing
  screenshot region `{x:352, y:100, width:574, height:574}` should be
  reviewed — it was tuned for a specific viewport and may need adjustment
- **No proprietary data** — all source material is public or town records
- The **Google Sheet** (not the XLSX) is the authoritative data source;
  the XLSX is an export. Re-export before generating a final report.

---

## Communication with claude.ai

The overall document plan, introductory sections, and archiving strategy
are managed in a claude.ai conversation (not here). If you need to relay
findings back to that conversation, paste relevant output or questions there.
The context file for claude.ai is `../acton_bounds_context.md` (in the Bounds folder, one level up).
This CLAUDE.md is updated by claude.ai when plans change.
