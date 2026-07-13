# Acton Bounds report — build pipeline
# =====================================
# Run from the project root:  make report   (or: make -C <this dir> report)
#
# NOTE — why this is a "task runner", not an incremental Make:
# Almost every input/output here has SPACES (and one an em-dash) in its name
# ("Acton Bounds.xlsx", "Acton Bounds Report 2025-2026.pdf",
# "report/The Work Behind This Report.pdf", "report/Monument Listings —
# Introduction.pdf"). Make can't use space-containing names as targets or
# prerequisites without fragile escaping, so these are all .PHONY targets that
# just run the steps in dependency order. Each step is fast (seconds), so
# always-rebuild is fine. The scripts themselves anchor their own paths (see
# code/claude.md), so the recipes work regardless of where make is invoked from.

PY := python3

.DEFAULT_GOAL := all
.PHONY: all report sections listings assemble verify overview-map manifest clean help

## all:          build the report (sections + listings + assemble) then verify
all: report verify

## report:       render sections + monument listings, then assemble the final PDF
report: sections listings assemble

## sections:     render every report/*.md intro section to report/*.pdf
sections:
	$(PY) code/intro2pdf.py report/*.md

## listings:     regenerate code/monument_listings.pdf from the spreadsheet + photos
listings:
	$(PY) code/bounds2pdf.py

## assemble:     merge all sections into "Acton Bounds Report 2025-2026.pdf"
# (assumes code/overview_map.pdf already exists — see the overview-map target)
assemble:
	$(PY) code/assemble_report.py

## verify:       check every overview-map callout link resolves (PASS/FAIL, exit 0/1)
verify:
	$(PY) code/verify_report.py

## overview-map: regenerate code/overview_map.pdf (needs geopandas+matplotlib;
##               run only when the boundary/base-map data changes — NOT part of
##               the default build, so a normal rebuild never needs those deps)
overview-map:
	$(PY) code/overview_map.py

## manifest:     rescan Photos/ into photo_manifest.csv (only after adding photos;
##               preserves hand edits — deliberately NOT part of the default build)
manifest:
	$(PY) code/build_manifest.py

## clean:        remove generated section + listings PDFs and the assembled report
##               (keeps code/overview_map.pdf, which is expensive to rebuild)
clean:
	rm -f report/*.pdf code/monument_listings.pdf "Acton Bounds Report 2025-2026.pdf"

## help:         list these targets
help:
	@grep -E '^## ' $(MAKEFILE_LIST) | sed -e 's/^## //'
