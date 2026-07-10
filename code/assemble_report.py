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

Usage:
  python3 assemble_report.py [--manifest report_sections.csv] [--out PATH]
"""
import argparse
import csv
import json
import os
import sys
from io import BytesIO

from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.colors import HexColor
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, DictionaryObject, FloatObject,
                           NameObject, NumberObject)

HERE = os.path.dirname(os.path.abspath(__file__))
BOUNDS = os.path.join(HERE, "..")              # section files resolve from here
DEFAULT_MANIFEST = os.path.join(HERE, "report_sections.csv")
DEFAULT_OUT = os.path.join(BOUNDS, "Acton Bounds Report 2025-2026.pdf")

# For the clickable overview-map callout boxes: which section is the map and
# which is the monument listings (matched by file basename), plus the sidecar
# of box rectangles overview_map.py writes.
MAP_BASENAME = "overview_map.pdf"
LISTINGS_BASENAME = "monument_listings.pdf"
LINKS_JSON = os.path.join(HERE, "overview_map_links.json")

REPORT_TITLE = "Acton Bounds Report 2025-2026"
MARGIN = 72               # 1 inch from the left edge
FOOTER_Y = 0.5 * 72 - 10  # 26 pt up from the bottom edge (matches sections)
GRAY = HexColor("#555555")


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
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(MARGIN, FOOTER_Y, text)
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


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
    ap.add_argument("--out", default=DEFAULT_OUT,
                    help="output PDF path")
    args = ap.parse_args()

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
        for pg in reader.pages:
            pages.append((pg, row["footer"]))
        plan.append((row["section"], row["file"], len(reader.pages), True))

    if not pages:
        sys.exit("No section PDFs found -- nothing to assemble.")

    total = len(pages)

    # Second pass: stamp the whole-report footer and write out.
    writer = PdfWriter()
    for gi, (pg, flag) in enumerate(pages, start=1):
        if flag:
            w, h = float(pg.mediabox.width), float(pg.mediabox.height)
            text = f"{REPORT_TITLE}, page {gi} of {total}"
            pg.merge_page(footer_overlay(w, h, text))
        writer.add_page(pg)

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
