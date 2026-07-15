#!/usr/bin/env python3
"""Assemble the final Acton Bounds report from its section PDFs and stamp the
whole-report footer on every page.

Each section is produced independently (cover via acton_cover.py, intro
sections via intro2pdf.py, the overview map via overview_map.py, the monument
listings via bounds2pdf.py) and already carries its own right-justified
per-section footer ("<Section>, page X of M"). This script concatenates them in
the order given by `report_sections.csv` and overlays the LEFT-justified
whole-report footer -- "Acton Bounds Report 2025-2026, page X of N" -- once the
true merged total N is finally known. See "Page numbering -- two-part footer"
in code/claude.md.

Section list / order lives in `report_sections.csv` (columns:
order, section, file, footer). `file` is resolved relative to the Bounds
folder (this script's parent). Missing files are skipped with a warning, so a
partial draft assembles fine while some sections are still unwritten. `footer`
= no suppresses the whole-report footer on that section's pages (e.g. the cover
title page) -- those pages still consume a page number in the sequence.

Pages may be mixed sizes (letter sections + the legal-size overview map); the
footer is stamped per page at the same 1in-from-left, 26pt-up position
regardless, so it lines up across sizes.

--draft marks a build for circulation to reviewers: every running footer gets
the assembly date/time, the cover gets a centered "DRAFT FOR REVIEW · <stamp>",
and the file is written to drafts/ named by that stamp, so it never overwrites
the real report or a previous draft. The stamp is the assembly time, NOT a git
commit -- photo_manifest.csv is gitignored, so two builds at the same SHA can
legitimately differ. Corollary: an old draft cannot be reconstructed from the
repo, so drafts/ is the only archive of what reviewers actually saw.

Usage:
  python3 assemble_report.py [--manifest report_sections.csv] [--out PATH]
  python3 assemble_report.py --draft
"""
import argparse
import csv
import datetime
import json
import os
import sys
from io import BytesIO

from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, DictionaryObject, FloatObject,
                           NameObject, NumberObject)

HERE = os.path.dirname(os.path.abspath(__file__))
BOUNDS = os.path.join(HERE, "..")              # section files resolve from here
DEFAULT_MANIFEST = os.path.join(HERE, "report_sections.csv")
DEFAULT_OUT = os.path.join(BOUNDS, "Acton Bounds Report 2025-2026.pdf")
# --draft builds land here, one timestamped file each, never overwriting the
# real report. This folder IS the archive of what went to reviewers: a draft
# can't be rebuilt later (photo_manifest.csv is gitignored, so no commit pins a
# build), so the copy you sent is the only copy. Gitignored, but it lives inside
# the Insync/Drive tree, so it syncs off-machine on its own.
DRAFTS_DIR = os.path.join(BOUNDS, "drafts")

# For the clickable overview-map callout boxes: which section is the map and
# which is the monument listings (matched by file basename), plus the sidecar
# of box rectangles overview_map.py writes.
MAP_BASENAME = "overview_map.pdf"
LISTINGS_BASENAME = "monument_listings.pdf"
LINKS_JSON = os.path.join(HERE, "overview_map_links.json")

REPORT_TITLE = "Acton Bounds Report 2025-2026"
# --draft trims the title in the left footer. The full title plus a timestamp
# does NOT fit: the left footer shares its baseline with each section's
# right-justified "<Section>, page X of M", and on the "Monument Listings —
# Introduction" pages the full title + stamp overruns it by ~27pt. "Acton
# Bounds" leaves ~59pt of clearance. See footer_clearance() below.
DRAFT_TITLE = "Acton Bounds"
MARGIN = 72               # 1 inch from the left edge
FOOTER_Y = 0.5 * 72 - 10  # 26 pt up from the bottom edge (matches sections)
GRAY = HexColor("#555555")
FOOTER_FONT = ("Helvetica", 9)      # must match intro2pdf.py / bounds2pdf.py
MIN_FOOTER_GAP = 18                 # pt of white the two footers must keep

# --draft cover stamp. It is overlaid here at assembly time rather than built
# into the cover, on purpose: FrontPage.pdf is a hand-made Inkscape artifact
# (acton_cover.py is a SimpInkScr script, not part of `make`) and is shared by
# the draft and final builds. Baking DRAFT into it would leak into the final
# report, and the timestamp changes every build, so it would mean an Inkscape
# round-trip per draft. As an overlay it costs nothing and cannot reach `make
# report`.
#
# Geometry/typography: the cover is a full-bleed collage around a cream panel.
# The footer baseline (y=26) lands on the photos and is unreadable, so the stamp
# sits in the clear cream just under the "PERAMBULATION OF TOWN BOUNDS" line,
# grouping with the title block. Times-Roman approximates the cover's Georgia
# (not installed here, and not worth a font dependency); #8a7a5a is exactly the
# cover's rule_color, so the line reads as part of the title block.
COVER_STAMP_Y = 280
COVER_STAMP_FONT = ("Times-Roman", 11)
COVER_STAMP_COLOR = HexColor("#8a7a5a")


def read_manifest(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append({
                "order": int(r["order"]),
                "section": r["section"].strip(),
                "file": r["file"].strip(),
                "footer": r["footer"].strip().lower() in ("yes", "y", "true", "1"),
            })
    rows.sort(key=lambda r: r["order"])
    return rows


def footer_overlay(width, height, text):
    """A single-page PDF (page-sized) carrying just the left footer text."""
    buf = BytesIO()
    c = pdfcanvas.Canvas(buf, pagesize=(width, height))
    c.setFont(*FOOTER_FONT)
    c.setFillColor(GRAY)
    c.drawString(MARGIN, FOOTER_Y, text)
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def cover_stamp_overlay(width, height, text):
    """A single-page PDF carrying just the centered draft line for the cover."""
    buf = BytesIO()
    c = pdfcanvas.Canvas(buf, pagesize=(width, height))
    c.setFont(*COVER_STAMP_FONT)
    c.setFillColor(COVER_STAMP_COLOR)
    c.drawCentredString(width / 2.0, COVER_STAMP_Y, text)
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def footer_clearance(left_text, section, page_w, sec_pg, sec_total):
    """White space (pt) between the left whole-report footer and the section's
    own right-justified footer, which share a baseline.

    The right-hand text isn't ours -- intro2pdf.py / bounds2pdf.py bake it into
    each section PDF -- but its format is fixed, so we can reconstruct it from
    the manifest and measure. Guards against a long title/stamp/section name
    silently overprinting the other footer.
    """
    right_text = f"{section}, page {sec_pg} of {sec_total}"
    used = (stringWidth(left_text, *FOOTER_FONT)
            + stringWidth(right_text, *FOOTER_FONT))
    return (page_w - 2 * MARGIN) - used


def add_overview_map_links(writer, map_start, listings_start, listings_count):
    """Drop an internal 'go to this monument's page' link over each callout box
    on the overview-map page. Box rectangles come from overview_map.py's sidecar
    (overview_map_links.json); the target is the monument's page in the merged
    doc -- listings_start + (Order - 1), since bounds2pdf.py emits one page per
    monument in Order sequence.

    Skips quietly (rather than risk wrong links) if either section is absent,
    the sidecar is missing, or the listings page count doesn't match the box
    count 1:1 (e.g. a monument page ever spilled onto two pages)."""
    if map_start is None or listings_start is None:
        return
    if not os.path.exists(LINKS_JSON):
        print("  (no overview_map_links.json -- skipping clickable callout boxes)")
        return
    with open(LINKS_JSON) as fh:
        boxes = json.load(fh)["boxes"]
    if listings_count != len(boxes):
        print(f"  WARNING: monument-listings pages ({listings_count}) != callout "
              f"boxes ({len(boxes)}); skipping clickable boxes to avoid mis-links")
        return
    map_page = writer.pages[map_start]
    annots = map_page.get(NameObject("/Annots"))
    if annots is None:
        annots = ArrayObject()
        map_page[NameObject("/Annots")] = annots
    for order_str, rect in boxes.items():
        target = listings_start + (int(order_str) - 1)
        annot = DictionaryObject({
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Link"),
            NameObject("/Rect"): ArrayObject([FloatObject(v) for v in rect]),
            NameObject("/Border"): ArrayObject([NumberObject(0)] * 3),  # no visible box
            # local GoTo destination referencing the actual page object
            NameObject("/Dest"): ArrayObject(
                [writer.pages[target].indirect_reference, NameObject("/Fit")]),
            NameObject("/P"): map_page.indirect_reference,
        })
        annots.append(writer._add_object(annot))
    print(f"  added {len(boxes)} clickable callout-box links on the overview map "
          f"(page {map_start + 1})")


def main():
    ap = argparse.ArgumentParser(description="Assemble the final report PDF.")
    ap.add_argument("--manifest", default=DEFAULT_MANIFEST,
                    help="section-order CSV (default: report_sections.csv)")
    ap.add_argument("--out", default=None,
                    help="output PDF path")
    ap.add_argument("--draft", action="store_true",
                    help="stamp every page with the assembly date/time and mark "
                         "the cover DRAFT FOR REVIEW; names the file by timestamp")
    args = ap.parse_args()

    # A draft is identified by when it was assembled, deliberately not by a git
    # commit: photo_manifest.csv is gitignored, so which photos/captions/links
    # are in a build is NOT captured by any commit -- two builds at the same SHA
    # can differ. The assembly time is the only honest identifier.
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M") if args.draft else None
    if args.out is None:
        if args.draft:
            os.makedirs(DRAFTS_DIR, exist_ok=True)
            args.out = os.path.join(DRAFTS_DIR, "Acton Bounds Report — DRAFT %s.pdf"
                                    % stamp.replace(":", "-"))
        else:
            args.out = DEFAULT_OUT

    rows = read_manifest(args.manifest)

    # First pass: gather every page (keeping readers alive) and its footer flag.
    readers = []          # keep references so pages stay valid until write
    pages = []            # (page_obj, footer_flag)
    plan = []             # (section, file, n_pages, present)
    map_start = listings_start = listings_count = None   # 0-based page indices
    for row in rows:
        path = os.path.normpath(os.path.join(BOUNDS, row["file"]))
        if not os.path.exists(path):
            plan.append((row["section"], row["file"], 0, False))
            print(f"  SKIP (missing): {row['section']}  <- {row['file']}")
            continue
        reader = PdfReader(path)
        readers.append(reader)
        start_idx = len(pages)
        base = os.path.basename(path)
        if base == MAP_BASENAME:
            map_start = start_idx
        elif base == LISTINGS_BASENAME:
            listings_start, listings_count = start_idx, len(reader.pages)
        n_sec = len(reader.pages)
        for sec_pg, pg in enumerate(reader.pages, start=1):
            pages.append((pg, row["footer"], row["section"], sec_pg, n_sec))
        plan.append((row["section"], row["file"], n_sec, True))

    if not pages:
        sys.exit("No section PDFs found -- nothing to assemble.")

    total = len(pages)

    # Second pass: stamp the whole-report footer and write out.
    writer = PdfWriter()
    title = f"{DRAFT_TITLE} DRAFT {stamp}" if args.draft else REPORT_TITLE
    tightest = None
    for gi, (pg, flag, section, sec_pg, sec_total) in enumerate(pages, start=1):
        w, h = float(pg.mediabox.width), float(pg.mediabox.height)
        if flag:
            text = f"{title}, page {gi} of {total}"
            gap = footer_clearance(text, section, w, sec_pg, sec_total)
            if tightest is None or gap < tightest[0]:
                tightest = (gap, gi, section)
            pg.merge_page(footer_overlay(w, h, text))
        elif args.draft:
            # The cover carries no running footer (footer=no), so a draft would
            # otherwise go out with an unmarked front page -- the one page most
            # likely to be forwarded on its own.
            pg.merge_page(cover_stamp_overlay(w, h, f"DRAFT FOR REVIEW · {stamp}"))
        writer.add_page(pg)

    if tightest is not None:
        gap, gi, section = tightest
        if gap < MIN_FOOTER_GAP:
            print(f"  WARNING: footers nearly collide on page {gi} ({section}): "
                  f"{gap:.1f}pt of white, want >={MIN_FOOTER_GAP}pt. Shorten the "
                  f"title/stamp or that section name.")
        else:
            print(f"  footer clearance OK (tightest: {gap:.1f}pt on page {gi})")

    add_overview_map_links(writer, map_start, listings_start, listings_count)

    with open(args.out, "wb") as fh:
        writer.write(fh)

    # Report what was assembled, with page ranges.
    print("\nAssembled sections:")
    start = 1
    for section, fname, npg, present in plan:
        if not present:
            print(f"  --  (not yet written)   {section}")
            continue
        end = start + npg - 1
        rng = f"p{start}" if npg == 1 else f"p{start}-{end}"
        print(f"  {rng:>10}  {section}")
        start = end + 1
    print(f"\nWrote {args.out}  ({total} pages)")


if __name__ == "__main__":
    main()
