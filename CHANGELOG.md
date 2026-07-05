# Acton Bounds — Changelog

Running log of substantive changes to shared project files.
One line per change, newest at top.
Format: YYYY-MM-DD [who] file changed: description

---

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
