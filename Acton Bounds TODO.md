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
- [x] [Both] Reverse geocoding (CSV generated, uploaded to Geoapify,
  results reviewed) — done Jul 9 2026, decided against: Jim concluded
  the addresses returned don't add enough useful information over the
  coordinates already in the report. Future searchers navigating to a
  monument are better served by coordinates than a street address
  anyway. No "Nearest address" column added.
- [x] [Jim] Re-check the measured coordinates for Acton/Littleton Fort Pond
  Road (Order 30) — resolved without a field recheck (Jul 10 2026). The
  ~8.6 m offset from `check_distance_to_line.py` is explained by the 1904
  survey's two monuments on the easterly and westerly sides of "the Cash
  Road" at this crossing; what's recorded is the westerly one, so the
  offset is expected, not a bad reading. See that row's "Notes on Location"
  in the Sheet and "Next Steps - draft.md" (Drive) for the full
  explanation. No further recheck needed. (The neighboring Acton/Littleton
  W B Marker on Fort Pond Road, Order 31, ~19.5 m off-line, is a Witness
  Bound intentionally set off the line — always expected, never part of
  this check.)
- [x] [Jim] Look up the date of the Select Board vote directing Dean Charter
  and Jim Snyder-Grant (two Select Board members) to conduct the perambulation.
  Needed for the legal background and summary of visits sections of the report.
  — done Jul 9 2026: October 21, 2024, Item 14 ("Approve Plan for Perambulation
  of Town Bounds"), approved 5-0. See Project Notes.md for full citation and two
  related follow-up items (Jul 21 2025 progress update, Mar 16 2026 liaison
  appointment).

---

## Comparative analysis

- [x] [Claude] Boxborough cross-reference table — done
- [x] [Claude] Concord cross-reference table — done
- [x] [Claude] Stow cross-reference table — done
- [x] [Claude] Sudbury — done (one corner, confirmed good)
- [x] [Jim] Carlisle/Littleton/Westford/Maynard perambulation reports —
  decided against further pursuit (Jul 10 2026). Requested once in 2025;
  no response, and a second request isn't expected to turn up anything
  new. Comparative analysis for these four towns will not be done.

(Full findings for Boxborough/Concord/Stow/Sudbury are written up in
Project Notes.md, not just here.)

---

## Neighboring-town cover notes

Cover notes accompany Acton's report to the neighbors whose bounds it
cross-references. The Carlisle/Littleton/Westford/Maynard clerk-letter and
cover-note items were dropped Jul 10 2026 (see the Comparative analysis
note above — those four towns' reports were never obtained and are no
longer being pursued). The three below stand because those towns' reports
*were* obtained and cross-referenced.

- [ ] [Claude] Draft cover note to Boxborough Select Board
- [ ] [Claude] Draft cover note to Concord Select Board
- [ ] [Claude] Draft cover note to Stow Select Board

---

## Introductory sections

Order below reflects planned appearance in the final report (tentative):

1. - [x] [Both] Cover page: COMPLETE (FrontPage.svg/pdf in Bounds folder)
   - [x] [Claude Code] Add `orientation` (landscape/portrait/square) and `cover_candidate` (yes/blank, defaults to yes for included photos) columns to `photo_manifest.csv`, for claude.ai's Inkscape collage script — done Jun 30 2026 (`add_cover_columns.py`): 169 included photos classified (147 portrait, 22 landscape, 0 square), all opened successfully, safe to re-run (preserves manual overrides)
2. - [x] [Claude] Legal background — approved draft "Legal Background -
        draft v2.md" (Drive), rendered to "Legal Background.pdf" and in the
        assembled report (Jul 10 2026). Pending only Jim's read-through of
        the rendered PDF.
3. - [x] [Claude] History of Acton's bounds — approved draft "History of
        Actons Bounds - draft.md" (Drive), rendered to "History.pdf" and in
        the assembled report (Jul 10 2026). Two minor threads may still see
        wording updates (automobile-era road-naming research; Parmenter
        Road path) but neither blocks inclusion.
4. - [x] [Both] How this report was created — draft "How This Report Was
        Created - draft.md" (Drive, 3 photos), rendered to "How This Report
        Was Created.pdf" and in the assembled report (Jul 10 2026). Needed
        new image support in `intro2pdf.py` (added Jul 10 2026). See scope
        note below. Jim is still considering moving its opening
        (Select Board vote) paragraph to the very front of the report.
5. - [x] [Both] Monument Listings — Introduction: one intro covering both
        the per-monument pages and the overview map, since they share the
        numbered-box system. Approved combined draft "Monument Listings and
        Overview Map intro - combined draft.md" (Drive), rendered to
        "Monument Listings — Introduction.pdf" and in the assembled report
        (Jul 10 2026). Now placed *before* the Overview Map (the reorder
        below is done).
   - [x] [Claude] Reorder so the Monument Listings intro comes *before* the
         Overview Map, with one combined intro introducing both — DONE
         Jul 10 2026: sections swapped in `code/report_sections.csv`
         (intro = 5, map = 6) and assembly re-run.
6. - [x] [Claude Code] Overview map — BUILT (`code/overview_map.py`,
        Jul 9 2026): legal-portrait vector PDF, gold boundary through
        corner monuments, type-coded icons, 51 status-colored numbered
        callout boxes, real MassGIS roads + open water inside the
        boundary, legend/compass/footer. Full spec in "Overview Map
        spec.md" (Drive). Clickable callout boxes: DONE Jul 9 2026 — each
        box is an internal link to that monument's page in the merged
        report (added at assembly from an `overview_map_links.json`
        sidecar; targets `listings_start + Order - 1`). Verified in the
        63-page assembled PDF (Order 1 → p11 … Order 51 → p61).
7. - [ ] [Claude Code] Monument pages (bounds2pdf.py output) — COMPLETE
        pending finalized data
8. - [x] [Claude] Next steps — approved draft "Next Steps - draft.md"
        (Drive), rendered to "Next Steps.pdf" and in the assembled report
        (Jul 10 2026). Closing section; replaced "Policy recommendations".

Note: Other towns' perambulation reports will be mentioned in passing
in section 4, not as a standalone section. Road name changes (previously
its own possible item) are folded into section 3, History.

- [x] [Claude Code] Right-justified per-section footer — DONE for
      Markdown-sourced intro sections via `code/intro2pdf.py` (Jul 9
      2026): renders any intro `.md` to a styled PDF with the matching
      "{Section Name}, page X of M" footer (Helvetica 9pt, #555555, 1in
      margins, 26pt above the bottom edge; section name from the first
      `#` H1). Sections authored some other way still need to match this
      style themselves. Cover page (section 1) is a title page, no footer.

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
- [x] [Claude Code] Merge section PDFs and stamp the left-justified
      "Acton Bounds Report 2025-2026, page X of N" whole-report footer —
      DONE Jul 9 2026 (`code/assemble_report.py`, uses pypdf). Section
      order/list lives in `code/report_sections.csv`
      (order,section,file,footer); missing sections skip gracefully so
      partial drafts assemble; mixed page sizes (letter + legal map)
      handled. Verified on the 5 sections that exist today → 57-page PDF
      with both footers correct. `bounds2pdf.py` now emits its section to
      `code/monument_listings.pdf`, so the assembly owns the canonical
      output "Acton Bounds Report 2025-2026.pdf". (Once History /
      How-created / Next-steps sections exist, just add/enable their rows
      in the manifest and re-run.)
- [ ] [Both] Install the map dependencies so `overview_map.py` can run again.
  `geopandas`, `matplotlib`, `shapely` and `pyproj` are listed in
  `code/requirements.txt` but are NOT actually installed in the `bounds` pyenv
  (confirmed Jul 15 2026) — so `make overview-map` fails, and the requirements
  file makes the map look rebuildable when it isn't. Everything else (pandas,
  reportlab, pypdf, playwright, Pillow) is installed, so the normal build is
  fine; only the map generator is dead.
  **Why this is worth doing, beyond convenience:** `code/overview_map.pdf` is
  gitignored and `code/gis_data/` (60MB: MassDOT RoadInventory roads, MassGIS
  hydro25k) is untracked — only `overview_map.py` itself is committed. So the
  report's whole map page currently exists as one un-backed-up local file that
  nothing on this machine can regenerate. Insync/Drive is the only thing behind
  it, and the report itself says Drive isn't a durable archive. Installing the
  deps turns a frozen artifact back into a reproducible output.
  **Deferred Jul 15 2026** — Jim was mid early-reviewer send, and geopandas may
  bump numpy/pandas in an env that currently builds the report perfectly; a bad
  day to break it.
  **Plan when picked up:** `pip freeze > snapshot.txt` first so the working env
  is exactly restorable → install → re-run `make all` and confirm 64 pages with
  verify PASS (proves nothing collateral broke) → then `make overview-map` and
  compare the regenerated map against the current one. Treat that last step as a
  real experiment, not a formality: `overview_map.py` hasn't been run since
  Jul 9 2026, and a newer matplotlib could shift fonts or box positions, which
  would move the callout rectangles in `overview_map_links.json` and therefore
  the 51 clickable links. `verify_report.py` catches links pointing at the wrong
  page, but NOT visual drift — eyeball the map before keeping it.
  Ties into the "Categorize every file/folder" item below: decide whether
  `gis_data/` should be tracked (60MB — large but not absurd) or whether its
  provenance is documented well enough to re-download.

- [ ] [Both] Design Google Drive archiving folder structure
- [ ] [Jim] Manually move Google Drive folder into DocuShare
- [ ] [Both] Categorize every file/folder in the Bounds Drive folder as one
  of: Keep & in git, Keep & in DocuShare, Both, Delete, or Keep until
  archive — the whole Drive folder structure will eventually go away once
  everything's archived, so nothing should end up with no destination.
  Surfaced while scoping the git repo (Jul 2 2026): several large root-level
  files (e.g. `ocm82856456-vol2.pdf`, `1904_Atlas...zip`) are candidates for
  DocuShare-only (not git) or deletion if superseded.
