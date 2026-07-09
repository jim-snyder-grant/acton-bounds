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

- [x] [Jim] Collect better coordinates with Town's iPad — done Jul 9 2026
- [x] [Jim] Check the west side of Main Street at the A/C crossing — done
  Jul 9 2026
- [x] [Jim] Get a better picture of the decoy ACW monument — done Jul 9 2026
- [x] [Jim] Check the other side of Fort Pond Road — done Jul 9 2026
- [x] [Jim] For "Not Found" monuments, fill in the "Date of visit" column in
  the Google Sheet with the date(s) searched, where known — done Jul 5
  2026; confirmed all 15 "Not Found" monuments now have a date filled in
  (bounds2pdf.py already shows these labeled "Date searched:" since Jul 2 2026).
- [x] [Both] Decide on number of decimal places for lat/lon in monument
  listings — Jim decided Jul 5 2026: report displays 5 digits (~1m
  precision, well within GPS/field accuracy), but the XLSX keeps whatever
  precision is already stored per coordinate (not normalized/truncated),
  in case the extra digits are useful later. `bounds2pdf.py` formats to
  5 decimal places at display time only.
- [x] [Jim] Finish gathering improved coordinates for all monuments (some
  were significantly off; field work with Town's iPad ongoing) — done
  Jul 9 2026
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
  Jim has located 4 Select Board minutes/plan documents on DocuShare
  confirming the vote/plan was in 2024 (not 2025); exact date pending
  claude.ai extracting it from the PDFs Claude Code fetched and saved to
  Drive's "Select Board Minutes/" folder Jul 9 2026.

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

Order below reflects planned appearance in the final report (tentative):

1. - [x] [Both] Cover page: COMPLETE (FrontPage.svg/pdf in Bounds folder)
   - [x] [Claude Code] Add `orientation` (landscape/portrait/square) and `cover_candidate` (yes/blank, defaults to yes for included photos) columns to `photo_manifest.csv`, for claude.ai's Inkscape collage script — done Jun 30 2026 (`add_cover_columns.py`): 169 included photos classified (147 portrait, 22 landscape, 0 square), all opened successfully, safe to re-run (preserves manual overrides)
2. - [ ] [Claude] Legal background — drafted (Drive: "Legal Background -
        draft.md"), pending Select Board vote date and Jim's review
3. - [ ] [Claude] History of Acton's bounds (material from 1904 book;
        road-naming research done; Parmenter Road thread; needs connective
        prose)
4. - [ ] [Both] How this report was created (see scope note below)
5. - [ ] [Both] Overview map: convert KML to static image with monument
        status indicated
6. - [ ] [Both] Monument Listings intro: one or two pages explaining what
        the per-monument pages are and how to read them. A plain-language
        rewrite exists in Drive ("Monument Listings intro - plain
        language rewrite.md") alongside the original, pending Jim's
        pick/merge.
7. - [ ] [Claude Code] Monument pages (bounds2pdf.py output) — COMPLETE
        pending finalized data
8. - [ ] [Claude] Next steps (short closing section; replaces "Policy
        recommendations")

Note: Other towns' perambulation reports will be mentioned in passing
in section 4, not as a standalone section. Road name changes (previously
its own possible item) are folded into section 3, History.

- [ ] [Claude] Add a right-justified, self-contained footer to sections
      2-6 (Legal background through Monument Listings intro): "{Section
      Name}, page X of M", matching the Monument Listings pages' footer
      style (Helvetica 9pt, #555555 gray, 1in side margins, 26pt above
      the bottom edge). Each section only needs to count its own pages —
      no need to know any other section's page count. Full visual spec
      in code/claude.md under "Page numbering — two-part footer." Cover
      page (section 1) is a title page and doesn't need one.

### Scope of section 4 — "How this report was created"

- The Select Board vote authorizing Jim Snyder-Grant and Dean Charter
  to conduct the perambulation (date TBD — Jim to look up)
- The process of locating monuments: what we did, what we found,
  what we didn't find, and what neighboring towns' records showed
  (brief mention of cross-referencing Boxborough, Concord, Stow,
  Sudbury reports — no separate bibliography section)
- Reaching out for additional witnesses: process and outcomes
- The painting process, with photos
- A note on Claude's role: appreciative in tone, noting this level
  of detailed municipal record-keeping would not have been practical
  for a two-person volunteer effort a few years ago. Mention the
  collaborative model (Claude Code for technical work, claude.ai for
  writing/analysis, coordinated via GitHub repo).
- Where the work is archived: DocuShare (Acton's permanent record)
  and the public GitHub repo (reusable by any Massachusetts town).
  Note: Google Drive was used as a working folder during the project
  but will not be maintained after completion — the durable archives
  are DocuShare and GitHub.

---

## Additional research

- [ ] [Jim] See if planning department has any info on missing Acton/Westford corner monument
- [ ] [Jim] See if planning department has any info on missing Maynard Rte 62 monument

---

## Final assembly

- [ ] [Jim] Decide on format for intro sections (PDF vs ODT)
- [ ] [Jim] Re-export XLSX from Google Sheet before final report run
- [ ] [Claude Code] Merge intro PDF + monument pages PDF with pypdf or
      similar, then stamp a left-justified "Acton Bounds Report
      2025-2026, page X of N" footer on every page of the merged result
      (N = merged total page count) — see "Page numbering" in
      code/claude.md
- [ ] [Both] Design Google Drive archiving folder structure
- [ ] [Jim] Manually move Google Drive folder into DocuShare
- [ ] [Both] Categorize every file/folder in the Bounds Drive folder as one
  of: Keep & in git, Keep & in DocuShare, Both, Delete, or Keep until
  archive — the whole Drive folder structure will eventually go away once
  everything's archived, so nothing should end up with no destination.
  Surfaced while scoping the git repo (Jul 2 2026): several large root-level
  files (e.g. `ocm82856456-vol2.pdf`, `1904_Atlas...zip`) are candidates for
  DocuShare-only (not git) or deletion if superseded.
