# Acton Bounds — Project TODO

Status markers: [ ] open  [x] done
Owner tags: [Claude] [Claude Code] [Jim] [Both]

---

## bounds2pdf.py (Claude Code)

- [x] [Claude Code] Code cleanup: fix asyncio screenshot pattern, add Date of visit field, add Witnesses line, defensive NaN handling
- [x] [Claude Code] Photo integration: read manifest, place photos at bottom, dynamic grid (2/3/4/5-across — 5 used when all photos in a row are portrait), captions in small italic
- [x] [Claude Code] OSM screenshot caching: skip re-capture if cached file exists, --force-screenshots flag
- [x] [Jim] Verify DocuShare collection URL is publicly viewable without login — confirmed Jun 30 2026, no login needed in incognito
- [x] [Claude Code] Write scraper script (`scrape_docushare.py`): fetches collection page, parses Document-NNNNN IDs from `<tr about="...">`, writes docushare_urls.csv — done and verified against live data Jun 30 2026
- [x] [Claude Code] Write merge script (`merge_docushare.py`): joins docushare_urls.csv into photo_manifest.csv by filename (added docushare_url column) — done and verified
- [x] [Claude Code] bounds2pdf.py: photo images themselves are clickable links to their DocuShare original (not just captions); captions stay plain text; a centered "Click any picture to see full size" note appears above the photo grid only on pages with at least one linked photo — done and verified in generated PDF (10 working photo links)
- [x] [Claude Code] OSM map images are clickable links to the live interactive OpenStreetMap page (using the existing `OpenStreetMap link` column), with a "Click map to see full size" caption underneath — done and verified (48 working map links)
- [x] [Claude Code] Fixed left-column text indentation to pixel-match the top fields (Date of visit, etc.) — Table cells were rendering text ~6pt further left than plain paragraphs in this reportlab version; compensated via LEFTPADDING
- [x] [Claude Code] Moved "WGS84 (EPSG 4326)" to its own line after Coordinate Source, labeled "Datum:" in bold
- [x] [Jim] Confirm pagination behavior past ~100 items — confirmed Jul 2 2026: the full 177-document collection rendered on a single page with nothing clipped, so pagination isn't actually a problem at this collection size
- [x] [Claude Code] Full DocuShare photo batch uploaded and linked — all 173 local photos now have a `docushare_url` (done Jul 2 2026)
- [x] [Claude Code] Add page-number footer: "Monument Listings, page X of N", centered at bottom of each monument page — done Jul 1 2026 (`NumberedCanvas` class, standard ReportLab two-pass technique). Numbering is self-contained to this section (starts at 1) since the intro material isn't merged in yet; a `MONUMENT_LISTINGS_INTRO_PAGES` constant near the top of `bounds2pdf.py` (currently 0) offsets both X and N once Jim's intro page count is known — see item below

---

## Photo pipeline

- [ ] [Jim] Decide if any additional photos are needed, and take them
- [ ] [Jim] Edit photo_manifest.csv: captions, include/exclude decisions
- [ ] [Jim] Check monument photos for neighbor paint years (Carlisle: possibly 1959; Littleton, Westford, Maynard pending)
- [ ] [Jim] Upload monument photos to DocuShare "Perambulation Images" collection (manual via web UI)

---

## Field work

- [ ] [Jim] Work with Dean to paint the Keefe Street monument
- [ ] [Jim] Collect better coordinates with Town's iPad
- [ ] [Jim] For "Not Found" monuments, fill in the "Date of visit" column in
  the Google Sheet with the date(s) searched, where known — several already
  have a date buried in "Notes on Location" text (e.g. "Jim looked 10/22
  near boundary sign...") that just needs copying into the structured
  field. Once filled in, the report will show it labeled "Date searched:"
  instead of "Not yet searched" (bounds2pdf.py change done Jul 2 2026).
- [x] [Both] Decide on number of decimal places for lat/lon in monument
  listings — Jim decided Jul 5 2026: report displays 5 digits (~1m
  precision, well within GPS/field accuracy), but the XLSX keeps whatever
  precision is already stored per coordinate (not normalized/truncated),
  in case the extra digits are useful later. `bounds2pdf.py` formats to
  5 decimal places at display time only.
- [ ] [Jim] Finish gathering improved coordinates for all monuments (some
  were significantly off; field work with Town's iPad ongoing)
- [ ] [Claude Code] Once coordinates are finalized: generate a CSV of all
  monument coordinates (name, lat, lon) for reverse geocoding
- [ ] [Jim] Upload CSV to Geoapify online reverse geocoding tool
  (geoapify.com/tools/reverse-geocoding-online) — free, no account needed,
  accepts CSV/Excel, returns addresses + distance-to-nearest-address column.
  Use the distance column to flag woodland/no-address monuments where the
  nearest address is far away, and discard those results.
- [ ] [Both] Review geocoded addresses; add useful ones to the spreadsheet
  as a new "Nearest address" column; discard unhelpful results (woodland
  corners, roads that no longer exist, etc.)
- [ ] [Jim] Look up the date of the Select Board vote directing Dean Charter
  and Jim Snyder-Grant (two Select Board members) to conduct the perambulation.
  Needed for the legal background and summary of visits sections of the report.

---

## Comparative analysis

- [x] [Claude] Boxborough cross-reference table — done
- [x] [Claude] Concord cross-reference table — done
- [x] [Claude] Stow cross-reference table — done
- [x] [Claude] Sudbury — done (one corner, confirmed good)
- [ ] [Jim] Obtain and read Carlisle perambulation report
- [ ] [Jim] Obtain and read Littleton perambulation report
- [ ] [Jim] Obtain and read Westford perambulation report
- [ ] [Jim] Obtain and read Maynard perambulation report
- [ ] [Claude] Cross-reference Carlisle once report obtained
- [ ] [Claude] Cross-reference Littleton once report obtained
- [ ] [Claude] Cross-reference Westford once report obtained
- [ ] [Claude] Cross-reference Maynard once report obtained

(Full findings for Boxborough/Concord/Stow/Sudbury are written up in
Project Notes.md, not just here.)

---

## Town clerk letters

- [ ] [Jim] Send inquiry letters to Carlisle, Littleton, Westford, Maynard clerks (drafts ready)
- [ ] [Claude] Draft cover note to Boxborough Select Board
- [ ] [Claude] Draft cover note to Concord Select Board
- [ ] [Claude] Draft cover note to Stow Select Board
- [ ] [Both] Draft cover notes to Carlisle, Littleton, Westford, Maynard (after reports received)

---

## Introductory sections

Order below reflects planned appearance in the final report (tentative — may be rearranged during drafting):

1. - [x] [Both] Cover page: COMPLETE (FrontPage.svg/pdf in Bounds folder)
   - [x] [Claude Code] Add `orientation` (landscape/portrait/square) and `cover_candidate` (yes/blank, defaults to yes for included photos) columns to `photo_manifest.csv`, for claude.ai's Inkscape collage script — done Jun 30 2026 (`add_cover_columns.py`): 169 included photos classified (147 portrait, 22 landscape, 0 square), all opened successfully, safe to re-run (preserves manual overrides)
2. - [ ] [Jim] Write a one-page (or two-page) introduction to the Monument Listings section — explains what the per-monument pages that follow are and how to read them. Once written, tell Claude Code the final page count so it can set `MONUMENT_LISTINGS_INTRO_PAGES` in `bounds2pdf.py` (currently 0) — this shifts the "Monument Listings, page X of N" footer so numbering continues correctly after this intro is merged in front of it during final assembly
3. - [ ] [Claude] Legal background section (1648 law + MGL Ch. 42 §2; text nearly ready from Bounds Report parts.odt)
4. - [ ] [Claude] History of Acton's bounds (material in hand from 1904 book, needs connective prose)
5. - [ ] [Both] Overview map: convert KML to static image with monument status indicated
6. - [ ] [Both] Summary of visits and results (Jim to draft with Claude's help)
7. - [ ] [Claude] Other towns' reports: bibliography + comparative notes section
8. - [ ] [Claude] Policy recommendations section (rough notes in Bounds Report parts.odt)

---

## Additional research

- [ ] [Jim] See if planning department has any info on missing Acton/Westford corner monument
- [ ] [Jim] See if planning department has any info on missing Maynard Rte 62 monument

---

## Final assembly

- [ ] [Jim] Decide on format for intro sections (PDF vs ODT)
- [ ] [Jim] Re-export XLSX from Google Sheet before final report run
- [ ] [Claude Code] Merge intro PDF + monument pages PDF with pypdf or similar
- [ ] [Both] Design Google Drive archiving folder structure
- [ ] [Jim] Manually move Google Drive folder into DocuShare
- [ ] [Both] Categorize every file/folder in the Bounds Drive folder as one
  of: Keep & in git, Keep & in DocuShare, Both, Delete, or Keep until
  archive — the whole Drive folder structure will eventually go away once
  everything's archived, so nothing should end up with no destination.
  Surfaced while scoping the git repo (Jul 2 2026): several large root-level
  files (e.g. `ocm82856456-vol2.pdf`, `1904_Atlas...zip`) are candidates for
  DocuShare-only (not git) or deletion if superseded.
