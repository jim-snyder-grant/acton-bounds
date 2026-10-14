# Building the Acton Bounds report from scratch

This guide reproduces the finished report —
`Acton Bounds Report 2025-2026.pdf` — starting from only two things:

1. **This git repository** (code, report text, the spreadsheet, the cover, specs)
2. **Acton's DocuShare** "Perambulation" archive (the photo files and the GIS
   base-map cache — the large, non-code inputs that are deliberately *not* in git)

Following it end to end is also the **completeness test for the archive**: if any
step can't be satisfied from the repo + DocuShare alone, something is missing and
needs to be added to one of them. Keep a copy of this file **both in git and in
DocuShare**, so whoever rebuilds has it from whichever side they start on.

---

## What comes from where

| Piece | Source | Notes |
|---|---|---|
| Code, Makefile, report `*.md`, `Acton Bounds.xlsx`, cover (`FrontPage.pdf/.svg`, `acton_seal.png`), specs, `photo_manifest.csv` | **git** | everything needed except the two big inputs below |
| Monument photos | **DocuShare** → "Perambulation Images" (Collection-20474) | ~190 `.jpg` files |
| GIS base-map cache | **DocuShare** → "gis_data" (Collection-20546) | `hydro25k.zip` + `roads_acton.geojson` |
| Overview map PDF (`code/overview_map.pdf`) | **regenerated** by `make overview-map` | needs the gis_data cache |
| OSM per-monument map images (`code/osm_screenshots/`) | **regenerated** at build time | Playwright captures them from OpenStreetMap (needs a browser + network) |

All collections sit under **Perambulation (Collection-19415)** on
`https://doc.actonma.gov`.

---

## Prerequisites

- `git`
- Python 3.11+ (this project used pyenv env **`bounds`**; `.python-version`
  selects it automatically if you use pyenv)
- Network access for the first build (OpenStreetMap map captures)
- Read access to the DocuShare Perambulation collections above

---

## Steps

### 1. Clone the repo

```
git clone https://github.com/jim-snyder-grant/acton-bounds.git
cd acton-bounds
```

### 2. Set up the Python environment

```
python3 -m venv .venv && source .venv/bin/activate      # or: pyenv activate bounds
pip install -r code/requirements.txt
python3 -m playwright install chromium                  # browser for OSM captures
```

(`geopandas`/`matplotlib` in requirements.txt are only needed for the overview
map in step 4; everything else is for the report itself.)

### 3. Restore the two inputs that aren't in git

**a. Photos** — download the monument photos from DocuShare *Perambulation
Images* (Collection-20474) into:

```
Photos/Monument Photos/
```

They are named to the project convention (see the **Photos** section of
`README.md`). Verify the folder before building:

```
python3 code/check_photo_names.py
```

Expect `All good -- every filename parses and matches a monument.`

**b. GIS base-map cache** — download the two files from DocuShare *gis_data*
(Collection-20546) into `code/gis_data/`:

```
code/gis_data/hydro25k.zip
code/gis_data/roads_acton.geojson
```

`overview_map.py` looks for exactly those names.

### 4. Build the overview map

`code/overview_map.pdf` is a build artifact, not in git. Regenerate it from the
cache you just restored (runs offline; no API key):

```
make overview-map
```

### 5. Build the report

```
make all
```

This renders the intro sections, builds the monument listings, assembles the
full PDF, and verifies it. **The first run also captures ~50 OpenStreetMap map
images** via Playwright — this needs network access and takes a few minutes;
they're cached in `code/osm_screenshots/` and reused on later builds.

### 6. Result

- Output: **`Acton Bounds Report 2025-2026.pdf`** in the repo root.
- Expect **66 pages** and verify's `RESULT: PASS -- all 51 overview-map links
  resolve`.
- For a date-stamped reviewer copy instead, run `make draft` (writes into
  `drafts/`).

---

## Troubleshooting

- **`make all` says `overview_map.pdf` not found** → run `make overview-map`
  first (step 4); assembly consumes that file.
- **Overview map fails / no base map** → the `code/gis_data/` files are missing;
  recheck step 3b.
- **Photos blank or a monument has no photos** → run
  `python3 code/check_photo_names.py`; a name that won't parse or doesn't match a
  monument won't be placed.
- **OSM captures hang or come out blank** → network issue or Playwright browser
  not installed (`python3 -m playwright install chromium`); re-run, or force a
  recapture with `python3 code/bounds2pdf.py --force-screenshots`.
- **Page count differs from 66** → the report content changed since this guide
  was written; confirm the spreadsheet and `report/*.md` match the archived
  versions.

---

## Note on completeness (the archive self-test)

This guide is the acceptance test for the DocuShare archive. The two DocuShare
collection IDs above should be confirmed the first time the uploads are done —
if a rebuilder following these steps can produce the 66-page report with a
`verify PASS` using only a fresh clone plus those collections, the archive is
complete. Anything they have to hunt for elsewhere is a gap to close.
