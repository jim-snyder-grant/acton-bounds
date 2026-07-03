# acton-bounds

Code and documentation for the 2025–2026 perambulation of Acton,
Massachusetts town boundary monuments.

Massachusetts General Laws Chapter 42 §2 requires towns to locate,
inspect, and renew the markings on their boundary monuments at least
once every five years. This project documents Acton's perambulation —
the first in many years — of all 59 monuments marking the boundaries
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
- `Photos/Monument Photos/` — 173 monument photos
- `photo_manifest.csv` — photo curation sheet (may contain personal info)
- `FrontPage.svg` / `FrontPage.pdf` — finished cover page
- `INBOX.md` — pending tasks from claude.ai for Claude Code to apply
- `acton_bounds_context.md` — claude.ai's own project context/orientation
  doc; stays Drive-only since claude.ai has no write access to this repo

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

## Orientation for a new Claude instance

If you are a Claude instance starting a new session on this project,
read these files in order:

1. `CHANGELOG.md` — what changed recently (start here for a quick catch-up)
2. `Acton Bounds TODO.md` — current task list
3. `code/claude.md` — technical spec and code status (Claude Code)
4. `Project Notes.md` — findings, decisions, and comparative analysis
5. `Photos/CLAUDE.md` — photo pipeline details (if relevant)

All repo files can be fetched directly (plain file content, not a
rendered page — works reliably with a `web_fetch`-style tool) via:
`https://raw.githubusercontent.com/jim-snyder-grant/acton-bounds/main/{path}`

The Google Drive Bounds folder contains additional files not in the
repo (photos, INBOX.md files, `acton_bounds_context.md`). Ask Jim for
the folder ID or access if needed.

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
- Cover page: built with SimpInkScr (Inkscape Python scripting extension)
- Coordinate precision: 5 or 6 decimal places (decision pending)
- Neighboring towns' perambulation reports: Boxborough (2007), Concord
  (2017), Stow (2007), and Sudbury confirmed — all cross-referenced.
  Carlisle, Littleton, Westford, Maynard reports not yet obtained.
