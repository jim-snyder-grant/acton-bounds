# Acton Bounds — Changelog

Running log of substantive changes to shared project files.
One line per change, newest at top.
Format: YYYY-MM-DD [who] file changed: description

---

2026-07-12 [Claude Code] Added code/verify_report.py -- the overview-map link
  check as a committed, allowlisted script (replaces the inline python3
  heredoc, which now prompts under the curated Tier-1 allowlist). Derives
  everything from the assembled PDF + overview_map_links.json (no hardcoded
  page numbers): finds the map page, matches each callout link's rect back to
  its sidecar box to recover its Order, and verifies all Orders 1..N are linked
  once and map slope-1 onto consecutive monument pages. Prints PASS/FAIL, exits
  0/1 (usable as a pre-commit gate). Verified both paths (PASS on the report,
  FAIL on a linkless section PDF). Added as pipeline step 4 in code/claude.md.

2026-07-12 [Claude Code] Tier 1 dev-workflow cleanup: curated the Bash
  permission allowlist in code/.claude/settings.local.json (personal, not
  committed -- noted here so a future session keeps the policy). Pruned the
  accumulated broad auto-approvals and now DELIBERATELY prompt for: git commit
  (so Jim reviews every message), on-the-fly Python (python3 -c / `python3 -
  <<heredoc`), rm/cp/mv, curl, gh, pip install. Auto-allowed (no review value):
  cd, ls, find, grep, head, tail, mkdir; git status/diff/log/show/ls-files/
  check-ignore/add/push; and the committed pipeline scripts by name
  (bounds2pdf/assemble_report/intro2pdf/build_manifest/overview_map, bare and
  code/-prefixed). Don't re-broaden this without Jim's say-so -- the prompts on
  commit and ad-hoc code are intentional.

2026-07-12 [Claude Code] Run the whole pipeline from the project root (no
  more `cd code/`). Every script now anchors its data paths to its own file
  location (HERE = code/, ROOT = Bounds/) instead of assuming the CWD is
  `code/`: fixed bounds2pdf.py, build_manifest.py, add_cover_columns.py,
  merge_docushare.py, scrape_docushare.py, check_distance_to_line.py, and
  generate_geocoding_csv.py (assemble_report.py, overview_map.py, intro2pdf.py
  already self-anchored). Added a root `.python-version` (= bounds, tracked)
  so pyenv activates the report env at the root too; `Photos/` keeps its own
  `photos` env. Verified the full pipeline end-to-end from the root:
  bounds2pdf -> code/monument_listings.pdf, intro2pdf -> report/*.pdf,
  assemble_report -> 64-page report with all 51 overview-map links intact;
  all edited scripts byte-compile. Updated code/claude.md "Running the
  Scripts" (run-from-root, output locations, why two pyenv envs). This is
  Tier 2 of the dev-workflow cleanup; the pruned permission allowlist (Tier 1)
  comes next, targeting the now-canonical `python3 code/<script>.py` forms.

2026-07-12 [Claude Code] intro2pdf.py: keep `##` subheads with the content
  that follows them (keep-with-next), so a subhead is never stranded at the
  foot of a page while its material begins on the next. New
  keep_headings_with_next() post-pass wraps each H2 + any following Spacers +
  the first real content block (paragraph, image row, quote, or bullet) in a
  KeepTogether; consecutive headings are left un-consumed so each binds to its
  own body. General/layout-only -- re-flows correctly as the text shifts with
  edits. Fixed the two reported cases ("The painting process" -> now on the
  same page as its equipment photos; "A road that disappeared: Parmenter Road"
  -> now with its paragraph). Re-rendered all five report/*.pdf and
  re-assembled -- still 64 pages, all 51 overview-map links resolve (p12-62).

2026-07-12 [Claude Code] NEW WORKFLOW — canonical report sources in git +
  a `from-claude-ai/` staging folder. TWO NEW CONVENTIONS, both aimed at
  keeping the Bounds root clean and making the report reproducible from a
  clone. (1) **`Bounds/report/`** now holds the canonical, stable-named
  section sources (`Introduction.md`, `History.md`, `The Work Behind This
  Report.md`, `Monument Listings — Introduction.md`, `Next Steps.md`),
  tracked in git (allowlist: `report/*.md` only; rendered `report/*.pdf`
  stay ignored as build artifacts). `report_sections.csv` is now tracked
  too and its rows point at `report/*.pdf`. Re-rendered all five into
  `report/` and re-assembled — "Acton Bounds Report 2025-2026.pdf" still 64
  pages, all 51 overview-map links still resolve (p12-62). The stale root
  copies of those drafts/PDFs were deleted. (2) **claude.ai handoffs now go
  in `Bounds/from-claude-ai/`** (Drive-only, never tracked) instead of the
  Bounds root — for claude.ai: drop report-section drafts there named for
  their final section title (e.g. `Introduction.md`, no `draft`/`v2`
  suffixes), and instruction files as `INBOX-<slug>.md`; Claude Code
  greps each for secrets, promotes drafts into `report/`, renders +
  re-assembles, then deletes the staging copy. Full spec in code/claude.md
  ("Canonical report sources" + updated INBOX protocol). Folder ID stored
  locally, not committed.

2026-07-12 [Claude Code] Processed 3 INBOX files (intro-section content and
  renames). (1) History: rendered `History of Actons Bounds - draft v2.md`
  (adds a new "The 1904 Atlas itself" subsection) -> History.pdf, now 3 pages.
  (2) Renamed the "Legal Background" section to "Introduction": rendered
  `Introduction - draft.md` -> Introduction.pdf (opens with the Oct 21 2024
  Select Board vote paragraph moved up from the next section), replaced
  Legal Background.pdf, updated report_sections.csv row 2. (3) Renamed "How
  This Report Was Created" to "The Work Behind This Report": rendered
  `The Work Behind This Report - draft.md` (opening vote paragraph removed;
  uses the corrected "(2)" duplicate body ending "...won't be maintained once
  the report is complete.") -> The Work Behind This Report.pdf, updated
  report_sections.csv row 4. Re-ran assemble_report.py -> "Acton Bounds
  Report 2025-2026.pdf", now 64 pages (was 63); re-verified all 51
  overview-map callout-box links still resolve 1:1 to the shifted listings
  pages (now p12-62, Order 1 -> p12 ... Order 51 -> p62). Deleted the
  superseded "How This Report Was Created" drafts/PDF and both v2 duplicates,
  plus Legal Background.pdf and the 3 INBOX files.

2026-07-10 [Claude Code] Processed 8 INBOX files -- all 8 report sections
  now drafted, rendered, and assembled into one 63-page PDF for the first
  time. (1) intro2pdf.py gained image support: `![cap](path)` lines group
  into a dynamic-grid photo row (<=3 across) with italic captions and
  optional DocuShare links, paths resolved against script dir/cwd/md dir;
  needed for "How This Report Was Created" (3 photos). (2) Rendered the five
  approved intro drafts -- Legal Background (v2), History, How This Report
  Was Created, the combined Monument Listings — Introduction, and Next
  Steps -- to PDFs at the Bounds root. (3) report_sections.csv: swapped so
  the Monument Listings intro (5) precedes the Overview Map (6) per the
  combined-intro decision, and pointed rows at the new PDFs. (4) Re-ran
  assemble_report.py -> "Acton Bounds Report 2025-2026.pdf", 63 pages, all
  8 sections; verified both footer halves across letter+legal sizes and all
  51 overview-map box links resolving to the right listings pages (Order 1
  -> p11 ... Order 51 -> p61). (5) TODO.md: closed the Fort Pond Road
  recheck (resolved, not deferred -- westerly-of-two 1904 monuments
  explains the ~8.6m offset), dropped the Carlisle/Littleton/Westford/
  Maynard clerk-letter + cross-reference items (decided against further
  pursuit), kept the Boxborough/Concord/Stow cover-note items, and marked
  intro items 2-8 done. Project Notes.md: renamed the "Not yet read"
  comparative-analysis subsection to reflect that closed decision. NOTE:
  installed pypdf into the `bounds` pyenv (it's in requirements.txt but was
  missing from the env); geopandas/matplotlib are also absent but weren't
  needed since overview_map.pdf was already built.

2026-07-09 [Claude Code] Clickable overview-map callout boxes -- the last
  of the three report-assembly pieces. overview_map.py writes a sidecar
  (overview_map_links.json) with each box's rectangle in PDF points;
  assemble_report.py overlays an internal "go to that monument's page" link
  over each box on the merged map page (target = listings_start + Order - 1).
  /Dest references the real page object (spec-correct, not a bare page
  number) with an invisible border. Verified in the assembled 57pp PDF: 51
  links, Order 1->p7, 7->p13, 25->p31, 51->p57, page count unchanged. Skips
  linking with a warning if the sidecar is missing or the listings page
  count doesn't match the box count 1:1 (spillover guard). All three pieces
  from notes.forclaude.code (intro2pdf, assemble_report, clickable boxes)
  are now done.

2026-07-09 [Claude Code] TODO.md: added a consideration (for claude.ai) —
  Jim would like to reorder so the Monument Listings intro comes *before*
  the Overview Map, and have claude.ai rewrite that intro to introduce the
  overview map at the same time as the per-monument listings (one intro
  covering both, since they share the numbered-box system). If adopted,
  swap sections 5↔6 in report_sections.csv and re-run assembly. See the
  Introductory sections list, item 6.

2026-07-09 [Claude Code] overview_map.py: narrowed the legend box (leg_w
  2.35->1.95) and nudged its center left (leg_cx 4.85->4.65) so its right
  edge no longer overlaps the gold boundary line; the left edge is
  unchanged and all labels still fit comfortably. Re-ran the assembly.

2026-07-09 [Claude Code] overview_map.py: added a centered "Overview Map"
  title (bold, rule beneath, intro-section H1 style) in a reserved band at
  the top of the page; the map/perimeter-boxes shift down to make room, no
  collision. Updated Overview Map spec.md and re-ran the assembly (57pp).

2026-07-09 [Claude Code] intro2pdf.py: body paragraphs are now left-aligned
  (ragged right) instead of fully justified -- Jim found the justified
  spacing created stretched-out "rivers." Only the BODY style changed;
  headings/bullets/quotes were already left-aligned. Regenerated the two
  intro section PDFs and re-ran the assembly (57pp) so the final report
  reflects it.

2026-07-09 [Claude Code] bounds2pdf.py now emits its Monument Listings
  section to code/monument_listings.pdf (gitignored, alongside
  overview_map.pdf) instead of the whole-report name, so assemble_report.py
  can output the canonical ../Acton Bounds Report 2025-2026.pdf. Updated
  report_sections.csv (row 7 -> code/monument_listings.pdf) and
  assemble_report.py's default output accordingly. Regenerated both:
  monument_listings.pdf (51pp) then the assembled ../Acton Bounds Report
  2025-2026.pdf (57pp), verified the two-part footer on the first monument
  page ("...page 7 of 57" left, "Monument Listings, page 1 of 51" right).
  The old whole-report file at that root path (previously just the
  listings) is now correctly the full assembled report.

2026-07-09 [Claude Code] Added code/assemble_report.py + report_sections.csv:
  the final-assembly step. Concatenates the section PDFs in the order given
  by report_sections.csv (order,section,file,footer) and stamps the
  left-justified whole-report footer "Acton Bounds Report 2025-2026, page X
  of N" on every merged page once the true total is known -- completing the
  two-part footer (each section already carries its own right-justified
  footer). Missing sections skip with a warning (partial drafts assemble);
  footer=no suppresses the whole-report footer on a section (e.g. the cover)
  while still consuming a page number; mixed page sizes handled (letter
  sections + legal-size overview map). Verified: assembled the 5 sections
  that exist today (Cover, Legal Background, Overview Map, Monument Listings
  intro, Monument Listings) into a 57-page PDF with both footers landing
  correctly across sizes. Needs pypdf (added to requirements.txt). This is
  the third of the three report-assembly pieces from notes.forclaude.code.
  Output name is "Acton Bounds Report 2025-2026 - FULL.pdf" for now, kept
  distinct from bounds2pdf.py's monument-listings output at "Acton Bounds
  Report 2025-2026.pdf"; report_sections.csv is a local (untracked) working
  file. Remaining piece: clickable callout boxes (PDF anchors).

2026-07-09 [Claude Code] Added code/intro2pdf.py: renders an intro-section
  Markdown file to a styled PDF matching the monument-listing pages (US
  Letter, 1in margins, Helvetica, right-justified per-section footer via
  the shared two-pass canvas). Supports H1/H2, justified paragraphs,
  bullets, gold-barred block quotes, rules, and inline bold/italic;
  section name comes from the first H1 (or --section). Verified against
  the two drafted intro sections in Drive ("Legal Background - draft.md",
  "Monument Listings intro - plain language rewrite.md") -- both render
  cleanly. This is the first of the three report-assembly pieces from
  notes.forclaude.code; the intro-MD-to-PDF step is now available.
  Draft-note headers / [bracketed] asides in the source .md render
  literally and should be stripped before a final run.

2026-07-09 [Claude Code] Overview Map (report section 5) built:
  code/overview_map.py generates a legal-portrait 8.5x14 vector PDF —
  gold boundary through corner monuments in Order sequence (ACC true
  corner substituted at Order 12), hollow type-coded icons, 51
  status-colored numbered callout boxes (per-side corner-fix placement,
  CCW from Order 1 = ACMS lower-right), legend, compass rose. Base map
  is real MassGIS data cached in gitignored code/gis_data/ (MassDOT
  RoadInventory roads + MassDEP Hydrography 1:25,000 open water),
  clipped to inside the boundary only. requirements.txt gains
  geopandas+matplotlib. Applied Jim's latest tweaks (notes.forclaude.code):
  callout leaders now leave each box from its interior-facing edge
  (inner corner for corner boxes), single "Route 2" road label, and a
  right-justified "Overview Map, page 1 of 1" footer matching the other
  sections. Documented in code/claude.md (standalone utilities).
  Still open: PDF anchors for clickable boxes.

2026-07-09 [Claude Code] Consolidated Overview Map spec.md into one
  authoritative document and deleted the six INBOX-overview-map-*.md
  messages (update, update-2, basemap, mockup-handoff, corner-fix,
  consolidate) now folded into it — per the consolidation request in
  INBOX-overview-map-consolidate.md. The spec now reflects the built
  state (page size, rotation-from-coordinates, base-map data sources,
  boundary/ACC substitution, icons, corner-fix box placement,
  interior-edge callout attachment, legend/compass, caption, footer)
  plus the remaining open item (clickable-box PDF anchors).

2026-07-09 [Claude Code] Resolved the Select Board vote-date question
  (claude.ai read the minutes PDFs and relayed the answer via INBOX.md).
  The Board voted 5-0 to approve the perambulation plan on October 21, 2024
  (Item 14). Applied: TODO.md Field work item marked done; Project Notes.md
  gained a RESOLVED line and a new "Select Board minutes" subsection
  summarizing the three relevant meetings (Oct 21 2024 authorizing vote,
  Jul 21 2025 progress update, Mar 16 2026 liaison appointment); Legal
  Background - draft.md placeholder replaced with the confirmed date.

2026-07-09 [Claude Code] Reran check_distance_to_line.py against the
  finalized iPad coordinates. All 3 issues from the Jul 7 run are
  resolved: Acton/Maynard Conant St (was ~110km, now 0.2m),
  Acton/Concord Great Rd (~52m -> 0.6m), Acton/Littleton Nagog Hill Rd
  (~16m -> 4.0m). Every crossing is now <=4m off-line except
  Acton/Littleton Fort Pond Road (~8.6m) -- added a TODO.md Field work
  item for Jim to re-check that reading with the iPad. The neighboring
  W B Marker on Fort Pond Road (~19.5m) is a Witness Bound, expected to
  sit off the line, so not flagged. No spreadsheet or code changes.

2026-07-09 [Jim] TODO.md: reverse geocoding tried and decided against.
  Reviewed Geoapify's results on the 49-monument CSV; the returned
  addresses don't add enough useful information over the coordinates
  already in the report, and coordinates are more useful than a street
  address for someone navigating to a monument anyway. Collapsed the
  3-item TODO sequence (generate CSV / upload / add Nearest address
  column) into one done-and-decided-against entry. No spreadsheet or
  report changes.

2026-07-09 [Claude Code] Added `code/generate_geocoding_csv.py` and ran
  it: 49 monuments' full-precision coordinates exported as
  `monument_coordinates_for_geoapify.csv` (lon/lat columns only, per
  Jim's spec) for Geoapify's drag-and-drop reverse-geocoding tool. 2
  monuments with no recorded coordinates skipped. Jim confirmed
  drag-and-drop is simpler than API calls for this one-off use.

2026-07-09 [Jim] TODO.md Field work: batch status update on the 13
  open [Jim] items. 5 marked done (Town's iPad coordinates, west side
  of Main St at the A/C crossing, ACW decoy picture, other side of Fort
  Pond Road, finishing improved coordinates for all monuments). 6
  removed rather than marked done -- their content moved to individual
  monuments' "Possible Next Steps" field in the spreadsheet instead
  (Keefe Street painting, Maynard-side Rte 27 picture, Powder Mill
  plans review, ACC/AC Ben's Woods walk, AW1/ALW walk, Sarah Indian Way
  map/walk): tracking the specific action against the specific
  monument is more useful going forward than a generic TODO line, and
  they weren't actually complete. Geoapify CSV upload still open;
  Select Board vote date unchanged (pending claude.ai). Coordinates
  being finalized unblocks the next TODO item (Claude Code generating
  a reverse-geocoding CSV) -- not started yet, Jim hasn't asked for it.

2026-07-09 [Claude Code] Fetched the 4 DocuShare PDFs claude.ai couldn't
  render (its web_fetch tool returned empty content and this session
  has no browser tool) -- saved to new Drive folder "Select Board
  Minutes/": 2024-10-21 Select Board Minutes.pdf, Perambulation Plan.pdf,
  Select Board Minutes item12.pdf (Jul 21 2025), 2026-03-16 Select Board
  Minutes.pdf. One fetch hit a transient DocuShare guest-license limit
  on first try, succeeded on retry. Content extraction (vote date,
  "2025 vs 2024" typo check, general skim of doc 4) left to claude.ai
  per Jim's steer -- not done here.
2026-07-08 [claude.ai via INBOX] README.md: updated claude.ai access
  model -- now has GitHub MCP + filesystem MCP but agreed NOT to write
  directly to repo; all repo changes still go through Claude Code via
  INBOX.md; added filesystem path and MCP tool examples to orientation
  section. Deviated from the INBOX text once: it included the literal
  local filesystem path as an example, which embeds Jim's Google account
  email as the Insync sync-folder name -- replaced with a placeholder
  and a pointer to ask Jim for the real path instead, per the standing
  rule against emails in public repo files.
2026-07-08 [claude.ai] Drafted "Legal Background - draft.md" (Drive only).
  Includes the 1648 law text and current MGL Ch. 42 §2 text (both verified
  live). Resolved the open $5/$20 fine question from Project Notes.md:
  confirmed at malegislature.gov that MGL Ch. 42 §3 (which held the
  penalty) was repealed in 1973 -- current law imposes no fine at all.
  Per Jim: last substantial Acton perambulation before this one was 1986
  (per stone markings); corrected "most consistent neighbor" from Stow to
  Sudbury (marks the Acton/Concord/Maynard/Sudbury corner roughly every 5
  years since at least 1995). Select Board vote date still open pending
  minutes (now fetched, see entry above); draft has a placeholder.
2026-07-08 [claude.ai] Drafted "Monument Listings intro - plain language
  rewrite.md" (Drive only) -- simpler-language version of Claude Code's
  original per Jim's request (shorter sentences/words, more bullets,
  matching History section style). Original left untouched; Jim to
  compare and pick/merge.
2026-07-08 [Both] Discussed Claude Code's proposed branch-based workflow
  (claude.ai commits doc-only changes to a non-main branch, fast-forward
  after a grep-for-secrets pass) as an alternative to the INBOX.md
  round-trip. Jim decided to keep INBOX.md as-is for now.
2026-07-08 [Jim] Root-caused the duplicate "Monument notes review.md"
  files (one .md, one Google Doc): opening a Drive .md file directly in
  Google Docs silently creates a converted Doc copy as a side effect --
  distinct from the Insync same-name-duplicate issue already documented
  in code/claude.md. Both stray copies deleted; Jim will use text tools
  on the Insync-synced files instead of opening them in Google Docs
  going forward.

2026-07-07 [Both] Reviewed and confirmed "Monument Listings intro
  draft.md" (Drive only) section by section with Jim. Added six new
  sections beyond the original content: reading the colored order-
  number/status boxes, Corner vs. Street Crossing (a monument's naming
  pattern reveals which — corners are named just for the towns
  involved, street crossings add the Acton-side street name), what each
  Status value means, what each Coordinate Source value means, witness
  markers / "Witness Bound" (kept intentionally unresolved per Jim —
  "an interesting mystery for a person in the future"), and tie-break
  numbers (corners are named for the towns that meet there; numbered
  when a shared two-town boundary has more than one corner along it,
  generally west-to-east/north-to-south). Corrected two of my own
  drafting assumptions along the way: corners aren't only triple-town
  meeting points (some are two-town corners where either the boundary
  bends or just the far-side town changes on an otherwise straight
  Acton line), and coordinate source "Mark R. phone" no longer exists —
  Jim found a GIS iPad reading for that monument instead and removed
  the name from the sheet (too specific to be useful to a reader).
  Also genericized personal attribution (Dean did most of the actual
  painting, not Jim) and pruned several implementation-only passages
  that belonged in code/claude.md, not a reader-facing intro (exact
  footer mechanics, exact display-rule edge cases) per Jim's framing:
  "the intro is for humans to read to orient themselves... not for
  people or AIs trying to recreate the report."
  footer (Jim's proposal): right-justified per-section self-contained
  counter (e.g. "Monument Listings, page 12 of 51"), rendered by
  whichever tool generates that section, plus a left-justified
  whole-report counter (e.g. "Acton Bounds Report 2025-2026, page 23 of
  73") stamped across every page in one pass at final assembly, once the
  true total is known. Replaces the `MONUMENT_LISTINGS_INTRO_PAGES`
  offset-constant approach (used briefly Jul 4-7), which required a
  manual recompute-and-set step and only solved the problem for the
  Monument Listings section. `bounds2pdf.py`: removed the constant,
  changed `NumberedCanvas._draw_footer()` from centered to
  right-justified at the 1in margin, self-contained numbering (no
  offset). Verified: 51 pages unchanged, footer renders correctly
  ("Monument Listings, page 1 of 51", right-justified). Added TODOs:
  claude.ai to add matching right-justified footers to sections 2-6;
  Claude Code to stamp the left-justified whole-report footer as part of
  the final-assembly merge step. Full spec in code/claude.md under "Page
  numbering — two-part footer."

2026-07-04 [claude.ai] TODO.md, Project Notes.md: revised report
  section order and scope — renamed "Summary of visits" to "How this
  report was created" (expanded scope); removed standalone "Other
  towns' reports" section; renamed "Policy recommendations" to "Next
  steps"; confirmed Google Drive will be retired after project
  completion (DocuShare + GitHub are durable archives)
2026-07-07 [Claude Code] Applied the above (held pending Jul 4–7 since
  it conflicted with a same-week direct restructure of TODO.md's
  Introductory sections — Jim resolved in favor of claude.ai's version):
  updated TODO.md's Introductory sections list to the 8-section
  structure and added the matching "Report structure" section to
  Project Notes.md.
2026-07-07 [claude.ai] bounds2pdf.py: add "Possible Next Steps" optional
  field (renders only when non-empty; placed after Notes on Monument,
  before photos; intended for Not Found/Documented/Couldn't paint pages)
2026-07-07 [claude.ai] photo_manifest.csv: context photos for sparse
  pages — Jim will add these; Claude Code rendering requires no changes
2026-07-07 [Claude Code] Implemented the above: `bounds2pdf.py` renders
  `Possible Next Steps` (bold label) right after Notes on Monument when
  non-empty. Jim filled in 19 rows to test; caught and fixed a data-entry
  mistake along the way (Acton/Westford Bear Hill Road's Possible Next
  Steps text had been typed into the Name and Tie-break number cells
  instead). Verified: 51 pages unchanged, text renders and wraps
  correctly (spot-checked Order 7, 18, 42). Correction: Jim's actual
  usage isn't limited to Not Found/Documented/Couldn't paint — he also
  added entries for damaged-but-Painted monuments (e.g. leaning or
  buried monuments needing repair), so the field is for any monument
  needing follow-up, not just the sparse-page statuses.
2026-07-04 [claude.ai] code/claude.md: clarified that
  MONUMENT_LISTINGS_INTRO_PAGES = total pages of all intro sections
  (1-6), not just the Monument Listings intro page; will be set in
  final assembly pass only
2026-07-07 [Claude Code] Added `code/check_distance_to_line.py`: measures
  each Street-Crossing monument's perpendicular distance from the
  straight line connecting its two nearest Corner monuments (MA town
  boundaries are straight lines between corners), using the true
  Acton/Carlisle/Concord corner location (parsed from its "Notes on
  Monument" text) rather than that row's witness-monument coordinates.
  First run found a clear data-entry bug -- Acton/Maynard Conant
  Street's latitude was off by a whole degree (`43.4...` instead of
  `42.4...`, ~110km) -- plus 2 real, unexplained offsets worth a field
  re-check (Acton/Concord Great Road ~52m, Acton/Littleton Nagog Hill
  Road ~16m). Full results in "Monument distance-to-line check.md"
  (Drive). Documented in code/claude.md alongside extract_town_corners.py
  under a new "Standalone utility scripts" section.
2026-07-07 [Both] Claude Code read through all 51 monuments' notes
  fields for coherence and handed Jim a checklist; Jim worked through it
  directly in Acton Bounds.xlsx/the Sheet. Two changes affect the
  report's meaning, not just wording:
  - **Status corrected on 2 monuments:** Acton/Westford (Order 20) and
    Acton/Boxborough/Littleton (Order 36) were marked `Documented`
    (meaning no field visit occurred) but their notes described an
    actual on-site search with nothing found -- changed to `Not Found`
    to match. Status color counts on any future summary/map will shift
    by these 2.
  - **"From 1904 description" label changed to "In 1904 description"**
    in bounds2pdf.py, so the 8 monuments whose cell just says "no" (not
    in the 1904 book) read as a sensible answer ("In 1904 description:
    no") instead of an odd non-answer. Column name in the sheet is
    unchanged, only the printed label.
  Everything else was minor spreadsheet cleanup with no effect on
  report logic: several typos fixed (coodinates/towalk/barm/acros), a
  1904-book quote marked `[sic]` rather than corrected (kept verbatim
  since it's a historical quotation), a truncated landmark note
  completed, two double-spaced names/street fields fixed, and the
  "same as Nashoba Road corner?" notes on Orders 25/27 replaced with a
  clearer explanation of why those crossings may never have gotten
  monuments. PDF regenerated, reflects all of the above.
2026-07-06 [Jim] Reverted the `Coordinate Datum` column change below:
  Jim downloaded MassDOT's Town_Corners.kml (extracted via new
  code/extract_town_corners.py -> code/acton_town_corners.csv, 12 Acton
  corner entries, KML Point coordinates are always WGS84 regardless of
  source projection) and used it to replace the 11 NAD83-sourced
  monument coordinates with real WGS84 values. All 49 rows with known
  coordinates are now WGS84 (2 rows have no coordinates at all, so no
  datum). bounds2pdf.py's per-row datum display is reverted back to a
  hardcoded "WGS84 (EPSG 4326)" for every row; the `Coordinate Datum`
  column itself can now be removed from the sheet whenever Jim gets to
  it. One row, Acton/Carlisle/Concord, is special: the real corner is
  inside a house, so the state's own witness monument (dated 2007,
  offset ~35m away) is what's actually recorded/visited -- that row
  keeps its original witness-monument coordinates, with the true
  corner's WGS84 location noted in "Notes on Monument" instead of
  replacing the monument's own coordinates.
2026-07-06 [Jim] Added a `Coordinate Datum` column to the Monuments
  sheet (per-row, e.g. `WGS84 (EPSG 4326)` or `NAD83 (EPSG 26986)`) since
  11 of the 50 monuments with known coordinates got their coordinates
  from the state in NAD83 and haven't been reprojected to WGS84.
  bounds2pdf.py now displays this column's value verbatim instead of
  hardcoding "WGS84 (EPSG 4326)" for every row. Flagged for Jim to
  double-check: EPSG 26986 is the Massachusetts State Plane *projected*
  system (meters), while the Latitude/Longitude columns are ordinary
  decimal-degree lat/lon -- geographic NAD83 is normally EPSG 4269, not
  26986. Not changed pending Jim's confirmation of which code is
  actually correct; the code just displays whatever string is in the
  column, so no code change is needed either way.
2026-07-06 [Jim] Reworked the per-monument page headline again, to a
  single line: `[order#] Name [status]`, dropping "Monument Listing" and
  the Corner/Street Crossing type entirely. Order number and status each
  sit in a small colored box keyed to that row's status (Painted green,
  Found blue, Couldn't paint orange, Not Found red, Documented light
  gray); text color (white knockout vs. black) is chosen automatically
  per box from the background color's relative luminance, not hand-
  picked per status. Headline font dropped from 16pt to 14pt so the
  longest monument name still fits on one line at the true 456pt frame
  width for every row (verified via Paragraph.wrap()); PDF regenerated,
  page count still 51. Order-number boxes are meant to be reused as
  clickable map markers later (a stated future plan, not built yet).
  Also fixed a leftover comment in bounds2pdf.py's Order-column sort
  that incorrectly said "counter-clockwise" (confirmed clockwise last
  session). Full detail in code/claude.md.
2026-07-05 [Jim] Reworked the per-monument page headline per Jim's
  formatting requests: name + "Monument Listing" on line 1 (no colon);
  type (Corner/Street Crossing, no brackets) + status on line 2, status
  highlighted in a box sized to just the status text using the same
  font/size/weight as the rest of the headline (via ReportLab's `<span
  backColor="...">` paragraph markup) instead of the old full-width grey
  table cell; "Status" label removed; horizontal rule still separates the
  headline from the detail fields below. Also found and fixed a real bug
  this surfaced: `flowable_h()` measured text height at the page's nominal
  468pt width instead of the ~456pt ReportLab actually renders into
  (SimpleDocTemplate's page frame adds its own 6pt padding per side by
  default), understating the height of long wrapped titles and letting
  `choose_cols()` overallocate space to photos -- this was spilling 2 of
  the 3 monuments with 3-line headlines ("...Powder Mill Road (Rte 62)",
  both the Concord and Maynard sides) onto an unnecessary second page.
  Fixed by measuring against a new `TEXT_W` constant; page count back to
  51 (was 53). code/claude.md documents both changes in full.
2026-07-05 [Jim] Coordinate precision decided: report displays 5 decimal
  places (~1m precision, well within GPS/field accuracy) via a display-
  time format in bounds2pdf.py; Acton Bounds.xlsx keeps whatever
  precision each coordinate already has, untouched, in case the extra
  digits are useful later. Documented in code/claude.md, README.md,
  TODO.md (marked done), and "Monument Listings intro draft.md".
2026-07-05 [Both] Monument page order is now driven by a new `Order`
  column in the Monuments sheet (1-51, clockwise around Acton's boundary
  starting at the Acton/Concord/Maynard/Sudbury corner, replacing the old
  implicit counter-clockwise-from-Boxborough/Stow spreadsheet row order).
  Confirmed clockwise is correct by checking that it puts the existing
  1904-report `Tie-break number` values in ascending order. bounds2pdf.py
  now sorts explicitly by `Order` (hard error on blanks, warning on
  gaps/duplicates, note if the sheet wasn't already sorted) so a future
  accidental re-sort in the Sheet can't silently change page order.
  code/claude.md documents the new column and sort behavior. Also fixed
  the stale "59 monuments" count in "Monument Listings intro draft.md"
  (Drive only) and added a note there on the new page order for
  claude.ai's use in the intro section.
2026-07-05 [Both] First real accuracy review of README.md (previously only
  security/secret-scrubbing had been checked, not content correctness):
  fixed a stale "59 monuments" claim to the correct 51 (Jim confirmed 59
  was likely a leftover from an older report version, possibly a page
  count before each monument fit on one page). Also found and fixed a
  matching stale reference in code/claude.md's OSM-screenshot-count
  estimate, and discovered that same section's "Remaining work" item for
  OSM screenshot caching was stale -- it's actually been complete for a
  while (osm_url_cache.json + --force-screenshots, already marked done in
  TODO.md) but code/claude.md was never updated to reflect it. No secrets
  found in README.md on a fresh grep pass.
2026-07-05 [Both] Established photo section conventions for intro photos:
  section column now supports intro, intro-visits, intro-legal,
  intro-history, intro-map, intro-other-towns, intro-policy in addition
  to existing monument/appendix/intro-cover values. include=yes for all
  report photos including intro; include=no reserved for truly excluded
  photos. build_manifest.py updated to recognize new values and report
  counts by section; code/claude.md and Photos/CLAUDE.md document the
  full convention.
2026-07-05 [claude.ai] Filesystem MCP now connected in Claude Desktop
  (npx @modelcontextprotocol/server-filesystem pointed at Bounds folder).
  claude.ai can now read plain text files directly without Jim dragging
  them in. ODT and XLSX still require Drive MCP or drag-in. Session-start
  protocol now: GitHub MCP reads CHANGELOG/TODO/README/claude.md; Drive
  MCP or filesystem MCP for other files as needed. Drafted
  "Monument Listings intro draft.md" (Drive only) per claude.ai's request,
  describing per-monument page contents for the Monument Listings intro
  section; MONUMENT_LISTINGS_INTRO_PAGES is currently 0.
2026-07-05 [Both] claude.ai now has GitHub MCP read access via Docker
  (github:get_file_contents, create_or_update_file, push_files,
  delete_file, get_commit tools available). Write access not yet enabled
  pending discussion of workflow implications -- Claude Code's perspective
  (conflict risk, loss of the secret-scrubbing review gate, a lighter
  branch-based middle ground) recorded in code/claude.md's Coordination
  section. Session-start protocol updated: claude.ai reads CHANGELOG,
  TODO, README, code/claude.md directly via get_file_contents instead of
  web_fetch workarounds.
2026-07-03 [claude.ai] README.md: added detailed session-start fetch
  protocol explaining raw vs blob URLs, CDN caching issue, and the
  search-workaround needed for raw.githubusercontent.com access (later
  folded together with GitHub MCP guidance on Jul 5 2026 once claude.ai
  gained MCP access).
2026-07-03 [Claude Code] Deleted code/borb/ (46MB of unused example files
  from the abandoned borb PDF library approach; never referenced by any
  script, never tracked in git). Added code/requirements.txt (pandas,
  openpyxl, Pillow, reportlab, playwright) so a new user can
  `pip install -r requirements.txt` instead of guessing dependencies from
  imports. Fixed a stale claim in code/claude.md that code/'s pyenv
  environment "may be photos" -- that's actually Photos/'s own separate
  environment; code/'s is bounds. Documented the `playwright install
  chromium` step, which `pip install` alone doesn't cover. Updated
  README.md's repo-structure tree to include requirements.txt and the
  previously-missing add_cover_columns.py.
2026-07-03 [Both] acton_bounds_context.md deleted (Jim has it backed up
  separately). Fixed dangling references in README.md, code/claude.md, and
  Project Notes.md: code/claude.md's "replying to claude.ai" channel is
  now CHANGELOG.md (explicitly the first file README.md's orientation
  guide tells a new Claude instance to read) plus README.md for anything
  meant to persist; also corrected a stale claim that this file "is
  updated by claude.ai" (it never had write access) and an outdated file
  list in the Source control section that predated CHANGELOG.md/Project
  Notes.md/README.md joining the repo.
2026-07-03 [Claude Code] README.md: verified acton_bounds_context.md's
  content against every other .md file (Jim wants to retire it now that
  README.md exists). Nearly everything was already duplicated, mostly
  more accurately, elsewhere (code/claude.md, Photos/CLAUDE.md, TODO.md,
  Project Notes.md). Folded in the three things that weren't: claude.ai's
  Drive-access mechanics, the no-DocuShare-API-integration rationale, and
  an explicit "repo is read-only for claude.ai" statement. Should now be
  safe to delete acton_bounds_context.md.
2026-07-03 [claude.ai] README.md: replaced stub with full orientation
  document covering project background, repo structure, AI collaboration
  model, Claude instance orientation guide, security notes, and key
  decisions. Claude Code corrected two things while applying: the "not in
  repo" list still said Acton Bounds.xlsx wasn't tracked (it was added
  Jul 2) -- moved it into the repo-structure tree instead; and the
  suggested fetch pattern (github.com/.../blob/main/) was swapped for
  raw.githubusercontent.com/.../main/, since blob URLs are JS-rendered
  pages that don't work reliably with a plain web_fetch tool, matching
  what's already documented in acton_bounds_context.md.
2026-07-03 [claude.ai] code/claude.md: added Security section listing
  what must not go in the public repo
2026-07-03 [Both] Added CHANGELOG.md and Project Notes.md to the repo (Jim
  reviewed and approved both, including Project Notes.md's town clerk
  contact table). acton_bounds_context.md deliberately stays Drive-only —
  it's claude.ai-owned and claude.ai can't write to the repo anyway, so
  tracking it in git would only add friction. Updated the tracked/untracked
  file list in acton_bounds_context.md's "GitHub repo" section to match.
2026-07-03 [Claude Code] acton_bounds_context.md: added a dedicated
  "GitHub repo" section (right after File Structure) explaining the
  raw.githubusercontent.com fetch pattern, the current list of
  tracked/untracked files, and that the repo is read-only for claude.ai
  (INBOX.md is still how it requests changes). This is the answer to
  "what do I need to tell claude.ai to get it started" -- nothing extra
  needed, since claude.ai reads this file fully every session and the
  instructions are now in it.
2026-07-02 [Both] Added Acton Bounds.xlsx to the public repo. Jim removed
  the Email and Phone columns from the Contacts sheet in the master Google
  Sheet and re-exported; verified clean (no emails/phone numbers/IDs
  anywhere in the workbook, all 7 sheets checked) and functionally
  smoke-tested (load_person_towns() still works — column lookups are by
  name, not position, so deleting the columns entirely was safe) before
  publishing.
2026-07-02 [Both] acton_bounds_context.md is now claude.ai-owned (Jim
  approved) — Claude Code will stop proactively editing it except via
  explicit INBOX.md requests, since its technical sections duplicated
  code/claude.md and drifted stale from not being reliably kept in sync.
  Left a note directly in the file (its own first-lines instruction is
  "read fully before responding," so this is the reliable way for Claude
  Code to reach claude.ai — there's no formal reverse-INBOX channel).
2026-07-02 [Both] Deleted "CLAUDE.md note - DocuShare photo linking.md" —
  Jim reviewed it (no sensitive info) but confirmed everything in it was
  already implemented and documented in code/claude.md, making it
  redundant. Fixed dangling references to it in acton_bounds_context.md
  and code/claude.md; also refreshed several other stale DocuShare-status
  mentions in acton_bounds_context.md ("not yet implemented" -> DONE) while
  in there. acton_bounds_context.md's broader "Code Status" section is
  still stale beyond just DocuShare (predates today's page footer, photo
  sizing, and Not Found/Witnesses wording changes) -- flagged, not fixed,
  since that's bigger scope than this cleanup.
2026-07-02 [Both] Found and fixed a real exposure in the just-created public
  repo: the Drive folder ID (acton_bounds_context.md, code/claude.md) and
  Google Sheet ID (acton_bounds_context.md, Photos/CLAUDE.md,
  Photos/process_takeout.py) were hardcoded in tracked files, plus Jim's
  email was embedded in absolute paths in code/acton_cover.py. Sheet ID
  moved out of process_takeout.py into a new local gitignored
  Photos/sheet_id.txt (script raises a clear error if it's missing);
  Drive folder ID references replaced with "ask Jim"; acton_cover.py's
  hardcoded paths replaced with placeholders. Since the sensitive IDs were
  already in the initial commit's history (not just the latest version),
  fix-forward alone wasn't enough -- deleted and recreated the GitHub repo
  from scratch (repo was only ~30 min old, no known clones) so the clean
  history has zero trace of either ID. Verified via `git log -p` locally
  and the GitHub API after push: 1 commit, same 14 files, no exposed IDs.
2026-07-02 [Both] Set up git + public GitHub repo: github.com/jim-snyder-grant/acton-bounds.
  Repo root is Bounds/ (the whole Insync-synced folder), using an
  allowlist-style .gitignore (deny by default, explicitly un-ignore only
  code/*.py, code/claude.md, Photos/process_takeout.py, Photos/CLAUDE.md,
  and a few small support files) since this folder has personal contact
  info and large reference material that must never be published. The
  shared coordination .md files (acton_bounds_context.md, TODO.md, Project
  Notes.md, this file) are NOT yet in the repo -- deliberately held back
  pending Jim's review for anything sensitive before they go public.
  Replaced an earlier local-only git repo that lived inside Photos/ (5
  commits, no remote, history not preserved -- Jim confirmed OK to lose).
  claude.ai can now read code/claude.md directly via
  raw.githubusercontent.com/jim-snyder-grant/acton-bounds/main/code/claude.md
  (confirmed working) instead of Jim relaying file contents by hand.
  Also identified a follow-on task: categorize every file in Bounds/ as
  Keep+git / Keep+DocuShare / Both / Delete / Keep-until-archive, since the
  whole Drive folder eventually goes away once archived (added to TODO.md).
2026-07-02 [Claude Code] bounds2pdf.py: "Not Found"/Documented status now
  labeled "Date searched:"/"Not yet searched" instead of "Date of visit:"/
  "Not yet visited"; Witnesses line now only shown for Painted/Found/
  Couldn't paint statuses (was showing for any status if the date happened
  to match a Contacts row); single/double-photo pages now use full page
  width and skip the old 200pt height cap, since remaining_h already
  prevents overlap; fixed a latent bug where importing the module (not
  just running it) silently triggered a full report regeneration
  (asyncio.run(main()) wasn't guarded by if __name__ == '__main__')
2026-07-02 [Claude Code] Processed 3 INBOX.md messages: TODO.md got a
  coordinate-precision decision item and a reverse-geocoding workflow
  (Geoapify manual tool, geocode.maps.co if ever scripted -- noted in
  code/claude.md); source control setup investigated and proposed to Jim
  directly (not yet actioned -- awaiting his go-ahead per the inbox
  instructions)
2026-07-02 [Both] All 173 local photos now have a docushare_url — full
  DocuShare photo linking complete. Jim uploaded the remaining 3 photos and
  fixed a stale local HTML save along the way; scrape_docushare.py fixed to
  read filenames from dc:title instead of the mangled URL-encoded path
  (was 165/173 linked due to that bug, briefly 170/173, now 173/173 -- no
  re-upload was ever actually needed, that earlier diagnosis was wrong).
  TODO.md pagination item marked confirmed-not-an-issue (177 docs, one
  page, nothing clipped). code/claude.md DocuShare section corrected and
  updated to match; 4 harmless duplicate DocuShare uploads noted for
  optional cleanup.
2026-07-02 [Claude Code] code/claude.md: updated DocuShare section with
  real Jul 2 merge results (165/173 linked), the merge_docushare.py
  MANIFEST_COLUMNS bugfix, and DocuShare's filename-mangling behavior
  (colon truncation, quote/apostrophe substitution); Photos/CLAUDE.md:
  documented process_takeout.py's new caption sanitization
2026-07-02 [Claude Code] Processed 2 INBOX.md messages: created this
  CHANGELOG.md and wired up the protocol; added Select Board vote lookup
  item to TODO.md Field work; added fine-amount and Perambulation Plan.odt
  source-document notes to Project Notes.md
2026-07-02 [Claude Code] process_takeout.py: sanitize captions for
  DocuShare-unsafe characters (':' -> '-', apostrophes/quotes stripped)
  before building filenames; validation report now shows before/after for
  any changed captions
2026-07-02 [Claude Code] Fixed merge_docushare.py: MANIFEST_COLUMNS was
  stale and would have silently dropped the orientation/cover_candidate
  columns on merge; scraped+merged the first real batch of 174 uploaded
  DocuShare photos (165 of 173 local photos now linked); found DocuShare
  truncates filenames at ':' and mangles quotes/apostrophes on upload
2026-07-01 [Claude Code] bounds2pdf.py: added "Monument Listings, page X
  of N" footer (NumberedCanvas); added MONUMENT_LISTINGS_INTRO_PAGES
  constant for offsetting once Jim's Monument Listings intro is written
2026-07-01 [Claude Code] TODO.md: marked OSM caching done; added DocuShare
  scraper/merge scripts as done; added clickable photo/map links as done;
  added page footer as done; added MONUMENT_LISTINGS_INTRO_PAGES note;
  added "Collect better coordinates" to Field work; renumbered intro sections
2026-07-01 [Claude Code] acton_bounds_context.md: updated bounds2pdf.py
  status (OSM caching done, scraper/merge done); updated file list; cover
  page marked complete
2026-07-01 [Both] Project Notes.md: added cover page section with design
  decisions, SimpInkScr lessons learned, and final photo selections
2026-07-01 [Both] TODO.md: cover page marked complete
2026-06-30 [Claude Code] photo_manifest.csv: added orientation and
  cover_candidate columns (add_cover_columns.py)
2026-06-30 [Claude Code] code/CLAUDE.md: added cover page section and
  INBOX.md protocol
