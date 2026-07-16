# acton-bounds

Code and documentation for the 2025–2026 perambulation of Acton,
Massachusetts town boundary monuments.

Massachusetts General Laws Chapter 42 §2 requires towns to locate,
inspect, and renew the markings on their boundary monuments at least
once every five years. This project documents Acton's perambulation —
the first in many years — of all 51 monuments marking the boundaries
between Acton and its six neighboring towns: Boxborough, Carlisle,
Concord, Littleton, Maynard, and Stow (and Sudbury at a four-town
corner). The work was authorized by a Select Board vote directing two
Select Board members, Jim Snyder-Grant and Dean Charter, to conduct
the perambulation.

The repo supports generation of a formal PDF report with two parts:
per-monument pages (generated from a spreadsheet and photos), and
introductory sections (legal background, history, overview map,
summary of visits, comparative analysis of neighboring towns' reports,
and policy recommendations).

In the future, this code and approach might help other Massachusetts
towns with similar work.

## Repo structure

```
code/
  bounds2pdf.py        # Main report generator (ReportLab + Playwright)
  build_manifest.py    # Builds photo_manifest.csv from Monument Photos/
  scrape_docushare.py  # Scrapes Document IDs from DocuShare collection page
  merge_docushare.py   # Merges DocuShare URLs into photo_manifest.csv
  acton_cover.py       # SimpInkScr script for the cover page (Inkscape)
  add_cover_columns.py # Adds orientation/cover_candidate columns to the manifest
  requirements.txt     # pip install -r requirements.txt to get started
  claude.md            # Guidance for Claude Code — read this first
Photos/
  CLAUDE.md            # Guidance for Claude Code on the photos pipeline
Acton Bounds.xlsx      # Monument data (exported from Google Sheet)
Acton Bounds TODO.md   # Task list (shared between Claude instances and Jim)
Project Notes.md       # Findings, decisions, comparative analysis results
CHANGELOG.md           # Running log of changes to shared files
README.md              # This file
```

Not in the repo (in Google Drive only):
- `Photos/Monument Photos/` — 173 monument photos (the photo *files*; note
  `code/photo_manifest.csv`, which indexes them, IS tracked — see below)
- `FrontPage.svg` / `FrontPage.pdf` — finished cover page
- `from-claude-ai/` — staging folder where claude.ai drops handoffs:
  `INBOX*.md` instruction files and report-section drafts, which Claude Code
  applies and then deletes (see `code/claude.md`'s INBOX protocol)

Tracked, but worth knowing why:
- `code/photo_manifest.csv` — the photo curation sheet. Tracked as of Jul 15
  2026: its `caption` / `include` / `exclude_reason` / `section` /
  `cover_candidate` columns are hand-authored editorial judgment that
  `build_manifest.py` can't regenerate. It's scanned for PII before each
  commit like any public file; `exclude_reason` is published deliberately so
  a future Acton group can revisit a photo decision.

## AI collaboration model

This project is built collaboratively by Jim Snyder-Grant (the project
owner), Claude Code (handles all Python/code work in `code/`), and
claude.ai (handles document planning, intro sections, comparative
analysis, and design work).

The two Claude instances communicate via shared files in this repo and
via an INBOX.md protocol: claude.ai writes proposed changes to
`INBOX.md` in the Google Drive Bounds folder; Claude Code reads and
applies them at the start of each session, then deletes the file.
Jim relays tasks between them and reviews changes.

**claude.ai does not write directly to this repo** — even though it has
GitHub MCP tools available (as of Jul 2026), all changes to repo-tracked
files go through Claude Code via the INBOX.md protocol. This ensures Jim,
claude.ai, and Claude Code all see and understand what goes into the
public repo before it's committed.

## Orientation for a new Claude instance

If you are a Claude instance starting a new session on this project,
read these files in order:

1. `CHANGELOG.md` — what changed recently (start here for a quick catch-up)
2. `Acton Bounds TODO.md` — current task list
3. `code/claude.md` — technical spec and code status (Claude Code)
4. `Project Notes.md` — findings, decisions, and comparative analysis
5. `Photos/CLAUDE.md` — photo pipeline details (if relevant)

### Editorial conventions and settled facts

For whoever is next writing or reviewing report prose. Folded in from a
claude.ai handoff note (2026-07-16) after a full read-through of the five
`report/*.md` sections and the Monuments sheet's text columns.

**Voice: third person, always.** The narrative sections (Introduction,
History, The Work Behind This Report, Monument Listings — Introduction,
Next Steps) are third person throughout — "Jim and Dean," never "I." This
is also the standard for the Monuments-sheet text columns that render onto
each monument's page: three rows there had slipped into first person or
named Jim directly, and Jim approved neutral rewrites for all three. Hold
new text in either place to the same standard by default.

**Settled — verified against `Acton Bounds.xlsx` on 2026-07-16, no need to
re-derive:**

- **Monument counts: 11 Corner + 38 Street Crossing + 2 Witness = 51.**
  Note `Type` has *three* values, not two — a witness marker is its own
  type, and the report's 51-monument sentence names all three.
- **Example monument names are real** and safe to keep using:
  `Acton/Carlisle/Westford` (a Corner) and `Acton/Concord Powder Mill Road
  (Rte 62)` (a Street Crossing).
- **"Riviage" is deliberate — don't "correct" it to "Rivage."** It's the
  development near the missing Acton/Maynard Powder Mill Road crossing. Be
  aware the basis is thinner than it may look: it occurs exactly *once* in
  the whole sheet (Order 50, Possible Next Steps), so the sheet doesn't
  corroborate its own spelling. It's unflagged by Jim rather than
  cross-checked. If it ever matters editorially, confirm against the
  development's own signage rather than the sheet.
- **Monument numbering and the overview map's callout boxes both run
  counter-clockwise.** The report text said "clockwise" until 2026-07-16.
  See `code/claude.md`'s page-order section for the geometric test that
  settles it — and for why the tie-break-number argument doesn't.
- **`report/Introduction.md` is what `Acton Bounds TODO.md` calls "Legal
  background"** in its section-4 scope notes. The section was retitled and
  the TODO wasn't updated. A naming mismatch, not a missing section.

**Known and deliberately not fixed:** terminal punctuation (trailing
periods, or their absence) is inconsistent across the Monuments sheet's
Notes on location / Notes on Monument / Possible Next Steps cells — some
are full sentences, many are fragments. Cosmetic, but it touches all 51
rows, so it's out of scope for a targeted edit pass. Worth doing only if a
full copyedit of the sheet is ever on the table.

### How to access project files

**Check what MCP tools are available first** — this determines your best
approach.

**If you have GitHub MCP tools** (`github:get_file_contents` etc.) — use
them directly. This is the most reliable method and needs no URL tricks.
Read these files to orient yourself:
1. `CHANGELOG.md` — what changed recently (start here)
2. `Acton Bounds TODO.md` — current task list
3. `code/claude.md` — technical spec and code status
4. `Project Notes.md` — findings, decisions, comparative analysis

Example:
  `github:get_file_contents(owner="jim-snyder-grant", repo="acton-bounds", path="CHANGELOG.md")`

Even with GitHub MCP access, do NOT write directly to the repo — propose
changes via INBOX.md and let Claude Code commit them (see AI collaboration
model above).

**If you have filesystem MCP tools** — the Bounds Drive folder is synced
locally and can be read directly. This avoids any caching issues with
web fetches. Ask Jim for the allowed root path — it's not written here
because Insync names the local sync folder after his Google account
email, which must not appear in this public repo (see "Security notes"
below).

Example:
  `filesystem:read_text_file(path="<allowed root>/Acton Bounds TODO.md")`

**If you only have web_fetch** — use the raw URL pattern (not blob URLs,
which cache stale content):
  `https://raw.githubusercontent.com/jim-snyder-grant/acton-bounds/main/{path}`

As of July 2026, web_fetch requires URLs to appear in a prior search
result. Workaround: search for `jim-snyder-grant acton-bounds` first,
then fetch raw URLs. Skip if your version doesn't have this restriction.

## Security notes for Claude instances

Do not put any of the following in any file that is or may become part
of this public repo:

- Google Drive folder IDs or file IDs
- Google Sheet IDs
- Email addresses or phone numbers
- Personal information about landowners, witnesses, or other individuals
- API keys, tokens, or credentials of any kind
- DocuShare collection or document IDs

These belong in gitignored local files (like `~/.acton_bounds_base_path`)
or in Google Drive only. When in doubt, ask Jim before committing.

## Key decisions

- PDF library: ReportLab + Platypus (switched from borb)
- OSM maps: captured via Playwright, cached in `osm_screenshots/`
- Full-resolution photos: hosted in Acton's DocuShare archive, linked
  from PDF captions (not embedded at full res)
- No DocuShare API integration for bulk document workflows — the REST
  API is confirmed non-functional for Jim's account, so archiving is a
  manual process (organize in Google Drive, move into DocuShare later)
  except for the individual photo uploads above
- Cover page: built with SimpInkScr (Inkscape Python scripting extension)
- Coordinate precision: report displays 5 decimal places (~1m); the XLSX
  keeps whatever precision each coordinate already has, untouched
- Neighboring towns' perambulation reports: Boxborough (2007), Concord
  (2017), Stow (2007), and Sudbury (2020) confirmed — all cross-referenced.
  Carlisle, Littleton, Westford, Maynard reports not yet obtained.
