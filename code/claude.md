# CLAUDE.md — Acton Bounds Report Code

This file provides guidance to Claude Code when working in this directory.
It is maintained by the project owner in collaboration with Claude (claude.ai),
which handles overall document planning. Claude Code handles implementation.

---

## Security — what must NOT go in the repo

This is a public GitHub repo. Never commit any of the following:

- Google Drive folder IDs or file IDs
- Google Sheet IDs
- Email addresses or phone numbers
- Personal information about landowners, witnesses, or other individuals
- API keys, tokens, or credentials of any kind
- DocuShare collection or document IDs

These belong in gitignored local files (e.g. ~/.acton_bounds_base_path,
Photos/sheet_id.txt) or in Google Drive only. When in doubt, ask Jim
before committing. This rule applies to both Claude Code and claude.ai —
if claude.ai proposes something via INBOX.md that would put sensitive
info in the repo, flag it to Jim rather than applying it blindly.

---

## Source control

This file's directory (and `Photos/`) are tracked in a public GitHub repo:
https://github.com/jim-snyder-grant/acton-bounds — repo root is `Bounds/`
(the whole Insync-synced folder), but only code is tracked. `.gitignore`
is allowlist-style (deny everything by default, explicitly un-ignore only
specific files) because `Bounds/` has personal contact info (Contacts
sheet) and large reference material that must never be published.
Photo binaries, the raw XLSX/manifest working files that predate a
review pass, generated PDFs, `.venv/`, and IDE cruft are all excluded.
As of Jul 3 2026, the tracked `.md`/data files are `Acton Bounds TODO.md`,
`Project Notes.md`, `CHANGELOG.md`, `README.md`, and `Acton Bounds.xlsx`
— Jim reviewed each individually before it went public (the XLSX had its
Email/Phone columns removed first). `.gitignore`'s allowlist is the
authoritative current list; don't add anything new to it without Jim
explicitly saying so, even if it looks similar to something already
approved.

**`Acton Bounds TODO.md` needs to stay clean as it grows** — it's public
now, so before adding a new TODO item (or editing an existing one), check
it doesn't introduce a Drive/Sheet ID, a landowner's name/address/contact
info, or anything else that wouldn't belong in a public repo. The rest of
this "Source control" section (secret-scrubbing lessons, grep-before-adding
habit) applies here too. If in doubt, ask Jim rather than guessing.
claude.ai can read this file directly at
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

`code/acton_cover.py` needed the same treatment for Jim's local absolute
path (it was embedded in the path string, revealing his email). Since that
script is pasted/loaded into Inkscape's Simple Inkscape Scripting console
rather than run via `python3`, a repo-relative local file wasn't reliable
(Inkscape's working directory when executing pasted code isn't
predictable, so relative paths and `__file__` lookups can't be trusted).
Used `~/.acton_bounds_base_path` instead — a dotfile in the home
directory, outside the repo entirely, read via `os.path.expanduser` which
works regardless of CWD. Use this same home-dotfile approach for any
future Inkscape/GUI-console script that needs a local secret or path.

---

## Coordination with claude.ai — INBOX.md protocol

At the start of every Claude Code session, check the **`from-claude-ai/`
staging subfolder** of the Bounds Drive folder (`Bounds/from-claude-ai/`,
created Jul 12 2026) for any file named INBOX.md (or INBOX*.md). This
subfolder is where claude.ai now drops everything it hands off — both INBOX
messages and the report-section draft `.md` files they reference — so that
this churn stays out of the Bounds root. It is Drive-only (never tracked in
git; `.gitignore` denies it by default). Its Drive folder ID lives in the
local gitignored `Bounds/.from-claude-ai-folder-id` (not committed — Drive
IDs are secrets). Day-to-day you just read and delete the local Insync
mirror at `Bounds/from-claude-ai/`; you only need the ID for Drive-MCP
operations. (Historical note: before Jul 12 2026 claude.ai wrote INBOX and
draft files directly to the Bounds root — a few legacy drafts may still
linger there.)

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

**Replying to claude.ai (no formal reverse channel exists):** INBOX.md is
one-directional (claude.ai → Claude Code) because claude.ai can't edit or
delete files, only create them. Claude Code has no such restriction, so
the way to get something to claude.ai's attention is to write directly
into a shared doc it actually reads. Since `acton_bounds_context.md` was
retired (Jul 3 2026, its content folded into `README.md`), the reliable
channel is now `CHANGELOG.md` — `README.md`'s own "Orientation for a new
Claude instance" section explicitly lists it as the *first* file a new
Claude instance should read ("start here for a quick catch-up"), so a
dated note left at the top of `CHANGELOG.md` should reach claude.ai next
session. For something that needs to persist as ongoing guidance rather
than a one-off note, edit `README.md` directly instead.

**claude.ai's MCP access (as of Jul 5 2026):** claude.ai now has read
access to this repo via a GitHub MCP server (`github:get_file_contents`,
etc. — set up via Docker) and to the Bounds Drive folder via a filesystem
MCP server, in addition to its existing Drive MCP. This makes the
`raw.githubusercontent.com` fetch-URL workaround documented in README.md
mostly moot *for claude.ai specifically* (GitHub MCP reads files
directly, no URL tricks needed) — but README.md's guidance is kept as the
fallback for any Claude instance that only has a web_fetch-style tool and
no MCP access. claude.ai does **not** yet have write access to the repo
(see "Claude Code's perspective on claude.ai write access" below) or to
the GitHub repo's `INBOX.md`-adjacent files — INBOX.md via Drive remains
the only way it proposes changes.

**Claude Code's perspective on claude.ai write access (INBOX response,
Jul 5 2026):** claude.ai proposed getting direct write access (via its
new GitHub MCP tools) to documentation files only — `TODO.md`,
`Project Notes.md`, `CHANGELOG.md`, `README.md` — while Claude Code keeps
sole write access to all code files. Asked for Claude Code's view on
conflict risk and workflow disruption:

- *Security check risk:* the main value INBOX.md currently provides isn't
  just relaying content — it's that Claude Code greps every new/changed
  public file for secrets before it goes public (see "Security" section
  above; this exact class of mistake happened once, Jul 2 2026). If
  claude.ai commits directly, that check either becomes claude.ai's own
  responsibility (a habit it hasn't needed before) or falls to Jim
  reviewing every commit — which could be more friction than the INBOX
  round-trip it's meant to remove, not less.
- *Concurrent-writer risk:* today Claude Code is the sole writer, so there's
  no race condition. With claude.ai writing too, Claude Code would need to
  `git pull` immediately before editing any of the four shared docs, every
  time, to avoid clobbering a claude.ai commit — a new discipline that
  doesn't exist today. `TODO.md` and `Project Notes.md` are also hand-edited
  by Jim directly in Drive/locally, so it'd be three potential writers, not two.
- *Stale-assumption risk:* README.md's orientation section and this file's
  Security section both currently say the repo is "read-only for
  claude.ai" — that statement would need updating the moment write access
  actually changes, and it's easy to miss a reference somewhere else.
- **Recommendation:** don't give claude.ai direct-to-`main` write access.
  A lighter middle ground: claude.ai commits doc-only changes to a
  non-main branch via its GitHub MCP tools; Claude Code (or Jim) does a
  quick grep-for-secrets pass and fast-forwards/merges into `main`. That
  keeps the one security gate that matters without requiring Claude Code
  to manually re-type every diff the way INBOX.md does today. Answering
  the specific open questions: write to a branch, not `main`; INBOX.md
  doesn't become fully redundant for docs but could shrink from "apply
  this diff" to "review this diff already sitting on a branch"; and
  `git pull` before editing becomes mandatory for Claude Code only once
  this actually ships (not needed yet, since claude.ai has no write access today).

## Canonical report sources — the `report/` directory (added Jul 12 2026)

The report's editable section sources (the intro-section Markdown) now live
as **canonical, stable-named files in `Bounds/report/`**, which IS tracked in
git (allowlisted: only `report/*.md`; the rendered `report/*.pdf` outputs
stay ignored as build artifacts). This closes the reproducibility gap — a
fresh clone now has the code *and* the text inputs to rebuild the report
(`Acton Bounds.xlsx` + `code/report_sections.csv` + `report/*.md`), which
serves the "another town can reuse the process" goal the report itself
states.

Current canonical sources (H1 sets each section's footer name):
`Introduction.md`, `History.md`, `The Work Behind This Report.md`,
`Monument Listings — Introduction.md`, `Next Steps.md`. (The Cover, Overview
Map, and Monument Listings sections have no `.md` source — they come from
`FrontPage.pdf` and the two generating scripts.)

**Promotion workflow (Drive draft → tracked canonical):**
1. claude.ai writes a new/updated draft into `Bounds/from-claude-ai/` (see
   INBOX protocol above), named for its final section title (e.g.
   `Introduction.md`) — not `draft`/`v2` names anymore.
2. Claude Code **greps it for secrets/PII first** (emails, phone numbers,
   Drive/Sheet/DocuShare IDs, absolute home paths — same gate as any
   allowlist addition), then copies the content to `report/<Canonical>.md`.
3. Render with `intro2pdf.py ... --out ../report/<Canonical>.pdf` (run from
   `code/` so the `../Photos/...` image paths in a draft resolve), update
   `report_sections.csv` if the section name/file changed, re-run
   `assemble_report.py`, re-verify the overview-map links.
4. Delete the now-promoted staging copy from `from-claude-ai/` (and any
   Insync `(2)` duplicate) — "move" means *copy into `report/` + delete the
   staging original*, since git isn't literally moving the Drive file.
5. `git add`/commit/push the tracked `report/*.md` (+ csv/docs) changes.

**Naming convention for claude.ai handoffs** (relayed via CHANGELOG so
claude.ai picks it up): drop files in `from-claude-ai/`; name a report-section
draft with its **final section title** + `.md` (Claude Code promotes it to
`report/` under that same name); name instruction files `INBOX-<slug>.md`.
If a correction is needed before Claude Code processes it, just re-create the
same filename — Insync makes a `(2)` copy and Claude Code takes the newest by
`modifiedTime` (existing duplicate-reconciliation rule).

## CHANGELOG protocol

After any session in which you make substantive changes to shared files
(README.md, TODO.md, Project Notes.md, CLAUDE.md, or any other file a
future Claude instance would need to read), append a brief entry to
CHANGELOG.md in the Bounds folder.

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
│   ├── bounds2pdf.py          # Monument Listings section — produces monument_listings.pdf
│   ├── build_manifest.py      # builds/updates photo_manifest.csv
│   ├── photo_manifest.csv     # editable photo curation sheet (see below)
│   └── osm_screenshots/       # OSM map tiles, one per monument row index
│       └── osm_screenshot_*.jpg
```

---

## Running the Scripts

**Run everything from the project root (the `Bounds/` folder)** — the same
directory git operates in. As of Jul 12 2026 every script anchors its data
paths to its own file location (`HERE = code/`, `ROOT = Bounds/`), so it works
from any working directory; and a root-level `.python-version` (= `bounds`)
makes pyenv activate the report environment at the root too (`Photos/` keeps
its own `photos` env). There is no longer any need to `cd code/` first.

```bash
# from the Bounds project root:
pip install -r code/requirements.txt
playwright install chromium   # one-time: downloads the browser binary
                               # pip alone doesn't install this
python3 code/build_manifest.py     # step 1: build/update photo manifest
python3 code/bounds2pdf.py         # step 2: generate code/monument_listings.pdf
python3 code/intro2pdf.py report/<Section>.md --out report/<Section>.pdf  # step 2b: render intro sections
python3 code/assemble_report.py    # step 3: merge all sections -> ../Acton Bounds Report 2025-2026.pdf
python3 code/verify_report.py      # step 4: check every overview-map link resolves (PASS/FAIL, exit 0/1)
```

Where outputs land: `bounds2pdf.py` and `overview_map.py` write their section
PDFs into `code/` (`monument_listings.pdf`, `overview_map.pdf`); `intro2pdf.py`
writes into `report/`; `assemble_report.py` writes the merged report to the
Bounds root. All are gitignored except the `report/*.md` sources.

Dependencies: `pandas`, `openpyxl` (pandas' `.xlsx` engine, not imported
directly but required), `Pillow`, `reportlab`, `playwright`, `pypdf`,
`geopandas`, `matplotlib` — see `requirements.txt`. Two separate pyenv
environments, on purpose: **`bounds`** (report generation — activated at both
the project root and `code/` via `.python-version`) and **`photos`** (the
`Photos/` Google-Takeout/Sheets-API pipeline, `gspread` +
`google-auth-oauthlib`, its own `Photos/.python-version`). They're kept apart
because only the photo pipeline talks to Google APIs.

### Standalone utility scripts (not part of the report pipeline)

- **`extract_town_corners.py`** (added Jul 6 2026) — pulls Acton entries
  out of a MassDOT `Town_Corners.kml` export into a CSV for hand-import
  into the Sheet. `python3 extract_town_corners.py [kml_path] [out_csv]`
  (defaults `Town_Corners.kml` / `acton_town_corners.csv`, both
  gitignored working files, not tracked). Used once already to replace
  11 NAD83-sourced coordinates with real WGS84 values (Jul 6 2026, see
  CHANGELOG); worth re-running if a fresher KML export ever comes in.
- **`check_distance_to_line.py`** (added Jul 7 2026) — QA check: for
  each Street-Crossing monument, measures the perpendicular distance
  from its recorded coordinates to the straight line connecting its two
  nearest official Corner monuments (Massachusetts town boundaries are
  straight survey lines between corners, so a large offset usually
  means a bad recorded coordinate, not an actually-crooked boundary).
  Substitutes the true Acton/Carlisle/Concord corner location (parsed
  from that row's "Notes on Monument" text) as the line anchor there,
  instead of the witness-monument coordinates stored in
  Latitude/Longitude for that row. `python3 check_distance_to_line.py`,
  prints every monument sorted worst-first. First run (Jul 7 2026) found
  one clear data-entry bug (Acton/Maynard Conant Street's latitude was
  off by a whole degree, ~110km) and 2 real unexplained offsets worth a
  field re-check (Acton/Concord Great Road ~52m, Acton/Littleton Nagog
  Hill Road ~16m) — see "Monument distance-to-line check.md" in Drive
  for the full first-run results.
- **`generate_geocoding_csv.py`** (added Jul 9 2026) — exports monument
  coordinates as a `lon,lat` CSV (`../monument_coordinates_for_geoapify.csv`,
  gitignored working file, not tracked) for Geoapify's drag-and-drop
  reverse-geocoding tool. `python3 generate_geocoding_csv.py`. Sorted by
  `Order`, full (untruncated) precision, skips the 2 rows with no
  coordinates. No name/ID column, per Jim's spec for the drag-and-drop
  format — match Geoapify's output back to monuments by row position.
  Re-run any time after coordinates change to get a fresh export.
- **`overview_map.py`** (added Jul 9 2026) — generates the report's
  Overview Map (intro section 5): a single legal-portrait (8.5×14in)
  page with Acton's boundary as a thick gold line through the corner
  monuments in `Order` sequence, every monument as a hollow type-coded
  icon (Corner=circle, Street Crossing=square, Witness=triangle), and a
  numbered, status-colored callout box per monument arranged
  counter-clockwise around the page perimeter (Order 1 = ACMS = lower
  right). Rotation (~27.97°) is derived programmatically from the
  ACMS→AMS coordinates, not hardcoded. The base map inside the boundary
  is real MassGIS data cached under `gis_data/` (gitignored): MassDOT
  RoadInventory roads (fetched by bbox from the ArcGIS REST service,
  cached to `roads_acton.geojson`) and MassDEP Hydrography 1:25,000 open
  water (`hydro25k.zip`, `POLY_CODE in {1,6}` = reservoir/lake/pond).
  Callout leaders leave each box from its interior-facing edge (inner
  corner for the 4 corner boxes) and bow away from the town center.
  Imports `STATUS_COLORS`/`knockout_text_color` from `status_colors.py`
  so box colors match the monument pages. Outputs `overview_map.pdf`
  (vector, the deliverable) and `overview_map.png` (raster preview),
  both gitignored. `python3 overview_map.py [--refresh-roads]`. Needs
  `geopandas`+`matplotlib` (in `requirements.txt`). A right-justified
  footer ("Overview Map, page 1 of 1") is drawn to match the other
  sections. Also writes `overview_map_links.json` (gitignored sidecar):
  each callout box's rectangle in PDF points, which `assemble_report.py`
  uses to make the boxes clickable links to each monument's page in the
  merged report.
- **`intro2pdf.py`** (added Jul 9 2026) — renders an intro-section
  Markdown file to a styled PDF matching the monument-listing pages:
  US Letter, 1in margins, Helvetica body, and the same right-justified
  per-section footer ("<Section Name>, page X of N", 9pt `#555555` via
  the shared two-pass canvas technique). Supported Markdown: `#` H1
  (centered title + rule; also becomes the footer's section name unless
  `--section` is given), `##` H2, left-aligned paragraphs, `-`/`*` bullets,
  `>` block quotes (gold left rule, multi-paragraph aware), `---` rules,
  and inline `**bold**`/`*italic*`. `python3 intro2pdf.py <file.md>
  [more.md ...] [--section NAME] [--out OUT.pdf]`; output defaults to the
  input path with a `.pdf` extension. Used for the drafted intro
  sections in Drive (Legal Background, Monument Listings intro, etc.) —
  those are Drive-only working files, not tracked. Draft-note headers and
  bracketed `[editor: ...]` asides render literally, so strip them from
  the Markdown before a final run.
- **`assemble_report.py`** (added Jul 9 2026) — the final-assembly step:
  concatenates the section PDFs in the order given by `report_sections.csv`
  and stamps the LEFT-justified whole-report footer ("Acton Bounds Report
  2025-2026, page X of N") on every page once the true merged total N is
  known (the second half of the two-part footer — each section already
  carries its own right-justified footer). `report_sections.csv` columns:
  `order,section,file,footer`; `file` resolves relative to the Bounds
  folder; `footer=no` suppresses the whole-report footer on that section
  (e.g. the cover) while still consuming a page number. Missing section
  files are skipped with a warning, so a partial draft assembles fine.
  Handles mixed page sizes (letter sections + the legal-size overview
  map) — the footer lands at the same 1in-from-left, 26pt-up spot on
  every page. Needs `pypdf` (in `requirements.txt`). `python3
  assemble_report.py [--manifest CSV] [--out PATH]`; output defaults to
  the canonical `../Acton Bounds Report 2025-2026.pdf`. As of Jul 9 2026
  `bounds2pdf.py` emits its Monument Listings *section* to
  `code/monument_listings.pdf` (gitignored, alongside `overview_map.pdf`)
  rather than the whole-report name, precisely so the assembled output can
  own `../Acton Bounds Report 2025-2026.pdf`. `report_sections.csv` is
  **tracked** as of Jul 12 2026 (allowlisted — it's build config, like a
  Makefile, and was scanned clean of IDs/PII first). Its `.md`-derived
  section rows now point at `report/*.pdf` (see the "Canonical report
  sources" section); the Cover stays `FrontPage.pdf` and the Overview Map /
  Monument Listings rows stay `code/*.pdf`.
  **Clickable overview-map boxes:** if both the Overview Map and Monument
  Listings sections are present, it reads `overview_map_links.json` and
  overlays an internal "go to that monument's page" link annotation over
  each callout box on the map page (target = `listings_start + Order - 1`,
  since `bounds2pdf.py` emits one page per monument in `Order` order). The
  `/Dest` references the real page object (not a bare page number, which
  some viewers ignore) with an invisible border. It skips linking (rather
  than risk wrong targets) if the sidecar is missing or the listings page
  count doesn't match the box count 1:1 — so if a monument page ever spills
  to two pages, the links are dropped with a warning instead of pointing at
  the wrong pages.
- **`verify_report.py`** (added Jul 12 2026) — post-assembly QA check: opens
  the assembled report and confirms every clickable overview-map callout box
  links to the correct monument page. It's the standalone version of the
  inline link check that used to be pasted as a `python3 - <<heredoc` after
  each run (now that ad-hoc Python prompts under the curated allowlist, this
  committed script is allowlisted instead). Everything is derived from the PDF
  + `overview_map_links.json` (nothing hardcoded, so it stays correct as page
  counts shift): finds the one page carrying internal GoTo links, matches each
  link's rectangle back to its sidecar box to recover its `Order`, and checks
  that all Orders 1..N are covered once and map slope-1 onto consecutive pages
  (`Order k -> listings_start + k - 1`) — catching a scrambled or off-by-one
  set, not just a non-contiguous one. Prints PASS/FAIL and exits 0/1, so it
  doubles as a pre-commit gate. `python3 code/verify_report.py [--report PATH]`
  (defaults to the canonical report at the Bounds root). Needs `pypdf`.

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
| `From 1904 description` | Optional — historical description. Column name unchanged, but the printed label is "In 1904 description:" (Jul 7 2026, Jim's fix) so that the 8 monuments whose cell is just "no" (not mentioned in the 1904 book) read as a sensible answer instead of an odd non-answer |
| `Notes on Monument` | Optional |
| `Possible Next Steps` | Optional (added Jul 7 2026 via claude.ai/INBOX.md). Printed as **Possible Next Steps:** right after Notes on Monument, before the map/photos. Originally proposed for Not Found/Documented/Couldn't Paint pages (which otherwise have significant white space), but Jim's actual usage is broader -- also used for damaged-but-Painted monuments (e.g. leaning or buried, needing repair). General purpose: actionable guidance for future Select Board members or town staff on any monument needing follow-up (which state agency to ask, cost-sharing under MGL Ch. 42, funding sources, etc.) |
| `Coordinate Source` | Text description of source |
| `Latitude` / `Longitude` | Decimal degrees WGS84; may be NaN if unknown. Stored precision varies by monument (not normalized) -- `bounds2pdf.py` formats to 5 decimal places (~1m) for display only, decided Jul 5 2026 |
| `OpenStreetMap link` | URL for map screenshot; may be NaN |
| `Tie-break number` | Used when multiple monuments share a name prefix |
| `Date of visit` | May be a float (Excel serial date) or string |
| `Order` | Integer 1–51, drives page order (see below) |

There are also town columns (`Boxborough`, `Littleton`, etc.) marked with `X`
for each town that shares that monument.

**Page order (added Jul 5 2026):** monument pages appear in the order given
by the `Order` column, not whatever order the sheet rows happen to be
in — `bounds2pdf.py` sorts by it explicitly (see "bounds2pdf.py — Current
State" below). This was added specifically so the intended order survives
future accidental re-sorting/row-insertion in the Google Sheet; before
this column existed, the report's order was just implicit spreadsheet row
order. `Order` walks clockwise around Acton's boundary starting at the
Acton/Concord/Maynard/Sudbury corner (a well-known landmark near the
Acton Senior Center), which also happens to put the existing `Tie-break
number` values (e.g. the two Carlisle and two Littleton monuments) in
ascending order — confirmed against the live data. A few monuments known
only from the 1904 report's unrecognized street names are placed at
Jim's best-guess position in the sequence.

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
| `section` | See "Section column conventions" below |
| `orientation` | `landscape`/`portrait`/`square`, computed by `add_cover_columns.py` for included photos — used by the cover-collage script |
| `cover_candidate` | `yes`/blank — defaults `yes` for included photos; lets Jim exclude a photo from the cover collage without touching `include` |
| `docushare_url` | Populated by `merge_docushare.py`; blank until that photo is uploaded and scraped |

### Section column conventions (added Jul 5 2026)

Jim started marking some photos for use in introductory sections rather
than per-monument pages. Valid `section` values:

- `monument` — appears on the per-monument page (existing default)
- `appendix` — appears in an appendix (existing)
- `intro` — belongs in an intro section, specific placement TBD (valid,
  not an error — just means undecided)
- `intro-visits` — Summary of visits and results section
- `intro-legal` — Legal background section
- `intro-history` — History of Acton's bounds section
- `intro-map` — Overview map section
- `intro-other-towns` — Other towns' reports section
- `intro-policy` — Policy recommendations section
- `intro-cover` — Cover page (handled separately by `acton_cover.py`)

`include = yes` for ALL photos that should appear anywhere in the report,
including intro sections. `include = no` is reserved for photos excluded
from the report entirely (blurry, wrong location, genuine duplicates,
etc.) — it does not mean "not decided which section yet" (that's what
bare `intro` is for). One placement per photo is assumed for now; if a
photo ever needs to appear in both a monument page and an intro section,
a second section column would need to be added.

`build_manifest.py` recognizes all of the above as valid (no warning) and
reports a count of photos by section value in its summary output.
`bounds2pdf.py` only pulls rows with `section == 'monument'` for the
per-monument pages (see `bounds2pdf.py`'s photo-loading loop) — intro
photos are already excluded there today; incorporating them into actual
intro pages is future work once those pages are built.

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
- One-line headline: order number, monument name, and status, each
  number/status in a colored box keyed to the status (see "Current
  state" below) — centered, with a rule underneath
- Coordinates (table with lat/long + source), or "Unknown Coordinates"
- Nearest Acton street name
- Nearest other town street name (if present)
- Nearby landmark (if present)
- Notes on location (if present)
- 1904 description (if present)
- Notes on Monument (if present)
- Possible Next Steps (if present) — added Jul 7 2026, see the
  `Possible Next Steps` row in the Data Source table above
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
- Page order: sorted explicitly by the `Order` column right after loading
  the Monuments sheet (`df.sort_values('Order').reset_index(drop=True)`).
  Hard error if any `Order` value is blank; a warning (not fatal) if the
  values aren't a clean 1..N sequence; a note if the sheet's raw row order
  didn't already match `Order` (harmless — it gets sorted either way, this
  is just a heads-up that a manual re-sort in the Sheet would otherwise
  have gone unnoticed)
- One-line headline (added Jul 6 2026, superseding the Jul 5 2026
  two-line version): `[order#] Name [status]`, no "Monument Listing"
  text and no Corner/Street Crossing type — order number and status are
  each in a small colored box (`<span backColor="..." textColor="...">`)
  using that row's `STATUS_COLORS` entry; text color is picked
  automatically per box via `knockout_text_color()` (relative-luminance
  threshold, white on dark backgrounds / black on light ones), not
  hand-picked per status. `TITLE_S` dropped from 16pt to 14pt so the
  longest name ("Acton/Littleton W B Marker on Fort Pond Road", 44 chars)
  still fits on one line at `TEXT_W` (worst case ~408pt of 456pt
  available at 14pt; two rows would have overflowed at 16pt). The `Type`
  column (Corner/Street Crossing) is no longer displayed anywhere on the
  page. Order-number boxes are meant to be reused later as clickable
  markers on an overview map (Jim's stated plan) — that will need each
  monument page to have a named PDF destination/bookmark, which doesn't
  exist yet; not needed for this change, just a known follow-on
  dependency.

  **`STATUS_COLORS`/`knockout_text_color()` moved to their own module,
  `code/status_colors.py`** (added Jul 6 2026), so a future map-generation
  script can import the exact same status colors instead of duplicating
  or drifting from them. `bounds2pdf.py` just imports from it now.

  `STATUS_COLORS` (hex backgrounds): Painted `#2E7D32` green, Found
  `#1565C0` blue, Couldn't paint `#EF6C00` orange, Not Found `#C62828`
  red, Documented `#BDBDBD` light gray (the only one that resolves to
  black text — deliberately the calmest color since it means no field
  visit happened, not a field outcome).

**Bug found and fixed Jul 5 2026 — `flowable_h()` underestimated text
height, could spill photos to an unnecessary second page:** ReportLab's
`SimpleDocTemplate` adds its own 6pt padding on every side of the page
frame by default (a `Frame` class default, not something this code sets)
on top of the `MARGIN`-based page margins already accounted for in
`AVAIL_W`. `flowable_h()` (used to measure how much vertical space the
header/detail text takes, which then determines `remaining_h` for
photos) was wrapping text at the full `AVAIL_W` (468pt) instead of the
narrower width ReportLab actually renders into (456pt) — invisible for
most text, but for a couple of long monument names the title paragraph
wraps to 2 lines at 456pt while `flowable_h()` measured it as 1 line at
468pt, understating `text_h` by ~20pt. That let `choose_cols()` allocate
more room to photos than the page actually had once the real (taller,
wrapped) title was drawn, pushing photos onto a spillover second page
that wasn't really necessary. Fixed by adding a `TEXT_W = AVAIL_W - 12`
constant (`FRAME_PAD = 6` per side) and measuring `flowable_h()` against
it instead of `AVAIL_W`. Confirmed fix: "Acton/Concord Powder Mill Road
(Rte 62)" and "Acton/Maynard Powder Mill Road (Rte 62)" (both 3-line
headlines) now keep their photos on one page; total page count back to
51 (was 53 with the two spillover pages). "Acton/Littleton W B Marker on
Fort Pond Road" also has a 3-line headline but was never affected (its
photos already fit in one page's remaining space either way).

### Page numbering — two-part footer (decided Jul 7 2026)

Each page carries two independent footer counters, resolving the
"nobody knows the final total page count while still drafting" problem
without any manual offset bookkeeping:

- **Right-justified, per-section, self-contained:** e.g. "Monument
  Listings, page 12 of 51". Whatever tool renders a given section (this
  script for Monument Listings, claude.ai's tooling for the intro
  sections) draws only this half, counting just its own pages. It never
  needs to know anything about any other section, at draft time or
  final assembly.
- **Left-justified, whole-report, stamped at final assembly:** e.g.
  "Acton Bounds Report 2025-2026, page 23 of 73". Added in one pass
  *after* every section is merged into the final PDF, by a small
  Claude Code script (see "Final assembly" in `Acton Bounds TODO.md`)
  that overlays this text on every page once — computed trivially at
  that point since the true total is finally known.

This replaces the earlier `MONUMENT_LISTINGS_INTRO_PAGES` offset-constant
design (used briefly Jul 4-7 2026): that approach required manually
recomputing and setting a constant in `bounds2pdf.py` before every
final-ish run, and only solved the problem for the Monument Listings
section specifically. The two-part split needs no manual step and
generalizes to every section the same way.

`bounds2pdf.py`'s `NumberedCanvas._draw_footer()` implements only the
right-justified half (see code); the left half is stamped at final
assembly by `assemble_report.py` (added Jul 9 2026 — see its entry under
"Standalone utility scripts"), which overlays "Acton Bounds Report
2025-2026, page X of N" on every merged page once the true total is known.
`intro2pdf.py` draws the right-justified half for the Markdown intro
sections in the same style.

#### Footer visual spec (for claude.ai to match in the intro sections)

Style used by `NumberedCanvas._draw_footer()` in `bounds2pdf.py`, for
visual consistency across every section:

- **Page size:** US Letter, 8.5×11in (`reportlab.lib.pagesizes.letter`)
- **Font:** Helvetica, 9pt, regular weight (not bold)
- **Color:** `#555555` (medium gray, not black)
- **Vertical position:** 26pt (0.36in) up from the bottom edge of the
  page — i.e. `0.5 * 72 - 10` in point units
- **Horizontal position:** both halves align to the same 72pt (1in)
  margins the body text uses, not the physical page edge — right half
  ends at `PAGE_W - MARGIN` (`drawRightString`), left half (added at
  final assembly) starts at `MARGIN` (`drawString`)
- **Right-half text:** `"{Section Name}, page {X} of {M}"` — Monument
  Listings pages use "Monument Listings"; other sections should use
  their own section name in the same pattern (e.g. "Legal Background,
  page 2 of 3")
- **Left-half text (final assembly only):** `"Acton Bounds Report
  2025-2026, page {X} of {N}"`
- No footer rule/line above the text, no other footer content

### Remaining work

#### OSM screenshot caching — COMPLETE

`osm_url_cache.json` (in `code/osm_screenshots/`) tracks the OSM link used
for each row; a screenshot is only re-captured if the cached file is
missing or the link changed. `--force-screenshots` bypasses the cache.
The browser isn't even launched when everything's cached, so a typical
run now takes seconds instead of ~4 minutes for all 51 monuments.

#### DocuShare photo linking and clickable images — COMPLETE

Full-resolution originals are hosted in DocuShare (Acton's permanent
archive, same place the finished report lives). This section is the full
spec (the standalone "CLAUDE.md note - DocuShare photo linking.md" file
that originally proposed this was deleted Jul 2 2026 once everything in it
was implemented and documented here).

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
5. Run `python3 code/build_manifest.py` (from the project root) — new photos
   are added to the manifest; existing edits are preserved
6. Edit `photo_manifest.csv` to set captions, exclude unwanted photos, etc.
7. Upload batch to DocuShare (manual), then run scrape + merge scripts to
   populate `docushare_url` column (see above)
8. Run `python3 code/bounds2pdf.py` to regenerate the report

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
are managed in a claude.ai conversation (not here). See the "Coordination
with claude.ai — INBOX.md protocol" and "Replying to claude.ai" sections
near the top of this file for how the two Claude instances actually
exchange information — this file (`code/claude.md`) is maintained by
Claude Code only; claude.ai has no write access to it or anything else in
this repo.
