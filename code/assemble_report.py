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
import os
import sys
from io import BytesIO

from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.colors import HexColor
from pypdf import PdfReader, PdfWriter

HERE = os.path.dirname(os.path.abspath(__file__))
BOUNDS = os.path.join(HERE, "..")              # section files resolve from here
DEFAULT_MANIFEST = os.path.join(HERE, "report_sections.csv")
DEFAULT_OUT = os.path.join(BOUNDS, "Acton Bounds Report 2025-2026 - FULL.pdf")

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
    for row in rows:
        path = os.path.normpath(os.path.join(BOUNDS, row["file"]))
        if not os.path.exists(path):
            plan.append((row["section"], row["file"], 0, False))
            print(f"  SKIP (missing): {row['section']}  <- {row['file']}")
            continue
        reader = PdfReader(path)
        readers.append(reader)
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
